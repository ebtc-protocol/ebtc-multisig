from brownie import web3


# Takes a string with a function signature and returns a 4 bytes hex string
def encode_signature(signature: str) -> str:
    return web3.keccak(text=signature).hex()[0:10]


# Assert approximate integer
def approx(actual, expected, percentage_threshold):
    print(actual, expected, percentage_threshold)
    diff = int(abs(actual - expected))
    # 0 diff should automtically be a match
    if diff == 0:
        return True
    return diff < (actual * percentage_threshold // 100)


# Takes a string with boolean value and returns an equivalent boolean
def str_to_bool(s):
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    else:
        raise ValueError("Cannot convert to boolean")


# Takes a decimal number and returns a 32 bytes hex string
def dec_to_hex(dec: int) -> str:
    return "0x" + hex(dec)[2:].zfill(64)
