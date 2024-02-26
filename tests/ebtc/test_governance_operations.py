from brownie import chain
import pytest
from helpers.constants import (
    AddressZero,
    EmptyBytes32,
    DECIMAL_PRECISION,
    MAX_REWARD_SPLIT,
    MIN_REDEMPTION_FEE_FLOOR,
    MIN_MINUTE_DECAY_FACTOR,
    MAX_MINUTE_DECAY_FACTOR,
    MINIMUM_GRACE_PERIOD,
    MAX_FEE_BPS,
)


# Test cdpManager_set_staking_reward_split
def test_cdpManager_set_staking_reward_split_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_staking_reward_split(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_staking_reward_split(1000)

    assert techops.ebtc.cdp_manager.stakingRewardSplit() == 1000


# Test cdpManager_set_staking_reward_split value checks
def test_cdpManager_set_staking_reward_split_checks(techops):
    techops.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Value too high"):
        techops.ebtc.cdpManager_set_staking_reward_split(MAX_REWARD_SPLIT + 1)


# Test cdpManager_set_redemption_fee_floor
def test_cdpManager_set_redemption_fee_floor_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_redemption_fee_floor(0.006e18)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_redemption_fee_floor(0.006e18)

    assert techops.ebtc.cdp_manager.redemptionFeeFloor() == 0.006e18


# Test cdpManager_set_redemption_fee_floor value checks
def test_cdpManager_set_redemption_fee_floor_checks(techops):
    techops.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Value too low"):
        techops.ebtc.cdpManager_set_redemption_fee_floor(MIN_REDEMPTION_FEE_FLOOR - 1)

    with pytest.raises(AssertionError, match="Error: Value too high"):
        techops.ebtc.cdpManager_set_redemption_fee_floor(DECIMAL_PRECISION + 1)


# Test cdpManager_set_minute_decay_factor
def test_cdpManager_set_minute_decay_factor_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_minute_decay_factor(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_minute_decay_factor(1000)

    assert techops.ebtc.cdp_manager.minuteDecayFactor() == 1000


# Test cdpManager_set_minute_decay_factor value checks
def test_cdpManager_set_minute_decay_factor_checks(techops):
    techops.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Value too low"):
        techops.ebtc.cdpManager_set_minute_decay_factor(MIN_MINUTE_DECAY_FACTOR - 1)

    with pytest.raises(AssertionError, match="Error: Value too high"):
        techops.ebtc.cdpManager_set_minute_decay_factor(MAX_MINUTE_DECAY_FACTOR + 1)


# Test cdpManager_set_beta
def test_cdpManager_set_beta_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_beta(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_beta(1000)

    assert techops.ebtc.cdp_manager.beta() == 1000


# Test cdpManager_set_redemptions_paused from Timelock
def test_cdpManager_set_redemptions_paused_happy_timelock(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_redemptions_paused(
        True, use_timelock=True, salt=EmptyBytes32, use_high_sec=False
    )

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_redemptions_paused(
        True, use_timelock=True, salt=EmptyBytes32, use_high_sec=False
    )

    assert techops.ebtc.cdp_manager.redemptionsPaused() == True


# Test cdpManager_set_redemptions_paused from TechOps
def test_cdpManager_set_redemptions_paused_happy_techOps(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_redemptions_paused(
        True, use_timelock=False, salt=EmptyBytes32, use_high_sec=False
    )

    assert techops.ebtc.cdp_manager.redemptionsPaused() == True


# Test cdpManager_set_redemptions_paused from Security Multisig
def test_cdpManager_set_redemptions_paused_happy_securityMultisig(security_multisig):
    security_multisig.init_ebtc()
    security_multisig.ebtc.cdpManager_set_redemptions_paused(
        True, use_timelock=False, salt=EmptyBytes32, use_high_sec=True
    )

    assert security_multisig.ebtc.cdp_manager.redemptionsPaused() == True


# Test cdpManager_set_grace_period
def test_cdpManager_set_grace_period_happy(techops):
    techops.init_ebtc()
    techops.ebtc.cdpManager_set_grace_period(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.cdpManager_set_grace_period(1000)

    assert techops.ebtc.cdp_manager.recoveryModeGracePeriodDuration() == 1000


# Test cdpManager_set_grace_period value checks
def test_cdpManager_set_grace_period_checks(techops):
    techops.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Value too low"):
        techops.ebtc.cdpManager_set_grace_period(MINIMUM_GRACE_PERIOD - 1)


# Test priceFeed_set_fallback_caller
def test_priceFeed_set_fallback_caller_happy(techops, mock_fallback_caller):
    techops.init_ebtc()

    ## Setup mock fallback caller with current price
    current_price = techops.ebtc.ebtc_feed.lastGoodPrice()
    current_time = chain.time()
    mock_fallback_caller.setFallbackResponse(
        current_price, current_time, True, {"from": techops.account}
    )
    techops.ebtc.priceFeed_set_fallback_caller(mock_fallback_caller)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.priceFeed_set_fallback_caller(mock_fallback_caller)

    assert techops.ebtc.price_feed.fallbackCaller() == mock_fallback_caller


# Test ebtcFeed_set_primary_oracle
def test_ebtcFeed_set_primary_oracle_happy(security_multisig, test_price_feed):
    security_multisig.init_ebtc()
    security_multisig.ebtc.ebtcFeed_set_primary_oracle(test_price_feed)

    chain.sleep(security_multisig.ebtc.highsec_timelock.getMinDelay() + 1)
    chain.mine()

    security_multisig.ebtc.ebtcFeed_set_primary_oracle(test_price_feed)

    assert security_multisig.ebtc.ebtc_feed.primaryOracle() == test_price_feed


# Test ebtcFeed_set_secondary_oracle
def test_ebtcFeed_set_secondary_oracle_happy(techops, test_price_feed):
    techops.init_ebtc()
    techops.ebtc.ebtcFeed_set_secondary_oracle(test_price_feed)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.ebtcFeed_set_secondary_oracle(test_price_feed)

    assert techops.ebtc.ebtc_feed.secondaryOracle() == test_price_feed


# Test activePool_set_fee_bps
def test_activePool_set_fee_bps_happy(techops):
    techops.init_ebtc()
    techops.ebtc.activePool_set_fee_bps(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.activePool_set_fee_bps(1000)

    assert techops.ebtc.active_pool.feeBps() == 1000


# Test activePool_set_fee_bps value checks
def test_activePool_set_fee_bps_checks(techops):
    techops.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Value too high"):
        techops.ebtc.activePool_set_fee_bps(MAX_FEE_BPS + 1)


# Test borrowerOperations_set_fee_bps
def test_borrowerOperations_set_fee_bps_happy(techops):
    techops.init_ebtc()
    techops.ebtc.borrowerOperations_set_fee_bps(1000)

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.borrowerOperations_set_fee_bps(1000)

    assert techops.ebtc.borrower_operations.feeBps() == 1000


# Test borrowerOperations_set_fee_bps value checks
def test_borrowerOperations_set_fee_bps_checks(techops):
    techops.init_ebtc()
    with pytest.raises(AssertionError, match="Error: Value too high"):
        techops.ebtc.borrowerOperations_set_fee_bps(MAX_FEE_BPS + 1)


# Test activePool_set_flash_loans_paused from Timelock
def test_activePool_set_flash_loans_paused_happy_timelock(techops):
    techops.init_ebtc()
    techops.ebtc.activePool_set_flash_loans_paused(
        True, use_timelock=True, salt=EmptyBytes32, use_high_sec=False
    )

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.activePool_set_flash_loans_paused(
        True, use_timelock=True, salt=EmptyBytes32, use_high_sec=False
    )

    assert techops.ebtc.active_pool.flashLoansPaused() == True


# Test activePool_set_flash_loans_paused from TechOps
def test_activePool_set_flash_loans_paused_happy_techOps(techops):
    techops.init_ebtc()
    techops.ebtc.activePool_set_flash_loans_paused(
        True, use_timelock=False, salt=EmptyBytes32, use_high_sec=False
    )

    assert techops.ebtc.active_pool.flashLoansPaused() == True


# Test activePool_set_flash_loans_paused from Security Multisig
def test_activePool_set_flash_loans_paused_happy_securityMultisig(security_multisig):
    security_multisig.init_ebtc()
    security_multisig.ebtc.activePool_set_flash_loans_paused(
        True, use_timelock=False, salt=EmptyBytes32, use_high_sec=True
    )

    assert security_multisig.ebtc.active_pool.flashLoansPaused() == True


# Test borrowerOperations_set_flash_loans_paused from Timelock
def test_borrowerOperations_set_flash_loans_paused_happy_timelock(techops):
    techops.init_ebtc()
    techops.ebtc.borrowerOperations_set_flash_loans_paused(
        True, use_timelock=True, salt=EmptyBytes32, use_high_sec=False
    )

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.borrowerOperations_set_flash_loans_paused(
        True, use_timelock=True, salt=EmptyBytes32, use_high_sec=False
    )

    assert techops.ebtc.borrower_operations.flashLoansPaused() == True


# Test borrowerOperations_set_flash_loans_paused from TechOps
def test_borrowerOperations_set_flash_loans_paused_happy_techOps(techops):
    techops.init_ebtc()
    techops.ebtc.borrowerOperations_set_flash_loans_paused(
        True, use_timelock=False, salt=EmptyBytes32, use_high_sec=False
    )

    assert techops.ebtc.borrower_operations.flashLoansPaused() == True


# Test borrowerOperations_set_flash_loans_paused from Security Multisig
def test_borrowerOperations_set_flash_loans_paused_happy_securityMultisig(
    security_multisig,
):
    security_multisig.init_ebtc()
    security_multisig.ebtc.borrowerOperations_set_flash_loans_paused(
        True, use_timelock=False, salt=EmptyBytes32, use_high_sec=True
    )

    assert security_multisig.ebtc.borrower_operations.flashLoansPaused() == True


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
def test_activePool_sweep_token_happy(fee_recipient, wbtc, security_multisig):
    fee_recipient.init_ebtc()

    active_pool = fee_recipient.ebtc.active_pool.address
    recipient = fee_recipient.ebtc.active_pool.feeRecipientAddress()
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(
        fee_recipient.ebtc.active_pool.address,
        amount,
        {"from": security_multisig.account},
    )
    assert wbtc.balanceOf(active_pool) == amount

    balance_before = wbtc.balanceOf(recipient)
    fee_recipient.ebtc.activePool_sweep_token(wbtc.address, amount)
    assert wbtc.balanceOf(recipient) - balance_before == amount


def test_activePool_sweep_token_permissions(wbtc, security_multisig, random_safe):
    random_safe.init_ebtc()

    active_pool = random_safe.ebtc.active_pool.address
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(
        random_safe.ebtc.active_pool.address,
        amount,
        {"from": security_multisig.account},
    )
    assert wbtc.balanceOf(active_pool) == amount

    with pytest.raises(AssertionError, match="Error: Not authorized"):
        random_safe.ebtc.activePool_sweep_token(wbtc.address, amount)


# Test activePool_sweep_token
def test_collSurplusPool_sweep_token_happy(fee_recipient, wbtc, security_multisig):
    fee_recipient.init_ebtc()

    coll_surplus_pool = fee_recipient.ebtc.coll_surplus_pool.address
    recipient = fee_recipient.ebtc.coll_surplus_pool.feeRecipientAddress()
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(
        fee_recipient.ebtc.coll_surplus_pool.address,
        amount,
        {"from": security_multisig.account},
    )
    assert wbtc.balanceOf(coll_surplus_pool) == amount

    balance_before = wbtc.balanceOf(recipient)
    fee_recipient.ebtc.collSurplusPool_sweep_token(wbtc.address, amount)
    assert wbtc.balanceOf(recipient) - balance_before == amount


def test_collSurplusPool_sweep_token_permissions(wbtc, security_multisig, random_safe):
    random_safe.init_ebtc()

    coll_surplus_pool = random_safe.ebtc.coll_surplus_pool.address
    amount = 500 * 10 ** wbtc.decimals()

    wbtc.mint(
        random_safe.ebtc.coll_surplus_pool.address,
        amount,
        {"from": security_multisig.account},
    )
    assert wbtc.balanceOf(coll_surplus_pool) == amount

    with pytest.raises(AssertionError, match="Error: Not authorized"):
        random_safe.ebtc.collSurplusPool_sweep_token(wbtc.address, amount)


# Test batch_collateral_feed_source_and_redemption_fee_floor
def test_batch_collateral_feed_source_and_redemption_fee_floor_happy(techops):
    techops.init_ebtc()
    new_status = not techops.ebtc.price_feed.useDynamicFeed()
    techops.ebtc.batch_collateral_feed_source_and_redemption_fee_floor(
        new_status, 0.006e18
    )

    chain.sleep(techops.ebtc.lowsec_timelock.getMinDelay() + 1)
    chain.mine()

    techops.ebtc.batch_collateral_feed_source_and_redemption_fee_floor(
        new_status, 0.006e18
    )

    assert techops.ebtc.price_feed.useDynamicFeed() == new_status
    assert techops.ebtc.cdp_manager.redemptionFeeFloor() == 0.006e18
