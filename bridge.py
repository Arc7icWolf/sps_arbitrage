"""ISTRUZIONI per usare headless=False su VSC Online
1) sudo apt-get update && sudo apt-get install -y xvfb
2) xvfb-run -s "-screen 0 1920x1080x24" python bridge.py
"""

from playwright.sync_api import sync_playwright
import time
import json

AMOUNT_IN = "1"

def simulate_swap(inputs, key):
    # print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
    inputs.nth(0).fill(AMOUNT_IN)

    # print("⏳ Attendo calcolo dello swap...")
    time.sleep(3)
    for i in range(15):
        value = inputs.nth(1).get_attribute("value")
        if value and float(value) > 0:
            # print(f"💰 Risultato swap: {value} {key.upper()}")
            return float(value)
        time.sleep(1)
    else:
        print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")
        return 0


def pancakeswap(page, key):
    page.wait_for_selector('input[title="Token Amount"]', timeout=30000)
    inputs = page.locator('input[title="Token Amount"]')
    
    for _ in range(20):
        amount = simulate_swap(inputs, key)
        if float(amount) != 0:
            return amount

        print("⏳ PancakeSwap non pronto, valore = 0. Riprovo tra 3s...")
        page.wait_for_timeout(3000)

    print("⛔ Timeout: PancakeSwap non ha fornito un valore valido.")
    return None


def aerodrome(page, key):
    try:
        page.wait_for_selector('input[data-testid^="swapper-asset-input"]', timeout=15000)
        inputs = page.locator('input[data-testid^="swapper-asset-input"]')
    except PlaywrightTimeoutError:
        return 0

    amount = simulate_swap(inputs, key)
    return amount


def uniswap(page, key):
    page.wait_for_selector('input[data-testid="amount-input-in"]', timeout=15000)
    inputs = page.locator('input[data-testid^="amount-input"]')

    amount = simulate_swap(inputs, key)
    return amount


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

        tokens_amount = []

        for key, route_list in routes.items():
            for route in route_list:
                print(f"🌐 Apro {route['dex']}...")
                page.goto(route["url"], wait_until="domcontentloaded", timeout=30000)

                match route["dex"]:
                    case "pancakeswap":
                        amount = pancakeswap(page, key)
                    case "aerodrome":
                        amount = aerodrome(page, key)
                    case "uniswap":
                        amount = uniswap(page, key)

                tokens_amount.append(amount)

                # Screenshot di debug
                # page.screenshot(path=f"{route['dex']}_result.png")
                # print(f"📸 Screenshot salvato come {route['dex']}_result.png")

        browser.close()

        return tokens_amount


if __name__ == "__main__":
    get_quote()
