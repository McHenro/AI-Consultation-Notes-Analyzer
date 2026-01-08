from rest_framework import serializers
from .models import NoteAnalysis


class NoteAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteAnalysis
        fields = "__all__"
        read_only_fields = (
            "summary",
            "key_points",
            "missing_info",
            "next_actions",
            "status",
            "error",
            "created_at",
        )
