from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from db.database import init_db
from app.routes import bp
from app.fetcher import fetch_and_save

app = Flask(__name__, template_folder="templates")
app.register_blueprint(bp)


def scheduled_sync():
    try:
        rate_date, count = fetch_and_save()
        print(f"[scheduler] синхронизировано: {rate_date}, записей: {count}")
    except Exception as e:
        print(f"[scheduler] ошибка: {e}")


if __name__ == "__main__":
    init_db()

    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_sync, "cron", hour=0, minute=1)  # каждый день в 00:01
    scheduler.start()

    app.run(debug=True, use_reloader=False)

