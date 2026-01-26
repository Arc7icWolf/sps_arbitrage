from web3 import Web3

TOKENS = {
    "bsc": {
        "SPS":  Web3.to_checksum_address("0x1633b7157e7638C4d6593436111Bf125Ee74703F"),
        "WBNB": Web3.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"),
    },
    "base": {
        "SPS":  Web3.to_checksum_address("0x578661E9A09Eee6b2cd97D4Ded1CCBaE7B8516B9"),
        "USDC": Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
    },
    "eth": {
        "SPS":  Web3.to_checksum_address("0x00813E3421E1367353BfE7615c7f7f133C89df74"),
    },
}
