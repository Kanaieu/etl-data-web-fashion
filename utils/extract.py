import time
import requests

from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}
 
 
def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan dengan error handling."""
    try:
        session = requests.Session()
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.HTTPError as e:
        print(f"[HTTP ERROR] {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"[CONNECTION ERROR] {url}: {e}")
    except requests.exceptions.Timeout as e:
        print(f"[TIMEOUT ERROR] {url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"[REQUEST ERROR] {url}: {e}")
    return None


def extract_product_data(card):
    """Ekstraksi data produk dari elemen HTML dengan pengecekan masing-masing field."""
    try:
        product_title = card.find('h3', class_='product-title')
        product_title = product_title.text.strip() if product_title else 'N/A'

        price_container = card.find('div', class_='price-container')
        if price_container:
            price_span = price_container.find('span', class_='price')
            price = price_span.text.strip() if price_span else 'N/A'
        else:
            price_p = card.find('p', class_='price')
            price = price_p.text.strip() if price_p else 'N/A'

        p_tags = card.find_all('p')
        rating = colors = size = gender = None

        for p in p_tags:
            text = p.get_text(strip=True)
            if text.startswith('Rating:'):
                rating = text.split('Rating:')[1].strip()
            elif 'Colors' in text:
                colors = text.split(' ')[0].strip()
            elif text.startswith('Size:'):
                size = text.split('Size:')[1].strip()
            elif text.startswith('Gender:'):
                gender = text.split('Gender:')[1].strip()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        product = {
            "Title": product_title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "Timestamp": timestamp,
        }

        return product
    except Exception as e:
        print(f"[ERROR EXTRACTING PRODUCT] {e}")
        return {
            "Title": "N/A",
            "Price": "N/A",
            "Rating": None,
            "Colors": None,
            "Size": None,
            "Gender": None,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def scrape_product(base_url, base_url_paged, start_page=1, delay=2):
    """Fungsi utama untuk scraping, dilengkapi dengan error handling tiap tahap."""
    data = []
    page_number = start_page

    while True:
        try:
            if page_number == 1:
                url = base_url
            else:
                url = base_url_paged.format(page_number)

            print(f"Scraping halaman: {url}")

            content = fetching_content(url)
            if not content:
                print("[INFO] Konten kosong atau gagal diambil.")
                break

            soup = BeautifulSoup(content, "html.parser")
            cards_element = soup.find_all('div', class_='collection-card')
            if not cards_element:
                print("[INFO] Tidak ada produk ditemukan di halaman ini.")
                break

            for card in cards_element:
                product = extract_product_data(card)
                data.append(product)

            next_button = soup.find('li', class_='next')
            if next_button:
                page_number += 1
                time.sleep(delay)
            else:
                break
        except Exception as e:
            print(f"[ERROR SCRAPING PAGE {page_number}] {e}")
            break

    return data