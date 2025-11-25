# api/views_staff_logs.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone

from .models import StaffAttendance
from .serializers import StaffAttendanceSerializer

class StaffLogViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
     - /api/staff_logs/              (list, create)
     - /api/staff_logs/{id}/         (retrieve, update, delete)
     - /api/staff_logs/today/?roles=&date=
    """
    queryset = StaffAttendance.objects.all()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        date = request.query_params.get("date", timezone.now().date().isoformat())
        roles = request.query_params.getlist("roles")
        qs = StaffAttendance.objects.filter(fecha=date)
        if roles:
            qs = qs.filter(rol__in=roles)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
