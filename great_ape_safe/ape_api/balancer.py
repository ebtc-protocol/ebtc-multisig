from decimal import Decimal
import requests
import json

from brownie import ZERO_ADDRESS, Contract
from helpers.addresses import registry
from web3 import Web3
import eth_abi

from great_ape_safe.ape_api.helpers.balancer.weighted_math import (
    calc_bpt_out_given_exact_tokens_in,
    calc_tokens_out_given_exact_bpt_in
)

from great_ape_safe.ape_api.helpers.balancer.queries \
    import pool_tokens_query


class Balancer():
    def __init__(self, safe):
        self.safe = safe
        # contracts
        self.vault = safe.contract(registry.eth.balancer.vault)
        self.gauge_factory = safe.contract(registry.eth.balancer.gauge_factory)
        # parameters
        self.max_slippage = Decimal(0.02)
        self.pool_query_liquidity_threshold = Decimal(10_000) # USD
        self.dusty = 0.99
        # misc
        self.subgraph = 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2'


    def get_pool_data(self, update_cache=False):
        # no on-chain registry, so pool data is cached locally
        # used for pool look up based on underlyings
        # `update_cache` to query subgraph for new pools above liquidity threshold
        if update_cache:
            res = requests.post(self.subgraph, json={'query': pool_tokens_query}).json()
            pool_data = res['data']['pools']
            pool_data_filtered = [x for x in pool_data if
                            Decimal(x['totalLiquidity']) > self.pool_query_liquidity_threshold]
            with open('great_ape_safe/ape_api/helpers/balancer/pools.json','w') as f:
                json.dump(pool_data_filtered, f)
            return pool_data_filtered

        with open('great_ape_safe/ape_api/helpers/balancer/pools.json') as f:
            data = json.load(f)
            return data


    def find_pool_for_underlyings(self, underlyings):
        # find pools with matching underlyings from cached pool data
        pool_data = self.get_pool_data()
        match = None
        for pool in pool_data:
            tokens = [Web3.toChecksumAddress(x['address']) for x in pool['tokens']]
            if underlyings == tokens:
                if match:
                    raise Exception('multiple matching pools exist, provide `pool_id`')
                match = pool['id']
        if not match:
            raise Exception('no pool found for underlyings')
        return match


    def order_tokens(self, underlyings, mantissas):
        # helper function to order tokens/amounts numerically
        tokens = dict(zip(underlyings, mantissas))
        sorted_tokens = dict(sorted(tokens.items()))
        return zip(*sorted_tokens.items())


    def deposit_and_stake(
        self, underlyings, mantissas, pool=None, is_eth=False, stake=True, destination=None
    ):
        # given underlyings and their amounts, deposit and stake `underlyings`
        destination = self.safe.address if not destination else destination

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#token-ordering
        underlyings, mantissas = \
            self.order_tokens([x.address for x in underlyings], mantissas)

        if pool:
            pool_id = pool.getPoolId()
        else:
            pool_id = self.find_pool_for_underlyings(list(underlyings))
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])

        tokens, reserves, _ = self.vault.getPoolTokens(pool_id)

        bpt_out = calc_bpt_out_given_exact_tokens_in(pool, reserves, mantissas)
        exact_tokens_for_bpt_enum = 1
        min_bpt_out = int(bpt_out * (1 - self.max_slippage))

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#encoding-how-do-i-encode
        data_encoded = eth_abi.encode_abi(
            ['uint256', 'uint256[]', 'uint256'],
            [exact_tokens_for_bpt_enum, mantissas, min_bpt_out]
            )

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins#arguments-explained
        request = (
            tokens,
            mantissas,
            data_encoded,
            is_eth
        )

        for i, token in enumerate(tokens):
            token = self.safe.contract(token)
            token.approve(self.vault, mantissas[i])

        pool_reciepient = self.safe if stake else destination
        balance_before = pool.balanceOf(pool_reciepient)

        # https://dev.balancer.fi/resources/joins-and-exits/pool-joins
        self.vault.joinPool(
            pool_id, self.safe, pool_reciepient, request
        )

        balance_delta = pool.balanceOf(pool_reciepient) - balance_before
        assert balance_delta > 0

        if stake:
            gauge_address = self.gauge_factory.getPoolGauge(pool)

            if gauge_address == ZERO_ADDRESS:
                raise Exception(f'no gauge for {pool_id}')

            gauge = self.safe.contract(gauge_address)
            balance_before = gauge.balanceOf(self.safe)
            pool.approve(gauge, balance_delta)
            gauge.deposit(balance_delta * self.dusty, destination)

            assert gauge.balanceOf(destination) > balance_before


    def unstake_all_and_withdraw_all(
        self, underlyings=None, pool=None, unstake=True, is_eth=False, destination=None
    ):
        # given underlyings or pool, unstake bpt and withdraw all to underlyings
        destination = self.safe.address if not destination else destination

        if not underlyings and not pool:
            raise TypeError('must provide either underlyings or pool')

        if underlyings:
            underlyings = sorted(underlyings)
            pool_id = self.find_pool_for_underlyings(underlyings)
            pool = self.safe.contract(self.vault.getPool(pool_id)[0])
        else:
            pool_id = pool.getPoolId()
            underlyings, reserves, _ = self.vault.getPoolTokens(pool_id)

        if unstake:
            balance_before = pool.balanceOf(self.safe)

            gauge = self.safe.contract(self.gauge_factory.getPoolGauge(pool))
            gauge.withdraw(gauge.balanceOf(self.safe))

            assert pool.balanceOf(self.safe) > balance_before

        exact_bpt_for_tokens_enum = 1
        amount_in = pool.balanceOf(self.safe)

        data_encoded = eth_abi.encode_abi(
            ['uint256', 'uint256'],
            [exact_bpt_for_tokens_enum, amount_in]
            )

        underlyings_out = calc_tokens_out_given_exact_bpt_in(
            pool, reserves, amount_in
        )
        min_underlyings_out = \
            [x * (1 - self.max_slippage) for x in underlyings_out]

        request = (
            underlyings,
            min_underlyings_out,
            data_encoded,
            is_eth
        )

        balances_before = [Contract(x).balanceOf(destination) for x in underlyings]

        pool.approve(self.vault, amount_in)
        self.vault.exitPool(
            pool_id, self.safe, destination, request
        )

        balances_after = [Contract(x).balanceOf(destination) for x in underlyings]
        assert all([x > y for x, y in zip(balances_after, balances_before)])


    def claim_all(self):
        pass

