import pytest
from brownie import accounts, interface, MockFallbackCaller, PriceFeedTestnet, chain
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture
def random_safe():
    return GreatApeSafe(accounts[9].address)


@pytest.fixture
def security_multisig():
    return GreatApeSafe(registry.eth.ebtc_wallets.security_multisig)


@pytest.fixture
def techops():
    return GreatApeSafe(registry.eth.ebtc_wallets.techops_multisig)


@pytest.fixture
def treasury():
    return GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)


@pytest.fixture
def fee_recipient():
    return GreatApeSafe(registry.eth.ebtc_wallets.fee_recipient_multisig)


@pytest.fixture
def wbtc(security_multisig):
    wbtc = interface.IMintableERC20(registry.eth.assets.wbtc)
    owner = accounts.at(wbtc.owner(), force=True)
    wbtc.mint(security_multisig.address, 10000e8, {"from": owner})
    return wbtc


@pytest.fixture
def test_price_feed():
    return PriceFeedTestnet.deploy(registry.eth.ebtc.authority, {"from": accounts[0]})


@pytest.fixture
def mock_fallback_caller(security_multisig):
    security_multisig.init_ebtc()
    price = security_multisig.ebtc.ebtc_feed.fetchPrice.call()
    caller = MockFallbackCaller.deploy(price, {"from": accounts[0]})
    caller.setFallbackResponse(
        price, chain.time(), True, {"from": security_multisig.account}
    )
    return caller


@pytest.fixture
def setup_test_coll(random_safe):
    random_safe.init_ebtc()
    collateral = random_safe.ebtc.collateral
    owner = accounts.at(collateral.owner(), force=True)
    collateral.addUncappedMinter(random_safe.account, {"from": owner})
    return random_safe
