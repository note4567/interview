# Module: Asynchronous processing
# Copyright © 2022 Ryan Munro (munro)
# Released under the MIT license(https://opensource.org/license/mit)

# 2024: Modified for Chrome

import asyncio
import random
from asyncio import AbstractEventLoop
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, TypeVar

from selenium.webdriver.chrome.options import Options

from selenium_async._selenium import CustomDriver, WebDriver
from selenium_async.pool import Pool, default_pool

T = TypeVar("T")


async def run_sync(
    func: Callable[[WebDriver], T],
    url: Any,
    options: Options | None,
    *,
    loop: Optional[AbstractEventLoop] = None,
    pool: Optional[Pool] = None,
) -> T:
    if loop is None:
        loop = asyncio.get_event_loop()
    if pool is None:
        pool = default_pool()

    async with use_browser(url, options=options, pool=pool) as driver:
        # Add url
        return await asyncio.to_thread(func, driver, url)


@asynccontextmanager
async def use_browser(
    url: Any,
    options: Optional[Options] = None,
    *,
    pool: Optional[Pool] = None,
):
    if pool is None:
        pool = default_pool()
    if options is None:
        options = Options()

    # Get the lock: acquire()
    await pool.semaphore.acquire()
    try:
        if options in pool.resources:
            # If the max_size specified in the Pool class is exceeded, the driver will be reused.
            driver = pool.resources[options].pop()
            if len(pool.resources[options]) == 0:
                del pool.resources[options]
        else:
            # close webdrivers if there are too many in the pool that
            # don't match our desired options
            too_many = len(pool) - (pool.max_size - 1)
            if too_many > 0:
                weighted_keys = [
                    k for k, v in pool.resources.items() for _ in range(len(v))
                ]
                random.shuffle(weighted_keys)
                remove_keys = weighted_keys[0:too_many]
                drivers: list[WebDriver] = []
                for key in remove_keys:
                    drivers.append(pool.resources[key].pop())
                    if len(pool.resources[key]) == 0:
                        del pool.resources[key]

                def _close_drivers():
                    for driver in drivers:
                        driver.quit()

                await asyncio.to_thread(_close_drivers)

            # create new driver
            driver = await launch(options)

        try:
            yield driver
            if pool.blank_page_after_use:
                driver.get_blank()

            # if successfully finishes, add driver back to pool
            if options not in pool.resources:
                pool.resources[options] = []
            pool.resources[options].append(driver)

        except:
            # if error, don't return driver back to pool
            try:
                driver.quit()
            except:
                pass
            raise
    finally:
        # Release the lock
        pool.semaphore.release()


async def launch(options: Optional[Options] = None) -> WebDriver:
    return await asyncio.to_thread(lambda: launch_sync(options))


def launch_sync(options: Optional[Options] = None) -> WebDriver:
    # Passing options
    driver = CustomDriver(options)
    return driver
