from typing import List
from backend.app.models.order import Order, OrderStatus
from ..models.trade import Trade

def match_orders(orders: List[Order]):
    orders_by_symbol = {}
    for order in orders:
        orders_by_symbol.setdefault(order.symbol, []).append(order)
    # sort group into buys or sells and match them since
    # group is the list of order objects with that symbol
    trades = []
    for symbol, group in orders_by_symbol.items():
        buys = []
        sells = []
        for order in group:
            # only consider live orders
            if order.status != OrderStatus.OPEN or order.remaining_qty <= 0:
                continue
            if order.side == 'buy':
                buys.append(order)
            elif order.side == 'sell':
                sells.append(order)
        buys.sort(key=lambda x: x.price, reverse=True)
        sells.sort(key=lambda x: x.price)
        # you can only perform a trade if you have a buy and sell list
        # and the prices are not negative
        while buys and sells and buys[0].price >= sells[0].price:
            qty = min(buys[0].remaining_qty, sells[0].remaining_qty)
            if qty > 0:
                trade = Trade(
                    sell_order_id= sells[0].id,
                    buy_order_id= buys[0].id,
                    symbol=symbol,
                    quantity=qty,
                    price= buys[0].price,
                )
                trades.append(trade)
                # decrement open quantities
                buys[0].remaining_qty -= qty
                sells[0].remaining_qty -= qty

                # update order status flags
                if buys[0].remaining_qty == 0:
                    buys[0].status = OrderStatus.FILLED
                else:
                    buys[0].status = OrderStatus.PARTIALLY_FILLED

                if sells[0].remaining_qty == 0:
                    sells[0].status = OrderStatus.FILLED
                else:
                    sells[0].status = OrderStatus.PARTIALLY_FILLED
                if buys and buys[0].remaining_qty == 0:
                    buys.pop(0)
                if sells and sells[0].remaining_qty == 0:
                    sells.pop(0)
    return trades
