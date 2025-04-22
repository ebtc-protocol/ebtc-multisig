from brownie import chain
import pytest
from helpers.constants import EmptyBytes32
from scripts.bsm_auth import set_bsm_auth

def test_bsm_auth(security_multisig):
    security_multisig.init_ebtc()

    # before
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.updateEscrow.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setOraclePriceConstraint.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setRateLimitingConstraint.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setBuyAssetConstraint.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.lowsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setFeeToSell.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.lowsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setFeeToBuy.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.security_multisig,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.pause.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.security_multisig,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.unpause.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.security_multisig,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm_escrow.claimProfit.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_escrow,
            security_multisig.ebtc.bsm_escrow.claimProfit.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_escrow,
            security_multisig.ebtc.bsm_escrow.claimTokens.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_oracle_price_constraint,
            security_multisig.ebtc.bsm_oracle_price_constraint.setMinPrice.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_oracle_price_constraint,
            security_multisig.ebtc.bsm_oracle_price_constraint.setOracleFreshness.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_rate_limiting_constraint,
            security_multisig.ebtc.bsm_rate_limiting_constraint.setMintingConfig.signature,
        )
        == False
    )

    set_bsm_auth(security_multisig)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    set_bsm_auth(security_multisig)

    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.updateEscrow.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setOraclePriceConstraint.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setRateLimitingConstraint.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.highsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setBuyAssetConstraint.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.lowsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setFeeToSell.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.lowsec_timelock,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.setFeeToBuy.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.security_multisig,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.pause.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.security_multisig,
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.bsm.unpause.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_escrow,
            security_multisig.ebtc.bsm_escrow.claimProfit.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_escrow,
            security_multisig.ebtc.bsm_escrow.claimTokens.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_oracle_price_constraint,
            security_multisig.ebtc.bsm_oracle_price_constraint.setMinPrice.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_oracle_price_constraint,
            security_multisig.ebtc.bsm_oracle_price_constraint.setOracleFreshness.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.techops_multisig,
            security_multisig.ebtc.bsm_rate_limiting_constraint,
            security_multisig.ebtc.bsm_rate_limiting_constraint.setMintingConfig.signature,
        )
        == True
    )
