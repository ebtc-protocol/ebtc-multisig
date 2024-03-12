import pytest
from helpers.addresses import registry
from brownie import interface


@pytest.fixture
def liq(treasury):
    return treasury.contract(registry.eth.assets.liq)


@pytest.fixture
def wbtc(treasury):
    return treasury.contract(registry.eth.assets.wbtc)


@pytest.fixture
def univ3_pool(treasury):
    return interface.IUniswapV3Pool(
        registry.eth.uniswap.v3pool_wbtc_badger, owner=treasury.account
    )
