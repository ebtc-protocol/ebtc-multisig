from helpers.addresses import r
from great_ape_safe import GreatApeSafe
from rich.console import Console
from brownie import interface

C = Console()

SENTINEL_OWNERS = "0x0000000000000000000000000000000000000001"

TECHOPS_SINGERS = r.ebtc_wallets.techops_signers
TREASURY_SIGNERS = r.badger_wallets.treasury_signers

HIGHSEC_TECHOPS_MULTISIG = r.ebtc_wallets.security_multisig
LOWSEC_TECHOPS_MULTISIG = r.ebtc_wallets.techops_multisig
FEE_RECIPIENT_MULTISIG = r.ebtc_wallets.fee_recipient_multisig

LOWSEC_POLICY = 3
HIGHSEC_POLICY = 4
FEE_RECIPIENT_POLICY = 3

# The following script iterates through the existing signers of each mutlisigs and adds/removes accordingly to end up
# with the desired signers. In addition, the script also sets the final policy as intended.
# HighSec TechOps: 4/7
# LowSec TechOps: 3/7
# FeeRecipient: 3/9


def highsec_config():
    safe = GreatApeSafe(HIGHSEC_TECHOPS_MULTISIG)
    highsec_techops = safe.contract(HIGHSEC_TECHOPS_MULTISIG, interface.IGnosisSafe_v1_3_0)

    configure_multisig(highsec_techops, TECHOPS_SINGERS, HIGHSEC_POLICY)

    safe.post_safe_tx()


def lowsec_config():
    safe = GreatApeSafe(LOWSEC_TECHOPS_MULTISIG)
    lowsec_techops = safe.contract(LOWSEC_TECHOPS_MULTISIG, interface.IGnosisSafe_v1_3_0)

    configure_multisig(lowsec_techops, TECHOPS_SINGERS, LOWSEC_POLICY)

    safe.post_safe_tx()


def fee_recipient_config():
    safe = GreatApeSafe(FEE_RECIPIENT_MULTISIG)
    fee_recipient = safe.contract(FEE_RECIPIENT_MULTISIG, interface.IGnosisSafe_v1_3_0)

    configure_multisig(fee_recipient, TREASURY_SIGNERS, FEE_RECIPIENT_POLICY)

    safe.post_safe_tx()


def configure_multisig(target, signers, policy):
    current_owners = target.getOwners()
    current_policy = target.getThreshold()
    C.print(f"Current signers: {current_owners}")
    C.print(f"Current policy: {current_policy}")

    for signer in signers.values():
        if signer not in current_owners:
            target.addOwnerWithThreshold(signer, policy)

    for owner in current_owners:
        if owner not in signers.values():
            prev_owner = get_previous_owner(target, owner)
            target.removeOwner(prev_owner, owner, policy)

    if target.getThreshold() != policy:
        target.changeThreshold(policy)

    C.print(f"New signers: {target.getOwners()}")
    C.print(f"New policy: {target.getThreshold()}")


def get_previous_owner(safe, owner):
    owners = safe.getOwners()
    for i in range(len(owners)):
        if owners[i] == owner:
            if i == 0:
                return SENTINEL_OWNERS
            else:
                return owners[i - 1]
