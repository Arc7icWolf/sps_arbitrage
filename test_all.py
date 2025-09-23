from playwright.sync_api import sync_playwright, TimeoutError
import time
import sys

AMOUNT_IN = "1"
OUTPUT_TOKEN = "SPS"
DEX = [
    {'dex': "pancakeswap", 'url': "https://pancakeswap.finance/swap?chain=bsc&outputCurrency=0x1633b7157e7638C4d6593436111Bf125Ee74703F&inputCurrency=0x2170Ed0880ac9A755fd29B2688956BD959F933F8"},
    {'dex': "aerodrome", 'url': "https://aerodrome.finance/swap?from=0x4200000000000000000000000000000000000006&to=0x578661e9a09eee6b2cd97d4ded1ccbae7b8516b9&chain0=8453&chain1=8453"},
    {'dex': "uniswap", 'url': "https://app.uniswap.org/swap?inputCurrency=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2&outputCurrency=0x00813E3421E1367353BfE7615c7f7f133C89df74&chain=1"},
    {'dex': "1inch", 'url': "https://app.1inch.io/swap?src=56:ETH&dst=56:SPS"}
]


def simulate_swap(inputs):
    # Riempio il primo input (ETH)
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
    print(f"✏️ Inserisco {AMOUNT_IN} ETH come importo di input...")
    page.wait_for_selector('input[title="Token Amount"]', timeout=15000)
    inputs = page.locator('input[title="Token Amount"]')

    simulate_swap(inputs)


def aerodrome(page):
    print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
    page.wait_for_selector('input[data-testid^="swapper-asset-input"]', timeout=15000)
    inputs = page.locator('input[data-testid^="swapper-asset-input"]')

    simulate_swap(inputs)


def uniswap(page):
    # Attendi caricamento degli input
    print(f"✏️ Inserisco {AMOUNT_IN} nel campo 'from'...")
    page.wait_for_selector('input[data-testid="amount-input-in"]', timeout=15000)
    inputs = page.locator('input[data-testid^="amount-input"]')
    
    simulate_swap(inputs)


def inch(page):
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
        final_value = rate_value * float(AMOUNT_IN)
        print(f"💰 Tasso per 1 unità: {rate_value}")
        print(f"💰 Output stimato per {AMOUNT_IN}: {final_value} {OUTPUT_TOKEN}")
    else:
        print("❌ Timeout: tasso di cambio non trovato")


def get_quote():
    with sync_playwright() as p:
        print("🌐 Avvio browser...")
        
        browser = p.chromium.launch(
            headless=False,  
            slow_mo=200,     # Aggiunge un leggero ritardo tra le azioni
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.new_page()
        page.set_default_timeout(60000)  # Timeout globale di 60s

        # Fase di "warm-up" per evitare il bug del primo caricamento
        page.goto("https://example.com", wait_until="domcontentloaded")

        for d in DEX:
            print(f"🌐 Apro {d['dex']}...")
            page.goto(d['url'], wait_until="domcontentloaded", timeout=30000)

            match d['dex']:
                case "pancakeswap":
                    pancakeswap(page)
                case "aerodrome":
                    aerodrome(page)
                case "uniswap":
                    uniswap(page)
                case "1inch":
                    inch(page)
       

            # ----------------------------
            # Screenshot di debug
            # ----------------------------
            page.screenshot(path=f"{d['dex']}_result.png")
            print(f"📸 Screenshot salvato come {d['dex']}_result.png")

        browser.close()



if __name__ == "__main__":
    get_quote()