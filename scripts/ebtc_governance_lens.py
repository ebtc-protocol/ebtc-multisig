from great_ape_safe import GreatApeSafe
from brownie import network
from rich.console import Console
from helpers.addresses import reverse, r
import pandas as pd
from tabulate import tabulate
import os
import time

C = Console()


def main(export_csv=False):
    """
    The following script iterates through the different pieces that make up the Authority's state and outputs it to the console.
    This includes al exisiting roles, their names, the users they are assigned to, as well as the target and capabilities for each.
    """

    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()
    authority = safe.ebtc.authority

    # Print the state of the Authority
    C.print(f"[cyan]Authority's state[/cyan]")
    C.print(f"[yellow]Authority address: {authority.address}[/yellow]")
    C.print(f"[yellow]Authority's Owner: {authority.owner()}[/yellow]")

    ## Get DF for roles, their names and the users they are assigned to
    roles_data = []
    roles = 0
    while True:
        try:
            name = authority.getRoleName(roles)
            if name == "":
                break
            users = authority.getUsersByRole(roles)
            user_addresses = "\n".join(users)  # Replace comma with new line
            user_ids = "\n".join(
                reverse[user] if user in reverse else "Unknown" for user in users
            )  # Replace comma with new line
            roles_data.append([roles, name, user_addresses, user_ids])
            roles += 1
        except:
            break

    roles_df = pd.DataFrame(
        roles_data, columns=["Role", "Name", "User Addresses", "User IDs"]
    )

    ## Gets df for roles, their targets and capabilities
    enabled_data = []
    ebtc_section = r.ebtc
    ebtc_section.pop("test_contracts", None)  # For testnets
    targets = list(ebtc_section.values())

    # Get function signatures mapping of IDs
    governance_signatures = safe.ebtc.governance_signatures
    reversed_signatures = {v: k for k, v in governance_signatures.items()}

    for target in targets:
        target_id = reverse[target]
        functions = authority.getEnabledFunctionsInTarget(target)
        for function in functions:
            function_id = reversed_signatures.get(f"{function}")
            roles = extract_roles(authority.getRolesWithCapability(target, function))
            for role in roles:
                enabled_data.append([role, target, target_id, function_id])

    # Group all values in single rows for each role
    grouped_data = {}
    for row in enabled_data:
        role = row[0]
        target = row[1]
        target_id = row[2]
        function_id = row[3]
        if role not in grouped_data:
            grouped_data[role] = {"Target": [], "Target ID": [], "Function": []}
        grouped_data[role]["Target"].append(target)
        grouped_data[role]["Target ID"].append(target_id)
        grouped_data[role]["Function"].append(function_id)

    # Create a new dataframe with grouped data
    grouped_df = pd.DataFrame(columns=["Role", "Target", "Target ID", "Function"])
    for role, values in grouped_data.items():
        target_str = "\n".join(values["Target"])
        target_id_str = "\n".join(values["Target ID"])
        function_str = "\n".join(values["Function"])
        grouped_df = grouped_df.append(
            {
                "Role": role,
                "Target": target_str,
                "Target ID": target_id_str,
                "Function": function_str,
            },
            ignore_index=True,
        )

    # Sort the dataframe by the "Role" column
    grouped_df = grouped_df.sort_values(by="Role")

    # Merge all data for each role and print final table
    merged_df = pd.merge(roles_df, grouped_df, on="Role")
    merged_table = tabulate(
        merged_df,
        headers=[
            "Role",
            "Name",
            "User Addresses",
            "User IDs",
            "Target",
            "Target ID",
            "Function",
        ],
        tablefmt="fancy_grid",
    )
    C.print(merged_table)

    if export_csv:
        # Dump result
        os.makedirs("data/authority_audit/", exist_ok=True)
        timestamp = int(time.time())  # Get current Unix timestamp
        merged_df.to_csv(
            f"data/authority_audit/authority_audit_{network.show_active()}_{timestamp}.csv",
            index=False,
        )


def extract_roles(bitmask):
    # Convert bytes32 bitmask to integer
    bitmask_int = int.from_bytes(bitmask, byteorder="big")

    # Initialize an empty list to store the roles
    roles = []

    # Iterate over each bit in the bitmask
    for role in range(256):  # A bytes32 value is 256 bits
        # Shift the integer to the right by the number of positions specified by the role
        shifted = bitmask_int >> role

        # Perform a bitwise AND operation with 1 to check if the bit at the position is set
        if (shifted & 1) != 0:
            # If the bit is set, add the role to the list
            roles.append(role)

    return roles
