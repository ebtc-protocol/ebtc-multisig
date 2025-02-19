// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IStakedEbtc {
    /// @notice Information about the current rewards cycle
    struct RewardsCycleData {
        uint40 cycleEnd; // Timestamp of the end of the current rewards cycle
        uint40 lastSync; // Timestamp of the last time the rewards cycle was synced
        uint192 rewardCycleAmount; // Amount of rewards to be distributed in the current cycle
    }
    
    function REWARDS_CYCLE_LENGTH() external view returns (uint256);
    function asset() external view returns (address);
    function donate(uint256 amount) external;
    function syncRewardsAndDistribution() external;
    function rewardsCycleData() external view returns (RewardsCycleData memory);
    function storedTotalAssets() external view returns (uint256);
    function totalBalance() external view returns (uint256);
    function setMintingFee(uint256 _mintingFee) external;
    function sweep(address token) external;
    function setMaxDistributionPerSecondPerAsset(uint256 _maxDistributionPerSecondPerAsset) external;
}
