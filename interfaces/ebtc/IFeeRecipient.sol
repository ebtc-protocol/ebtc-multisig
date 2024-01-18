// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IFeeRecipient {
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event SweepTokenSuccess(address indexed _token, uint256 _amount, address indexed _recipient);

    function NAME() external view returns (string memory);
    function authority() external view returns (address);
    function authorityInitialized() external view returns (bool);
    function owner() external view returns (address);
    function renounceOwnership() external;
    function setAuthority(address newAuthority) external;
    function sweepToken(address token, uint256 amount) external;
    function transferOwnership(address newOwner) external;
}
