import scrapy
from bs4 import BeautifulSoup
import requests
import random
import csv
from collections import defaultdict
from io import StringIO
from datetime import datetime
import pytz

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

ENDPOINT_URL = "http://13.59.202.16/create-request"

class UArkSpider(scrapy.Spider):
    saved_metadata = dict()
    name = "UArkSpider"
    start_urls = ["https://www.amazon.com/"]
    visited_pages = set()
    page_rank = defaultdict(lambda: 1.0)
    link_graph = defaultdict(set)
    crawled_html = dict()
    max_traversals = 10
    teleport_probability = 0.15

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "CONCURRENT_REQUESTS_PER_IP": 8,
        "AUTOTHROTTLE_ENABLED": False,
        "USER_AGENT": random.choice(USER_AGENTS),
    }

    def parse(self, response):
        url = response.url
        if url in self.visited_pages:
            return
        self.visited_pages.add(url)
        self.logger.info(f"Crawled: {url}")

        self.crawled_html[url] = response.text

        soup = BeautifulSoup(response.text, "html.parser")
        out_links = set()
        for link in soup.select("a[href]"):
            href = link.get("href")
            if href.startswith("/"):
                full_url = response.urljoin(href)
                out_links.add(full_url)
                yield scrapy.Request(full_url, callback=self.parse)

        self.link_graph[url] = out_links
        self.update_pagerank()

        if random.random() < self.teleport_probability or len(self.visited_pages) % self.max_traversals == 0:
            yield self.teleport()

    def update_pagerank(self):
        damping_factor = 0.85
        new_page_rank = defaultdict(lambda: (1 - damping_factor))

        for page, out_links in self.link_graph.items():
            if not out_links:
                continue
            contribution = self.page_rank[page] / len(out_links)
            for linked_page in out_links:
                new_page_rank[linked_page] += damping_factor * contribution

        self.page_rank.update(new_page_rank)
        self.upload_data()

    def teleport(self):
        unvisited_pages = [url for url in self.link_graph.keys() if url not in self.visited_pages]
        if unvisited_pages:
            teleport_url = random.choice(unvisited_pages)
            self.logger.info(f"Teleporting to: {teleport_url}")
            return scrapy.Request(teleport_url, callback=self.parse)

    def upload_data(self):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["URL", "PageRank", "HTML File", "Timestamp (CST)"])
    
        files = {
            "pagerank": ("pagerank.csv", output, "text/csv")
        }
    
        central = pytz.timezone("US/Central")
    
        for i, (url, html) in enumerate(self.crawled_html.items()):
            now_cst = datetime.now(central).strftime("%H:%M:%S")
            filename = f"page_{i}.html"
    
            self.saved_metadata[url] = (filename, now_cst)
    
            rank = self.page_rank[url]
            writer.writerow([url, rank, filename, now_cst])
    
            files[f"page_{i}"] = (filename, html, "text/html")
    
        csv_data = output.getvalue()
        output.close()
    
        files["pagerank"] = ("pagerank.csv", csv_data, "text/csv")
    
        try:
            response = requests.post(ENDPOINT_URL, files=files)
            if response.status_code == 200:
                self.logger.info(f"Successfully uploaded data to {ENDPOINT_URL}")
            else:
                self.logger.error(f"Upload failed. Status: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Upload error: {e}")
    