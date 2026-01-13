from django.db import models
import uuid
import os

# Rename files on upload to meet the chars max for the filename
def upload_to(instance, filename):
    ext = filename.split(".")[-1]
    return f"notes/{uuid.uuid4().hex}.{ext}"

class NoteAnalysis(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    raw_text = models.TextField(blank=True, help_text="Original notes submitted by the user")
    file = models.FileField(upload_to=upload_to, null=True, blank=True, max_length=255)

    summary = models.TextField(blank=True)
    key_points = models.JSONField(null=True, blank=True)
    missing_info = models.JSONField(null=True, blank=True)
    next_actions = models.JSONField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NoteAnalysis #{self.id} - {self.status}"
