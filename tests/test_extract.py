import pytest
from bs4 import BeautifulSoup
from unittest.mock import patch, Mock

from utils.extract import extract_product_data, fetching_content, scrape_product


def test_extract_product_data():
    html = """
    <div class="collection-card">
        <div class="product-details">
            <h3 class="product-title">T-shirt 2</h3>
            <div class="price-container">
                <span class="price">$102.15</span>
            </div>
            <p>Rating: ⭐ 3.9 / 5</p>
            <p>3 Colors</p>
            <p>Size: M</p>
            <p>Gender: Women</p>
        </div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    card = soup.find('div', class_='collection-card')
    result = extract_product_data(card)

    assert result["Title"] == "T-shirt 2"
    assert result["Price"] == "$102.15"
    assert result["Rating"] == "⭐ 3.9 / 5"
    assert result["Colors"] == "3"
    assert result["Size"] == "M"
    assert result["Gender"] == "Women"


@patch("utils.extract.requests.Session")
def test_fetching_content(mock_session):
    # Setup response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body><p>Mock Page</p></body></html>"
    mock_response.raise_for_status = Mock()
    
    # Setup session.get to return mock_response
    mock_session.return_value.get.return_value = mock_response

    url = "http://example.com"
    result = fetching_content(url)
    assert b"Mock Page" in result


@patch("utils.extract.fetching_content")
def test_scrape_product(mock_fetching_content):
    html = """
    <html>
        <body>
            <div class="collection-card">
                <div class="product-details">
                    <h3 class="product-title">T-shirt 2</h3>
                    <div class="price-container">
                        <span class="price">$102.15</span>
                    </div>
                    <p>Rating: ⭐ 3.9 / 5</p>
                    <p>3 Colors</p>
                    <p>Size: M</p>
                    <p>Gender: Women</p>
                </div>
            </div>
        </body>
    </html>
    """
    # Simulasi hanya 1 halaman (tanpa <li class="next">)
    mock_fetching_content.return_value = html

    base_url = "http://mocksite.com/"
    page_url = "http://mocksite.com/page{}.html"
    data = scrape_product(base_url, page_url)

    assert len(data) == 1
    assert data[0]["Title"] == "T-shirt 2"