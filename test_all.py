''' ISTRUZIONI per bypassare usare headless=False su VSC Online
1) sudo apt-get update && sudo apt-get install -y xvfb
2) xvfb-run -s "-screen 0 1920x1080x24" python test_all.py
'''


from playwright.sync_api import sync_playwright, TimeoutError
import time
import sys

AMOUNT_IN = "0.025"
OUTPUT_TOKEN = "SPS"
DEX = [
    {
        "dex": "pancakeswap",
        "url": "https://pancakeswap.finance/swap?chain=bsc&outputCurrency=0x1633b7157e7638C4d6593436111Bf125Ee74703F&inputCurrency=0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
    },
    {
        "dex": "aerodrome",
        "url": "https://aerodrome.finance/swap?from=0x4200000000000000000000000000000000000006&to=0x578661e9a09eee6b2cd97d4ded1ccbae7b8516b9&chain0=8453&chain1=8453",
    },
    {
        "dex": "uniswap",
        "url": "https://app.uniswap.org/swap?inputCurrency=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2&outputCurrency=0x00813E3421E1367353BfE7615c7f7f133C89df74&chain=1",
    },
]


def simulate_swap(inputs):
    print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
    inputs.nth(0).fill(AMOUNT_IN)

    print("⏳ Attendo calcolo dello swap...")
    # Il secondo input è quello di output
    for i in range(15):  # 15 tentativi, circa 15 secondi
        value = inputs.nth(1).get_attribute("value")
        if value and float(value) > 0:
            print(f"💰 Risultato swap: {value} {OUTPUT_TOKEN}")
            break
        time.sleep(1)
    else:
        print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")


def pancakeswap(page):
    page.wait_for_selector('input[title="Token Amount"]', timeout=15000)
    inputs = page.locator('input[title="Token Amount"]')

    simulate_swap(inputs)


def aerodrome(page):
    page.wait_for_selector('input[data-testid^="swapper-asset-input"]', timeout=15000)
    inputs = page.locator('input[data-testid^="swapper-asset-input"]')

    simulate_swap(inputs)


def uniswap(page):
    page.wait_for_selector('input[data-testid="amount-input-in"]', timeout=15000)
    inputs = page.locator('input[data-testid^="amount-input"]')

    simulate_swap(inputs)


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

        for d in DEX:
            print(f"🌐 Apro {d['dex']}...")
            page.goto(d["url"], wait_until="domcontentloaded", timeout=30000)

            match d["dex"]:
                case "pancakeswap":
                    pancakeswap(page)
                case "aerodrome":
                    aerodrome(page)
                case "uniswap":
                    uniswap(page)

            # Screenshot di debug
            # page.screenshot(path=f"{d['dex']}_result.png")
            # print(f"📸 Screenshot salvato come {d['dex']}_result.png")

        browser.close()


if __name__ == "__main__":
    get_quote()
