from rest_framework.views import APIView

from admin_app.authentication import AdminJWTAuthentication
from admin_app.services.dashboard_service import DashboardService
from admin_app.utils import IsSuperUser
from admin_app.views.auth import _auth_response


class AdminDashboardView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 15))
        except (TypeError, ValueError):
            days = 15
        days = max(1, min(days, 90))

        data = DashboardService.summary(days=days)

        return _auth_response(
            "Dashboard summary fetched.",
            data=data,
        )
