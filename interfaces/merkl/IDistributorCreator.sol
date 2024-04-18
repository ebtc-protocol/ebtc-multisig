// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IDistributorCreator {
    event NewCampaign(CampaignParameters campaign);
    event NewDistribution(
        DistributionParameters distribution,
        address indexed sender
    );
    struct CampaignParameters {
        bytes32 campaignId;
        address creator;
        address rewardToken;
        uint256 amount;
        uint32 campaignType;
        uint32 startTimestamp;
        uint32 duration;
        bytes campaignData;
    }

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

    function BASE_9() external view returns (uint256);

    function CHAIN_ID() external view returns (uint256);

    function HOUR() external view returns (uint32);

    function _nonces(address) external view returns (uint256);

    function acceptConditions() external;

    function campaign(bytes32 _campaignId) external view returns (CampaignParameters memory);

    function campaignId(CampaignParameters memory campaignData) external view returns (bytes32);

    function campaignList(uint256)
        external
        view
        returns (
            bytes32 campaignId,
            address creator,
            address rewardToken,
            uint256 amount,
            uint32 campaignType,
            uint32 startTimestamp,
            uint32 duration,
            bytes memory campaignData
        );

    function campaignLookup(bytes32 _campaignId) external view returns (uint256);

    function campaignSpecificFees(uint32) external view returns (uint256);

    function core() external view returns (address);

    function createCampaign(CampaignParameters memory newCampaign) external returns (bytes32);

    function createCampaigns(CampaignParameters[] memory campaigns) external returns (bytes32[] memory);

    function createDistribution(DistributionParameters memory newDistribution)
        external
        returns (uint256 distributionAmount);

    function createDistributions(DistributionParameters[] memory distributions) external returns (uint256[] memory);

    function defaultFees() external view returns (uint256);

    function distribution(uint256 index) external view returns (CampaignParameters memory);

    function distributionList(uint256)
        external
        view
        returns (
            bytes32 rewardId,
            address uniV3Pool,
            address rewardToken,
            uint256 amount,
            uint32 propToken0,
            uint32 propToken1,
            uint32 propFees,
            uint32 epochStart,
            uint32 numEpoch,
            uint32 isOutOfRangeIncentivized,
            uint32 boostedReward,
            address boostingAddress,
            bytes memory additionalData
        );

    function distributor() external view returns (address);

    function feeRebate(address) external view returns (uint256);

    function feeRecipient() external view returns (address);

    function getCampaignsBetween(uint32 start, uint32 end, uint32 skip, uint32 first)
        external
        view
        returns (CampaignParameters[] memory, uint256 lastIndexCampaign);

    function getDistributionsBetweenEpochs(uint32 epochStart, uint32 epochEnd, uint32 skip, uint32 first)
        external
        view
        returns (DistributionParameters[] memory, uint256 lastIndexDistribution);

    function getValidRewardTokens() external view returns (RewardTokenAmounts[] memory);

    function getValidRewardTokens(uint32 skip, uint32 first)
        external
        view
        returns (RewardTokenAmounts[] memory, uint256);

    function initialize(address _core, address _distributor, uint256 _fees) external;

    function isWhitelistedToken(address) external view returns (uint256);

    function message() external view returns (string memory);

    function messageHash() external view returns (bytes32);

    function proxiableUUID() external view returns (bytes32);

    function recoverFees(address[] memory tokens, address to) external;

    function rewardTokenMinAmounts(address) external view returns (uint256);

    function rewardTokens(uint256) external view returns (address);

    function setCampaignFees(uint32 campaignType, uint256 _fees) external;

    function setFeeRecipient(address _feeRecipient) external;

    function setFees(uint256 _defaultFees) external;

    function setMessage(string memory _message) external;

    function setNewDistributor(address _distributor) external;

    function setRewardTokenMinAmounts(address[] memory tokens, uint256[] memory amounts) external;

    function setUserFeeRebate(address user, uint256 userFeeRebate) external;

    function sign(bytes memory signature) external;

    function signAndCreateCampaign(CampaignParameters memory newCampaign, bytes memory signature)
        external
        returns (bytes32);

    function toggleSigningWhitelist(address user) external;

    function toggleTokenWhitelist(address token) external;

    function upgradeTo(address newImplementation) external;

    function upgradeToAndCall(address newImplementation, bytes memory data) external payable;

    function userSignatureWhitelist(address) external view returns (uint256);

    function userSignatures(address) external view returns (bytes32);
}