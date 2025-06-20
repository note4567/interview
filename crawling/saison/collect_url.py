import os
import sys
from time import sleep
from typing import Any, Final, List

import pandas as pd
from retry import retry

CSV_PATH: Final[str] = "./csv"
MY_MODULES_PATH: Final[str] = "./my_modules"
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), MY_MODULES_PATH))

import count_items
import define_item_category
import selenium_driver


@retry(tries=5, delay=1)
def ajax(driver, **kwargs) -> dict:
    # ajax スクリプトの定義
    # f文字列中に波括弧{}を使用する為 { を2重にする
    script: str = f"""
    let parameter = {{
        'transactionid':'{kwargs['transactionid']}',
        'limit':90,
        'orderby':1,
        'pageno':{kwargs['page_no']},
        'name':'',
        'donation_id':[0],
        'donation_range':[0],
        'tag':'',
        'temperature_zone':'',
        'category_all':{kwargs['category_all']},
        'sub_category':{kwargs['sub_category']},
        'municipally':'',
        'area':'',
        'pref':'',
    }}

    return $.ajax({{
        type: "POST",
        url:  "/ajax/get_products_list.php",
        data: parameter,
        dataType: "json",
    }})
        .done(data =>{{
            return data;
        }})
        .fail(data =>{{
            return data;
        }});"""

    return driver.execute_script(script)


def csv_write(url_list, category_no, sub_category_no) -> None:
    # サブカテゴリー毎に csvファイルに保存する
    url_list = list(set(url_list))

    df = pd.DataFrame(url_list)
    df.to_csv(f"{CSV_PATH}/shop_url_{category_no}_{sub_category_no}.csv", index=False)


def collect_url() -> None:
    TOP_URL: Final[str] = "https://furusato.saisoncard.co.jp/"
    # アイテムカテゴリーを取得する
    item_categorys: List = define_item_category.ItemCategory().item_categorys
    # リクエストの ID
    transactionid = "37e4181032976325928df9248da0f8567d97c930"

    try:
        # Selenium 起動
        driver: selenium_driver.CustomDriver = selenium_driver.CustomDriver()
        driver.get(TOP_URL)
        sleep(5)

        # サブカテゴリー毎に取得する
        for item_category in item_categorys:
            for sub_category in item_category["sub_category"]:
                # カテゴリー毎の url を格納して、これをカテゴリー毎の csvファイルに保存する
                url_list: List = []
                # ページングの停止条件(同じデータである場合は whileループを抜ける)
                before_result: str = ""
                # page を数える
                page_counter: Any = count_items.CountItem().counter_item()

                # リクエストを送る(ajax 形式)
                while True:
                    results: dict = ajax(
                        driver,
                        page_no=page_counter(),
                        transactionid=transactionid,
                        category_all=item_category["category_all"],
                        sub_category=[sub_category],
                    )
                    url_list.extend([TOP_URL + result["detail_path"] for result in results["list"]])

                    # [ページングの停止条件 その1] 存在しないページの場合 result["list"] は空になる
                    if not results["list"]:
                        break

                    # [ページングの停止条件 その2] 同じデータを繰り返す場合
                    if before_result == results["list"][0]["detail_path"]:
                        break

                    # ここで現在の値を代入して、次のループでの判定処理に用いる
                    before_result = results["list"][0]["detail_path"]

                # サブカテゴリー毎の url一覧を csvに書き出す
                csv_write(url_list, item_category["category_all"][0], sub_category)
    except Exception as e:
        print(e)
    finally:
        del driver


if __name__ == "__main__":
    # url一覧を収集する
    collect_url()
