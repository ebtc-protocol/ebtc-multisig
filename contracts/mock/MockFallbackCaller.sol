// SPDX-License-Identifier: MIT
// File: Interfaces/IFallbackCaller.sol

pragma solidity 0.8.17;

interface IFallbackCaller {
  // --- Events ---
  event FallbackTimeOutChanged(uint256 _oldTimeOut, uint256 _newTimeOut);

  // --- Function External View ---

  // NOTE: The fallback oracle must always return its answer scaled to 18 decimals where applicable
  //       The system will assume an 18 decimal response for efficiency.
  function getFallbackResponse() external view returns (uint256, uint256, bool);

  // NOTE: this returns the timeout window interval for the fallback oracle instead
  // of storing in the `PriceFeed` contract is retrieve for the `FallbackCaller`
  function fallbackTimeout() external view returns (uint256);

  // --- Function External Setter ---

  function setFallbackTimeout(uint256 newFallbackTimeout) external;
}
// File: contracts/MockFallbackCaller.sol

pragma solidity 0.8.17;

contract MockFallbackCaller is IFallbackCaller {
  uint256 public _answer;
  uint256 public _timestampRetrieved;
  uint256 public _fallbackTimeout = 90000; // NOTE: MAYBE BEST TO CUSTOMIZE
  bool public _success;
  uint256 public _initAnswer;

  bool public getFallbackResponseRevert;
  bool public fallbackTimeoutRevert;

  constructor(uint256 answer) {
    _initAnswer = answer;
  }

  function setGetFallbackResponseRevert() external {
    getFallbackResponseRevert = !getFallbackResponseRevert;
  }

  function setFallbackTimeoutRevert() external {
    fallbackTimeoutRevert = !fallbackTimeoutRevert;
  }

  function setFallbackResponse(
    uint256 answer,
    uint256 timestampRetrieved,
    bool success
  ) external {
    _answer = answer;
    _timestampRetrieved = timestampRetrieved;
    _success = success;
  }

  function setFallbackTimeout(uint256 newFallbackTimeout) external {
    uint256 oldTimeOut = _fallbackTimeout;
    _fallbackTimeout = newFallbackTimeout;
    emit FallbackTimeOutChanged(oldTimeOut, newFallbackTimeout);
  }

  function getFallbackResponse()
    external
    view
    returns (uint256, uint256, bool)
  {
    if (getFallbackResponseRevert) {
      require(1 == 0, "getFallbackResponse reverted");
    }
    return (_answer, _timestampRetrieved, _success);
  }

  function fallbackTimeout() external view returns (uint256) {
    if (fallbackTimeoutRevert) {
      require(1 == 0, "fallbackTimeout reverted");
    }
    return _fallbackTimeout;
  }
}
