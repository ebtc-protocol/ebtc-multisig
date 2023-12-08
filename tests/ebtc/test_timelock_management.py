from brownie import chain
import pytest


def test_grant_timelock_role_happy(techops, random_safe):
    techops.init_ebtc()

    techops.ebtc.grant_timelock_role("PROPOSER_ROLE", random_safe.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.grant_timelock_role("PROPOSER_ROLE", random_safe.account)

    assert techops.ebtc.lowsec_timelock.hasRole(
        techops.ebtc.lowsec_timelock.PROPOSER_ROLE(), random_safe.account
    )


def test_revoke_timelock_role_happy(techops, council):
    techops.init_ebtc()

    techops.ebtc.revoke_timelock_role("PROPOSER_ROLE", council.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.revoke_timelock_role("PROPOSER_ROLE", council.account)

    assert (
        techops.ebtc.lowsec_timelock.hasRole(
            techops.ebtc.lowsec_timelock.PROPOSER_ROLE(), council.account
        )
        == False
    )


def test_update_timelock_delay_happy(techops):
    techops.init_ebtc()
    new_dalay = 400

    techops.ebtc.update_timelock_delay(new_dalay)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.update_timelock_delay(new_dalay)

    assert techops.ebtc.lowsec_timelock.getMinDelay() == new_dalay


def test_high_sec_management_happy(ecosystem):
    ecosystem.init_ebtc()
    new_dalay = 1000

    ecosystem.ebtc.update_timelock_delay(new_dalay, True)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.update_timelock_delay(new_dalay, True)

    assert ecosystem.ebtc.highsec_timelock.getMinDelay() == new_dalay


def test_high_sec_management_permissions(techops):
    techops.init_ebtc()
    new_dalay = 1000

    with pytest.raises(AssertionError):
        techops.ebtc.update_timelock_delay(new_dalay, True)
