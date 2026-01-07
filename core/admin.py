from django.contrib import admin
from .models import NoteAnalysis


@admin.register(NoteAnalysis)
class NoteAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("raw_text",)
    readonly_fields = ("created_at",)
