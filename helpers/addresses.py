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
        "bsm": "0x828787A14fd4470Ef925Eefa8a56C88D85D4a06A",
        "bsm_escrow": "0x686FdecC0572e30768331D4e1a44E5077B2f6083",
        "bsm_oracle_price_constraint": "0xE66CD7ce741cF314Dc383d66315b61e1C9A3A15e",
        "bsm_rate_limiting_constraint": "0x6c289F91A8B7f622D8d5DcF252E8F5857CAc3E8B",
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
    "balancer": {
        "vault": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
        "gauge_factory": "0x4E7bBd911cf1EFa442BC1b2e9Ea01ffE785412EC",
        "veBAL": "0xC128a9954e6c874eA3d62ce62B468bA073093F25",
        "minter": "0x239e55F427D44C3cc793f49bFB507ebe76638a2b",
        "composable_stable_pool_factory": "0xDB8d758BCb971e482B2C45f7F8a7740283A1bd3A",
    },
    "uniswap": {
        "factoryV3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "NonfungiblePositionManager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "routerV3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
        "v3pool_wbtc_badger": "0xe15e6583425700993bd08F51bF6e7B73cd5da91B",
        "v3pool_wbtc_ebtc": "0xEf9b4FddD861aa2F00eE039C323b7FAbd7AFE239",
        "v3pool_wbtc_weth": "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD",
        "v3pool_ebtc_badger": "0x81d97d927cE883B46a5ecBE696B7189677FdC0Cd",
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
    # scout stores prices for all tokens here, either from coingecko or
    # interpolation. any token here that does not have a coingeco price must be
    # included in sett_vaults, lp_tokens or crvpools or one of the crv_ lists
    # in order to have its price calculated and not break scout.
    "treasury_tokens": {
        "FARM": "0xa0246c9032bC3A600820415aE600c6388619A14D",
        "BADGER": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
        "ibBTC": "0xc4E15973E6fF2A35cC804c2CF9D2a1b817a8b40F",
        "wibBTC": "0x8751D4196027d4e6DA63716fA7786B5174F04C15",
        "DIGG": "0x798D1bE841a82a273720CE31c822C61a67a601C3",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "aUSDC": "0xBcca60bB61934080951369a648Fb03DF4F96263C",
        "aUSDT": "0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811",
        "aFEI": "0x683923dB55Fead99A79Fa01A27EeC3cB19679cC3",
        "cUSDC": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
        "cDAI": "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643",
        "cETH": "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5",
        "DUSD": "0x5BC25f649fc4e26069dDF4cF4010F9f706c23831",
        "alUSD": "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "MIM": "0x99D8a9C45b2ecA8864373A26D1459e3Dff1e17F3",
        "FRAX": "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        "aFRAX": "0xd4937682df3C8aEF4FE912A96A74121C0829E664",
        "FEI": "0x956F47F50A910163D8BF957Cf5846D573E7f87CA",
        "DFD": "0x20c36f062a31865bED8a5B1e512D9a1A20AA333A",
        "CRV": "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "aWBTC": "0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656",
        "renBTC": "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        "sBTC": "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "SUSHI": "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2",
        "GTC": "0xDe30da39c46104798bB5aA3fe8B9e0e1F348163F",
        "bDIGG": "0x7e7E112A68d8D2E221E11047a72fFC1065c38e1a",
        "bBADGER": "0x19D97D8fA813EE2f51aD4B4e04EA08bAf4DFfC28",
        "xSUSHI": "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272",
        "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "stkAAVE": "0x4da27a545c0c5B758a6BA100e3a049001de870f5",
        "SPELL": "0x090185f2135308bad17527004364ebcc2d37e5f6",
        "ALCX": "0xdBdb4d16EdA451D0503b854CF79D55697F90c8DF",
        "FXS": "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0",
        "crvRenBTC": "0x49849C98ae39Fff122806C06791Fa73784FB3675",
        "crvSBTC": "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
        "crvTBTC": "0x64eda51d3Ad40D56b9dFc5554E06F94e1Dd786Fd",
        "slpWbtcEth": "0xceff51756c56ceffca006cd410b03ffc46dd3a58",
        "slpWbtcBadger": "0x110492b31c59716ac47337e616804e3e3adc0b4a",
        "uniWbtcBadger": "0xcd7989894bc033581532d2cd88da5db0a4b12859",
        "uniWbtcDigg": "0xe86204c4eddd2f70ee00ead6805f917671f56c52",
        "slpWbtcDigg": "0x9a13867048e01c663ce8ce2fe0cdae69ff9f35e3",
        "slpWbtcibBTC": "0x18d98D452072Ac2EB7b74ce3DB723374360539f1",
        "slpEthBBadger": "0x0a54d4b378c8dbfc7bc93be50c85debafdb87439",
        "slpEthBDigg": "0xf9440fedc72a0b8030861dcdac39a75b544e7a3c",
        "crvHBTC": "0xb19059ebb43466C323583928285a49f558E572Fd",
        "crvBBTC": "0x410e3E86ef427e30B9235497143881f717d93c2A",
        "crvOBTC": "0x2fE94ea3d5d4a175184081439753DE15AeF9d614",
        "crvPBTC": "0xDE5331AC4B3630f94853Ff322B66407e0D6331E8",
        "crvIbBTC": "0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B",
        "crvTricrypto": "0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF",
        "crvTricrypto2": "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
        "crv3pool": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
        "crvMIM": "0x5a6A4D54456819380173272A5E8E9B9904BdF41B",
        "crvALUSD": "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c",
        "crvFRAX": "0xd632f22692FaC7611d2AA1C0D552930D43CAEd3B",
        "CVX": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "cvxCRV": "0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7",
        "bcvxCRV": "0x2B5455aac8d64C14786c3a29858E43b5945819C0",
        "bCVX": "0x53c8e199eb2cb7c01543c137078a038937a68e40",
        "bveCVX_CVX_f": "0x04c90C198b2eFF55716079bc06d7CCc4aa4d7512",
        "bcrvRenBTC": "0x6dEf55d2e18486B9dDfaA075bc4e4EE0B28c1545",
        "bcrvSBTC": "0xd04c48A53c111300aD41190D63681ed3dAd998eC",
        "bcrvTBTC": "0xb9D076fDe463dbc9f915E5392F807315Bf940334",
        "bveCVX": "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305",
        "yvWBTC": "0xA696a63cc78DfFa1a63E9E50587C197387FF6C7E",  ##TODO NO COINGECKO PRICE
        "aBADGER": "0x43298F9f91a4545dF64748e78a2c777c580573d6",
        "badgerWBTC_f": "0x137469B55D1f15651BA46A89D0588e97dD0B6562",
        "EURS": "0xdB25f211AB05b1c97D595516F45794528a807ad8",
        "crv3eur": "0xb9446c4Ef5EBE66268dA6700D26f96273DE3d571",
        "FTM": "0x4E15361FD6b4BB609Fa63C81A2be19d873717870",
        "BAL": "0xba100000625a3754423978a60c9317c58a424e3D",
        "BOR": "0x3c9d6c1C73b31c837832c72E04D3152f051fc1A9",
        "BORING": "0xBC19712FEB3a26080eBf6f2F7849b417FdD792CA",
        "PNT": "0x89Ab32156e46F46D02ade3FEcbe5Fc4243B9AAeD",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
        "AURA": "0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF",
        "AURABAL": "0x616e8BfA43F920657B3497DBf40D6b1A02D4608d",
        "ANGLE": "0x31429d1856aD1377A8A0079410B297e1a9e214c2",
        "badgerFRAXBP_f_lp": "0x09b2E090531228d1b8E3d948C73b990Cb6e60720",
        "ENS": "0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72",
        "RETH": "0xae78736Cd615f374D3085123A210448E74Fc6393",
        "cvxFXS": "0xFEEf77d3f69374f66429C91d732A244f074bdf74",
        "mBTC": "0x945Facb997494CC2570096c74b5F66A3507330a1",
        "crvFRAXUSDC": "0x3175df0976dfa876431c2e9ee6bc45b65d3473cc",
        "GRT": "0xc944E90C64B2c07662A292be6244BDf05Cda44a7",
        "LIQ": "0xD82fd4D6D62f89A1E50b1db69AD19932314aa408",
        "LIQLIT": "0x03C6F0Ca0363652398abfb08d154F114e61c4Ad8",
        "LUSD": "0x5f98805A4E8be255a32880FDeC7F6728C6568bA0",
        "EBTC": "0x661c70333AA1850CcDBAe82776Bb436A0fCfeEfB",
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
