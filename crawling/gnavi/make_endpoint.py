import re

import pandas as pd

# ログ関連など(個人用モジュール)
from my_modules import set_log

# logging
log_name: str = "make_endpoint"
log = set_log.Log(f"{log_name}", f"./log/{log_name}.text")
log.set_level(20)


def make_endpoint():
    """ ApiEndpoit 用のアドレスを生成する """

    # collect_url.py に取得した詳細ページの URLを読み込む
    df: pd.DataFrame = pd.read_csv("./csv/shop_urls.csv", encoding="utf-8")
    shop_urls = df.values.flatten().tolist()

    endpoints: list = []
    for shop_url in shop_urls:
        # 詳細ページの id から endpoint のアドレスを生成
        id: str = re.search(r"[^/]+?(?=/$)", shop_url).group()
        endpoint: str = f"https://r.gnavi.co.jp/api/v1/shops/{id}/reviews/tripadvisor/?appKey=34872a21d4505ecb9c84f044567aaec4"
        endpoints.append(endpoint)

    df = pd.DataFrame(endpoints)
    df.to_csv("./csv/endpoints.csv", index=False)


if __name__ == "__main__":
    make_endpoint()
    log.logger.info("[END]")
