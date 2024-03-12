import pytest
from brownie import accounts, interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie_tokens import MintableForkToken


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture
def random_safe():
    return GreatApeSafe(accounts[9].address)


@pytest.fixture
def security_multisig():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.security_multisig)


@pytest.fixture
def techops():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.techops_multisig)


@pytest.fixture
def treasury():
    return GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)


@pytest.fixture
def fee_recipient():
    return GreatApeSafe(registry.sepolia.ebtc_wallets.fee_recipient_multisig)


@pytest.fixture
def wbtc(security_multisig):
    return interface.IMintableERC20(
        registry.sepolia.assets.wbtc, owner=security_multisig.account
    )


@pytest.fixture
def test_price_feed():
    return registry.sepolia.ebtc.test_contracts.test_price_feed


@pytest.fixture
def mock_fallback_caller():
    return interface.IMockFallbackCaller(
        registry.sepolia.ebtc.test_contracts.mock_fallback_caller
    )


@pytest.fixture
def setup_test_coll(random_safe):
    random_safe.init_ebtc()
    collateral = random_safe.ebtc.collateral
    owner = accounts.at(collateral.owner(), force=True)
    collateral.addUncappedMinter(random_safe.account, {"from": owner})
    return random_safe
