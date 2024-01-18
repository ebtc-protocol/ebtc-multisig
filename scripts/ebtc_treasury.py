from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

"""
The following scripts are meant to provide a convenient access to the multisig treausry operations of the EBTC ecosystem.
These script will use the default multisig intended for each of the operations.
"""


"""
Low Sec Treasury Operations

The following operations are meant to be executed by the Fee Recipient multisig.
"""


def activePool_claim_fee_recipient_coll_shares(value):
    """
    Set the fee recipient address for the ActivePool contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.fee_recipient_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.claimFeeRecipientCollShares\n")
    safe.ebtc.activePool_claim_fee_recipient_coll_shares(value)

    safe.post_safe_tx()


def activePool_sweep_token(token_address, value):
    """
    Sweep a token from the ActivePool contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.fee_recipient_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for ActivePool.sweepToken\n")
    safe.ebtc.activePool_sweep_token(token_address, value)

    safe.post_safe_tx()


def collSurplusPool_sweep_token(token_address, value):
    """
    Sweep a token from the CollSurplusPool contract.
    """
    safe = GreatApeSafe(r.ebtc_wallets.fee_recipient_multisig)
    safe.init_ebtc()
    C.print(f"\nUsing {safe.account} for CollSurplusPool.sweepToken\n")
    safe.ebtc.collSurplusPool_sweep_token(token_address, value)

    safe.post_safe_tx()
