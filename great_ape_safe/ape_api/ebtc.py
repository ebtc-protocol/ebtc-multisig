from datetime import datetime

from brownie import interface
from rich.console import Console
from helpers.addresses import registry
from helpers.constants import EmptyBytes32

C = Console()


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
        """
        @dev Schedules a timelock transaction.
        @param timelock The timelock contract to execute the transaction on.
        @param target The target of the timelock transaction.
        @param value The ETH value of the timelock transaction.
        @param data The data of the timelock transaction (encoding of function signature and parameters).
        @param predecessor The predecessing transacction of the timelock transaction. Matters when cancelling batched transactions.
        @param salt The salt of the timelock. Matters when cancelling a batched, repeated, transaction.
        @param delay The time delay at which the transaction will be executable. Must be higher than the min delay.
        """
        ## Check that safe has PROPOSER_ROLE on timelock
        assert timelock.hasRole(
            timelock.PROPOSER_ROLE(), self.safe.account
        ), "Error: No role"

        ## Check that timelock has the appropiate permissions
        if target != timelock.address:
            assert self.authority.canCall(
                timelock.address, target, data[:10]
            ), "Error: Not authorized"

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
        """
        @dev Executes a timelock transaction.
        @param timelock The timelock contract to execute the transaction on.
        @param target The target of the timelock transaction.
        @param value The ETH value of the timelock transaction.
        @param data The data of the timelock transaction (encoding of function signature and parameters).
        @param predecessor The predecessing transacction of the timelock transaction. Matters when cancelling batched transactions.
        @param salt The salt of the timelock. Matters when cancelling a batched, repeated, transaction.
        """
        ## Check that safe has EXECUTOR_ROLE on timelock
        assert timelock.hasRole(
            timelock.EXECUTOR_ROLE(), self.safe.account
        ), "Error: No role"

        ## Check that timelock has the appropiate permissions
        if target != timelock.address:
            assert self.authority.canCall(
                timelock.address, target, data[:10]
            ), "Error: Not authorized"

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
            raise Exception("Error: operation does not exist")

    def cancel_lowsec_timelock(
        self,
        id,
        target=None,
        value=None,
        data=None,
        predecessor=None,
        salt=None,
    ):
        """
        @dev Cancels a low security timelock transaction.
        @param id The ID of the timelock transaction to cancel. Set to 0x0 if prefer to generate id from parameters.
        @param target The target of the timelock transaction.
        @param value The ETH value of the timelock transaction.
        @param data The data of the timelock transaction (encoding of function signature and parameters).
        @param predecessor The predecessing transacction of the timelock transaction. Matters when cancelling batched transactions.
        @param salt The salt of the timelock. Matters when cancelling a batched, repeated, transaction.
        """
        ## Check that safe has CANCELLER_ROLE on timelock
        assert self.lowsec_timelock.hasRole(
            self.lowsec_timelock.CANCELLER_ROLE(), self.safe.account
        ), "Error: No role"
        if id == "0x0":
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
        """
        @dev Cancels a high security timelock transaction.
        @param id The ID of the timelock transaction to cancel. Set to 0x0 if prefer to generate id from parameters.
        @param target The target of the timelock transaction.
        @param value The ETH value of the timelock transaction.
        @param data The data of the timelock transaction (encoding of function signature and parameters).
        @param predecessor The predecessing transacction of the timelock transaction. Matters when cancelling batched transactions.
        @param salt The salt of the timelock. Matters when cancelling a batched, repeated, transaction.
        """
        ## Check that safe has CANCELLER_ROLE on timelock
        assert self.highsec_timelock.hasRole(
            self.highsec_timelock.CANCELLER_ROLE(), self.safe.account
        ), "Error: No role"
        if id == "0x0":
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
        """
        @dev Grants a role on the timelock to an account.
        @param role_key The key of the role to grant. Can be one of "PROPOSER_ROLE", "CANCELLER_ROLE", "EXECUTOR_ROLE", or "TIMELOCK_ADMIN_ROLE".
        @param account The account to grant the role to.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Revokes a role on the timelock from an account.
        @param role_key The key of the role to revoke. Can be one of "PROPOSER_ROLE", "CANCELLER_ROLE", "EXECUTOR_ROLE", or "TIMELOCK_ADMIN_ROLE".
        @param account The account to revoke the role from.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        assert timelock.hasRole(role, account), "Error: No role"

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
        """
        @dev Updates the delay on the timelock.
        @param new_delay The new delay to set on the timelock.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check that new delay is different
        assert timelock.getMinDelay() != new_delay, "Error: Delay already set"

        ## Check if tx is already scheduled
        target = timelock
        data = target.updateDelay.encode_input(new_delay)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if timelock.isOperation(id):
            self.execute_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
            assert timelock.getMinDelay() == new_delay
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
        """
        @dev Sets the staking reward split in the CDP Manager.
        @param value The new staking reward split to set.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """    
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
        """
        @dev Sets the redemption fee floor in the CDP Manager.
        @param value The new redemption fee floor to set.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the minute decay factor for the redemption fee in the CDP Manager.
        @param value The new redemption fee minute decay factor.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the beta for the redemption fee in the CDP Manager.
        @param value The new redemption fee beta.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the redemptions paused state in the CDP Manager.
        @param paused The new redemptions paused state to set (True or False).
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the grace period in the CDP Manager.
        @param value The new grace period to set.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the fallbak Oracle caller on the PriceFeed.
        @param address The address of the new fallback caller
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the fee bps on the Active Pool.
        @param value The new fee bps.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the fee bps on the CDP Manager.
        @param value The new fee bps.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Sets the new fee recipient address on the Active Pool.
        @param address The new fee recipient address.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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

    def borrowerOperations_set_fee_recipient_address(self, address, use_high_sec=False):
        """
        @dev Sets the new fee recipient address on the Borrowers Operations.
        @param address The new fee recipient address.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
        """
        @dev Claims the accumulated collateral shares for the Fee Recipient on the Active Pool.
        @param value The amount of collateral shares to claim.
        @param use_timelock If true, use the timelock. Otherwise, use direct tx.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
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
            assert self.authority.canCall(
                self.safe.account, target, data[:10]
            ), "Error: Not authorized"

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
        """
        @dev Sweeps an amount of an specific unprotected, stuck, token from the Active Pool into the fee recipient.
        @param token_address The address of the token to sweep.
        @param value The amount of tokens to sweep.
        @param use_timelock If true, use the timelock. Otherwise, use direct tx.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
        target = self.active_pool
        data = target.sweepToken.encode_input(token_address, value)
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
            assert self.authority.canCall(
                self.safe.account, target, data[:10]
            ), "Error: Not authorized"
            # sweep token
            token = self.safe.contract(token_address)
            fee_recipient = self.active_pool.feeRecipientAddress()
            balance_before = token.balanceOf(fee_recipient)
            target.sweepToken(token_address, value)
            assert token.balanceOf(fee_recipient) - balance_before == value

    def collSurplusPool_sweep_token(
        self, token_address, value, use_timelock=False, use_high_sec=False
    ):
        """
        @dev Sweeps an amount of an specific unprotected, stuck, token from the Collateral Surplus pool into the fee recipient.
        @param token_address The address of the token to sweep.
        @param value The amount of tokens to sweep.
        @param use_timelock If true, use the timelock. Otherwise, use direct tx.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
        target = self.coll_surplus_pool
        data = target.sweepToken.encode_input(token_address, value)
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
                    self.coll_surplus_pool.feeRecipientAddress()
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
            assert self.authority.canCall(
                self.safe.account, target, data[:10]
            ), "Error: Not authorized"
            # sweep token
            token = self.safe.contract(token_address)
            fee_recipient = (
                self.coll_surplus_pool.feeRecipientAddress()
            )  # Fee recipient will be modified to track the Active Pool's
            balance_before = token.balanceOf(fee_recipient)
            target.sweepToken(token_address, value)
            assert token.balanceOf(fee_recipient) - balance_before == value

    #### ===== GOVERNANCE CONFIGURATION (Only high sec) ===== ####

    def authority_set_role_name(self, role, name):
        """
        @dev Sets the name of a role in the Authority.
        @param role The role to set the name of.
        @param name The new name of the role.
        """
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
        """
        @dev Grants a role to a user in the Authority.
        @param user The user to grant the role to.
        @param role The role to set the name of.
        @param enabled Whether to grant or revoke the role.
        """
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
        """
        @dev Assigns the capability to call a contrat's function to a role in the Authority.
        @param role The role to set the name of.
        @param target_address The address of the contract containing the function.
        @param functionSig The signature of the function to grant the capability to.
        @param enabled Whether to grant or revoke the role.
        """
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
        """
        @dev Flags a contract's function as callable by anyone (public) in the Authority.
        @param target_address The address of the contract containing the function.
        @param functionSig The signature of the function to grant the capability to.
        @param enabled Whether to grant or revoke public access to the function.
        """
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
        """
        @dev Burns the ability to call a contract's function from anyone irrespective of their roles in the Authority.
        @param target_address The address of the contract containing the function.
        @param functionSig The signature of the function to grant the capability to.
        """
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
        """
        @dev Changes the Governance underying authority contract.
        @param new_authority The address of the new Authority contract.
        """
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
