from flask import Flask
from db.database import init_db
from app.routes import bp

app = Flask(__name__, template_folder="templates")
app.register_blueprint(bp)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
