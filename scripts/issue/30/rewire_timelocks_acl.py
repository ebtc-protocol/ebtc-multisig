from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from scripts import ebtc_timelock_lens as lens
from rich.console import Console
from helpers.constants import EmptyBytes32

C = Console()


def main():
    C.print("[yellow]Initial timelocks state:\n[/yellow]")
    lens.main()

    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()

    timelocks = {
        "lowsec_timelock": safe.ebtc.lowsec_timelock,
        "highsec_timelock": safe.ebtc.highsec_timelock,
    }

    for id, timelock in timelocks.items():
        C.print(f"[blue]Rewiring {id}[/blue]")
        ## Remove all cancellers
        C.print(f"[yellow]Removing all cancellers from {id}[/yellow]")
        members = []
        for i in range(timelock.getRoleMemberCount(timelock.CANCELLER_ROLE())):
            members.append(timelock.getRoleMember(timelock.CANCELLER_ROLE(), i))
        for member in members:
            timelock.revokeRole(timelock.CANCELLER_ROLE(), member)
            C.print(f"[yellow]Removed {member} from {id} CANCELLER_ROLE[/yellow]")
        assert timelock.getRoleMemberCount(timelock.CANCELLER_ROLE()) == 0

        ## Assert Timelock has TIMELOCK_ADMIN_ROLE
        assert timelock.hasRole(timelock.TIMELOCK_ADMIN_ROLE(), timelock.address)
        C.print(f"[yellow]{id} has TIMELOCK_ADMIN_ROLE[/yellow]")
        ## Remove security multisig as TIMELOCK_ADMIN_ROLE
        C.print(
            f"[yellow]Removing security multisig from {id} TIMELOCK_ADMIN_ROLE[/yellow]"
        )
        ## We could revoke the TIMELOCK_ADMIN_ROLE from the security multisig directly but will do
        ## through the Timelocks instead in order to test the flows. Will require exection once both time periods are met.
        ## Execution can be handled by using the lowsec_revoke_timelock_role() and highsec_revoke_timelock_role() scripts
        ## within the scripts/ebtc_timelocks.py file.
        safe.ebtc.revoke_timelock_role(
            "TIMELOCK_ADMIN_ROLE",
            r.ebtc_wallets.security_multisig,
            EmptyBytes32,
            timelock.address == timelocks["highsec_timelock"],  # Use highSec
        )

    C.print("[yellow]\nFinal timelocks state:\n[/yellow]")
    # Print out new state
    lens.main()

    safe.post_safe_tx(skip_preview=True)
