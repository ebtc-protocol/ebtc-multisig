// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface ICollSurplusPool {
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event CollSharesTransferred(address indexed _to, uint256 _amount);
    event SurplusCollSharesUpdated(address indexed _account, uint256 _newBalance);
    event SweepTokenSuccess(address indexed _token, uint256 _amount, address indexed _recipient);

    function NAME() external view returns (string memory);
    function activePoolAddress() external view returns (address);
    function authority() external view returns (address);
    function authorityInitialized() external view returns (bool);
    function borrowerOperationsAddress() external view returns (address);
    function cdpManagerAddress() external view returns (address);
    function claimSurplusCollShares(address _account) external;
    function collateral() external view returns (address);
    function feeRecipientAddress() external view returns (address);
    function getSurplusCollShares(address _account) external view returns (uint256);
    function getTotalSurplusCollShares() external view returns (uint256);
    function increaseSurplusCollShares(address _account, uint256 _amount) external;
    function increaseTotalSurplusCollShares(uint256 _value) external;
    function locked() external view returns (uint256);
    function setAuthority(address newAuthority) external;
    function sweepToken(address token, uint256 amount) external;
}
