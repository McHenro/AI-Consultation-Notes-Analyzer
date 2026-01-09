from celery import shared_task
from .models import NoteAnalysis
from .prompts import ANALYSIS_PROMPT
import json
from openai import OpenAI

client = OpenAI()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def analyze_note_task(self, analysis_id):
    analysis = NoteAnalysis.objects.get(id=analysis_id)
    analysis.status = "processing"
    analysis.save(update_fields=["status"])

    try:
        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {
                    "role": "user",
                    "content": ANALYSIS_PROMPT.format(notes=analysis.raw_text)
                }
            ],
            max_output_tokens=400,
            temperature=0.2
        )

        content = response.output_text

        # Safe JSON parsing
        data = json.loads(content)

        analysis.summary = data.get("summary", "")
        analysis.key_points = data.get("key_points", [])
        analysis.missing_info = data.get("missing_information", [])
        analysis.next_actions = data.get("suggested_next_actions", [])
        analysis.status = "completed"
        analysis.save()

    except json.JSONDecodeError:
        analysis.status = "failed"
        analysis.error = "Invalid JSON returned from AI"
        analysis.save()

    except Exception as e:
        analysis.status = "failed"
        analysis.error = str(e)
        analysis.save()
        raise
