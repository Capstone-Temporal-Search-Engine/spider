import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

startingSite = ''

file = open('webpage.csv', 'w')
urls = []
timeStamps = []
visitedUrls = []
urls.append(startingSite)
timeStamps.append(datetime.now())

while len(urls) != 0:
    currUrl = urls.pop()

    response = requests.get(currUrl)
    soup = BeautifulSoup(response.content, "html.parser")

    visitedUrls.append(currUrl)

    pageLinks = soup.select("a[href]")

    for link in pageLinks:
        url = link['href']
        if url not in visitedUrls:
            currTime = datetime.now()
            timeStamps.append(currTime)
            visitedUrls.append(url)

    time.sleep(random.uniform(1, 2))

i = 0
for url in visitedUrls:
    file.write(str(timeStamps[i]) + "," + url + "\n")
    i = i + 1