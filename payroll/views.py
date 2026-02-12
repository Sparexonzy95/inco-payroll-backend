import base64
import os
from datetime import time as dtime

from django.core.exceptions import ValidationError
from django.utils import timezone
from eth_utils import to_checksum_address
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from web3 import Web3

from accounts.models import Employer, UserProfile
from chain.verify import receipt_has_payroll_created, receipt_has_private_transfer_to_vault
from payroll.id_utils import generate_payroll_id
from payroll.merkle import build_merkle_tree, leaf_hash, merkle_proof, merkle_root
from payroll.models import Employee, PayrollClaim, PayrollRun, PayrollSchedule
from payroll.schedule_utils import _local_now, next_daily, next_monthly, next_weekly, next_yearly

RPC = os.getenv("BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org")
PAYROLL_VAULT = os.getenv("PAYROLL_VAULT")
CUSDC = os.getenv("CUSDC")
WRAP_GATEWAY = os.getenv("WRAP_GATEWAY")
CHAIN_ID = int(os.getenv("CHAIN_ID", "84532"))

w3 = Web3(Web3.HTTPProvider(RPC))

ZERO_REF = "0x" + "00" * 32


def _json_error(msg: str, status: int = 400):
    return Response({"error": msg}, status=status)


def _require_env():
    missing = []
    for k in ["PAYROLL_VAULT", "CUSDC", "BASE_SEPOLIA_RPC_URL", "CHAIN_ID"]:
        if not os.getenv(k):
            missing.append(k)
    if missing:
        raise RuntimeError(f"Missing env: {', '.join(missing)}")


def _norm_addr(addr: str) -> str:
    if not isinstance(addr, str):
        raise ValueError("Invalid address type")
    addr = addr.strip()
    if len(addr) != 42 or not addr.startswith("0x"):
        raise ValueError("Invalid address format")
    return to_checksum_address(addr)


def _parse_time(hhmm: str) -> dtime:
    if not hhmm:
        return dtime(9, 0, 0)
    parts = hhmm.split(":")
    if len(parts) != 2:
        raise ValueError("time_of_day must be HH:MM")
    hh = int(parts[0])
    mm = int(parts[1])
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        raise ValueError("Invalid time_of_day")
    return dtime(hh, mm, 0)


def _compute_initial_next_run(stype, tod, weekday=None, dom=None, moy=None, doy=None):
    now = _local_now()
    if stype == "daily":
        return next_daily(now, tod)
    if stype == "weekly":
        return next_weekly(now, tod, weekday)
    if stype == "monthly":
        return next_monthly(now, tod, dom)
    if stype == "yearly":
        return next_yearly(now, tod, moy, doy)
    if stype == "instant":
        return None
    return None


