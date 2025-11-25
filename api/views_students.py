# api/views_students.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # change to IsAuthenticated in production

from .models import Estudiantes, Salones
from .serializers import EstudianteSerializer

class StudentViewSet(viewsets.ModelViewSet):
    """
    Endpoints:
     - /api/estudiantes/               (list, create)
     - /api/estudiantes/{student_id}/  (retrieve, update, destroy)
     - /api/estudiantes/by_grade/{grado}/{seccion}/
     - /api/estudiantes/by_parent/{padre_uid}/
     - /api/estudiantes/by_teacher/{teacher_uid}/
     - /api/estudiantes/grades/
     - /api/estudiantes/sections/{grado}/
    """
    queryset = Estudiantes.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [AllowAny]

    lookup_field = "student_id"

    @action(detail=False, methods=["get"], url_path="by_grade/(?P<grado>[^/.]+)/(?P<seccion>[^/.]+)")
    def list_by_grade(self, request, grado=None, seccion=None):
        qs = Estudiantes.objects.filter(
            grado=grado,
            salon__seccion=seccion,
            activo=True
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=["get"], url_path="by_parent/(?P<padre_uid>[^/.]+)")
    def list_by_parent(self, request, padre_uid=None):
        qs = Estudiantes.objects.filter(padre_uid=padre_uid, activo=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by_teacher/(?P<teacher_uid>[^/.]+)")
    def list_by_teacher(self, request, teacher_uid=None):
        qs = Estudiantes.objects.filter(profesor_uid=teacher_uid, activo=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="grades")
    def grades(self, request):
        grados = Estudiantes.objects.exclude(grado="").order_by("grado").values_list("grado", flat=True).distinct()
        return Response(list(grados))

    @action(detail=False, methods=["get"], url_path="sections/(?P<grado>[^/.]+)")
    def sections_by_grade(self, request, grado=None):
        # if 'seccion' exists on Estudiantes, use it; otherwise use related Salon
        secciones = Estudiantes.objects.filter(grado=grado).exclude(salon__seccion="").order_by("salon__seccion").values_list("salon__seccion", flat=True).distinct()
        return Response(list(secciones))
    
    @action(detail=False, methods=["get"], url_path="by_salon")
    def by_salon(self, request):
        salon_id = request.GET.get("salon")

        if not salon_id:
            return Response({"error": "salon es requerido"}, status=400)

        try:
            estudiantes = Estudiantes.objects.filter(
                salon_id=salon_id,
                activo=True
            )
        except Exception:
            return Response({"error": "salon inválido"}, status=400)

        serializer = self.get_serializer(estudiantes, many=True)
        return Response(serializer.data)


