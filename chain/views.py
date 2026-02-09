import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orgs.models import Organization
from .models import ChainTx

CHAIN_ID = int(os.getenv("CHAIN_ID", "84532"))

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_tx(request):
    org_id = request.data["org_id"]
    tx_hash = request.data["tx_hash"]
    kind = request.data["kind"]  # create_payroll, fund_vault, claim
    run_id = request.data.get("run_id")
    payroll_id = request.data.get("payroll_id")
    employee_wallet = request.data.get("employee_wallet", "")

    org = Organization.objects.get(id=org_id)

    obj, created = ChainTx.objects.get_or_create(
        tx_hash=tx_hash,
        defaults={
            "org": org,
            "chain_id": CHAIN_ID,
            "kind": kind,
            "run_id": run_id,
            "payroll_id": payroll_id,
            "employee_wallet": employee_wallet,
            "status": "pending",
            "meta": request.data.get("meta", {}),
        }
    )

    return Response({
        "tx_hash": obj.tx_hash,
        "status": obj.status,
        "created": created
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_txs(request):
    org_id = request.query_params.get("org_id")
    qs = ChainTx.objects.filter(org_id=org_id).order_by("-created_at")[:100]
    data = []
    for t in qs:
        data.append({
            "tx_hash": t.tx_hash,
            "kind": t.kind,
            "status": t.status,
            "run_id": t.run_id,
            "payroll_id": str(t.payroll_id) if t.payroll_id else None,
            "employee_wallet": t.employee_wallet,
            "block_number": t.block_number,
            "success": t.success,
            "updated_at": t.updated_at,
        })
    return Response(data)
