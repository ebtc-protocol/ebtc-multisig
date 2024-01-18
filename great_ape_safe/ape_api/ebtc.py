from datetime import datetime
from enum import Enum

from brownie import interface, web3
from rich.console import Console
from helpers.addresses import registry
from helpers.constants import (
    EmptyBytes32,
    AddressZero,
    DECIMAL_PRECISION,
    MAX_REWARD_SPLIT,
    MIN_REDEMPTION_FEE_FLOOR,
    MIN_MINUTE_DECAY_FACTOR,
    MAX_MINUTE_DECAY_FACTOR,
    MINIMUM_GRACE_PERIOD,
    MAX_FEE_BPS,
)


C = Console()


class CdpStatus(Enum):
    # NOTE: there are more states, adding `2` to avoid magic numbers in code
    CLOSED = 2


class eBTC:
    def __init__(self, safe):
        self.safe = safe

        # constants
        self.SAFE_ICR_THRESHOLD = 120e16
        self.CCR = 125e16

        self.LIQUIDATOR_REWARD = 2e17

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
        self.fee_recipient = self.active_pool.feeRecipientAddress()

        ##################################################################
        ##
        ##             Governance Configuration and Settings
        ##
        ##################################################################

        # Contains a mapping of governancce roles to the role numbers used in the authority contract
        class governanceRoles(Enum):
            ADMIN = 0  # Admin
            EBTC_MINTER = 1  # eBTCToken: mint
            EBTC_BURNER = 2  # eBTCToken: burn
            CDP_MANAGER_ALL = 3  # CDPManager: all
            FALLBACK_ADMIN = 4  # PriceFeed: setFallbackCaller
            FEE_ADMIN = 5  # BorrowerOperations+ActivePool: setFeeBps, setFlashLoansPaused, setFeeRecipientAddress
            FEE_RECIPIENT_OPS = 6  # ActivePool: sweep tokens & claim fee recipient coll

        self.governance_roles = governanceRoles

        # Dictionary of all of the governable function signatures used in the authority contract
        self.governance_signatures = {
            "SET_STAKING_REWARD_SPLIT_SIG": web3.keccak(
                text="setStakingRewardSplit(uint256)"
            ).hex()[0:10],
            "SET_REDEMPTION_FEE_FLOOR_SIG": web3.keccak(
                text="setRedemptionFeeFloor(uint256)"
            ).hex()[0:10],
            "SET_MINUTE_DECAY_FACTOR_SIG": web3.keccak(
                text="setMinuteDecayFactor(uint256)"
            ).hex()[0:10],
            "SET_BETA_SIG": web3.keccak(text="setBeta(uint256)").hex()[0:10],
            "SET_REDEMPTIONS_PAUSED_SIG": web3.keccak(
                text="setRedemptionsPaused(bool)"
            ).hex()[0:10],
            "SET_GRACE_PERIOD_SIG": web3.keccak(text="setGracePeriod(uint128)").hex()[
                0:10
            ],
            "MINT_SIG": web3.keccak(text="mint(address,uint256)").hex()[0:10],
            "BURN_SIG": web3.keccak(text="burn(address,uint256)").hex()[0:10],
            "BURN2_SIG": web3.keccak(text="burn(uint256)").hex()[0:10],
            "SET_FALLBACK_CALLER_SIG": web3.keccak(
                text="setFallbackCaller(address)"
            ).hex()[0:10],
            "SET_FEE_BPS_SIG": web3.keccak(text="setFeeBps(uint256)").hex()[0:10],
            "SET_FLASH_LOANS_PAUSED_SIG": web3.keccak(
                text="setFlashLoansPaused(bool)"
            ).hex()[0:10],
            "SWEEP_TOKEN_SIG": web3.keccak(text="sweepToken(address,uint256)").hex()[
                0:10
            ],
            "CLAIM_FEE_RECIPIENT_COLL_SIG": web3.keccak(
                text="claimFeeRecipientCollShares(uint256)"
            ).hex()[0:10],
            "SET_FEE_RECIPIENT_ADDRESS_SIG": web3.keccak(
                text="setFeeRecipientAddress(address)"
            ).hex()[0:10],
            "SET_ROLE_NAME_SIG": web3.keccak(text="setRoleName(uint8,string)").hex()[
                0:10
            ],
            "SET_USER_ROLE_SIG": web3.keccak(
                text="setUserRole(address,uint8,bool)"
            ).hex()[0:10],
            "SET_ROLE_CAPABILITY_SIG": web3.keccak(
                text="setRoleCapability(uint8,address,bytes4,bool)"
            ).hex()[0:10],
            "SET_PUBLIC_CAPABILITY_SIG": web3.keccak(
                text="setPublicCapability(address,bytes4,bool)"
            ).hex()[0:10],
            "BURN_CAPABILITY_SIG": web3.keccak(
                text="burnCapability(address,bytes4)"
            ).hex()[0:10],
            "TRANSFER_OWNERSHIP_SIG": web3.keccak(
                text="transferOwnership(address)"
            ).hex()[0:10],
            "SET_AUTHORITY_SIG": web3.keccak(text="setAuthority(address)").hex()[0:10],
        }

        # Mapping of the governance roles to the list of permissions (signatures within contracts) that they have
        self.governance_configuration = {
            governanceRoles.ADMIN.value: [
                {
                    "target": self.authority,
                    "signature": self.governance_signatures["SET_ROLE_NAME_SIG"],
                },
                {
                    "target": self.authority,
                    "signature": self.governance_signatures["SET_USER_ROLE_SIG"],
                },
                {
                    "target": self.authority,
                    "signature": self.governance_signatures["SET_ROLE_CAPABILITY_SIG"],
                },
                {
                    "target": self.authority,
                    "signature": self.governance_signatures[
                        "SET_PUBLIC_CAPABILITY_SIG"
                    ],
                },
                {
                    "target": self.authority,
                    "signature": self.governance_signatures["BURN_CAPABILITY_SIG"],
                },
                {
                    "target": self.authority,
                    "signature": self.governance_signatures["TRANSFER_OWNERSHIP_SIG"],
                },
                {
                    "target": self.authority,
                    "signature": self.governance_signatures["SET_AUTHORITY_SIG"],
                },
            ],
            governanceRoles.EBTC_MINTER.value: [
                {
                    "target": self.ebtc_token,
                    "signature": self.governance_signatures["MINT_SIG"],
                },
            ],
            governanceRoles.EBTC_BURNER.value: [
                {
                    "target": self.ebtc_token,
                    "signature": self.governance_signatures["BURN_SIG"],
                },
                {
                    "target": self.ebtc_token,
                    "signature": self.governance_signatures["BURN2_SIG"],
                },
            ],
            governanceRoles.CDP_MANAGER_ALL.value: [
                {
                    "target": self.cdp_manager,
                    "signature": self.governance_signatures[
                        "SET_STAKING_REWARD_SPLIT_SIG"
                    ],
                },
                {
                    "target": self.cdp_manager,
                    "signature": self.governance_signatures[
                        "SET_REDEMPTION_FEE_FLOOR_SIG"
                    ],
                },
                {
                    "target": self.cdp_manager,
                    "signature": self.governance_signatures[
                        "SET_MINUTE_DECAY_FACTOR_SIG"
                    ],
                },
                {
                    "target": self.cdp_manager,
                    "signature": self.governance_signatures["SET_BETA_SIG"],
                },
                {
                    "target": self.cdp_manager,
                    "signature": self.governance_signatures[
                        "SET_REDEMPTIONS_PAUSED_SIG"
                    ],
                },
                {
                    "target": self.cdp_manager,
                    "signature": self.governance_signatures["SET_GRACE_PERIOD_SIG"],
                },
            ],
            governanceRoles.FALLBACK_ADMIN.value: [
                {
                    "target": self.price_feed,
                    "signature": self.governance_signatures["SET_FALLBACK_CALLER_SIG"],
                },
            ],
            governanceRoles.FEE_ADMIN.value: [
                {
                    "target": self.borrower_operations,
                    "signature": self.governance_signatures["SET_FEE_BPS_SIG"],
                },
                {
                    "target": self.borrower_operations,
                    "signature": self.governance_signatures[
                        "SET_FLASH_LOANS_PAUSED_SIG"
                    ],
                },
                {
                    "target": self.borrower_operations,
                    "signature": self.governance_signatures[
                        "SET_FEE_RECIPIENT_ADDRESS_SIG"
                    ],
                },
                {
                    "target": self.active_pool,
                    "signature": self.governance_signatures["SET_FEE_BPS_SIG"],
                },
                {
                    "target": self.active_pool,
                    "signature": self.governance_signatures[
                        "SET_FLASH_LOANS_PAUSED_SIG"
                    ],
                },
                {
                    "target": self.active_pool,
                    "signature": self.governance_signatures[
                        "SET_FEE_RECIPIENT_ADDRESS_SIG"
                    ],
                },
            ],
            governanceRoles.FEE_RECIPIENT_OPS.value: [
                {
                    "target": self.active_pool,
                    "signature": self.governance_signatures["SWEEP_TOKEN_SIG"],
                },
                {
                    "target": self.active_pool,
                    "signature": self.governance_signatures[
                        "CLAIM_FEE_RECIPIENT_COLL_SIG"
                    ],
                },
                {
                    "target": self.coll_surplus_pool,
                    "signature": self.governance_signatures["SWEEP_TOKEN_SIG"],
                },
            ],
        }

        # Mapping of the permissioned actors to their assigned roles
        self.users_roles_configuration = {
            self.highsec_timelock.address: [
                governanceRoles.ADMIN.value,
                governanceRoles.CDP_MANAGER_ALL.value,
                governanceRoles.FALLBACK_ADMIN.value,
                governanceRoles.FEE_ADMIN.value,
                governanceRoles.FEE_RECIPIENT_OPS.value,
            ],
            self.lowsec_timelock.address: [
                governanceRoles.CDP_MANAGER_ALL.value,
                governanceRoles.FALLBACK_ADMIN.value,
                governanceRoles.FEE_ADMIN.value,
                governanceRoles.FEE_RECIPIENT_OPS.value,
            ],
            self.fee_recipient: [
                governanceRoles.FEE_RECIPIENT_OPS.value,
            ],
        }

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
        @param predecessor The predecessing transacction of the timelock transaction. Matters when there is a dependency between operations.
        @param salt Value used to generate a unique ID for a transaction with identical parameters than an existing.
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
        tx = timelock.schedule(target, value, data, predecessor, salt, delay)
        id = timelock.hashOperation(target, value, data, predecessor, salt)
        assert timelock.isOperationPending(id)
        exec_date = datetime.utcfromtimestamp(timelock.getTimestamp(id)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        C.print(
            f"[green]Operation {id} has been scheduled! Execution available at {exec_date}[/green]"
        )
        return tx

    def execute_timelock(self, timelock, target, value, data, predecessor, salt):
        """
        @dev Executes a timelock transaction.
        @param timelock The timelock contract to execute the transaction on.
        @param target The target of the timelock transaction.
        @param value The ETH value of the timelock transaction.
        @param data The data of the timelock transaction (encoding of function signature and parameters).
        @param predecessor The predecessing transacction of the timelock transaction. Matters when there is a dependency between operations.
        @param salt Value used to generate a unique ID for a transaction with identical parameters than an existing.
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
            tx = timelock.execute(target, value, data, predecessor, salt)
            assert timelock.isOperationDone(id)
            C.print(f"[green]Operation {id} has been executed![/green]")
            return tx
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
            tx = timelock.cancel(id)
            assert timelock.isOperation(id) == False
            C.print(f"[green]Operation {id} has been cancelled![/green]")
            return tx
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
        @param predecessor The predecessing transacction of the timelock transaction. Matters when there is a dependency between operations.
        @param salt Value used to generate a unique ID for a transaction with identical parameters than an existing.
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
        @param predecessor The predecessing transacction of the timelock transaction. Matters when there is a dependency between operations.
        @param salt Value used to generate a unique ID for a transaction with identical parameters than an existing.
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

    def grant_timelock_role(
        self, role_key, account, salt=EmptyBytes32, use_high_sec=False
    ):
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
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert timelock.hasRole(role, account)
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def revoke_timelock_role(
        self, role_key, account, salt=EmptyBytes32, use_high_sec=False
    ):
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
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert timelock.hasRole(role, account) == False
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def update_timelock_delay(self, new_delay, salt=EmptyBytes32, use_high_sec=False):
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
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert timelock.getMinDelay() == new_delay
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    ##################################################################
    ##
    ##                CDP System Management Functions
    ##
    ##################################################################

    #### ===== CDP MANAGER ===== ####

    def cdpManager_set_staking_reward_split(
        self, value, salt=EmptyBytes32, use_high_sec=False
    ):
        """
        @dev Sets the staking reward split in the CDP Manager.
        @param value The new staking reward split to set.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """
        ## Ref: uint256 public constant MAX_REWARD_SPLIT = 10_000;
        assert value <= MAX_REWARD_SPLIT, "Error: Value too high"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setStakingRewardSplit.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.cdp_manager.stakingRewardSplit() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def cdpManager_set_redemption_fee_floor(
        self, value, salt=EmptyBytes32, use_high_sec=False
    ):
        """
        @dev Sets the redemption fee floor in the CDP Manager.
        @param value The new redemption fee floor to set.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert value >= MIN_REDEMPTION_FEE_FLOOR, "Error: Value too low"
        assert value <= DECIMAL_PRECISION, "Error: Value too high"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setRedemptionFeeFloor.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.cdp_manager.redemptionFeeFloor() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def cdpManager_set_minute_decay_factor(
        self, value, salt=EmptyBytes32, use_high_sec=False
    ):
        """
        @dev Sets the minute decay factor for the redemption fee in the CDP Manager.
        @param value The new redemption fee minute decay factor.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert value >= MIN_MINUTE_DECAY_FACTOR, "Error: Value too low"
        assert value <= MAX_MINUTE_DECAY_FACTOR, "Error: Value too high"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setMinuteDecayFactor.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.cdp_manager.minuteDecayFactor() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def cdpManager_set_beta(self, value, salt=EmptyBytes32, use_high_sec=False):
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
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.cdp_manager.beta() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def cdpManager_set_redemptions_paused(
        self, pause, salt=EmptyBytes32, use_high_sec=False
    ):
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
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.cdp_manager.redemptionsPaused() == pause
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def cdpManager_set_grace_period(self, value, salt=EmptyBytes32, use_high_sec=False):
        """
        @dev Sets the grace period in the CDP Manager.
        @param value The new grace period to set.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert value >= MINIMUM_GRACE_PERIOD, "Error: Value too low"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.cdp_manager
        data = target.setGracePeriod.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.cdp_manager.recoveryModeGracePeriodDuration() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    #### ===== PRICE FEED ===== ####

    def priceFeed_set_fallback_caller(
        self, address, salt=EmptyBytes32, use_high_sec=False
    ):
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
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.price_feed.fallbackCaller() == address
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    #### ===== FLASHLOANS and FEES (ACTIVE POOL AND BORROWERS OPERATIONS) ===== ####

    def activePool_set_fee_bps(self, value, salt=EmptyBytes32, use_high_sec=False):
        """
        @dev Sets the fee bps on the Active Pool.
        @param value The new fee bps.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert value <= MAX_FEE_BPS, "Error: Value too high"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.active_pool
        data = target.setFeeBps.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.active_pool.feeBps() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def borrowerOperations_set_fee_bps(
        self, value, salt=EmptyBytes32, use_high_sec=False
    ):
        """
        @dev Sets the fee bps on the CDP Manager.
        @param value The new fee bps.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert value <= MAX_FEE_BPS, "Error: Value too high"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.borrower_operations
        data = target.setFeeBps.encode_input(value)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.borrower_operations.feeBps() == value
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    ## TODO: Function to change the fee on both the AP and the BO through a batched timelock tx

    def activePool_set_fee_recipient_address(
        self, address, salt=EmptyBytes32, use_high_sec=False
    ):
        """
        @dev Sets the new fee recipient address on the Active Pool.
        @param address The new fee recipient address.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert address != AddressZero, "Error: Address cannot be zero"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.active_pool
        data = target.setFeeRecipientAddress.encode_input(address)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.active_pool.feeRecipientAddress() == address
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    def borrowerOperations_set_fee_recipient_address(
        self, address, salt=EmptyBytes32, use_high_sec=False
    ):
        """
        @dev Sets the new fee recipient address on the Borrowers Operations.
        @param address The new fee recipient address.
        @param use_high_sec If true, use the high security timelock. Otherwise, use the low security timelock.
        """

        assert address != AddressZero, "Error: Address cannot be zero"

        if use_high_sec:
            timelock = self.highsec_timelock
        else:
            timelock = self.lowsec_timelock

        ## Check if tx is already scheduled
        target = self.borrower_operations
        data = target.setFeeRecipientAddress.encode_input(address)
        id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

        if timelock.isOperation(id):
            self.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
            assert self.borrower_operations.feeRecipientAddress() == address
        else:
            delay = timelock.getMinDelay()
            self.schedule_timelock(
                timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
            )

    ## TODO: Function to change the fee recipient on both the AP and the BO through a batched timelock tx

    #### ===== ACTIVE POOL ===== ####
    def activePool_claim_fee_recipient_coll_shares(
        self, value, use_timelock=False, salt=EmptyBytes32, use_high_sec=False
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
            id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

            if timelock.isOperation(id):
                coll = self.collateral
                fee_recipient = self.active_pool.feeRecipientAddress()
                shares_before = coll.sharesOf(fee_recipient)
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, salt
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
                    salt,
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
        self,
        token_address,
        value,
        use_timelock=False,
        salt=EmptyBytes32,
        use_high_sec=False,
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
            id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

            if timelock.isOperation(id):
                token = self.safe.contract(token_address)
                fee_recipient = self.active_pool.feeRecipientAddress()
                balance_before = token.balanceOf(fee_recipient)
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, salt
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
                    salt,
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
        self,
        token_address,
        value,
        use_timelock=False,
        salt=EmptyBytes32,
        use_high_sec=False,
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
            id = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)

            if timelock.isOperation(id):
                token = self.safe.contract(token_address)
                fee_recipient = (
                    self.coll_surplus_pool.feeRecipientAddress()
                )  # Fee recipient will be modified to track the Active Pool's
                balance_before = token.balanceOf(fee_recipient)
                self.execute_timelock(
                    timelock, target.address, 0, data, EmptyBytes32, salt
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
                    salt,
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

    def authority_set_role_name(self, role, name, salt=EmptyBytes32):
        """
        @dev Sets the name of a role in the Authority.
        @param role The role to set the name of.
        @param name The new name of the role.
        """
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setRoleName.encode_input(role, name)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, salt
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                salt,
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

    def authority_set_user_role(self, user, role, enabled, salt=EmptyBytes32):
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
            target.address, 0, data, EmptyBytes32, salt
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                salt,
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
                salt,
                delay + 1,
            )

    def authority_set_role_capability(
        self, role, target_address, functionSig, enabled, salt=EmptyBytes32
    ):
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
            target.address, 0, data, EmptyBytes32, salt
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                salt,
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
                salt,
                delay + 1,
            )

    def authority_set_public_capability(
        self, target_address, functionSig, enabled, salt=EmptyBytes32
    ):
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
            target.address, 0, data, EmptyBytes32, salt
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                salt,
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
                salt,
                delay + 1,
            )

    def authority_burn_capability(self, target_address, functionSig, salt=EmptyBytes32):
        """
        @dev Burns the ability to call a contract's function from anyone irrespective of their roles in the Authority.
        @param target_address The address of the contract containing the function.
        @param functionSig The signature of the function to grant the capability to.
        """
        ## Check if tx is already scheduled
        target = self.authority
        data = target.burnCapability.encode_input(target_address, functionSig)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, salt
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                salt,
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
                salt,
                delay + 1,
            )

    def authority_set_authority(self, new_authority, salt=EmptyBytes32):
        """
        @dev Changes the Governance underying authority contract.
        @param new_authority The address of the new Authority contract.
        """
        ## Check if tx is already scheduled
        target = self.authority
        data = target.setAuthority.encode_input(new_authority)
        id = self.highsec_timelock.hashOperation(
            target.address, 0, data, EmptyBytes32, salt
        )

        if self.highsec_timelock.isOperation(id):
            self.execute_timelock(
                self.highsec_timelock,
                target.address,
                0,
                data,
                EmptyBytes32,
                salt,
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
                salt,
                delay + 1,
            )

    #### ===== CDP OPS ===== ####

    def _assert_collateral_balance(self, coll_amount):
        total_coll_bal = self.collateral.balanceOf(self.safe.address)
        # NOTE: ongoing work on solidity side for at https://github.com/ebtc-protocol/ebtc/pull/739. new deployment incoming
        assert total_coll_bal >= self.collateral.getSharesByPooledEth(coll_amount)

    def _assert_debt_balance(self, debt_amount):
        total_debt_bal = self.ebtc_token.balanceOf(self.safe.address)
        assert total_debt_bal >= debt_amount
        return total_debt_bal

    def _assert_cdp_id_ownership(self, cdp_id):
        cdp_safe_owned = self.sorted_cdps.getCdpsOf(self.safe.address)
        assert cdp_id in cdp_safe_owned

    def _assert_health_new_icr(self, new_icr):
        # NOTE: chose 120% to have alert with a breath range from MCR
        assert new_icr > self.SAFE_ICR_THRESHOLD

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
        @dev Opens a new cdp position. Attention to target_cr unit format, see below!
        @param coll_amount The total stETH collateral amount deposited for the specified Cdp.
        @param target_cr The desired target collateral ratio in the cdp position. Unit format: cr follows a 10^18 formatting
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
        cdp_id_liquidator_reward_shares = self.collateral.getSharesByPooledEth(self.LIQUIDATOR_REWARD)
        cdp_id_debt, cdp_id_coll = self.cdp_manager.getSyncedDebtAndCollShares(cdp_id)
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

        # 2.2. verify that enough collateral was returned + gas stipend, assertion denominated in common `shares` unit
        assert self.collateral.getSharesByPooledEth(
            self.collateral.balanceOf(self.safe.address)
        ) == (
            cdp_id_coll
            + cdp_id_liquidator_reward_shares
            + self.collateral.getSharesByPooledEth(collateral_balance_before)
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
        prev_icr = self.cdp_manager.getSyncedICR(cdp_id, feed_price)
        prev_tcr = self.cdp_manager.getSyncedTCR(feed_price)
        prev_coll_balance = self.cdp_manager.getCdpCollShares(cdp_id)

        # 1. collateral approval for BO
        self.collateral.approve(self.borrower_operations.address, coll_amount)

        # 2. increase collateral in target cdp id
        self.borrower_operations.addColl(cdp_id, cdp_id, cdp_id, coll_amount)

        # 3. assertions:

        # 3.1. icr and tcr had increased
        assert self.cdp_manager.getSyncedICR(cdp_id, feed_price) > prev_icr
        assert self.cdp_manager.getSyncedTCR(feed_price) > prev_tcr

        # 3.2 collateral in cdp at storage is exact on "shares" terms, following internal cdp accounting
        # after increase should be equal to final = initial + top-up collateral
        assert self.cdp_manager.getCdpCollShares(
            cdp_id
        ) == prev_coll_balance + self.collateral.getSharesByPooledEth(coll_amount)

    def cdp_withdraw_collateral(self, cdp_id, coll_amount):
        """
        @dev Withdraws the amount of collateral from the specified Cdp.
        @param cdp_id The CdpId on which this operation is operated.
        @param coll_amount The total stETH collateral amount withdrawn (reduced) for the specified Cdp.
        """
        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        # verify: cdp holds enough collateral to be withdrawn
        _, cdp_id_coll = self.cdp_manager.getSyncedDebtAndCollShares(cdp_id)
        assert cdp_id_coll > coll_amount

        # verify: check recovery mode status. use sync tcr so accounts for split fee
        feed_price = self.price_feed.fetchPrice.call()
        prev_tcr = self.cdp_manager.getSyncedTCR(feed_price)
        assert prev_tcr > self.CCR

        prev_icr = self.cdp_manager.getSyncedICR(cdp_id, feed_price)
        prev_tcr = self.cdp_manager.getSyncedTCR(feed_price)

        # 1. decreased collateral in target cdp id
        self.borrower_operations.withdrawColl(cdp_id, coll_amount, cdp_id, cdp_id)

        # 2. assertions:
        new_icr = self.cdp_manager.getSyncedICR(cdp_id, feed_price)

        # 2.1 verify icr not below `SAFE_ICR_THRESHOLD`
        self._assert_health_new_icr(new_icr)

        C.print(
            f"[green]Withdrawing {coll_amount/1e18} collateral brings the CDP from {prev_icr/1e16}% to {new_icr/1e16}% ICR[/green]"
        )

        # 2.1. icr and tcr had decreased
        assert new_icr < prev_icr
        assert self.cdp_manager.getSyncedTCR(feed_price) < prev_tcr

        # 2.2 collateral in cdp at storage has decreased
        assert self.cdp_manager.getCdpCollShares(cdp_id) < cdp_id_coll

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
        prev_icr = self.cdp_manager.getSyncedICR(cdp_id, feed_price)

        # 1. repay debt
        self.borrower_operations.repayDebt(cdp_id, debt_repay_amount, cdp_id, cdp_id)

        # 2. assertions

        # 2.1. debt balance decreased
        assert self.ebtc_token.balanceOf(self.safe.address) < prev_debt_balance

        # 2.2. icr should improved
        assert self.cdp_manager.getSyncedICR(cdp_id, feed_price) > prev_icr

    def cdp_withdraw_debt(self, cdp_id, debt_withdrawable_amount):
        """
        @dev Withdraws the amount of eBTC token from the specified Cdp, thus increasing its debt accounting.
        @param cdp_id The CdpId on which this operation is operated.
        @param debt_withdrawable_amount The total debt collateral amount increased for the specified Cdp.
        """
        # verify: cdp id ownership from caller
        self._assert_cdp_id_ownership(cdp_id)

        # verify: check recovery mode status. use sync tcr so accounts for split fee
        feed_price = self.price_feed.fetchPrice.call()
        sync_tcr = self.cdp_manager.getSyncedTCR(feed_price)
        assert sync_tcr > self.CCR

        # verify: existing debt in cdp id is greater than amount to wd
        debt_before = self.cdp_manager.getCdpDebt(cdp_id)
        assert debt_before > debt_withdrawable_amount

        prev_icr = self.cdp_manager.getSyncedICR(cdp_id, feed_price)

        # 1. wd debt from cdp
        self.borrower_operations.withdrawDebt(
            cdp_id, debt_withdrawable_amount, cdp_id, cdp_id
        )

        # 2. assertions
        new_icr = self.cdp_manager.getSyncedICR(cdp_id, feed_price)

        # 2.1 verify icr not below `SAFE_ICR_THRESHOLD`
        self._assert_health_new_icr(new_icr)

        C.print(
            f"[green]Withdrawing {debt_withdrawable_amount/1e18} eBTC brings the CDP from {prev_icr/1e16}% to {new_icr/1e16}% ICR[/green]"
        )

        # 2.1. debt should increased
        assert self.cdp_manager.getCdpDebt(cdp_id) > debt_before

        # 2.2. icr decreased
        assert new_icr < prev_icr
