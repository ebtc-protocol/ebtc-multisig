from brownie import chain
import pytest
from helpers.constants import EmptyBytes32
from scripts.stebtc_auth import set_stebtc_auth


def test_stebtc_auth(security_multisig):
    security_multisig.init_ebtc()

    # before
    assert security_multisig.ebtc.authority.getRoleName(13) == ""
    assert security_multisig.ebtc.authority.getRoleName(14) == ""
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.active_pool.feeRecipientAddress(),
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.donate.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.setMinRewardsPerPeriod.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.sweep.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.setMaxDistributionPerSecondPerAsset.signature,
        )
        == False
    )

    set_stebtc_auth(security_multisig)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    set_stebtc_auth(security_multisig)

    # after
    assert security_multisig.ebtc.authority.getRoleName(13) == "StakedEbtc: Donor"
    assert security_multisig.ebtc.authority.getRoleName(14) == "StakedEbtc: Manager"
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.active_pool.feeRecipientAddress(),
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.donate.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.setMinRewardsPerPeriod.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.sweep.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.staked_ebtc,
            security_multisig.ebtc.staked_ebtc.setMaxDistributionPerSecondPerAsset.signature,
        )
        == True
    )
