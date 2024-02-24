from brownie import chain
import pytest
import brownie
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


def test_cancel_timelock_before_scheduling(techops, security_multisig, random_safe):
    techops.init_ebtc()
    security_multisig.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    id = techops.ebtc.lowsec_timelock.hashOperation(
        target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    ## Attempts to cancel the operation before scheduled
    with pytest.raises(Exception, match="Error: operation does not exist"):
        security_multisig.ebtc.cancel_lowsec_timelock(id)


def test_cancel_timelock_permissions(techops, security_multisig, random_safe):
    techops.init_ebtc()
    security_multisig.init_ebtc()
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


def test_cancel_pending_operation(techops, security_multisig):
    techops.init_ebtc()
    security_multisig.init_ebtc()

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
    security_multisig.ebtc.cancel_lowsec_timelock(id)

    assert techops.ebtc.lowsec_timelock.isOperationPending(id) == False


def test_cancel_ready_operation(techops, security_multisig):
    techops.init_ebtc()
    security_multisig.init_ebtc()

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
    security_multisig.ebtc.cancel_lowsec_timelock(id)

    assert techops.ebtc.lowsec_timelock.isOperationReady(id) == False


def test_cancel_operation_from_parameters(techops, security_multisig):
    techops.init_ebtc()
    security_multisig.init_ebtc()

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
    security_multisig.ebtc.cancel_lowsec_timelock(
        "0x0", target.address, 0, data, EmptyBytes32, EmptyBytes32
    )

    assert techops.ebtc.lowsec_timelock.isOperationReady(id) == False


# Test posting two operations with the same parameters but differentiating them with a salt value
def test_repeated_operations_with_salt(techops):
    techops.init_ebtc()

    target = techops.ebtc.active_pool
    data = target.setFeeBps.encode_input(100)
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()

    ## Schedule and execute first operation
    id1 = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)
    techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
    )
    chain.sleep(delay + 1)
    chain.mine()
    techops.ebtc.execute_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
    )
    assert target.feeBps() == 100
    assert techops.ebtc.lowsec_timelock.isOperationDone(id1)

    ## Schedule and execute second operation with different value (changing value)
    data = target.setFeeBps.encode_input(200)
    id2 = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)
    techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
    )
    chain.sleep(delay + 1)
    chain.mine()
    techops.ebtc.execute_timelock(
        timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32
    )
    assert target.feeBps() == 200
    assert techops.ebtc.lowsec_timelock.isOperationDone(id2)

    ## Attempting to schedule and execute third operation with the same value as the first operation and no salt
    data = target.setFeeBps.encode_input(100)
    id3 = timelock.hashOperation(target.address, 0, data, EmptyBytes32, EmptyBytes32)
    assert id1 == id3

    with brownie.reverts("TimelockController: operation already scheduled"):
        techops.ebtc.schedule_timelock(
            timelock, target.address, 0, data, EmptyBytes32, EmptyBytes32, delay + 1
        )

    ## Schedule and execute third operation with the same value as the first operation but with a salt
    salt = "0x0000000000000000000000000000000000000000000000000000000000000001"
    id3 = timelock.hashOperation(target.address, 0, data, EmptyBytes32, salt)
    assert id1 != id3
    tx = techops.ebtc.schedule_timelock(
        timelock, target.address, 0, data, EmptyBytes32, salt, delay + 1
    )
    assert tx.events["CallSalt"]["id"] == id3
    assert tx.events["CallSalt"]["salt"] == str(salt)
    chain.sleep(delay + 1)
    chain.mine()
    techops.ebtc.execute_timelock(timelock, target.address, 0, data, EmptyBytes32, salt)
    assert target.feeBps() == 100
    assert techops.ebtc.lowsec_timelock.isOperationDone(id3)


def test_schedule_batch_timelock(techops):
    techops.init_ebtc()

    targets = [techops.ebtc.active_pool, techops.ebtc.borrower_operations]
    data = [
        targets[0].setFeeBps.encode_input(100),
        targets[1].setFeeBps.encode_input(50),
    ]
    timelock = techops.ebtc.lowsec_timelock
    delay = timelock.getMinDelay()

    ## Schedule both operations in batch
    techops.ebtc.schedule_or_execute_batch_timelock(
        timelock, targets, [0, 0], data, EmptyBytes32
    )

    chain.sleep(delay + 1)
    chain.mine()

    ## Execute both operations in batch
    techops.ebtc.schedule_or_execute_batch_timelock(
        timelock, targets, [0, 0], data, EmptyBytes32
    )

    assert targets[0].feeBps() == 100
    assert targets[1].feeBps() == 50
