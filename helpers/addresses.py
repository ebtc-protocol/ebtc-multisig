import pandas as pd

from brownie import chain
from dotmap import DotMap
from web3 import Web3
import json

ADDRESSES_ETH = {
    "assets": {
        "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "ebtc": "0x0000000000000000000000000000000000000000",
        "liq": "0xD82fd4D6D62f89A1E50b1db69AD19932314aa408",
    },
    "badger_wallets": {
        "treasury_ops_multisig": "0x042B32Ac6b453485e357938bdC38e0340d4b9276",
        "treasury_vault_multisig": "0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e",
    },
    "ebtc_wallets": {"placeholder": "0x0000000000000000000000000000000000000000"},
    "uniswap": {
        "factoryV3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "NonfungiblePositionManager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "routerV3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
        "v3pool_wbtc_badger": "0xe15e6583425700993bd08F51bF6e7B73cd5da91B",
    },
    "cow": {
        "vault_relayer": "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110",
        "settlement": "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    },
}

ADDRESSES_SEPOLIA = {
    "ebtc": {
        "collateral": "0x97BA9AA7B7DC74f7a74864A62c4fF93b2b22f015",
        "authority": "0xb80142C74353066519a47119CE589ef0059EC169",
        "liquidation_library": "0x8C4f04c7164fB3847D4dFdD0470707a74DB72215",
        "cdp_manager": "0x4819558026d1bAe3ab4B6DE203a0483E8F23E047",
        "borrower_operations": "0x3CABDD1dF8aDdd87DA26a24ccD292f64b6065f2B",
        "ebtc_token": "0x0b3e07D082F07d6a8Dba3a6f6aCf32ae1ed16Ea4",
        "price_feed": "0xD91c9CF0499ba9A6Eee7BED92c9F938C5fD4eD69",
        "ebtc_feed": "0x5DbF3c1417BE8E0DF3e167E7054823B018EE5fdD",
        "active_pool": "0x2A83d2b80D908A03032ddb274ED854c17815f60A",
        "coll_surplus_pool": "0xb7a0f6e823ba9f4b80003aF37af71bAE04868eBb",
        "sorted_cdps": "0x9637Aa7b8fEAa6Ae3481f7cC08EAe523ac032D61",
        "hint_helpers": "0xfc6dc2C90bF01c7B7bfe7F4D14C77F155613C54b",
        "fee_recipient": "0x37A7E626dac6d6253a6423674CaA41204661cAcd",
        "multi_cdp_getter": "0x3Bf95b56488Dfb33B23c6CcB80F1589d87530A37",
        "ebtc_deployer": "0xC0BB8cB46778777308C51b863e6200A48BCDaEC5",
        "highsec_timelock": "0x0F7eBa761D85351aa94F47AF66B16409b673144d",
        "lowsec_timelock": "0x981EF454d1433C664C09F1b8d73B0381D13ac7BD",
        "test_contracts": {
            "test_price_feed": "0xD91c9CF0499ba9A6Eee7BED92c9F938C5fD4eD69"
        },
    },
    "ebtc_wallets": {
        "security_multisig": "0xC8A7768D2a9EE15437c981a7130268622083c2BD",
        "techops_multisig": "0x664F43229dDa9fdEE00e723753f88f3Ba81967F6",
        "fee_recipient_multisig": "0x5C1246E0b464060919301273781a266Ac119A0Bb",
    },
    "tokens": {
        "ebtc": "0x0b3e07D082F07d6a8Dba3a6f6aCf32ae1ed16Ea4",
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
        "security_multisig": "0x0A8fE898020f5E02C8D7ac29CCb907198f77ed92",
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
