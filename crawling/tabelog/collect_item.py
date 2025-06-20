import asyncio
import datetime
import json
import re
from typing import Any

import fake_useragent
import lxml.html
import pandas as pd
from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession, SQLiteBackend
from my_modules import count_items, set_log

# Execute the table creation process
from my_modules.database import engine, session
from my_modules.models import DbSpotModel

# async _retry
from tenacity import retry, stop_after_attempt, wait_fixed

# tor を用いる場合
# from aiohttp_socks import ProxyConnector  # type: ignore

# logging
log_name: str = "collect_item"
log = set_log.Log(f"{log_name}", f"./log/{log_name}.text")
log.set_level(20)


class AsyncCacheClient:
    def __init__(
        self,
        cache_name: str = "http_cache.sqlite",
        allowed_codes: tuple = (200,),
        max_concurrent: int = 7,
    ) -> None:

        # asyncキャッシュ
        self.cache_name = cache_name
        self.allowed_codes = allowed_codes

        # ノンブロッキング処理数
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # 取得したアイテムを数える
        self.counter: Any = count_items.CountItem().counter_item()

        # カラム名の取得(クロールしたデータを詰める際の初期化処理で使う)
        column_names: list = [column.name for column in DbSpotModel.__table__.columns]
        self.columns = list(filter(lambda x: not re.search("id|created_at|updated_at", x), column_names))

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

    async def get_text_all(self, tree, path, sep=""):
        elements = tree.xpath(path)
        if sep == "/":
            text: str = "".join([ele + "/" for ele in elements])[:-1]
            text = re.sub(r"\s+", "", text)
            return text

        if sep == "blank":
            text: str = "".join([ele + " " for ele in elements])[:-1]
            text = re.sub(r"\s+", " ", text)
            return text

        text: str = sep.join([ele for ele in elements])
        text = re.sub(r"\s+", "", text)
        return text

    @retry(wait=wait_fixed(0.2), stop=stop_after_attempt(60))
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

        proxy = "http://127.0.0.1:xxxxxxx"

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
                            log.logger.error(f"{resp.status = }")
                            raise

                        content = await resp.text()

                        if not content:
                            log.logger.error("Nothing content")
                            raise

                        tree = lxml.html.fromstring(content)

                        # 取得するデータ項目の初期化・設定
                        data = {k: "" for k in self.columns}

                        # 1
                        data["URL"] = str(resp.url)
                        # 2
                        official: str = await self.get_text(tree, "//p[@class='owner-badge__icon']//text()")
                        data["公式_非公式"] = "公式" if official else "非公式"
                        # 3
                        reserve: str = await self.get_text(tree, "//h3[@class='rstdtl-side-yoyaku__booking-title']//text()")
                        data["ネット予約可否"] = "可" if reserve else "不可"
                        # 4
                        data["店名"] = await self.get_text(tree, "//th[contains(text(),'店名')]/following-sibling::td//span//text()")
                        # 5
                        temp_old_name: str = await self.get_text(tree, "//span[contains(text(),'旧店名')]//text()")
                        reg_result = re.search(r"(?<=【旧店名】).+(?=）)", temp_old_name)
                        data["旧店名"] = reg_result.group() if reg_result else ""
                        # 6
                        data["最寄り駅"] = await self.get_text(tree, "//dt[contains(text(),'最寄り駅')]/following-sibling::dd//span//text()")
                        # 7
                        data["ジャンル"] = await self.get_text(tree, "//th[contains(text(),'ジャンル')]/following-sibling::td//span//text()")
                        # 8
                        data["予約_お問合せ"] = await self.get_text_all(tree, "//th[contains(normalize-space(.), 'お問い合わせ')]//following-sibling::td//text()")
                        
                        # ... Omit ...

                        # 54
                        data["ユーザーの評価平均_分布_雰囲気"] = await self.get_text(tree, "//dt[contains(text(),'雰囲気')]/following-sibling::dd//text()")
                        # 55
                        data["ユーザーの評価平均_分布_酒_ドリンク"] = await self.get_text(tree, "//dt[contains(text(),'酒・ドリンク')]/following-sibling::dd//text()")
                        # 56
                        data["ユーザーの評価平均_分布_コストパフォーマンス"] = await self.get_text(tree, "//dt[contains(text(),'コストパフォーマンス')]/following-sibling::dd//text()")

                        async with asyncio.Lock():
                            log.logger.info(self.counter())
                            log.logger.debug(f"[{self.counter()}] \n {json.dumps(data, indent=4, ensure_ascii=False)}")

                        return data

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


async def start_async() -> list:
    # クライアントのインスタンス化
    client = AsyncCacheClient(cache_name="./cache/taberog.sqlite", max_concurrent=10)
    # CSVの読み込み
    df: pd.DataFrame = pd.read_csv("./csv/url.csv", header=None)

    # DataFrameをリストに変換
    url_list = df.values.flatten().tolist()
    url_list = list(set(url_list))
    url_list.sort()
    log.logger.info(f"件数: {len(url_list)}")

    try:
        # [アイテムの取得]
        # task の登録を 70個程度にして上限を設定して実行
        start = 0
        end: int = len(url_list)
        step = 70
        for i in range(start, end, step):
            chunk: list = url_list[i : i + step]
            log.logger.info(f"分割: {len(chunk)}")
            data_list = await client.fetch_multiple(chunk)

            # None を弾く
            data_list = list(filter(None, data_list))

            try:
                session.bulk_insert_mappings(DbSpotModel, data_list)
                session.commit()
                log.logger.info(f"[DB OK]: {len(data_list)}")
            except Exception:
                # 重複データをエラーにする
                log.logger.error(f"[Error] {i} : {chunk[:10]}")
                session.rollback()

        # [csv]
        # SQLクエリを実行して DataFrame に変換
        table_name = DbSpotModel.__table__.name
        sql: str = f"SELECT * FROM {table_name}"
        df: pd.DataFrame = pd.read_sql(sql, con=session.bind)

        # 不要なカラムを除外
        column_names: list = [column.name for column in DbSpotModel.__table__.columns]
        columns = list(filter(lambda x: not re.search("id|created_at|updated_at", x), column_names))
        df.sort_values(by="URL", ascending=True, inplace=True)

        # csv に出力
        df.to_csv(f"./csv/{table_name}.csv", columns=columns, index=False)
    except Exception:
        log.logger.error(f"[Error] {i} : {chunk[:10]}")
        log.logger.error(data_list[:10])
        session.rollback()
    finally:
        session.close()
        engine.dispose()
        log.logger.info("[Close]")


if __name__ == "__main__":
    asyncio.run(start_async())
    log.logger.info("[END]")
