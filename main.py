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
    # Page vide pour l'instant
    return render_template('genres.html')

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


