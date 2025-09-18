from playwright.sync_api import sync_playwright
import time

AMOUNT_IN = "1"          # quantità del token iniziale da scambiare
OUTPUT_TOKEN = "SPS"     # simbolo per stampa

# URL già con token di input impostato (ETH su BSC nell'esempio)
ONEINCH_URL = (
    "https://app.1inch.io/swap?src=56:ETH&dst=56:SPS"
)

def get_1inch_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        page = browser.new_page()

        print("🌐 Apro 1inch...")
        page.goto(ONEINCH_URL, wait_until="networkidle")

        # ----------------------------
        # 1. Apri selettore token output
        # ----------------------------
        print("🔍 Apro selettore del token di output...")
        try:
            page.wait_for_selector('a[data-id="swap-box.dst-token.dropdown-button"]', timeout=15000)
            page.locator('a[data-id="swap-box.dst-token.dropdown-button"]').click()
            time.sleep(1)  # breve pausa per caricamento lista token
        except:
            print("❌ Errore nell'aprire selettore token output")
            browser.close()
            return

        # ----------------------------
        # 2. Inserisci contract del token di output e selezionalo
        # ----------------------------
        TOKEN_OUTPUT_ADDRESS = "0x1633b7157e7638c4d6593436111bf125ee74703f"  # SPS
        try:
            page.wait_for_selector('input[data-id="swap-box.token-list-input"]', timeout=10000)
            input_token = page.locator('input[data-id="swap-box.token-list-input"]')
            input_token.fill(TOKEN_OUTPUT_ADDRESS)
            time.sleep(1)

            # seleziona il token dalla lista
            page.locator('div.token-item.token-item__selectable').first.click()
            print(f"✅ Token {OUTPUT_TOKEN} selezionato!")
        except:
            print("❌ Errore nella selezione del token di output")
            browser.close()
            return

        # ----------------------------
        # 3. Gestione eventuale pulsante Continue
        # ----------------------------
        try:
            time.sleep(1)
            continue_btn = page.locator('button:has-text("Continue")')
            if continue_btn.count() > 0 and continue_btn.is_visible():
                continue_btn.first.click()
                print("▶️ Pulsante 'Continue' cliccato")
        except:
            pass  # nessun pulsante Continue presente

        # ----------------------------
        # 4. Inserisci quantità token di input
        # ----------------------------
        try:
            page.wait_for_selector('input[automation-id="tui-primitive-textfield__native-input"]', timeout=10000)
            input_box = page.locator('input[automation-id="tui-primitive-textfield__native-input"]').first
            input_box.fill(AMOUNT_IN)
            print(f"✏️ Inserito {AMOUNT_IN} nel campo 'from'")
        except:
            print("❌ Timeout: input 'from' non trovato")
            browser.close()
            return

        # ----------------------------
        # 5. Attendi calcolo del risultato
        # ----------------------------
        print("⏳ Attendo calcolo del risultato dello swap...")
        try:
            # prendiamo il secondo input readonly del form
            output_box = page.locator('input[automation-id="tui-primitive-textfield__native-input"][readonly]').first

            for i in range(30):  # fino a ~30 secondi
                value = output_box.get_attribute("value")
                if value and float(value) > 0:
                    print(f"💰 Risultato stimato: {value} {OUTPUT_TOKEN}")
                    break
                time.sleep(1)
            else:
                print("❌ Timeout: risultato swap non trovato")
        except Exception as e:
            print(f"❌ Errore nella lettura del risultato: {e}")


        # ----------------------------
        # 6. Screenshot di debug
        # ----------------------------
        page.screenshot(path="1inch_swap_result.png")
        print("📸 Screenshot salvato come 1inch_swap_result.png")

        browser.close()


if __name__ == "__main__":
    get_1inch_quote()
