import atexit
import itertools
import json
import re
from typing import Any, List

import count_items
import pandas as pd
import scrapy
import set_log

# Execute the table creation process
from database import engine, session
from models import DbSpotModel

# ログの設定
path = "../../.."
log_name: str = "collect_item"
log = set_log.Log(f"{log_name}", f"{path}/log/{log_name}.text")
log.set_level(20)


class GnaviSpider(scrapy.Spider):
    name = "gnavi"
    allowed_domains = ["r.gnavi.co.jp"]

    # 取得したアイテムを数える
    counter: Any = count_items.CountItem().counter_item()

    # 詳細ページの URLを取得する
    df: pd.DataFrame = pd.read_csv(f"{path}/csv/endpoints.csv", encoding="utf-8")

    start_urls = list(itertools.chain.from_iterable(df.values.tolist()))
    start_urls.sort()
    log.logger.info(f"Start {len(start_urls)}")

    # カラム名の取得(クロールしたデータを詰める際の初期化処理で使う)
    column_names: list = [column.name for column in DbSpotModel.__table__.columns]
    columns = list(
        filter(lambda x: not re.search("id|created_at|updated_at", x), column_names)
    )

    def parse(self, response):
        # Apiendpoint リクエスト
        json_data = json.loads(response.text)

        value: dict = {
            "rating": json_data["rating"],
            "numReviews": json_data["numReviews"],
        }

        # endpoint のアドレスから詳細ページの URLを生成する
        id: str = re.search(r"[^/]+(?=/reviews)", response.url).group()
        shop_url: str = f"https://r.gnavi.co.jp/{id}/"

        return response.follow(
            shop_url, callback=self.parse_html, meta={"value": value}
        )

    def cleansing_text(self, text: str, reg=None) -> str:
        text = re.sub(r"\s+", "", text)
        if reg:
            text = re.sub(reg, "", text)

        return text.strip()

    def cleansing_texts(self, texts: list) -> str:
        text = " ".join(texts)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def parse_html(self, response, **kwargs):
        # 取得するデータ項目の初期化・設定
        data = {k: "" for k in self.columns}

        # 1
        data["URL"] = response.url
        # 2
        data["店名"] = response.xpath('//p[@id="info-name"]/text()').get(default="")
        # 3
        data["電話番号"] = response.xpath('//span[@class="number"]/text()').get(
            default=""
        )
        # 4
        data["FAX"] = response.xpath('//ul[@id="info-fax"]//span//text()').get(
            default=""
        )
        # 5
        text = response.xpath('//p[@class="adr slink"]/text()').get(default="")
        data["郵便番号"] = self.cleansing_text(text, r"〒")
        # 6
        texts: list = response.xpath(
            '//span[@class="region" or @class="locality"]//text()'
        ).getall()
        data["住所"] = self.cleansing_texts(texts)
        # 7

        # ...  Omit ...

        # 29
        texts: list = response.xpath(
            '//th[contains(text(),"お店のウリ")]//following-sibling::td//li//text()'
        ).getall()
        data["お店のウリ"] = self.cleansing_texts(texts)

        # meta から値を取り出す
        # 30
        data["評価"] = response.meta["value"]["rating"]
        # 31
        data["口コミ数"] = response.meta["value"]["numReviews"]

        # DB
        try:
            # データの挿入
            new_data = DbSpotModel(**data)
            session.add(new_data)
            session.commit()
        except Exception:
            # 重複データはエラーになる
            log.logger.error(f"[Error]: {response.url}")
            session.rollback()

        log.logger.debug(
            f"[{self.counter()}] \n {json.dumps(data, indent=4, ensure_ascii=False)}"
        )


@atexit.register
def end():
    """
    プログラムの最後に呼ばれる
     csv ファイルに書き出す
    """
    try:
        # [csv]
        # SQLクエリを実行して DataFrame に変換
        table_name = DbSpotModel.__table__.name
        sql: str = f"SELECT * FROM {table_name}"
        df: pd.DataFrame = pd.read_sql(sql, con=session.bind)

        # 不要なカラムを除外
        column_names: list = [column.name for column in DbSpotModel.__table__.columns]
        columns = list(
            filter(lambda x: not re.search("id|created_at|updated_at", x), column_names)
        )
        df.sort_values(by="URL", ascending=True, inplace=True)

        # csv に出力
        df.to_csv(f"{path}/csv/{table_name}.csv", columns=columns, index=False)
    except Exception:
        log.logger.error("[Error]")
    finally:
        # セッションのクローズ
        session.close()
        engine.dispose()
        log.logger.info("[Close]")

    log.logger.info("[END]")
