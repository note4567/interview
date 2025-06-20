import re
from typing import Final

import pandas as pd
from my_modules import make_bs, set_log

# ログの設定
log = set_log.Log("collect_paging_url_Logging", "./log/collect_paging_url.text")
log.set_level(2)

TOP_URL: Final[str] = "https://r.gnavi.co.jp/area/jp/rs/"


def collect_city_urls() -> list:
    """市区町村用のURLを収集 (都道府県 → 市区町村)"""
    city_urls_list: list = []
    top_bs = make_bs.MakeBeautifulSoup(TOP_URL)
    prefectures_urls: list = top_bs.collect_urls('section[data-cy="related-area"] > ul > li > a')
    log.logger.info(f"[都道府県_URL] {len(prefectures_urls)}")

    for prefectures_url in top_bs.collect_urls('section[data-cy="related-area"] > ul > li > a'):
        prefectures_bs = make_bs.MakeBeautifulSoup(prefectures_url)
        urls: list = prefectures_bs.collect_urls('section[data-cy="related-area"] > ul > li > a')
        city_urls_list.extend(urls)

    log.logger.info(f"[市町村_URL] {len(prefectures_urls)}")

    return city_urls_list


def collect_paging_urls(city_urls: list) -> list:
    """ページング処理。ページ数分の URLを作成する"""
    paging_url_list: list = []
    for city_url in city_urls:
        # デフォルトのページ数を 1に設定
        last_index: str = "1"

        # ページがある場合はその最大ページ番号を取得
        city_bs = make_bs.MakeBeautifulSoup(city_url)
        last_index_page: str = city_bs.collect_url('ul.style_pages__MXEZp li a')
        if reg_match := re.search(r"(?<=p=)[0-9]+", last_index_page):
            last_index = reg_match.group()

        log.logger.info(f"[city_url] {city_url}")
        log.logger.info(f"[last_index] {last_index}")

        # ページ数分の URLを作成
        paging_urls: list = [f"{city_url}?p={str(index)}" for index in range(1, int(last_index) + 1)]
        paging_url_list.extend(paging_urls)

    return paging_url_list


if __name__ == "__main__":
    # 市区町村用の URLを取得する
    city_urls: list = collect_city_urls()

    # さらにページング用 URLを取得する
    paging_urls: list = collect_paging_urls(city_urls)

    # 重複削除(順序を保持)
    url_list = list(dict.fromkeys(paging_urls))

    # csv ファイルに保存する
    df = pd.DataFrame(url_list)
    df.to_csv("./csv/paging_url.csv", index=False)
