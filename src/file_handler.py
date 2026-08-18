import csv
import os
import shutil
from datetime import datetime

LOG_FILE = "processing_log.csv"

def sanitize_filename(text):
    """Removes characters that aren't safe in filenames."""
    if not text:
        return "unknown"
    safe = "".join(c for c in text if c.isalnum() or c in (" ", "-", "_"))
    return safe.strip().replace(" ", "_")

def build_new_filename(extracted_data, original_extension):
    """Builds a filename like 2024-01-01_TestCo_INV1001.pdf from extracted data."""
    date = extracted_data.get("date") or "unknown-date"
    customer = sanitize_filename(extracted_data.get("customer_name"))
    doc_number = sanitize_filename(extracted_data.get("document_number"))
    return f"{date}_{customer}_{doc_number}{original_extension}"

def log_result(original_filename, new_filename, extracted_data, destination):
    """Appends a row describing what happened to this file."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "original_filename", "new_filename",
                "customer_name", "date", "document_type",
                "document_number", "confidence", "destination"
            ])
        writer.writerow([
            datetime.now().isoformat(),
            original_filename,
            new_filename,
            extracted_data.get("customer_name"),
            extracted_data.get("date"),
            extracted_data.get("document_type"),
            extracted_data.get("document_number"),
            extracted_data.get("confidence"),
            destination
        ])

def process_file(pdf_path, extracted_data, dry_run=False):
    """
    Moves and renames a PDF based on extracted data.
    Low-confidence extractions go to review_needed/ instead of processed/.
    Returns the destination path.
    """
    original_filename = os.path.basename(pdf_path)
    _, extension = os.path.splitext(original_filename)

    confidence = extracted_data.get("confidence", "low")
    destination_folder = "processed" if confidence == "high" else "review_needed"

    new_filename = build_new_filename(extracted_data, extension)
    destination_path = os.path.join(destination_folder, new_filename)

    if dry_run:
        print(f"[DRY RUN] Would move {pdf_path} -> {destination_path}")
    else:
        shutil.move(pdf_path, destination_path)
        log_result(original_filename, new_filename, extracted_data, destination_folder)
        print(f"Moved {pdf_path} -> {destination_path}")

    return destination_path