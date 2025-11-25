from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import TeacherAssignments
from .serializers import TeacherAssignmentSerializer

class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherAssignments.objects.all()
    serializer_class = TeacherAssignmentSerializer

    # GET /api/asignaciones/by_teacher/<uid>/
    def list_by_teacher(self, request, teacher_uid=None):
        qs = TeacherAssignments.objects.filter(
            teacher_uid=teacher_uid,
            activo=True
        )
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)

    # PUT /api/asignaciones/<id>/deactivate/
    def deactivate(self, request, pk=None):
        try:
            assignment = TeacherAssignments.objects.get(id=pk)
            assignment.activo = False
            assignment.save()
            return Response({"ok": True})
        except TeacherAssignments.DoesNotExist:
            return Response({"ok": False, "error": "No existe"}, status=404)
        except Exception as e:
            return Response({"ok": False, "error": str(e)}, status=400)
