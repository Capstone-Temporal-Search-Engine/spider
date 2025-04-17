import scrapy
from bs4 import BeautifulSoup
import requests
import time
import random
import os
import csv
from io import BytesIO
from collections import defaultdict
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

class UArkSpider(scrapy.Spider):
    name = "UArkSpider"
    start_urls = ["https://www.amazon.com/"]
    visited_pages = set()
    page_rank = defaultdict(lambda: 1.0)
    link_graph = defaultdict(set)
    max_traversals = 10
    teleport_probability = 0.15
    
    csv_file = os.path.join(save_dir, "log.csv")
    os.makedirs(save_dir, exist_ok=True)
    
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "URL", "Title"])

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
        
        title = response.css("title::text").get()
        title = title.strip().replace(" ", "_") if title else f"page_{int(time.time())}"
        
        self.saveLocally(response.text, url, title)
        
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

    def teleport(self):
        unvisited_pages = [url for url in self.link_graph.keys() if url not in self.visited_pages]
        if unvisited_pages:
            teleport_url = random.choice(unvisited_pages)
            self.logger.info(f"Teleporting to: {teleport_url}")
            return scrapy.Request(teleport_url, callback=self.parse)

    def sanitizeFilename(title):
        return re.sub(r'[<>:"/\\|?*]', '', title)

    def saveLocally(self, content, url, title):
        title = UArkSpider.sanitizeFilename(title)
        filename = f"{title}.html"
        file_path = os.path.join(self.save_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([int(time.time()), url, title])
        
        self.logger.info(f"Saved {url} as {filename}")
