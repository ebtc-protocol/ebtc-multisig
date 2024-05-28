from brownie import chain, web3

from great_ape_safe import GreatApeSafe

from helpers.addresses import r

from scripts.ebtc_governance_lens import main as ebtc_governance_lens

SALT = web3.solidityKeccak(
    ["string"], ["PYS_STAKING_REWARD_SPLIT_INTO_TREASURY_TIMELOCK"]
).hex()

# @note that txs are schedule individually due to timelock ui support (lack of batching support atm)
def main(sim=True):
    # safe: security msig is a proposer in `highsec_timelock`
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()

    print("SALT:", SALT)

    # contracts
    highsec_timelock = safe.ebtc.highsec_timelock
    treasury_timelock = r.ebtc.treasury_timelock
    auth = safe.ebtc.authority

    # 1. disable role `CDP_MANAGER_ALL` (3) signature `SET_STAKING_REWARD_SPLIT_SIG`
    disable_role_data = auth.setRoleCapability.encode_input(
        safe.ebtc.governance_roles.CDP_MANAGER_ALL.value,
        r.ebtc.cdp_manager,
        safe.ebtc.governance_signatures["SET_STAKING_REWARD_SPLIT_SIG"],
        False,
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, disable_role_data, SALT
    )

    # 2. create new role `PYS_REWARD_SPLIT_SETTER` (12) provided to the treasury_timelock
    set_user_role_data = auth.setUserRole.encode_input(
        treasury_timelock,
        safe.ebtc.governance_roles.PYS_REWARD_SPLIT_SETTER.value,
        True,
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, set_user_role_data, SALT
    )

    # 3. Set name for the new role as `CDPManager: setStakingRewardSplit`
    set_role_name_data = auth.setRoleName.encode_input(
        safe.ebtc.governance_roles.PYS_REWARD_SPLIT_SETTER.value,
        "CDPManager: setStakingRewardSplit",
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, set_role_name_data, SALT
    )

    # 4. enable role `STETH_MARKET_RATE_SWITCHER` (12) authority over signature `SET_STAKING_REWARD_SPLIT_SIG`
    enable_pys_signature_data = auth.setRoleCapability.encode_input(
        safe.ebtc.governance_roles.PYS_REWARD_SPLIT_SETTER.value,
        r.ebtc.cdp_manager,
        safe.ebtc.governance_signatures["SET_STAKING_REWARD_SPLIT_SIG"],
        True,
    )
    safe.ebtc.schedule_or_execute_timelock(
        highsec_timelock, auth, enable_pys_signature_data, SALT
    )

    # sim the exec after delay
    if sim:
        delay = highsec_timelock.getMinDelay()  # 1 week
        chain.sleep(delay + 1)
        chain.mine()

        # read point 1) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, disable_role_data, SALT
        )
        # read point 2) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, set_user_role_data, SALT
        )
        # read point 3) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, set_role_name_data, SALT
        )
        # read point 4) above
        assert True == safe.ebtc.schedule_or_execute_timelock(
            highsec_timelock, auth, enable_pys_signature_data, SALT
        )
        ebtc_governance_lens()

    else:
        safe.post_safe_tx()
