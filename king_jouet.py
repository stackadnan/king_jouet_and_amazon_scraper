import requests,random,logging,json,csv,os
from time import sleep
from bs4 import BeautifulSoup
from ean_scraper import EAN
from amazon_scraper import amazon_scraper

# ==================== Logging Configuration ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==================== Load Cookies ====================
def load_cookies_from_file(filepath: str) -> str:
    """Read and return cookies from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            cookies = file.read().strip()
            logging.info("✅ Cookies loaded successfully.")
            return cookies
    except FileNotFoundError:
        logging.error("❌ Cookie file not found.")
        return ""

# ==================== Generate URL ====================
def generate_king_jouet_url(title, reference, category, subcategory):
    def slugify(text):
        return (
            text.lower()
            .replace("'", "")
            .replace(",", "")
            .replace("’", "")
            .replace("–", "-")
            .replace(":", "")
            .replace("!", "")
            .replace("?", "")
            .replace(".", "")
            .replace("à", "a")
            .replace("â", "a")
            .replace("ç", "c")
            .replace("é", "e")
            .replace("è", "e")
            .replace("ê", "e")
            .replace("ë", "e")
            .replace("î", "i")
            .replace("ï", "i")
            .replace("ô", "o")
            .replace("ù", "u")
            .replace("û", "u")
            .replace("ü", "u")
            .replace(" ", "-")
        )
    
    cat_slug = slugify(category or "")
    subcat_slug = slugify(subcategory or "")
    title_slug = slugify(title or "")
    return f"https://www.king-jouet.com/jeu-jouet/{cat_slug}/{subcat_slug}/ref-{reference}-{title_slug}.htm"

# ==================== Parse & Save Product Data ====================
def parse_and_save_product_data(html_content: str, page_index: int, csv_filepath: str):
    """
    Parse product data from the given HTML and append it to the CSV.
    Only processes elements with 'data-ekind' == 'Product'.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    product_elements = soup.find_all('div', {'data-ekind': 'Product'})
    products = []

    for product_div in product_elements:
        hidden_input = product_div.find('input', {'type': 'hidden'})
        if hidden_input:
            try:
                product_json = json.loads(hidden_input['value'])

                title = product_json.get('Libelle')
                reference = product_json.get('Reference')
                category = product_json.get('Segmentation')
                subcategory = product_json.get('Segmentation02')

                product_info = {
                    'Page': page_index,  # Save page index for tracking
                    'Title': title,
                    'Brand': product_json.get('Marque'),
                    'Reference': reference,
                    'Category': category,
                    'Subcategory': subcategory,
                    'Availability': "Available in central stock" if product_json.get('DisponibleCentrale') else "Not available",
                    'PriceHT': product_json.get('PuHT'),
                    'PriceTTC': product_json.get('PuTTC'),
                    'SalePriceHT': product_json.get('PuPromoHT'),
                    'SalePriceTTC': product_json.get('PuPromoTTC'),
                    'DiscountPercentage': product_json.get('PctRemise'),
                    'ID': product_json.get('ID'),
                    'dateDebutPromo': product_json.get('DateDebutPromo'),
                    'dateFinPromo': product_json.get('DateFinPromo'),
                    'product url': generate_king_jouet_url(title.replace("---","-").replace("--","-"), reference, category.replace("&",""), subcategory.split()[0]),
                    'EAN':"",
                    'ASIN':"",
                    'Amazon_Brand':"",
                    'Amazon_Price':"",
                    'Amazon_URL':"",
                }
                products.append(product_info)
            except Exception as e:
                logging.error(f"❌ Error parsing product JSON: {e}")

    if products:
        file_exists = os.path.isfile(csv_filepath)
        with open(csv_filepath, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=products[0].keys())
            if not file_exists or os.path.getsize(csv_filepath) == 0:
                writer.writeheader()
            writer.writerows(products)
        logging.info(f"✅ Page {page_index}: {len(products)} products saved to CSV.")
    else:
        logging.warning(f"⚠️ No product data found on page {page_index}.")

# ==================== Build Request Headers ====================
def get_request_headers(cookies: str) -> dict:
    """Build headers for HTTP requests including cookies."""
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'if-modified-since': 'Thu, 10 Apr 2025 11:28:43 GMT',
        'if-none-match': 'W/"68a02-MVfEyDGg8AjEsMNacbF3FTI1EEQ"',
        'priority': 'u=0, i',
        'referer': 'https://www.king-jouet.com/jeux-jouets/promotions/page1.htm',
        'sec-ch-device-memory': '8',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'cookie': cookies,
    }

