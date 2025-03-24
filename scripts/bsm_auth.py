from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from helpers.constants import EmptyBytes32
from rich.console import Console

C = Console()

def set_bsm_auth(safe):
    data = [
        # Role names
        safe.ebtc.authority.setRoleName.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value, 
            "BSM: Admin"
        ),
        safe.ebtc.authority.setRoleName.encode_input(
            safe.ebtc.governance_roles.BSM_FEE_MANAGER.value, 
            "BSM: Fee Manager"
        ),
        safe.ebtc.authority.setRoleName.encode_input(
            safe.ebtc.governance_roles.BSM_PAUSER.value, 
            "BSM: Pauser"
        ),
        safe.ebtc.authority.setRoleName.encode_input(
            safe.ebtc.governance_roles.BSM_ESCROW_MANAGER.value, 
            "BSM: Escrow Manager"
        ),
        safe.ebtc.authority.setRoleName.encode_input(
            safe.ebtc.governance_roles.BSM_CONSTRAINT_MANAGER.value, 
            "BSM: Constraint Manager"
        ),
        safe.ebtc.authority.setRoleName.encode_input(
            safe.ebtc.governance_roles.BSM_AUTHORIZED_USER.value, 
            "BSM: Authorized User"
        ),
        # Role capabilities
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.updateEscrow.signature,
            True,
        ),
        # Role capabilities
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setOraclePriceConstraint.signature,
            True,
        ),
        # Role capabilities
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setRateLimitingConstraint.signature,
            True,
        ),
        # Role capabilities
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setBuyAssetConstraint.signature,
            True,
        ),
    ]

    targets = [safe.ebtc.authority] * len(data)
    values = [0] * len(data)

    safe.ebtc.schedule_or_execute_batch_timelock(
        safe.ebtc.highsec_timelock, targets, values, data, EmptyBytes32
    )

def main():
    safe = GreatApeSafe(r.ebtc_wallets.security_multisig)
    safe.init_ebtc()

    set_bsm_auth(safe)

    safe.post_safe_tx(tenderly=False)
