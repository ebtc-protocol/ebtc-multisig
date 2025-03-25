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
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setOraclePriceConstraint.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setRateLimitingConstraint.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setBuyAssetConstraint.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_FEE_MANAGER.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setFeeToSell.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_FEE_MANAGER.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.setFeeToBuy.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_PAUSER.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.pause.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_PAUSER.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.unpause.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ESCROW_MANAGER.value,
            safe.ebtc.bsm_escrow,
            safe.ebtc.bsm_escrow.feeProfit.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ESCROW_MANAGER.value,
            safe.ebtc.bsm_escrow,
            safe.ebtc.bsm_escrow.claimProfit.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_ESCROW_MANAGER.value,
            safe.ebtc.bsm_escrow,
            safe.ebtc.bsm_escrow.claimTokens.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_CONSTRAINT_MANAGER.value,
            safe.ebtc.bsm_oracle_price_constraint,
            safe.ebtc.bsm_oracle_price_constraint.setMinPrice.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_CONSTRAINT_MANAGER.value,
            safe.ebtc.bsm_oracle_price_constraint,
            safe.ebtc.bsm_oracle_price_constraint.setOracleFreshness.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_CONSTRAINT_MANAGER.value,
            safe.ebtc.bsm_rate_limiting_constraint,
            safe.ebtc.bsm_rate_limiting_constraint.setMintingConfig.signature,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_AUTHORIZED_USER.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.unpause.sellAssetNoFee,
            True,
        ),
        safe.ebtc.authority.setRoleCapability.encode_input(
            safe.ebtc.governance_roles.BSM_AUTHORIZED_USER.value,
            safe.ebtc.bsm,
            safe.ebtc.bsm.unpause.buyAssetNoFee,
            True,
        ),
        # Grant roles
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.highsec_timelock,
            safe.ebtc.governance_roles.BSM_ADMIN.value,
            True,
        ),
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.lowsec_timelock,
            safe.ebtc.governance_roles.BSM_FEE_MANAGER.value,
            True,
        ),
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.security_multisig,
            safe.ebtc.governance_roles.BSM_PAUSER.value,
            True,
        ),
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.techops_multisig,
            safe.ebtc.governance_roles.BSM_ESCROW_MANAGER.value,
            True,
        ),
        safe.ebtc.authority.setUserRole.encode_input(
            safe.ebtc.techops_multisig,
            safe.ebtc.governance_roles.BSM_CONSTRAINT_MANAGER.value,
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
