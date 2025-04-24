// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IOraclePriceConstraint {
    function setMinPrice(uint256 _minPriceBPS) external;
    function setOracleFreshness(uint256 _oracleFreshnessSeconds) external;
}
