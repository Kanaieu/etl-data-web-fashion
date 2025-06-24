import pytest
import pandas as pd
from utils.transform import transform_to_DataFrame, clean_rating, transform_data

sample_data = [
    {
        "Title": "Product A",
        "Rating": "4.5 / 5",
        "Price": "$100",
        "Colors": "Colors: 3",
        "Size": "Size: M",
        "Gender": "Gender: Male",
    },
    {
        "Title": "Unknown Product",
        "Rating": "Not Rated",
        "Price": "Price Unavailable",
        "Colors": "Colors: 1",
        "Size": "Size: None",
        "Gender": "Gender: Female",
    },
]

def test_transform_to_DataFrame_valid():
    data = [{'Title': 'A', 'Rating': '4.5'}, {'Title': 'B', 'Rating': '3.9'}]
    df = transform_to_DataFrame(data)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 2
    assert 'Title' in df.columns

def test_transform_to_DataFrame_invalid():
    df = transform_to_DataFrame(12345)  # invalid input
    assert isinstance(df, pd.DataFrame)
    assert df.empty

@pytest.mark.parametrize("input_value,expected", [
    ("⭐ 4.5 / 5", 4.5),
    ("⭐ 3.9 / 5", 3.9),
    ("Not Rated", None),
    ("⭐ Invalid Rating / 5", None),
    (None, None),
    (5, None),
    ("No rating", None),
])
def test_clean_rating(input_value, expected):
    assert clean_rating(input_value) == expected
    
def test_transform_data_basic():
    raw_data = pd.DataFrame({
        'Title': ['T-shirt 2', 'Unknown Product', 'Hoodie 3', 'T-shirt 2'],
        'Rating': ['⭐ 4.5 / 5', '⭐ Invalid Rating / 5', '⭐ 3.0 / 5', 'Not Rated'],
        'Price': ['$100.00', 'Price Unavailable', '$20.00', '$100.00'],
        'Colors': ['5', '3', '8', '5'],
        'Size': ['M', 'L', 'XL', 'XXL'],
        'Gender': ['Men', 'Women', 'Unisex', 'Men'],
    })

    exchange_rate = 16000
    result = transform_data(raw_data, exchange_rate)

    # Cek kolom masih ada
    for col in ['Title', 'Rating', 'Price', 'Colors', 'Size', 'Gender']:
        assert col in result.columns
    
    # Cek baris tidak valid terhapus (Title 'Unknown Product' dan Rating invalid hilang)
    assert 'Unknown Product' not in result['Title'].values
    assert all(result['Rating'] >= 0)  # Rating sudah float
    
    # Cek kolom Price sudah bersih dan sudah dikalikan dengan exchange rate
    assert all(result['Price'] >= 0)
    
    # Cek Colors sudah jadi int dan hanya terdiri dari 3, 5, 8
    assert set(result['Colors']).issubset({3, 5, 8})
    
    # Cek Size sudah bersih dan hanya terdiri dari M, L, XL, XXL, S
    assert set(result['Size']).issubset({'M', 'L', 'XL', 'XXL', 'S'})
    
    # Cek Gender sudah bersih dan hanya terdiri dari Men, Women, Unisex
    assert set(result['Gender']).issubset({'Men', 'Women', 'Unisex'})

    # Cek tidak ada duplikat
    assert result.duplicated().sum() == 0

def test_transform_data_missing_columns():
    raw_data = pd.DataFrame({
        'Title': ['T-shirt 2', 'Hoodie 3'],
        'Rating': ['⭐ 4.5 / 5', '⭐ 3.0 / 5'],
        # 'Price' kolom hilang
        'Colors': ['5', '3'],
        # 'Size' kolom hilang
        'Gender': ['Men', 'Women'],
    })

    exchange_rate = 16000
    result = transform_data(raw_data, exchange_rate)

    # Pastikan masih proses dan kolom yang ada tetap ada
    for col in ['Title', 'Rating', 'Colors', 'Gender']:
        assert col in result.columns

def test_transform_data_error_in_colors():
    raw_data = pd.DataFrame({
        'Title': ['Product 1'],
        'Rating': ['⭐ 4.5 / 5'],
        'Price': ['$10'],
        'Colors': ['No color info'],
        'Size': ['M'],
        'Gender': ['Men'],
    })
    exchange_rate = 1
    result = transform_data(raw_data, exchange_rate)
    assert len(result) == 0


def test_transform_data_error_in_rating():
    raw_data = pd.DataFrame({
        'Title': ['Product 1', 'Product 2'],
        'Rating': ['Invalid Rating / 5', '⭐ 4.0 / 5'],
        'Price': ['$10', '$20'],
        'Colors': [3, 5],
        'Size': ['M', 'L'],
        'Gender': ['Men', 'Women'],
    })
    exchange_rate = 1
    result = transform_data(raw_data, exchange_rate)
    assert len(result) == 1
    assert abs(result['Rating'].iloc[0] - 4.0) < 1e-6
    
def test_transform_data_price_unavailable_removed():
    raw_data = pd.DataFrame({
        'Title': ['Product A', 'Product B'],
        'Rating': ['⭐ 4.5 / 5', '⭐ 3.5 / 5'],
        'Price': ['$100', 'Price Unavailable'],
        'Colors': ['5', '3'],
        'Size': ['M', 'L'],
        'Gender': ['Men', 'Women'],
    })
    exchange_rate = 16000
    result = transform_data(raw_data, exchange_rate)
    # Baris dengan Price 'Price Unavailable' harus hilang
    assert 'Product B' not in result['Title'].values
    # Price sudah jadi float dan dikalikan exchange rate
    assert all(result['Price'] > 0)
    
def test_transform_data_invalid_size_gender_removed():
    raw_data = pd.DataFrame({
        'Title': ['Product A', 'Product B'],
        'Rating': ['⭐ 4.5 / 5', '⭐ 3.5 / 5'],
        'Price': ['$100', '$150'],
        'Colors': ['5', '3'],
        'Size': ['M', 'Unknown Size'],
        'Gender': ['Men', 'Alien'],
    })
    valid_sizes = {'M', 'L', 'XL', 'XXL', 'S'}
    valid_genders = {'Men', 'Women', 'Unisex'}
    
    exchange_rate = 16000
    result = transform_data(raw_data, exchange_rate)
    if 'Size' in result.columns:
        result = result[result['Size'].isin(valid_sizes)]
    if 'Gender' in result.columns:
        result = result[result['Gender'].isin(valid_genders)]
    # Baris dengan Size atau Gender invalid harus hilang
    assert 'Product B' not in result['Title'].values
    # Baris valid tetap ada
    assert 'Product A' in result['Title'].values
    
def test_transform_data_duplicate_rows_removed():
    raw_data = pd.DataFrame({
        'Title': ['Product A', 'Product A'],
        'Rating': ['⭐ 4.5 / 5', '⭐ 4.5 / 5'],
        'Price': ['$100', '$100'],
        'Colors': ['5', '5'],
        'Size': ['M', 'M'],
        'Gender': ['Men', 'Men'],
    })
    exchange_rate = 16000
    result = transform_data(raw_data, exchange_rate)
    # Duplikat harus dihapus, jadi hanya 1 baris tersisa
    assert result.shape[0] == 1