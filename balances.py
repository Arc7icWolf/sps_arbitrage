import asyncio
from chains import get_async_web3

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
# GLOBAL CACHE & RATE LIMIT
# ==============================

_DECIMALS_CACHE = {}

# Limite globale di chiamate RPC concorrenti
RPC_SEMAPHORE = asyncio.Semaphore(3)

# ==============================
# ERC20 BALANCE
# ==============================

async def erc20_balance_async(w3, token, holder):
    contract = w3.eth.contract(address=token, abi=ERC20_ABI)

    async with RPC_SEMAPHORE:
        if token in _DECIMALS_CACHE:
            decimals = _DECIMALS_CACHE[token]
        else:
            decimals = await contract.functions.decimals().call()
            _DECIMALS_CACHE[token] = decimals

        raw = await contract.functions.balanceOf(holder).call()

    return raw / (10 ** decimals)

# ==============================
# POOL READER
# ==============================

async def read_pool_async(pool_def, tokens_by_chain):
    chain   = pool_def["chain"]
    holder  = pool_def["holder"]
    symbols = pool_def["tokens"]

    w3 = get_async_web3(chain)

    tasks = []

    for symbol in symbols:
        token = tokens_by_chain[chain][symbol]
        tasks.append(
            erc20_balance_async(w3, token, holder)
        )

    results = await asyncio.gather(*tasks)
    return dict(zip(symbols, results))
