import json
import requests
from decimal import Decimal
import configparser
import os
import sys

'''
config = configparser.ConfigParser()
config.read("config.ini")
user_id = config["DEFAULT"].get("user_id")
'''
'''
# Get credentias from Secrets
USER_ID = os.getenv("USER_ID")
if not USER_ID:
    raise ValueError("USER_ID not found")
'''

USER_ID = 132


def get_response(method, url, session: requests.Session, json=None):
    try:
        if method == "GET":
            response = session.get(url, allow_redirects=False)
        else:  # POST
            response = session.post(url, json=json, allow_redirects=False)
        response.raise_for_status()
        if response.status_code == 204:
            print("Notifica inviata con successo!")
        else:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP error: {e}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {}


def get_he_price(token, session: requests.Session):
    url = "https://api.hive-engine.com/rpc/contracts"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "find",
        "params": {
            "contract": "marketpools",
            "table": "pools",
            "query": {"tokenPair": token},
            "limit": 1,
        },
    }
    token_price = get_response("POST", url, session, json=payload)

    return token_price["result"][0]["basePrice"]


def get_maya_price(quantity, session: requests.Session):
    amount = Decimal(quantity)
    token_amount = int(amount * (10**8))
    url = (
        f"https://mayanode.mayachain.info/mayachain/quote/swap?"
        f"from_asset=ARB.ETH"
        f"&to_asset=ARB.LEO-0X93864D81175095DD93360FFA2A529B8642F76A6E"
        f"&amount={token_amount}"
        f"&destination=0x1EdF9F4d2e98A2eb5DFeeC7f07c2e8b6C3FFaA4E"
        f"&streaming_interval=3"
        f"&streaming_quantity=0"
        f"&liquidity_tolerance_bps=100"
        f"&affiliate_bps=45&affiliate=wr"
    )
    maya_price = get_response("GET", url, session)
    return maya_price


def get_prices(tokens, session: requests.Session):
    prices = {}
    for token in tokens:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies=usd"
        price = get_response("GET", url, session)
        prices[token] = price[token]["usd"]

    return prices


def notification(content):
    webhook_url = "https://discord.com/api/webhooks/1359216089023906063/9PLtNmPUoSwm8UUStyxZzpxVjALWFdKcULtRF3kBJVBzBsVywnXZ4OmvInk8Tt5IhQdW"
    message = {
        "content": f"{content}! <@{USER_ID}>",
        "allowed_mentions": {"users": [USER_ID]},
    }
    get_response("POST", webhook_url, session, json=message)


def compare_prices(tokens, session: requests.Session):
    prices = get_prices(tokens, session)
    one_hundred_dollars = {token: 100 / float(price) for token, price in prices.items()}

    leo_price = get_he_price("SWAP.HIVE:SPS", session)
    he_leo_amount = one_hundred_dollars['hive'] * float(leo_price) * 0.99

    print(he_leo_amount)

    maya_price = get_maya_price(one_hundred_dollars['ethereum'], session)
    arb_leo_amount = maya_price.get("expected_amount_out")

    if not arb_leo_amount:
        sys.exit("Arb Network halted")

    arb_leo_amount = int(arb_leo_amount) / (10**8)
    
    print(arb_leo_amount)

    threshold = 1.17
    fee = 0.895

    if he_leo_amount > arb_leo_amount * threshold:
        print("HIVE --> LEO --> ARB.LEO --> ETH")
        notification(f"H-E: {he_leo_amount}, ARB: {arb_leo_amount}. Sell {he_leo_amount * fee} on ARB")
    elif arb_leo_amount > he_leo_amount * threshold:
        print("ETH --> ARB.LEO --> LEO --> HIVE")
        notification(f"ARB: {arb_leo_amount}, H-E: {he_leo_amount}. Sell {arb_leo_amount * fee} on H-E")
    else:
        print("Nothing to see here")


if __name__ == "__main__":
    tokens = ["hive", "ethereum"]
    with requests.Session() as session:
        compare_prices(tokens, session)