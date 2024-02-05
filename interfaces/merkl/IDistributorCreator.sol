// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IDistributorCreator {
    event NewDistribution(
        DistributionParameters distribution,
        address indexed sender
    );

    struct DistributionParameters {
        bytes32 rewardId;
        address uniV3Pool;
        address rewardToken;
        uint256 amount;
        address[] positionWrappers;
        uint32[] wrapperTypes;
        uint32 propToken0;
        uint32 propToken1;
        uint32 propFees;
        uint32 epochStart;
        uint32 numEpoch;
        uint32 isOutOfRangeIncentivized;
        uint32 boostedReward;
        address boostingAddress;
        bytes additionalData;
    }

    struct RewardTokenAmounts {
        address token;
        uint256 minimumAmountPerEpoch;
    }

    function createDistribution(DistributionParameters memory distribution)
        external
        returns (uint256 distributionAmount);

    function createDistributions(DistributionParameters[] memory distributions)
        external
        returns (uint256[] memory);

    function getValidRewardTokens()
        external
        view
        returns (RewardTokenAmounts[] memory);

    function fees() external view returns (uint256);

    function message() external view returns (string memory);

    function setRewardTokenMinAmounts(
        address[] memory tokens,
        uint256[] memory amounts
    ) external;

    function sign(bytes memory signature) external;

    function rewardTokenMinAmounts(address) external view returns (uint256);

    function toggleSigningWhitelist(address user) external;

    function toggleTokenWhitelist(address token) external;
}
