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

_ASYNC_W3 = {}

def get_async_web3(chain: str) -> AsyncWeb3:
    if chain not in _ASYNC_W3:
        provider = AsyncHTTPProvider(CHAINS[chain]["rpc"])
        _ASYNC_W3[chain] = AsyncWeb3(provider)

    return _ASYNC_W3[chain]
