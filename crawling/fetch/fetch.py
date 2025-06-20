import datetime
import json
import os
import sys
from time import sleep
from typing import List

import pytz
import selenium_driver

# your module ...
import db
import tocsv

# 取得項目名
item_name: List[str] = [
    "都道府県名",
    "都市名",
    "地区名",
    "採択年度",
    "種別",   
    "緯度",
    "経度",
    "URL",
]


# fetch リクエストの送信
def api_fetch(driver, endpoint) -> dict:
    script = """return fetch(arguments[0])
    .then(response => response.json())
    .then(data => {
        return data;
    });"""
    # fetch の実行
    return driver.execute_script(script, endpoint)


def get_item(table_name) -> None:
    top_url = "https://www.uraja.or.jp/map/"
    driver = selenium_driver.CustomDriver()

    # DB
    db_handler = db.Operator(table_name)

    try:
        # top へアクセス
        driver.get(top_url)
        sleep(5)

        # APIエンドポイントへのリクエスト
        api_endpoint = "https://www.uraja.or.jp/map-content/api/get_data.php"
        api_data: dict = api_fetch(driver, api_endpoint)

        # アイテムの取得
        for item in api_data["data"]:
            data: dict[str, str] = {k: "" for k in item_name}
            data["都道府県名"] = item["pref"]
            data["都市名"] = item["city"]
            data["地区名"] = item["area"]
            data["採択年度"] = item["saitaku-nen"]
            data["種別"] = item["syubetsu"]           
            data["緯度"] = item["latitude"]
            data["経度"] = item["longitude"]

            data["URL"] = driver.current_url

            # DB
            print(json.dumps(data, indent=4, ensure_ascii=False))
            db_handler.insert(data)

    except Exception as e:
        print(e)
    finally:
        driver.quit()
        del db_handler


if __name__ == "__main__":
    today: str = datetime.datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y_%m_%d")
    table_name: str = f"name_{today}"
    get_item(table_name)
    
    # CSV ....
    
