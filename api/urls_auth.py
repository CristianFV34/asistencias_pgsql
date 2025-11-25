from django.urls import path
from .views_auth import *

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),

    path("usuario/<uuid:uid>/", GetUsuarioView.as_view()),
    path("usuario/create/", CreateUserView.as_view()),
    path("usuario/<uuid:uid>/activate/", SetUserActiveView.as_view()),
    path("usuario/<uuid:uid>/delete/", DeleteUserView.as_view()),

    path("usuarios/role/<rol>/active/", UsersByRoleActiveView.as_view()),
    path("usuarios/role/<rol>/inactive/", UsersByRoleInactiveView.as_view()),

    path("director-exists/", DirectorExistsView.as_view()),

    path("change-password/", ChangePasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),

    path("email-exists/", EmailExistsView.as_view()),
]
