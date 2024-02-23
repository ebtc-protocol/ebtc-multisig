// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBorrowerOperations {
  event AuthorityUpdated(address indexed user, address indexed newAuthority);
  event FeeRecipientAddressChanged(address indexed _feeRecipientAddress);
  event FlashFeeSet(address indexed _setter, uint256 _oldFee, uint256 _newFee);
  event FlashLoanSuccess(
    address indexed _receiver,
    address indexed _token,
    uint256 _amount,
    uint256 _fee
  );
  event FlashLoansPaused(address indexed _setter, bool _paused);
  event MaxFlashFeeSet(
    address indexed _setter,
    uint256 _oldMaxFee,
    uint256 _newMaxFee
  );
  event PositionManagerApprovalSet(
    address indexed _borrower,
    address indexed _positionManager,
    uint8 _approval
  );

  function BORROWING_FEE_FLOOR() external view returns (uint256);
  function CCR() external view returns (uint256);
  function DECIMAL_PRECISION() external view returns (uint256);
  function DOMAIN_SEPARATOR() external view returns (bytes32);
  function FLASH_SUCCESS_VALUE() external view returns (bytes32);
  function LICR() external view returns (uint256);
  function LIQUIDATOR_REWARD() external view returns (uint256);
  function MAX_BPS() external view returns (uint256);
  function MAX_FEE_BPS() external view returns (uint256);
  function MAX_REWARD_SPLIT() external view returns (uint256);
  function MCR() external view returns (uint256);
  function MIN_CHANGE() external view returns (uint256);
  function MIN_NET_STETH_BALANCE() external view returns (uint256);
  function NAME() external view returns (string memory);
  function PERCENT_DIVISOR() external view returns (uint256);
  function STAKING_REWARD_SPLIT() external view returns (uint256);
  function activePool() external view returns (address);
  function addColl(
    bytes32 _cdpId,
    bytes32 _upperHint,
    bytes32 _lowerHint,
    uint256 _stEthBalanceIncrease
  ) external;
  function adjustCdp(
    bytes32 _cdpId,
    uint256 _stEthBalanceDecrease,
    uint256 _debtChange,
    bool _isDebtIncrease,
    bytes32 _upperHint,
    bytes32 _lowerHint
  ) external;
  function adjustCdpWithColl(
    bytes32 _cdpId,
    uint256 _stEthBalanceDecrease,
    uint256 _debtChange,
    bool _isDebtIncrease,
    bytes32 _upperHint,
    bytes32 _lowerHint,
    uint256 _stEthBalanceIncrease
  ) external;
  function authority() external view returns (address);
  function authorityInitialized() external view returns (bool);
  function cdpManager() external view returns (address);
  function claimSurplusCollShares() external;
  function closeCdp(bytes32 _cdpId) external;
  function collSurplusPool() external view returns (address);
  function collateral() external view returns (address);
  function domainSeparator() external view returns (bytes32);
  function ebtcToken() external view returns (address);
  function feeBps() external view returns (uint16);
  function feeRecipientAddress() external view returns (address);
  function flashFee(
    address token,
    uint256 amount
  ) external view returns (uint256);
  function flashLoan(
    address receiver,
    address token,
    uint256 amount,
    bytes memory data
  ) external returns (bool);
  function flashLoansPaused() external view returns (bool);
  function getPositionManagerApproval(
    address _borrower,
    address _positionManager
  ) external view returns (uint8);
  function getSystemCollShares()
    external
    view
    returns (uint256 entireSystemColl);
  function increasePermitNonce() external returns (uint256);
  function locked() external view returns (uint256);
  function maxFlashLoan(address token) external view returns (uint256);
  function nonces(address owner) external view returns (uint256);
  function openCdp(
    uint256 _debt,
    bytes32 _upperHint,
    bytes32 _lowerHint,
    uint256 _stEthBalance
  ) external returns (bytes32);
  function openCdpFor(
    uint256 _debt,
    bytes32 _upperHint,
    bytes32 _lowerHint,
    uint256 _stEthBalance,
    address _borrower
  ) external returns (bytes32);
  function permitPositionManagerApproval(
    address _borrower,
    address _positionManager,
    uint8 _approval,
    uint256 _deadline,
    uint8 v,
    bytes32 r,
    bytes32 s
  ) external;
  function permitTypeHash() external pure returns (bytes32);
  function positionManagers(address, address) external view returns (uint8);
  function priceFeed() external view returns (address);
  function renouncePositionManagerApproval(address _borrower) external;
  function repayDebt(
    bytes32 _cdpId,
    uint256 _debt,
    bytes32 _upperHint,
    bytes32 _lowerHint
  ) external;
  function revokePositionManagerApproval(address _positionManager) external;
  function setFeeBps(uint256 _newFee) external;
  function setFlashLoansPaused(bool _paused) external;
  function setPositionManagerApproval(
    address _positionManager,
    uint8 _approval
  ) external;
  function sortedCdps() external view returns (address);
  function version() external pure returns (string memory);
  function withdrawColl(
    bytes32 _cdpId,
    uint256 _stEthBalanceDecrease,
    bytes32 _upperHint,
    bytes32 _lowerHint
  ) external;
  function withdrawDebt(
    bytes32 _cdpId,
    uint256 _debt,
    bytes32 _upperHint,
    bytes32 _lowerHint
  ) external;
}
