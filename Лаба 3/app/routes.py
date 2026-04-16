from datetime import datetime
from flask import Blueprint, jsonify, request, render_template
from db.database import get_db
from app.fetcher import fetch_and_save

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/sync")
def sync():
    d = None
    if "date" in request.args:
        d = datetime.strptime(request.args["date"], "%Y-%m-%d").date()
    rate_date, count = fetch_and_save(d)
    return jsonify({"date": rate_date, "saved": count})


@bp.route("/rates")
def rates():
    query = "SELECT * FROM rates WHERE 1=1"
    params = []

    if "date" in request.args:
        query += " AND date = ?"
        params.append(request.args["date"])
    if "currency" in request.args:
        codes = [c.strip().upper() for c in request.args["currency"].split(",")]
        query += f" AND currency IN ({','.join('?'*len(codes))})"
        params.extend(codes)

    query += " ORDER BY date DESC, currency"

    with get_db() as db:
        rows = db.execute(query, params).fetchall()

    return jsonify([{
        "date": r["date"],
        "currency": r["currency"],
        "rate_per_unit": round(r["rate"] / r["amount"], 4),
    } for r in rows])
