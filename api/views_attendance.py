# api/views_attendance.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Attendances, Estudiantes
from .serializers import AttendanceSerializer

channel_layer = get_channel_layer()  # acceso global al layer de Channels

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendances.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [AllowAny]
    lookup_field = "asistencia_id"

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get("student_id")
        fecha = self.request.query_params.get("fecha")
        if student_id:
            qs = qs.filter(student__student_id=student_id)
        if fecha:
            qs = qs.filter(fecha=fecha)
        return qs

    @action(detail=False, methods=["get"], url_path="por_fecha/(?P<fecha>[^/.]+)/(?P<grado>[^/.]+)/(?P<seccion>[^/.]+)")
    def list_by_date(self, request, fecha=None, grado=None, seccion=None):
        qs = Attendances.objects.filter(fecha=fecha, grado=grado, seccion=seccion)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="historial/(?P<student_id>[^/.]+)")
    def history(self, request, student_id=None):
        qs = Attendances.objects.filter(student__student_id=student_id).order_by("-fecha")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="for_student_on_date")
    def for_student_on_date(self, request):
        student_id = request.query_params.get("student_id")
        fecha = request.query_params.get("fecha")
        if not student_id or not fecha:
            return Response({"detail": "student_id and fecha required"}, status=status.HTTP_400_BAD_REQUEST)
        qs = Attendances.objects.filter(student__student_id=student_id, fecha=fecha)
        if not qs.exists():
            return Response(None)
        serializer = self.get_serializer(qs.first())
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        self.notify_attendance_ws(instance)

    @staticmethod
    def notify_attendance_ws(attendance_instance):
        """
        Envía la asistencia recién creada al grupo WebSocket correspondiente
        """
        if not channel_layer:
            return

        serializer = AttendanceSerializer(attendance_instance)
        payload = serializer.data
        group_name = f"attendances_{attendance_instance.fecha.isoformat()}"

        # async_to_sync para llamar desde sync a async
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "attendance_message",  # coincide con tu consumer
                "payload": payload,
            }
        )
