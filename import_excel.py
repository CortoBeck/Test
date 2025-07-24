import pandas as pd
import numpy as np
import sqlite3
from config import DB_NAME, EXCEL_PATH


def import_excel_to_numpy_and_insert():
    # 1. Lecture Excel
    df = pd.read_excel(EXCEL_PATH)

    # 2. Nettoyage des noms de colonnes
    df.columns = [c.strip().lower() for c in df.columns]

    # 3. Conversion en tableau numpy
    data_array = df.to_numpy()

    # 4. Connexion à la base
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for row in data_array:
        titre = str(row[0]).strip()
        auteur = str(row[1]).strip()
        edition = (
            str(row[2]).strip() if len(row) > 2 else None
        )  # dépend de l'ordre dans Excel
        remarque = str(row[3]).strip() if len(row) > 3 else None
        genre = str(row[4]).strip()
        resume = str(row[5]).strip()

        # Force status = 'disponible'
        statut = "disponible"

        # Si le livre existe, on le met à jour
        cursor.execute(
            "SELECT * FROM books WHERE title = ? AND author = ?", (titre, auteur)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                "UPDATE books SET edition = ?, remarque = ?, genre = ?, resume = ? WHERE title = ? AND author = ?",
                (edition, remarque, genre, resume, titre, auteur),
            )
        else:
            cursor.execute(
                "INSERT INTO books (title, author, status, edition, remarque, genre, resume) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (titre, auteur, statut, edition, remarque, genre, resume),
            )

            print(f"> Livre ajouté : {titre} - {auteur}")

    conn.commit()
    conn.close()
    print("Importation terminée.")
