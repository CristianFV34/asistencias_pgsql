from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_students import StudentViewSet
from .views_attendance import AttendanceViewSet
from .views_notifications import NotificationViewSet
from .views_staff_logs import StaffLogViewSet
from .views_staff_attendance import StaffAttendanceViewSet
from .views_salones import SalonViewSet
from .views_teacher_assignments import TeacherAssignmentViewSet

router = DefaultRouter()
router.register("estudiantes", StudentViewSet, basename="estudiantes")
router.register("asistencias", AttendanceViewSet, basename="asistencias")
router.register("notificaciones", NotificationViewSet, basename="notificaciones")
router.register("staff_logs", StaffLogViewSet, basename="staff_logs")
router.register("staff_attendance", StaffAttendanceViewSet, basename="staff_attendance")
router.register("salones", SalonViewSet, basename="salones")
router.register(r'asignaciones', TeacherAssignmentViewSet, basename='asignaciones')

urlpatterns = [
    # --- AUTENTICACIÓN (JWT) ---
    path("auth/", include("api.urls_auth")),

    # --- RUTAS REST GENERADAS POR DRF ---
    path("", include(router.urls)),

    # =============================
    # RUTAS PERSONALIZADAS (OPCIÓN A)
    # =============================

    # Listar estudiantes por grado y salón
    path(
        "estudiantes/by_grade/<str:grado>/<str:salon>/",
        StudentViewSet.as_view({"get": "list_by_grade"}),
        name="estudiantes-by-grade"
    ),

    # Listar estudiantes por apoderado
    path(
        "estudiantes/by_parent/<uuid:padre_uid>/",
        StudentViewSet.as_view({"get": "list_by_parent"}),
        name="estudiantes-by-parent"
    ),

    # Asistencias por fecha, grado y sección
    path(
        "asistencias/por_fecha/<str:fecha>/<str:grado>/<str:seccion>/",
        AttendanceViewSet.as_view({"get": "list_by_date"}),
        name="asistencias-por-fecha"
    ),

    # Historial de asistencias de un estudiante
    path(
        "asistencias/historial/<uuid:student_id>/",
        AttendanceViewSet.as_view({"get": "history"}),
        name="asistencias-historial"
    ),

    # Notificaciones por usuario
    path(
        "notificaciones/usuario/<uuid:user_uid>/",
        NotificationViewSet.as_view({"get": "list_user"}),
        name="notificaciones-usuario"
    ),

    # Asignaciones por profesor
    path(
        "asignaciones/by_teacher/<str:teacher_uid>/",
        TeacherAssignmentViewSet.as_view({"get": "list_by_teacher"}),
        name="asignaciones-by-teacher"
    ),

    # Desactivar asignación
    path(
        "asignaciones/<uuid:pk>/deactivate/",
        TeacherAssignmentViewSet.as_view({"put": "deactivate"}),
        name="asignaciones-deactivate"
    ),

]
