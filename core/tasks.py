import json
import logging
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from openai import OpenAI
from .models import NoteAnalysis
from .prompts import ANALYSIS_PROMPT

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client with increased timeout
client = OpenAI(timeout=180.0)  # 3 minutes timeout for larger files


def extract_content_from_response(response):
    """
    Extract text content from OpenAI API response.

    The OpenAI GPT-5-nano response structure typically looks like:
    Response(
        id='resp_0800e7e36191e806006960f68df200819284e30da5ba03fbf9',
        output=[
            ResponseReasoningItem(...),  # First item (index 0) is usually reasoning
            ResponseOutputMessage(       # Second item (index 1) contains the actual output
                content=[
                    ResponseOutputText(  # First content item has the text we need
                        text='{"summary": "..."}'
                    )
                ]
            )
        ]
    )

    This function tries multiple approaches to extract the content:
    1. Direct access to the expected path (output[1].content[0].text)
    2. Search for any message item with output_text content
    3. General search for any text content in any output item

    Args:
        response: The OpenAI API response object

    Returns:
        str: The extracted text content

    Raises:
        ValueError: If no content could be found in the response
    """
    content = None

    # Log basic response info
    logger.info(f"Response received: ID={response.id}, Model={response.model}")

    # Approach 1: Try direct access to the expected path
    if len(response.output) >= 2:
        try:
            content = response.output[1].content[0].text
            logger.info(f"Content found using direct path access")
            return content
        except (AttributeError, IndexError):
            logger.debug("Direct path access failed, trying alternative methods")

    # Approach 2: Find any message item with output_text content
    for output_item in response.output:
        if getattr(output_item, 'type', None) == "message":
            if hasattr(output_item, 'content') and output_item.content:
                for content_item in output_item.content:
                    if getattr(content_item, 'type', None) == "output_text" and hasattr(content_item, 'text'):
                        content = content_item.text
                        logger.info(f"Content found in message with output_text")
                        return content

    # Approach 3: General search for any text content
    for output_item in response.output:
        if hasattr(output_item, 'content') and output_item.content:
            for content_item in output_item.content:
                if hasattr(content_item, 'text') and content_item.text:
                    content = content_item.text
                    logger.info(f"Content found using general search")
                    return content

    # If we get here, no content was found
    raise ValueError("Could not find content in the response")


def parse_json_content(content):
    """
    Parse JSON content from text, handling various edge cases.

    Args:
        content (str): The text content to parse

    Returns:
        dict: The parsed JSON data

    Raises:
        json.JSONDecodeError: If the content cannot be parsed as JSON
    """
    try:
        # Try to parse as is first
        return json.loads(content)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON from the content
        import re
        json_pattern = r'({[\s\S]*})'
        match = re.search(json_pattern, content)

        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                # If that still fails, try to clean up the content
                cleaned_content = content.strip()
                # Remove any leading or trailing backticks (common in markdown code blocks)
                if cleaned_content.startswith('```') and cleaned_content.endswith('```'):
                    cleaned_content = cleaned_content[3:-3].strip()
                # Try parsing again
                return json.loads(cleaned_content)
        else:
            raise json.JSONDecodeError("Could not extract JSON from response", content, 0)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 5},
)
def analyze_note_task(analysis_id):
    """
    Analyze a medical note using OpenAI API.

    This task:
    1. Retrieves the note analysis record from the database
    2. Calls the OpenAI API to analyze the note
    3. Extracts the content from the response
    4. Parses the JSON content
    5. Updates the note analysis record with the results

    Args:
        analysis_id (int): The ID of the NoteAnalysis record to process
    """
    # Get the analysis record
    analysis = NoteAnalysis.objects.get(id=analysis_id)
    analysis.status = "processing"
    analysis.save(update_fields=["status"])

    try:
        # Call OpenAI API
        logger.info(f"Sending note {analysis_id} to OpenAI for analysis")
        response = client.responses.create(
            model="gpt-5-nano",
            input=ANALYSIS_PROMPT.format(notes=analysis.raw_text),
            store=True
        )

        # Extract content from response
        content = extract_content_from_response(response)

        # Parse JSON content
        data = parse_json_content(content)

        # Update analysis record
        analysis.summary = data.get("summary", "")
        analysis.key_points = data.get("key_points", [])
        analysis.missing_info = data.get("missing_information", [])
        analysis.next_actions = data.get("suggested_next_actions", [])
        analysis.status = "completed"
        analysis.save()

        logger.info(f"Successfully analyzed note {analysis_id}")

    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from OpenAI response for note {analysis_id}")
        analysis.status = "failed"
        analysis.error = "Invalid JSON returned from AI"
        analysis.save()

    except SoftTimeLimitExceeded:
        logger.error(f"Task exceeded time limit for note {analysis_id}")
        analysis.status = "failed"
        analysis.error = "Analysis took too long to complete. The file might be too large or complex."
        analysis.save()
        # Don't raise the exception to prevent retries for timeout issues

    except Exception as e:
        logger.error(f"Error analyzing note {analysis_id}: {str(e)}")
        analysis.status = "failed"
        analysis.error = str(e)
        analysis.save()
        raise
