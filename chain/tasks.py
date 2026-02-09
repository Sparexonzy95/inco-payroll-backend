# chain/tasks.py
import os
from celery import shared_task
from web3 import Web3
from django.utils import timezone
from eth_utils import to_checksum_address

from chain.models import ChainTx
from payroll.models import PayrollRun, PayrollClaim
from chain.verify import receipt_has_private_transfer_to_vault

RPC = os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")
w3 = Web3(Web3.HTTPProvider(RPC))


@shared_task
def poll_pending_txs():
    """
    Poll pending txs and update:
      - ChainTx.status (pending/confirmed/failed)
      - PayrollRun status transitions:
            committed -> onchain_created (create_payroll confirmed)
            onchain_created/committed -> open (fund_vault confirmed AND verified transfer to vault)
      - PayrollClaim -> claimed (claim confirmed)
    """
    pending = ChainTx.objects.filter(status="pending").order_by("created_at")[:50]

    for tx in pending:
        receipt = None
        try:
            receipt = w3.eth.get_transaction_receipt(tx.tx_hash)
        except Exception:
            # not mined yet or temporary rpc failure
            continue

        if not receipt:
            continue

        ok = (receipt.get("status", 0) == 1)

        tx.status = "confirmed" if ok else "failed"
        tx.success = ok
        tx.block_number = receipt.get("blockNumber")
        tx.save(update_fields=["status", "success", "block_number", "updated_at"])

        _apply_tx_effects(tx, ok, receipt)


def _apply_tx_effects(tx: ChainTx, ok: bool, receipt):
    if not ok:
        return

    # createPayroll confirmed
    if tx.kind == "create_payroll" and tx.run_id:
        try:
            run = PayrollRun.objects.get(id=tx.run_id)
            run.create_tx_hash = tx.tx_hash
            run.status = "onchain_created"
            run.save(update_fields=["create_tx_hash", "status"])
        except PayrollRun.DoesNotExist:
            return

    # fund vault confirmed (ONLY open if we verify a cUSDC TransferPrivate to the vault in this tx)
    if tx.kind == "fund_vault" and tx.run_id:
        if not receipt_has_private_transfer_to_vault(receipt):
            # Tx confirmed, but it wasn't a private cUSDC transfer into the vault.
            # Do not open the run.
            return

        try:
            run = PayrollRun.objects.get(id=tx.run_id)
            run.fund_tx_hash = tx.tx_hash
            run.status = "open"
            run.save(update_fields=["fund_tx_hash", "status"])
        except PayrollRun.DoesNotExist:
            return

    # claim confirmed
    if tx.kind == "claim" and tx.payroll_id and tx.employee_wallet:
        try:
            run = PayrollRun.objects.get(payroll_id=tx.payroll_id)

            employee_wallet = to_checksum_address(tx.employee_wallet)

            claim = PayrollClaim.objects.get(run=run, employee_wallet__iexact=employee_wallet)
            claim.status = "claimed"
            claim.claim_tx_hash = tx.tx_hash
            claim.claimed_at = timezone.now()
            claim.save(update_fields=["status", "claim_tx_hash", "claimed_at"])
        except Exception:
            return
