from flask import Flask
from db.database import init_db
from app.routes import bp
from app.crypto import generate_keys

app = Flask(__name__, template_folder="templates")
app.secret_key = "eds-secret"

# Ключи сервера генерируются один раз при старте
priv, pub = generate_keys()
app.config["SERVER_PRIVATE_KEY"] = priv
app.config["SERVER_PUBLIC_KEY"]  = pub

app.register_blueprint(bp)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
