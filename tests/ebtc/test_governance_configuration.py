from brownie import chain, accounts

# Test authority_set_role_name


def test_authority_set_role_name_happy(security_multisig):
    security_multisig.init_ebtc()
    role = 10
    security_multisig.ebtc.authority_set_role_name(role, "test_name")

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_role_name(role, "test_name")

    assert security_multisig.ebtc.authority.getRoleName(role) == "test_name"


# Test authority_set_user_role


def test_authority_set_user_role_happy(security_multisig, random_safe):
    security_multisig.init_ebtc()
    role = 6

    security_multisig.ebtc.authority_set_user_role(random_safe.account, role, True)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_user_role(random_safe.account, role, True)

    assert security_multisig.ebtc.authority.doesUserHaveRole(random_safe.account, role) == True


# Test authority_set_role_capability


def test_authority_set_role_capability_happy(security_multisig):
    security_multisig.init_ebtc()

    mock_signature = "0x1a1a1a1a"
    target = security_multisig.ebtc.ebtc_token.address
    role = 7

    security_multisig.ebtc.authority_set_role_capability(role, target, mock_signature, True)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_role_capability(role, target, mock_signature, True)

    assert (
        security_multisig.ebtc.authority.doesRoleHaveCapability(role, target, mock_signature)
        == True
    )

    # Now we test disabling the capability
    security_multisig.ebtc.authority_set_role_capability(role, target, mock_signature, False)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_role_capability(role, target, mock_signature, False)

    assert (
        security_multisig.ebtc.authority.doesRoleHaveCapability(role, target, mock_signature)
        == False
    )


# Test authority_set_public_capability


def test_authority_set_public_capability_happy(security_multisig):
    security_multisig.init_ebtc()

    mock_signature = "0x1a1a1a1a"
    target = security_multisig.ebtc.ebtc_token.address

    security_multisig.ebtc.authority_set_public_capability(target, mock_signature, True)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_public_capability(target, mock_signature, True)

    assert security_multisig.ebtc.authority.isPublicCapability(target, mock_signature) == True

    # Now we test making cabaility private
    security_multisig.ebtc.authority_set_public_capability(target, mock_signature, False)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_public_capability(target, mock_signature, False)

    assert security_multisig.ebtc.authority.isPublicCapability(target, mock_signature) == False


# Test authority_burn_capability


def test_authority_burn_capability_happy(security_multisig):
    security_multisig.init_ebtc()

    target = security_multisig.ebtc.active_pool
    signature = target.setFeeBps.signature
    actor = security_multisig.ebtc.lowsec_timelock.address

    # Confirm that the actor can call the function
    assert security_multisig.ebtc.authority.canCall(actor, target.address, signature) == True

    security_multisig.ebtc.authority_burn_capability(target.address, signature)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    # Governance capability is burned over the target and function signature
    security_multisig.ebtc.authority_burn_capability(target, signature)

    # Actor can no longer call the function
    assert security_multisig.ebtc.authority.canCall(actor, target.address, signature) == False


# Test authority_set_authority


def test_authority_set_authority_happy(security_multisig):
    security_multisig.init_ebtc()

    new_authority = accounts[9].address

    security_multisig.ebtc.authority_set_authority(new_authority)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.authority_set_authority(new_authority)

    assert security_multisig.ebtc.authority.authority() == new_authority
