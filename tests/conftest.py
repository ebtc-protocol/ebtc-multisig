import pytest
from brownie import accounts, interface, MockFallbackCaller, PriceFeedTestnet, chain
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from helpers.constants import AddressZero


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
def canceller(security_multisig):
    security_multisig.init_ebtc()
    lowsec_timelock = security_multisig.ebtc.lowsec_timelock
    highsec_timelock = security_multisig.ebtc.highsec_timelock

    # Grant CANCELLER_ROLE to account on both timelocks
    role = lowsec_timelock.CANCELLER_ROLE()
    canceller = accounts[8].address
    lowsec_timelock.grantRole(
        role,
        canceller,
        {"from": accounts.at(lowsec_timelock.address, force=True)},
    )
    highsec_timelock.grantRole(
        role,
        canceller,
        {"from": accounts.at(highsec_timelock.address, force=True)},
    )
    return GreatApeSafe(canceller)


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
    assert random_safe.account.balance() > 0

    collateral = random_safe.ebtc.collateral
    # Depositing ETH into stETH via submit
    collateral.submit(
        AddressZero,
        {"value": random_safe.account.balance(), "from": random_safe.account},
    )
    assert collateral.balanceOf(random_safe) > 0

    return random_safe


@pytest.fixture
def setup_base_cdp(random_safe):
    # The system requires at least on CDP to be open, so we open one here
    # in order to test closing of others. This CDP will basically act as the base CDP
    random_safe.init_ebtc()
    random_safe.ebtc.open_cdp(5e18, 160e16)
