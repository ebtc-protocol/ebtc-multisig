from math import sqrt

from great_ape_safe import GreatApeSafe
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import Q96

from brownie import accounts, interface
from helpers.addresses import r
from rich.console import Console

C = Console()

"""
Funds allocation (univ3):
* 0.925-0.99 eBTC/WBTC: 10% of funds allocated to liquidity provision
* 0.99-1 eBTC/WBTC: 40% of funds allocated to liquidity provision
* 1-1.01 eBTC/WBTC: 40% of funds allocated to liquidity provision
* 1.01-1.08 eBTC/WBTC: 10% of funds allocated to liquidity provision
"""

# misc.univ3
FEE_TIER = 500
PCT_10 = 0.1
PCT_40 = 0.4

PRICE_0925 = 0.925
PRICE_099 = 0.99
PRICE_1 = 1
PRICE_101 = 1.01
PRICE_108 = 1.08

# misc.cow
COEF = 0.98
DEADLINE = 60 * 60 * 3

# misc.ebtc
COLLATERAL_TARGET_RATIO = 200

safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
safe.init_uni_v3()


def prep_():
    safe.init_cow(prod=True)

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)
    reth = safe.contract(r.assets.reth)
    steth = safe.contract(r.assets.steth)

    # =========== $reth -> $steth swap (happens async) ===========
    safe.cow.market_sell(
        reth, steth, reth.balanceOf(safe), deadline=DEADLINE, coef=COEF
    )

    # =========== pool creation & initialization ===========

    _pool_creation(ebtc, wbtc)

    safe.post_safe_tx()


def seed_pool_w1(sim=False):
    safe.init_ebtc()

    # week 1 targets
    collateral_amount_week_1 = 100

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)
    steth = safe.contract(r.assets.steth)

    # sim
    if sim:
        # 1. pool creation
        pool_address = _pool_creation(ebtc, wbtc)
        # 2. fake enough $steth balance
        _provide_collateral(steth, collateral_amount_week_1)
    else:
        pool_address = r.uniswap.v3pool_wbtc_ebtc

    pool = interface.IUniswapV3Pool(pool_address, owner=safe.account)

    # 1. open cdp
    safe.ebtc.open_cdp(collateral_amount_week_1 * 1e18, COLLATERAL_TARGET_RATIO * 1e16)

    # 2. pool seeding, mint nft's. Deposit equal 1:1 (ebtc:wbtc)
    ebtc_bal = ebtc.balanceOf(safe.account)
    wbtc_bal = int(ebtc_bal / 10 ** (ebtc.decimals() - wbtc.decimals()))
    C.print(f"[green]$ebtc balance to seed the pool: {ebtc_bal}[/green]")
    C.print(f"[green]$wbtc balance to seed the pool: {wbtc_bal}[/green]")

    nft_from_0925_to_099 = safe.uni_v3.mint_position(
        pool, PRICE_0925, PRICE_099, wbtc_bal * PCT_10 * 2, 0
    )
    C.print(f"[green]nft_from_0925_to_099 token id: {nft_from_0925_to_099}[/green]")

    nft_from_099_to_1 = safe.uni_v3.mint_position(
        pool,
        PRICE_099,
        PRICE_1,
        wbtc_bal * PCT_40,  # token0: $wbtc
        ebtc_bal * PCT_40,  # token1: $ebtc
    )
    C.print(f"[green]nft_from_099_to_1 token id: {nft_from_099_to_1}[/green]")

    nft_from_1_to_101 = safe.uni_v3.mint_position(
        pool,
        PRICE_1,
        PRICE_101,
        wbtc_bal * PCT_40,  # token0: $wbtc
        ebtc_bal * PCT_40,  # token1: $ebtc
    )
    C.print(f"[green]nft_from_1_to_101 token id: {nft_from_1_to_101}[/green]")

    nft_from_101_to_108 = safe.uni_v3.mint_position(
        pool, PRICE_101, PRICE_108, 0, ebtc_bal * PCT_10 * 2
    )
    C.print(f"[green]nft_from_101_to_108 token id: {nft_from_101_to_108}[/green]")

    if not sim:
        safe.post_safe_tx()
    else:
        return (
            nft_from_0925_to_099,
            nft_from_099_to_1,
            nft_from_1_to_101,
            nft_from_101_to_108,
        )


