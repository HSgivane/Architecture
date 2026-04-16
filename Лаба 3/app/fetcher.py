import requests
from datetime import date, datetime
from db.database import get_db


def fetch_and_save(target_date: date = None):
    url = (
        "https://www.cnb.cz/en/financial_markets/"
        "foreign_exchange_market/exchange_rate_fixing/daily.txt"
    )
    params = {"date": target_date.strftime("%d.%m.%Y")} if target_date else {}
    resp = requests.get(url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    lines = resp.text.strip().splitlines()

    # парсим дату
    try:
        rate_date = datetime.strptime(lines[0].split()[0], "%d.%m.%Y").date().isoformat()
    except ValueError:
        rate_date = (target_date or date.today()).isoformat()

    records = []
    for line in lines[2:]:
        parts = line.split("|")
        if len(parts) != 5:
            continue
        _, _, amount, code, rate_str = parts
        try:
            records.append((rate_date, code.strip(), int(amount), float(rate_str.replace(",", "."))))
        except ValueError:
            continue

    with get_db() as db:
        db.executemany("INSERT OR REPLACE INTO rates VALUES (?,?,?,?)", records)

    return rate_date, len(records)
