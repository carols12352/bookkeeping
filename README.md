Bookkeeping CLI

Simple command-line bookkeeping tool backed by SQLite.

Features
- Add income/expense transactions with categories and notes
- List and filter transactions by type, category, and date range
- Summarize totals and balances, including per-category breakdowns

Setup
1) Create and activate a virtual environment
   - Windows PowerShell:
     - python -m venv .venv
     - .venv\\Scripts\\Activate.ps1
2) Install dependencies
   - pip install -r requirements.txt

Usage
- Show help:
  - python main.py --help
- Add a transaction:
  - python main.py add --amount 45.5 --type expense --category food --note "lunch" --date 2024-01-05
- List transactions:
  - python main.py list
  - python main.py list --type income --from 2024-01-01 --to 2024-01-31
- Summary:
  - python main.py summary --from 2024-01-01 --to 2024-01-31
- Delete a transaction:
  - python main.py delete 3

Notes
- Dates are stored in YYYY-MM-DD format.
- The SQLite database file is data.db in the project root.
