from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from scripts import ebtc_timelock_lens as lens
from rich.console import Console

C = Console()


def main():
    C.print("[yellow]Initial timelocks state:\n[/yellow]")
    lens.main()

    safe = GreatApeSafe(registry.eth.ebtc_wallets.security_multisig)
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
        timelock.revokeRole(
            timelock.TIMELOCK_ADMIN_ROLE(), registry.eth.ebtc_wallets.security_multisig
        )

    C.print("[yellow]\nFinal timelocks state:\n[/yellow]")
    # Print out new state
    lens.main()

    safe.post_safe_tx()
