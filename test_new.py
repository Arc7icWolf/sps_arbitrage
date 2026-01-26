from web3 import Web3

# ==============================
# RPC ENDPOINTS (pubblici)
# ==============================

RPC_BSC  = "https://bsc-dataseed.binance.org/"
RPC_BASE = "https://mainnet.base.org"
RPC_ETH  = "https://eth.llamarpc.com"

# ==============================
# INDIRIZZI CONTRATTI
# ==============================

BSC_POOL = Web3.to_checksum_address(
    "0x96e55d2d53b79D636166B23103552253E23B699E"
)

BASE_POOL = Web3.to_checksum_address(
    "0x726962F81eE8eFdC83266858B5bCf2146713A8Cf"
)

UNISWAP_V4_SINGLETON = Web3.to_checksum_address(
    "0x000000000004444c5dc75cB358380D2e3dE08A90"
)

# ==============================
# TOKEN ADDRESSES
# ==============================

SPS_BSC  = Web3.to_checksum_address(
    "0x1633b7157e7638C4d6593436111Bf125Ee74703F"
)
SPS_BASE = Web3.to_checksum_address(
    "0x578661E9A09Eee6b2cd97D4Ded1CCBaE7B8516B9"
)
SPS_ETH  = Web3.to_checksum_address(
    "0x00813E3421E1367353BfE7615c7f7f133C89df74"
)

WBNB_BSC = Web3.to_checksum_address(
    "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
)

USDC_BASE = Web3.to_checksum_address(
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
)

# ==============================
# ERC20 ABI MINIMALE
# ==============================

ERC20_ABI = [
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "owner", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "decimals",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
    },
]

# ==============================
# UTILITY
# ==============================

def erc20_balance(w3, token, holder):
    contract = w3.eth.contract(address=token, abi=ERC20_ABI)
    decimals = contract.functions.decimals().call()
    raw = contract.functions.balanceOf(holder).call()
    return raw / (10 ** decimals)

# ==============================
# MAIN
# ==============================

def main():
    w3_bsc  = Web3(Web3.HTTPProvider(RPC_BSC))
    w3_base = Web3(Web3.HTTPProvider(RPC_BASE))
    w3_eth  = Web3(Web3.HTTPProvider(RPC_ETH))

    # --- BSC ---
    sps_bsc  = erc20_balance(w3_bsc, SPS_BSC, BSC_POOL)
    wbnb_bsc = erc20_balance(w3_bsc, WBNB_BSC, BSC_POOL)

    print("BSC")
    print(f"  SPS  : {sps_bsc}")
    print(f"  WBNB : {wbnb_bsc}")

    # --- Base ---
    sps_base  = erc20_balance(w3_base, SPS_BASE, BASE_POOL)
    usdc_base = erc20_balance(w3_base, USDC_BASE, BASE_POOL)

    print("\nBase")
    print(f"  SPS  : {sps_base}")
    print(f"  USDC : {usdc_base}")

    # --- Ethereum (Uniswap v4 singleton) ---
    sps_eth = erc20_balance(
        w3_eth, SPS_ETH, UNISWAP_V4_SINGLETON
    )

    print("\nEthereum (Uniswap v4)")
    print(f"  SPS : {sps_eth}")


if __name__ == "__main__":
    main()
