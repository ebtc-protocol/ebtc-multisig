from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from helpers.constants import EmptyBytes32
from rich.console import Console

C = Console()


def set_stebtc_auth(safe):
    data = [
        # Role capabilities
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.STEBTC_DONOR.value,
            safe.ebtc.staked_ebtc,
            safe.ebtc.staked_ebtc.donate.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.STEBTC_MANAGER.value,
            safe.ebtc.staked_ebtc,
            safe.ebtc.staked_ebtc.sweep.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.STEBTC_MANAGER.value,
            safe.ebtc.staked_ebtc,
            safe.ebtc.staked_ebtc.setMintingFee.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.STEBTC_MANAGER.value,
            safe.ebtc.staked_ebtc,
            safe.ebtc.staked_ebtc.setMaxDistributionPerSecondPerAsset.signature,
            True,
        ),
        # Grant roles
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.active_pool.feeRecipientAddress(),
            safe.ebtc.governance_roles.STEBTC_DONOR.value,
            True,
        ),
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.techops_multisig,
            safe.ebtc.governance_roles.STEBTC_MANAGER.value,
            True,
        ),
    ]
    targets = [safe.ebtc.authority] * len(data)
    values = [0] * len(data)

    safe.ebtc.schedule_or_execute_batch_timelock(
        safe.ebtc.highsec_timelock, targets, values, data, EmptyBytes32
    )


def main():
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()

    set_stebtc_auth(safe)

    safe.post_safe_tx(tenderly=False)
