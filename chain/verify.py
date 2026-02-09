import os
from web3 import Web3
from eth_utils import to_checksum_address

from chain.abis.cusdc_abi import CUSDC_ABI
from chain.abis.payroll_vault_abi import PAYROLL_VAULT_ABI

RPC = os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")

CUSDC = to_checksum_address(os.getenv("CUSDC"))
PAYROLL_VAULT = to_checksum_address(os.getenv("PAYROLL_VAULT"))

w3 = Web3(Web3.HTTPProvider(RPC))
cusdc = w3.eth.contract(address=CUSDC, abi=CUSDC_ABI)
vault = w3.eth.contract(address=PAYROLL_VAULT, abi=PAYROLL_VAULT_ABI)


def receipt_has_private_transfer_to_vault(receipt) -> bool:
    if not receipt:
        return False

    for log in receipt.get("logs", []):
        if to_checksum_address(log["address"]) != CUSDC:
            continue
        try:
            decoded = cusdc.events.TransferPrivate().process_log(log)
        except Exception:
            continue

        if to_checksum_address(decoded["args"]["to"]) == PAYROLL_VAULT:
            return True

    return False


def receipt_has_payroll_created(receipt, payroll_id: int, token: str, root: str, total: int) -> bool:
    if not receipt:
        return False

    token = to_checksum_address(token)
    root_l = root.lower()

    for log in receipt.get("logs", []):
        if to_checksum_address(log["address"]) != PAYROLL_VAULT:
            continue

        try:
            decoded = vault.events.PayrollCreated().process_log(log)
        except Exception:
            continue

        args = decoded["args"]
        if int(args["payrollId"]) != int(payroll_id):
            continue
        if to_checksum_address(args["token"]) != token:
            continue
        if args["root"].lower() != root_l:
            continue
        if int(args["total"]) != int(total):
            continue

        return True

    return False


def receipt_has_claimed(receipt, payroll_id: int, index: int, employee: str) -> bool:
    if not receipt:
        return False

    employee = to_checksum_address(employee)

    for log in receipt.get("logs", []):
        if to_checksum_address(log["address"]) != PAYROLL_VAULT:
            continue

        try:
            decoded = vault.events.Claimed().process_log(log)
        except Exception:
            continue

        args = decoded["args"]
        if int(args["payrollId"]) != int(payroll_id):
            continue
        if int(args["index"]) != int(index):
            continue
        if to_checksum_address(args["employee"]) != employee:
            continue

        return True

    return False
