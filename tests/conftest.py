import pytest
from brownie import accounts
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture
def random_safe():
    return GreatApeSafe(accounts[9].address)


@pytest.fixture
def ecosystem():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.ecosystem_multisig)


@pytest.fixture
def council():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.council_multisig)


@pytest.fixture
def techops():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.techops_multisig)


@pytest.fixture
def fee_recipient():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.fee_recipient_multisig)
