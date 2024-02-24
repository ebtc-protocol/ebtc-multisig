// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IPriceFeedTestnet {
  event AuthorityUpdated(address indexed user, address indexed newAuthority);
  event CollateralFeedSourceUpdated(address indexed stEthFeed);
  event FallbackCallerChanged(
    address indexed _oldFallbackCaller,
    address indexed _newFallbackCaller
  );
  event LastGoodPriceUpdated(uint256 _lastGoodPrice);
  event PriceFeedStatusChanged(uint8 newStatus);
  event UnhealthyFallbackCaller(
    address indexed _fallbackCaller,
    uint256 timestamp
  );

  function DECIMAL_PRECISION() external view returns (uint256);

  function DENOMINATOR() external view returns (uint256);

  function ETH_BTC_CL_FEED() external view returns (address);

  function MAX_DECIMALS() external view returns (uint8);

  function MAX_PRICE_DEVIATION_FROM_PREVIOUS_ROUND()
    external
    view
    returns (uint256);

  function MAX_PRICE_DIFFERENCE_BETWEEN_ORACLES()
    external
    view
    returns (uint256);

  function NAME() external view returns (string memory);

  function SCALED_DECIMAL() external view returns (uint256);

  function STETH_ETH_CL_FEED() external view returns (address);

  function STETH_ETH_FIXED_FEED() external view returns (address);

  function TIMEOUT_ETH_BTC_FEED() external view returns (uint256);

  function TIMEOUT_STETH_ETH_FEED() external view returns (uint256);

  function authority() external view returns (address);

  function authorityInitialized() external view returns (bool);

  function fallbackCaller() external view returns (address);

  function fetchPrice() external returns (uint256);

  function lastGoodPrice() external view returns (uint256);

  function setCollateralFeedSource(bool _useDynamicFeed) external;

  function setFallbackCaller(address _fallbackCaller) external;

  function status() external view returns (uint8);

  function useDynamicFeed() external view returns (bool);
}
