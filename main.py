from utils.extract import scrape_product
from utils.transform import transform_to_DataFrame, transform_data
from utils.load import store_to_postgre, store_to_csv, store_to_google_sheets

def main():
    """Fungsi utama untuk keseluruhan proses scraping hingga menyimpannya."""
    BASE_URL = 'https://fashion-studio.dicoding.dev/'
    PAGE_URL = 'https://fashion-studio.dicoding.dev/page{}.html'
    all_products_data = scrape_product(BASE_URL, PAGE_URL)
    if all_products_data:
        try:
            # Mengubah data menjadi DataFrame
            DataFrame = transform_to_DataFrame(all_products_data)
            
            DataFrame = transform_data(DataFrame, 16000)
 
            # Menyimpan data ke PostgreSQL
            db_url = 'postgresql+psycopg2://developer:Hahgakjelas1@localhost:5432/fashionsdb'
            store_to_postgre(DataFrame, db_url)
            
            # Menyimpan ke CSV
            store_to_csv(DataFrame, 'fashion_data.csv')
            
            # Menyimpan ke Google Sheets
            spreadsheet_id = '1xLFMe1U0P2uKwsKzuUQ1VP5R09vHDFyza_qlaD--lxY'
            range_name = 'Sheet1!A1'
            store_to_google_sheets(DataFrame, spreadsheet_id, range_name, 'google-sheets-api.json')
 
        except Exception as e:
            print(f"Terjadi kesalahan dalam proses: {e}")
    else:
        print("Tidak ada data yang ditemukan.")
 
 
if __name__ == '__main__':
    main()