// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface ICollSurplusPool {
  event AuthorityUpdated(address indexed user, address indexed newAuthority);
  event CollSharesTransferred(address indexed _to, uint256 _amount);
  event SurplusCollSharesAdded(
    bytes32 indexed _cdpId,
    address indexed _account,
    uint256 _claimableSurplusCollShares,
    uint256 _surplusCollSharesAddedFromCollateral,
    uint256 _surplusCollSharesAddedFromLiquidatorReward
  );
  event SweepTokenSuccess(
    address indexed _token,
    uint256 _amount,
    address indexed _recipient
  );

  function NAME() external view returns (string memory);
  function activePoolAddress() external view returns (address);
  function authority() external view returns (address);
  function authorityInitialized() external view returns (bool);
  function borrowerOperationsAddress() external view returns (address);
  function cdpManagerAddress() external view returns (address);
  function claimSurplusCollShares(address _account) external;
  function collateral() external view returns (address);
  function feeRecipientAddress() external view returns (address);
  function getSurplusCollShares(
    address _account
  ) external view returns (uint256);
  function getTotalSurplusCollShares() external view returns (uint256);
  function increaseSurplusCollShares(
    bytes32 _cdpId,
    address _account,
    uint256 _collateralShares,
    uint256 _liquidatorRewardShares
  ) external;
  function increaseTotalSurplusCollShares(uint256 _value) external;
  function locked() external view returns (uint256);
  function sweepToken(address token, uint256 amount) external;
}
