import requests
from bs4 import BeautifulSoup
import re
import csv

BASE_URL = "https://djmag.com"
YEARS = range(2004, 2025)

def scrape_top100_djs_by_year(year):
    url = f"{BASE_URL}/top100djs/{year}" if year != 2024 else f"{BASE_URL}/top100djs"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve {year}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Regex to match DJ href pattern
    pattern = re.compile(f"/top100djs/{year}/\\d+/.+")
    dj_entries = []

    for a in soup.find_all("a", href=pattern):
        name = a.get_text(strip=True)
        href_parts = a["href"].split("/")
        try:
            rank = int(href_parts[3])
        except (IndexError, ValueError):
            continue
        dj_entries.append((rank, name))
    # Sort by rank just in case
    return sorted(dj_entries, key=lambda x: x[0])

# Scrape all years and save
all_djs = []

for year in YEARS:
    print(f"Scraping {year}...")
    entries = scrape_top100_djs_by_year(year)
    for rank, name in entries:
        all_djs.append((year, rank, name))

# Write to CSV
with open("top100djs_by_year.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Year", "Rank", "DJ Name"])
    writer.writerows(all_djs)
