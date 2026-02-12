import secrets
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone as django_timezone
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Employer, UserProfile, WalletNonce

APP_NAME = "Inco Payroll"
APP_DOMAIN = "localhost"


def _json_error(message: str, status: int = 400):
    return Response({"error": message}, status=status)


def _normalize_wallet(wallet: str) -> str:
    if not wallet or not isinstance(wallet, str):
        raise ValueError("wallet is required")
    wallet = wallet.strip()
    if len(wallet) != 42 or not wallet.startswith("0x"):
        raise ValueError("wallet must be a valid EVM address")
    return to_checksum_address(wallet)


def _employer_payload(employer: Employer):
    return {
        "id": employer.id,
        "name": employer.name,
        "email": employer.email,
        "wallet_address": employer.wallet_address,
        "is_active": employer.is_active,
        "created_at": employer.created_at,
    }


def _me_payload(wallet: str):
    employer = Employer.objects.filter(wallet_address__iexact=wallet).first() if wallet else None
    if employer and employer.is_active:
        return {
            "wallet": wallet,
            "is_employer_registered": True,
            "employer": _employer_payload(employer),
        }

    return {
        "wallet": wallet,
        "is_employer_registered": False,
        "employer": None,
    }


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
        f"domain: {APP_DOMAIN}\n"
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

    with transaction.atomic():
        nonce_row = (
            WalletNonce.objects.select_for_update()
            .filter(wallet=wallet, nonce=nonce, consumed_at__isnull=True)
            .order_by("-issued_at")
            .first()
        )
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

        nonce_row.consumed_at = django_timezone.now()
        nonce_row.save(update_fields=["consumed_at"])

        username = f"wallet_{wallet.lower()}"
        user, _ = User.objects.get_or_create(username=username)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        changed = False
        if profile.wallet_address != wallet:
            profile.wallet_address = wallet
            changed = True

        employer = Employer.objects.filter(wallet_address__iexact=wallet).first()
        if employer and profile.employer_id != employer.id:
            profile.employer = employer
            changed = True

        if changed:
            profile.save()

    refresh = RefreshToken.for_user(user)

    response_payload = _me_payload(wallet)
    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": response_payload,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return Response(_me_payload(profile.wallet_address))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def employer_register(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    wallet = profile.wallet_address
    if not wallet:
        return _json_error("Wallet not found for authenticated user", status=400)

    name = (request.data.get("name") or "").strip()
    email = (request.data.get("email") or "").strip().lower()
    if not name or not email:
        return _json_error("name and email are required")

    existing_by_email = Employer.objects.filter(email__iexact=email).exclude(wallet_address__iexact=wallet).first()
    if existing_by_email:
        return _json_error("email is already in use", status=400)

    employer = Employer.objects.filter(wallet_address__iexact=wallet).first()
    if employer and not employer.is_active:
        return _json_error("Employer account is inactive", status=403)

    if employer:
        employer.name = name
        employer.email = email
        employer.save(update_fields=["name", "email"])
    else:
        employer = Employer.objects.create(name=name, email=email, wallet_address=wallet)

    if profile.employer_id != employer.id:
        profile.employer = employer
        profile.save(update_fields=["employer"])

    return Response(_me_payload(wallet))
