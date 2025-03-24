// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEbtcBsm {
    function updateEscrow(address _newEscrow) external;
    function setOraclePriceConstraint(address _newOraclePriceConstraint) external;
    function setRateLimitingConstraint(address _newRateLimitingConstraint) external;
    function setBuyAssetConstraint(address _newBuyAssetConstraint) external;
}
