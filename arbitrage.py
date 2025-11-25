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


def notification(content):
    webhook_url = "https://discord.com/api/webhooks/1359216089023906063/9PLtNmPUoSwm8UUStyxZzpxVjALWFdKcULtRF3kBJVBzBsVywnXZ4OmvInk8Tt5IhQdW"
    message = {
        "content": f"{content}! <@{USER_ID}>",
        "allowed_mentions": {"users": [USER_ID]},
    }
    get_response("POST", webhook_url, session, json=message)


def find_divergence(values_dict, threshold=3):
    print("\n" + ", ".join(f"{key}: {value}" for key, value in values_dict.items()))
    max_key = max(values_dict, key=values_dict.get)
    max_value = values_dict[max_key]    

    outliers = []
    for key, value in values_dict.items():
        if key == "ethSPS" or max_key == "ethSPS":
            threshold = 6
        elif key == "ethDEC" or max_key == "ethDEC":
            threshold = 5
        else:
            threshold = 3         
        diff_percent = ((max_value - value) / max_value) * 100
        if diff_percent > threshold:
            outliers.append({"name": key, "value": value, "diff_percent": diff_percent})

    if not outliers and "bscDEC" in values_dict:
        threshold = 3
        max_key = max(['bscDEC', 'DEC'], key=values_dict.get)
        max_value = values_dict[max_key]

        for key, value in values_dict.items():
            if key == "ethDEC":
                continue         
            diff_percent = ((max_value - value) / max_value) * 100
            if diff_percent > threshold:
                outliers.append({"name": key, "value": value, "diff_percent": diff_percent})

    if not outliers and "bscSPS" in values_dict:
        threshold = 3
        max_key = max(['bscSPS', 'baseSPS', 'SPS'], key=values_dict.get)
        max_value = values_dict[max_key]

        for key, value in values_dict.items():
            if key == "spsDEC":
                continue         
            diff_percent = ((max_value - value) / max_value) * 100
            if diff_percent > threshold:
                outliers.append({"name": key, "value": value, "diff_percent": diff_percent})

    outliers_dict = {"max_name": max_key, "max_value": max_value, "outliers": outliers}

    calculate_divergence(outliers_dict)


def calculate_divergence(result):
    if result["outliers"]:
        print(f"\nValore massimo: {result['max_name']} = {result['max_value']}")
        print("Valori fuori soglia:")
        for outlier in result["outliers"]:
            print(
                f"- {outlier['name']} = {outlier['value']} "
                f"(differenza {outlier['diff_percent']:.2f}%)"
            )
            if outlier['diff_percent'] > 90:
                continue
            notification(
                f"Valore massimo: {result['max_name']} = {result['max_value']}\n"
                f"Valori fuori soglia:\n"
                f"- {outlier['name']} = {outlier['value']} "
                f"(differenza {outlier['diff_percent']:.2f}%)"
            )
    else:
        print("✅ Tutti i valori sono entro la soglia")


def compare_prices(tokens, session: requests.Session):
    prices = get_prices(tokens, session)
    dollars = {token: 50 / float(price) for token, price in prices.items()}

    dollars_hive = (
        dollars["ethereum"]
        / float(get_he_price("SWAP.HIVE:SWAP.ETH", session))
        * 0.992
    )

    spl_tokens = ["SWAP.HIVE:SPS", "SWAP.HIVE:DEC"]
    spl_prices = []
    for spl_token in spl_tokens:
        spl_price = get_he_price(spl_token, session)
        spl_prices.append(spl_price)

    sps_amount, dec_amount = (
        dollars_hive * float(price) for price in spl_prices
    )

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
    tokens = ["hive", "ethereum"]
    with requests.Session() as session:
        compare_prices(tokens, session)
