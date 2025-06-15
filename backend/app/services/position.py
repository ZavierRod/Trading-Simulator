# backend/app/services/position.py
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from ..models.order import Order
from ..models.trade import Trade
from sqlalchemy import select, func, case

def _stmt_positions():
    """
    Select firm_id, symbol, net_qty, cash_flow.
    signed_qty  = +qty for buys  / -qty for sells
    cash_flow   = signed_qty * price  (negative cash for buys)
    """
    signed_qty = case(
        (Order.side == "buy", Trade.quantity),
        else_=-Trade.quantity,
    )
    signed_cash = signed_qty * Trade.price

    return (
        select(
            Order.firm_id.label("firm_id"),
            Trade.symbol.label("symbol"),
            func.sum(signed_qty).label("net_qty"),
            func.sum(signed_cash).label("cash_flow"),
        )
        .join(
            Order,
            (Trade.buy_order_id == Order.id) |
            (Trade.sell_order_id == Order.id),
            )
        .group_by(Order.firm_id, Trade.symbol)
    )

def _stmt_last_px():
    """Return symbol → last trade price (latest ID)."""
    latest_id_sub = (
        select(
            Trade.symbol.label("symbol"),
            func.max(Trade.id).label("max_id")
        ).group_by(Trade.symbol).subquery()
    )

    return (
        select(Trade.symbol, Trade.price.label("last_px"))
        .join(latest_id_sub, (Trade.symbol == latest_id_sub.c.symbol) &
              (Trade.id == latest_id_sub.c.max_id))
    )


def get_positions_with_pnl(db):
    # ① positions aggregate
    pos_rows = db.execute(_stmt_positions()).all()

    # ② latest price per symbol (dict)
    last_px_rows = db.execute(_stmt_last_px()).all()
    last_price = {r.symbol: r.last_px for r in last_px_rows}

    positions = []
    for r in pos_rows:
        net = r.net_qty
        avg = (r.cash_flow / net) if net else None        # conventional positive cost
        last = last_price.get(r.symbol)
        pnl = (net * (last - avg)) if (net and avg is not None and last is not None) else 0.0
        positions.append(
            {
                "firm_id":  r.firm_id,
                "symbol":   r.symbol,
                "net_qty":  net,
                "avg_price": avg,
                "last_price": last,
                "pnl":      pnl,
            }
        )
    return positions

def get_positions(db: Session):
    rows = db.execute(_stmt_positions()).all()
    positions = []
    for r in rows:
        net = r.net_qty
        avg = (r.cash_flow / net) if net else None        # conventional positive cost
        positions.append(
            {
                "firm_id":  r.firm_id,
                "symbol":   r.symbol,
                "net_qty":  net,
                "avg_price": avg,
            }
        )
    return positions