from playwright.sync_api import sync_playwright
import time

AMOUNT_IN = "1"        # quantità del token iniziale da scambiare
OUTPUT_TOKEN = "TARGET"  # solo per stampa (puoi mettere simbolo reale)

AERODROME_URL = (
    "https://aerodrome.finance/swap?"
    "from=0x4200000000000000000000000000000000000006&"
    "to=0x578661e9a09eee6b2cd97d4ded1ccbae7b8516b9&"
    "chain0=8453&chain1=8453"
)

def get_aerodrome_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        page = browser.new_page()

        print("🌐 Apro Aerodrome...")
        page.goto(AERODROME_URL, wait_until="networkidle")

        # ----------------------------
        # 1. Inserisci quantità iniziale
        # ----------------------------
        print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
        page.wait_for_selector('input[data-testid^="swapper-asset-input"]', timeout=15000)
        inputs = page.locator('input[data-testid^="swapper-asset-input"]')

        # Primo input = token iniziale
        inputs.nth(0).fill(AMOUNT_IN)

        # ----------------------------
        # 2. Attendi calcolo output
        # ----------------------------
        print("⏳ Attendo calcolo del risultato dello swap...")
        for i in range(15):  # fino a ~15 secondi
            value = inputs.nth(1).get_attribute("value")  # secondo input = output
            if value and float(value) > 0:
                print(f"💰 Risultato stimato: {value} {OUTPUT_TOKEN}")
                break
            time.sleep(1)
        else:
            print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")

        # ----------------------------
        # 3. Screenshot di debug
        # ----------------------------
        page.screenshot(path="aerodrome_swap_result.png")
        print("📸 Screenshot salvato come aerodrome_swap_result.png")

        browser.close()

if __name__ == "__main__":
    get_aerodrome_quote()
