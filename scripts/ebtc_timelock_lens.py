from great_ape_safe import GreatApeSafe
from brownie import accounts, network
import pandas as pd
from tabulate import tabulate
from helpers.addresses import reverse
import os
from rich.console import Console

C = Console()

def main(export_csv=False):
    safe = GreatApeSafe(accounts[0].address)
    safe.init_ebtc()

    timelocks = {
        "lowsec_timelock": safe.ebtc.lowsec_timelock,
        "highsec_timelock": safe.ebtc.highsec_timelock,
    }

    roles = {
        "DEFAULT_ADMIN_ROLE": timelocks["lowsec_timelock"].DEFAULT_ADMIN_ROLE(),
        "TIMELOCK_ADMIN_ROLE": timelocks["lowsec_timelock"].TIMELOCK_ADMIN_ROLE(),
        "PROPOSER_ROLE": timelocks["lowsec_timelock"].PROPOSER_ROLE(),
        "CANCELLER_ROLE": timelocks["lowsec_timelock"].CANCELLER_ROLE(),
        "EXECUTOR_ROLE": timelocks["lowsec_timelock"].EXECUTOR_ROLE(),
    }

    for timelock_key, timelock in timelocks.items():
        timelock_data = []
        delay = timelock.getMinDelay()
        C.print(f"[blue]{timelock_key}, delay: {delay}s[/blue]")
        for key, role in roles.items():
            role_member_count = timelock.getRoleMemberCount(role)
            role_admin = timelock.getRoleAdmin(role)
            for k, v in roles.items():
                if f"{v}" == f"{role_admin}":
                    role_admin = k
            for member_number in range(role_member_count):
                member_address = timelock.getRoleMember(role, member_number)
                member_id = reverse[member_address]
                timelock_data.append(
                    {
                        "timelock_contract": timelock_key,
                        "role": key,
                        "role_admin": role_admin,
                        "member_number": member_number,
                        "member_address": member_address,
                        "member_id": member_id,
                    }
                )

        C.print(tabulate(timelock_data, headers="keys", tablefmt="grid"))

        if export_csv:
            # build dataframe
            df = pd.DataFrame(timelock_data)
            # Dump result
            os.makedirs("data/timelocks_audit", exist_ok=True)
            df.to_csv(
                f"data/timelocks_audit/{timelock_key}_audit_{network.show_active()}.csv"
            )
