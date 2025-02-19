import pandas as pd

from brownie import chain
from dotmap import DotMap
from web3 import Web3
import json

ADDRESSES_ETH = {
    "ebtc": {
        "collateral": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
        "authority": "0x2A095d44831C26cFB6aCb806A6531AE3CA32DBc1",
        "liquidation_library": "0x4Ae990C3b2F7C3961c51483eFba20760946a7681",
        "cdp_manager": "0xc4cbaE499bb4Ca41E78f52F07f5d98c375711774",
        "borrower_operations": "0xd366e016Ae0677CdCE93472e603b75051E022AD0",
        "ebtc_token": "0x661c70333AA1850CcDBAe82776Bb436A0fCfeEfB",
        "price_feed": "0x6a24ECc18224857BD73A7aa53c2a4Eb43c17D5A8",
        "ebtc_feed": "0xa9a65B1B1dDa8376527E89985b221B6bfCA1Dc9a",
        "active_pool": "0x6dBDB6D420c110290431E863A1A978AE53F69ebC",
        "coll_surplus_pool": "0x335982DaE827049d35f09D5ec927De2bc38df3De",
        "sorted_cdps": "0x591AcB5AE192c147948c12651a0a5f24f0529BE3",
        "hint_helpers": "0x2591554c5EE0b62B8E2725556Cc27744D8C2E7eB",
        "fee_recipient": "0xD4D1e77C69E7AA63D0E66a06df89A2AA5d3b1d9E",
        "multi_cdp_getter": "0x5Dd90e208E1086DFBC265c848067c6Da79dD1390",
        "ebtc_deployer": "0x5c42faC7eEa7e724986bB5e4F3B12912F046120a",
        "highsec_timelock": "0xaDDeE229Bd103bb5B10C3CdB595A01c425dd3264",
        "lowsec_timelock": "0xE2F2D9e226e5236BeC4531FcBf1A22A7a2bD0602",
        "treasury_timelock": "0xf1B767381819A69094a2A5a715A99776a2701b73",
        "staked_ebtc": "0x5884055ca6CacF53A39DA4ea76DD88956baFAee0",
    },
    "ebtc_wallets": {
        "security_multisig": "0xB3d3B6482fb50C82aa042A710775c72dfa23F7B4",
        "techops_multisig": "0x690C74AF48BE029e763E61b4aDeB10E06119D3ba",
        "fee_recipient_multisig": "0x2CEB95D4A67Bf771f1165659Df3D11D8871E906f",
        "techops_signers": {
            "techops_signer1": "0xaF94D299a73c4545ff702E79D16d9fb1AB5BDAbF",
            "techops_signer2": "0xfA5bb45895Cb3C0aE5B1583Fe068f009A48F0187",
            "techops_signer3": "0xDA82F543613f90deA718c46D02Ca15e05e88e4aC",
            "techops_signer4": "0xE78e3E1668D42FfCa767e22e57d7d249e02B5F0e",
            "techops_signer5": "0xE2C5B2008d9cc8F8E1FDa8552f7df63Af1f747f8",
            "techops_signer6": "0xcC692077C65dd464cAA7e7ae614328914f8469b3",
            "techops_signer7": "0x20359b5f320Ee24FA0B1000D80DAc4aFBF49738C",
        },
    },
    "badger_wallets": {
        "treasury_ops_multisig": "0x042B32Ac6b453485e357938bdC38e0340d4b9276",
        "treasury_vault_multisig": "0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e",
        "ibbtc_multisig_incentives": "0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8",
        "treasury_signers": {
            "treasury_signer1": "0xaFD01c6161729aa857404763c9577498327c6Aee",
            "treasury_signer2": "0x0a9af7FAba0d5DF7A8C881e1B9cd679ee07Af8A2",
            "treasury_signer3": "0xD10617AE4Da733d79eF0371aa44cd7fa74C41f6B",
            "treasury_signer4": "0x6C6238309f4f36DFF9942e655A678bbd4EA3BC5d",
            "treasury_signer5": "0x66496eBB9d848C6A8F19612a6Dd10E09954532D0",
            "treasury_signer6": "0x9c8C8bcD625Ed2903823b0b60DeaB2D70B92aFd9",
            "treasury_signer7": "0xaC7B5f4E631b7b5638B9b41d07f1eBED30753f16",
            "treasury_signer8": "0x2afc096981c2CFe3501bE4054160048718F6C0C8",
            "treasury_signer9": "0xaF94D299a73c4545ff702E79D16d9fb1AB5BDAbF",
        },
    },
    "assets": {
        "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "ebtc": "0x661c70333AA1850CcDBAe82776Bb436A0fCfeEfB",
        "liq": "0xD82fd4D6D62f89A1E50b1db69AD19932314aa408",
        "steth": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
        "wsteth": "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
        "reth": "0xae78736Cd615f374D3085123A210448E74Fc6393",
        "badger": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
    },
    "uniswap": {
        "factoryV3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "NonfungiblePositionManager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "routerV3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
        "v3pool_wbtc_badger": "0xe15e6583425700993bd08F51bF6e7B73cd5da91B",
        "v3pool_wbtc_ebtc": "0xEf9b4FddD861aa2F00eE039C323b7FAbd7AFE239",
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
        "authority": "0x68Aa57A7b02c02f53A99e8Fd451CaE761210C5d2",
        "liquidation_library": "0xD036320bf778651684415AB372c7ab58acB5f3d8",
        "cdp_manager": "0xe89A0378237c21B94126f77eD5Fa0FDd2eDE2b36",
        "borrower_operations": "0x58aa3dE50CfeF7450657C52766dD43da8747285e",
        "ebtc_token": "0xa78F78Aba222d20cE82eA4868a9E00c954e469c0",
        "price_feed": "0x240E4141E13c6613bBBC53049dFEc0dAC70D692e",
        "ebtc_feed": "0xF08F9Ae30e19f2CA9b0876a7Dc57E6695010dE40",
        "active_pool": "0x7e0A97660B477a79C2e9f472bbFCFd8A715D9E6f",
        "coll_surplus_pool": "0xd5E6e5c5F46fa1A038b62B0625e21B97a4897F8F",
        "sorted_cdps": "0xbc79539670992A4E1948dAdB737472a2FaD7CEcf",
        "hint_helpers": "0xD4612689dC45a84dE503dc375eAE348d034e7df1",
        "fee_recipient": "0x76Fb3d53Dc44eE733d8fD7b1581b35B7C76349F8",
        "multi_cdp_getter": "0x1a951f87347bD16a7aD2B44add9B4522E6452af6",
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
        "ebtc": "0xa78F78Aba222d20cE82eA4868a9E00c954e469c0",
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
