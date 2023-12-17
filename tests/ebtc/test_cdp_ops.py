import pytest


def test_cdp_open_happy(random_safe):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.collateral.forceDeposit(coll_amount)

    random_safe.ebtc.open_cdp(coll_amount, 160e16)


def test_cdp_close_happy(random_safe):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.collateral.forceDeposit(coll_amount)

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    random_safe.ebtc.close_cdp(cdp_id)


def test_cdp_add_collateral_happy(random_safe):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.collateral.forceDeposit(coll_amount * 2)

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    random_safe.ebtc.cdp_add_collateral(cdp_id, coll_amount)


def test_cdp_withdraw_collateral_happy(random_safe):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.collateral.forceDeposit(coll_amount)

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    random_safe.ebtc.cdp_withdraw_collateral(cdp_id, coll_amount / 10)


def test_cdp_repay_debt_happy(random_safe):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.collateral.forceDeposit(coll_amount)

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    ebtc_balance = random_safe.ebtc.ebtc_token.balanceOf(random_safe)

    random_safe.ebtc.cdp_repay_debt(cdp_id, ebtc_balance / 10)


def test_cdp_withdraw_debt_happy(random_safe):
    coll_amount = 5e18
    random_safe.init_ebtc()

    random_safe.ebtc.collateral.forceDeposit(coll_amount)

    cdp_id = random_safe.ebtc.open_cdp(coll_amount, 160e16)

    ebtc_balance = random_safe.ebtc.ebtc_token.balanceOf(random_safe)

    random_safe.ebtc.cdp_withdraw_debt(cdp_id, ebtc_balance / 9)
