import secrets
from payroll.models import PayrollRun

def generate_payroll_id(max_tries: int = 10) -> int:
    """
    Generates a unique uint256-like integer for payroll_id.
    SQLite stores it fine as BigInteger.
    Uses randomness + uniqueness check.
    """
    for _ in range(max_tries):
        # 96 bits is more than enough, still comfortably fits BigInteger.
        pid = secrets.randbits(96)
        if pid == 0:
            continue
        if not PayrollRun.objects.filter(payroll_id=pid).exists():
            return pid

    # Extremely unlikely to ever happen, but we handle it.
    raise RuntimeError("Could not generate unique payroll_id")
