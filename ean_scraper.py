import requests,json,html,csv,time,os,random,logging
from bs4 import BeautifulSoup

csv_file = "king_jouet_Products.csv"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

with open("cookies.txt", "r") as file:
    cookies = file.read().strip()

def extract_ean_from_html(soup):
    ean13_values = set()

    for input_tag in soup.find_all("input", {"id": "product_datas"}):
        raw_value = input_tag.get("value")
        if raw_value:
            try:
                json_data = json.loads(html.unescape(raw_value))
                if "Ean13" in json_data:
                    ean13_values.add(json_data["Ean13"])
            except json.JSONDecodeError:
                pass

    for script_tag in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            json_obj = json.loads(script_tag.string)
            if isinstance(json_obj, dict) and "gtin13" in json_obj:
                ean13_values.add(json_obj["gtin13"])
        except Exception:
            pass

    return list(ean13_values)[0] if ean13_values else ""

def EAN(csv_file):
    if not os.path.exists(csv_file):
        print("❌ CSV file does not exist.")
        return

    with open(csv_file, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames
        if "EAN" not in fieldnames:
            fieldnames.append("EAN")
            for row in rows:
                row["EAN"] = ""

    total = len(rows)
    for i, row in enumerate(rows):
        url = row.get("product url", "").strip()

        if not url:
            print(f"{i+1}/{total}. ⚠️ No URL in row, skipping")
            continue

        if row.get("EAN"):
            print(f"{i+1}/{total}. ✅ Already processed, skipping")
            continue

        logging.info(f"{i+1}/{total}. 🔄 Processing: {url}")
        try:
            response = requests.get(url, 
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'if-modified-since': 'Fri, 11 Apr 2025 20:22:55 GMT',
            'if-none-match': 'W/"2927d-8lQwaGGmdbA7HrMCIV534jO2oWI"',
            'priority': 'u=0, i',
            'sec-ch-device-memory': '8',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.85", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.85"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'cookie': cookies,
        }
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                ean = extract_ean_from_html(soup)
                row["EAN"] = ean
                logging.info(f"   ➤ ✅ EAN: {ean}" if ean else "   ➤ ❌ No EAN found")
            elif response.status_code == 404:
                logging.info("   ➤ ❌ 404 Not Found")
                row["EAN"] = "N/A"
            else:
                logging.info(f"   ➤ ❌ Request failed: Status {response.status_code}")

        except Exception as e:
            logging.info(f"   ➤ ❌ Error: {e}")
            row["EAN"] = ""

        # Save progress after each row
        with open(csv_file, "w", newline='', encoding="utf-8-sig") as write_file:
            writer = csv.DictWriter(write_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        time.sleep(random.uniform(3, 6)) # Random sleep to avoid being blocked

    print("✅ All URLs processed and saved.")

# if __name__ == "__main__":
#     EAN(csv_file)