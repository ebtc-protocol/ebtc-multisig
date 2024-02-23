// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IPriceFeedTestnet {
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event FallbackCallerChanged(
        address indexed _oldFallbackCaller,
        address indexed _newFallbackCaller
    );
    event LastGoodPriceUpdated(uint256 _lastGoodPrice);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event PriceFeedStatusChanged(uint8 newStatus);
    event UnhealthyFallbackCaller(address indexed _fallbackCaller, uint256 timestamp);

    function _useFallback() external view returns (bool);
    function authority() external view returns (address);
    function authorityInitialized() external view returns (bool);
    function fallbackCaller() external view returns (address);
    function fetchPrice() external returns (uint256);
    function getPrice() external view returns (uint256);
    function owner() external view returns (address);
    function renounceOwnership() external;
    function setAddresses(
        address _priceAggregatorAddress,
        address _fallbackCallerAddress,
        address _authorityAddress
    ) external;
    function setAuthority(address newAuthority) external;
    function setFallbackCaller(address _fallbackCaller) external;
    function setPrice(uint256 price) external returns (bool);
    function toggleUseFallback() external returns (bool);
    function transferOwnership(address newOwner) external;
}