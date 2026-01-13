from rest_framework.viewsets import ModelViewSet
from .models import NoteAnalysis
from .serializers import NoteAnalysisSerializer
from .tasks import analyze_note_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .serializers import UploadNoteSerializer
from .services import extract_text_from_file
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



class NoteAnalysisViewSet(ModelViewSet):
    queryset = NoteAnalysis.objects.all().order_by("-created_at")
    serializer_class = NoteAnalysisSerializer

    def perform_create(self, serializer):
        analysis = serializer.save()
        analyze_note_task.delay(analysis.id)


@method_decorator(csrf_exempt, name="dispatch")
class UploadNoteView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = UploadNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = serializer.save()

        try:
            extracted = extract_text_from_file(note.file)
        except Exception as e:
            note.status = "failed"
            note.error = str(e)
            note.save()
            return Response({"error": str(e)}, status=400)

        note.raw_text = extracted
        note.status = "pending"
        note.save()
        breakpoint()

        analyze_note_task.delay(note.id)

        return Response(
            {"id": note.id, "status": "processing"},
            status=status.HTTP_201_CREATED,
        )


class IndexView(TemplateView):
    template_name = "core/index.html"
