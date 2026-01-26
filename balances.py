from web3 import Web3
from chains import get_web3

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

def erc20_balance(w3: Web3, token: str, holder: str) -> float:
    contract = w3.eth.contract(address=token, abi=ERC20_ABI)
    decimals = contract.functions.decimals().call()
    raw = contract.functions.balanceOf(holder).call()
    return raw / (10 ** decimals)

def read_pool(pool_def, tokens_by_chain):
    chain = pool_def["chain"]
    holder = pool_def["holder"]
    symbols = pool_def["tokens"]

    w3 = get_web3(chain)

    balances = {}

    for symbol in symbols:
        token = tokens_by_chain[chain][symbol]
        balances[symbol] = erc20_balance(w3, token, holder)

    return balances
