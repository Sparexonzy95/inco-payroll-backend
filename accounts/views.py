import secrets
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone as django_timezone
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserProfile, WalletNonce
from orgs.models import Membership, Organization


APP_NAME = "Inco Payroll"


def _json_error(message: str, status: int = 400):
    return Response({"error": message}, status=status)


def _normalize_wallet(wallet: str) -> str:
    if not wallet or not isinstance(wallet, str):
        raise ValueError("wallet is required")
    wallet = wallet.strip()
    if len(wallet) != 42 or not wallet.startswith("0x"):
        raise ValueError("wallet must be a valid EVM address")
    return to_checksum_address(wallet)


def _membership_payload_for_user(user: User):
    rows = Membership.objects.filter(user=user).select_related("org")
    orgs = []
    roles = set()
    seen = set()

    for m in rows:
        roles.add(m.role)
        if m.org_id in seen:
            continue
        seen.add(m.org_id)
        orgs.append({"id": m.org_id, "name": m.org.name, "role": m.role})

    owned = Organization.objects.filter(owner=user).values("id", "name")
    for org in owned:
        roles.add("owner")
        if org["id"] in seen:
            continue
        seen.add(org["id"])
        orgs.append({"id": org["id"], "name": org["name"], "role": "owner"})

    return sorted(list(roles)), orgs


@api_view(["POST"])
@permission_classes([AllowAny])
def wallet_nonce(request):
    try:
        wallet = _normalize_wallet(request.data.get("wallet"))
    except ValueError as ex:
        return _json_error(str(ex))

    nonce = secrets.token_hex(16)
    issued_at = datetime.now(timezone.utc).isoformat()
    chain_id = request.data.get("chainId")

    message = (
        f"{APP_NAME} wallet login\n"
        f"domain: localhost\n"
        f"wallet: {wallet}\n"
        f"nonce: {nonce}\n"
        f"issuedAt: {issued_at}\n"
        f"chainId: {chain_id if chain_id is not None else 'any'}"
    )

    WalletNonce.objects.create(wallet=wallet, nonce=nonce, message=message)

    return Response({"wallet": wallet, "nonce": nonce, "message": message})


@api_view(["POST"])
@permission_classes([AllowAny])
def wallet_login(request):
    try:
        wallet = _normalize_wallet(request.data.get("wallet"))
    except ValueError as ex:
        return _json_error(str(ex))

    signature = request.data.get("signature")
    nonce = request.data.get("nonce")

    if not signature or not nonce:
        return _json_error("wallet, nonce, and signature are required")

    nonce_row = WalletNonce.objects.filter(
        wallet=wallet,
        nonce=nonce,
        consumed_at__isnull=True,
    ).order_by("-issued_at").first()

    if not nonce_row:
        return _json_error("Invalid or already used nonce", status=400)

    try:
        recovered = Account.recover_message(
            encode_defunct(text=nonce_row.message),
            signature=signature,
        )
        recovered = _normalize_wallet(recovered)
    except Exception:
        return _json_error("Signature verification failed", status=400)

    if recovered.lower() != wallet.lower():
        return _json_error("Signature does not match wallet", status=400)

    with transaction.atomic():
        nonce_row.consumed_at = django_timezone.now()
        nonce_row.save(update_fields=["consumed_at"])

        username = f"wallet_{wallet.lower()}"
        user, _ = User.objects.get_or_create(username=username)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.wallet:
            profile.wallet = wallet
            profile.save(update_fields=["wallet"])

    refresh = RefreshToken.for_user(user)
    roles, orgs = _membership_payload_for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "wallet": profile.wallet,
                "roles": roles,
                "orgs": orgs,
                "active_org_id": profile.active_org_id,
            },
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    roles, orgs = _membership_payload_for_user(request.user)

    return Response(
        {
            "user_id": request.user.id,
            "wallet": profile.wallet,
            "roles": roles,
            "active_org_id": profile.active_org_id,
            "orgs": orgs,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_active_org(request):
    org_id = request.data.get("org_id")
    if not org_id:
        return _json_error("org_id is required")

    membership = Membership.objects.filter(user=request.user, org_id=org_id).first()
    is_owner = Organization.objects.filter(id=org_id, owner=request.user).exists()

    if not membership and not is_owner:
        return _json_error("You are not a member of this organization", status=403)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.active_org_id = org_id
    profile.save(update_fields=["active_org"])

    role = "owner" if is_owner else membership.role
    return Response({"org_id": int(org_id), "role": role})
