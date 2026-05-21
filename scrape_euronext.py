import requests
import csv
from datetime import datetime
import re

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
}


def clean_html(text):
    return re.sub("<.*?>", "", text).strip()


def scrape_api():
    all_rows = []
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for product in PRODUCTS:
        url = BASE_URL.format(code=product["code"])
        name = product["name"]

        print(f"\n🔎 Hakee: {url}")

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            continue

        html = response.text

        # ✅ etsitään kaikki <tr> rivit
        rows = re.findall(r"<tr.*?>(.*?)</tr>", html, re.DOTALL)

        print(f"✅ HTML rivejä: {len(rows)}")

        for row in rows:
            cols = re.findall(r"<td.*?>(.*?)</td>", row, re.DOTALL)
            cols = [clean_html(c) for c in cols]

            if len(cols) < 6:
                continue

            delivery = cols[0]
            settlement = cols[5]

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

    # ✅ kirjoita CSV
    with open("combined_settlement.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Delivery", "Settlement", "Product", "Date"])
        writer.writerows(all_rows)

    print("\n✅ CSV valmis!")


if __name__ == "__main__":
    scrape_api()
