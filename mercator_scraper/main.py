import logging
from src.config import PROJECT_URLS, OUTPUT_FILE, RETRIES
from src.scraper import get_page, parse_project_section, transform_data, save_to_json

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run():
    full_data = []
    for url in PROJECT_URLS:
        logging.info(f"Scraping {url}")
        try:
            html = get_page(url, RETRIES)
            project_details = parse_project_section(html)
            if project_details:
                transformed = transform_data(project_details)
                full_data.append(transformed)
            else:
                logging.info(f"Could not parse {url}")
        except Exception as e:
            logging.info(f"Error scraping {url}: {e}")
    
    save_to_json(OUTPUT_FILE, full_data)


if __name__ == "__main__":
    run()