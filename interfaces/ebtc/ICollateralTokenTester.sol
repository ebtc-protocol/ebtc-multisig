// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface ICollateralTokenTester {
  event Approval(address indexed owner, address indexed spender, uint256 value);
  event Deposit(address indexed dst, uint256 wad, uint256 _share);
  event MintCapSet(uint256 indexed newCap);
  event MintCooldownSet(uint256 indexed newCooldown);
  event OwnershipTransferred(
    address indexed previousOwner,
    address indexed newOwner
  );
  event Transfer(address indexed from, address indexed to, uint256 value);
  event TransferShares(
    address indexed from,
    address indexed to,
    uint256 sharesValue
  );
  event UncappedMinterAdded(address indexed account);
  event UncappedMinterRemoved(address indexed account);
  event Withdrawal(address indexed src, uint256 wad, uint256 _share);

  function addUncappedMinter(address account) external;

  function allowance(address, address) external view returns (uint256);

  function approve(address guy, uint256 wad) external returns (bool);

  function authority() external view returns (address);

  function balanceOf(address _usr) external view returns (uint256);

  function decimals() external view returns (uint8);

  function decreaseAllowance(
    address spender,
    uint256 subtractedValue
  ) external returns (bool);

  function deposit() external payable;

  function feeRecipientAddress() external view returns (address);

  function forceDeposit(uint256 ethToDeposit) external;

  function getBeaconSpec()
    external
    view
    returns (uint64, uint64, uint64, uint64);

  function getEthPerShare() external view returns (uint256);

  function getOracle() external view returns (address);

  function getPooledEthByShares(
    uint256 _sharesAmount
  ) external view returns (uint256);

  function getSharesByPooledEth(
    uint256 _ethAmount
  ) external view returns (uint256);

  function increaseAllowance(
    address spender,
    uint256 addedValue
  ) external returns (bool);

  function isUncappedMinter(address) external view returns (bool);

  function lastMintTime(address) external view returns (uint256);

  function mintCap() external view returns (uint256);

  function mintCooldown() external view returns (uint256);

  function name() external view returns (string memory);

  function nonStandardSetApproval(
    address owner,
    address guy,
    uint256 wad
  ) external returns (bool);

  function owner() external view returns (address);

  function removeUncappedMinter(address account) external;

  function renounceOwnership() external;

  function setBeaconSpec(
    uint64 _epochsPerFrame,
    uint64 _slotsPerEpoch,
    uint64 _secondsPerSlot
  ) external;

  function setEthPerShare(uint256 _ePerS) external;

  function setMintCap(uint256 newCap) external;

  function setMintCooldown(uint256 newCooldown) external;

  function sharesOf(address _account) external view returns (uint256);

  function symbol() external view returns (string memory);

  function totalSupply() external view returns (uint256);

  function transfer(address dst, uint256 wad) external returns (bool);

  function transferFrom(
    address src,
    address dst,
    uint256 wad
  ) external returns (bool);

  function transferOwnership(address newOwner) external;

  function transferShares(
    address _recipient,
    uint256 _sharesAmount
  ) external returns (uint256);

  function withdraw(uint256 wad) external;

  receive() external payable;
}
