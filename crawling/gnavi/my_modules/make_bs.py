from urllib.parse import urljoin

import fake_useragent
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from retry import retry


class MakeBeautifulSoup:
    @retry(tries=50, delay=0.3)
    def __init__(self, url: str, message=""):
        print(f"Making BeautifulSoup ... {message}")
        proxies = {"http": "http://127.0.0.1:xxxxxx", "https": "http://127.0.0.1:xxxxx"}
        fake_ua = fake_useragent.UserAgent()
        headers = {"User-Agent": fake_ua.random}
        response = requests.get(url, timeout=10, headers=headers, proxies=proxies)
        self.status_code = response.status_code
        self.soup = BeautifulSoup(
            response.content, "html.parser", from_encoding="utf-8"
        )
        self.url: str = response.url

    def collect_urls(self, path: str, bs: BeautifulSoup = None) -> list:
        urls: list = []
        bs = bs if bs else self
        for url_element in bs.soup.select(path):
            urls.append(urljoin(bs.url, url_element.get("href")))

        return urls

    def collect_url(self, path: str, obj: BeautifulSoup = None, index=-1) -> str:
        obj = obj if obj else self.soup
        elements: ResultSet[Tag] = obj.select(path)
        url: str = elements[index].get("href") if elements else ""

        return urljoin(self.url, url)

    def get_text(self, path: str, obj: BeautifulSoup = None) -> str:
        # 最初の要素だけテキストを返す
        obj = obj if obj else self.soup
        elements = obj.select(path)
        return elements[0].get_text(strip=True) if elements else ""

    def get_text_all(self, path: str, obj: BeautifulSoup = None) -> list:
        # 全てのテキストを返す
        obj = obj if obj else self.soup
        elements = obj.select(path)
        text: str = " ".join([ele.get_text(strip=True) for ele in elements])
        # return elements
        return text

    def get_content(self, path: str, obj: BeautifulSoup = None) -> str:
        # 最初の要素だけを返す
        obj = obj if obj else self.soup
        elements = obj.select(path)
        return elements[0].contents[0] if elements else ""

    def get_content_all(self, path: str, obj: BeautifulSoup = None) -> str:
        # 全ての要素を返す
        obj = obj if obj else self.soup
        elements = obj.select(path)

        return elements[0].contents

    def get_href(self, path: str, obj: BeautifulSoup = None) -> str:
        # 最初の要素だけテキストを返す
        obj = obj if obj else self.soup
        elements = obj.select(path)
        return elements[0].get("href") if elements else ""
