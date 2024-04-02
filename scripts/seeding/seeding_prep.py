import json
import os
from math import sqrt
from pathlib import Path

from great_ape_safe import GreatApeSafe
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import Q96

from great_ape_safe.ape_api.helpers.coingecko import get_cg_price

from brownie import accounts, interface
from helpers.addresses import r
from rich.console import Console

C = Console()

# misc.univ3
FEE_TIER = 500
PCT_10 = 0.1
PCT_40 = 0.4

LIQUIDITY_MULTIPLIER = 2

PRICE_0925 = 0.925
PRICE_099 = 0.99
PRICE_1 = 1
PRICE_101 = 1.01
PRICE_108 = 1.08

# misc.cow
COEF = 0.98
DEADLINE = 60 * 60 * 3

# misc.coll amount
STETH_TARGET_AMOUNT = 800

# misc.ebtc
COLLATERAL_TARGET_RATIO = 200
CR_FACTOR = 1e16

safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
safe.init_uni_v3()


def prep():
    safe.init_cow(prod=True)

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)
    reth = safe.contract(r.assets.reth)
    steth = safe.contract(r.assets.steth)

    # prices of $eth versions
    reth_price = get_cg_price(reth.address)
    steth_price = get_cg_price(steth.address)

    # @note adding a minor multiplier to ensure the swap hits the $steth target amount
    reth_amount = (STETH_TARGET_AMOUNT * steth_price / reth_price) * 1.03

    # =========== $reth -> $steth swap (happens async) ===========
    reth_amount_mantissa = reth_amount * 10 ** reth.decimals()
    safe.cow.market_sell(
        reth, steth, reth_amount_mantissa, deadline=DEADLINE, coef=COEF
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
    safe.ebtc.open_cdp(
        collateral_amount_week_1 * 1e18, COLLATERAL_TARGET_RATIO * CR_FACTOR
    )

    # 2. pool seeding, mint nft's. Deposit equal 1:1 (ebtc:wbtc)
    ebtc_bal = ebtc.balanceOf(safe.account)
    wbtc_bal = int(ebtc_bal / 10 ** (ebtc.decimals() - wbtc.decimals()))
    C.print(f"[green]$ebtc balance to seed the pool: {ebtc_bal}[/green]")
    C.print(f"[green]$wbtc balance to seed the pool: {wbtc_bal}[/green]")

    nft_from_0925_to_099 = safe.uni_v3.mint_position(
        pool, PRICE_0925, PRICE_099, wbtc_bal * PCT_10 * LIQUIDITY_MULTIPLIER, 0
    )
    C.print(f"[green]nft_from_0925_to_099 token id: {nft_from_0925_to_099}[/green]")

    nft_from_099_to_1 = safe.uni_v3.mint_position(
        pool,
        PRICE_099,
        PRICE_1,
        wbtc_bal * PCT_40 * LIQUIDITY_MULTIPLIER,  # token0: $wbtc
        ebtc_bal * PCT_40 * LIQUIDITY_MULTIPLIER,  # token1: $ebtc
    )
    C.print(f"[green]nft_from_099_to_1 token id: {nft_from_099_to_1}[/green]")

    nft_from_1_to_101 = safe.uni_v3.mint_position(
        pool,
        PRICE_1,
        PRICE_101,
        wbtc_bal * PCT_40 * LIQUIDITY_MULTIPLIER,  # token0: $wbtc
        ebtc_bal * PCT_40 * LIQUIDITY_MULTIPLIER,  # token1: $ebtc
    )
    C.print(f"[green]nft_from_1_to_101 token id: {nft_from_1_to_101}[/green]")

    remaining_ebtc_balance = ebtc.balanceOf(safe.account)
    nft_from_101_to_108 = safe.uni_v3.mint_position(
        pool, PRICE_101, PRICE_108, 0, remaining_ebtc_balance
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


# @note same method can be called for W3 & W4
def seed_pool_w3(sim=False, nfts_list_sim=[]):
    safe.init_ebtc()

    # week 3 targets
    collateral_amount_week_3 = 200

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)
    steth = safe.contract(r.assets.steth)

    # pool
    pool = interface.IUniswapV3Pool(r.uniswap.v3pool_wbtc_ebtc, owner=safe.account)
    current_tick = pool.slot0()[1]
    C.print(f"[green]Current tick in the pool: {current_tick} \n[/green]")

    # sim
    if sim:
        # 1. fake enough $steth balance
        _provide_collateral(steth, collateral_amount_week_3)
        nft_from_0925_to_099 = nfts_list_sim[0]
        nft_from_099_to_1 = nfts_list_sim[1]
        nft_from_1_to_101 = nfts_list_sim[2]
        nft_from_101_to_108 = nfts_list_sim[3]
    else:
        # @note the token ids are retrieved from json files in `scripts/TCL/positionData` directory
        nft_from_0925_to_099 = _retrive_token_id("0925_to_099", current_tick)
        nft_from_099_to_1 = _retrive_token_id("099_to_1", current_tick)
        nft_from_1_to_101 = _retrive_token_id("1_to_101", current_tick)
        nft_from_101_to_108 = _retrive_token_id("101_to_108", current_tick)

    feed_price = safe.ebtc.ebtc_feed.fetchPrice.call()
    prev_tcr = safe.ebtc.cdp_manager.getSyncedTCR(feed_price)

    # 1. top-up cdp
    collateral_mantissa = collateral_amount_week_3 * 1e18
    cdp_id = safe.ebtc.sorted_cdps.getCdpsOf(safe)[
        0
    ]  # @note assuming there is only one cdp belong to treasury!
    safe.ebtc.cdp_add_collateral(cdp_id, collateral_mantissa)

    borrow_amount = (
        collateral_mantissa * feed_price / (COLLATERAL_TARGET_RATIO * CR_FACTOR)
    )
    safe.ebtc.safe.ebtc.cdp_withdraw_debt(cdp_id, borrow_amount)

    post_actions_tcr = safe.ebtc.cdp_manager.getSyncedTCR(feed_price)
    C.print(
        f"[blue]System TCR before treasury actions {(prev_tcr / CR_FACTOR):.3f}% and after actions {(post_actions_tcr / CR_FACTOR):.3f}% [/blue]"
    )

    # 2. increase liquidity in existing nft's
    ebtc_bal = ebtc.balanceOf(safe.account)
    ebtc_decimals = ebtc.decimals()
    wbtc_decimals = wbtc.decimals()
    wbtc_bal = int(ebtc_bal / 10 ** (ebtc_decimals - wbtc_decimals))
    C.print(
        f"[green]$ebtc balance to seed the pool: {ebtc_bal / 10 ** ebtc_decimals}[/green]"
    )
    C.print(
        f"[green]$wbtc balance to seed the pool: {wbtc_bal / 10 ** wbtc_decimals}[/green]"
    )

    safe.uni_v3.increase_liquidity(
        nft_from_0925_to_099, wbtc, ebtc, wbtc_bal * PCT_10 * LIQUIDITY_MULTIPLIER, 0
    )
    safe.uni_v3.increase_liquidity(
        nft_from_099_to_1,
        wbtc,
        ebtc,
        wbtc_bal * PCT_40,
        ebtc_bal * PCT_40,
    )
    safe.uni_v3.increase_liquidity(
        nft_from_1_to_101,
        wbtc,
        ebtc,
        wbtc_bal
        * PCT_40,  # @note this is currently out of range, it will not top up $wbtc portion!
        ebtc_bal * PCT_40,
    )
    remaining_ebtc_balance = ebtc.balanceOf(safe.account)
    safe.uni_v3.increase_liquidity(
        nft_from_101_to_108, wbtc, ebtc, 0, remaining_ebtc_balance
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


def _retrive_token_id(file_matching_pattern_str, current_tick):
    path = os.path.dirname("scripts/TCL/positionData/")
    directory = os.fsencode(path)

    token_id = 0

    for file in os.listdir(directory):
        file_name = os.fsdecode(file)

        if str(file_matching_pattern_str) in file_name:
            data = open(f"scripts/TCL/positionData/{file_name}")
            json_file = json.load(data)
            token_id = json_file["tokenId"]
            if json_file["lowerTick"] <= current_tick <= json_file["upperTick"]:
                C.print(f"[red]Range {file_matching_pattern_str} is in range![/red]")
            break

    assert token_id > 0
    C.print(
        f"[green]token id for range {file_matching_pattern_str} is: {token_id} \n[/green]"
    )
    return token_id


# ================ SIMULATIONS ================


def _provide_collateral(steth, collateral_amount):
    steth_whale = accounts.at(r.assets.wsteth, force=True)
    steth.transfer(safe, collateral_amount * 1e18, {"from": steth_whale})


def sim_seed_pool_w1_and_w3():
    # sim week 1
    (
        nft_from_0925_to_099,
        nft_from_099_to_1,
        nft_from_1_to_101,
        nft_from_101_to_108,
    ) = seed_pool_w1(sim=True)
    # sim week 3
    seed_pool_w3(
        sim=True,
        nfts_list_sim=[
            nft_from_0925_to_099,
            nft_from_099_to_1,
            nft_from_1_to_101,
            nft_from_101_to_108,
        ],
    )
