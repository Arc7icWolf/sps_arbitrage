"""ISTRUZIONI per usare headless=False su VSC Online
1) sudo apt-get update && sudo apt-get install -y xvfb
2) xvfb-run -s "-screen 0 1920x1080x24" python test_all.py
"""

from playwright.sync_api import sync_playwright
import time
import json

AMOUNT_IN = "0.025"

def simulate_swap(inputs, key):
    print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
    inputs.nth(0).fill(AMOUNT_IN)

    print("⏳ Attendo calcolo dello swap...")
    time.sleep(3)
    # Il secondo input è quello di output
    for i in range(15):  # 15 tentativi, circa 15 secondi
        value = inputs.nth(1).get_attribute("value")
        if value and float(value) > 0:
            print(f"💰 Risultato swap: {value} {key.upper()}")
            break
        time.sleep(1)
    else:
        print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")


def pancakeswap(page, key):
    page.wait_for_selector('input[title="Token Amount"]', timeout=15000)
    inputs = page.locator('input[title="Token Amount"]')

    simulate_swap(inputs, key)


def aerodrome(page, key):
    page.wait_for_selector('input[data-testid^="swapper-asset-input"]', timeout=15000)
    inputs = page.locator('input[data-testid^="swapper-asset-input"]')

    simulate_swap(inputs, key)


def uniswap(page, key):
    page.wait_for_selector('input[data-testid="amount-input-in"]', timeout=15000)
    inputs = page.locator('input[data-testid^="amount-input"]')

    simulate_swap(inputs, key)


def get_quote():
    with sync_playwright() as p:
        print("🌐 Avvio browser...")

        browser = p.chromium.launch(
            headless=False,
            slow_mo=200,  # Aggiunge un leggero ritardo tra le azioni
            args=["--disable-blink-features=AutomationControlled"],
        )

        page = browser.new_page()
        page.set_default_timeout(90000)  # Timeout globale di 90s

        # Fase di "warm-up"
        page.goto("https://example.com", wait_until="domcontentloaded")

        with open("routes.json") as f:
            routes = json.load(f)

        for key, route_list in routes.items():
            for route in route_list:
                print(f"🌐 Apro {route['dex']}...")
                page.goto(route["url"], wait_until="domcontentloaded", timeout=30000)

                match route["dex"]:
                    case "pancakeswap":
                        pancakeswap(page, key)
                    case "aerodrome":
                        aerodrome(page, key)
                    case "uniswap":
                        uniswap(page, key)

                # Screenshot di debug
                # page.screenshot(path=f"{d['dex']}_result.png")
                # print(f"📸 Screenshot salvato come {d['dex']}_result.png")

        browser.close()


if __name__ == "__main__":
    get_quote()
