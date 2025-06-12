import argparse
import importlib.util
import logging
import sys
import os
import requests
import json
import time

logging.basicConfig(level=logging.INFO)
def parse_args():
    parser = argparse.ArgumentParser(description="Runs the sandbox environment")
    parser.add_argument("--strategy-id", type=int, required=True,
                        help='ID of the strat that is loaded from the database/API')
    parser.add_argument('--feed-file', type=str, required=True,
                        help='Path to JSON file that contains the price feed data')
    return parser.parse_args()




def run_strategy(strategy_id: int, feed_file: str):
    # Fetch strategy code via HTTP with retry logic
    backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(f"{backend_url}/api/strategies/{strategy_id}")
            response.raise_for_status()
            code_text = response.json().get("code", "")
            if not code_text:
                raise ValueError(f"Empty code for strategy {strategy_id}")
            break
        except Exception as e:
            logging.warning(f"Attempt {attempt}/{max_retries} failed: {e}")
            time.sleep(1)
    else:
        logging.error(f"Failed to fetch strategy {strategy_id} after {max_retries} attempts")
        sys.exit(1)

    strategy_path = "/tmp/strategy.py"
    with open(strategy_path, "w") as f:
        f.write(code_text)

    spec = importlib.util.spec_from_file_location("strategy", strategy_path)
    strategy_module = importlib.util.module_from_spec(spec)
    sys.modules["strategy"] = strategy_module
    spec.loader.exec_module(strategy_module)
    logging.info(f"Loaded strategy {strategy_id} from {strategy_path}")
    with open(feed_file, 'r') as f:
        try:
            feed_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse feed file {feed_file}: {e}")
            sys.exit(1)
    ctx = {}
    if hasattr(strategy_module, 'initialize'):
        try:
            strategy_module.initialize(ctx)
        except Exception as e:
            logging.error(f"Error in initialize: {e}")
    else:
        logging.info("No initialize() func in the strategy; gonna skip initialization")
    for tick in feed_data:

        if hasattr(strategy_module,'on_tick'):
            try:
                action = strategy_module.on_tick(ctx, tick)
            except Exception as e:
                logging.error(f'Error in on_tick: {e}')
                action = None
        else:
            logging.info("No on_tick() func in the strategy; skipping the tick")
            action = None
        if action:
            order_payload = {
                "firm_id": strategy_id,
                'symbol': action.symbol,
                'side': action.side,
                'quantity': action.quantity,
                'price': action.price
            }
            post_response = requests.post(f"{backend_url}/api/orders",
            json=order_payload
            )
            try:
                post_response.raise_for_status()
            except Exception as e:
                logging.error(f"Error posting order: {e} – {post_response.text}")
        time.sleep(1)




if __name__ == "__main__":
    args = parse_args()
    run_strategy(args.strategy_id, args.feed_file)
