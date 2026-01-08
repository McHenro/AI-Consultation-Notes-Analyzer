from celery import shared_task
from .models import NoteAnalysis
import time


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def analyze_note_task(self, analysis_id):
    analysis = NoteAnalysis.objects.get(id=analysis_id)
    analysis.status = "processing"
    analysis.save(update_fields=["status"])

    # simulate heavy work (AI later)
    time.sleep(5)

    analysis.summary = "This is a placeholder summary."
    analysis.key_points = ["Sample key point"]
    analysis.missing_info = ["Sample missing info"]
    analysis.next_actions = ["Sample next action"]
    analysis.status = "completed"
    analysis.save()