# ==================== Fetch & Process Page ====================
def fetch_and_process_page(page_number: int, headers: dict, csv_filepath: str) -> bool:
    """Fetch and process a single promotion page."""
    url = f'https://www.king-jouet.com/jeux-jouets/promotions/page{page_number}.htm'
    logging.info(f"📄 Fetching page {page_number}: {url}")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logging.info(f"✅ Page {page_number} fetched successfully.")
        soup = BeautifulSoup(response.text, 'html.parser')
        # Optionally, save the page locally for debugging
        # with open('page.html', 'w', encoding='utf-8') as file:
        #     file.write(soup.prettify())
        # logging.info(f"✅ Page {page_number} saved as 'page.html'.")
        product_section = soup.find('div', class_='ais-Hits-list list-articles grid grid-cols-2 md:grid-cols-3 gap-1 xl:grid-cols-4 2xl:grid-cols-5 2xl:gap-4')

        if product_section:
            parse_and_save_product_data(product_section.prettify(), page_number, csv_filepath)
        else:
            logging.warning(f"⚠️ No product container found on page {page_number}.")

        sleep_duration = random.randint(8, 22)
        logging.info(f"😴 Sleeping for {sleep_duration} seconds to mimic human behavior.")
        sleep(sleep_duration)

    # Handle known response statuses
    elif response.status_code in [403, 304]:
        logging.warning(f"⚠️ Access issue or not modified: Status {response.status_code} on page {page_number}.")
    elif response.status_code == 404:
        logging.error(f"❌ Page {page_number} not found (404). Stopping further processing.")
        return False
    elif response.status_code in [500, 301, 302]:
        logging.error(f"❌ Server error or redirection: Status {response.status_code} on page {page_number}.")
        return False
    elif response.status_code == 503:
        logging.warning("⚠️ Service unavailable (503). Sleeping before retrying...")
        sleep(random.randint(30, 60))
    elif response.status_code == 429:
        logging.warning("⚠️ Rate limited (429). Sleeping longer before retrying...")
        sleep(random.randint(60, 120))
    elif response.status_code == 408:
        logging.warning("⚠️ Request timeout (408). Sleeping before retrying...")
        sleep(random.randint(10, 30))
    else:
        logging.error(f"❌ Unhandled status code {response.status_code} for page {page_number}.")
        return False

    return True

# ==================== Utility Functions ====================

def get_last_saved_page(csv_file: str) -> int:
    """
    Reads the CSV file and returns the maximum page number found in the first column.
    Assumes that the first row is the header.
    """
    if not os.path.exists(csv_file):
        return 0
    last_page = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip the header row
            for row in reader:
                if row and row[0].isdigit():
                    page_num = int(row[0])
                    if page_num > last_page:
                        last_page = page_num
        logging.info(f"✅ Last saved page in CSV: {last_page}.")
    except Exception as e:
        logging.error(f"❌ Error reading CSV for last page: {e}")
    return last_page


# ==================== Main Scraper Loop ====================

def main():
    csv_file = 'king_jouet_Products.csv'
    cookies = load_cookies_from_file('cookies.txt')
    if not cookies:
        logging.error("❌ No cookies available. Exiting.")
        return

    headers = get_request_headers(cookies)

    choice = input("🟡 Do you want to start fresh or continue? (enter '1' or '2'): ")

    if choice == '1':
        if os.path.exists(csv_file):
            os.remove(csv_file)
            logging.info("🧹 Old CSV file removed.")
        start_page = 1
    elif choice == '2':
        start_page = get_last_saved_page(csv_file) + 1
        logging.info(f"🔄 Continuing from page {start_page}.")
    else:
        logging.error("❌ Invalid choice. Exiting.")
        return

    max_page = 87  # or your desired maximum
    for page in range(start_page, max_page + 1):
        success = fetch_and_process_page(page, headers, csv_file)
        print(f"Pages Completed: {page}/{max_page} no More Pages to fetch")
        print("\n\n-----------------Now Getting EAN-----------------")
        EAN(csv_file)
        print("\n-----------------EAN Fetched Sucessfully-----------------")
        print("\n\n-----------------Now Getting ASIN And Amazon Product URL-----------------")
        amazon_scraper()
        print("\n-----------------ASIN Fetched Sucessfully-----------------")
        if not success:
            logging.info("🛑 Terminating script due to unsuccessful page fetch.")
            return



if __name__ == "__main__":
    main()


# ==================== Entry Point ====================
if __name__ == "__main__":
    main()
