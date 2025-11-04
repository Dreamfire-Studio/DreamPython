from typing import Optional, List, Dict
import requests
from bs4 import BeautifulSoup, ResultSet, Tag

class BeautifulSoupController:
    def __init__(self, *, user_agent: str = "Mozilla/5.0 (compatible; DreamfireBot/1.0)") -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def fetch_html(self, url: str, *, timeout: int = 10) -> Optional[str]:
        try:
            r = self.session.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"[BeautifulSoupController] Failed to fetch {url}: {e}")
            return None

    def parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def fetch_html_and_parse(self, url: str, *, timeout: int = 10) -> Optional[BeautifulSoup]:
        html = self.fetch_html(url, timeout=timeout)
        if html is None:
            return None
        return self.parse(html)

    def find_all(self, soup: BeautifulSoup, tag: str, *, class_name: Optional[str] = None, attrs: Optional[dict] = None) -> ResultSet[Tag]:
        if class_name:
            return soup.find_all(tag, class_=class_name)
        if attrs:
            return soup.find_all(tag, attrs=attrs)
        return soup.find_all(tag)

    def extract_links(self, soup: BeautifulSoup, *, tag: str = "a", class_name: Optional[str] = None, base_url: str = "") -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        for a in self.find_all(soup, tag, class_name=class_name):
            href = a.get("href")
            if not href:
                continue
            title = a.get_text(strip=True)
            if base_url and not href.startswith("http"):
                href = f"{base_url}{href}"
            results.append({"title": title, "url": href})
        return results