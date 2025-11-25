# api/views_notifications.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Notifications
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
     - /api/notificaciones/                        (list, create)
     - /api/notificaciones/{id}/                   (retrieve, update, delete)
     - /api/notificaciones/usuario/{uid}/          (list for user)
     - /api/notificaciones/por_estudiante/{id}/    (list for student with date filters)
     - /api/notificaciones/{id}/mark_read/         (mark single notification as read)
    """
    queryset = Notifications.objects.all().order_by("-fecha_creacion")
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @action(detail=False, methods=["get"], url_path="usuario/(?P<uid>[^/.]+)")
    def list_user(self, request, uid=None):
        qs = Notifications.objects.filter(destinatario_uid=uid).order_by("-fecha_creacion")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="por_estudiante/(?P<student_id>[^/.]+)")
    def by_student(self, request, student_id=None):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        qs = Notifications.objects.filter(estudiante_id=student_id)
        if start:
            qs = qs.filter(fecha_creacion__gte=start)
        if end:
            qs = qs.filter(fecha_creacion__lte=end)
        qs = qs.order_by("-fecha_creacion")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="mark_read")
    def mark_read(self, request, id=None):
        Notifications.objects.filter(id=id).update(leida=True)
        return Response({"ok": True})
