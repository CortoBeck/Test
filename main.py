import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, get_all_books, add_book, update_status, update_book
from config import ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "ta_clef_secrete_123"
)  # valeur par défaut pour dev


### enlever après
import os
###

print("Chemin absolu vers books.db :", os.path.abspath("books.db"))
print("Le fichier books.db existe-t-il ? ", os.path.exists("books.db"))

init_db()

# --- ROUTES ---


@app.route("/")
def home():
    query = request.args.get("q", "").strip().lower()
    books = get_all_books()

    if query:
        books = [
            book
            for book in books
            if query in book["title"].lower() or query in book["author"].lower()
        ]

    return render_template("catalogue.html", books=books, query=query)


@app.route("/genres")
def genres():
    genre_list = [
        "Roman",
        "Poésie",
        "Théâtre",
        "Science-fiction",
        "Essai",
        "Biographie et mémoires",
        "Histoire",
        "Philosophie",
        "Fantastique",
        "Policier",
        "Manuels et guides",
        "Magazine",
    ]
    return render_template("genres.html", genres=genre_list)


@app.route("/genres/<genre_name>")
def genre_books(genre_name):
    # Mise en forme pour affichage
    display_name = genre_name.replace("_", " ").title()

    # Récupère tous les livres
    books = get_all_books()

    # Ne garde que ceux du bon genre (en ignorant la casse)
    filtered_books = [
        book for book in books if book["genre"].strip().lower() == display_name.lower()
    ]

    return render_template("genre_books.html", genre=display_name, books=filtered_books)


@app.route("/request/<int:book_id>", methods=["GET", "POST"])
def request_book(book_id):
    books = get_all_books()
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        flash("Livre introuvable.", "danger")
        return redirect(url_for("home"))

    if book["status"] != "disponible":
        flash("Ce livre est déjà emprunté.", "warning")
        return redirect(url_for("home"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()

        if not nom or not prenom:
            flash("Merci de remplir tous les champs.", "danger")
            return redirect(url_for("request_book", book_id=book_id))

        # Change le statut du livre
        update_status(book_id)

        # Stocke la demande (à améliorer si besoin)
        with open("notifications_admin.txt", "a", encoding="utf-8") as f:
            f.write(f"[DEMANDE] {prenom} {nom} souhaite emprunter '{book['title']}'\n")

        flash("Demande envoyée. Merci !", "success")
        return redirect(url_for("home"))

    return render_template("request_book.html", book=book)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            flash("Connexion réussie", "success")
            return redirect(url_for("admin"))
        else:
            flash("Identifiants incorrects. Réessaie.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté.", "info")
    return redirect(url_for("home"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for("login"))

    books = get_all_books()

    # Lecture des notifications d'emprunt
    try:
        with open("notifications_admin.txt", "r", encoding="utf-8") as f:
            notifications = f.readlines()
    except FileNotFoundError:
        notifications = []

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        edition = request.form.get("edition", "").strip()
        remarque = request.form.get("remarque", "").strip()
        genre = request.form.get("genre", "").strip()
        resume = request.form.get("resume", "").strip()

        if title:
            add_book(title, author, edition, remarque, genre, resume)
            flash(f"Livre '{title}' ajouté !", "success")
            return redirect(url_for("admin"))
        else:
            flash("Le titre et l'auteur sont obligatoires.", "danger")

    return render_template("admin.html", books=books, notifications=notifications)


@app.route("/update_status/<int:book_id>")
def update_book_status(book_id):
    if not session.get("logged_in"):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for("login"))
    update_status(book_id)
    flash("Statut mis à jour.", "success")
    return redirect(url_for("admin"))


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if not session.get("logged_in"):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for("login"))

    books = get_all_books()
    book = next((b for b in books if b["id"] == book_id), None)

    if not book:
        flash("Livre introuvable.", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        edition = request.form.get("edition", "").strip()
        remarque = request.form.get("remarque", "").strip()
        genre = request.form.get("genre", "").strip()
        resume = request.form.get("resume", "").strip()

        update_book(book_id, title, author, edition, remarque, genre, resume)

        flash("Livre mis à jour !", "success")
        return redirect(url_for("admin"))

    return render_template("edit_book.html", book=book)


@app.route("/delete", methods=["GET", "POST"])
def delete_books():
    if not session.get("logged_in"):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for("login"))

    books = get_all_books()

    if request.method == "POST":
        selected_ids = request.form.getlist("book_ids")
        if selected_ids:
            return render_template(
                "confirm_bulk_delete.html", selected_ids=selected_ids, books=books
            )
        else:
            flash("Aucun livre sélectionné.", "warning")
            return redirect(url_for("admin"))

    return render_template("bulk_delete.html", books=books)


@app.route("/confirm-delete", methods=["POST"])
def confirm_delete_books():
    if not session.get("logged_in"):
        flash("Connecte-toi d'abord !", "warning")
        return redirect(url_for("login"))

    selected_ids = request.form.getlist("selected_ids")
    if selected_ids:
        from database import delete_book

        for book_id in selected_ids:
            delete_book(int(book_id))
        flash(f"{len(selected_ids)} livre(s) supprimé(s).", "success")
    else:
        flash("Aucune sélection trouvée.", "warning")

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
    # from import_excel import import_excel_to_numpy_and_insert
    ### à n'utiliser que si on a vraiment besoin de transmettre les infos de l'excel - a priori plus jamais
    # import_excel_to_numpy_and_insert()
    app.run(debug=True)
