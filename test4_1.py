from playwright.sync_api import sync_playwright, TimeoutError
import time

AMOUNT_IN = "1"  # quantità del token iniziale da scambiare
OUTPUT_TOKEN = "SPS"  # simbolo del token di output
ONEINCH_URL = "https://app.1inch.io/swap?src=56:ETH&dst=56:SPS"

def get_1inch_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
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
        time.sleep(1)  # lascia il tempo alla lista di aggiornarsi
        
        # Clicca sul token corretto appena compare
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
        page.locator('input[automation-id="tui-primitive-textfield__native-input"]').first.fill(AMOUNT_IN)
        
        # ----------------------------
        # 5. Attendi calcolo del risultato
        # ----------------------------
        print("⏳ Attendo calcolo del risultato dello swap...")
        for i in range(30):  # fino a ~30 secondi
            try:
                output_span = page.locator('div.source-token-amount-input-container span.t-ghost').first
                value = output_span.inner_text().strip().replace("\u202f", "")
                if value and float(value.replace(',', '')) > 0:
                    print(f"💰 Risultato stimato: {value} {OUTPUT_TOKEN}")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("❌ Timeout: risultato swap non trovato")
        
        # ----------------------------
        # 6. Screenshot di debug
        # ----------------------------
        page.screenshot(path="1inch_swap_result.png")
        print("📸 Screenshot salvato come 1inch_swap_result.png")
        
        browser.close()

if __name__ == "__main__":
    get_1inch_quote()
