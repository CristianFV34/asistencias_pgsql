from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid
from django.contrib.auth.models import User

# Create your models here.
# ==========================
# ENUMS (choices)
# ==========================

class NotificationType(models.TextChoices):
    COMUNICADO = "comunicado", "Comunicado"
    ADVERTENCIA = "advertencia", "Advertencia"
    RECORDATORIO = "recordatorio", "Recordatorio"
    # agrega más si existen en tu schema original


class UserRole(models.TextChoices):
    DIRECTOR = "director", "Director"
    PADRE = "padre", "Padre"
    PROFESOR = "profesor", "Profesor"
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    # agrega más si existen en tu schema original


class AttendanceStatus(models.TextChoices):
    PRESENTE = "presente", "Presente"
    TARDE = "tarde", "Tarde"
    FALTA = "falta", "Falta"
    JUSTIFICADO = "justificado", "Justificado"
    # agrega más si existen según supabase

# ==========================
# TABLA: SALONES
# ==========================
class Salones(models.Model):
    salon_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grado = models.TextField()
    seccion = models.TextField()
    nombre = models.TextField()
    teacher_uid = models.TextField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "salones"
        indexes = [
            models.Index(fields=["grado", "seccion"]),
            models.Index(fields=["teacher_uid"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return f"{self.grado} - {self.seccion} ({self.nombre})"

# ==========================
# TABLA: NOTIFICATIONS
# ==========================
class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.TextField()
    mensaje = models.TextField()
    tipo = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.COMUNICADO,
    )
    destinatario_uid = models.TextField()
    estudiante_id = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    enviada = models.BooleanField(default=False)
    datos_adicionales = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["destinatario_uid"]),
            models.Index(fields=["estudiante_id"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["-fecha_creacion"]),
        ]

# ==========================
# TABLA: STAFF_ATTENDANCE
# ==========================
class StaffAttendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_uid = models.TextField()
    rol = models.CharField(max_length=20, choices=UserRole.choices)
    tipo = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    campus_name = models.TextField(null=True, blank=True)
    address_full = models.TextField(null=True, blank=True)
    address_short = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff_attendance"
        indexes = [
            models.Index(fields=["staff_uid"]),
            models.Index(fields=["fecha"]),
            models.Index(fields=["rol"]),
        ]

# ==========================
# TABLA: TEACHER_ASSIGNMENTS
# ==========================
class TeacherAssignments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher_uid = models.TextField()
    grado = models.TextField()
    seccion = models.TextField()
    fecha_asignacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_assignments"
        indexes = [
            models.Index(fields=["teacher_uid"]),
            models.Index(fields=["grado", "seccion"]),
            models.Index(fields=["activo"]),
        ]

# ==========================
# TABLA: USUARIOS
# ==========================

class Usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    rol = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PADRE,
    )
    nombre = models.TextField()
    correo = models.TextField(unique=True)
    telefono = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    datos_adicionales = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "usuarios"
        indexes = [
            models.Index(fields=["rol"]),
            models.Index(fields=["activo"]),
            models.Index(fields=["nombre"]),
        ]

    def __str__(self):
        return self.nombre


# ==========================
# TABLA: ESTUDIANTES
# ==========================

class Estudiantes(models.Model):
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.TextField()
    apellido = models.TextField()
    grado = models.TextField()
    salon = models.ForeignKey(Salones, on_delete=models.CASCADE, db_column="salon_id")
    padre_uid = models.TextField()
    profesor_uid = models.TextField(null=True, blank=True)
    fecha_nacimiento = models.DateField()
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    datos_medicos = models.JSONField(null=True, blank=True)
    codigo = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "estudiantes"
        indexes = [
            models.Index(fields=["salon"]),
            models.Index(fields=["padre_uid"]),
            models.Index(fields=["profesor_uid"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return self.nombre


# ==========================
# TABLA: ATTENDANCES
# ==========================

class Attendances(models.Model):
    asistencia_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Estudiantes, on_delete=models.CASCADE, db_column="student_id")
    fecha = models.DateField()
    entrada = models.TimeField(null=True, blank=True)
    salida = models.TimeField(null=True, blank=True)
    registrado_por_uid = models.TextField()
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices, null=True, blank=True)
    profesor_uid = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    observaciones_aux = models.TextField(null=True, blank=True)
    justificacion = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_registro_profesor = models.DateTimeField(null=True, blank=True)
    fecha_registro_aux = models.DateTimeField(null=True, blank=True)
    grado = models.TextField(null=True, blank=True)
    seccion = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    campus_name = models.TextField(null=True, blank=True)
    address_full = models.TextField(null=True, blank=True)
    address_short = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "attendances"
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["fecha"]),
            models.Index(fields=["registrado_por_uid"]),
            models.Index(fields=["status"]),
        ]