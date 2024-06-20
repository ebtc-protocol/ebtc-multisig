from math import sqrt, log

from brownie import interface

from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import BASE, Q96

# misc.
FEE_TIER = 500
PARITY_PAIR_VALUE = 1


def test_pool_creation(treasury, liq, wbtc):
    treasury.init_uni_v3()

    pool_address = treasury.uni_v3.factory.createPool(liq, wbtc, FEE_TIER).return_value
    pool = interface.IUniswapV3Pool(pool_address, owner=treasury.account)

    initial_sqrt_price_x96, initial_tick, _, _, _, _, _ = pool.slot0()

    # assert the following conditions against the pool creation
    assert pool.token0() == wbtc.address
    assert pool.token1() == liq.address
    assert pool.fee() == FEE_TIER
    assert initial_sqrt_price_x96 == 0
    assert initial_tick == 0

    # init pool at parity, similar w/ the intention of ebtc/wbtc
    sqrt_of_p = sqrt(1e18 / 10 ** wbtc.decimals())
    sqrt_price_x_96 = sqrt_of_p * Q96

    expected_tick = round((2 * log(sqrt_price_x_96 / Q96)) / log(BASE))

    pool.initialize(sqrt_price_x_96)
    initialized_sqrt_price_x96, initialized_tick, _, _, _, _, _ = pool.slot0()

    common_decimal_denominator = liq.decimals() - wbtc.decimals()

    # rounding here since in essence should be 0.99999...
    p = round(((BASE**initialized_tick) / (10**common_decimal_denominator)))

    # assert the following conditions against the pool after initialization state
    assert initialized_tick > 0 and initialized_sqrt_price_x96 > 0
    assert initialized_tick == expected_tick
    # proofs parity on the pair creation!
    assert PARITY_PAIR_VALUE == p
