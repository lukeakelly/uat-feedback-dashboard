# UAT Feedback Dashboard

A local-first Streamlit MVP for managing UAT feedback for an AI Library project.
It ingests common feedback files, creates structured pending items, requires human
review, stores approved feedback in SQLite, and provides a dashboard and exports.

## Features

- Upload `.docx`, `.xlsx`, `.csv`, and `.txt` feedback files.
- Preserve source feedback and approximate source locations.
- Use optional OpenAI extraction or a fully local fallback extractor.
- Edit, approve, reject, defer, or clarify extracted items.
- Assign sequential feedback IDs such as `UAT-0001`.
- Maintain an editable approved register with soft archiving.
- View KPIs, charts, priority tables, and recurring themes.
- Export approved and rejected data to CSV or a three-sheet Excel workbook.

## Install

Python 3.11 or later is recommended.

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Optional OpenAI extraction

The app works without an API key. Without one, it creates a pending item for each
non-empty paragraph, line, or spreadsheet row and marks classification fields as
`Needs review`.

To enable AI extraction:

1. Copy `.env.example` to `.env`.
2. Add `OPENAI_API_KEY`.
3. Optionally change `OPENAI_MODEL`.
4. Restart Streamlit.

AI output is validated against the controlled values and always goes to the pending
review table. It is never written directly to the approved register.

## Workflow

1. Open **Upload Feedback**, upload one file, and enter the source metadata.
2. Open **Extract Feedback** and choose AI or fallback extraction.
3. Open **Review Extracted Items**, edit the rows, and explicitly approve or reject
   selected items.
4. Maintain approved items in **Feedback Register**.
5. Review approved-only reporting in **Dashboard**.
6. Download CSV or Excel files from **Export**.

Rejected rows are retained in a separate audit table. Approved rows can be archived
instead of deleted.

## Data storage

SQLite data is stored at `data/uat_feedback.db` by default. Set `UAT_DB_PATH` in
`.env` to use a different path. Normalised source content is stored in the local
database so extraction still works after navigating between pages.

The `source_files`, `pending_feedback`, `approved_feedback`, `rejected_feedback`,
and `audit_log` tables separate ingestion, review, decisions, and reporting.

## Security and privacy

- This MVP stores data locally in SQLite.
- Do not upload sensitive production data unless the environment is approved.
- Raw feedback is preserved for traceability.
- AI extraction must be reviewed by a human before anything is approved.
- No approved row is created without human review.
- Do not commit the SQLite database, `.env`, uploaded files, or exports to Git.
- When AI extraction is enabled, feedback content is sent to the configured OpenAI
  API account.

## Tests

Run:

```bash
pytest
```

The tests cover controlled-value validation, fallback extraction, database creation
and approval, and CSV/Excel export generation.

## Known limitations

- The MVP is designed for a single local user and has no authentication.
- There is no duplicate detection beyond a human decision field.
- Word source locations are approximate because paragraphs and tables are extracted
  as normalised blocks.
- Large files are not chunked before AI extraction.
- AI extraction depends on the configured model, account access, and API limits.
- There is no Power BI, SharePoint, Azure DevOps, or deployment integration.

## Suggested enhancements

- Add duplicate and recurring-theme detection.
- Add chunked AI extraction for large documents.
- Add configurable controlled values and saved dashboard filters.
- Add source-file retention controls and a richer audit history.
- Add SharePoint, Azure DevOps, or enterprise identity only after the local workflow
  has been validated.
