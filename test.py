from playwright.sync_api import sync_playwright
import time

ETH_AMOUNT = "1"  # quantità di BNB da scambiare
OUTPUT_TOKEN = "SPS"  # solo per stampa

def get_quote():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        page = browser.new_page()

        print("🌐 Apro PancakeSwap...")
        # URL con token di output già preimpostato (SPS in questo caso)
        url = "https://pancakeswap.finance/swap?chain=bsc&outputCurrency=0x1633b7157e7638C4d6593436111Bf125Ee74703F&inputCurrency=0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
        page.goto(url, wait_until="networkidle")

        # ----------------------------
        # 1. Chiudi banner cookie se presente
        # ----------------------------
        try:
            page.wait_for_selector('button:has-text("Accept all cookies")', timeout=5000)
            page.click('button:has-text("Accept all cookies")')
            print("🍪 Cookie banner chiuso!")
        except:
            print("Nessun banner cookie trovato.")

        # ----------------------------
        # 2. Inserisci la quantità di ETH
        # ----------------------------
        print(f"✏️ Inserisco {ETH_AMOUNT} ETH come importo di input...")
        # Primo input è quello per BNB
        page.wait_for_selector('input[title="Token Amount"]', timeout=15000)
        input_boxes = page.locator('input[title="Token Amount"]')

        # Riempio il primo input (ETH)
        input_boxes.nth(0).fill(ETH_AMOUNT)

        # ----------------------------
        # 3. Aspetta il calcolo dell'importo di output
        # ----------------------------
        print("⏳ Attendo calcolo dello swap...")
        # Il secondo input è quello di output
        for i in range(15):  # 15 tentativi, circa 15 secondi
            value = input_boxes.nth(1).get_attribute("value")
            if value and float(value) > 0:
                print(f"💰 Risultato swap: {value} {OUTPUT_TOKEN}")
                break
            time.sleep(1)
        else:
            print("❌ Timeout: non sono riuscito a leggere il risultato dello swap.")

        # ----------------------------
        # 4. Screenshot di debug
        # ----------------------------
        page.screenshot(path="pancake_swap_result.png")
        print("📸 Screenshot salvato come pancake_swap_result.png")

        browser.close()

get_quote()
