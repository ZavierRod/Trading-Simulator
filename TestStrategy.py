# TestStrategy.py
# A simple container for an order action
class Action:
    def __init__(self, symbol: str, side: str, quantity: int, price: float):
        self.symbol = symbol
        self.side = side  # "buy" or "sell"
        self.quantity = quantity
        self.price = price


def initialize(ctx):
    """
    Called once before the feed starts.
    We’ll keep a rolling list of recent prices
    so that the strategy can decide when to buy
    and when to sell.
    """
    ctx["prices"] = []


def on_tick(ctx, tick):
    """
    Simple mean‑reversion example:
    * BUY when the price is more than 2 % below the 20‑tick average
    * SELL when the price is more than 2 % above the 20‑tick average
    Otherwise do nothing.
    """
    price = tick["price"]
    ctx["prices"].append(price)

    # Need enough history to compute an average
    if len(ctx["prices"]) < 20:
        return None

    avg = sum(ctx["prices"][-20:]) / 20

    if price < 0.98 * avg:
        return Action(
            symbol=tick["symbol"],
            side="buy",
            quantity=1,
            price=price,
        )
    elif price > 1.02 * avg:
        return Action(
            symbol=tick["symbol"],
            side="sell",
            quantity=1,
            price=price,
        )

    return None
