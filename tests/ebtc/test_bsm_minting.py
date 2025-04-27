from brownie import chain
import pytest
from helpers.constants import EmptyBytes32
from scripts.bsm_minting import set_bsm_minting


def test_bsm_minting(security_multisig):
    security_multisig.init_ebtc()

    # before
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.ebtc_token,
            security_multisig.ebtc.ebtc_token.mint.signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.ebtc_token,
            security_multisig.ebtc.ebtc_token.burn.methods["address", "uint"].signature,
        )
        == False
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.ebtc_token,
            security_multisig.ebtc.ebtc_token.burn.methods[
                "uint",
            ].signature,
        )
        == False
    )

    set_bsm_minting(security_multisig)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    set_bsm_minting(security_multisig)

    # before
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.ebtc_token,
            security_multisig.ebtc.ebtc_token.mint.signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.ebtc_token,
            security_multisig.ebtc.ebtc_token.burn.methods["address", "uint"].signature,
        )
        == True
    )
    assert (
        security_multisig.ebtc.authority.canCall(
            security_multisig.ebtc.bsm,
            security_multisig.ebtc.ebtc_token,
            security_multisig.ebtc.ebtc_token.burn.methods[
                "uint",
            ].signature,
        )
        == True
    )
