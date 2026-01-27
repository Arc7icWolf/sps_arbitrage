import requests

USER_ID = "500357318613925889"

WEBHOOK_URL = "https://discord.com/api/webhooks/1359216089023906063/9PLtNmPUoSwm8UUStyxZzpxVjALWFdKcULtRF3kBJVBzBsVywnXZ4OmvInk8Tt5IhQdW"


def notify(content: str):
    payload = {
        "content": f"{content}! <@{USER_ID}>",
        "allowed_mentions": {"users": [USER_ID]},
    }

    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        if r.status_code == 204:
            print("Notifica inviata")
    except requests.RequestException as e:
        print(f"Errore notifica: {e}")
