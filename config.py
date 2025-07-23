import os

DB_NAME = "books.db"
EXCEL_PATH = "data/livres.xlsx"

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "thomas")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "sankara")
