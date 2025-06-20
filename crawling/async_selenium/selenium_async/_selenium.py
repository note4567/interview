# Module: Asynchronous processing
# Copyright © 2022 Ryan Munro (munro)
# Released under the MIT license(https://opensource.org/license/mit)

# 2024: I modified it for Chrome. Also,Change in driver termination process

import atexit
import re
import weakref
from typing import Any, Literal

import fake_useragent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as WebDriverBase
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class WebDriver(WebDriverBase):
    running: bool

    def get_blank(self):
        raise NotImplementedError


class WebdriverMixin(WebDriver, object):
    running: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def _atexit():
            self.quit()

        def _finalizer(_driver: WebDriver):
            if _driver:
                _driver.quit()
                print("[driver] quit()")

        self.__atexit__ = atexit.register(_atexit)
        self._finalizer = weakref.finalize(self, _finalizer, self)


# Chrome
class CustomDriver(WebdriverMixin, WebDriver, webdriver.Chrome):
    def __init__(self, options: Options | None) -> None:
        # Default options
        if not type(options) == "selenium.webdriver.chrome.options.Options":
            print("[driver] set_option")
            options = Options()
            options.add_argument("--headless=new")
            fake_ua = fake_useragent.UserAgent()
            options.add_argument(f"user-agent={fake_ua.random}")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--blink-settings=imagesEnabled=true")
            options.add_argument("--proxy-server=http://localhost:xxxxx")
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
        super().__init__(options=options)
        self.implicitly_wait(2)

    def get_blank(self):
        self.get("about:blank")

    def page_open(self, url: str) -> None:
        """Open the specified URL in a new tab"""
        self.execute_script(f"window.open('{url}')")
        self.switch_to.window(self.window_handles[-1])

    def page_close(self) -> None:
        self.close()
        self.switch_to.window(self.window_handles[-1])

    def wait_driver(self, path: str) -> None:
        """Driver Waiting"""
        wait = WebDriverWait(self, 15)
        wait.until(expected_conditions.presence_of_element_located((By.XPATH, path)))

    def get_text(self, path: str, obj=None) -> str | None | Any:
        """Returns the text of only the first element"""
        if not obj:
            obj = self
        elements = obj.find_elements(By.XPATH, path)
        return elements[0].get_attribute("textContent") if elements else ""

    def get_text_all(self, path: str, obj=None) -> Any | Literal[""]:
        """Returns the text of all elements"""
        if not obj:
            obj = self
        elements = obj.driver.find_elements(By.XPATH, path)
        text = ""
        for element in elements:
            text += element.get_attribute("textContent")
        return text

    def get_reg(self, reg: str, st: str) -> str:
        """Get items by regular expression"""
        if match_reg := re.search(reg, st):
            return match_reg.group()
        else:
            return ""
