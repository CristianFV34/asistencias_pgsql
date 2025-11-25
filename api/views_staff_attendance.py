from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StaffAttendance
from .serializers import StaffAttendanceSerializer
from django.utils.timezone import datetime

class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.all()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="today")
    def get_today(self, request):
        date = request.query_params.get("date")
        roles = request.query_params.getlist("roles")

        # 🔥 IMPORTANTE: SIEMPRE LISTA
        if not date:
            return Response([], status=200)

        qs = StaffAttendance.objects.filter(fecha_registro=date)

        if roles:
            qs = qs.filter(rol__in=roles)

        data = StaffAttendanceSerializer(qs, many=True).data
        return Response(data)

