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


def strip_html(text):
    import re
    return re.sub("<.*?>", "", text).strip()


def scrape_api():
    all_rows = []
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for product in PRODUCTS:
        url = BASE_URL.format(code=product["code"])
        name = product["name"]

        print(f"🔎 Hakee: {url}")

        response = requests.get(url)
        data = response.json()

        rows = data.get("aaData", [])

        for row in rows:
            clean = [strip_html(cell) for cell in row]

            if len(clean) < 6:
                continue

            delivery = clean[0]
            settlement = clean[5]

            if delivery.lower() == "total":
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

    print("✅ CSV valmis!")


if __name__ == "__main__":
    scrape_api()
