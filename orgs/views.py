from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orgs.models import Organization, Membership

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_my_orgs(request):
    user = request.user

    owned = Organization.objects.filter(owner=user).values("id", "name")
    member_rows = Membership.objects.filter(user=user).select_related("org")

    data = []
    seen = set()

    for o in owned:
        if o["id"] in seen:
            continue
        seen.add(o["id"])
        data.append({"id": o["id"], "name": o["name"], "role": "owner"})

    for m in member_rows:
        oid = m.org_id
        if oid in seen:
            continue
        seen.add(oid)
        data.append({"id": oid, "name": m.org.name, "role": m.role})

    return Response(data)
