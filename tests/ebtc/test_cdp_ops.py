import pytest


def test_cdp_open_happy(random_safe, setup_test_coll):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.open_cdp(coll_amount, 160e16)


def test_cdp_close_happy(random_safe, setup_test_coll, setup_base_cdp):
    coll_amount = 5e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    random_safe.ebtc.close_cdp(cdp_id)


def test_cdp_add_collateral_happy(random_safe, setup_test_coll):
    coll_amount = 5e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    random_safe.ebtc.cdp_add_collateral(cdp_id, coll_amount)


def test_cdp_withdraw_collateral_happy(random_safe, setup_test_coll):
    coll_amount = 5e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    random_safe.ebtc.cdp_withdraw_collateral(cdp_id, coll_amount / 10)


def test_cdp_repay_debt_happy(random_safe, setup_test_coll):
    coll_amount = 5e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    ebtc_balance = random_safe.ebtc.ebtc_token.balanceOf(random_safe)

    random_safe.ebtc.cdp_repay_debt(cdp_id, ebtc_balance / 10)


def test_cdp_withdraw_debt_happy(random_safe, setup_test_coll):
    coll_amount = 5e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    ebtc_balance = random_safe.ebtc.ebtc_token.balanceOf(random_safe)

    random_safe.ebtc.cdp_withdraw_debt(cdp_id, ebtc_balance / 9)


def test_adjust_cdp_with_collateral_increase_debt_and_collateral(
    random_safe, setup_test_coll
):
    coll_amount = 5e18
    coll_shares = random_safe.ebtc.collateral.getSharesByPooledEth(coll_amount)
    debt_amount = 0.1e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    (
        prev_debt,
        prev_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    # Increase the collateral amount and increase the debt
    random_safe.ebtc.adjust_cdp_with_collateral(
        cdp_id,
        0,
        debt_amount,
        True,
        coll_amount,
    )

    (
        final_debt,
        final_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    assert final_debt == prev_debt + debt_amount
    assert final_coll_shares == prev_coll_shares + coll_shares


def test_adjust_cdp_with_collateral_decrease_debt_and_collateral(
    random_safe, setup_test_coll
):
    coll_amount = 10e18
    coll_reduction = 2e18
    coll_reduction_shares = random_safe.ebtc.collateral.getSharesByPooledEth(
        coll_reduction
    )
    debt_amount = 0.01e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    (
        prev_debt,
        prev_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    # Reduce the collateral amount and repay some debt
    random_safe.ebtc.adjust_cdp_with_collateral(
        cdp_id,
        coll_reduction,
        debt_amount,
        False,
        0,
    )

    (
        final_debt,
        final_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    assert final_debt == prev_debt - debt_amount
    assert final_coll_shares == prev_coll_shares - coll_reduction_shares


def test_adjust_cdp_with_collateral_decrease_debt_and_increase_collateral(
    random_safe, setup_test_coll
):
    coll_amount = 10e18
    coll_increase = 2e18
    coll_increase_shares = random_safe.ebtc.collateral.getSharesByPooledEth(
        coll_increase
    )
    debt_amount = 0.01e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    (
        prev_debt,
        prev_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    # Increase the collateral amount and repay some debt
    random_safe.ebtc.adjust_cdp_with_collateral(
        cdp_id,
        0,
        debt_amount,
        False,
        coll_increase,
    )

    (
        final_debt,
        final_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    assert final_debt == prev_debt - debt_amount
    assert final_coll_shares == prev_coll_shares + coll_increase_shares


def test_adjust_cdp_with_collateral_increase_debt_and_decrease_collateral(
    random_safe, setup_test_coll
):
    coll_amount = 10e18
    coll_reduction = 2e18
    coll_reduction_shares = random_safe.ebtc.collateral.getSharesByPooledEth(
        coll_reduction
    )
    debt_amount = 0.01e18
    random_safe.init_ebtc()

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    (
        prev_debt,
        prev_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    # Reduce the collateral amount and increase the debt
    random_safe.ebtc.adjust_cdp_with_collateral(
        cdp_id,
        coll_reduction,
        debt_amount,
        True,
        0,
    )

    (
        final_debt,
        final_coll_shares,
    ) = random_safe.ebtc.cdp_manager.getSyncedDebtAndCollShares(cdp_id)

    assert final_debt == prev_debt + debt_amount
    assert final_coll_shares == prev_coll_shares - coll_reduction_shares
