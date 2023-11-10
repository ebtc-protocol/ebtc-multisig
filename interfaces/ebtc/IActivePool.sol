// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IActivePool {
    event ActivePoolEBTCDebtUpdated(uint256 _EBTCDebt);
    event AuthorityUpdated(address indexed user, address indexed newAuthority);
    event CollSharesTransferred(address indexed _to, uint256 _amount);
    event EBTCBalanceUpdated(uint256 _newBalance);
    event ETHBalanceUpdated(uint256 _newBalance);
    event FeeRecipientAddressChanged(address indexed _feeRecipientAddress);
    event FeeRecipientClaimableCollSharesDecreased(uint256 _coll, uint256 _fee);
    event FeeRecipientClaimableCollSharesIncreased(uint256 _coll, uint256 _fee);
    event FlashFeeSet(address indexed _setter, uint256 _oldFee, uint256 _newFee);
    event FlashLoanSuccess(
        address indexed _receiver,
        address indexed _token,
        uint256 _amount,
        uint256 _fee
    );
    event FlashLoansPaused(address indexed _setter, bool _paused);
    event MaxFlashFeeSet(address indexed _setter, uint256 _oldMaxFee, uint256 _newMaxFee);
    event SweepTokenSuccess(address indexed _token, uint256 _amount, address indexed _recipient);
    event SystemCollSharesUpdated(uint256 _coll);

    function DECIMAL_PRECISION() external view returns (uint256);
    function FLASH_SUCCESS_VALUE() external view returns (bytes32);
    function MAX_BPS() external view returns (uint256);
    function MAX_FEE_BPS() external view returns (uint256);
    function NAME() external view returns (string memory);
    function allocateSystemCollSharesToFeeRecipient(uint256 _shares) external;
    function authority() external view returns (address);
    function authorityInitialized() external view returns (bool);
    function borrowerOperationsAddress() external view returns (address);
    function cdpManagerAddress() external view returns (address);
    function claimFeeRecipientCollShares(uint256 _shares) external;
    function collSurplusPoolAddress() external view returns (address);
    function collateral() external view returns (address);
    function decreaseSystemDebt(uint256 _amount) external;
    function feeBps() external view returns (uint16);
    function feeRecipientAddress() external view returns (address);
    function flashFee(address token, uint256 amount) external view returns (uint256);
    function flashLoan(
        address receiver,
        address token,
        uint256 amount,
        bytes memory data
    ) external returns (bool);
    function flashLoansPaused() external view returns (bool);
    function getFeeRecipientClaimableCollShares() external view returns (uint256);
    function getSystemCollShares() external view returns (uint256);
    function getSystemDebt() external view returns (uint256);
    function increaseSystemCollShares(uint256 _value) external;
    function increaseSystemDebt(uint256 _amount) external;
    function locked() external view returns (uint256);
    function maxFlashLoan(address token) external view returns (uint256);
    function setAuthority(address newAuthority) external;
    function setFeeBps(uint256 _newFee) external;
    function setFeeRecipientAddress(address _feeRecipientAddress) external;
    function setFlashLoansPaused(bool _paused) external;
    function sweepToken(address token, uint256 amount) external;
    function transferSystemCollShares(address _account, uint256 _shares) external;
    function transferSystemCollSharesAndLiquidatorReward(
        address _account,
        uint256 _shares,
        uint256 _liquidatorRewardShares
    ) external;
}
