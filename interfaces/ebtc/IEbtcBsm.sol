// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEbtcBsm {
    function updateEscrow(address _newEscrow) external;
    function setOraclePriceConstraint(address _newOraclePriceConstraint) external;
    function setRateLimitingConstraint(address _newRateLimitingConstraint) external;
    function setBuyAssetConstraint(address _newBuyAssetConstraint) external;
    function setFeeToSell(uint256 _feeToSellBPS) external;
    function setFeeToBuy(uint256 _feeToBuyBPS) external;
    function pause() external;
    function unpause() external;
    function sellAssetNoFee(uint256 _assetAmountIn, address _recipient, uint256 _minOutAmount) external;
    function buyAssetNoFee(uint256 _ebtcAmountIn, address _recipient, uint256 _minOutAmount) external;
}
