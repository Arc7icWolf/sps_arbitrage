from web3 import Web3

CHAINS = {
    "bsc": {
        "rpc": "https://bsc-dataseed.binance.org/",
    },
    "base": {
        "rpc": "https://mainnet.base.org",
    },
    "eth": {
        "rpc": "https://eth.llamarpc.com",
    },
}

def get_web3(chain: str) -> Web3:
    return Web3(Web3.HTTPProvider(CHAINS[chain]["rpc"]))
