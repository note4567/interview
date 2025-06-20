import asyncio
import csv
import re
from itertools import chain
from typing import Any

import fake_useragent
import lxml.html
import pandas as pd
from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession, SQLiteBackend

# ログ関連など(個人用モジュール)
from my_modules import count_items, set_log

# async _retry
from tenacity import retry, stop_after_attempt, wait_fixed

# tor を用いる場合
# from aiohttp_socks import ProxyConnector

# logging
log_name: str = "collect_url"
log = set_log.Log(f"{log_name}", f"./log/{log_name}.text")
log.set_level(2)


class AsyncCacheClient:
    def __init__(
        self,
        cache_name: str = "http_cache.sqlite",
        allowed_codes: tuple = (200,),
        max_concurrent: int = 1,
    ) -> None:

        # asyncキャッシュ
        self.cache_name = cache_name
        self.allowed_codes = allowed_codes

        # ノンブロッキング処理数
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # 取得したアイテムを数える
        self.counter: Any = count_items.CountItem().counter_item()

    async def get_cached_session(self) -> CachedSession:
        """キャッシュ付きセッションを作成"""
        cache = SQLiteBackend(
            cache_name=self.cache_name,
            allowed_codes=self.allowed_codes,
            # キャッシュの期限
            # expire_after=self.expire_after,
            # tor用
            # connector=connector,
        )

        return CachedSession(cache=cache)

    async def get_session(self) -> ClientSession:
        """キャッシュを利用せずに通常のセッションを作成"""
        return ClientSession()

    async def get_text(self, tree, path):
        elements = tree.xpath(path)
        return elements[0] if elements else ""

    @retry(wait=wait_fixed(5), stop=stop_after_attempt(15))
    async def fetch(
        self,
        url: str,
        verify_ssl: bool = False,
    ) -> list:

        # ヘッダー等の設定
        fake_ua = fake_useragent.UserAgent()
        headers = {
            "User-Agent": fake_ua.random,
            "accept-language": "ja,en-US;q=0.9,en;q=0.8",
            "Proxy-connection": "Keep-alive",
        }

        proxy = "http://127.0.0.1:55555"

        # SOCKS5プロキシを使うためのProxyConnector
        # connector = ProxyConnector.from_url(proxy)

        async with self.semaphore:
            try:
                log.logger.info(url)
                # tor 場合
                # async with await self.get_cached_session(connector=connector) as session:
                # cahce を使う場合
                # async with await self.get_cached_session() as _session:
                async with await self.get_session() as _session:
                    async with _session.get(
                        url,
                        timeout=30,
                        headers=headers,
                        proxy=proxy,
                        verify_ssl=verify_ssl,
                    ) as resp:

                        log.logger.info(f"{resp.status = }")
                        if 404 == resp.status:
                            log.logger.error(f"[404] {resp.status = }")
                            return
                        if 200 != resp.status:
                            log.logger.error(f"[Error] {resp.status = }")
                            raise

                        content = await resp.text()

                        if not content:
                            log.logger.error("Nothing content")
                            raise

                        tree = lxml.html.fromstring(content)
                        temp_shop_urls = tree.xpath(
                            '//div[@data-cy="results"]//a[@class="style_titleLink___TtTO"]/@href'
                        )
                        shop_urls = list(filter(lambda x: not re.search(r"\?", x), temp_shop_urls))

                        log.logger.debug(f"[urls 件数] {len(shop_urls) = }")

                        # counterを安全に更新するためのロック
                        async with asyncio.Lock():
                            log.logger.info(self.counter())

                        return shop_urls

            except Exception as e:
                log.logger.error(f"Error fetching {url}: {str(e)}")
                raise

    async def fetch_multiple(self, urls: list, **kwargs):
        # 上限の設定(2重の防止策)
        if len(urls) > 700:
            log.logger.error("too many")
            return

        tasks = [self.fetch(url, **kwargs) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def append_urls_to_csv(urls: list):
    """詳細ページの URLをファイルに書き出す(追記実行)"""
    with open("./csv/shop_urls.csv", mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for url in urls:
            writer.writerow([url])


async def start_async() -> list:
    """詳細ページの URLを取得する"""
    # クライアントのインスタンス化
    client = AsyncCacheClient(cache_name="./temp.sqlite", max_concurrent=10)
    # CSVの読み込み(事前に collect_paging_url.py で取得した一覧ページを取得)
    df: pd.DataFrame = pd.read_csv("./csv/paging_url.csv", encoding="utf-8")

    # DataFrameをリストに変換
    paging_urls = df.values.flatten().tolist()
    log.logger.info(f"件数: {len(paging_urls)}")
    log.logger.debug(paging_urls[:10])

    # 10件毎にタスクを登録
    start = 0
    end: int = len(paging_urls)
    step = 10
    for i in range(start, end, step):
        chunk: list = paging_urls[i : i + step]
        log.logger.info(f"分割: {len(chunk)}")
        try:
            # 詳細ページの URLを取得する
            url_list = await client.fetch_multiple(chunk)

            # None を弾く
            url_list = list(filter(None, url_list))

            # ファイルに書き出す(取得した URLを持ちすぎないで、定期的に書き出す。メモリの消費を防止する)
            log.logger.info(f"[write] {i}")
            shop_urls = list(chain.from_iterable(url_list))
            await append_urls_to_csv(shop_urls)
        except Exception:
            log.logger.error(f"[Error] {i} : {chunk}")
            log.logger.error(url_list[:10])


if __name__ == "__main__":
    # 詳細ページの URLを取得する
    asyncio.run(start_async())
    log.logger.info("[END]")
