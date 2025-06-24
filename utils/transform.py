import pandas as pd
import re

dirty_patterns = {
    "Title": ["Unknown Product"],
    "Rating": ["Not Rated"],
    "Price": ["Price Unavailable", None],
}

def transform_to_DataFrame(data):
    """Mengubah data menjadi DataFrame."""
    try:
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error saat mengubah data menjadi DataFrame: {e}")
        return pd.DataFrame()

def clean_rating(value):
    try:
        if isinstance(value, str):
            if value in ["Not Rated", "No rating", None]:
                return None
            
            # Regex harus match keseluruhan string yang valid seperti '⭐ 4.5 / 5'
            pattern = r'^⭐\s*(\d+(\.\d+)?)\s*/\s*5$'
            match = re.match(pattern, value)
            if match:
                val = float(match.group(1))
                if 0 <= val <= 5:
                    return val
        return None
    except Exception as e:
        print(f"Error saat membersihkan rating '{value}': {e}")
        return None

def transform_data(data, exchange_rate):
    """Menggabungkan semua transformasi data menjadi satu fungsi dengan error handling."""
    try:
        # Menghapus data yang tidak valid
        for column, invalid_values in dirty_patterns.items():
            if column in data.columns:
                data = data[~data[column].isin(invalid_values)]
            else:
                print(f"Peringatan: Kolom '{column}' tidak ditemukan di data")

        data.reset_index(drop=True, inplace=True)
    except Exception as e:
        print(f"Error saat menghapus data tidak valid: {e}")
        return data

    try:
        # Transformasi Price
        if 'Price' in data.columns:
            data['Price'] = data['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            data['Price'] = pd.to_numeric(data['Price'], errors='coerce')  # pakai to_numeric agar bisa handle error parsing
            data['Price'] = data['Price'] * exchange_rate
        else:
            print("Peringatan: Kolom 'Price' tidak ditemukan di data")
    except Exception as e:
        print(f"Error saat transformasi Price: {e}")

    try:
        # Transformasi Rating
        # if 'Rating' in data.columns:
        #     data['Rating'] = data['Rating'].apply(clean_rating)
        #     data = data[data['Rating'].notnull()]
        if 'Rating' in data.columns:
            data['Rating'] = data['Rating'].apply(clean_rating)
            print("Setelah clean_rating dan filtering:")
            print(data)
            data = data[data['Rating'].notnull()]
            print("Setelah filtering rating not null:")
            print(data)
        else:
            print("Peringatan: Kolom 'Rating' tidak ditemukan di data")
    except Exception as e:
        print(f"Error saat transformasi Rating: {e}")

    try:
        # Transformasi kolom 'Colors' menjadi angka saja
        if 'Colors' in data.columns:
            def extract_colors(x):
                try:
                    if pd.isna(x):
                        return None
                    if isinstance(x, (int, float)):
                        return int(x)
                    if isinstance(x, str):
                        match = re.search(r'\d+', x)
                        if match:
                            return int(match.group())
                    return None
                except Exception as ex:
                    print(f"Error mengkonversi Colors '{x}': {ex}")
                    return None
            data['Colors'] = data['Colors'].apply(extract_colors)
            data = data[data['Colors'].notna()]
        else:
            print("Peringatan: Kolom 'Colors' tidak ditemukan di data")
    except Exception as e:
        print(f"Error saat transformasi Colors: {e}")

    try:
        # Transformasi kolom 'Size' menjadi 1 huruf saja
        if 'Size' in data.columns:
            data['Size'] = data['Size'].astype(str).str.replace(r'^Size:\s*', '', regex=True)
            data = data[data['Size'].notna() & (data['Size'] != '') & (data['Size'].str.lower() != 'none')]
        else:
            print("Peringatan: Kolom 'Size' tidak ditemukan di data")
    except Exception as e:
        print(f"Error saat transformasi Size: {e}")

    try:
        # Transformasi kolom 'Gender'
        if 'Gender' in data.columns:
            data['Gender'] = data['Gender'].astype(str).str.replace(r'^Gender:\s*', '', regex=True)
        else:
            print("Peringatan: Kolom 'Gender' tidak ditemukan di data")
    except Exception as e:
        print(f"Error saat transformasi Gender: {e}")

    try:
        # Menghapus nilai redundan (duplikat)
        data = data.drop_duplicates(keep='first').reset_index(drop=True)
    except Exception as e:
        print(f"Error saat menghapus duplikat: {e}")

    try:
        # Transformasi Tipe Data
        if 'Title' in data.columns:
            data['Title'] = data['Title'].astype(object)
        if 'Gender' in data.columns:
            data['Gender'] = data['Gender'].astype(object)
    except Exception as e:
        print(f"Error saat transformasi tipe data: {e}")

    return data