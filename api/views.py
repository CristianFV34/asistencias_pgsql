from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from models import *
from serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.
# ---------------------------
# Auth endpoints
# ---------------------------

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    # uses SimpleJWT built-in serializer; endpoint: /api/auth/login/


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            if refresh:
                RefreshToken(refresh).blacklist()
        except Exception:
            pass
        return Response({"ok": True})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"detail": "new_password required"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"ok": True})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Implement sending email or token flow here. For now, we simulate success.
        email = request.data.get("email")
        # TODO: implement actual email/password reset
        return Response({"email_sent": True})


# ---------------------------
# Usuarios (director check + create + crud)
# ---------------------------

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]  # adjust to IsAuthenticated + role checks in production
    lookup_field = "uid"

    @action(detail=False, methods=["get"], url_path="director-exists")
    def director_exists(self, request):
        exists = Usuarios.objects.filter(rol="director", activo=True).exists()
        return Response({"exists": exists})

    @action(detail=False, methods=["get"], url_path="by-role/(?P<rol>[^/.]+)/active")
    def by_role_active(self, request, rol=None):
        users = Usuarios.objects.filter(rol=rol, activo=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-role/(?P<rol>[^/.]+)/inactive")
    def by_role_inactive(self, request, rol=None):
        users = Usuarios.objects.filter(rol=rol, activo=False)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, uid=None):
        active = request.data.get("active", True)
        Usuarios.objects.filter(uid=uid).update(activo=active)
        return Response({"ok": True})


# ---------------------------
# Salones
# ---------------------------

class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salones.objects.all()
    serializer_class = SalonSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"], url_path="by-teacher/(?P<teacher_uid>[^/.]+)")
    def by_teacher(self, request, teacher_uid=None):
        q = Salones.objects.filter(teacher_uid=teacher_uid, activo=True)
        return Response(SalonSerializer(q, many=True).data)


# ---------------------------
# Estudiantes
# ---------------------------

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiantes.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [AllowAny]
    lookup_field = "student_id"

    @action(detail=False, methods=["get"], url_path="by_grade/(?P<grado>[^/.]+)/(?P<seccion>[^/.]+)")
    def by_grade(self, request, grado=None, seccion=None):
        q = Estudiantes.objects.filter(grado=grado, salon__salon_id__exact=request.query_params.get("salon_id", None) if False else None)
        # simpler: filter by grado and seccion
        q = Estudiantes.objects.filter(grado=grado, grado__isnull=False, activo=True)
        q = Estudiantes.objects.filter(grado=grado, activo=True)
        # If you want to match seccion use related Salon if needed. We assume Estudiantes has salon FK.
        q = Estudiantes.objects.filter(grado=grado, salon__seccion=seccion, activo=True)
        return Response(self.get_serializer(q, many=True).data)

    @action(detail=False, methods=["get"], url_path="by_parent/(?P<padre_uid>[^/.]+)")
    def by_parent(self, request, padre_uid=None):
        q = Estudiantes.objects.filter(padre_uid=padre_uid, activo=True)
        return Response(self.get_serializer(q, many=True).data)

    @action(detail=False, methods=["get"], url_path="by_teacher/(?P<teacher_uid>[^/.]+)")
    def by_teacher(self, request, teacher_uid=None):
        q = Estudiantes.objects.filter(profesor_uid=teacher_uid, activo=True)
        return Response(self.get_serializer(q, many=True).data)

    @action(detail=False, methods=["get"], url_path="grades")
    def grades(self, request):
        # distinct grados
        grados = Estudiantes.objects.exclude(grado="").order_by("grado").values_list("grado", flat=True).distinct()
        return Response(list(grados))

    @action(detail=False, methods=["get"], url_path="sections/(?P<grado>[^/.]+)")
    def sections_by_grade(self, request, grado=None):
        secciones = Estudiantes.objects.filter(grado=grado).exclude(seccion="").order_by("seccion").values_list("seccion", flat=True).distinct()
        return Response(list(secciones))


# ---------------------------
# Attendances
# ---------------------------

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendances.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [AllowAny]
    lookup_field = "asistencia_id"

    def get_queryset(self):
        qs = super().get_queryset()
        # Allow query params: student_id, fecha
        student_id = self.request.query_params.get("student_id")
        fecha = self.request.query_params.get("fecha")
        if student_id:
            qs = qs.filter(student__student_id=student_id)
        if fecha:
            qs = qs.filter(fecha=fecha)
        return qs

    @action(detail=False, methods=["get"], url_path="por_fecha/(?P<fecha>[^/.]+)/(?P<grado>[^/.]+)/(?P<seccion>[^/.]+)")
    def by_date_grade_section(self, request, fecha=None, grado=None, seccion=None):
        q = Attendances.objects.filter(fecha=fecha, grado=grado, seccion=seccion)
        return Response(self.get_serializer(q, many=True).data)

    @action(detail=True, methods=["get"], url_path="historial")
    def historial(self, request, asistencia_id=None):
        # asistencia_id param here is student's uuid in this route design
        student_id = asistencia_id
        q = Attendances.objects.filter(student__student_id=student_id).order_by("-fecha")
        return Response(self.get_serializer(q, many=True).data)


# ---------------------------
# Staff Attendance
# ---------------------------

class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.all()
    serializer_class = StaffAttendanceSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        roles_param = request.query_params.getlist("roles")
        date = request.query_params.get("date", timezone.now().date().isoformat())
        qs = StaffAttendance.objects.filter(fecha=date)
        if roles_param:
            qs = qs.filter(rol__in=roles_param)
        return Response(self.get_serializer(qs, many=True).data)


# ---------------------------
# Notifications
# ---------------------------

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notifications.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    @action(detail=False, methods=["get"], url_path="usuario/(?P<uid>[^/.]+)")
    def by_user(self, request, uid=None):
        q = Notifications.objects.filter(destinatario_uid=uid).order_by("-fecha_creacion")
        return Response(self.get_serializer(q, many=True).data)

    @action(detail=False, methods=["get"], url_path="por_estudiante/(?P<student_id>[^/.]+)")
    def by_student(self, request, student_id=None):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        q = Notifications.objects.filter(estudiante_id=student_id)
        if start:
            q = q.filter(fecha_creacion__gte=start)
        if end:
            q = q.filter(fecha_creacion__lte=end)
        q = q.order_by("-fecha_creacion")
        return Response(self.get_serializer(q, many=True).data)

    @action(detail=True, methods=["post"], url_path="mark_read")
    def mark_read(self, request, id=None):
        Notifications.objects.filter(id=id).update(leida=True)
        return Response({"ok": True})