def require_employer(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if not profile.wallet_address:
        return None, _json_error("Wallet not found for authenticated user", status=403)

    employer = Employer.objects.filter(wallet_address__iexact=profile.wallet_address).first()
    if not employer:
        return None, _json_error("Employer profile not set. Register name and email first.", status=403)
    if not employer.is_active:
        return None, _json_error("Employer account is inactive", status=403)
    return employer, None


def _require_run_for_employer(user, run_id: int):
    employer, error = require_employer(user)
    if error:
        return None, None, error

    run = PayrollRun.objects.filter(id=run_id).first()
    if not run:
        return None, None, _json_error("Run not found", status=404)
    if run.employer_id != employer.id:
        return None, None, _json_error("Run does not belong to employer", status=403)

    return employer, run, None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_schedule(request):
    employer, error = require_employer(request.user)
    if error:
        return error

    name = request.data.get("name")
    schedule_type = request.data.get("schedule_type")

    if not name or not schedule_type:
        return _json_error("name and schedule_type are required")

    if schedule_type not in ["instant", "daily", "weekly", "monthly", "yearly"]:
        return _json_error("Invalid schedule_type")

    try:
        tod = _parse_time(request.data.get("time_of_day", "09:00"))
    except Exception as ex:
        return _json_error(str(ex))

    weekday = request.data.get("weekday")
    day_of_month = request.data.get("day_of_month")
    month_of_year = request.data.get("month_of_year")
    day_of_year = request.data.get("day_of_year")

    if schedule_type == "weekly" and weekday is None:
        return _json_error("weekday is required for weekly schedule")
    if schedule_type == "monthly" and day_of_month is None:
        return _json_error("day_of_month is required for monthly schedule")
    if schedule_type == "yearly" and (month_of_year is None or day_of_year is None):
        return _json_error("month_of_year and day_of_year are required for yearly schedule")

    next_run = _compute_initial_next_run(
        schedule_type,
        tod,
        weekday=int(weekday) if weekday is not None else None,
        dom=int(day_of_month) if day_of_month is not None else None,
        moy=int(month_of_year) if month_of_year is not None else None,
        doy=int(day_of_year) if day_of_year is not None else None,
    )

    sched = PayrollSchedule.objects.create(
        employer=employer,
        name=name,
        schedule_type=schedule_type,
        time_of_day=tod if schedule_type != "instant" else None,
        weekday=int(weekday) if weekday is not None else None,
        day_of_month=int(day_of_month) if day_of_month is not None else None,
        month_of_year=int(month_of_year) if month_of_year is not None else None,
        day_of_year=int(day_of_year) if day_of_year is not None else None,
        enabled=True,
        next_run_at=next_run,
    )

    return Response({"id": sched.id, "name": sched.name, "schedule_type": sched.schedule_type, "next_run_at": sched.next_run_at, "enabled": sched.enabled})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_schedules(request):
    employer, error = require_employer(request.user)
    if error:
        return error

    qs = PayrollSchedule.objects.filter(employer=employer).order_by("-created_at")
    return Response([
        {
            "id": s.id,
            "name": s.name,
            "schedule_type": s.schedule_type,
            "time_of_day": s.time_of_day.isoformat() if s.time_of_day else None,
            "weekday": s.weekday,
            "day_of_month": s.day_of_month,
            "month_of_year": s.month_of_year,
            "day_of_year": s.day_of_year,
            "next_run_at": s.next_run_at,
            "enabled": s.enabled,
            "created_at": s.created_at,
        }
        for s in qs
    ])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_schedule(request, schedule_id: int):
    employer, error = require_employer(request.user)
    if error:
        return error

    sched = PayrollSchedule.objects.filter(id=schedule_id).first()
    if not sched:
        return _json_error("Schedule not found", status=404)
    if sched.employer_id != employer.id:
        return _json_error("Schedule does not belong to employer", status=403)

    enabled = bool(request.data.get("enabled", True))
    sched.enabled = enabled
    sched.save(update_fields=["enabled"])
    return Response({"id": sched.id, "enabled": sched.enabled})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_run(request):
    try:
        _require_env()
    except RuntimeError as ex:
        return _json_error(str(ex))

    employer, error = require_employer(request.user)
    if error:
        return error

    try:
        claim_window_days = int(request.data.get("claim_window_days", 14))
    except Exception:
        return _json_error("claim_window_days must be an integer")

    employees = Employee.objects.filter(employer=employer, active=True).order_by("wallet")
    total = employees.count()
    if total == 0:
        return _json_error("No active employees")

    now = timezone.now()
    close_at = now + timezone.timedelta(days=claim_window_days)
    payroll_id = generate_payroll_id()

    try:
        run = PayrollRun.objects.create(
            employer=employer,
            payroll_id=payroll_id,
            token=_norm_addr(CUSDC),
            vault=_norm_addr(PAYROLL_VAULT),
            total=total,
            total_amount_units=sum(int(e.salary_units) for e in employees),
            status="draft",
            claim_window_days=claim_window_days,
            close_at=close_at,
        )
    except (ValidationError, ValueError) as ex:
        return _json_error(str(ex))

    for idx, emp in enumerate(employees):
        PayrollClaim.objects.create(
            run=run,
            employee_wallet=_norm_addr(emp.wallet),
            index=idx,
            leaf="",
            proof=[],
            net_ciphertext_b64="",
            encrypted_ref=ZERO_REF,
            status="unclaimed",
        )

    return Response(
        {
            "run_id": run.id,
            "payroll_id": str(run.payroll_id),
            "token": run.token,
            "vault": run.vault,
            "total": run.total,
            "total_amount_units": int(run.total_amount_units),
            "status": run.status,
            "close_at": run.close_at,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_runs(request):
    employer, error = require_employer(request.user)
    if error:
        return error

    qs = PayrollRun.objects.filter(employer=employer).order_by("-created_at")

    return Response([
        {
            "id": r.id,
            "payroll_id": str(r.payroll_id),
            "token": r.token,
            "vault": r.vault,
            "merkle_root": r.merkle_root,
            "total": r.total,
            "total_amount_units": int(r.total_amount_units),
            "status": r.status,
            "create_tx_hash": r.create_tx_hash,
            "fund_tx_hash": r.fund_tx_hash,
            "claim_window_days": r.claim_window_days,
            "close_at": r.close_at,
            "created_at": r.created_at,
        }
        for r in qs
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_run_claims(request, run_id: int):
    employer, run, error = _require_run_for_employer(request.user, run_id)
    if error:
        return error

    claims = PayrollClaim.objects.filter(run=run).order_by("index")

    data = []
    for c in claims:
        salary_units = None
        try:
            emp = Employee.objects.get(employer=employer, wallet__iexact=c.employee_wallet)
            salary_units = int(emp.salary_units)
        except Employee.DoesNotExist:
            pass

        data.append(
            {
                "index": c.index,
                "employee_wallet": _norm_addr(c.employee_wallet),
                "status": c.status,
                "salary_units": salary_units,
                "leaf": c.leaf,
                "has_ciphertext": bool(c.net_ciphertext_b64),
                "claim_tx_hash": c.claim_tx_hash,
                "claimed_at": c.claimed_at,
            }
        )

    return Response(
        {
            "run_id": run.id,
            "payroll_id": str(run.payroll_id),
            "status": run.status,
            "merkle_root": run.merkle_root,
            "total": run.total,
            "total_amount_units": int(run.total_amount_units),
            "claims": data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def commit_run(request, run_id: int):
    _, run, error = _require_run_for_employer(request.user, run_id)
    if error:
        return error

    if run.status != "draft":
        return _json_error(f"Run status must be draft, got {run.status}")

    items = request.data.get("items", [])
    if not isinstance(items, list) or len(items) == 0:
        return _json_error("items must be a non-empty list")

    claims_qs = PayrollClaim.objects.filter(run=run).order_by("index")
    claims = list(claims_qs)

    if len(items) != len(claims):
        return _json_error(f"items length must equal run total ({len(claims)})")

    claim_by_wallet = {c.employee_wallet.lower(): c for c in claims}
    leaves = [None] * len(claims)

    for item in items:
        try:
            wallet = _norm_addr(item["wallet"])
        except Exception:
            return _json_error("Invalid wallet in items")

        ct_b64 = item.get("net_ciphertext_b64", "")
        if not ct_b64:
            return _json_error("Missing net_ciphertext_b64 for some item")

        encrypted_ref = item.get("encrypted_ref", ZERO_REF)
        if not isinstance(encrypted_ref, str) or not encrypted_ref.startswith("0x") or len(encrypted_ref) != 66:
            return _json_error("encrypted_ref must be bytes32 hex string")

        try:
            ct_bytes = base64.b64decode(ct_b64, validate=True)
        except Exception:
            return _json_error("Invalid base64 ciphertext")

        c = claim_by_wallet.get(wallet.lower())
        if not c:
            return _json_error(f"Wallet not found in this run: {wallet}")

        leaf = leaf_hash(run.payroll_id, c.index, wallet, run.token, ct_bytes, encrypted_ref)

        c.net_ciphertext_b64 = ct_b64
        c.encrypted_ref = encrypted_ref
        c.leaf = "0x" + leaf.hex()
        c.save(update_fields=["net_ciphertext_b64", "encrypted_ref", "leaf"])

        leaves[c.index] = leaf

    if any(x is None for x in leaves):
        return _json_error("Some indices missing ciphertext")

    tree = build_merkle_tree(leaves)
    root = merkle_root(tree)

    for c in claims:
        proof_bytes = merkle_proof(tree, c.index)
        c.proof = ["0x" + p.hex() for p in proof_bytes]
        c.save(update_fields=["proof"])

    run.merkle_root = "0x" + root.hex()
    run.status = "committed"
    run.save(update_fields=["merkle_root", "status"])

    return Response({"run_id": run.id, "payroll_id": str(run.payroll_id), "merkle_root": run.merkle_root, "total": run.total, "status": run.status})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_claim(request, payroll_id: int, wallet: str):
    try:
        normalized_wallet = _norm_addr(wallet)
    except Exception as ex:
        return _json_error(str(ex))

    run = PayrollRun.objects.filter(payroll_id=payroll_id).first()
    if not run:
        return _json_error("Run not found", status=404)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_wallet = (profile.wallet_address or "").lower()
    if user_wallet != normalized_wallet.lower():
        return _json_error("Not allowed to access this claim", status=403)

    claim = PayrollClaim.objects.filter(run=run, employee_wallet__iexact=normalized_wallet).first()
    if not claim:
        return _json_error("Claim not found", status=404)

    if run.status not in ["open", "funded"]:
        return _json_error(f"Run not open yet. status={run.status}", status=400)

    return Response(
        {
            "payroll_id": str(run.payroll_id),
            "index": int(claim.index),
            "token": run.token,
            "vault": run.vault,
            "net_ciphertext_b64": claim.net_ciphertext_b64,
            "encrypted_ref": claim.encrypted_ref,
            "proof": claim.proof,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tx_create_payroll(request, run_id: int):
    _, run, error = _require_run_for_employer(request.user, run_id)
    if error:
        return error

    if run.status != "committed":
        return _json_error(f"Run must be committed before createPayroll. status={run.status}")

    return Response(
        {
            "chainId": CHAIN_ID,
            "to": run.vault,
            "function": "createPayroll(uint256,address,bytes32,uint256)",
            "args": [str(run.payroll_id), run.token, run.merkle_root, str(run.total)],
            "valueWei": "0",
            "notes": ["Frontend encodes and signs using PayrollVault ABI"],
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tx_fund_plan(request, run_id: int):
    _, run, error = _require_run_for_employer(request.user, run_id)
    if error:
        return error

    amount_units = int(run.total_amount_units)

    if not WRAP_GATEWAY:
        wrap_note = "WRAP_GATEWAY env is missing. Set it to your deployed WrapGateway."
    else:
        wrap_note = "If employer only has public USDC, call WrapGateway.deposit(amount_units) first."

    return Response(
        {
            "run_id": run.id,
            "payroll_id": str(run.payroll_id),
            "vault": run.vault,
            "token": run.token,
            "amount_units": amount_units,
            "decimals": 6,
            "plan": [
                {"step": 1, "action": wrap_note, "contract": WRAP_GATEWAY, "function": "deposit(uint256 amount)", "args": [str(amount_units)], "valueWei": "0"},
                {
                    "step": 2,
                    "action": "Transfer private cUSDC from employer to PayrollVault using ciphertext",
                    "contract": run.token,
                    "function": "transfer(address to, bytes amountCiphertext)",
                    "args": [run.vault, "<amountCiphertext bytes>"],
                    "valueWei": "<inco_fee_wei>",
                    "notes": ["msg.value must pay inco.getFee() for the ciphertext op"],
                },
            ],
            "notes": ["Frontend should query inco.getFee() using Inco JS and pass it as tx value"],
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_run_tx(request, run_id: int):
    _, run, error = _require_run_for_employer(request.user, run_id)
    if error:
        return error

    kind = request.data.get("kind")
    tx_hash = request.data.get("tx_hash")

    if kind not in ["create_payroll", "fund_vault"]:
        return _json_error("kind must be create_payroll or fund_vault")
    if not tx_hash or not isinstance(tx_hash, str) or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return _json_error("Invalid tx_hash")

    if kind == "create_payroll":
        run.create_tx_hash = tx_hash
        run.save(update_fields=["create_tx_hash"])
    else:
        run.fund_tx_hash = tx_hash
        run.save(update_fields=["fund_tx_hash"])

    return Response({"run_id": run.id, "kind": kind, "tx_hash": tx_hash})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_claim_tx(request, run_id: int, index: int):
    run = PayrollRun.objects.filter(id=run_id).first()
    if not run:
        return _json_error("Run not found", status=404)

    tx_hash = request.data.get("tx_hash")
    wallet = request.data.get("wallet")

    if not tx_hash or not isinstance(tx_hash, str) or not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return _json_error("Invalid tx_hash")
    if not wallet:
        return _json_error("wallet is required")

    try:
        wallet = _norm_addr(wallet)
    except Exception as ex:
        return _json_error(str(ex))

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_wallet = (profile.wallet_address or "").lower()
    employer, _ = require_employer(request.user)
    is_employer = bool(employer and employer.id == run.employer_id)
    is_self = user_wallet == wallet.lower()

    if not is_employer and not is_self:
        return _json_error("Not allowed to record claim tx for this wallet", status=403)

    claim = PayrollClaim.objects.filter(run=run, index=index, employee_wallet__iexact=wallet).first()
    if not claim:
        return _json_error("Claim not found", status=404)

    claim.claim_tx_hash = tx_hash
    claim.save(update_fields=["claim_tx_hash"])

    return Response({"run_id": run.id, "index": index, "wallet": wallet, "tx_hash": tx_hash})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def open_run(request, run_id: int):
    _, run, error = _require_run_for_employer(request.user, run_id)
    if error:
        return error

    if run.status not in ["committed", "onchain_created", "funded"]:
        return _json_error(f"Run not ready. status={run.status}")

    if not run.create_tx_hash:
        return _json_error("create_tx_hash missing. Call record_run_tx for create_payroll")
    if not run.fund_tx_hash:
        return _json_error("fund_tx_hash missing. Call record_run_tx for fund_vault")

    try:
        create_receipt = w3.eth.get_transaction_receipt(run.create_tx_hash)
    except Exception:
        return _json_error("Could not fetch create tx receipt yet")

    if not receipt_has_payroll_created(create_receipt, run.payroll_id, run.token, run.merkle_root, run.total):
        return _json_error("createPayroll tx missing PayrollCreated event")

    run.status = "onchain_created"
    run.save(update_fields=["status"])

    try:
        fund_receipt = w3.eth.get_transaction_receipt(run.fund_tx_hash)
    except Exception:
        return _json_error("Could not fetch fund tx receipt yet")

    if not receipt_has_private_transfer_to_vault(fund_receipt):
        return _json_error("Funding tx does not include TransferPrivate to vault")

    run.status = "open"
    run.save(update_fields=["status"])

    return Response({"run_id": run.id, "status": run.status})
