// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.4;

interface IBalancerVault {
    struct ExitPoolRequest {
        address[] assets;
        uint256[] minAmountsOut;
        bytes userData;
        bool toInternalBalance; 
    }

   function exitPool(
        bytes32 poolId,
        address sender,
        address recipient,
        ExitPoolRequest memory request
    ) external;

    function getPoolTokens(bytes32 poolId)
        external
        view
        returns (
            address[] memory tokens,
            uint256[] memory balances,
            uint256 lastChangeBlock
        );

}