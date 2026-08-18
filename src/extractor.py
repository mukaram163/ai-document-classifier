import json
import time
from pdf2image import convert_from_path
from google import genai
from src.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-flash-latest"

EXTRACTION_PROMPT = """
Extract the following fields from this document image.
Return ONLY valid JSON, no other text, in this exact format:
{
  "customer_name": "...",
  "date": "YYYY-MM-DD",
  "document_type": "invoice/receipt/other",
  "document_number": "...",
  "confidence": "high/low"
}
Set confidence to "low" if any field is unclear, missing, or you had to guess.
"""

def pdf_to_image(pdf_path):
    """Converts page 1 of a PDF into a PIL Image object."""
    images = convert_from_path(pdf_path, dpi=200)
    return images[0]

def extract_data_from_pdf(pdf_path, max_retries=3):
    """Sends a PDF page to Gemini vision and returns extracted fields as a dict.
    Retries automatically if the API is temporarily overloaded (503 errors)."""
    image = pdf_to_image(pdf_path)

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[EXTRACTION_PROMPT, image]
            )
            raw_output = response.text
            break  # success, exit the retry loop
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait_time = attempt * 5  # 5s, then 10s, then 15s
                print(f"  Attempt {attempt} failed ({e}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise last_error  # out of retries, let main.py's except catch it

    cleaned = raw_output.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "customer_name": None,
            "date": None,
            "document_type": None,
            "document_number": None,
            "confidence": "low",
            "error": "Failed to parse model output",
            "raw_output": raw_output
        }