// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IMultiCdpGetter {
    function cdpManager() external view returns (address);
    function getMultipleSortedCdps(
        int256 _startIdx,
        uint256 _count
    ) external view returns (MultiCdpGetter.CombinedCdpData[] memory _cdps);
    function sortedCdps() external view returns (address);
}

interface MultiCdpGetter {
    struct CombinedCdpData {
        bytes32 id;
        uint256 debt;
        uint256 coll;
        uint256 stake;
        uint256 snapshotEBTCDebt;
    }
}