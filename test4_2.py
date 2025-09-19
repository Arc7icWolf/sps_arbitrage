from playwright.sync_api import sync_playwright, TimeoutError
import time

AMOUNT_IN = 0.02
OUTPUT_TOKEN = "SPS"
ONEINCH_URL = "https://app.1inch.io/swap?src=56:ETH&dst=56:SPS"

def get_1inch_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        page = browser.new_page()

        print("🌐 Apro 1inch...")
        page.goto(ONEINCH_URL, wait_until="networkidle")

        # Apri selettore del token di output
        print("🔍 Apro selettore del token di output...")
        try:
            page.wait_for_selector('a[data-id="swap-box.dst-token.dropdown-button"]', timeout=10000)
            page.locator('a[data-id="swap-box.dst-token.dropdown-button"]').click()
        except TimeoutError:
            print("❌ Errore nella selezione del token")
            browser.close()
            return

        # Inserisci indirizzo token di output
        print("✏️ Inserisco l'indirizzo del token di output...")
        page.wait_for_selector('input[data-id="swap-box.token-list-input"]', timeout=10000)
        page.locator('input[data-id="swap-box.token-list-input"]').fill("0x1633b7157e7638c4d6593436111bf125ee74703f")
        time.sleep(1)
        page.wait_for_selector('div.token-item.token-item__selectable', timeout=10000)
        page.locator('div.token-item.token-item__selectable').first.click()
        print(f"✅ Token {OUTPUT_TOKEN} selezionato!")

        # Pulsante "Continue" se presente
        continue_button = page.locator('button:has-text("Continue")')
        if continue_button.count() > 0:
            continue_button.click()
            print("▶️ Pulsante 'Continue' cliccato")

        # Inserisci quantità nel campo 'from'
        print(f"✏️ Inserito {AMOUNT_IN} nel campo 'from'")
        page.wait_for_selector('input[automation-id="tui-primitive-textfield__native-input"]', timeout=10000)
        page.locator('input[automation-id="tui-primitive-textfield__native-input"]').first.fill(str(AMOUNT_IN))

        # Recupera valore tasso di cambio stabile
        print("⏳ Attendo tasso di cambio stabile (per 1 unità)...")
        rate_span = page.locator('span[data-id="token-amount"]').first
        prev_value, stable_count = None, 0
        rate_value = None

        end_time = time.time() + 10  # timeout 10 sec
        while time.time() < end_time:
            try:
                text = rate_span.inner_text().strip().replace("\u202f", "")
                if text and text != prev_value:
                    prev_value = text
                    stable_count = 0
                else:
                    stable_count += 1
                    if stable_count >= 2:
                        rate_value = float(text.replace(",", ""))
                        break
            except:
                pass
            time.sleep(0.2)

        if rate_value:
            final_value = rate_value * AMOUNT_IN
            print(f"💰 Tasso per 1 unità: {rate_value}")
            print(f"💰 Output stimato per {AMOUNT_IN}: {final_value} {OUTPUT_TOKEN}")
        else:
            print("❌ Timeout: tasso di cambio non trovato")

        browser.close()

if __name__ == "__main__":
    get_1inch_quote()
