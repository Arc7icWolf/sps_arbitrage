import json
import requests

HIVE_ENGINE_NODE = "https://api.hive-engine.com/rpc/contracts"
# HIVE_ENGINE_NODE_2 = 'https://api2.hive-engine.com/rpc/contracts'


def get_response(payload, session: requests.Session):
    url = HIVE_ENGINE_NODE
    try:
        request = requests.Request("POST", url=url, json=payload).prepare()
        response = session.send(request, allow_redirects=False)
        response.raise_for_status()
        response = response.json()
        return response
    except requests.exceptions.RequestException as e:
        print(f"HTTP error: {e}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {}


def get_pool_price(session: requests.Session):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "find",
        "params": {
            "contract": "marketpools",
            "table": "pools",
            "query": {"tokenPair": "SWAP.GIFU:SWAP.HIVE"},
            "limit": 1,
        },
    }
    pool_price = get_response(payload, session)
    return pool_price["result"][0]["basePrice"]


def get_orders(session: requests.Session):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "find",
        "params": {
            "contract": "market",
            "table": "metrics",
            "query": {"symbol": "SWAP.GIFU"},
            "limit": 5,
        },
    }
    buy_order = get_response(payload, session)
    return buy_order["result"][0]


def compare_prices():
    with requests.Session() as session:
        pool_price = get_pool_price(session)
        order = get_orders(session)
        highest_bid = order["highestBid"]
        lowest_ask = order["lowestAsk"]
        buy_spread = float(pool_price) - float(highest_bid)
        sell_spread = float(pool_price) - float(lowest_ask)
        if buy_spread < 0:
            print(f"Pool price is lower than lowest buy order: {buy_spread:.08f}\n")
        elif sell_spread > 0:
            print(f"Pool price is higher than highest sell order: {sell_spread:.08f}")
        else:
            print("No arbitrage opportunities on the horizon...")


if __name__ == "__main__":
    compare_prices()
