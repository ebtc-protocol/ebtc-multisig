<div align="center" style="margin-bottom:15px">
  <img height=80 src="https://www.ebtc.finance/_next/image?url=%2Fassets%2Fmain-logo.png&w=640&q=75">
</div>

# eBTC Multisig

This repo is where all EVM multisig operations take place for the eBTC Protocol.
It relies heavily on [`ganache-cli`](https://docs.nethereum.com/en/latest/ethereum-and-clients/ganache-cli/), [`eth-brownie`](https://github.com/eth-brownie/brownie), [`gnosis-py`](https://github.com/gnosis/gnosis-py) and a custom developed evolution of [`ape-safe`](https://github.com/banteg/ape-safe); [`great-ape-safe`](https://github.com/gosuto-ai/great-ape-safe).

[Learn more](https://docs.ebtc.finance/ebtc/) about the eBTC Protocol and checkout its [website](https://ebtc.finance/).

eBTC was built by the Badger DAO. Read more about the Badger DAO and its community at https://badger.com/.

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

## eBTC Council Signers

To be defined

## Techops Signers

To be defined
