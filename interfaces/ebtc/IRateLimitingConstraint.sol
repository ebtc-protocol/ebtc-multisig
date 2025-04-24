// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IRateLimitingConstraint {
    struct MintingConfig {
        uint256 relativeCapBPS;  // Basis points of total supply allowed to mint
        uint256 absoluteCap;     // Hard cap on tokens that can be minted
        bool useAbsoluteCap;     // Flag to determine if absolute cap is used
    }

    function setMintingConfig(address _minter, MintingConfig calldata _newMintingConfig) external;
}
