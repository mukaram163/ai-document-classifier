
# AI Document Classifier

Automatically classifies, renames, and organizes scanned PDF documents (invoices, receipts, etc.) using AI vision — with a built-in review queue for anything the AI isn't confident about.

## What it does

1. Watches an `incoming/` folder for new PDFs

2. Sends each document to Gemini's vision model to extract:

   - Customer name

   - Date

   - Document type

   - Document number

3. Renames the file based on extracted data (e.g. `2024-01-15_AcmeCorp_INV1042.pdf`)

4. Routes high-confidence results to `processed/`, and anything uncertain to `review_needed/` for manual checking

5. Logs every decision to `processing_log.csv` — a full audit trail of what happened to each file

6. Automatically retries on temporary API failures

## Setup

1. Clone this repo and create a virtual environment:

```bash

   python3 -m venv venv

   source venv/bin/activate

   pip install -r requirements.txt

```

2. Install Poppler (required for PDF-to-image conversion):

   - Mac: `brew install poppler`

   - Linux: `sudo apt install poppler-utils`

   - Windows: [download poppler binaries](https://github.com/oschwartz10612/poppler-windows/releases)

3. Copy `.env.example` to `.env` and add your Gemini API key:

GEMINI_API_KEY=your-key-here

## Usage

Drop PDF files into `incoming/`, then run:

```bash

python3 main.py

```

Preview what would happen without actually moving files:

```bash

python3 main.py --dry-run

```

## Project structure


├── incoming/ # Drop new PDFs here
├── processed/ # Successfully classified documents
├── review_needed/ # Low-confidence documents, flagged for manual review
├── src/
│ ├── config.py # API key loading
│ ├── extractor.py # PDF → image → Gemini vision extraction
│ └── file_handler.py # Renaming, routing, logging
├── main.py # Entry point — processes everything in incoming/
└── processing_log.csv # Audit trail of every file processed


## Notes

Built as a lightweight, reliable alternative to a constantly-running watcher process — designed to be run on a schedule (cron / Task Scheduler) for production use.

