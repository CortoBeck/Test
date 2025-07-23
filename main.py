from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, get_all_books, add_book, update_status
from config import ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = "ta_clef_secrete_123"  # Change pour une vraie clé secrète en prod

init_db()

# --- ROUTES ---

@app.route('/')
def home():
    query = request.args.get('q', '').strip().lower()
    books = get_all_books()

    if query:
        books = [book for book in books if query in book['title'].lower() or query in book['author'].lower()]

    return render_template('catalogue.html', books=books, query=query)

@app.route('/genres')
def genres():
    genre_list = [
        "Roman", "Poésie", "Théâtre", "Science-fiction",
        "Essai", "Biographie", "Histoire", "Philosophie",
        "Fantastique", "Policier", "Manuels scolaires", "Magazines"
    ]
    return render_template('genres.html', genres=genre_list)

@app.route('/genres/<genre_name>')
def genre_books(genre_name):
    # Pour l'instant : message temporaire
    display_name = genre_name.replace('_', ' ').title()
    return render_template('genre_books.html', genre=display_name, books=[])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Connexion réussie', 'success')
            return redirect(url_for('admin'))
        else:
            flash("Identifiants incorrects. Réessaie.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnecté.", "info")
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for('login'))
    books = get_all_books()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        edition = request.form.get('edition', '').strip()    # <-- nouveau
        remarque = request.form.get('remarque', '').strip()  # <-- nouveau

        if title and author:
            add_book(title, author, edition, remarque)       # <-- passe les nouveaux champs
            flash(f"Livre '{title}' ajouté !", "success")
            return redirect(url_for('admin'))
        else:
            flash("Le titre et l'auteur sont obligatoires.", "danger")
    return render_template('admin.html', books=books)


@app.route('/update_status/<int:book_id>')
def update_book_status(book_id):
    if not session.get('logged_in'):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for('login'))
    update_status(book_id)
    flash("Statut mis à jour.", "success")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    from import_excel import import_excel_to_numpy_and_insert
    import_excel_to_numpy_and_insert()
    app.run(debug=True)


