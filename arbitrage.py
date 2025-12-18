import json
import requests
import os
import bridge

"""
# Get credentias from Secrets
USER_ID = os.getenv("USER_ID")
if not USER_ID:
    raise ValueError("USER_ID not found")
"""

USER_ID = 500357318613925889


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


def get_prices(tokens, session: requests.Session):
    prices = {}
    for token in tokens:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies=usd"
        price = get_response("GET", url, session)
        prices[token] = price[token]["usd"]

    return prices


def get_hive_price(session: requests.Session):
    urls = [
        "https://api.deathwing.me",
        "https://api.hive.blog",
        "https://hive-api.arcange.eu",
        "https://api.openhive.network",
    ]
    for url in urls:
        data = {"jsonrpc": "2.0", "method": "market_history_api.get_ticker", "id": 1}
        hive_price = get_response("POST", url, json=data).get("result", [], session)
        if not hive_price or len(hive_price) == 0:
            continue
        return hive_price["latest"]


def notification(content):
    webhook_url = "https://discord.com/api/webhooks/1359216089023906063/9PLtNmPUoSwm8UUStyxZzpxVjALWFdKcULtRF3kBJVBzBsVywnXZ4OmvInk8Tt5IhQdW"
    message = {
        "content": f"{content}! <@{USER_ID}>",
        "allowed_mentions": {"users": [USER_ID]},
    }
    get_response("POST", webhook_url, session, json=message)


def load_rules(filepath="rules.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


RULES = load_rules()


def get_threshold(token_max, token_min, percent_diff):

    # ---- 1) Regola per coppia specifica ----
    pair_key = f"{token_max}-{token_min}"
    if pair_key in RULES["pairs"]:
        return percent_diff >= RULES["pairs"][pair_key]

    # ---- 2) Regola se il token maggiore ha una soglia ----
    if token_max in RULES["when_max"]:
        return percent_diff >= RULES["when_max"][token_max]

    # ---- 3) Regola se il token minore ha una soglia ----
    if token_min in RULES["when_min"]:
        return percent_diff >= RULES["when_min"][token_min]

    # ---- 4) Default ----
    return percent_diff >= RULES["default"]


def find_divergence(values_dict):
    print("\n" + ", ".join(f"{k}: {v}" for k, v in values_dict.items()))
    results = []
    keys = list(values_dict.keys())
    n = len(keys)

    for i in range(n):
        key_a = keys[i]
        val_a = values_dict[key_a]

        for j in range(i + 1, n):
            key_b = keys[j]
            val_b = values_dict[key_b]

            # Trova max e min
            if val_a >= val_b:
                max_key, max_val = key_a, val_a
                min_key, min_val = key_b, val_b
            else:
                max_key, max_val = key_b, val_b
                min_key, min_val = key_a, val_a

            percent_diff = (max_val - min_val) / max_val * 100 if max_val else 0

            if get_threshold(max_key, min_key, percent_diff):
                results.append(
                    {
                        "token_max": {"key": max_key, "value": max_val},
                        "token_min": {"key": min_key, "value": min_val},
                        "percent_diff": percent_diff,
                    }
                )

    results.sort(key=lambda x: x["percent_diff"], reverse=True)

    format_results(results)


def format_results(results):
    for r in results:
        max_token = r["token_max"]["key"]
        min_token = r["token_min"]["key"]
        percent_diff = r["percent_diff"]
        message = f'Acquista "{max_token}" ---> vendi "{min_token}" === differenza {percent_diff:.2f}%'
        print(message)
        notification(message)
    if not results:
        print("✅ Tutti i valori sono entro la soglia")


def compare_prices(tokens, session: requests.Session):
    hive_price = get_hive_price(session)
    prices = get_prices(tokens, session)

    dollars_hive = 100 / float(hive_price)
    dollars = {token: 50 / float(price) for token, price in prices.items()}

    # DEPRECATED
    """
    dollars_hive = (
        dollars["ethereum"]
        / float(get_he_price("SWAP.HIVE:SWAP.ETH", session))
        * 0.992
    )
    """

    spl_tokens = ["SWAP.HIVE:SPS", "SWAP.HIVE:DEC"]
    spl_prices = []
    for spl_token in spl_tokens:
        spl_price = get_he_price(spl_token, session)
        spl_prices.append(spl_price)

    sps_amount, dec_amount = (dollars_hive * float(price) for price in spl_prices)

    bridge.AMOUNT_IN = str(dollars["ethereum"])
    bscSPS, baseSPS, ethSPS, bscDEC, ethDEC = bridge.get_quote()

    sps_values = {
        "SPS": sps_amount,
        "bscSPS": bscSPS,
        "baseSPS": baseSPS,
        "ethSPS": ethSPS,
    }

    sps_outliers = find_divergence(sps_values)

    dec_values = {"DEC": dec_amount, "bscDEC": bscDEC, "ethDEC": ethDEC}

    dec_outliers = find_divergence(dec_values)


if __name__ == "__main__":
    tokens = ["ethereum"]
    with requests.Session() as session:
        compare_prices(tokens, session)
