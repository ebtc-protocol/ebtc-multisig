from great_ape_safe import GreatApeSafe

from brownie import multicall, web3

from helpers.constants import AddressZero
from helpers.addresses import r


def main(balancer_creation_and_seed=False):
    safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    safe.init_balancer()
    safe.init_uni_v3()

    # tokens
    wbtc = safe.contract(r.assets.wbtc)
    ebtc = safe.contract(r.assets.ebtc)

    # contracts
    pool_factory = safe.contract(r.balancer.composable_stable_pool_factory)

    # snap
    safe.take_snapshot(tokens=[ebtc, wbtc])

    # 1. remove univ3 positions
    nfts_owned = safe.uni_v3.nonfungible_position_manager.balanceOf(safe) - 1

    if nfts_owned >= 0:
        with multicall:
            token_ids = [
                safe.uni_v3.nonfungible_position_manager.tokenOfOwnerByIndex(safe, i)
                for i in range(nfts_owned)
            ]
        for token_id in token_ids:
            if (
                r.assets.ebtc
                == safe.uni_v3.nonfungible_position_manager.positions(token_id)[3]
            ):
                safe.uni_v3.burn_token_id(token_id)

    # 2. conditionally create balancer pool and seed it to avoid disrupting onchain liquidity
    if balancer_creation_and_seed:
        amplification_factor = 500  # @note TBD-BALCO!
        token_rate_cache_duration = 600  # @note TBD-BALCO! (10min)
        swap_fee = 500000000000000  # 0.05%

        # 2.1. pool creation
        pool_address = pool_factory.create(
            "Balancer WBTC/eBTC",
            "WBTC/eBTC",
            [r.assets.wbtc, r.assets.ebtc],
            amplification_factor,
            [AddressZero, AddressZero],  # rateProviders
            [
                token_rate_cache_duration,
                token_rate_cache_duration,
            ],  # tokenRateCacheDurations
            True,  # exemptFromYieldProtocolFeeFlag. There is not intrinsic yield to be extracted from tokens
            swap_fee,  # swapFeePercentage
            safe.address,  # owner
            web3.solidityKeccak(["string"], ["EBTC_PROTOCOL_POOL"]).hex(),  # salt
        ).return_value

        # 2.2. pool seeding
        # @note TBD: should be all liquidity wd being seed on the new pool?

    safe.print_snapshot()

    safe.post_safe_tx()
