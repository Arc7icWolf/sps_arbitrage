from playwright.sync_api import sync_playwright, TimeoutError
import time

AMOUNT_IN = 0.02  # quantità del token iniziale da scambiare
OUTPUT_TOKEN = "SPS"
ONEINCH_URL = "https://app.1inch.io/swap?src=56:ETH&dst=56:SPS"

def get_1inch_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)  # headless disattivato
        page = browser.new_page()
        
        print("🌐 Apro 1inch...")
        page.goto(ONEINCH_URL, wait_until="networkidle")

        # ----------------------------
        # 1. Apri selettore del token di output
        # ----------------------------
        print("🔍 Apro selettore del token di output...")
        try:
            page.wait_for_selector('a[data-id="swap-box.dst-token.dropdown-button"]', timeout=10000)
            page.locator('a[data-id="swap-box.dst-token.dropdown-button"]').click()
        except TimeoutError:
            print("❌ Errore nella selezione del token")
            browser.close()
            return

        # ----------------------------
        # 2. Inserisci l'indirizzo del token di destinazione
        # ----------------------------
        print("✏️ Inserisco l'indirizzo del token di output...")
        page.wait_for_selector('input[data-id="swap-box.token-list-input"]', timeout=10000)
        page.locator('input[data-id="swap-box.token-list-input"]').fill("0x1633b7157e7638c4d6593436111bf125ee74703f")
        time.sleep(1)
        
        page.wait_for_selector('div.token-item.token-item__selectable', timeout=10000)
        page.locator('div.token-item.token-item__selectable').first.click()
        print(f"✅ Token {OUTPUT_TOKEN} selezionato!")

        # ----------------------------
        # 3. Pulsante "Continue" se presente
        # ----------------------------
        continue_button = page.locator('button:has-text("Continue")')
        if continue_button.count() > 0:
            continue_button.click()
            print("▶️ Pulsante 'Continue' cliccato")

        # ----------------------------
        # 4. Inserisci quantità nel campo 'from'
        # ----------------------------
        print(f"✏️ Inserito {AMOUNT_IN} nel campo 'from'")
        page.wait_for_selector('input[automation-id="tui-primitive-textfield__native-input"]', timeout=10000)
        page.locator('input[automation-id="tui-primitive-textfield__native-input"]').first.fill(str(AMOUNT_IN))

        # ----------------------------
        # 5. Recupera valore tasso di cambio (sempre per 1 unità)
        # ----------------------------
        print("⏳ Attendo tasso di cambio (per 1 unità)...")
        time.sleep(3)
        for i in range(30):  # massimo 30 secondi
            try:
                rate_span = page.locator('span[data-id="token-amount"]').first
                rate_text = rate_span.inner_text().strip().replace("\u202f", "")
                
                if rate_text and rate_text != "0":
                    print(rate_text)
                    rate_value = float(rate_text.replace(",", ""))
                    final_value = rate_value * AMOUNT_IN
                    print(f"💰 Tasso per 1 unità: {rate_value}")
                    print(f"💰 Output stimato per {AMOUNT_IN}: {final_value} {OUTPUT_TOKEN}")
                    break
            except Exception as e:
                print(f"⚠️ Tentativo {i+1}: {e}")
            
            time.sleep(1)
        else:
            print("❌ Timeout: non ho trovato il tasso di cambio")

        # ----------------------------
        # 6. Screenshot di debug
        # ----------------------------
        page.screenshot(path="1inch_swap_result.png")
        print("📸 Screenshot salvato come 1inch_swap_result.png")

        browser.close()

if __name__ == "__main__":
    get_1inch_quote()
