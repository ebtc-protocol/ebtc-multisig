// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEbtcFeed {
  event AuthorityUpdated(address indexed user, address indexed newAuthority);
  event CollateralFeedSourceUpdated(address indexed stEthFeed);
  event FallbackCallerChanged(
    address indexed _oldFallbackCaller,
    address indexed _newFallbackCaller
  );
  event LastGoodPriceUpdated(uint256 _lastGoodPrice);
  event PriceFeedStatusChanged(uint8 newStatus);
  event PrimaryOracleUpdated(
    address indexed _oldOracle,
    address indexed _newOracle
  );
  event SecondaryOracleUpdated(
    address indexed _oldOracle,
    address indexed _newOracle
  );
  event UnhealthyFallbackCaller(
    address indexed _fallbackCaller,
    uint256 timestamp
  );

  function NAME() external view returns (string memory);
  function authority() external view returns (address);
  function authorityInitialized() external view returns (bool);
  function fetchPrice() external returns (uint256);
  function lastGoodPrice() external view returns (uint256);
  function primaryOracle() external view returns (address);
  function secondaryOracle() external view returns (address);
  function setPrimaryOracle(address _newPrimary) external;
  function setSecondaryOracle(address _newSecondary) external;
  function tinfoilCall(
    address _target,
    bytes memory _calldata
  ) external returns (uint256);
}
