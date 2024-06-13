from datetime import datetime, timezone, timedelta

from eth_abi import encode
from brownie import interface, web3, accounts

from great_ape_safe import GreatApeSafe

from helpers.addresses import r
from helpers.constants import AddressZero, EmptyBytes32

from great_ape_safe.ape_api.helpers.coingecko import get_cg_price

from rich.console import Console

from decimal import Decimal

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
- CampaignSouldStartInFuture(): typed error: 0xcb737dcc
- CampaignDurationBelowHour(): typed error: 0x1b5982fd
- CampaignRewardTokenNotWhitelisted(): typed error: 0xc0460cfb
"""

# Merkl Incentives Policy Vote
APR = 0.08
DAYS_PER_WEEK = 7
DAYS_PER_YEAR = 365

COEF = 0.98
DEADLINE = 60 * 60 * 3

HOURS_PER_DAY = 24
SECONDS_PER_HOUR = 3600
WEIGHTS_TOTAL_BASE = 10_000
CAMPAIGN_TYPE_ERC20 = 1
CAMPAIGN_TYPE_CLAMM = 2

safe = GreatApeSafe(r.badger_wallets.ibbtc_multisig_incentives)

# contracts
distribution_creator = interface.IDistributorCreator(
    r.merkl.distribution_creator, owner=safe.account
)


def distribute_incentives_concentrated_liquidity_pool(
    incentive_token=r.assets.badger,
    token_amount=0,  # in ether denomination. sc expects on wei
    weight_token_a=0,  # format in cli: %. sc expects on base 10 ** 4
    weight_token_b=0,  # format in cli: %. sc expects on base 10 ** 4
    weight_fees=0,  # format in cli: %. sc expects on base 10 ** 4
    starting_date="",  # format in cli: %Y-%m-%d %H:%M. sc expects ts
    duration_campaign=1,  # format in cli: days. sc expects hours
    whitelist_safe=False,  # it is required to post incentives
    sim=False,
):
    # @note only to call once from the msig posting the incentives
    # whitelisting dynamic changed on the contract, now requires this method to be called
    if whitelist_safe:
        distribution_creator.acceptConditions()

    # token
    incentive_token = safe.contract(incentive_token)

    # snap
    safe.take_snapshot(tokens=[incentive_token])

    # assert arguments correctness
    (
        token_amount_mantissa,
        duration_campaign,
        weight_token_a,
        weight_token_b,
        weight_fees,
        start_date_ts,
    ) = _verify_cli_args(
        incentive_token,
        token_amount,
        weight_token_a,
        weight_token_b,
        weight_fees,
        starting_date,
        duration_campaign,
    )

    # calculate fee
    token_amount_mantissa_and_fee = _get_token_mantissa_and_fee(token_amount_mantissa)

    # actions
    incentive_token.approve(distribution_creator, token_amount_mantissa_and_fee)
    distribution_creator.createDistribution(
        (
            EmptyBytes32,
            r.uniswap.v3pool_wbtc_ebtc,
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


def create_campaign(
    incentive_token=r.assets.badger,
    token_amount=0,  # in ether denomination. sc expects on wei
    weight_token_a=1,  # format in cli: %. sc expects on base 10 ** 4
    weight_token_b=1,  # format in cli: %. sc expects on base 10 ** 4
    weight_fees=98,  # format in cli: %. sc expects on base 10 ** 4
    starting_date="2024-06-13 17:00",  # format in cli: %Y-%m-%d %H:%M. sc expects ts
    duration_campaign=7,  # format in cli: days. sc expects hours
    ebtc_vault_owned=21.897, # float, pull from debank (manually)
    whitelist_safe=False,  # it is required to post incentives
    sim=False,
):
    # @note only to call once from the msig posting the incentives
    # whitelisting dynamic changed on the contract, now requires this method to be called
    if whitelist_safe:
        distribution_creator.acceptConditions()

    # token
    incentive_token = safe.contract(incentive_token)

    # snap
    safe.take_snapshot(tokens=[incentive_token])

    if token_amount == 0:
        # buy incentives on uni v3
        token_amount_mantissa = swap_badger_for_campaign_target(ebtc_vault_owned)
    else:
        token_amount_mantissa = int(
            Decimal(token_amount) * 10 ** incentive_token.decimals()
        )

    # assert arguments correctness
    (
        token_amount_mantissa,
        duration_campaign,
        weight_token_a,
        weight_token_b,
        weight_fees,
        start_date_ts,
    ) = _verify_cli_args(
        incentive_token,
        token_amount,
        weight_token_a,
        weight_token_b,
        weight_fees,
        starting_date,
        duration_campaign,
    )

    # https://github.com/AngleProtocol/merkl-contracts/blob/main/contracts/DistributionCreator.sol#L525-L535
    # https://github.com/AngleProtocol/merkl-contracts/blob/main/test/hardhat/middleman/merklGaugeMiddleman.test.ts#L216
    campaign_data = encode(
        [
            "address",  # target token which the campaign is incentivizing
            "uint",  # propFees
            "uint",  # propToken0
            "uint",  # propToken1
            "uint",  # isOutOfRangeIncentivized
            "address",  # boostingAddress
            "uint",  # boostedReward
            "address[]",  # whitelist
            "address[]",  # blacklist
            "string",  # reason
        ],
        [
            r.uniswap.v3pool_wbtc_ebtc,
            weight_fees,  # propFees
            weight_token_a,  # propToken0
            weight_token_b,  # propToken1
            0,  # isOutOfRangeIncentivized
            AddressZero,  # boostingAddress
            0,  # boostedReward
            [],  # @note in case that whitelist feature would be leverage this will require review
            [
                r.badger_wallets.treasury_vault_multisig
            ],  # @note that the treasury is getting blacklisted in the campaign
            "Incentivizing eBTC ecosystem",
        ],
    )

    # should help identifying on analytics $ebtc campaigns on the past
    campaign_id = web3.solidity_keccak(["string"], ["EBTC_CAMPAIGN"]).hex()

    campaign_params = (
        campaign_id,
        safe.address,
        incentive_token.address,
        token_amount_mantissa,
        CAMPAIGN_TYPE_CLAMM,  # campaignType can be: CLAMM: 2, ERC20: 1
        start_date_ts,  # needs to be on the future
        duration_campaign * SECONDS_PER_HOUR,  # duration in seconds
        campaign_data,
    )

    # calculate fee
    token_amount_mantissa_and_fee = _get_token_mantissa_and_fee(token_amount_mantissa)

    # actions
    # required as per $badger allowance logic to reset first to 0
    incentive_token.approve(distribution_creator, 0)
    incentive_token.approve(distribution_creator, token_amount_mantissa_and_fee)
    distribution_creator.createCampaign(campaign_params)

    safe.print_snapshot()

    if not sim:
        safe.post_safe_tx()


def swap_badger_for_campaign_target(ebtc_vault_owned=0):
    safe.init_uni_v3()

    # tokens
    weth = safe.contract(r.assets.weth)
    badger = safe.contract(r.assets.badger)
    ebtc = safe.contract(r.ebtc.ebtc_token)

    # calc amount to swap based on user owned $ebtc supply vs treasury
    ebtc_total_supply = ebtc.totalSupply()

    # @note calculating on-chain currently owned $ebtc by the treasury is convoluted due to some
    # portions showing up in the cdp_manager` storage vs other being direct swaps from $steth -> $ebtc
    # instead opting for ease of precision for time being to digest the argument in the script
    user_ebtc_owned = ebtc_total_supply - (
        float(ebtc_vault_owned) * 10 ** ebtc.decimals()
    )

    # calc $ value of incentive
    ebtc_price = get_cg_price(ebtc.address)
    C.print(f"[green]ebtc_price={ebtc_price}[/green]\n")
    weth_price = get_cg_price(weth.address)

    user_ebtc_owned_formatted = user_ebtc_owned / 10 ** ebtc.decimals()
    C.print(f"[green]user_ebtc_owned_formatted={user_ebtc_owned_formatted}\n[/green]")

    usd_debt_value = user_ebtc_owned_formatted * ebtc_price
    incentive_usd_apr_target_weekly = (
        (usd_debt_value * APR) / DAYS_PER_YEAR
    ) * DAYS_PER_WEEK
    C.print(
        f"[green]incentive_usd_apr_target_weekly=${incentive_usd_apr_target_weekly}\n[/green]"
    )

    weth_equivalent_mantissa = int(
        (incentive_usd_apr_target_weekly / weth_price) * (10 ** weth.decimals())
    )
    C.print(
        f"[green]swapping {weth_equivalent_mantissa / (10 ** weth.decimals())} $weth for $badger\n[/green]"
    )

    # univ3 swap
    return safe.uni_v3.swap([weth, badger], weth_equivalent_mantissa)


# ===================== FEE AMOUNT CALCULATOR ===================== #
# The following method is meant to be used for calculating the fee amount


def _get_token_mantissa_and_fee(token_amount_mantissa):
    base = distribution_creator.BASE_9()  # base is expressed on base 10 ** 9
    fee = distribution_creator.defaultFees()
    fee_mantissa = (token_amount_mantissa * fee) / base

    return token_amount_mantissa + fee_mantissa


# ===================== ARGUMENTS VERIFICATION HELPER ===================== #
# The following method is meant to be used for checking the validity of the cli arguments


def _verify_cli_args(
    incentive_token,
    token_amount_mantissa,
    weight_token_a,
    weight_token_b,
    weight_fees,
    starting_date,
    duration_campaign,
):
    valid_incentive_tokens = [
        token_tuple[0] for token_tuple in distribution_creator.getValidRewardTokens()
    ]
    assert (
        incentive_token.address in valid_incentive_tokens
    ), "incentive token not valid!"

    reward_token_min_amount = distribution_creator.rewardTokenMinAmounts(
        incentive_token
    )
    incentive_token_balance = incentive_token.balanceOf(safe)
    assert (
        (token_amount_mantissa > 0) and (token_amount_mantissa <= incentive_token_balance),
        "amount greater than balance or zero",
    )
    C.print(f"[blue]reward_token_min_amount={reward_token_min_amount}\n[/blue]")
    C.print(f"[green]token_amount_mantissa={token_amount_mantissa}\n[/green]")

    duration_campaign = int(int(duration_campaign) * HOURS_PER_DAY)
    assert duration_campaign >= HOURS_PER_DAY, "campaign duration smaller than 1 day"
    C.print(f"[green]duration_campaign={duration_campaign}\n[/green]")

    weight_token_a = int(weight_token_a) * 10**2
    weight_token_b = int(weight_token_b) * 10**2
    weight_fees = int(weight_fees) * 10**2
    assert (
        weight_token_a + weight_token_b + weight_fees == WEIGHTS_TOTAL_BASE
    ), "total weights does not match 10_000"

    start_date_ts = (
        datetime.strptime(starting_date, "%Y-%m-%d %H:%M")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )
    now = datetime.now().timestamp()
    assert start_date_ts > now, "starting time is on the past!"
    C.print(f"[green]start_date_ts={start_date_ts}\n[/green]")

    return (
        token_amount_mantissa,
        duration_campaign,
        weight_token_a,
        weight_token_b,
        weight_fees,
        start_date_ts,
    )


# ===================== SIMULATIONS ===================== #
# The following methods are meant to be used for testing purposes only
# They will not create any transaction on chain


def _sim_prep():
    governance_distributor_contract = accounts.at(
        "0x529619a10129396a2F642cae32099C1eA7FA2834", force=True
    )
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


def sim_distribute_incentives_concentrated_liquidity_pool():
    _sim_prep()

    # Dummy start time 2 days into the future
    start = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")

    # run script
    distribute_incentives_concentrated_liquidity_pool(
        incentive_token=r.assets.weth,
        token_amount=2,
        weight_token_a=20,
        weight_token_b=20,
        weight_fees=60,
        starting_date=start,
        duration_campaign=1,
        sim=True,
    )


def sim_create_campaign():
    _sim_prep()

    # Dummy start time 2 days into the future
    start = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")

    # run script
    create_campaign(
        incentive_token=r.assets.weth,
        token_amount=2,
        weight_token_a=20,
        weight_token_b=20,
        weight_fees=60,
        starting_date=start,
        duration_campaign=1,
        sim=True,
    )
