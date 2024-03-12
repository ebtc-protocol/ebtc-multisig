import pandas as pd

from brownie import chain
from dotmap import DotMap
from web3 import Web3
import json

ADDRESSES_ETH = {
    "ebtc": {
        "collateral": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
        "authority": "0x93d4f82903B87E94796Ec3665efa5f67F2072c6e",
        "liquidation_library": "0x55262e1128FafD9Bb0B0fD59A8998c13299c4AD4",
        "cdp_manager": "0x3c672ee8e13Cde7617923658138B111e157C8997",
        "borrower_operations": "0x99c4ea5d7aDF5d115c85AEEDD98Bd26DdBa714Cb",
        "ebtc_token": "0xead18fD27CAa1CFf909B5f2BD26ac9a46a6Ab1b5",
        "price_feed": "0x12A7897Cb1a2Ce8A2F1Bf221c1E6ef9bb11ECA8D",
        "ebtc_feed": "0x4039ca03Ce49021655c9B7C52Ab817d42DB7325e",
        "active_pool": "0x1e3Bf0965dca89Cd057d63c0cD65A37Acf920590",
        "coll_surplus_pool": "0x596EfaF17dFb3fd2CAE7543Ffa399F6e31658E4D",
        "sorted_cdps": "0x6cb99cF839c5AD3C24431c85da5Fdb7c7ab66d97",
        "hint_helpers": "0xE5A25E39A95750326322175249699eC5Cd66919F",
        "fee_recipient": "0x522ef088d94BD2125eC47F0967bf5B4E79Af4ed8",
        "multi_cdp_getter": "0x4e638aA073cAB30Ef2Ba63AA38ca5795Ada48E82",
        "ebtc_deployer": "0xA93A9CBBD47AA7B57853D460f442E2de2FB1dA4D",
        "highsec_timelock": "0xaDDeE229Bd103bb5B10C3CdB595A01c425dd3264",
        "lowsec_timelock": "0xE2F2D9e226e5236BeC4531FcBf1A22A7a2bD0602",
    },
    "ebtc_wallets": {
        "security_multisig": "0xB3d3B6482fb50C82aa042A710775c72dfa23F7B4",
        "techops_multisig": "0x690C74AF48BE029e763E61b4aDeB10E06119D3ba",
        "fee_recipient_multisig": "0x2CEB95D4A67Bf771f1165659Df3D11D8871E906f",
    },
    "badger_wallets": {
        "treasury_ops_multisig": "0x042B32Ac6b453485e357938bdC38e0340d4b9276",
        "treasury_vault_multisig": "0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e",
    },
    "assets": {
        "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "ebtc": "0xead18fD27CAa1CFf909B5f2BD26ac9a46a6Ab1b5",
        "liq": "0xD82fd4D6D62f89A1E50b1db69AD19932314aa408",
        "steth": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
    },
    "uniswap": {
        "factoryV3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "NonfungiblePositionManager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "routerV3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
        "v3pool_wbtc_badger": "0xe15e6583425700993bd08F51bF6e7B73cd5da91B",
        "v3pool_wbtc_ebtc": "0x0000000000000000000000000000000000000000",  # @note TBD!
        "v3pool_wbtc_weth": "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD",
    },
    "cow": {
        "vault_relayer": "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110",
        "settlement": "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    },
    "chainlink": {
        "collEthCLFeed": "0x86392dC19c0b719886221c78AB11eb8Cf5c52812",
        "btcUsdCLFeed": "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",
        "ethUsdCLFeed": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
        "chainlinkAdapter": "0x791a60EfEB402187852BdCDeC6Df3BEDd429fd81",
    },
    "merkl": {
        "distribution_creator": "0x8BB4C975Ff3c250e0ceEA271728547f3802B36Fd",
    },
}

ADDRESSES_SEPOLIA = {
    "ebtc": {
        "collateral": "0x97BA9AA7B7DC74f7a74864A62c4fF93b2b22f015",
        "authority": "0x85A074FF5adDf47fD66c94C780E7596922B3d1D9",
        "liquidation_library": "0x64B22874Bdc9F2e98C11b1bd6BA5527cf42Ef5c9",
        "cdp_manager": "0x39D6613ABEDd78a0b8edEEfE62cDEc85FCbe08c0",
        "borrower_operations": "0x3D6697c8Cfcc36b68a3077d0a94385B8904B1299",
        "ebtc_token": "0xeA2D83AA5e7da0668AdbddADAAc28e51318DDd86",
        "price_feed": "0xd2Bdc5Acb219ECeEE3578DA86774BBE4dd85665E",
        "ebtc_feed": "0x14BBa0A866f49D1ef33096557e661bE20BeBADA0",
        "active_pool": "0x8EbA6a17Fcd480A96a87308C560170206186D3EA",
        "coll_surplus_pool": "0x6a6Ee2146f851fA745016B9e5592379f775b4ff3",
        "sorted_cdps": "0x0ADF592E25ba775b89cA37e0Fc01420CA96563C8",
        "hint_helpers": "0x6AAB2e5f4bA902890197e5F60EB1aA420F2c079F",
        "fee_recipient": "0xed072C4DaA8c3068eAda19B17ec63172975Abe7e",
        "multi_cdp_getter": "0xBdd15a507945557ef039c847FB70d31f65522150",
        "ebtc_deployer": "0x21D4211d6125B40bA6049308204B091A8efE3452",
        "highsec_timelock": "0x0393846e97ab5Ec1DC8CB7A59Ee8505F72A6aEEb",
        "lowsec_timelock": "0xaADf07C98E2420E4d995Ba41Db53399648f50076",
        "test_contracts": {
            "test_price_feed": "0xD91c9CF0499ba9A6Eee7BED92c9F938C5fD4eD69",
            "mock_fallback_caller": "0x9283D34b5559218C3E36a1fc53c78356D8DFEa30",
        },
    },
    "ebtc_wallets": {
        "security_multisig": "0xC8A7768D2a9EE15437c981a7130268622083c2BD",
        "techops_multisig": "0x664F43229dDa9fdEE00e723753f88f3Ba81967F6",
        "fee_recipient_multisig": "0x5C1246E0b464060919301273781a266Ac119A0Bb",
    },
    "assets": {
        "ebtc": "0xeA2D83AA5e7da0668AdbddADAAc28e51318DDd86",
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
