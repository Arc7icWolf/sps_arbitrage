from playwright.sync_api import sync_playwright
import time

AMOUNT_IN = "1"         # quantità di WETH da scambiare
OUTPUT_TOKEN = "TARGET"  # simbolo del token di output per stampa

UNISWAP_URL = (
    "https://app.uniswap.org/swap?"
    "inputCurrency=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2&"
    "outputCurrency=0x00813E3421E1367353BfE7615c7f7f133C89df74&"
    "chain=1"
)

def get_uniswap_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=1000)  # headless=False per debug
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        print("🌐 Apro Uniswap...")
        try:
            page.goto(UNISWAP_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"❌ Errore caricamento pagina: {str(e)}")
            page.screenshot(path="uniswap_error.png")
            browser.close()
            return

        # Gestisci eventuali pop-up o consensi (es. cookie)
        try:
            consent_button = page.query_selector('button[data-testid="cookie-consent-accept"], button:has-text("Accept"), button:has-text("I understand")')
            if consent_button:
                consent_button.click()
                print("✅ Consenso cookie accettato")
                time.sleep(2)  # Attendi aggiornamento pagina
        except:
            print("ℹ️ Nessun pop-up di consenso trovato")

        # Attendi caricamento degli input
        print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
        input_in_selector = 'input[data-testid="amount-input-in"]'
        input_out_selector = 'input[data-testid="amount-input-out"]'
        try:
            page.wait_for_selector(input_in_selector, state="attached", timeout=90000)  # 90 secondi
            input_in = page.query_selector(input_in_selector)
            input_out = page.query_selector(input_out_selector)
            if not input_in or not input_out:
                print("❌ Errore: uno o entrambi gli input non trovati")
                page.screenshot(path="uniswap_error.png")
                browser.close()
                return
        except Exception as e:
            print(f"❌ Timeout: input 'from' non trovato - Errore: {str(e)}")
            page.screenshot(path="uniswap_error.png")
            browser.close()
            return

        # Inserisci valore nel campo 'from' e trigger evento
        try:
            input_in.fill("")
            input_in.fill(AMOUNT_IN)
            page.evaluate("element => element.dispatchEvent(new Event('input', { bubbles: true }))", input_in)
        except Exception as e:
            print(f"❌ Errore durante l'inserimento del valore: {str(e)}")
            page.screenshot(path="uniswap_error.png")
            browser.close()
            return

        # Attendi calcolo output
        print("⏳ Attendo calcolo del risultato dello swap...")
        result = None
        for _ in range(30):
            try:
                value = input_out.input_value()
                if value and float(value) > 0:
                    result = value
                    break
            except:
                pass
            time.sleep(1)

        if result:
            print(f"💰 Risultato stimato: {result} {OUTPUT_TOKEN}")
        else:
            print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")

        # Screenshot di debug
        try:
            page.screenshot(path="uniswap_swap_result.png")
            print("📸 Screenshot salvato come uniswap_swap_result.png")
        except Exception as e:
            print(f"❌ Errore durante lo screenshot: {str(e)}")

        browser.close()

if __name__ == "__main__":
    get_uniswap_quote()