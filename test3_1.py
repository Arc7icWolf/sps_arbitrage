''' ISTRUZIONI per bypassare usare headless=False su VSC Online
1) sudo apt-get update && sudo apt-get install -y xvfb
2) xvfb-run -s "-screen 0 1920x1080x24" python test3_1.py
'''

from playwright.sync_api import sync_playwright
import time
import sys

AMOUNT_IN = "1"         # quantità di WETH da scambiare
OUTPUT_TOKEN = "SPS"  # simbolo del token di output per stampa

UNISWAP_URL = (
    "https://app.uniswap.org/swap?"
    "inputCurrency=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2&"
    "outputCurrency=0x00813E3421E1367353BfE7615c7f7f133C89df74&chain=1"
)

def get_uniswap_quote():
    with sync_playwright() as p:
        print("🌐 Avvio browser...")
        
        # ✅ Modalità visibile, ma simulata tramite xvfb-run
        browser = p.chromium.launch(
            headless=False,  # Ora il browser viene eseguito in modalità normale
            slow_mo=200,     # Aggiunge un leggero ritardo tra le azioni
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.new_page()
        page.set_default_timeout(60000)  # Timeout globale di 60s

        # Fase di "warm-up" per evitare il bug del primo caricamento
        page.goto("https://example.com", wait_until="domcontentloaded")

        print("🌐 Apro Uniswap...")
        page.goto(UNISWAP_URL, wait_until="domcontentloaded", timeout=30000)

        # Gestisci eventuali pop-up o consensi (es. cookie)
        try:
            consent_button = page.query_selector(
                'button[data-testid="cookie-consent-accept"], '
                'button:has-text("Accept"), '
                'button:has-text("I understand")'
            )
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
            page.wait_for_selector(input_in_selector, state="attached", timeout=90000)
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
            page.evaluate(
                "element => element.dispatchEvent(new Event('input', { bubbles: true }))",
                input_in
            )
        except Exception as e:
            print(f"❌ Errore durante l'inserimento del valore: {str(e)}")
            page.screenshot(path="uniswap_error.png")
            browser.close()
            return

        # Attendi calcolo output
        print("⏳ Attendo calcolo del risultato dello swap...")
        time.sleep(3)
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
