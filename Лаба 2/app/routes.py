import random
from flask import Blueprint, request, jsonify, render_template, current_app
from db.database import get_db
from app.crypto import sign, verify, public_key_to_pem, public_key_from_pem

bp = Blueprint("main", __name__)

RANDOM_MESSAGES = [
    "Сервер подтверждает подлинность соединения.",
    "Данные успешно прошли контроль целостности.",
    "Транзакция авторизована в 03:47 UTC.",
    "Доступ к защищённому ресурсу разрешён.",
    "Сессия установлена. Токен действителен 24 часа.",
]


@bp.route("/")
def index():
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM messages ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    return render_template("index.html", messages=rows)


# ── Сценарий 1: клиент подписывает, сервер проверяет ──────────────────────────

@bp.route("/verify-client", methods=["POST"])
def verify_client():
    """
    Принимает: { message, signature, public_key }
    Возвращает: { verified }
    """
    data = request.get_json()
    message   = data.get("message", "")
    signature = data.get("signature", "")
    pem       = data.get("public_key", "")

    try:
        public_key = public_key_from_pem(pem)
        ok = verify(message, signature, public_key)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    with get_db() as db:
        db.execute(
            "INSERT INTO messages (scenario, message, signature, verified) VALUES (?,?,?,?)",
            ("client", message, signature, int(ok))
        )

    return jsonify({"verified": ok})


# ── Сценарий 2: сервер подписывает, клиент проверяет ──────────────────────────

@bp.route("/server/public-key")
def server_public_key():
    pub = current_app.config["SERVER_PUBLIC_KEY"]
    return jsonify({"public_key": public_key_to_pem(pub)})


@bp.route("/server/sign")
def server_sign():
    priv = current_app.config["SERVER_PRIVATE_KEY"]
    message   = random.choice(RANDOM_MESSAGES)
    signature = sign(message, priv)

    with get_db() as db:
        db.execute(
            "INSERT INTO messages (scenario, message, signature, verified) VALUES (?,?,?,?)",
            ("server", message, signature, 1)
        )

    return jsonify({"message": message, "signature": signature})
