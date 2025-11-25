from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models import Salones
from api.serializers import SalonSerializer


class SalonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint:
      - GET /api/salones/        → lista todos
      - GET /api/salones/<id>/   → detalle
    """

    queryset = Salones.objects.filter(activo=True).order_by("grado", "seccion")
    serializer_class = SalonSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Si quieres filtrar por grado desde Flutter:
    @action(detail=False, methods=["get"])
    def by_grado(self, request):
        grado = request.GET.get("grado")
        if not grado:
            return Response({"error": "grado es requerido"}, status=400)

        salones = Salones.objects.filter(grado=grado, activo=True)
        serializer = self.get_serializer(salones, many=True)
        return Response(serializer.data)
