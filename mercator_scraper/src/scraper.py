import json
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.config import SITE_DATE_FORMAT

def get_page(url, retries=2):
   for retry in range(1, retries + 1):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            logging.warning(f"HTTP error for {url} on try {retry}: {e}")
        except requests.exceptions.Timeout:
            logging.warning(f"Timed out on attempt {retry} for {url}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error for {url} on try {retry}")
        
        if retry < retries:
            logging.info(f"Retrying for {url}")
            
   logging.error(f"Failed to get page after {retries} for {url}")
   return None

def parse_project_section(page_html):
    bs = BeautifulSoup(page_html, "html.parser")
    project_section = bs.find("div", class_="project-details-project")
    if not project_section:
        return None
    
    project_details = {}

    for dl in project_section.find_all('dl'):
        dt_tags = dl.find_all("dt")
        dd_tags = dl.find_all("dd")

        for dt, dd in zip(dt_tags, dd_tags):
            key = dt.text.strip().replace(":", "")
            val = dd.text.strip()
            project_details[key] = val
    return project_details

def transform_data(raw_data):
    mapped_data = {
        "event_id": raw_data.get("Project Number", ""),
        "address": raw_data.get("Location Address", ""),
        "event_created_at": datetime.strptime(raw_data.get("Start Date", None), SITE_DATE_FORMAT).date().isoformat(),
        "description": f'{raw_data.get("Project Name", "")}: {raw_data.get("Type of Work", "")} {raw_data.get("Scope of Work", "")}',
        "category": raw_data.get("Type of Work", "")
    }
    return mapped_data

def save_to_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)