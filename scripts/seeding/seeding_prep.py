from math import sqrt

from great_ape_safe import GreatApeSafe
from great_ape_safe.ape_api.helpers.uni_v3.uni_v3_sdk import Q96

from brownie import interface
from helpers.addresses import r
from rich.console import Console

C = Console()

# misc.cow
COEF = 0.98
DEADLINE = 60 * 60 * 3

# misc.coll amount (it should equate at current rates into 800 $steth)
RETH_AMOUNT = 730

safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
safe.init_uni_v3()


def prep():
    safe.init_cow(prod=True)

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)
    reth = safe.contract(r.assets.reth)
    steth = safe.contract(r.assets.steth)

    # =========== $reth -> $steth swap (happens async) ===========
    reth_amount = RETH_AMOUNT * 10 ** reth.decimals()
    safe.cow.market_sell(reth, steth, reth_amount, deadline=DEADLINE, coef=COEF)

    # =========== pool creation & initialization ===========

    _pool_creation(ebtc, wbtc)

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
