# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import AttendanceSerializer

@receiver(post_save, sender=Attendances)
def attendance_saved(sender, instance, created, **kwargs):
    # serializa la instancia
    data = AttendanceSerializer(instance).data
    # usa la fecha (YYYY-MM-DD) como group key
    date = instance.fecha.isoformat()  # assuming instance.fecha is date
    group_name = f"attendances_{date}"

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "attendance_message",
            "payload": {
                "event": "created" if created else "updated",
                "attendance": data,
            },
        },
    )

@receiver(post_save, sender=Notifications)
def notify_user(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    data = {
        "id": instance.id,
        "titulo": instance.titulo,
        "mensaje": instance.mensaje,
        "destinatario_uid": instance.destinatario_uid,
        "estudiante_id": instance.estudiante_id,
        "fecha_creacion": instance.fecha_creacion.isoformat(),
        "leida": instance.leida,
        "enviada": instance.enviada,
        "tipo": instance.tipo,
        "datos_adicionales": instance.datos_adicionales or {}
    }

    group = f"user_{instance.destinatario_uid}"

    async_to_sync(channel_layer.group_send)(
        group,
        {
            "type": "send_notification",
            "data": data,
        }
    )
