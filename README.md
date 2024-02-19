<div align="center" style="margin-bottom:15px">
  <img height=80 src="https://www.ebtc.finance/_next/image?url=%2Fassets%2Fmain-logo.png&w=640&q=75">
</div>

# eBTC Multisig

This repo is where all EVM multisig operations take place for the eBTC Protocol.
It relies heavily on [`ganache-cli`](https://docs.nethereum.com/en/latest/ethereum-and-clients/ganache-cli/), [`eth-brownie`](https://github.com/eth-brownie/brownie), [`gnosis-py`](https://github.com/gnosis/gnosis-py) and a custom developed evolution of [`ape-safe`](https://github.com/banteg/ape-safe); [`great-ape-safe`](https://github.com/gosuto-ai/great-ape-safe).

[Learn more](https://docs.ebtc.finance/ebtc/) about the eBTC Protocol and checkout its [website](https://ebtc.finance/).

eBTC was built by the Badger DAO. Read more about the Badger DAO and its community at https://badger.com/.

## Table of Contents
- [Installation](#installation)
  - [OpenSSL Deprecation (macOS)](#openssl-deprecation-macos)
  - [Arm Chipset Architecture (M1/M2)](#arm-chipset-architecture-m1m2)
- [Uninstall](#uninstall)
- [Testing](#running-greatapesafe-tests)
- [Multisig Addresses](#multisig-addresses)
- [eBTC Governance Operations Instructions](#ebtc-governance-operations-instructions)
  - [Low Sec Governance Operations](#low-sec-governance-operations)
  - [High Sec Governance Operations](#high-sec-governance-operations)
  - [Timelock Salt](#timelock-salt)
  - [EMERGENCY: Pausing Operations](#emergency-pausing-operations)
- [eBTC Governance Parameters Cheatsheet](#ebtc-governance-parameters-cheatsheet)

## Installation

The recommended installation tool for this repository is [`poetry`](https://python-poetry.org/docs/):

```
poetry install
```

In case of missing python versions, and depending on your setup, you might want to have a look at [`pyenv`](https://github.com/pyenv/pyenv).

Enter `poetry`'s virtual environment through `poetry shell`. You should now be able to run `brownie` from within this virtual environment. Type `exit` or ctrl-D to leave the environment.

Alternatively, you could use the `requirements.txt` (or `requirements-dev.txt` if you want to include testing packages) via `pip`: `pip install -r requirements.txt`.

### OpenSSL Deprecation (macOS)

The installation process might run into some OpenSSL issues (`fatal error: openssl/aes.h: No such file or directory`). Please see [the note on OpenSSL in the Vyper docs](https://docs.vyperlang.org/en/v0.1.0-beta.17/installing-vyper.html#installation) or [this related issue](https://github.com/ethereum/pyethereum/issues/292) in order to fix it.

### Arm Chipset Architecture (M1/M2)

MacBooks with arm chipsets have some additional challenges [[source]](https://github.com/psf/black/issues/2524).

In our case, since `eth-brownie` locks on this borked `regex==2021.10.8` [[source]](https://github.com/eth-brownie/brownie/blob/1eeb5b3a42509f14cdd2d269c5629cfeaf850fcc/requirements.txt#L193), we have to override `regex` after `poetry`'s lock. Go into the virtual environment created by `poetry` and install the next version of `regex`:

```
poetry shell
pip install regex==2021.10.21
```

You can ignore the following warning:

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
eth-brownie 1.17.0 requires regex==2021.10.8, but you have regex 2021.10.21 which is incompatible.
```

### module 'rlp' has no attribute 'Serializable'

Another corner case you may encountered while trying to run `brownie console` or scripts is `AttributeError: module 'rlp' has no attribute 'Serializable'`. Solution can be found [here](https://lightrun.com/answers/apeworx-ape-docker-startup-error-attributeerror-module-rlp-has-no-attribute-serializable).

```
poetry shell
pip uninstall rlp --yes && pip install rlp==3.0.0
```

Warning can be ignored regarding pip's dependency resolver conflicts.

## Uninstall

Delete the virtual environment as such:

```
rm -rf `poetry env info -p`
```

## Running GreatApeSafe Tests

1. Run the following command to install the Sepolia testnet. Don't forget to change the `{ALCHEMY_SEPOLIA_RPC_KEY}` for your Sepolia Alchemy RPC key:

```
brownie networks add Ethereum sepolia host=https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_SEPOLIA_RPC_KEY} chainid=11155111 explorer=https://api-sepolia.etherscan.io/api
```

2. Run the following command to install the Sepolia Fork network:

```
brownie networks import network-config.yaml
```

3. Use the following command to run the tests:

```
brownie test --network sepolia-fork
```

## Multisig Addresses

To be deployed

## eBTC Governance Operations Instructions

### Low Sec Governance Operations

These operations are executed by the Low Sec TechOps multisig with a Low Sec Timelock (2 day delay). Scripts interacting with the Low Sec Timelock need to be run twice (**with the exact same parameters**) in order to fully execute each transaction: Once to shcedule the transaction and antoher time, once the delay time has elapsed, to execute it. If the parameters don't match when running the script the second time, the script will recognize it as a new operation and new "schedule" transaction will be posted instead. You can verify the parameters used when scheduling the scheduled transaction within the Timelock Transparency Dashboard (WIP).

1. **Set Staking Reward Split for CDPManager Contract**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_staking_reward_split <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_staking_reward_split 5000`

2. **Set Redemption Fee Floor for CDPManager Contract**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_redemption_fee_floor <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_redemption_fee_floor 100`

3. **Set Minute Decay Factor for CDPManager Contract**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_minute_decay_factor <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_minute_decay_factor 900`

4. **Set Minute Beta for CDPManager Contract**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_beta <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_beta 2000`

5. **Set Redemptions Paused for CDPManager Contract**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_redemptions_paused <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_redemptions_paused False`

6. **Set Grace Period for CDPManager Contract**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_grace_period <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_grace_period 140506`

7. **Set FallBack Caller for PriceFeed Contract**
   ```bash
   brownie run scripts/ebtc_governance.py priceFeed_set_fallback_caller <address>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py priceFeed_set_fallback_caller 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1`

8. **Set Fee BPS for ActivePool Contract**
   ```bash
   brownie run scripts/ebtc_governance.py activePool_set_fee_bps <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py activePool_set_fee_bps 3000`

9. **Set Fee BPS for BorrowerOperations Contract**
   ```bash
   brownie run scripts/ebtc_governance.py borrowerOperations_set_fee_bps <value>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py borrowerOperations_set_fee_bps 3000`

10. **Set Secondary Oracle for EBTCFeed Contract**
   ```bash
   brownie run scripts/ebtc_governance.py ebtcFeed_set_secondary_oracle <address>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py ebtcFeed_set_secondary_oracle 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1`

### High Sec Governance Operations

These operations are executed by the High Sec TechOps multisig with a Low Sec Timelock (7 day delay). Scripts interacting with the High Sec Timelock need to be run twice (**with the exact same parameters**) in order to fully execute each transaction: Once to shcedule the transaction and antoher time, once the delay time has elapsed, to execute it. If the parameters don't match when running the script the second time, the script will recognize it as a new operation and new "schedule" transaction will be posted instead. You can verify the parameters used when scheduling the scheduled transaction within the Timelock Transparency Dashboard (WIP).

1. **Set Role Name for Authority Contract**
   ```bash
   brownie run scripts/ebtc_governance.py authority_set_role_name <role> <name>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py authority_set_role_name 1 "example role"`

2. **Set User Role for Authority Contract**
   ```bash
   brownie run scripts/ebtc_governance.py authority_set_user_role <user> <role> <enabled>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py authority_set_user_role 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1 1 True`

3. **Set Role Capability for Authority Contract**
   ```bash
   brownie run scripts/ebtc_governance.py authority_set_role_capability <role> <target_address> <signature> <enabled>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py authority_set_role_capability 1 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1 0x12345678`

4. **Set Public Capability for Authority Contract**
   ```bash
   brownie run scripts/ebtc_governance.py authority_set_public_capability <target_address> <signature> <enabled>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py authority_set_public_capability 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1 0x12345678 False`

5. **Burn Capability for Authority Contract**
   ```bash
   brownie run scripts/ebtc_governance.py authority_burn_capability <target_address> <signature>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py authority_burn_capability 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1 0x12345678`

6. **Set Authority for Authority Contract**
   ```bash
   brownie run scripts/ebtc_governance.py authority_set_authority <address>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py authority_set_authority 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1`

7. **Set Primary Oracle for EBTCFeed Contract**
   ```bash
   brownie run scripts/ebtc_governance.py ebtcFeed_set_primary_oracle <address>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py ebtcFeed_set_primary_oracle 0xa1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1`

### Timelock Salt
All Timelock scripts accept an optional *salt* at the end of their parameter list, a unique 32-byte identifier that allows for the distinction of transactions. This is especially useful for queuing transactions that are identical in contract, changes, and values to previous ones. To ensure the correct execution of a scheduled transaction that includes a salt, this same salt must be repeated during the execution phase.

*Example:* `brownie run scripts/ebtc_governance.py borrowerOperations_set_fee_bps 3000 0x0000000000000000000000000000000000000000000000000000000000000001`

### EMERGENCY: Pausing Operations

Operations within the EMERGENCY section are meant to be executed directly without the timelock process.

1. **Pause or Unpause Redemptions for CDPManager Contract from TechOps Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_redemptions_paused_techops <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_redemptions_paused_techops True`

2. **Pause or Unpause Redemptions for CDPManager Contract from Security Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py cdpManager_set_redemptions_paused_security <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py cdpManager_set_redemptions_paused_security True`

3. **Pause or Unpause Flash Loans for ActivePool Contract from TechOps Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py activePool_set_flash_loans_paused_techops <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py activePool_set_flash_loans_paused_techops True`

4. **Pause or Unpause Flash Loans for ActivePool Contract from Security Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py activePool_set_flash_loans_paused_security <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py activePool_set_flash_loans_paused_security True`

5. **Pause or Unpause Flash Loans for BorrowerOperations Contract from TechOps Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py borrowerOperations_set_flash_loans_paused_techops <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py borrowerOperations_set_flash_loans_paused_techops True`

6. **Pause or Unpause Flash Loans for BorrowerOperations Contract from Security Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py borrowerOperations_set_flash_loans_paused_security <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py borrowerOperations_set_flash_loans_paused_security True`

7. **Pause or Unpause Flash Loans for BorrowerOperations and ActivePool Contract from TechOps Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py pause_flashloans_techops <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py pause_flashloans_techops True`

8. **Pause or Unpause Flash Loans for BorrowerOperations and ActivePool Contract from Security Multisig**
   ```bash
   brownie run scripts/ebtc_governance.py pause_flashloans_security <pause>
   ```
   *Example:* `brownie run scripts/ebtc_governance.py pause_flashloans_security True`


Please note that the specific `<value>`, `<role>`, `<address>`, `<target_address>`, `<signature>`, `<name>`, and `<pause>` should be replaced with the actual parameters you wish to use for each operation. The examples provided are meant to give you an idea of how to structure your commands for the CLI.

In addition, it must also be noted that only delegated accounts with posting access to the multisigs in matter will be able to post these transactions. Delegation can be granted to any EOA from one of the signers via the following [tool](https://gnosis-delegator.badger.com/). Remember that posting the transactions is not enough, it must also be executed via its respective multisig for it to be loaded into the Timelock.

## eBTC Governance Parameters Cheatsheet
The section below provides a concise overview and a table detailing the adjustable numerical parameters within the eBTC system. This guide aims to facilitate the execution and review of changes. The table includes essential information such as the parameter name, its base value, both the upper and lower bounds that define the limits within which these parameters can be adjusted and an example for each. Additional notes are provided to give context or specific details relevant to each parameter.

Parameter | Base (conversion from decimal) | Upper Bound | Lower Bound | Example | Notes
----------|--------------------------------|-------------|-------------|---------|------
Staking Reward Split | 10_000 | 10_000 (100%) | 0  | 5_000 (50%) | Protocol Yield Share: Percentage of collateral's yield taken as fee
Redemption Fee Floor | 1e18 | 1e18 (100%) | 5e15 (0.5%) | 1e16 (1%) | Determines the minimum redemption fee possible
Minute Decay Factor (Delta) | 1 | 999999999999999999 | 1 | 999037758833783000 (720 min) | 12 hr (720 min) halflife -> d = (1/2)^(1/720)
Beta | 1 | - | - (⚠️ NOT ZERO) | 2 (Initial) | Corresponds to 1 / ALPHA, determines the fee increase steepness
Grace Period | 1 | - | 900 | 1200 (20 minutes) | Length of recovery mode's Grace Period's duration
Active Pool FL Fee | 10_000 | 1_000 (10%) | 0 | 3 (0.03%) | Determines the fee charged on a Flashloan
Borrower Operations FL Fee | 10_000 | 1_000 (10%) | 0 | 3 (0.03%) | Determines the fee charged on a Flashloan

This cheat sheet serves as a handy reference for anyone involved in the governance of eBTC, from developers and contributors to users interested in understanding the parameters that shape the protocol's functionality and security. 