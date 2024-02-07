from brownie import chain
import pytest
from helpers.constants import EmptyBytes32


def test_grant_timelock_role_happy(techops, random_safe):
    techops.init_ebtc()

    techops.ebtc.grant_timelock_role("PROPOSER_ROLE", random_safe.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.grant_timelock_role("PROPOSER_ROLE", random_safe.account)

    assert techops.ebtc.lowsec_timelock.hasRole(
        techops.ebtc.lowsec_timelock.PROPOSER_ROLE(), random_safe.account
    )


def test_revoke_timelock_role_happy(techops, security_multisig):
    techops.init_ebtc()

    techops.ebtc.revoke_timelock_role("PROPOSER_ROLE", security_multisig.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.revoke_timelock_role("PROPOSER_ROLE", security_multisig.account)

    assert (
        techops.ebtc.lowsec_timelock.hasRole(
            techops.ebtc.lowsec_timelock.PROPOSER_ROLE(), security_multisig.account
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


def test_high_sec_management_happy(security_multisig):
    security_multisig.init_ebtc()
    new_dalay = 1000

    security_multisig.ebtc.update_timelock_delay(new_dalay, EmptyBytes32, True)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.update_timelock_delay(new_dalay, EmptyBytes32, True)

    assert security_multisig.ebtc.highsec_timelock.getMinDelay() == new_dalay


def test_high_sec_management_permissions(techops):
    techops.init_ebtc()
    new_dalay = 1000

    with pytest.raises(AssertionError):
        techops.ebtc.update_timelock_delay(new_dalay, EmptyBytes32, True)
