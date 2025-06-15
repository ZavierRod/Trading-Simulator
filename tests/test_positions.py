import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.order import Order, OrderStatus
from backend.app.models.trade import Trade
from backend.app.services.position import get_positions_with_pnl

@pytest.fixture(scope="function")
def db():
    # in-memory SQLite, fresh per test
    engine = create_engine("sqlite+pysqlite:///:memory:",
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    yield Session()


def _insert_order(db, **kw):
    o = Order(
        firm_id=kw["firm_id"],
        symbol=kw["symbol"],
        side=kw["side"],
        quantity=kw["qty"],
        remaining_qty=kw.get("remaining", 0),
        price=kw["px"],
        status=OrderStatus.FILLED,
    )
    db.add(o)
    db.flush()      # assign id
    return o


def _insert_trade(db, buy, sell, qty, px):
    t = Trade(
        buy_order_id=buy.id,
        sell_order_id=sell.id,
        symbol=buy.symbol,
        quantity=qty,
        price=px,
    )
    db.add(t)
    return t


def test_positions_pnl_long_short_flat(db):
    # ---- 1. create two trades in AAPL ----
    # long firm (id 1)   buys 10 @ 100, buys 10 @ 110   (avg 105)
    # short firm (id 2)  sells 20 @ same prices
    o1 = _insert_order(db, firm_id=1, symbol="AAPL", side="buy",  qty=10, px=100)
    o2 = _insert_order(db, firm_id=2, symbol="AAPL", side="sell", qty=10, px=100)
    _insert_trade(db, buy=o1, sell=o2, qty=10, px=100)

    o3 = _insert_order(db, firm_id=1, symbol="AAPL", side="buy",  qty=10, px=110)
    o4 = _insert_order(db, firm_id=2, symbol="AAPL", side="sell", qty=10, px=110)
    _insert_trade(db, buy=o3, sell=o4, qty=10, px=110)

    # ---- 2. create a flat position in TEST ----
    ob = _insert_order(db, firm_id=1, symbol="TEST", side="buy",  qty=5, px=50)
    os = _insert_order(db, firm_id=1, symbol="TEST", side="sell", qty=5, px=60)
    _insert_trade(db, buy=ob, sell=os, qty=5, px=50)   # first leg
    _insert_trade(db, buy=ob, sell=os, qty=5, px=60)   # second leg

    db.commit()

    # ---- 3. last prices: AAPL 120, TEST 60 ----
    last_aapl = Trade(symbol="AAPL", quantity=0, price=120,
                      buy_order_id=o1.id, sell_order_id=o2.id)
    last_test = Trade(symbol="TEST", quantity=0, price=60,
                      buy_order_id=ob.id, sell_order_id=os.id)
    db.add_all([last_aapl, last_test])
    db.commit()

    # ---- 4. run helper ----
    pos = { (p["firm_id"], p["symbol"]): p
            for p in get_positions_with_pnl(db) }

    # long AAPL (firm 1)
    long = pos[(1, "AAPL")]
    assert long["net_qty"] == 20
    assert pytest.approx(long["avg_price"]) == 105.0
    assert long["last_price"] == 120
    assert pytest.approx(long["pnl"]) == 20 * (120 - 105)  # +300

    # short AAPL (firm 2)
    short = pos[(2, "AAPL")]
    assert short["net_qty"] == -20
    assert pytest.approx(short["avg_price"]) == 105.0
    assert pytest.approx(short["pnl"]) == -20 * (120 - 105)  # -300

    # flat TEST
    flat = pos[(1, "TEST")]
    assert flat["net_qty"] == 0
    assert flat["avg_price"] is None
    assert flat["pnl"] == 0.0