from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from helpers.constants import EmptyBytes32
from rich.console import Console

C = Console()


def set_bsm_minting(safe):
    data = [
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.bsm,
            safe.ebtc.governance_roles.EBTC_MINTER.value,
            True,
        ),
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.bsm,
            safe.ebtc.governance_roles.EBTC_BURNER.value,
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

    set_bsm_minting(safe)

    safe.post_safe_tx(tenderly=False)
