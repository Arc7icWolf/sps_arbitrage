"""ISTRUZIONI per usare headless=False su VSC Online
1) sudo apt-get update && sudo apt-get install -y xvfb
2) python3 -m playwright install chromium
3) python3 -m playwright install-deps
4) xvfb-run -s "-screen 0 1920x1080x24" python arbitrage.py
"""

from playwright.sync_api import sync_playwright, TimeoutError
import time
import json

AMOUNT_IN = "1"

def simulate_swap(inputs):
    # print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
    inputs.nth(0).fill(AMOUNT_IN)

    # print("⏳ Attendo calcolo dello swap...")
    time.sleep(3)
    for i in range(10):
        value = inputs.nth(1).get_attribute("value")
        if value and float(value) > 0:
            # print(f"💰 Risultato swap: {value}")
            return float(value)
        time.sleep(1)
    else:
        print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")
        return 0


def run_dex_query(browser, url, simulate_fn, dex, wait_selector, input_selector, max_attempts=10):
    """
    browser      = istanza Playwright
    url          = URL della pagina
    simulate_fn  = funzione personalizzata del DEX (inputs, page, key) -> amount
    """
    for attempt in range(max_attempts):
        print(f"Procedo con il tentativo n. {attempt + 1}...")
        page = browser.new_page()
        page.set_default_timeout(90000)

        page.goto(url, wait_until="domcontentloaded")

        try:
            page.wait_for_selector(wait_selector, timeout=30000)
            inputs = page.locator(input_selector)
        except TimeoutError:
            page.close()
            print("La pagina non risponde... ritento")
            continue

        # 🟢 Chiamata alla logica specifica del DEX
        print("Simulo lo swap...")
        amount = simulate_fn(inputs)

        page.screenshot(path=f"{dex}_attempt_{attempt + 1}.png")
        page.close()

        if float(amount) > 1:
            return amount

        print("⏳ Non pronto, valore = 0. Riprovo tra 3s...")
        time.sleep(3)

    print("⛔ Timeout: nessun valore valido.")
    return 0


def pancakeswap(browser, url):
    DEX = "pancakeswap"
    WAIT_SELECTOR = "input[title='Token Amount']"
    INPUT_SELECTOR = "input[title='Token Amount']"

    def simulate_pcs(inputs):
        # Eventuale logica personalizzata
        return simulate_swap(inputs)
    print("Avvio pancakeswap")
    return run_dex_query(browser, url, simulate_pcs, DEX, WAIT_SELECTOR, INPUT_SELECTOR)


def aerodrome(browser, url):
    DEX = "aerodrome"
    WAIT_SELECTOR = "input[data-testid^='swapper-asset-input']"
    INPUT_SELECTOR = "input[data-testid^='swapper-asset-input']"

    def simulate_aero(inputs):
        # Eventuale logica personalizzata
        return simulate_swap(inputs)
    print("Avvio aerodrome")
    return run_dex_query(browser, url, simulate_aero, DEX, WAIT_SELECTOR, INPUT_SELECTOR)


def uniswap(browser, url):
    DEX = "uniswap"
    WAIT_SELECTOR = "input[data-testid='amount-input-in']"
    INPUT_SELECTOR = "input[data-testid^='amount-input']"

    def simulate_uni(inputs):
        # Eventuale logica personalizzata
        return simulate_swap(inputs)
    print("Avvio uniswap")
    return run_dex_query(browser, url, simulate_uni, DEX, WAIT_SELECTOR, INPUT_SELECTOR)


def get_quote():
    with sync_playwright() as p:
        print("🌐 Avvio browser...")

        browser = p.chromium.launch(
            headless=False,
            slow_mo=200,  # Aggiunge un leggero ritardo tra le azioni
            args=["--disable-blink-features=AutomationControlled"],
        )

        with open("routes.json") as f:
            routes = json.load(f)

        tokens_amount = []

        for _, route_list in routes.items():
            for route in route_list:
                print(f"🌐 Apro {route['dex']}...")
                match route["dex"]:
                    case "pancakeswap":
                        amount = pancakeswap(browser, route["url"])
                    case "aerodrome":
                        amount = aerodrome(browser, route["url"])
                    case "uniswap":
                        amount = uniswap(browser, route["url"])

                tokens_amount.append(amount)

        browser.close()

        return tokens_amount


if __name__ == "__main__":
    get_quote()
