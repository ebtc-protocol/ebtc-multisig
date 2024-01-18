// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface ICdpManager {
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event BaseRateUpdated(uint256 _baseRate);
    event BetaSet(uint256 _beta);
    event CdpArrayIndexUpdated(bytes32 _cdpId, uint256 _newIndex);
    event CdpDebtRedistributionIndexUpdated(bytes32 _cdpId, uint256 _cdpDebtRedistributionIndex);
    event CdpFeeSplitApplied(
        bytes32 _cdpId,
        uint256 _oldPerUnitCdp,
        uint256 _newPerUnitCdp,
        uint256 _collReduced,
        uint256 _collLeft
    );
    event CdpLiquidated(
        bytes32 indexed _cdpId,
        address indexed _borrower,
        uint256 _debt,
        uint256 _collShares,
        uint8 _operation,
        address indexed _liquidator,
        uint256 _premiumToLiquidator
    );
    event CdpPartiallyLiquidated(
        bytes32 indexed _cdpId,
        address indexed _borrower,
        uint256 _debt,
        uint256 _collShares,
        uint8 operation,
        address indexed _liquidator,
        uint256 _premiumToLiquidator
    );
    event CdpUpdated(
        bytes32 indexed _cdpId,
        address indexed _borrower,
        address indexed _executor,
        uint256 _oldDebt,
        uint256 _oldCollShares,
        uint256 _debt,
        uint256 _collShares,
        uint256 _stake,
        uint8 _operation
    );
    event CollateralFeePerUnitUpdated(uint256 _oldPerUnit, uint256 _newPerUnit, uint256 _feeTaken);
    event FeeRecipientAddressChanged(address indexed _feeRecipientAddress);
    event GracePeriodDurationSet(uint256 _recoveryModeGracePeriodDuration);
    event GracePeriodEnd();
    event GracePeriodStart();
    event LastRedemptionTimestampUpdated(uint256 _lastFeeOpTime);
    event Liquidation(uint256 _liquidatedDebt, uint256 _liquidatedColl, uint256 _liqReward);
    event MinuteDecayFactorSet(uint256 _minuteDecayFactor);
    event Redemption(
        uint256 _debtToRedeemExpected,
        uint256 _debtToRedeemActual,
        uint256 _collSharesSent,
        uint256 _feeCollShares,
        address indexed _redeemer
    );
    event RedemptionFeeFloorSet(uint256 _redemptionFeeFloor);
    event RedemptionsPaused(bool _paused);
    event StEthIndexUpdated(uint256 _oldIndex, uint256 _newIndex, uint256 _updTimestamp);
    event StakingRewardSplitSet(uint256 _stakingRewardSplit);
    event SystemDebtRedistributionIndexUpdated(uint256 _systemDebtRedistributionIndex);
    event SystemSnapshotsUpdated(uint256 _totalStakesSnapshot, uint256 _totalCollateralSnapshot);
    event TCRNotified(uint256 TCR);
    event TotalStakesUpdated(uint256 _newTotalStakes);

    function BORROWING_FEE_FLOOR() external view returns (uint256);
    function CCR() external view returns (uint256);
    function CdpIds(uint256) external view returns (bytes32);
    function Cdps(
        bytes32
    )
        external
        view
        returns (
            uint256 debt,
            uint256 coll,
            uint256 stake,
            uint256 liquidatorRewardShares,
            uint8 status,
            uint128 arrayIndex
        );
    function DECIMAL_PRECISION() external view returns (uint256);
    function LICR() external view returns (uint256);
    function LIQUIDATOR_REWARD() external view returns (uint256);
    function MAX_MINUTE_DECAY_FACTOR() external view returns (uint256);
    function MAX_REWARD_SPLIT() external view returns (uint256);
    function MCR() external view returns (uint256);
    function MINIMUM_GRACE_PERIOD() external view returns (uint128);
    function MIN_MINUTE_DECAY_FACTOR() external view returns (uint256);
    function MIN_NET_STETH_BALANCE() external view returns (uint256);
    function MIN_REDEMPTION_FEE_FLOOR() external view returns (uint256);
    function NAME() external view returns (string memory);
    function PERCENT_DIVISOR() external view returns (uint256);
    function SECONDS_IN_ONE_MINUTE() external view returns (uint256);
    function STAKING_REWARD_SPLIT() external view returns (uint256);
    function UNSET_TIMESTAMP() external view returns (uint128);
    function activePool() external view returns (address);
    function authority() external view returns (address);
    function authorityInitialized() external view returns (bool);
    function baseRate() external view returns (uint256);
    function batchLiquidateCdps(bytes32[] memory _cdpArray) external;
    function beta() external view returns (uint256);
    function borrowerOperationsAddress() external view returns (address);
    function calcFeeUponStakingReward(
        uint256 _newIndex,
        uint256 _prevIndex
    ) external view returns (uint256, uint256, uint256);
    function canLiquidateRecoveryMode(uint256 icr, uint256 tcr) external view returns (bool);
    function cdpDebtRedistributionIndex(bytes32) external view returns (uint256);
    function cdpStEthFeePerUnitIndex(bytes32) external view returns (uint256);
    function checkPotentialRecoveryMode(
        uint256 _systemCollShares,
        uint256 _systemDebt,
        uint256 _price
    ) external view returns (bool);
    function checkRecoveryMode(uint256 _price) external view returns (bool);
    function closeCdp(bytes32 _cdpId, address _borrower, uint256 _debt, uint256 _coll) external;
    function collateral() external view returns (address);
    function ebtcToken() external view returns (address);
    function getAccumulatedFeeSplitApplied(
        bytes32 _cdpId,
        uint256 _systemStEthFeePerUnitIndex
    ) external view returns (uint256, uint256);
    function getActiveCdpsCount() external view returns (uint256);
    function getCachedICR(bytes32 _cdpId, uint256 _price) external view returns (uint256);
    function getCachedNominalICR(bytes32 _cdpId) external view returns (uint256);
    function getCachedTCR(uint256 _price) external view returns (uint256);
    function getCdpCollShares(bytes32 _cdpId) external view returns (uint256);
    function getCdpDebt(bytes32 _cdpId) external view returns (uint256);
    function getCdpLiquidatorRewardShares(bytes32 _cdpId) external view returns (uint256);
    function getCdpStake(bytes32 _cdpId) external view returns (uint256);
    function getCdpStatus(bytes32 _cdpId) external view returns (uint256);
    function getDeploymentStartTime() external view returns (uint256);
    function getIdFromCdpIdsArray(uint256 _index) external view returns (bytes32);
    function getPendingRedistributedDebt(
        bytes32 _cdpId
    ) external view returns (uint256 pendingEBTCDebtReward);
    function getRedemptionFeeWithDecay(uint256 _stETHToRedeem) external view returns (uint256);
    function getRedemptionRate() external view returns (uint256);
    function getRedemptionRateWithDecay() external view returns (uint256);
    function getSyncedCdpCollShares(bytes32 _cdpId) external view returns (uint256);
    function getSyncedCdpDebt(bytes32 _cdpId) external view returns (uint256);
    function getSyncedDebtAndCollShares(
        bytes32 _cdpId
    ) external view returns (uint256 debt, uint256 coll);
    function getSyncedICR(bytes32 _cdpId, uint256 _price) external view returns (uint256);
    function getSyncedNominalICR(bytes32 _cdpId) external view returns (uint256);
    function getSyncedTCR(uint256 _price) external view returns (uint256);
    function getSystemCollShares() external view returns (uint256 entireSystemColl);
    function getSystemDebt() external view returns (uint256 entireSystemDebt);
    function hasPendingRedistributedDebt(bytes32 _cdpId) external view returns (bool);
    function initializeCdp(
        bytes32 _cdpId,
        uint256 _debt,
        uint256 _coll,
        uint256 _liquidatorRewardShares,
        address _borrower
    ) external;
    function lastEBTCDebtErrorRedistribution() external view returns (uint256);
    function lastGracePeriodStartTimestamp() external view returns (uint128);
    function lastRedemptionTimestamp() external view returns (uint256);
    function liquidate(bytes32 _cdpId) external;
    function liquidationLibrary() external view returns (address);
    function locked() external view returns (uint256);
    function minuteDecayFactor() external view returns (uint256);
    function notifyEndGracePeriod(uint256 tcr) external;
    function notifyStartGracePeriod(uint256 tcr) external;
    function partiallyLiquidate(
        bytes32 _cdpId,
        uint256 _partialAmount,
        bytes32 _upperPartialHint,
        bytes32 _lowerPartialHint
    ) external;
    function priceFeed() external view returns (address);
    function recoveryModeGracePeriodDuration() external view returns (uint128);
    function redeemCollateral(
        uint256 _debt,
        bytes32 _firstRedemptionHint,
        bytes32 _upperPartialRedemptionHint,
        bytes32 _lowerPartialRedemptionHint,
        uint256 _partialRedemptionHintNICR,
        uint256 _maxIterations,
        uint256 _maxFeePercentage
    ) external;
    function redemptionFeeFloor() external view returns (uint256);
    function redemptionsPaused() external view returns (bool);
    function setAuthority(address newAuthority) external;
    function setBeta(uint256 _beta) external;
    function setGracePeriod(uint128 _gracePeriod) external;
    function setMinuteDecayFactor(uint256 _minuteDecayFactor) external;
    function setRedemptionFeeFloor(uint256 _redemptionFeeFloor) external;
    function setRedemptionsPaused(bool _paused) external;
    function setStakingRewardSplit(uint256 _stakingRewardSplit) external;
    function sortedCdps() external view returns (address);
    function stEthIndex() external view returns (uint256);
    function stakingRewardSplit() external view returns (uint256);
    function syncAccounting(bytes32 _cdpId) external;
    function syncGlobalAccounting() external;
    function syncGlobalAccountingAndGracePeriod() external;
    function systemDebtRedistributionIndex() external view returns (uint256);
    function systemStEthFeePerUnitIndex() external view returns (uint256);
    function systemStEthFeePerUnitIndexError() external view returns (uint256);
    function totalCollateralSnapshot() external view returns (uint256);
    function totalStakes() external view returns (uint256);
    function totalStakesSnapshot() external view returns (uint256);
    function updateCdp(
        bytes32 _cdpId,
        address _borrower,
        uint256 _coll,
        uint256 _debt,
        uint256 _newColl,
        uint256 _newDebt
    ) external;
    function updateStakeAndTotalStakes(bytes32 _cdpId) external returns (uint256);
}
