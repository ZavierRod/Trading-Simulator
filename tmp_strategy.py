def on_tick(ctx, tick):
    from pydantic import BaseModel
    class Order(BaseModel):
        symbol: str
        side: str
        quantity: int
        price: float
    return Order(symbol=tick["symbol"],
                 side="buy",
                 quantity=1,
                 price=tick["price"])
