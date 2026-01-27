from web3 import AsyncWeb3, AsyncHTTPProvider

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

def get_async_web3(chain: str) -> AsyncWeb3:
    return AsyncWeb3(AsyncHTTPProvider(CHAINS[chain]["rpc"]))
