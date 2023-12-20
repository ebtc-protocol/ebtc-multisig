from datetime import datetime, timezone
from enum import Enum

from brownie import web3, interface
from rich.console import Console
from helpers.addresses import registry
from helpers.constants import EmptyBytes32

C = Console()


class CdpStatus(Enum):
    # NOTE: there are more states, adding `2` to avoid magic numbers in code
    CLOSED = 2


class eBTC:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.collateral = safe.contract(
            registry.sepolia.ebtc.collateral, interface.ICollateralToken
        )
        self.authority = safe.contract(
            registry.sepolia.ebtc.authority, interface.IGovernor
        )
        self.liquidation_library = safe.contract(
            registry.sepolia.ebtc.liquidation_library, interface.ILiquidationLibrary
        )
        self.cdp_manager = safe.contract(
            registry.sepolia.ebtc.cdp_manager, interface.ICdpManager
        )
        self.borrower_operations = safe.contract(
            registry.sepolia.ebtc.borrower_operations, interface.IBorrowerOperations
        )
        self.ebtc_token = safe.contract(
            registry.sepolia.ebtc.ebtc_token, interface.IEBTCToken
        )
        self.price_feed = safe.contract(
            registry.sepolia.ebtc.price_feed, interface.IPriceFeedTestnet
        )
        self.active_pool = safe.contract(
            registry.sepolia.ebtc.active_pool, interface.IActivePool
        )
        self.coll_surplus_pool = safe.contract(
            registry.sepolia.ebtc.coll_surplus_pool, interface.ICollSurplusPool
        )
        self.sorted_cdps = safe.contract(
            registry.sepolia.ebtc.sorted_cdps, interface.ISortedCdps
        )
        self.hint_helpers = safe.contract(
            registry.sepolia.ebtc.hint_helpers, interface.IHintHelpers
        )
        self.fee_recipient = safe.contract(
            registry.sepolia.ebtc.fee_recipient, interface.IFeeRecipient
        )
        self.multi_cdp_getter = safe.contract(
            registry.sepolia.ebtc.multi_cdp_getter, interface.IMultiCdpGetter
        )
        self.highsec_timelock = safe.contract(
            registry.sepolia.ebtc.highsec_timelock,
            interface.ITimelockControllerEnumerable,
        )
        self.lowsec_timelock = safe.contract(
            registry.sepolia.ebtc.lowsec_timelock,
            interface.ITimelockControllerEnumerable,
        )

    ##################################################################
    ##
    ##                  Timelock Operations Helpers
    ##
    ##################################################################

    def schedule_timelock(
        self, timelock, target, value, data, predecessor, salt, delay
    ):
        ## Check that safe has PROPOSER_ROLE on timelock
        assert timelock.hasRole(timelock.PROPOSER_ROLE(), self.safe.account)

        ## Check that timelock has the appropiate permissions
        if target != timelock.address:
            assert self.authority.canCall(timelock.address, target, data[:10])

        ## Schedule tx
        timelock.schedule(target, value, data, predecessor, salt, delay)
        id = timelock.hashOperation(target, value, data, predecessor, salt)
        assert timelock.isOperationPending(id)
        exec_date = datetime.utcfromtimestamp(timelock.getTimestamp(id)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        C.print(
            f"[green]Operation {id} has been scheduled! Execution available at {exec_date}[/green]"
        )

    def execute_timelock(self, timelock, target, value, data, predecessor, salt):
        ## Check that safe has EXECUTOR_ROLE on timelock
        assert timelock.hasRole(timelock.EXECUTOR_ROLE(), self.safe.account)

        ## Check that timelock has the appropiate permissions
        if target != timelock.address:
            assert self.authority.canCall(timelock.address, target, data[:10])

        ## Check that valid tx and execute if so
        id = timelock.hashOperation(target, value, data, predecessor, salt)
        if timelock.isOperationReady(id):
            timelock.execute(target, value, data, predecessor, salt)
            assert timelock.isOperationDone(id)
            C.print(f"[green]Operation {id} has been executed![/green]")
        elif timelock.isOperationPending(id):
            exec_date = datetime.utcfromtimestamp(timelock.getTimestamp(id)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            C.print(
                f"[red]Operation {id} is still pending! Execution available at {exec_date}[/red]"
            )
            raise
        elif timelock.isOperationDone(id):
            C.print(f"[green]Operation {id} has already been executed![/green]")
            raise
        else:
            C.print(f"[red]Operation {id} hasn't been scheduled![/red]")
            raise

    def cancel_timelock(
        self,
        timelock,
        id,
    ):
        if timelock.isOperationPending(id):
            timelock.cancel(id)
            assert timelock.isOperation(id) == False
            C.print(f"[green]Operation {id} has been cancelled![/green]")
        else:
            C.print(f"[red]Operation {id} can't be cancelled![/red]")
            raise

    def cancel_lowsec_timelock(
        self,
        id,
        target=None,
        value=None,
        data=None,
        predecessor=None,
        salt=None,
    ):
        ## Check that safe has CANCELLER_ROLE on timelock
        assert self.lowsec_timelock.hasRole(
            self.lowsec_timelock.CANCELLER_ROLE(), self.safe.account
        )
        if id == "":
            id = self.lowsec_timelock.hashOperation(
                target, value, data, predecessor, salt
            )

        self.cancel_timelock(self.lowsec_timelock, id)

    def cancel_highsec_timelock(
        self,
        id,
        target=None,
        value=None,
        data=None,
        predecessor=None,
        salt=None,
    ):
        ## Check that safe has CANCELLER_ROLE on timelock
        assert self.highsec_timelock.hasRole(
            self.highsec_timelock.CANCELLER_ROLE(), self.safe.account
        )
        if id == "":
            id = self.highsec_timelock.hashOperation(
                target, value, data, predecessor, salt
            )

        self.cancel_timelock(self.highsec_timelock, id)

    ##################################################################
    ##
    ##                Timelock Management Functions
    ##
    ##################################################################

    def grant_timelock_role(self, role_key, account, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        if role_key == "PROPOSER_ROLE":
            role = timelock.PROPOSER_ROLE()
        elif role_key == "CANCELLER_ROLE":
            role = timelock.CANCELLER_ROLE()
        elif role_key == "EXECUTOR_ROLE":
            role = timelock.EXECUTOR_ROLE()
        elif role_key == "TIMELOCK_ADMIN_ROLE":
            role = timelock.TIMELOCK_ADMIN_ROLE()
        else:
            C.print(f"[red]Role not found![/red]")
            return

        ## Check if tx is already scheduled
        target = timelock
        data = target.grantRole.encode_input(role, account)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert timelock.hasRole(role, account)
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def revoke_timelock_role(self, role_key, account, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        if role_key == "PROPOSER_ROLE":
            role = timelock.PROPOSER_ROLE()
        elif role_key == "CANCELLER_ROLE":
            role = timelock.CANCELLER_ROLE()
        elif role_key == "EXECUTOR_ROLE":
            role = timelock.EXECUTOR_ROLE()
        elif role_key == "TIMELOCK_ADMIN_ROLE":
            role = timelock.TIMELOCK_ADMIN_ROLE()
        else:
            C.print(f"[red]Role not found![/red]")
            return

        ## Check that target has role
        assert timelock.hasRole(role, account)

        ## Check if tx is already scheduled
        target = timelock
        data = target.revokeRole.encode_input(role, account)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert timelock.hasRole(role, account) == False
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def update_timelock_delay(self, new_delay, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check that new delay is different
        assert timelock.getDelay() != new_delay

        ## Check if tx is already scheduled
        target = timelock
        data = target.updateDelay.encode_input(new_delay)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert timelock.getDelay() == new_delay
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    ##################################################################
    ##
    ##                CDP System Management Functions
    ##
    ##################################################################

    #### ===== CDP MANAGER ===== ####

    def cdpManager_set_staking_reward_split(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setStakingRewardSplit.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.cdp_manager.stakingRewardSplit() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def cdpManager_set_redemption_fee_floor(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setRedemptionFeeFloor.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.cdp_manager.redemptionFeeFloor() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def cdpManager_set_minute_decay_factor(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setMinuteDecayFactor.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.cdp_manager.minuteDecayFactor() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def cdpManager_set_beta(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setBeta.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.cdp_manager.beta() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def cdpManager_set_redemptions_paused(self, pause, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setRedemptionsPaused.encode_input(pause)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.cdp_manager.redemptionsPaused() == pause
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def cdpManager_set_grace_period(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setGracePeriod.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.cdp_manager.recoveryModeGracePeriodDuration() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    #### ===== PRICE FEED ===== ####

    def priceFeed_set_fallback_caller(self, address, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.price_feed
        data = target.setFallbackCaller.encode_input(address)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.price_feed.fallbackCaller() == address
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    #### ===== FLASHLOANS and FEES (ACTIVE POOL AND BORROWERS OPERATIONS) ===== ####

    def activePool_set_fee_bps(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.active_pool
        data = target.setFeeBps.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.active_pool.feeBps() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def borrowerOperations_set_fee_bps(self, value, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.borrower_operations
        data = target.setFeeBps.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.borrower_operations.feeBps() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    ## TODO: Function to change the fee on both the AP and the BO through a batched timelock tx

    def activePool_set_fee_recipient_address(self, address, use_high_sec=False):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.active_pool
        data = target.setFeeRecipientAddress.encode_input(address)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.active_pool.feeRecipientAddress() == address
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    def borrowerOperations_set_fee_recipient_addresss(
        self, address, use_high_sec=False
    ):
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.borrower_operations
        data = target.setFeeRecipientAddress.encode_input(address)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert self.borrower_operations.feeRecipientAddress() == address
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

    ## TODO: Function to change the fee recipient on both the AP and the BO through a batched timelock tx

    #### ===== ACTIVE POOL ===== ####
    def activePool_claim_fee_recipient_coll_shares(
        self, value, use_timelock=False, use_high_sec=False
    ):
        target = self.active_pool
        data = target.claimFeeRecipientCollShares.encode_input(value)
        if use_timelock:
            if use_high_sec:
                timelock = self.highsec_timelock
            else:
                timelock = self.lowsec_timelock

            ## Check if tx is already scheduled
            id = timelock.hashOperation(
                target.address, 0, data, EmptyBytes32, EmptyBytes32
            )

            if timelock.isOperation(id):
                coll = self.collateral
                fee_recipient = self.active_pool.feeRecipientAddress()
                shares_before = coll.sharesOf(fee_recipient)
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
                )
                assert coll.sharesOf(fee_recipient) - shares_before == value
            else:
                delay = timelock.getMinDelay()
                self.schedule_timelock(
                    timelock,
                    target.address,
                    0,
                    data,
                    EmptyBytes32,
                    EmptyBytes32,
                    delay + 1,
                )
        else:
            assert self.authority.canCall(self.safe.account, target, data[:10])

            # Claim shares
            coll = self.collateral
            fee_recipient = self.active_pool.feeRecipientAddress()
            shares_before = coll.sharesOf(fee_recipient)
            target.claimFeeRecipientCollShares(value)
            assert coll.sharesOf(fee_recipient) - shares_before == value

    #### ===== SWEEP STUCK TOKENS (ACTIVE POOL AND COLL SURPLUS POOL) ===== ####

    def activePool_sweep_token(
        self, token_address, value, use_timelock=False, use_high_sec=False
    ):
        target = self.active_pool
        data = target.sweeptoken.encode_input(token_address, value)
        if use_timelock:
            if use_high_sec:
                timelock = self.highsec_timelock
            else:
                timelock = self.lowsec_timelock

            ## Check if tx is already scheduled
            id = timelock.hashOperation(
                target.address, 0, data, EmptyBytes32, EmptyBytes32
            )

            if timelock.isOperation(id):
                token = self.safe.contract(token_address)
                fee_recipient = self.active_pool.feeRecipientAddress()
                balance_before = token.balanceOf(fee_recipient)
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
                )
                assert token.balanceOf(fee_recipient) - balance_before == value
            else:
                delay = timelock.getMinDelay()
                self.schedule_timelock(
                    timelock,
                    target.address,
                    0,
                    data,
                    EmptyBytes32,
                    EmptyBytes32,
                    delay + 1,
                )
        else:
            assert self.authority.canCall(self.safe.account, target, data[:10])
            # sweep token
            token = self.safe.contract(token_address)
            fee_recipient = self.active_pool.feeRecipientAddress()
            balance_before = token.balanceOf(fee_recipient)
            target.claimFeeRecipientCollShares(value)
            assert token.balanceOf(fee_recipient) - balance_before == value

    def collSurplusPool_sweep_token(
        self, token_address, value, use_timelock=False, use_high_sec=False
    ):
        target = self.coll_surplus_pool
        data = target.sweeptoken.encode_input(token_address, value)
        if use_timelock:
            if use_high_sec:
                timelock = self.highsec_timelock
            else:
                timelock = self.lowsec_timelock

            ## Check if tx is already scheduled
            id = timelock.hashOperation(
                target.address, 0, data, EmptyBytes32, EmptyBytes32
            )

            if timelock.isOperation(id):
                token = self.safe.contract(token_address)
                fee_recipient = (
                    self.active_pool.feeRecipientAddress()
                )  # Fee recipient will be modified to track the Active Pool's
                balance_before = token.balanceOf(fee_recipient)
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
                )
                assert token.balanceOf(fee_recipient) - balance_before == value
            else:
                delay = timelock.getMinDelay()
                self.schedule_timelock(
                    timelock,
                    target.address,
                    0,
                    data,
                    EmptyBytes32,
                    EmptyBytes32,
                    delay + 1,
                )
        else:
            assert self.authority.canCall(self.safe.account, target, data[:10])
            # sweep token
            token = self.safe.contract(token_address)
            fee_recipient = (
                self.active_pool.feeRecipientAddress()
            )  # Fee recipient will be modified to track the Active Pool's
            balance_before = token.balanceOf(fee_recipient)
            target.claimFeeRecipientCollShares(value)
            assert token.balanceOf(fee_recipient) - balance_before == value

    #### ===== GOVERNANCE CONFIGURATION (Only high sec) ===== ####

    def authority_set_role_name(self, role, name):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setRoleName.encode_input(role, name)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, EmptyBytes32
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
            )
            assert self.authority.getRoleName(role) == name
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
                delay + 1,
            )

    def authority_set_user_role(self, user, role, enabled):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setUserRole.encode_input(user, role, enabled)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, EmptyBytes32
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
            )
            assert self.authority.doesUserHaveRole(user, role) == enabled
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
                delay + 1,
            )

    def authority_set_role_capability(self, role, target_address, functionSig, enabled):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setRoleCapability.encode_input(
            role, target_address, functionSig, enabled
        )
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, EmptyBytes32
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
            )
            assert (
                self.authority.doesRoleHaveCapability(role, target_address, functionSig)
                == enabled
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
                delay + 1,
            )

    def authority_set_public_capability(self, target_address, functionSig, enabled):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setPublicCapability.encode_input(
            target_address, functionSig, enabled
        )
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, EmptyBytes32
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
            )
            assert (
                self.authority.isPublicCapability(target_address, functionSig)
                == enabled
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
                delay + 1,
            )

    def authority_burn_capability(self, target_address, functionSig):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.burnCapability.encode_input(target_address, functionSig)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, EmptyBytes32
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
            )
            assert (
                self.authority.capabilityFlag(target_address, functionSig) == 2
            )  # 2: Burned
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
                delay + 1,
            )

    def authority_set_authority(self, new_authority):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setAuthority.encode_input(new_authority)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, EmptyBytes32
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
            )
            assert self.authority.authority() == new_authority
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                EmptyBytes32,
                delay + 1,
            )

    #### ===== CDP OPS ===== ####

    def _assert_collateral_balance(self, coll_amount):
        total_coll_bal = self.collateral.balanceOf(self.safe.address)
        assert total_coll_bal >= self.collateral.getSharesByPooledEth(coll_amount)

    def _assert_debt_balance(self, debt_amount):
        total_debt_bal = self.ebtc_token.balanceOf(self.safe.address)
        assert total_debt_bal >= debt_amount
        return total_debt_bal

    def _assert_cdp_id_ownership(self, cdp_id):
        cdp_safe_owned = self.sorted_cdps.getCdpsOf(self.safe.address)
        assert cdp_id in cdp_safe_owned

    def _hint_helper_values(self, coll_amount, debt_amount):
        nicr = self.hint_helpers.computeNominalCR(coll_amount, debt_amount)

        total_cdps = self.sorted_cdps.getSize()
        hint, _, _ = self.hint_helpers.getApproxHint(
            nicr, total_cdps, 42
        )  # random seed 42

        upper_hint, lower_hint = self.sorted_cdps.findInsertPosition(nicr, hint, hint)

        return upper_hint, lower_hint

    def open_cdp(self, coll_amount, target_cr):
        """
        @dev Opens a new cdp position.
        @param coll_amount The total stETH collateral amount deposited for the specified Cdp.
        @param target_cr The desired target collateral ratio in the cdp position.
        """
        # verify: is it coll balance available
        self._assert_collateral_balance(coll_amount)

        debt_balance_before = self.ebtc_token.balanceOf(self.safe.address)

        # 1. collateral approval for BO
        self.collateral.approve(self.borrower_operations.address, coll_amount)

        # 2. decide borrow amount based on: collateral, feed price & CR
        feed_price = self.price_feed.fetchPrice.call()
        borrow_amount = (coll_amount * feed_price) / target_cr

        # 3. open cdp with args
        upper_hint, lower_hint = self._hint_helper_values(coll_amount, borrow_amount)
        cdp_id = self.borrower_operations.openCdp(
            borrow_amount, upper_hint, lower_hint, coll_amount
        ).return_value

        # 4. assertions:

        # 4.1. verify cdp id is owned by caller
        self._assert_cdp_id_ownership(cdp_id)

        # 4.2. debt balance of caller increased (difference)
        bal_diff = self.ebtc_token.balanceOf(self.safe.address) - debt_balance_before
        assert bal_diff == borrow_amount

        return cdp_id

    def close_cdp(self, cdp_id):
        """
        @dev Closes a target cdp id.
        @param cdp_id The CdpId on which this operation is operated.
        """
        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        # verify: sufficient ebtc is hold for closing
        (
            cdp_id_debt,
            cdp_id_coll,
            _,
            cdp_id_liquidator_reward_shares,
            _,
            _,
        ) = self.cdp_manager.Cdps(cdp_id)
        self._assert_debt_balance(cdp_id_debt)

        # cached prev collateral balance
        collateral_balance_before = self.collateral.balanceOf(self.safe.address)

        # 1. close target cdp id
        self.borrower_operations.closeCdp(cdp_id)

        # 2. assertions:

        # 2.1. verify status (2): `closedByOwner`
        # ref: https://github.com/ebtc-protocol/ebtc/blob/main/packages/contracts/contracts/Interfaces/ICdpManagerData.sol#L91
        cdp_id_status = self.cdp_manager.getCdpStatus(cdp_id)
        assert cdp_id_status == CdpStatus.CLOSED.value

        # 2.2. verify that enough collateral was returned + gas stipend
        assert (
            self.collateral.balanceOf(self.safe.address)
            == cdp_id_coll + cdp_id_liquidator_reward_shares + collateral_balance_before
        )

        # 2.3. verify expected values are 0 at readings from the cdp manager
        (
            cdp_id_debt,
            cdp_id_coll,
            cdp_id_stake,
            cdp_id_liq_reward_shares,
            _,
            _,
        ) = self.cdp_manager.Cdps(cdp_id)
        assert self.cdp_manager.cdpStEthFeePerUnitIndex(cdp_id) == 0
        assert cdp_id_debt == 0
        assert cdp_id_coll == 0
        assert cdp_id_stake == 0
        assert cdp_id_liq_reward_shares == 0

    def cdp_add_collateral(self, cdp_id, coll_amount):
        """
        @dev Adds the received stETH to the specified Cdp.
        @param cdp_id The CdpId on which this operation is operated.
        @param coll_amount The total stETH collateral amount deposited (added) for the specified Cdp.
        """
        # verify: is it coll balance available
        self._assert_collateral_balance(coll_amount)

        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        feed_price = self.price_feed.fetchPrice.call()
        prev_icr = self.cdp_manager.getCachedICR(cdp_id, feed_price)
        prev_tcr = self.cdp_manager.getCachedTCR(feed_price)
        prev_coll_balance = self.cdp_manager.getCdpCollShares(cdp_id)

        # 1. collateral approval for BO
        self.collateral.approve(self.borrower_operations.address, coll_amount)

        # 2. increase collateral in target cdp id
        self.borrower_operations.addColl(cdp_id, cdp_id, cdp_id, coll_amount)

        # 3. assertions:

        # 3.1. icr and tcr had increased
        assert self.cdp_manager.getCachedICR(cdp_id, feed_price) > prev_icr
        assert self.cdp_manager.getCachedTCR(feed_price) > prev_tcr

        # 3.2 collateral in cdp at storage has increased
        assert self.cdp_manager.getCdpCollShares(cdp_id) > prev_coll_balance

    def cdp_withdraw_collateral(self, cdp_id, coll_amount):
        """
        @dev Withdraws the amount of collateral from the specified Cdp.
        @param cdp_id The CdpId on which this operation is operated.
        @param coll_amount The total stETH collateral amount withdrawn (reduced) for the specified Cdp.
        """
        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        # verify: cdp holds enough collateral to be withdrawn
        (
            _,
            cdp_id_coll,
            _,
            _,
            _,
            _,
        ) = self.cdp_manager.Cdps(cdp_id)
        assert cdp_id_coll > coll_amount

        feed_price = self.price_feed.fetchPrice.call()
        prev_icr = self.cdp_manager.getCachedICR(cdp_id, feed_price)
        prev_tcr = self.cdp_manager.getCachedTCR(feed_price)
        prev_coll_balance = self.cdp_manager.getCdpCollShares(cdp_id)

        # 1. decreased collateral in target cdp id
        self.borrower_operations.withdrawColl(cdp_id, coll_amount, cdp_id, cdp_id)

        # 2. assertions:

        # 2.1. icr and tcr had decreased
        assert self.cdp_manager.getCachedICR(cdp_id, feed_price) < prev_icr
        assert self.cdp_manager.getCachedTCR(feed_price) < prev_tcr

        # 2.2 collateral in cdp at storage has decreased
        assert self.cdp_manager.getCdpCollShares(cdp_id) < prev_coll_balance

    def cdp_repay_debt(self, cdp_id, debt_repay_amount):
        """
        @dev Repays the received eBTC token to the specified Cdp, thus reducing its debt accounting.
        @param cdp_id The CdpId on which this operation is operated.
        @param debt_repay_amount The total eBTC debt amount repaid for the specified Cdp.
        """
        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        # verify: check debt caller balance
        prev_debt_balance = self._assert_debt_balance(debt_repay_amount)

        feed_price = self.price_feed.fetchPrice.call()
        prev_icr = self.cdp_manager.getCachedICR(cdp_id, feed_price)

        # 1. repay debt
        self.borrower_operations.repayDebt(cdp_id, debt_repay_amount, cdp_id, cdp_id)

        # 2. assertions

        # 2.1. debt balance decreased
        assert self.ebtc_token.balanceOf(self.safe.address) < prev_debt_balance

        # 2.2. icr should improved
        assert self.cdp_manager.getCachedICR(cdp_id, feed_price) > prev_icr

    def cdp_withdraw_debt(self, cdp_id, debt_withdrawable_amount):
        """
        @dev Withdraws the amount of eBTC token from the specified Cdp, thus increasing its debt accounting.
        @param cdp_id The CdpId on which this operation is operated.
        @param debt_withdrawable_amount The total debt collateral amount increased for the specified Cdp.
        """
        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        # verify: existing debt in cdp id is greater than amount to wd
        debt_before = self.cdp_manager.getCdpDebt(cdp_id)
        assert debt_before > debt_withdrawable_amount

        feed_price = self.price_feed.fetchPrice.call()
        prev_icr = self.cdp_manager.getCachedICR(cdp_id, feed_price)

        # 1. wd debt from cdp
        self.borrower_operations.withdrawDebt(
            cdp_id, debt_withdrawable_amount, cdp_id, cdp_id
        )

        # 2. assertions

        # 2.1. debt should increased
        assert self.cdp_manager.getCdpDebt(cdp_id) > debt_before

        # 2.2. icr decreased
        assert self.cdp_manager.getCachedICR(cdp_id, feed_price) < prev_icr
