import pandas as pd

from brownie import chain
from dotmap import DotMap
from web3 import Web3
import json

ADDRESSES_ETH = {
    "ebtc": {"placeholder": "0x0000000000000000000000000000000000000000"},
    "ebtc_wallets": {"placeholder": "0x0000000000000000000000000000000000000000"},
}

ADDRESSES_SEPOLIA = {
    "ebtc": {
        "collateral": "0x97BA9AA7B7DC74f7a74864A62c4fF93b2b22f015",
        "authority": "0xDcf7533497bC4baAf5beB385C82027A39B11a2f6",
        "liquidation_library": "0xFbeCFbA9B33f95C0Dc8E915D7b4ECA06E09bb67c",
        "cdp_manager": "0x4BaA1Fdf4EeA0C52a4D37ce6F64EBb51b342b348",
        "borrower_operations": "0x606bC21c399cBBA0c0d427047cDB2b50B1E05087",
        "ebtc_token": "0x2459A79d406256030d339379592ae2fF639bA324",
        "price_feed": "0x825e07ad92B2933481E63DC8eAd087EF0dB5d7Ca",
        "active_pool": "0x55F246A87E988E582b621355E952f6ac3aF5CDd2",
        "coll_surplus_pool": "0x7bc76C622A5c35c4610864a83cd7da5CB668C986",
        "sorted_cdps": "0xdA3Bb1b380C7Cfd9279dC3334F6122587C8e52A9",
        "hint_helpers": "0x52A6C2C30Eb6E3c9E8a0BF1479d8d81ad4c6fCE4",
        "fee_recipient": "0xeAB976bBE69fE936beD9D079B4f61A19be4Cb69A",
        "multi_cdp_getter": "0xE9F8c2ff6014184959b970ac7CbE7073B78C291c",
        "ebtc_deployer": "0xC39A1159eDd78458E7b4943fcCa45c769b0E223e",
        "highsec_timelock": "0x0b6cA096Cc6C21a06d5476b3d147F0398A5251C0",
        "lowsec_timelock": "0x29001E42899308A61d981c5f5780e4E4D727a0BB",
    },
    "ebtc_wallets": {
        "ecosystem_multisig": "0xC8A7768D2a9EE15437c981a7130268622083c2BD",
        "council_multisig": "0x005E0Ad70b40B23cef409978350CA77a179de350",
        "techops_multisig": "0x664F43229dDa9fdEE00e723753f88f3Ba81967F6",
        "fee_recipient_multisig": "0x5C1246E0b464060919301273781a266Ac119A0Bb",
    },
    "tokens": {
        "ebtc": "0x2459A79d406256030d339379592ae2fF639bA324",
        "steth": "0x97BA9AA7B7DC74f7a74864A62c4fF93b2b22f015",
        "wbtc": "0x84beA728aFb989756B4AF86600C0a95919035849",
    },
}

ADDRESSES_GOERLI = {
    "ebtc": {
        "collateral": "0x879fB0Ea23d3e08c67437D88e6B38AA67A91646e",
        "authority": "0x0A64EFEA554769De201d362A755CDAC7C949a6E5",
        "liquidation_library": "0xd98c30Dab8F018456ba966E67fB6311efB334C2D",
        "cdp_manager": "0x97387ddA50765356f6f1F5957c4afB79CED4ebd6",
        "borrower_operations": "0x9FeAd18276448c27E8174a4e542a57dB294Ea1e7",
        "ebtc_token": "0x6Db7BF0DE56d10b1B8F9cb966a9F9F08cbd07231",
        "price_feed": "0x4B8A691A135A7Dd7f90538569b5032B1DAa7369c",
        "active_pool": "0x463902ccCbcbfB1c5F9B35E4D0032Ef8fEaa8392",
        "coll_surplus_pool": "0xbb8D843f223E11a93d00594Dd473a213BaB198c7",
        "sorted_cdps": "0xfcE06D412bBb010466e95b24E69Cd1017a10269f",
        "hint_helpers": "0x83fee3737E0F15a78F9f08eDc86493B8ed3b7E2C",
        "fee_recipient": "0x103c5096F4268d9BB5A69DA173C7b26BbA1AD95f",
        "multi_cdp_getter": "0xD7E6F2bB0b6fE392cD01e311cc1EeDa9d209Ae9f",
        "ebtc_deployer": "0xC39A1159eDd78458E7b4943fcCa45c769b0E223e",
        "highsec_timelock": "0xcFF5f6c02d6627483850116A96c9c8f78FDb0aAe",
        "lowsec_timelock": "0x0fcc64DA819F9Ae13B48329fbCF7f42F96200D43",
    },
    "ebtc_wallets": {
        "ecosystem_multisig": "0x0A8fE898020f5E02C8D7ac29CCb907198f77ed92",
        "council_multisig": "0xed448dA7b82Df32bEeDdc91DaE169cBC278Bc108",
        "techops_multisig": "0xb1939449B5612F632F2651cBe56b8FDc7f04dE26",
        "fee_recipient_multisig": "0x821Ef96C19db290d2E4856460C730E59F4688539",
    },
}


def checksum_address_dict(addresses):
    """
    convert addresses to their checksum variant taken from a (nested) dict
    """
    checksummed = {}
    for k, v in addresses.items():
        if isinstance(v, str):
            checksummed[k] = Web3.toChecksumAddress(v)
        elif isinstance(v, dict):
            checksummed[k] = checksum_address_dict(v)
        else:
            print(k, v, "formatted incorrectly")
    return checksummed


with open("helpers/chaindata.json") as chaindata:
    chain_ids = json.load(chaindata)


registry = DotMap(
    {
        "eth": checksum_address_dict(ADDRESSES_ETH),
        "goerli": checksum_address_dict(ADDRESSES_GOERLI),
        "sepolia": checksum_address_dict(ADDRESSES_SEPOLIA),
    }
)


def get_registry():
    try:
        if chain.id == 1:
            return registry.eth
        elif chain.id == 5:
            return registry.goerli
        elif chain.id == 11155111:
            return registry.sepolia
    except:
        return registry.eth


r = get_registry()

# flatten nested dicts and invert the resulting key <-> value
# this allows for reversed lookup of an address
df = pd.json_normalize(registry, sep="_")
reverse = df.T.reset_index().set_index(0)["index"].to_dict()
