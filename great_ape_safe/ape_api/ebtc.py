from datetime import datetime, timezone

from brownie import web3
from rich.console import Console
from helpers.addresses import r
from helpers.constants import EmptyBytes32

C = Console()


class eBTC:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.collateral = safe.contract(r.ebtc.collateral)
        self.authority = safe.contract(r.ebtc.authority)
        self.liquidation_library = safe.contract(r.ebtc.liquidation_library)
        self.cdp_manager = safe.contract(r.ebtc.cdp_manager)
        self.borrower_operations = safe.contract(r.ebtc.borrower_operations)
        self.ebtc_token = safe.contract(r.ebtc.ebtc_token)
        self.price_feed = safe.contract(r.ebtc.price_feed)
        self.active_pool = safe.contract(r.ebtc.active_pool)
        self.coll_surplus_pool = safe.contract(r.ebtc.coll_surplus_pool)
        self.sorted_cdps = safe.contract(r.ebtc.sorted_cdps)
        self.hint_helpers = safe.contract(r.ebtc.hint_helpers)
        self.fee_recipient = safe.contract(r.ebtc.fee_recipient)
        self.multi_cdp_getter = safe.contract(r.ebtc.multi_cdp_getter)
        self.ebtc_deployer = safe.contract(r.ebtc.ebtc_deployer)
        self.highsec_timelock = safe.contract(r.ebtc.highsec_timelock)
        self.lowsec_timelock = safe.contract(r.ebtc.lowsec_timelock)

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
        elif timelock.isOperationDone(id):
            C.print(f"[green]Operation {id} has already been executed![/green]")
        else:
            C.print(f"[red]Operation {id} hasn't been scheduled![/red]")

    def cancel_timelock(
        self,
        timelock,
        id,
        target=None,
        value=None,
        data=None,
        predecessor=None,
        salt=None,
    ):
        ## Check that safe has CANCELLER_ROLE on timelock
        assert timelock.hasRole(timelock.CANCELLER_ROLE(), self.safe.account)
        ## If ID is given, check that it is valid and cancel if so
        if id == "":
            id = timelock.hashOperation(target, value, data, predecessor, salt)

        if timelock.isOperationPending(id):
            timelock.cancel(id)
            assert timelock.isOperation(id) == False
            C.print(f"[green]Operation {id} has been cancelled![/green]")
        else:
            C.print(f"[red]Operation {id} can't be cancelled![/red]")

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

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
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
                )
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

            self.safe.post_safe_tx()

    #### ===== SWEEP STUCK TOKENS (ACTIVE POOL AND COLL SURPLUS POOL) ===== ####

    def activePool_sweep_token(
        self, address, value, use_timelock=False, use_high_sec=False
    ):
        target = self.active_pool
        data = target.sweeptoken.encode_input(address, value)
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
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
                )
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
            token = self.safe.contract(address)
            fee_recipient = self.active_pool.feeRecipientAddress()
            balance_before = token.balanceOf(fee_recipient)
            target.claimFeeRecipientCollShares(value)
            assert token.balanceOf(fee_recipient) - balance_before == value

            self.safe.post_safe_tx()

    def collSurplusPool_sweep_token(
        self, address, value, use_timelock=False, use_high_sec=False
    ):
        target = self.coll_surplus_pool
        data = target.sweeptoken.encode_input(address, value)
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
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
                )
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
            token = self.safe.contract(address)
            fee_recipient = (
                self.active_pool.feeRecipientAddress()
            )  # Fee recipient will be modified to track the Active Pool's
            balance_before = token.balanceOf(fee_recipient)
            target.claimFeeRecipientCollShares(value)
            assert token.balanceOf(fee_recipient) - balance_before == value

            self.safe.post_safe_tx()


    #### ===== GOVERNANCE CONFIGURATION (Only high sec) ===== ####

    def authority_set_role_name(self, role, name):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setRoleName.encode_input(role, name)
        id = self.highsec_timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

    def authority_set_user_role(self, user, role, enabled):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setUserRole.encode_input(user, role, enabled)
        id = self.highsec_timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

    def authority_set_role_capability(self, role, target_address, functionSig, enabled):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setRoleCapability.encode_input(role, target_address, functionSig, enabled)
        id = self.highsec_timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

    def authority_set_public_capability(self, target_address, functionSig, enabled):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setPublicCapability.encode_input(target_address, functionSig, enabled)
        id = self.highsec_timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

    def authority_burn_capability(self, target_address, functionSig):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.burnCapability.encode_input(target_address, functionSig)
        id = self.highsec_timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()

    def authority_set_authority(self, new_authority):
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setAuthority.encode_input(new_authority)
        id = self.highsec_timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
            )
        else:
            delay = self.highsec_timelock.getMinDelay()
            self.schedule_timelock(
                self.highsec_timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
            )

        self.safe.post_safe_tx()