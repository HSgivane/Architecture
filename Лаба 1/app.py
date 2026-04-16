from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from functools import wraps
from db import *

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Сначала войдите в систему.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Сначала войдите в систему.")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            flash("Заполни логин и пароль.")
            return redirect(url_for("register"))

        try:
            create_user(username, password, "viewer")
            flash("Регистрация успешна. Теперь войди.")
            return redirect(url_for("login"))
        except Exception:
            flash("Пользователь уже существует или ошибка регистрации.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = verify_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("notes"))
        flash("Неверный логин или пароль.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/notes")
@login_required
def notes():
    return render_template("notes.html", notes=get_all_notes())


@app.route("/notes/create", methods=["GET", "POST"])
@role_required("moderator", "admin")
def notes_create():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        create_note(title, content, session["user_id"])
        return redirect(url_for("notes"))
    return render_template("note_form.html", mode="create", note=None)


@app.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
@role_required("moderator", "admin")
def notes_edit(note_id):
    note = get_note(note_id)
    if not note:
        abort(404)

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        update_note(note_id, title, content)
        return redirect(url_for("notes"))

    return render_template("note_form.html", mode="edit", note=note)


@app.route("/notes/delete/<int:note_id>", methods=["POST"])
@role_required("moderator", "admin")
def notes_delete(note_id):
    delete_note(note_id)
    return redirect(url_for("notes"))


@app.route("/users")
@role_required("admin")
def users():
    return render_template("users.html", users=get_all_users())


@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@role_required("admin")
def admin_edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        abort(404)

    if request.method == "POST":
        role = request.form["role"]
        if role not in ["viewer", "moderator", "admin"]:
            abort(400)
        update_user_role(user_id, role)
        return redirect(url_for("users"))

    return render_template("admin_edit_user.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)