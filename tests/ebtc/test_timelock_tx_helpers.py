from brownie import chain
import pytest
from helpers.constants import EmptyBytes32


def test_schedule_permissions(random_safe):
    random_safe.init_ebtc()

    ## Dummy data
    target = random_safe.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = random_safe.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()

    with pytest.raises(AssertionError, match="Error: No role"):
        random_safe.ebtc.schedule_timelock(
            timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
        )


def test_schedule_timelock_permissions_on_target(techops):
    techops.init_ebtc()

    ## Attempt to schedule grant TechOps minting rights by techopss
    target = techops.ebtc.authority
    data = target.setUserRole.encode_input(
        techops.account, techops.ebtc.governance_roles.EBTC_MINTER.value, True
    )
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()

    with pytest.raises(AssertionError, match="Error: Not authorized"):
        techops.ebtc.schedule_timelock(
            timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
        )


def test_execute_permissions(random_safe):
    random_safe.init_ebtc()

    ## Dummy data
    target = random_safe.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = random_safe.ebtc.lowsec_timelock

    with pytest.raises(AssertionError, match="Error: No role"):
        random_safe.ebtc.execute_timelock(
            timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
        )


def test_execute_timelock_permissions_on_target(techops):
    techops.init_ebtc()

    ## Attempt to execute grant TechOps minting rights by techopss
    target = techops.ebtc.authority
    data = target.setUserRole.encode_input(
        techops.account, techops.ebtc.governance_roles.EBTC_MINTER.value, True
    )
    timelock = techops.ebtc.lowsec_timelock

    with pytest.raises(AssertionError, match="Error: Not authorized"):
        techops.ebtc.execute_timelock(
            timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
        )


def test_cancel_timelock_before_scheduling(techops, ecosystem, random_safe):
    techops.init_ebtc()
    ecosystem.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    id = techops.ebtc.lowsec_timelock.hashOperation(
        target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    ## Attempts to cancel the operation before scheduled
    with pytest.raises(Exception, match="Error: operation does not exist"):
        ecosystem.ebtc.cancel_lowsec_timelock(id)


def test_cancel_timelock_permissions(techops, ecosystem, random_safe):
    techops.init_ebtc()
    ecosystem.init_ebtc()
    random_safe.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()
    id = techops.ebtc.lowsec_timelock.hashOperation(
        target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
    )

    ## Random account attempts to cancel (permissions)
    with pytest.raises(AssertionError, match="Error: No role"):
        random_safe.ebtc.cancel_lowsec_timelock(id)


def test_cancel_pending_operation(techops, ecosystem):
    techops.init_ebtc()
    ecosystem.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()
    id = techops.ebtc.lowsec_timelock.hashOperation(
        target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
    )

    ## Some time passes
    chain.sleep(delay - 10)
    chain.mine()

    assert techops.ebtc.lowsec_timelock.isOperationPending(id)

    ## Permissioned account can cancel pending operation
    ecosystem.ebtc.cancel_lowsec_timelock(id)

    assert techops.ebtc.lowsec_timelock.isOperationPending(id) == False


def test_cancel_ready_operation(techops, ecosystem):
    techops.init_ebtc()
    ecosystem.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()
    id = techops.ebtc.lowsec_timelock.hashOperation(
        target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
    )

    ## Some time passes
    chain.sleep(delay + 10)
    chain.mine()

    assert techops.ebtc.lowsec_timelock.isOperationReady(id)

    ## Permissioned account can cancel ready operation
    ecosystem.ebtc.cancel_lowsec_timelock(id)

    assert techops.ebtc.lowsec_timelock.isOperationReady(id) == False


def test_cancel_operation_from_parameters(techops, ecosystem):
    techops.init_ebtc()
    ecosystem.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()
    id = techops.ebtc.lowsec_timelock.hashOperation(
        target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
    )

    ## Some time passes
    chain.sleep(delay + 10)
    chain.mine()

    assert techops.ebtc.lowsec_timelock.isOperationReady(id)

    ## Permissioned account can cancel ready operation
    ecosystem.ebtc.cancel_lowsec_timelock(
        "0x0", target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    assert techops.ebtc.lowsec_timelock.isOperationReady(id) == False
