// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IGovernor {
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event CapabilityBurned(address indexed target, bytes4 indexed functionSig);
    event OwnershipTransferred(address indexed user, address indexed newOwner);
    event PublicCapabilityUpdated(address indexed target, bytes4 indexed functionSig, bool enabled);
    event RoleCapabilityUpdated(
        uint8 indexed role,
        address indexed target,
        bytes4 indexed functionSig,
        bool enabled
    );
    event RoleNameSet(uint8 indexed role, string indexed name);
    event UserRoleUpdated(address indexed user, uint8 indexed role, bool enabled);

    function authority() external view returns (address);
    function burnCapability(address target, bytes4 functionSig) external;
    function canCall(address user, address target, bytes4 functionSig) external view returns (bool);
    function capabilityFlag(address, bytes4) external view returns (uint8);
    function doesRoleHaveCapability(
        uint8 role,
        address target,
        bytes4 functionSig
    ) external view returns (bool);
    function doesUserHaveRole(address user, uint8 role) external view returns (bool);
    function getByteMapFromRoles(uint8[] memory roleIds) external pure returns (bytes32);
    function getEnabledFunctionsInTarget(
        address _target
    ) external view returns (bytes4[] memory _funcs);
    function getRoleName(uint8 role) external view returns (string memory roleName);
    function getRolesForUser(address user) external view returns (uint8[] memory rolesForUser);
    function getRolesFromByteMap(bytes32 byteMap) external pure returns (uint8[] memory roleIds);
    function getRolesWithCapability(address, bytes4) external view returns (bytes32);
    function getUserRoles(address) external view returns (bytes32);
    function getUsersByRole(uint8 role) external view returns (address[] memory usersWithRole);
    function isPublicCapability(address target, bytes4 functionSig) external view returns (bool);
    function owner() external view returns (address);
    function setAuthority(address newAuthority) external;
    function setPublicCapability(address target, bytes4 functionSig, bool enabled) external;
    function setRoleCapability(
        uint8 role,
        address target,
        bytes4 functionSig,
        bool enabled
    ) external;
    function setRoleName(uint8 role, string memory roleName) external;
    function setUserRole(address user, uint8 role, bool enabled) external;
    function transferOwnership(address newOwner) external;
}
