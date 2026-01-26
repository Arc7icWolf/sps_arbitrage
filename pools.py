from web3 import Web3

POOLS = {
    "bsc_sps_wbnb": {
        "chain": "bsc",
        "holder": Web3.to_checksum_address(
            "0x96e55d2d53b79D636166B23103552253E23B699E"
        ),
        "tokens": ["SPS", "WBNB"],
    },

    "base_sps_usdc": {
        "chain": "base",
        "holder": Web3.to_checksum_address(
            "0x726962F81eE8eFdC83266858B5bCf2146713A8Cf"
        ),
        "tokens": ["SPS", "USDC"],
    },

    "uniswap_v4_eth": {
        "chain": "eth",
        "holder": Web3.to_checksum_address(
            "0x000000000004444c5dc75cB358380D2e3dE08A90"
        ),
        "tokens": ["SPS"],
    },
}
