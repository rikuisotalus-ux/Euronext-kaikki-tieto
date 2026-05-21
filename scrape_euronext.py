import requests
import csv
from datetime import datetime
import re

# =============================
# TUOTTEET
# =============================
PRODUCTS = [
    {"code": "HLBY", "name": "HLBY"},
    {"code": "HLBQ", "name": "HLBQ"},
    {"code": "HLBM", "name": "HLBM"},
    {"code": "NSBY", "name": "NSBY"},
    {"code": "NSBQ", "name": "NSBQ"},
    {"code": "NSBM", "name": "NSBM"},
]

# =============================
# URL + HEADERS
# =============================
BASE_URL = "https://live.euronext.com/en/ajax/getPricesFutures/commodities-futures/{code}/DAMS"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


# =============================
# CLEAN HTML
# =============================
def clean_html(text):
    return re.sub("<.*?>", "", text).strip()


# =============================
# PRODUCT CODE BUILDER
# =============================
def build_product_code(product, delivery):
    if not delivery:
        return None

    d = delivery.strip()

    if d.lower() == "total":
        return None

    parts = d.split()

    # YYYY (vuosituote)
    if len(parts) == 1:
        return f"{product}-{d[-2:]}"

    year = parts[-1]
    yy = year[-2:]
    first = parts[0].upper()

    # Quarter (Q1, Q2...)
    if first.startswith("Q"):
        return f"{product}{first[1]}-{yy}"

    # Month mapping
    month_map = {
        "JAN": "JAN", "FEB": "FEB", "MAR": "MAR",
        "APR": "APR", "MAY": "MAY", "JUN": "JUN",
        "JUL": "JUL", "AUG": "AUG", "SEP": "SEP",
        "OCT": "OCT", "NOV": "NOV", "DEC": "DEC",
    }

    month = first[:3]

    if month in month_map:
        return f"{product}{month_map[month]}-{yy}"

    return None


# =============================
# SCRAPER
# =============================
def scrape_api():
    all_rows = []
    headers = []
    header_written = False

    today = datetime.utcnow().strftime("%Y-%m-%d")

    for product in PRODUCTS:
        url = BASE_URL.format(code=product["code"])
        name = product["name"]

        print(f"\n🔎 Hakee: {url}")

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ HTTP virhe: {response.status_code}")
            continue

        html = response.text

        # ✅ HEADERIT (vain kerran)
        if not header_written:
            header_match = re.findall(r"<th.*?>(.*?)</th>", html)
            headers = [clean_html(h) for h in header_match]

            headers.extend(["Product", "ProductCode", "Date"])
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

            # ✅ ProductCode
            product_code = build_product_code(name, delivery)

            full_row = cols + [name, product_code, today]
            all_rows.append(full_row)

    # ✅ CSV
    with open("combined_settlement.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_rows)

    print("\n✅ CSV valmis täydellisillä sarakkeilla + ProductCode!")


# =============================
# RUN
# =============================
if __name__ == "__main__":
    scrape_api()
