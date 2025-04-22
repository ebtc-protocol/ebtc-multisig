// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEscrow {
    function claimProfit() external;
    function claimTokens(address token, uint256 amount) external;
}
