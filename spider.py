import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import os
import re
import csv

startingSite = 'https://catalog.uark.edu/undergraduatecatalog/collegesandschools/collegeofengineering/electricalengineeringcomputerscience/'

os.makedirs('scrapedPages', exist_ok=True)
timestampFile = os.path.join('scrapedPages', 'scrapedPages.csv')

if not os.path.exists(timestampFile):
    with open(timestampFile, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["HTML", "Timestamp"])

urls = [startingSite]
visitedUrls = set()

while urls:
    currUrl = urls.pop(0)
    
    if currUrl in visitedUrls:
        continue
    
    try:
        response = requests.get(currUrl, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {currUrl}: {e} please note for further testing")
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")
    visitedUrls.add(currUrl)
    
    fileName = re.sub(r'[<>:"/\\|?*]', '_', currUrl.replace("https://", "")) + ".html"
    filePath = os.path.join("scrapedPages", fileName)

    with open(filePath, "w", encoding="utf-8") as file:
            file.write(response.text)

    with open(timestampFile, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([filePath, datetime.now().isoformat()])
        
    
    for link in soup.select("a[href]"):
        href = link.get("href")
        if href and href.startswith("/"):
            fullUrl = "https://catalog.uark.edu" + href
            if fullUrl not in visitedUrls and fullUrl not in urls:
                urls.append(fullUrl)
    
    time.sleep(random.uniform(1, 2)) 