""" Asynchronous processing of selenium (Google Chrome) """

# Execution environment: Python 3.9 or higher

import asyncio
import itertools
import json
from time import sleep

import fake_useragent
import pandas as pd
from selenium.webdriver.chrome.options import Options

# Module: Classes that handle items
import item

# Module: Asynchronous processing
# Copyright © 2022 Ryan Munro (munro)
# Released under the MIT license(https://opensource.org/license/mit)
# 2024: I modified it for Chrome. Also,Change in driver termination process
import selenium_async
from selenium_async.core import run_sync


def get_urls() -> list:
    # Import URLs from a CSV file
    df: pd.DataFrame = pd.read_csv("url.csv", encoding="utf-8")
    urls = list(itertools.chain.from_iterable(df.values.tolist()))

    return urls


def get_item(driver: selenium_async, url: str):
    # Access
    driver.get(url)

    # Waiting process
    sleep(2)
    driver.wait_driver('//h1[@class="hdg-lv1"]')

    # Acquiring items
    data = items.data_init()
    data["社名"] = driver.get_text('//h1[@class="hdg-lv1"]').strip()
    data["URL"] = driver.current_url

    # debug
    print(json.dumps(data, indent=4, ensure_ascii=False))

    return data


async def fetch_data(options: Options | None) -> list:
    urls: list = get_urls()

    # Retrieving items asynchronously
    scraping_results: list = await asyncio.gather(
        *[run_sync(get_item, url, options) for url in urls]
    )

    return scraping_results


async def set_option() -> Options:
    """chrome driver options"""
    options = Options()
    options.add_argument("--headless=new")
    fake_ua = fake_useragent.UserAgent()
    options.add_argument(f"user-agent={fake_ua.random}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--blink-settings=imagesEnabled=true")
    options.add_argument("--proxy-server=http://localhost:xxxxxxx")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--blink-settings=imagesEnabled=true")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=ja")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--incognito")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    return options


async def main() -> list:
    """Set options and start asynchronous processing"""
    # options = None: If None, the default option
    options: Options = await set_option()
    results: list = await fetch_data(options)

    return results


if __name__ == "__main__":
    items: item.Items = item.Items()
    data_list: list = asyncio.run(main())

    # Using data_list with CSV or DB ....
