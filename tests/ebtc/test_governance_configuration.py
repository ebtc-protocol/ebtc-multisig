from brownie import chain, accounts

# Test authority_set_role_name

def test_authority_set_role_name_happy(ecosystem):
    ecosystem.init_ebtc()
    role = 10
    ecosystem.ebtc.authority_set_role_name(role, "test_name")

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_role_name(role, "test_name")

    assert ecosystem.ebtc.authority.getRoleName(role) == "test_name"


# Test authority_set_user_role

def test_authority_set_user_role_happy(ecosystem, random_safe):
    ecosystem.init_ebtc()
    role = 6

    ecosystem.ebtc.authority_set_user_role(random_safe.account, role, True)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_user_role(random_safe.account, role, True)

    assert ecosystem.ebtc.authority.doesUserHaveRole(random_safe.account, role) == True


# Test authority_set_role_capability

def test_authority_set_role_capability_happy(ecosystem):
    ecosystem.init_ebtc()

    mock_signature = "0x1a1a1a1a"
    target = ecosystem.ebtc.ebtc_token.address
    role = 7

    ecosystem.ebtc.authority_set_role_capability(role, target, mock_signature, True)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_role_capability(role, target, mock_signature, True)

    assert (
        ecosystem.ebtc.authority.doesRoleHaveCapability(role, target, mock_signature)
        == True
    )

    # Now we test disabling the capability
    ecosystem.ebtc.authority_set_role_capability(role, target, mock_signature, False)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_role_capability(role, target, mock_signature, False)

    assert (
        ecosystem.ebtc.authority.doesRoleHaveCapability(role, target, mock_signature)
        == False
    )


# Test authority_set_public_capability

def test_authority_set_public_capability_happy(ecosystem):
    ecosystem.init_ebtc()

    mock_signature = "0x1a1a1a1a"
    target = ecosystem.ebtc.ebtc_token.address

    ecosystem.ebtc.authority_set_public_capability(target, mock_signature, True)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_public_capability(target, mock_signature, True)

    assert (
        ecosystem.ebtc.authority.isPublicCapability(target, mock_signature)
        == True
    )

    # Now we test making cabaility private
    ecosystem.ebtc.authority_set_public_capability(target, mock_signature, False)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_public_capability(target, mock_signature, False)

    assert (
        ecosystem.ebtc.authority.isPublicCapability(target, mock_signature)
        == False
    )

# Test authority_burn_capability

def test_authority_burn_capability_happy(ecosystem):
    ecosystem.init_ebtc()

    target = ecosystem.ebtc.active_pool
    signature = target.setFeeBps.signature
    actor = ecosystem.ebtc.lowsec_timelock.address

    # Confirm that the actor can call the function
    assert ecosystem.ebtc.authority.canCall(actor, target.address, signature) == True

    ecosystem.ebtc.authority_burn_capability(target.address, signature)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    # Governance capability is burned over the target and function signature
    ecosystem.ebtc.authority_burn_capability(target, signature)

    # Actor can no longer call the function
    assert ecosystem.ebtc.authority.canCall(actor, target.address, signature) == False


# Test authority_set_authority

def test_authority_set_authority_happy(ecosystem):
    ecosystem.init_ebtc()

    new_authority = accounts[9].address

    ecosystem.ebtc.authority_set_authority(new_authority)

    chain.sleep(ecosystem.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    ecosystem.ebtc.authority_set_authority(new_authority)

    assert ecosystem.ebtc.authority.authority() == new_authority



