// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IActivePool {
  event ActivePoolEBTCDebtUpdated(uint256 _EBTCDebt);
  event AuthorityUpdated(address indexed user, address indexed newAuthority);
  event CollSharesTransferred(address indexed _to, uint256 _amount);
  event EBTCBalanceUpdated(uint256 _newBalance);
  event ETHBalanceUpdated(uint256 _newBalance);
  event FeeRecipientClaimableCollSharesDecreased(uint256 _coll, uint256 _fee);
  event FeeRecipientClaimableCollSharesIncreased(uint256 _coll, uint256 _fee);
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
  event NewTrackValue(
    uint256 _oldValue,
    uint256 _newValue,
    uint256 _ts,
    uint256 _newAcc
  );
  event SweepTokenSuccess(
    address indexed _token,
    uint256 _amount,
    address indexed _recipient
  );
  event SystemCollSharesUpdated(uint256 _coll);
  event TwapDisabled();

  function DECIMAL_PRECISION() external view returns (uint256);
  function FLASH_SUCCESS_VALUE() external view returns (bytes32);
  function MAX_BPS() external view returns (uint256);
  function MAX_FEE_BPS() external view returns (uint256);
  function NAME() external view returns (string memory);
  function PERIOD() external view returns (uint256);
  function allocateSystemCollSharesToFeeRecipient(uint256 _shares) external;
  function authority() external view returns (address);
  function authorityInitialized() external view returns (bool);
  function borrowerOperationsAddress() external view returns (address);
  function cdpManagerAddress() external view returns (address);
  function claimFeeRecipientCollShares(uint256 _shares) external;
  function collSurplusPoolAddress() external view returns (address);
  function collateral() external view returns (address);
  function data()
    external
    view
    returns (
      uint128 observerCumuVal,
      uint128 accumulator,
      uint64 lastObserved,
      uint64 lastAccrued,
      uint128 lastObservedAverage
    );
  function decreaseSystemDebt(uint256 _amount) external;
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
  function getData()
    external
    view
    returns (IBaseTwapWeightedObserver.PackedData memory);
  function getFeeRecipientClaimableCollShares() external view returns (uint256);
  function getLatestAccumulator() external view returns (uint128);
  function getSystemCollShares() external view returns (uint256);
  function getSystemDebt() external view returns (uint256);
  function increaseSystemCollShares(uint256 _value) external;
  function increaseSystemDebt(uint256 _amount) external;
  function locked() external view returns (uint256);
  function maxFlashLoan(address token) external view returns (uint256);
  function observe() external returns (uint256);
  function setFeeBps(uint256 _newFee) external;
  function setFlashLoansPaused(bool _paused) external;
  function setValueAndUpdate(uint128 value) external;
  function sweepToken(address token, uint256 amount) external;
  function timeToAccrue() external view returns (uint64);
  function transferSystemCollShares(address _account, uint256 _shares) external;
  function transferSystemCollSharesAndLiquidatorReward(
    address _account,
    uint256 _shares,
    uint256 _liquidatorRewardShares
  ) external;
  function twapDisabled() external view returns (bool);
  function update() external;
  function valueToTrack() external view returns (uint128);
}

interface IBaseTwapWeightedObserver {
  struct PackedData {
    uint128 observerCumuVal;
    uint128 accumulator;
    uint64 lastObserved;
    uint64 lastAccrued;
    uint128 lastObservedAverage;
  }
}
