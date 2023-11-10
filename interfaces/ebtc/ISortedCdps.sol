// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface ISortedCdps {
    event NodeAdded(bytes32 _id, uint256 _NICR);
    event NodeRemoved(bytes32 _id);

    function NAME() external view returns (string memory);
    function batchRemove(bytes32[] memory _ids) external;
    function borrowerOperationsAddress() external view returns (address);
    function cdpCountOf(address owner) external view returns (uint256);
    function cdpManager() external view returns (address);
    function cdpOfOwnerByIdx(
        address owner,
        uint256 index,
        bytes32 startNodeId,
        uint256 maxNodes
    ) external view returns (bytes32, bool);
    function cdpOfOwnerByIndex(address owner, uint256 index) external view returns (bytes32);
    function contains(bytes32 _id) external view returns (bool);
    function data() external view returns (bytes32 head, bytes32 tail, uint256 size);
    function dummyId() external view returns (bytes32);
    function findInsertPosition(
        uint256 _NICR,
        bytes32 _prevId,
        bytes32 _nextId
    ) external view returns (bytes32, bytes32);
    function getAllCdpsOf(
        address owner,
        bytes32 startNodeId,
        uint256 maxNodes
    ) external view returns (bytes32[] memory, uint256, bytes32);
    function getCdpCountOf(
        address owner,
        bytes32 startNodeId,
        uint256 maxNodes
    ) external view returns (uint256, bytes32);
    function getCdpsOf(address owner) external view returns (bytes32[] memory cdps);
    function getFirst() external view returns (bytes32);
    function getLast() external view returns (bytes32);
    function getMaxSize() external view returns (uint256);
    function getNext(bytes32 _id) external view returns (bytes32);
    function getOwnerAddress(bytes32 cdpId) external pure returns (address);
    function getPrev(bytes32 _id) external view returns (bytes32);
    function getSize() external view returns (uint256);
    function insert(
        address owner,
        uint256 _NICR,
        bytes32 _prevId,
        bytes32 _nextId
    ) external returns (bytes32);
    function isEmpty() external view returns (bool);
    function isFull() external view returns (bool);
    function maxSize() external view returns (uint256);
    function nextCdpNonce() external view returns (uint256);
    function nonExistId() external pure returns (bytes32);
    function reInsert(bytes32 _id, uint256 _newNICR, bytes32 _prevId, bytes32 _nextId) external;
    function remove(bytes32 _id) external;
    function toCdpId(
        address owner,
        uint256 blockHeight,
        uint256 nonce
    ) external pure returns (bytes32);
    function validInsertPosition(
        uint256 _NICR,
        bytes32 _prevId,
        bytes32 _nextId
    ) external view returns (bool);
}
