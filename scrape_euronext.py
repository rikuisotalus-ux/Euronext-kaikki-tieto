import requests
import csv
from datetime import datetime

PRODUCTS = [
    {"code": "HLBY", "name": "HLBY"},
    {"code": "HLBQ", "name": "HLBQ"},
    {"code": "HLBM", "name": "HLBM"},
    {"code": "NSBY", "name": "NSBY"},
    {"code": "NSBQ", "name": "NSBQ"},
    {"code": "NSBM", "name": "NSBM"},
]

BASE_URL = "https://live.euronext.com/en/ajax/getPricesFutures/commodities-futures/{code}/DAMS"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}


def strip_html(text):
    import re
    return re.sub("<.*?>", "", text).strip()


def scrape_api():
    all_rows = []
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for product in PRODUCTS:
        url = BASE_URL.format(code=product["code"])
        name = product["name"]

        print(f"\n🔎 Hakee: {url}")

        response = requests.get(url, headers=HEADERS)

        # ✅ DEBUG jos menee pieleen
        if response.status_code != 200:
            print(f"❌ HTTP error: {response.status_code}")
            continue

        text = response.text.strip()

        # ✅ jos ei ole JSON → skip
        if not text.startswith("{"):
            print("⚠️ Ei JSON vastaus, ohitetaan")
            continue

        data = response.json()

        rows = data.get("aaData", [])

        print(f"✅ Rivejä: {len(rows)}")

        for row in rows:
            clean = [strip_html(cell) for cell in row]

            if len(clean) < 6:
                continue

            delivery = clean[0]
            settlement = clean[5]

            if (
                delivery == ""
                or delivery.lower() == "total"
                or "/" in delivery
            ):
                continue

            all_rows.append([
                delivery,
                settlement,
                name,
                today
            ])

    with open("combined_settlement.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Delivery", "Settlement", "Product", "Date"])
        writer.writerows(all_rows)

    print("\n✅ CSV valmis!")


if __name__ == "__main__":
    scrape_api()