# @note same method can be called for W2 & W3
def seed_pool_w2(sim=False, nfts_list_sim=[]):
    safe.init_ebtc()

    # week 2 targets
    collateral_amount_week_2 = 200

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)
    steth = safe.contract(r.assets.steth)

    # sim
    if sim:
        # 1. fake enough $steth balance
        _provide_collateral(steth, collateral_amount_week_2)
        nft_from_0925_to_099 = nfts_list_sim[0]
        nft_from_099_to_1 = nfts_list_sim[1]
        nft_from_1_to_101 = nfts_list_sim[2]
        nft_from_101_to_108 = nfts_list_sim[3]
    else:
        # @note here the real nft ids should be retrieve ideal from json files once week 1 is executed!
        nft_from_0925_to_099 = 0
        nft_from_099_to_1 = 0
        nft_from_1_to_101 = 0
        nft_from_101_to_108 = 0

    # 1. open cdp
    safe.ebtc.open_cdp(collateral_amount_week_2 * 1e18, COLLATERAL_TARGET_RATIO * 1e16)

    # 2. increase liquidity in existing nft's
    ebtc_bal = ebtc.balanceOf(safe.account)
    wbtc_bal = int(ebtc_bal / 10 ** (ebtc.decimals() - wbtc.decimals()))
    C.print(f"[green]$ebtc balance to seed the pool: {ebtc_bal}[/green]")
    C.print(f"[green]$wbtc balance to seed the pool: {wbtc_bal}[/green]")

    safe.uni_v3.increase_liquidity(
        nft_from_0925_to_099, wbtc, ebtc, wbtc_bal * PCT_10 * 2, 0
    )
    safe.uni_v3.increase_liquidity(
        nft_from_099_to_1, wbtc, ebtc, wbtc_bal * PCT_40, ebtc_bal * PCT_40
    )
    safe.uni_v3.increase_liquidity(
        nft_from_1_to_101, wbtc, ebtc, wbtc_bal * PCT_40, ebtc_bal * PCT_40
    )
    safe.uni_v3.increase_liquidity(
        nft_from_101_to_108, wbtc, ebtc, 0, ebtc_bal * PCT_10 * 2
    )

    if not sim:
        safe.post_safe_tx()


def _pool_creation(ebtc, wbtc):
    # 1. pool creation: tick spacing should be end-up being `10`
    # ref: https://github.com/Uniswap/v3-core/blob/main/contracts/UniswapV3Factory.sol#L26
    pool_address = safe.uni_v3.factory.createPool(ebtc, wbtc, FEE_TIER).return_value
    C.print(f"[green]Pool address is: {pool_address}[/green]")

    # 2. pool initialize
    pool = interface.IUniswapV3Pool(pool_address, owner=safe.account)
    # @note order of which is token0 & token1 depends on
    # ref: https://github.com/Uniswap/v3-core/blob/main/contracts/UniswapV3Factory.sol#L41
    token0 = pool.token0()
    token1 = pool.token1()
    C.print(f"[green]Token0 is: {token0}[/green]")
    C.print(f"[green]Token1 is: {token1}\n[/green]")

    # sqrt(p) * Q96. where "p" is price of wbtc in terms of ebtc. assume "init" at parity
    sqrt_of_p = sqrt(1e18 / 10 ** wbtc.decimals())
    sqrt_price_x_96 = sqrt_of_p * Q96

    # expect tick ~230270 & sqrtPriceX96 ~7922816251426434000000000000000000
    pool.initialize(sqrt_price_x_96)
    sqrtPriceX96, tick, _, _, _, _, _ = pool.slot0()
    C.print(f"[green]sqrtPriceX96={sqrtPriceX96}[/green]")
    C.print(f"[green]tick={tick}\n[/green]")

    return pool_address


# ================ SIMULATIONS ================


def _provide_collateral(steth, collateral_amount):
    steth_whale = accounts.at(r.assets.wsteth, force=True)
    steth.transfer(safe, collateral_amount * 1e18, {"from": steth_whale})


def sim_seed_pool_w1_and_w2():
    # sim week 1
    (
        nft_from_0925_to_099,
        nft_from_099_to_1,
        nft_from_1_to_101,
        nft_from_101_to_108,
    ) = seed_pool_w1(sim=True)
    # sim week 2
    seed_pool_w2(
        sim=True,
        nfts_list_sim=[
            nft_from_0925_to_099,
            nft_from_099_to_1,
            nft_from_1_to_101,
            nft_from_101_to_108,
        ],
    )
