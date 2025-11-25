from rest_framework import serializers
from .models import *


class UsuarioSerializer(serializers.ModelSerializer):
    uid = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

    class Meta:
        model = Usuarios
        fields = [
            "uid",
            "rol",
            "nombre",
            "correo",
            "telefono",
            "fecha_creacion",
            "activo",
            "extra_data",
            "created_at",
            "updated_at",
        ]

    def get_uid(self, obj):
        return str(obj.user_id)  # PK del OneToOne

    def get_extra_data(self, obj):
        return obj.datos_adicionales

class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salones
        fields = [
            "salon_id",
            "grado",
            "seccion",
            "nombre",
            "teacher_uid",
            "activo",
        ]


class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiantes
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    fecha_registro_profesor = serializers.DateTimeField(source="fecha_registro_profesor", required=False, allow_null=True)
    fecha_registro_aux = serializers.DateTimeField(source="fecha_registro_aux", required=False, allow_null=True)
    observaciones_aux = serializers.CharField(source="observaciones_aux", required=False, allow_blank=True, allow_null=True)

    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    campus_name = serializers.CharField(required=False, allow_blank=True)
    address_full = serializers.CharField(required=False, allow_blank=True)
    address_short = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Attendances
        fields = [
            "asistencia_id",
            "student_id",
            "fecha",
            "status",
            "profesor_uid",
            "grado",
            "seccion",
            "observaciones",
            "justificacion",
            "fecha_registro",
            "registrado_por_uid",
            "fecha_registro_profesor",
            "fecha_registro_aux",
            "observaciones_aux",
            "latitude",
            "longitude",
            "campus_name",
            "address_full",
            "address_short",
            "entrada",
            "salida",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"


class StaffAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAttendance
        fields = "__all__"


class TeacherAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherAssignments
        fields = [
            "id",
            "teacher_uid",
            "grado",
            "seccion",
            "fecha_asignacion",
            "activo",
        ]
        read_only_fields = ["fecha_asignacion"]






