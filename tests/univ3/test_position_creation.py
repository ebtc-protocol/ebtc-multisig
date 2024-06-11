from math import sqrt, log

from brownie import interface

from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import BASE, Q96

# misc.
FEE_TIER = 500
PRICE_1 = 1
PRICE_101 = 1.01


def test_position_creation(treasury, liq, wbtc):
    decimals_diff = liq.decimals() - wbtc.decimals()

    treasury.init_uni_v3()

    pool_address = treasury.uni_v3.factory.createPool(liq, wbtc, FEE_TIER).return_value
    pool = interface.IUniswapV3Pool(pool_address, owner=treasury.account)

    sqrt_of_p = sqrt(1e18 / 10 ** wbtc.decimals())
    sqrt_price_x_96 = sqrt_of_p * Q96

    pool.initialize(sqrt_price_x_96)

    token_0_init_seeding_amount = 2.5e8
    token_1_init_seeding_amount = 2.5e18

    token_id = treasury.uni_v3.mint_position(
        pool,
        PRICE_1,
        PRICE_101,
        token_0_init_seeding_amount,
        token_1_init_seeding_amount,
    )

    positions = treasury.uni_v3.nonfungible_position_manager.positions(token_id)

    price_lower_tick = round(
        ((BASE ** positions["tickLower"]) / (10**decimals_diff)), 4
    )
    price_higher_tick = round(
        ((BASE ** positions["tickUpper"]) / (10**decimals_diff)), 4
    )

    assert (
        treasury.uni_v3.nonfungible_position_manager.ownerOf(token_id)
        == treasury.account
    )
    assert positions["token0"] == wbtc.address
    assert positions["token1"] == liq.address
    assert positions["liquidity"] > 0
    assert price_lower_tick < price_higher_tick
