from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

"""
The following scripts are meant to provide a convenient access to timelock management functions for both eBTC Tiemlocks.
"""


"""
Low Sec Timelock Management Operations

The following operations are meant to be executed by the TechOps multisig.
"""


def lowsec_grant_timelock_role(role_key, account):
    """
    Grant a role to an account for the Low Sec Timelock.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for LowSecTimelock.grantRole\n")
    safe.ebtc.grant_timelock_role(role_key, account)

    safe.post_safe_tx()


def lowsec_revoke_timelock_role(role_key, account):
    """
    Revoke a role from an account for the Low Sec Timelock.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for LowSecTimelock.revokeRole\n")
    safe.ebtc.revoke_timelock_role(role_key, account)

    safe.post_safe_tx()


def lowsec_update_timelock_delay(new_delay):
    """
    Set the new_delay for the Low Sec Timelock.
    """
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for LowSecTimelock.updateDelay\n")
    safe.ebtc.update_timelock_delay(new_delay)

    safe.post_safe_tx()


"""
High Sec Timelock Management Operations

The following operations are meant to be executed by the Ecossytem multisig.
"""


def highsec_grant_timelock_role(role_key, account):
    """
    Grant a role to an account for the Low Sec Timelock.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for HighSecTimelock.grantRole\n")
    safe.ebtc.grant_timelock_role(role_key, account, True)

    safe.post_safe_tx()


def highsec_revoke_timelock_role(role_key, account):
    """
    Revoke a role from an account for the Low Sec Timelock.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for HighSecTimelock.revokeRole\n")
    safe.ebtc.revoke_timelock_role(role_key, account, True)

    safe.post_safe_tx()


def highsec_update_timelock_delay(new_delay):
    """
    Set the new_delay for the Low Sec Timelock.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for HighSecTimelock.updateDelay\n")
    safe.ebtc.update_timelock_delay(new_delay, True)

    safe.post_safe_tx()


def lowsec_cancel_timelock(
    id, target=None, value=None, data=None, predecessor=None, salt=None
):
    """
    Cancel a transaction for the Low Sec Timelock. If ID is unknown, pass 0x0 and provide the parameters instead.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for LowSecTimelock.cancel\n")
    safe.ebtc.cancel_lowsec_timelock(id, target, value, data, predecessor, salt)

    safe.post_safe_tx()


def highsec_cancel_timelock(
    id, target=None, value=None, data=None, predecessor=None, salt=None
):
    """
    Cancel a transaction for the High Sec Timelock. If ID is unknown, pass 0x0 and provide the parameters instead.
    """
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for HighSecTimelock.cancel\n")
    safe.ebtc.cancel_highsec_timelock(id, target, value, data, predecessor, salt)

    safe.post_safe_tx()
