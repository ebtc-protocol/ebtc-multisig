from brownie import chain

from great_ape_safe import GreatApeSafe

from helpers.addresses import r
from helpers.constants import EmptyBytes32

# @note that txs are schedule individually due to timelock ui support (lack of batching support atm)
def main(sim=False):
    # safe: security msig is a proposer in `highsec_timelock`
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()

    # contracts
    highsec_timelock = safe.ebtc.highsec_timelock
    treasury_timelock = r.ebtc.treasury_timelock  # @note TBD once it's deployed
    auth = safe.ebtc.authority

    # 1. disable role `CDP_MANAGER_ALL` (3) signature `SET_STAKING_REWARD_SPLIT_SIG`
    disable_role_data = auth.setRoleCapability.encode_input(
        safe.ebtc.governance_roles.CDP_MANAGER_ALL.value,
        r.ebtc.cdp_manager,
        safe.ebtc.governance_signatures["SET_STAKING_REWARD_SPLIT_SIG"],
        False,
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, disable_role_data, EmptyBytes32
    )

    # 2. create new role `PYS_REWARD_SPLIT_SETTER` (12) provided to the treasury_timelock
    set_user_role_data = auth.setUserRole.encode_input(
        treasury_timelock,
        safe.ebtc.governance_roles.PYS_REWARD_SPLIT_SETTER.value,
        True,
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, set_user_role_data, EmptyBytes32
    )

    # 3. enable role `STETH_MARKET_RATE_SWITCHER` (12) authority over signature `SET_STAKING_REWARD_SPLIT_SIG`
    enable_pys_signature_data = auth.setRoleCapability.encode_input(
        safe.ebtc.governance_roles.PYS_REWARD_SPLIT_SETTER.value,
        r.ebtc.cdp_manager,
        safe.ebtc.governance_signatures["SET_STAKING_REWARD_SPLIT_SIG"],
        True,
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, enable_pys_signature_data, EmptyBytes32
    )

    # sim the exec after delay
    if sim:
        delay = highsec_timelock.getMinDelay()  # 1 week
        chain.sleep(delay + 1)
        chain.mine()

        # read point 1) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, disable_role_data, EmptyBytes32
        )
        # read point 2) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, set_user_role_data, EmptyBytes32
        )
        # read point 3) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, enable_pys_signature_data, EmptyBytes32
        )

    else:
        safe.post_safe_tx()
