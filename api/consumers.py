# api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from api.models import *

User = get_user_model()

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # path param date from scope['url_route']['kwargs']
        self.date = self.scope['url_route']['kwargs']['date']  # '2025-11-19'
        self.group_name = f"attendances_{self.date}"

        # token from querystring ?token=...
        query = parse_qs(self.scope["query_string"].decode())
        token_list = query.get("token") or query.get("access_token")
        token = token_list[0] if token_list else None

        # Authenticate token (SimpleJWT)
        if not token:
            await self.close(code=4001)
            return

        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
        except (TokenError, InvalidToken, Exception):
            await self.close(code=4002)
            return

        self.scope["user"] = user  # optional: let scope have user

        # Accept and add to group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # (optional) send initial state
        await self.send(json.dumps({"type": "connected", "date": self.date}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive messages from group
    async def attendance_message(self, event):
        # event should contain 'type': 'attendance_message' and 'payload'
        payload = event.get("payload")
        await self.send(text_data=json.dumps(payload))

    # If client sends a message (optional)
    async def receive(self, text_data=None, bytes_data=None):
        # ignore or handle client messages
        pass

class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope["query_string"].decode().replace("token=", "")
        
        user = await self.authenticate(token)

        if not user or isinstance(user, AnonymousUser):
            await self.close()
            return
        
        self.user = user
        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except:
            pass

    async def receive(self, text_data):
        pass  # No recibimos nada desde el cliente Flutter

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def authenticate(self, token):
        try:
            return User.objects.get(auth_token=token)
        except:
            return None