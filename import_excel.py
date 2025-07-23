# import_excel.py

import pandas as pd
import sqlite3
from config import DB_NAME, EXCEL_PATH

def import_books_from_excel():
    df = pd.read_excel(EXCEL_PATH)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO livres (titre, auteur, edition, statut, remarque, genre)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (row['titre'], row['auteur'], row['edition'], row['statut'], row['remarque'], row['genre']))

    conn.commit()
    conn.close()
