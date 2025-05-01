import requests
from bs4 import BeautifulSoup
import re
import csv
import cloudscraper
import pandas as pd
import logging
import time
import random

allDjsPath = "top100djs_by_year_cleaned_names.csv"

BASE_URL = "https://www.whosampled.com"
NAMES = pd.read_csv(allDjsPath).dropna()['DJ Name'].unique()

def normalize_name(name):
    return name.replace(" ","-")
    
logging.basicConfig(filename='attempt_2_By_error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

def scrape_num_sampled(raw_name):
    name = normalize_name(raw_name)
    url = f"{BASE_URL}/{name}/samples/?role=1"
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'desktop': True,
            'mobile': False,
        }
    )
    
    try:
        response = scraper.get(url)
        if response.history:
            new_url = f"{response.url}samples/?role=1"
            response = scraper.get(new_url)

        if response.status_code != 200:
            logging.error(f"Failed to retrieve {name}: Status code {response.status_code} for url {response.url}")
            return (raw_name, 0)

        soup = BeautifulSoup(response.content, "html.parser")
        pattern = re.compile("^section-header-title$")
        numSampled = int(re.findall(r"\d+", soup.find("span", pattern).get_text(strip=True))[0])
        logging.info(f"Retrieved artist {name} from url {response.url}")
        return (raw_name, numSampled)

    except Exception as e:
        logging.error(f"Error processing {name}: {e}")
        return (raw_name, 0)
    
# Scrape all djs and save
all_djs = []

for name in NAMES:
    print(f"Scraping artist: {name}...")
    entry = scrape_num_sampled(name)
    all_djs.append(entry)
    time.sleep(random.uniform(15, 25)) 

# Write to CSV
with open("attempt_2_numSampledByDJs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["DJ Name", "Num Sampled By"])
    writer.writerows(all_djs)