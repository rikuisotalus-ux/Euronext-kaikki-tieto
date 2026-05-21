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
    header_written = False
    headers = []

    today = datetime.utcnow().strftime("%Y-%m-%d")

    for product in PRODUCTS:
        url = BASE_URL.format(code=product["code"])
        name = product["name"]

        print(f"\n🔎 Hakee: {url}")

        response = requests.get(url, headers=HEADERS)

        html = response.text

        # ✅ HEADERIT
        if not header_written:
            header_match = re.findall(r"<th.*?>(.*?)</th>", html)
            headers = [clean_html(h) for h in header_match]

            headers.extend(["Product", "Date"])
            header_written = True

        # ✅ RIVIT
        rows = re.findall(r"<tr.*?>(.*?)</tr>", html, re.DOTALL)

        print(f"✅ Rivejä: {len(rows)}")

        for row in rows:
            cols = re.findall(r"<td.*?>(.*?)</td>", row, re.DOTALL)
            cols = [clean_html(c) for c in cols]

            if len(cols) < 5:
                continue

            delivery = cols[0]

            if (
                delivery == ""
                or delivery.lower() == "total"
                or "/" in delivery
            ):
                continue

            # ✅ LISÄÄ kaikki sarakkeet
            full_row = cols + [name, today]
            all_rows.append(full_row)

    # ✅ CSV
    with open("combined_settlement.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_rows)

    print("\n✅ CSV valmis täydellisillä sarakkeilla!")


if __name__ == "__main__":
    scrape_api()
