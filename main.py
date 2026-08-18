import os
import glob
from src.extractor import extract_data_from_pdf
from src.file_handler import process_file

INCOMING_DIR = "incoming"

def run(dry_run=False):
    pdf_files = glob.glob(os.path.join(INCOMING_DIR, "*.pdf"))

    if not pdf_files:
        print("No PDFs found in incoming/. Nothing to do.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.")

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path}")
        try:
            extracted_data = extract_data_from_pdf(pdf_path)
            print(f"  Extracted: {extracted_data}")
            process_file(pdf_path, extracted_data, dry_run=dry_run)
        except Exception as e:
            print(f"  ERROR processing {pdf_path}: {e}")
            # Don't crash the whole batch over one bad file
            continue

    print("\nDone.")

if __name__ == "__main__":
    import sys
    dry_run_mode = "--dry-run" in sys.argv
    run(dry_run=dry_run_mode)