// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IHintHelpers {
    function BORROWING_FEE_FLOOR() external view returns (uint256);
    function CCR() external view returns (uint256);
    function DECIMAL_PRECISION() external view returns (uint256);
    function LICR() external view returns (uint256);
    function LIQUIDATOR_REWARD() external view returns (uint256);
    function MAX_REWARD_SPLIT() external view returns (uint256);
    function MCR() external view returns (uint256);
    function MIN_NET_STETH_BALANCE() external view returns (uint256);
    function NAME() external view returns (string memory);
    function PERCENT_DIVISOR() external view returns (uint256);
    function STAKING_REWARD_SPLIT() external view returns (uint256);
    function activePool() external view returns (address);
    function cdpManager() external view returns (address);
    function collateral() external view returns (address);
    function computeCR(uint256 _coll, uint256 _debt, uint256 _price) external pure returns (uint256);
    function computeNominalCR(uint256 _coll, uint256 _debt) external pure returns (uint256);
    function getApproxHint(
        uint256 _CR,
        uint256 _numTrials,
        uint256 _inputRandomSeed
    ) external view returns (bytes32 hint, uint256 diff, uint256 latestRandomSeed);
    function getRedemptionHints(
        uint256 _EBTCamount,
        uint256 _price,
        uint256 _maxIterations
    )
        external
        view
        returns (
            bytes32 firstRedemptionHint,
            uint256 partialRedemptionHintNICR,
            uint256 truncatedEBTCamount,
            uint256 partialRedemptionNewColl
        );
    function getSystemCollShares() external view returns (uint256 entireSystemColl);
    function priceFeed() external view returns (address);
    function sortedCdps() external view returns (address);
}
