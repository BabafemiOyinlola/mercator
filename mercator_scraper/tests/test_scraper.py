import requests
from unittest.mock import MagicMock, patch
from src.scraper import get_page, parse_project_section, transform_data

def test_transform_data():
    raw_details = {
        "Project Number": "EABPRJ93000456",
        "Location Address": "1600 SARAH DEWITT CENTER Gonzales, TX 78629",
        "Start Date": "1/1/1900",
        "Project Name": "LEASE 657-7742-E3-GONZALES",
        "Type of Work": "Unknown",
        "Scope of Work": ""
    }

    transformed_details = transform_data(raw_details)
    assert transformed_details["event_id"] == "EABPRJ93000456"
    assert transformed_details["address"] == "1600 SARAH DEWITT CENTER Gonzales, TX 78629"
    assert transformed_details["event_created_at"] == "1900-01-01"
    assert "LEASE 657-7742-E3-GONZALES: Unknown" in transformed_details["description"]
    assert transformed_details["category"] == "Unknown"

def test_parse_project_section():
    source_html = """
    <div class="project-details-project">
        <dl>
            <dt>Project Number:</dt><dd>EABPRJ93000456</dd>
            <dt>Location Address:</dt><dd>1600 SARAH DEWITT CENTER Gonzales, TX 78629</dd>
        </dl>
    </div>
    """
    project_details = parse_project_section(source_html)
    assert project_details["Project Number"] == "EABPRJ93000456"
    assert project_details["Location Address"] == "1600 SARAH DEWITT CENTER Gonzales, TX 78629"

@patch("src.scraper.requests.get")
def test_get_page_success(mock):
    mock_response = MagicMock()
    mock_response.text = "<div>Sample Response</div>"
    mock_response.raise_for_status.return_value = None
    mock.return_value = mock_response
    page_response = get_page("https://www.tdlr.texas.gov/TABS/Search/Project/sample")
    assert page_response == "<div>Sample Response</div>"
    assert mock.call_count == 1

@patch("src.scraper.requests.get")
def test_get_page_failure(mock):
    mock.side_effect = requests.exceptions.HTTPError("404 Not Found")
    page_response = get_page("https://www.tdlr.texas.gov/TABS/Search/Project/sample", retries=2)
    
    assert page_response is None
    assert mock.call_count == 2