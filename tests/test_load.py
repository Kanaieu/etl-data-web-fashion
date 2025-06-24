import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from utils.load import store_to_postgre, store_to_csv, store_to_google_sheets

df_sample = pd.DataFrame({
    'name': ['T-shirt', 'Jacket'],
    'price': [20000, 35000],
    'rating': [4.5, 4.8]
})

def test_store_to_postgre_success():
    with patch('utils.load.create_engine') as mock_engine, \
         patch.object(df_sample, 'to_sql') as mock_to_sql:  # Mock to_sql method dari DataFrame
         
        mock_conn = MagicMock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        store_to_postgre(df_sample, 'postgresql://dummy_url')
        
        mock_to_sql.assert_called_once()

def test_store_to_postgre_error():
    with patch('utils.load.create_engine', side_effect=Exception("DB error")):
        store_to_postgre(df_sample, 'postgresql://invalid_url')

def test_store_to_csv_success(tmp_path):
    file_path = tmp_path / "test.csv"
    store_to_csv(df_sample, file_path)
    
    # Validasi hasil file
    df_loaded = pd.read_csv(file_path)
    assert df_loaded.equals(df_sample)


def test_store_to_csv_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise Exception("CSV error")

    monkeypatch.setattr("pandas.DataFrame.to_csv", raise_error)
    store_to_csv(df_sample, "fake.csv")


@patch("utils.load.service_account.Credentials")
@patch("utils.load.build")
def test_store_to_google_sheets_success(mock_build, mock_creds):
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
        'updatedCells': 6
    }

    store_to_google_sheets(
        df_sample,
        spreadsheet_id="spreadsheet123",
        range_name="Sheet1!A1",
        creds_path="path/to/fake/credentials.json"
    )

    mock_build.assert_called_once()
    mock_creds.from_service_account_file.assert_called_once()


@patch("utils.load.service_account.Credentials.from_service_account_file", side_effect=Exception("Auth error"))
def test_store_to_google_sheets_error(mock_creds):
    with pytest.raises(Exception) as exc_info:
        store_to_google_sheets(
            df_sample,
            spreadsheet_id="spreadsheet123",
            range_name="Sheet1!A1",
            creds_path="wrong.json"
        )
    # Opsional: cek pesan error
    assert "Auth error" in str(exc_info.value)