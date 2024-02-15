from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from helpers.constants import EmptyBytes32
from rich.console import Console

C = Console()

"""
The following scripts are meant to provide a convenient access to the multisig governance operations of the EBTC security.
These script will use the default multisig intended for each of the timelocks. In other words, operations interacting with
the Low Sec Timelock will TechOps multisig and those interacting with the High Sec Timelock will use the security multisig.

NOTE: Operations interacting with timelock will need to be executed twice. Once to queue the transaction and once to execute
it at the end of the delay period.
"""


"""
Low Sec Governance Operations

The following operations are meant to be executed by the TechOps multisig.
"""


def cdpManager_set_staking_reward_split(value, salt=EmptyBytes32):
    """
    Set the staking reward split for the CDPManager contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setStakingRewardSplit\n")
    safe.ebtc.cdpManager_set_staking_reward_split(value, salt)

    safe.post_safe_tx()


def cdpManager_set_redemption_fee_floor(value, salt=EmptyBytes32):
    """
    Set the redemption fee floor for the CDPManager contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setRedemptionFeeFloor\n")
    safe.ebtc.cdpManager_set_redemption_fee_floor(value, salt)

    safe.post_safe_tx()


def cdpManager_set_minute_decay_factor(value, salt=EmptyBytes32):
    """
    Set the minute decay factor for the CDPManager contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setMinuteDecayFactor\n")
    safe.ebtc.cdpManager_set_minute_decay_factor(value, salt)

    safe.post_safe_tx()


def cdpManager_set_beta(value, salt=EmptyBytes32):
    """
    Set the beta for the CDPManager contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setBeta\n")
    safe.ebtc.cdpManager_set_beta(value, salt)

    safe.post_safe_tx()


def cdpManager_set_redemptions_paused(pause, salt=EmptyBytes32):
    """
    Pause or unpause redemptions for the CDPManager contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setRedemptionsPaused\n")
    safe.ebtc.cdpManager_set_redemptions_paused(pause, use_timelock=True, salt=salt)

    safe.post_safe_tx()


def cdpManager_set_grace_period(value, salt=EmptyBytes32):
    """
    Set the grace period for the CDPManager contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setGracePeriod\n")
    safe.ebtc.cdpManager_set_grace_period(value, salt)

    safe.post_safe_tx()


def priceFeed_set_fallback_caller(address, salt=EmptyBytes32):
    """
    Set the fallback caller for the PriceFeed contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for PriceFeed.setFallbackCaller\n")
    safe.ebtc.priceFeed_set_fallback_caller(address, salt)

    safe.post_safe_tx()


def activePool_set_fee_bps(value, salt=EmptyBytes32):
    """
    Set the fee basis points for the ActivePool contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.setFeeBps\n")
    safe.ebtc.activePool_set_fee_bps(value, salt)

    safe.post_safe_tx()


def borrowerOperations_set_fee_bps(value, salt=EmptyBytes32):
    """
    Set the fee basis points for the BorrowerOperations contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for BorrowerOperations.setFeeBps\n")
    safe.ebtc.borrowerOperations_set_fee_bps(value, salt)

    safe.post_safe_tx()


def ebtcFeed_set_secondary_oracle(address, salt=EmptyBytes32):
    """
    Set the secondary oracle for the EBTCFeed contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for EBTCFeed.setSecondaryOracle\n")
    safe.ebtc.ebtcFeed_set_secondary_oracle(address, salt)

    safe.post_safe_tx()


"""
High Sec Governance Operations

The following operations are meant to be executed by the security multisig.
"""


def authority_set_role_name(role, name, salt=EmptyBytes32):
    """
    Set the role name for the Authority contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for Authority.setRoleName\n")
    safe.ebtc.authority_set_role_name(role, name, salt)

    safe.post_safe_tx()


def authority_set_user_role(user, role, enabled, salt=EmptyBytes32):
    """
    Set the user role for the Authority contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for Authority.setUserRole\n")
    safe.ebtc.authority_set_user_role(user, role, enabled, salt)

    safe.post_safe_tx()


