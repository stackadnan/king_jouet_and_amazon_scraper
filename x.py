# # import requests
# # from bs4 import BeautifulSoup
# # import urllib.parse

# # def fetch_amazon_search_html(title: str, brand: str, reference: str, output_file="amazon.html"):
# #     # Combine search keywords
# #     search_keywords = f"{title},{brand},{reference}"
    
# #     # Encode for URL and query
# #     encoded_keywords = urllib.parse.quote_plus(search_keywords)
    
# #     base_url = "https://www.amazon.fr/s"
# #     querystring = {
# #         "k": search_keywords,
# #         "i": "toys",
# #         "__mk_fr_FR": "ÅMÅŽÕÑ",
# #         "ref": "nb_sb_noss"
# #     }

# #     headers = {
# #         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
# #     }

# #     response = requests.get(base_url, headers=headers, params=querystring)

# #     print(f"Status Code: {response.status_code}")
# #     if response.status_code == 200:
# #         soup = BeautifulSoup(response.text, "html.parser")
        
# #         # Save the full HTML
# #         with open(output_file, "w", encoding="utf-8") as file:
# #             file.write(soup.prettify())
# #         price_tags = soup.find_all("span", class_="a-price")
# #         prices = []

# #         for tag in price_tags:
# #             whole = tag.find("span", class_="a-price-whole")
# #             fraction = tag.find("span", class_="a-price-fraction")
# #             symbol = tag.find("span", class_="a-price-symbol")
            
# #             if whole and fraction and symbol:
# #                 price = f"{whole.get_text(strip=True)},{fraction.get_text(strip=True)}{symbol.get_text(strip=True)}"
# #                 prices.append(price)
# #             elif whole and symbol:
# #                 # In case there's no fraction part (e.g., whole number like "20€")
# #                 price = f"{whole.get_text(strip=True)}{symbol.get_text(strip=True)}"
# #                 prices.append(price)

# #         if prices:
# #             price = prices[0]
# #             print(f"Found Price: {price}")
# #         else:
# #             price = "N/A"
# #             print("No price found for this product.")

# #         # Find all prices
# #         # price_tags = soup.find_all("span", class_="a-price")
# #         # prices = [tag.get_text(strip=True) for tag in price_tags]
        
# #         # print("Found Prices:")
        
# #         # price = (prices[0].strip().replace(" ", "")).split('€')[0] + '€'
# #         # print(price)

# #     else:
# #         print("Failed to fetch the page.")
# # for i in range(500):
# #     print(i)
# #     fetch_amazon_search_html(
# #         title="Trampoline 183 cm avec filet",
# #         brand="SUN and SPORT",
# #         reference="952705"
# #     )



# import requests

# url = "https://real-time-amazon-data.p.rapidapi.com/search"

# querystring = {"query":"Phone","page":"1","country":"US","sort_by":"RELEVANCE","product_condition":"ALL","is_prime":"false","deals_and_discounts":"NONE"}

# headers = {
# 	"x-rapidapi-key": "5a7b79ad9dmsh05edb2ebd9dda41p191385jsn422c8c2cd042",
# 	"x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# print(response.json())
# with open("amazon.json", "w") as f:
#     f.write(response.text)



import pandas as pd

def remove_column_from_csv(file_path):
    # Load the CSV
    df = pd.read_csv(file_path)
    print("Available columns:", list(df.columns))

    # Ask user for column name to remove
    column_to_remove = input("Enter the column name you want to remove: ")

    if column_to_remove in df.columns:
        df.drop(columns=[column_to_remove], inplace=True)
        # Save the updated CSV (overwrite the original or change filename as needed)
        df.to_csv(file_path, index=False)
        print(f"Column '{column_to_remove}' removed and CSV updated.")
    else:
        print(f"Column '{column_to_remove}' not found in the CSV.")

# Example usage
if __name__ == "__main__":
    file_path = input("Enter the path to your CSV file: ")
    remove_column_from_csv(file_path)
