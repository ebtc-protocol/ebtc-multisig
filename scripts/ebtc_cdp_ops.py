from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

"""
The following methods are meant to provide the interface for:
    - opening & closing a cdp
    - increase and/or decrease collateral of an existing cdp id
    - repay and/or withdraw debt of an existing cdp id
"""


def open_cdp(collateral_amount, target_collateral_ratio):
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(
        f"\nUsing {safe.account} for opening cdp position with {collateral_amount} collateral at {target_collateral_ratio}% CR\n"
    )
    safe.ebtc.open_cdp(collateral_amount * 1e18, target_collateral_ratio * 1e16)
    safe.post_safe_tx()


def close_cdp(cdp_id):
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for closing cdp position with {cdp_id} id\n")
    safe.ebtc.close_cdp(cdp_id)
    safe.post_safe_tx()


def cdp_add_collateral(cdp_id, collateral_amount):
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(
        f"\nUsing {safe.account} for increasing {collateral_amount} collateral at cdp position with {cdp_id} id\n"
    )
    safe.ebtc.cdp_add_collateral(cdp_id, collateral_amount * 1e18)
    safe.post_safe_tx()


def cdp_withdraw_collateral(cdp_id, collateral_amount):
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(
        f"\nUsing {safe.account} for decreasing {collateral_amount} collateral at cdp position with {cdp_id} id\n"
    )
    safe.ebtc.cdp_withdraw_collateral(cdp_id, collateral_amount * 1e18)
    safe.post_safe_tx()


def cdp_repay_debt(cdp_id, debt_repay_amount):
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(
        f"\nUsing {safe.account} for repaying {debt_repay_amount} debt at cdp position with {cdp_id} id\n"
    )
    safe.ebtc.cdp_repay_debt(cdp_id, debt_repay_amount * 1e18)
    safe.post_safe_tx()


def cdp_withdraw_debt(cdp_id, debt_withdrawable_amount):
    safe = GreatApeSafe(r.ebtc_wallets.techops_multisig)
    safe.init_ebtc()
    C.print(
        f"\nUsing {safe.account} for withdrawing {debt_withdrawable_amount} debt at cdp position with {cdp_id} id\n"
    )
    safe.ebtc.cdp_withdraw_debt(cdp_id, debt_withdrawable_amount * 1e18)
    safe.post_safe_tx()
