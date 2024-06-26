// SPDX-License-Identifier: BUSL-1.1
pragma solidity >=0.7.5;

interface IUniswapV3SwapCallback {
  function uniswapV3SwapCallback(
    int amount0Delta,
    int amount1Delta,
    bytes calldata data
  ) external;
}