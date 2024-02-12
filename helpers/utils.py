from brownie import web3


def encode_signature(signature: str) -> str:
    return web3.keccak(text=signature).hex()[0:10]
