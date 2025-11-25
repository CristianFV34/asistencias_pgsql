import uuid
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .models import Usuarios, UserRole
from .serializers import UsuarioSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# =============================================================
# Login (equivalente a supabase.auth.signInWithPassword)
# =============================================================
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return Response({"error": "Usuario no existe"}, status=404)

        auth = authenticate(username=email, password=password)
        if not auth:
            return Response({"error": "Credenciales incorrectas"}, status=401)

        tokens = generate_tokens(auth)

        # Obtener datos desde modelo Usuarios
        try:
            usuario = Usuarios.objects.get(user=auth)
            usuario_data = UsuarioSerializer(usuario).data
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario no tiene perfil"}, status=400)

        return Response({
            "tokens": tokens,
            "user": usuario_data
        })

# =============================================================
# Logout
# =============================================================
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            RefreshToken(refresh).blacklist()
        except Exception:
            pass
        return Response({"ok": True})
        

# =============================================================
# Obtener usuario por UID
# =============================================================
class GetUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        try:
            usuario = Usuarios.objects.get(user_id=uid)
            return Response(UsuarioSerializer(usuario).data)
        except Usuarios.DoesNotExist:
            return Response(None)


# =============================================================
# Crear usuario (solo director)
# =============================================================
class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get("correo")
        password = request.data.get("password")
        nombre = request.data.get("nombre")
        rol = request.data.get("rol")
        datos = request.data.get("datos_adicionales")

        # 1️⃣ Validar antes de crear auth_user
        if rol == "director":
            if Usuarios.objects.filter(rol="director").exists():
                return Response({"error": "Ya existe un director."}, 403)
        else:
            if not request.user.is_authenticated:
                return Response({"error": "Autenticación requerida."}, 401)

        # 2️⃣ Crear auth_user
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=password
        )

        # 3️⃣ Crear registro en tabla Usuarios
        usuario = Usuarios.objects.create(
            user=user,
            correo=correo,
            nombre=nombre,
            rol=rol,
            datos_adicionales=datos
        )

        return Response(UsuarioSerializer(usuario).data, 201)

# =============================================================
# Cambiar contraseña
# =============================================================
class ChangePasswordView(APIView):
    def post(self, request):
        user = request.user
        new_pass = request.data.get("password")
        user.set_password(new_pass)
        user.save()
        return Response({"ok": True})


# =============================================================
# Reset password (solo simulado)
# =============================================================
class ResetPasswordView(APIView):
    def post(self, request):
        return Response({"email_sent": True})


# =============================================================
# Director Setup
# =============================================================
class DirectorExistsView(APIView):
    def get(self, request):
        exists = Usuarios.objects.filter(rol="director", activo=True).exists()
        return Response({"exists": exists})


# =============================================================
# Usuarios por rol
# =============================================================
class UsersByRoleActiveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, rol):
        users = Usuarios.objects.filter(rol=rol, activo=True)
        return Response(UsuarioSerializer(users, many=True).data)


class UsersByRoleInactiveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, rol):
        users = Usuarios.objects.filter(rol=rol, activo=False)
        return Response(UsuarioSerializer(users, many=True).data)


# =============================================================
# Activar / Desactivar usuario
# =============================================================
class SetUserActiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        active = request.data.get("activo")
        Usuarios.objects.filter(uid=uid).update(activo=active)
        return Response({"ok": True})


# =============================================================
# Eliminar usuario
# =============================================================
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, uid):
        try:
            Usuarios.objects.filter(uid=uid).delete()
            User.objects.filter(id=uid).delete()
        except Exception:
            pass
        return Response({"deleted": True})
    
class EmailExistsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"error": "email requerido"}, status=400)

        exists = User.objects.filter(email=email).exists()
        return Response({"exists": exists})
