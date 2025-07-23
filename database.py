import sqlite3

DB_NAME = 'books.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT DEFAULT 'disponible',
            edition TEXT,
            remarque TEXT,
            genre TEXT,
            resume TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_all_books():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_book(title, author, edition=None, remarque=None, genre=None, resume=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO books (title, author, edition, remarque, genre, resume) VALUES (?, ?, ?, ?, ?, ?)",
        (title, author, edition, remarque, genre, resume)
    )
    conn.commit()
    conn.close()



def update_status(book_id):
    conn = get_connection()
    c = conn.cursor()
    # Change status from disponible to emprunté or vice versa
    c.execute("SELECT status FROM books WHERE id = ?", (book_id,))
    current = c.fetchone()
    if current:
        new_status = 'emprunté' if current['status'] == 'disponible' else 'disponible'
        c.execute("UPDATE books SET status = ? WHERE id = ?", (new_status, book_id))
        conn.commit()
    conn.close()
