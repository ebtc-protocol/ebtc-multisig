from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console
from rich.table import Table

C = Console()

"""
The following methods are meant to provide insight of cdp's owned by specific msig:
    - cdp id
    - collateral and debt amounts
    - ICR and TCR
    - % of total collateral of the cdp's and system
    - $ of total debt of the cdp's and system
    - cdp list ordered by ICR
"""


def main(msig_address=r.badger_wallets.treasury_vault_multisig):
    # table generation
    table = Table(title=f"CDPs owned by {msig_address} ordered by ICR")

    table.add_column("Cdp ID", justify="right")
    table.add_column("Collateral", justify="right")
    table.add_column("Debt", justify="right")
    table.add_column("ICR", justify="right")
    table.add_column("cdp collateral vs total cdp's owned (%)", justify="right")
    table.add_column("cdp debt vs total cdp's owned (%)", justify="right")

    safe = GreatApeSafe(msig_address)
    safe.init_ebtc()

    # helpers vars
    cdps_info = []
    total_collateral = 0
    total_debt = 0

    # general TCR info of the system at current oracle price w/ all elements sync
    feed_price = safe.ebtc.price_feed.fetchPrice.call()
    current_tcr = safe.ebtc.cdp_manager.getSyncedTCR(feed_price)
    C.print(
        f"[cyan]System's TCR: {(current_tcr/1e16):.3f}%. Oracle price: {(feed_price/1e18):.3f}.\n[/cyan]"
    )

    cdps_safe_owned = safe.ebtc.sorted_cdps.getCdpsOf(safe)
    for cdp_id in cdps_safe_owned:
        C.print(f"[green]Inspecting cdp id: {cdp_id}\n[/green]")
        (
            cdp_id_debt,
            cdp_id_coll,
            _,
            _,
            _,
            _,
        ) = safe.ebtc.cdp_manager.Cdps(cdp_id)
        icr = safe.ebtc.cdp_manager.getSyncedICR(cdp_id, feed_price)

        # increase global vars
        total_collateral += cdp_id_coll
        total_debt += cdp_id_debt

        cdps_info.append((cdp_id, cdp_id_coll, cdp_id_debt, icr))

    # reordering cdps by ICR
    ICR_INDEX = 3
    cdps_info.sort(key=lambda x: x[ICR_INDEX])

    # fill up table rows
    for cdp_info in cdps_info:
        table.add_row(
            f"{str(cdp_info[0])[:7]}...{str(cdp_info[0])[-7:]}",
            f"{(cdp_info[1] / 10 ** 18):.3f}",
            f"{(cdp_info[2] / 10 ** 18):.3f}",
            f"{(cdp_info[3] / 1e16):.3f}%",
            f"{(cdp_info[1] / total_collateral * 100):.3f}%",
            f"{(cdp_info[2] / total_debt * 100):.3f}%",
        )

    # table printout
    C.print(table)
