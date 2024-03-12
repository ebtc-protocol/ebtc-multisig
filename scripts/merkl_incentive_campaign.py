from datetime import datetime, timezone
from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from helpers.constants import AddressZero, EmptyBytes32
from rich.console import Console

C = Console()

"""
The following methods are meant to provide the interface for the `DistributionCreator` contract

## `distribute_incentives_concentrated_liquidity_pool` method:
    - it is meant to be used to create a new campaign for incentivising a univ3 pool (less flexible method)
    - incentive a selected univ3 pool
    - set token to incentivise with
    - determine the weights for each of the components (token A, token B & fees)
    - timestamp when the campaign will kick off by passing date in string format UTC based
    - length of the campaign defined in weeks

## `create_campaign` method:
    - more flexible as it allows us to put almost any configuration we want in the campaign data
    - incentivize holders of an specific behaviour: erc20, CR of $eBTC holders

Errors map:
- InvalidReward(): typed error: 0x28829e82
- NotSigned(): typed error: 0xa72952d8
"""

HOURS_PER_DAY = 24
WEIGHTS_TOTAL_BASE = 10_000


def distribute_incentives_concentrated_liquidity_pool(
    incentive_token=r.assets.weth,
    token_amount=0,  # in ether denomination. sc expects on wei
    weight_token_a=0,  # format in cli: %. sc expects on base 10 ** 4
    weight_token_b=0,  # format in cli: %. sc expects on base 10 ** 4
    weight_fees=0,  # format in cli: %. sc expects on base 10 ** 4
    starting_date="",  # format in cli: %Y-%m-%d %H:%M. sc expects ts
    duration_campaign=1,  # format in cli: days. sc expects hours
    sim=False,
):
    safe = GreatApeSafe(r.badger_wallets.ibbtc_multisig_incentives)

    # token
    incentive_token = safe.contract(incentive_token)

    # contracts
    distribution_creator = interface.IDistributorCreator(
        r.merkl.distribution_creator, owner=safe.account
    )

    # snap
    safe.take_snapshot(tokens=[incentive_token])

    # assert arguments correctness
    valid_incentive_tokens = [
        token_tuple[0] for token_tuple in distribution_creator.getValidRewardTokens()
    ]
    assert (
        incentive_token.address in valid_incentive_tokens
    ), "incentive token not valid!"

    reward_token_min_amount = distribution_creator.rewardTokenMinAmounts(
        incentive_token
    )
    token_amount_mantissa = int(token_amount) * 10 ** incentive_token.decimals()
    incentive_token_balance = incentive_token.balanceOf(safe)
    assert (
        token_amount_mantissa > 0 and token_amount_mantissa <= incentive_token_balance,
        "amount greater than balancer or zero",
    )
    C.print(f"[blue]reward_token_min_amount={reward_token_min_amount}\n[/blue]")
    C.print(f"[green]token_amount_mantissa={token_amount_mantissa}\n[/green]")

    weight_token_a = int(weight_token_a) * 10 ** 2
    weight_token_b = int(weight_token_b) * 10 ** 2
    weight_fees = int(weight_fees) * 10 ** 2
    assert (
        weight_token_a + weight_token_b + weight_fees == WEIGHTS_TOTAL_BASE
    ), "total weights does not match 10_000"

    duration_campaign = int(duration_campaign) * HOURS_PER_DAY
    assert duration_campaign >= HOURS_PER_DAY, "campaign duration smaller than 1 day"
    C.print(f"[green]duration_campaign={duration_campaign}\n[/green]")
    # this represents the drip of token per epoch (hourly)
    C.print(
        f"[green]token_amount_mantissa/duration_campaign={str(int(token_amount_mantissa/duration_campaign))}\n[/green]"
    )

    start_date_ts = (
        datetime.strptime(starting_date, "%Y-%m-%d %H:%M")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )
    now = datetime.now().timestamp()
    assert start_date_ts > now, "starting time is on the past!"
    C.print(f"[green]start_date_ts={start_date_ts}\n[/green]")

    # actions
    fee = distribution_creator.BASE_9()  # fees is on base 10 ** 9
    fee_mantissa = (token_amount_mantissa * fee) / 1e9
    token_amount_mantissa_and_fee = token_amount_mantissa + fee_mantissa

    incentive_token.approve(distribution_creator, token_amount_mantissa_and_fee)
    distribution_creator.createDistribution(
        (
            EmptyBytes32,
            r.uniswap.v3pool_wbtc_weth,  # @note TBD! using a placeholder for script testing
            incentive_token,
            token_amount_mantissa_and_fee,
            [],  # positionWrappers
            [],  # wrapperTypes (0=whitelisted addresses,3=blacklisted addresses)
            weight_token_a,  # @note verify the correct token A is the one you expect!
            weight_token_b,  # @note verify the correct token B is the one you expect!
            weight_fees,
            start_date_ts,  # epochStart (timestamp)
            duration_campaign,  # numEpoch (epochs are defined in hours)
            0,  # isOutOfRangeIncentivized (0 represent False)
            0,  # boostedReward (in base 10 ** 4)
            AddressZero,  # boostingAddress
            EmptyBytes32,  # additionalData
        )
    )

    safe.print_snapshot()

    if not sim:
        safe.post_safe_tx()


def sim():
    governance_distributor_contract = "0x529619a10129396a2F642cae32099C1eA7FA2834"
    distribution_creator = interface.IDistributorCreator(
        r.merkl.distribution_creator, owner=governance_distributor_contract
    )

    # wl msig addy so does not revert on modifier `hasSigned`
    # ref: https://github.com/AngleProtocol/merkl-contracts/blob/main/contracts/DistributionCreator.sol#L145-L153
    distribution_creator.toggleSigningWhitelist(
        r.badger_wallets.ibbtc_multisig_incentives
    )
    distribution_creator.toggleTokenWhitelist(r.assets.weth)
    distribution_creator.setRewardTokenMinAmounts([r.assets.weth], [10000000000000000])

    # run script
    distribute_incentives_concentrated_liquidity_pool(
        incentive_token=r.assets.weth,
        token_amount=2,
        weight_token_a=20,
        weight_token_b=20,
        weight_fees=60,
        starting_date="2024-3-22 13:00",
        duration_campaign=1,
        sim=True,
    )
