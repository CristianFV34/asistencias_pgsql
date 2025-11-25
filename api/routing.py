# api/routing.py
from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/attendances/(?P<date>\d{4}-\d{2}-\d{2})/$", consumers.AttendanceConsumer.as_asgi()),
    path("ws/notifications/", consumers.NotificationsConsumer.as_asgi()),
]
