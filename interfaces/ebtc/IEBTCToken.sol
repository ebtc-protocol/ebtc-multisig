// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEBTCToken {
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event Transfer(address indexed from, address indexed to, uint256 value);

    function DOMAIN_SEPARATOR() external view returns (bytes32);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function authority() external view returns (address);
    function authorityInitialized() external view returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function borrowerOperationsAddress() external view returns (address);
    function burn(uint256 _amount) external;
    function burn(address _account, uint256 _amount) external;
    function cdpManagerAddress() external view returns (address);
    function decimals() external pure returns (uint8);
    function decreaseAllowance(address spender, uint256 subtractedValue) external returns (bool);
    function domainSeparator() external view returns (bytes32);
    function increaseAllowance(address spender, uint256 addedValue) external returns (bool);
    function increasePermitNonce() external returns (uint256);
    function mint(address _account, uint256 _amount) external;
    function name() external pure returns (string memory);
    function nonces(address owner) external view returns (uint256);
    function permit(
        address owner,
        address spender,
        uint256 amount,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;
    function permitTypeHash() external pure returns (bytes32);
    function setAuthority(address newAuthority) external;
    function symbol() external pure returns (string memory);
    function totalSupply() external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function version() external pure returns (string memory);
}
