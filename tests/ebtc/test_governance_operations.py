from brownie import chain
import pytest
from helpers.constants import EmptyBytes32


# Test cdpManager_set_staking_reward_split
def test_cdpManager_set_staking_reward_split_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_staking_reward_split(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_staking_reward_split(1000)

    assert techops.ebtc.cdp_manager.stakingRewardSplit() == 1000


# Test cdpManager_set_redemption_fee_floor
def test_cdpManager_set_redemption_fee_floor_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_redemption_fee_floor(0.006e18)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_redemption_fee_floor(0.006e18)

    assert techops.ebtc.cdp_manager.redemptionFeeFloor() == 0.006e18


# Test cdpManager_set_minute_decay_factor
def test_cdpManager_set_minute_decay_factor_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_minute_decay_factor(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_minute_decay_factor(1000)

    assert techops.ebtc.cdp_manager.minuteDecayFactor() == 1000


# Test cdpManager_set_beta
def test_cdpManager_set_beta_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_beta(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_beta(1000)

    assert techops.ebtc.cdp_manager.beta() == 1000


# Test cdpManager_set_redemptions_paused
def test_cdpManager_set_redemptions_paused_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_redemptions_paused(True)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_redemptions_paused(True)

    assert techops.ebtc.cdp_manager.redemptionsPaused() == True


# Test cdpManager_set_grace_period
def test_cdpManager_set_grace_period_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_grace_period(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_grace_period(1000)

    assert techops.ebtc.cdp_manager.recoveryModeGracePeriodDuration() == 1000


# Test priceFeed_set_fallback_caller
def test_priceFeed_set_fallback_caller_happy(techops):
    techops.init_ebtc()
    techops.ebtc.priceFeed_set_fallback_caller(techops.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.priceFeed_set_fallback_caller(techops.account)

    assert techops.ebtc.price_feed.fallbackCaller() == techops.account


# Test activePool_set_fee_bps
def test_activePool_set_fee_bps_happy(techops):
    techops.init_ebtc()
    techops.ebtc.activePool_set_fee_bps(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.activePool_set_fee_bps(1000)

    assert techops.ebtc.active_pool.feeBps() == 1000

# Test borrowerOperations_set_fee_bps
def test_borrowerOperations_set_fee_bps_happy(techops):
    techops.init_ebtc()
    techops.ebtc.borrowerOperations_set_fee_bps(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.borrowerOperations_set_fee_bps(1000)

    assert techops.ebtc.borrower_operations.feeBps() == 1000


# Test activePool_set_fee_recipient_address
def test_activePool_set_fee_recipient_address_happy(techops):
    techops.init_ebtc()
    techops.ebtc.activePool_set_fee_recipient_address(techops.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.activePool_set_fee_recipient_address(techops.account)

    assert techops.ebtc.active_pool.feeRecipientAddress() == techops.account


# Test borrowerOperations_set_fee_recipient_address
def test_borrowerOperations_set_fee_recipient_address_happy(techops):
    techops.init_ebtc()
    techops.ebtc.borrowerOperations_set_fee_recipient_address(techops.account)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.borrowerOperations_set_fee_recipient_address(techops.account)

    assert techops.ebtc.borrower_operations.feeRecipientAddress() == techops.account


# Test activePool_claim_fee_recipient_coll_shares
def test_activePool_claim_fee_recipient_coll_shares_happy(fee_recipient):
    fee_recipient.init_ebtc()

    claimable = fee_recipient.ebtc.active_pool.getFeeRecipientClaimableCollShares()
    value = claimable / 2 if claimable > 0 else 0

    coll = fee_recipient.ebtc.collateral
    recipient = fee_recipient.ebtc.active_pool.feeRecipientAddress()

    shares_before = coll.sharesOf(recipient)
    fee_recipient.ebtc.activePool_claim_fee_recipient_coll_shares(value)
    assert coll.sharesOf(recipient) - shares_before == value


def test_activePool_claim_fee_recipient_coll_shares_permissions(random_safe):
    random_safe.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Not authorized"):
        random_safe.ebtc.activePool_claim_fee_recipient_coll_shares(1)


# Test activePool_sweep_token
def test_activePool_sweep_token_happy(fee_recipient, wbtc, ecosystem):
    fee_recipient.init_ebtc()

    active_pool = fee_recipient.ebtc.active_pool.address
    recipient = fee_recipient.ebtc.active_pool.feeRecipientAddress()
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(fee_recipient.ebtc.active_pool.address, amount, {"from": ecosystem.account})
    assert wbtc.balanceOf(active_pool) == amount

    balance_before = wbtc.balanceOf(recipient)
    fee_recipient.ebtc.activePool_sweep_token(wbtc.address, amount)
    assert wbtc.balanceOf(recipient) - balance_before == amount


def test_activePool_sweep_token_permissions(wbtc, ecosystem, random_safe):
    random_safe.init_ebtc()

    active_pool = random_safe.ebtc.active_pool.address
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(random_safe.ebtc.active_pool.address, amount, {"from": ecosystem.account})
    assert wbtc.balanceOf(active_pool) == amount

    with pytest.raises(AssertionError, match="Error: Not authorized"):
        random_safe.ebtc.activePool_sweep_token(wbtc.address, amount)


# Test activePool_sweep_token
def test_collSurplusPool_sweep_token_happy(fee_recipient, wbtc, ecosystem):
    fee_recipient.init_ebtc()

    coll_surplus_pool = fee_recipient.ebtc.coll_surplus_pool.address
    recipient = fee_recipient.ebtc.coll_surplus_pool.feeRecipientAddress()
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(fee_recipient.ebtc.coll_surplus_pool.address, amount, {"from": ecosystem.account})
    assert wbtc.balanceOf(coll_surplus_pool) == amount

    balance_before = wbtc.balanceOf(recipient)
    fee_recipient.ebtc.collSurplusPool_sweep_token(wbtc.address, amount)
    assert wbtc.balanceOf(recipient) - balance_before == amount


def test_collSurplusPool_sweep_token_permissions(wbtc, ecosystem, random_safe):
    random_safe.init_ebtc()

    coll_surplus_pool = random_safe.ebtc.coll_surplus_pool.address
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(random_safe.ebtc.coll_surplus_pool.address, amount, {"from": ecosystem.account})
    assert wbtc.balanceOf(coll_surplus_pool) == amount

    with pytest.raises(AssertionError, match="Error: Not authorized"):
        random_safe.ebtc.collSurplusPool_sweep_token(wbtc.address, amount)