def authority_set_role_capability(role, target_address, functionSig, enabled, salt=EmptyBytes32):
    """
    Set the role capability for the Authority contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for Authority.setRoleCapability\n")
    safe.ebtc.authority_set_role_capability(role, target_address, functionSig, enabled, salt)

    safe.post_safe_tx()


def authority_set_public_capability(target_address, functionSig, enabled, salt=EmptyBytes32):
    """
    Set the public capability for the Authority contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for Authority.setPublicCapability\n")
    safe.ebtc.authority_set_public_capability(target_address, functionSig, enabled, salt)

    safe.post_safe_tx()


def authority_burn_capability(target_address, functionSig, salt=EmptyBytes32):
    """
    Burn the capability for the Authority contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for Authority.burnCapability\n")
    safe.ebtc.authority_burn_capability(target_address, functionSig, salt)

    safe.post_safe_tx()


def authority_set_authority(new_authority, salt=EmptyBytes32):
    """
    Set the authority for the Authority contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for Authority.setAuthority\n")
    safe.ebtc.authority_set_authority(new_authority, salt)

    safe.post_safe_tx()


def ebtcFeed_set_primary_oracle(address, salt=EmptyBytes32):
    """
    Set the primary oracle for the EBTCFeed contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for EBTCFeed.setPrimaryOracle\n")
    safe.ebtc.ebtcFeed_set_primary_oracle(address, salt)

    safe.post_safe_tx()


"""
WAROOM: Pausing operations

The following scripts are meant to be executed by the TechOps or Security multisig and
are used to pause or unpause certain functions directly.
"""


def cdpManager_set_redemptions_paused_techops(pause):
    """
    Pause or unpause redemptions for the CDPManager contract from the TechOps multisig.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setRedemptionsPaused\n")
    safe.ebtc.cdpManager_set_redemptions_paused(pause)

    safe.post_safe_tx()


def cdpManager_set_redemptions_paused_security(pause):
    """
    Pause or unpause redemptions for the CDPManager contract from the Security multisig.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CDPManager.setRedemptionsPaused\n")
    safe.ebtc.cdpManager_set_redemptions_paused(pause)

    safe.post_safe_tx()


def activePool_set_flash_loans_paused_techops(pause):
    """
    Pause or unpause flashloans for the ActivePool contract from the TechOps multisig.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.setFlashloansPaused\n")
    safe.ebtc.activePool_set_flash_loans_paused(pause)

    safe.post_safe_tx()


def activePool_set_flash_loans_paused_security(pause):
    """
    Pause or unpause flashloans for the ActivePool contract from the Security multisig.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.setFlashloansPaused\n")
    safe.ebtc.activePool_set_flash_loans_paused(pause)

    safe.post_safe_tx()


def borrowerOperations_set_flash_loans_paused_techops(pause):
    """
    Pause or unpause flashloans for the BorrowerOperations contract from the TechOps multisig.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for BorrowerOperations.setFlashLoansPaused\n")
    safe.ebtc.borrowerOperations_set_flash_loans_paused(pause)

    safe.post_safe_tx()


def borrowerOperations_set_flash_loans_paused_security(pause):
    """
    Pause or unpause flashloans for the BorrowerOperations contract from the Security multisig.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for BorrowerOperations.setFlashLoansPaused\n")
    safe.ebtc.borrowerOperations_set_flash_loans_paused(pause)

    safe.post_safe_tx()


def pause_flashloans_techops(pause):
    """
    Pause or unpause flashloans for the ActivePool and BorrowerOperations contracts from the TechOps multisig.
    """

    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.setFlashloansPaused\n")
    safe.ebtc.activePool_set_flash_loans_paused(pause)
    C.print(f"\nUsing {safe.account} for BorrowerOperations.setFlashLoansPaused\n")
    safe.ebtc.borrowerOperations_set_flash_loans_paused(pause)

    safe.post_safe_tx()


def pause_flashloans_security(pause):
    """
    Pause or unpause flashloans for the ActivePool and BorrowerOperations contracts from the Security multisig.
    """

    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.setFlashloansPaused\n")
    safe.ebtc.activePool_set_flash_loans_paused(pause)
    C.print(f"\nUsing {safe.account} for BorrowerOperations.setFlashLoansPaused\n")
    safe.ebtc.borrowerOperations_set_flash_loans_paused(pause)

    safe.post_safe_tx()
