from sqlalchemy import create_engine
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
 
def store_to_postgre(data, db_url):
    """Fungsi untuk menyimpan data ke dalam PostgreSQL."""
    try:
        # Membuat engine database
        engine = create_engine(db_url)
        
        # Menyimpan data ke tabel 'fashionstudio' jika tabel sudah ada, data akan ditambahkan (append)
        with engine.connect() as con:
            data.to_sql('fashionstudio', con=con, if_exists='append', index=False)
            print("Data berhasil ditambahkan!")
    
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data: {e}")
        
# to csv and to google sheet
def store_to_csv(data, filename="products.csv"):
    try:
        data.to_csv(filename, index=False)
        print(f"Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data ke CSV: {e}")
        
def store_to_google_sheets(data, spreadsheet_id, range_name, creds_path):
    """
    Upload DataFrame ke Google Sheets via Google Sheets API.

    Args:
        data (pd.DataFrame): Data yang akan diupload.
        spreadsheet_id (str): ID dari Google Sheet.
        range_name (str): Range tujuan, misal: 'Sheet1!A1'.
        creds_path (str): Path ke service account JSON.
    """
    try:
        # Autentikasi
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        # Format data: header + isi
        values = [data.columns.tolist()] + data.astype(str).values.tolist()
        body = {'values': values}

        # Kirim data ke Google Sheets
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"{result.get('updatedCells')} cells updated to Google Sheets.")

    except FileNotFoundError:
        print(f"File JSON untuk autentikasi tidak ditemukan di path: {creds_path}")
        raise
    except KeyError as e:
        print(f"Kunci yang hilang dalam file JSON: {e}")
        raise
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data ke Google Sheets: {e}")
        raise