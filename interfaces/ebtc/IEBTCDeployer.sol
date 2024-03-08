// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IEBTCDeployer {
  error ErrorCreatingContract();
  error ErrorCreatingProxy();
  error TargetAlreadyExists();
  event ContractDeployed(
    address indexed contractAddress,
    string contractName,
    bytes32 salt
  );
  event OwnershipTransferred(
    address indexed previousOwner,
    address indexed newOwner
  );

  function ACTIVE_POOL() external view returns (string memory);
  function AUTHORITY() external view returns (string memory);
  function BORROWER_OPERATIONS() external view returns (string memory);
  function CDP_MANAGER() external view returns (string memory);
  function COLL_SURPLUS_POOL() external view returns (string memory);
  function EBTC_FEED() external view returns (string memory);
  function EBTC_TOKEN() external view returns (string memory);
  function FEE_RECIPIENT() external view returns (string memory);
  function HINT_HELPERS() external view returns (string memory);
  function LIQUIDATION_LIBRARY() external view returns (string memory);
  function MULTI_CDP_GETTER() external view returns (string memory);
  function PRICE_FEED() external view returns (string memory);
  function SORTED_CDPS() external view returns (string memory);
  function addressOf(string memory _saltString) external view returns (address);
  function addressOfSalt(bytes32 _salt) external view returns (address);
  function deploy(
    string memory _saltString,
    bytes memory _creationCode
  ) external returns (address deployedAddress);
  function deployWithCreationCode(
    string memory _saltString,
    bytes memory creationCode
  ) external returns (address);
  function deployWithCreationCodeAndConstructorArgs(
    string memory _saltString,
    bytes memory creationCode,
    bytes memory constructionArgs
  ) external returns (address);
  function getFutureEbtcAddresses()
    external
    view
    returns (EBTCDeployer.EbtcAddresses memory);
  function name() external view returns (string memory);
  function owner() external view returns (address);
  function renounceOwnership() external;
  function transferOwnership(address newOwner) external;
}

interface EBTCDeployer {
  struct EbtcAddresses {
    address authorityAddress;
    address liquidationLibraryAddress;
    address cdpManagerAddress;
    address borrowerOperationsAddress;
    address priceFeedAddress;
    address sortedCdpsAddress;
    address activePoolAddress;
    address collSurplusPoolAddress;
    address hintHelpersAddress;
    address ebtcTokenAddress;
    address feeRecipientAddress;
    address multiCdpGetterAddress;
    address ebtcFeedAddress;
  }
}
