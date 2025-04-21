import requests,csv,time,logging,os,re,random
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


ua= UserAgent().random

# ==================== Logging Configuration ====================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==================== Amazon Scraper Function ====================

def scrape_amazon(product_name, brand, reference, file_path):
    query = f"{product_name} {brand} {reference}".strip().replace(" ", "+")
    url = f"https://www.amazon.fr/s"
    
    querystring = {
        "k": f"{product_name} {brand} {reference}",
        "i": "toys",
        "__mk_fr_FR": "ÅMÅŽÕÑ",
        "ref": "nb_sb_noss"
    }

    headers = {
        "host": "www.amazon.fr",
        "connection": "keep-alive",
        "cache-control": "max-age=0",
        "device-memory": "8",
        "sec-ch-device-memory": "8",
        "dpr": "1",
        "sec-ch-dpr": "1",
        "viewport-width": "811",
        "sec-ch-viewport-width": "811",
        "rtt": "850",
        "downlink": "1.5",
        "ect": "3g",
        "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua-platform-version": "\"19.0.0\"",
        "upgrade-insecure-requests": "1",
        # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "user-agent": ua,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        # "referer": "https://www.amazon.fr/s?k=Trampoline+183+cm+avec+filet+SUN+and+SPORT+952705&i=toys&__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1N169BJMPO672&sprefix=trampoline+183+cm+avec+filet+sun+and+sport+952705%2Ctoys%2C835&ref=nb_sb_noss",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "session-id=262-4653968-1255555; session-id-time=2082787201l; i18n-prefs=EUR; ubid-acbfr=259-9585818-8572264; csm-hit=tb:QT008BGW742MHTPVN909+s-BVD1QRER1Q72HKQZ1P32|1745006728144&t:1745006728144&adb:adblk_no; session-token=xPWrd1qyd8jPQXpiqcpRsMzYp4tsFn53azWyf5y8VXtYRBSHf5yUMV9mOFWqDaTix8veW5629xiFBtui6P0CyeKFtEpTC+ImaOs+NojsugL/Qcr2AQlB42csbotsIcczc1ZP6Ya71zgxGcBv4wSX4ns1imjJrIc/5ALVxkQdLnTnNchzMi6ElBK0dHYF1wGEPQjSsfjNBCE3Y6WXK6+fORNlmkmKXtGZDbd4o0Ix/hSez1vGw2v6jcEydqrspuSOIBudehVB4kR6OHMUyzJ4r7HX0GOyDJ9sHRgMNEasz2PKBowb601b2+/9pWWUUOBNqHdUlSHImTavnbJY8kiGlWOCHutgASB1"
    }

    try:
        logging.info(f"Searching for: {querystring['k']}")
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code != 200:
            logging.error(f"Request failed with status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        price_whole = soup.find_all("span", class_="a-price-whole")
        price_fraction = soup.find_all("span", class_="a-price-fraction")
        prices1 = [tag.get_text(strip=True) for tag in price_whole]
        prices2 = [tag.get_text(strip=True) for tag in price_fraction]

        price = f"{prices1[0]}{prices2[0]}€" if prices1 and prices2 else "N/A"

        link_tag = soup.find('a', attrs={"aria-describedby": "price-link"})
        if not link_tag or not link_tag.get("href"):
            logging.warning("No valid product link found.")
            return

        href = link_tag['href']
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
        asin = asin_match.group(1) if asin_match else "N/A"
        brand_from_url = href.split('/')[1].split('-')[0] if '/' in href else "N/A"
        product_link = "https://www.amazon.fr" + href

        # Read, update and write back to CSV
        updated_rows = []
        headers_row = []

        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            headers_row = next(reader)
            if "ASIN" not in headers_row:
                headers_row.extend(["ASIN", "Amazon_Brand", "Amazon_Price", "Amazon_URL"])

            for row in reader:
                if len(row) < len(headers_row):
                    row.extend([""] * (len(headers_row) - len(row)))

                if row[1] == product_name and row[2] == brand and row[3] == reference:
                    row[headers_row.index("ASIN")] = asin
                    row[headers_row.index("Amazon_Price")] = price
                    row[headers_row.index("Amazon_Brand")] = brand_from_url
                    row[headers_row.index("Amazon_URL")] = product_link

                updated_rows.append(row)

        with open(file_path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers_row)
            writer.writerows(updated_rows)

        logging.info(f"✅ ASIN: {asin}, Brand: {brand_from_url}, Price: {price} added to CSV.")

    except Exception as e:
        logging.exception(f"An error occurred while scraping: {e}")

    time.sleep(random.uniform(4,8))  # Random sleep to avoid being blocked


# ==================== Read Product Names from CSV ====================
def read_pending_products(file_path):
    pending_products = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            asin_index = headers.index("ASIN") if "ASIN" in headers else -1
            name_index = 1  # Product name
            brand_index = 2  # Brand
            reference_index = 3  # Reference

            for row in reader:
                if asin_index == -1 or row[asin_index].strip() == "":
                    name = row[name_index].strip()
                    brand = row[brand_index].strip() if len(row) > brand_index else ""
                    reference = row[reference_index].strip() if len(row) > reference_index else ""
                    pending_products.append((name, brand, reference))

        logging.info(f"Found {len(pending_products)} products without ASIN.")
    except FileNotFoundError:
        logging.error(f"Product file not found: {file_path}")
    except Exception as e:
        logging.exception(f"Error reading product names: {e}")

    return pending_products



# ==================== Main Program ====================
def amazon_scraper():
    file_path = "king_jouet_Products.csv"
    product_entries = read_pending_products(file_path)

    for name, brand, reference in product_entries:
        scrape_amazon(name, brand, reference, file_path)
        time.sleep(3)


# if __name__ == "__main__":
#     amazon_scraper()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        amazon_scraper()
