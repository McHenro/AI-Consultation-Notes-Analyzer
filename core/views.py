from rest_framework.viewsets import ModelViewSet
from .models import NoteAnalysis
from .serializers import NoteAnalysisSerializer
from .tasks import analyze_note_task


class NoteAnalysisViewSet(ModelViewSet):
    queryset = NoteAnalysis.objects.all().order_by("-created_at")
    serializer_class = NoteAnalysisSerializer

    def perform_create(self, serializer):
        analysis = serializer.save()
        analyze_note_task.delay(analysis.id)
