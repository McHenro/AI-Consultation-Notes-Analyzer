from rest_framework.viewsets import ModelViewSet
from .models import NoteAnalysis
from .serializers import NoteAnalysisSerializer


class NoteAnalysisViewSet(ModelViewSet):
    queryset = NoteAnalysis.objects.all().order_by("-created_at")
    serializer_class = NoteAnalysisSerializer
