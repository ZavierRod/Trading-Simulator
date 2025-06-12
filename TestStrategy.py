# TestStrategy.py
# A simple container for an order action
class Action:
    def __init__(self, symbol: str, side: str, quantity: int, price: float):
        self.symbol = symbol
        self.side = side  # "buy" or "sell"
        self.quantity = quantity
        self.price = price


def initialize(ctx):
    # Called once before the feed starts.
    ctx["initialized"] = True


def on_tick(ctx, tick):
    # tick is a dict: {"symbol": "...", "price": ..., "timestamp": "..."}
    # Always buy one share at the incoming price.
    return Action(
        symbol=tick["symbol"],
        side="buy",
        quantity=1,
        price=tick["price"]
    )
