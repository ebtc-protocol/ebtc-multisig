from math import sqrt

from great_ape_safe import GreatApeSafe
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import Q96

from brownie import interface
from helpers.addresses import r
from rich.console import Console

C = Console()

# --- Forum Scope ---
# link: https://forum.badger.finance/t/ebtc-launch-planning-peg-management-and-monetary-policy/6129#protocol-owned-liquidity-6

# misc.
FEE_TIER = 500
PCT_10 = 0.1
PCT_40 = 0.4


def pool_creation_and_init_seeding():
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    safe.init_uni_v3()

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    # ebtc = safe.contract(r.assets.ebtc)
    # @note this is a random token just to exemplify the scope of the script till ebtc is deployed
    liq = safe.contract(r.assets.liq)

    # 1. pool creation: tick spacing should be end-up being `10`
    # ref: https://github.com/Uniswap/v3-core/blob/main/contracts/UniswapV3Factory.sol#L26
    pool_address = safe.uni_v3.factory.createPool(liq, wbtc, FEE_TIER).return_value
    C.print(f"[green]Pool address is: {pool_address}[/green]")

    # 2. pool initialize
    pool = interface.IUniswapV3Pool(pool_address, owner=safe.account)
    # @note: order of which is token0 & token1 depends on
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

    # 3. seed pool on four ranges
    # POL target: 25ebtc/25wbtc
    # Initial seeding is smaller size than final aim: 10%. 2.5/2.5
    price_0925 = 0.925
    price_099 = 0.99
    price_1 = 1
    price_101 = 1.01
    price_108 = 1.08

    # @note these figures are note definitive, will be updated in the future!
    token_0_init_seeding_amount = 2.5e8 if token0 == wbtc.address else 2.5e18
    token_1_init_seeding_amount = 2.5e18 if token1 == liq.address else 2.5e8

    # single-side lp only ebtc
    safe.uni_v3.mint_position(
        pool, price_0925, price_099, token_0_init_seeding_amount * PCT_10 * 2, 0
    )

    # range with active tick at [.99,1] & [1,1.01]
    safe.uni_v3.mint_position(
        pool,
        price_099,
        price_1,
        token_0_init_seeding_amount * PCT_40,
        token_1_init_seeding_amount * PCT_40,
    )
    safe.uni_v3.mint_position(
        pool,
        price_1,
        price_101,
        token_0_init_seeding_amount * PCT_40,
        token_1_init_seeding_amount * PCT_40,
    )

    # single-side only wbtc
    safe.uni_v3.mint_position(
        pool, price_101, price_108, 0, token_1_init_seeding_amount * PCT_10 * 2
    )

    safe.post_safe_tx()
