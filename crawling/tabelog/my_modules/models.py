from datetime import datetime

import pytz
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import declarative_base

from . import set_log
from .database import engine

log = set_log.Log("models_Logging", "./log/models_log.text")
log.set_level(2)

Base = declarative_base()

# テーブル名設定
today: str = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y_%m_%d")
table_name: str = f"name_{today}"


# 日本時間を取得する関数
def get_jp_time():
    return datetime.now(pytz.timezone("Asia/Tokyo"))


# モデルの定義
class DbSpotModel(Base):
    __tablename__: str = table_name
    log.logger.info(f"[models]: {__tablename__ = }")

    # IDカラムを主キーとして定義
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 処理時間のカラム
    jp_time: datetime = datetime.now(pytz.timezone("Asia/Tokyo"))

    created_at = Column(DateTime, default=get_jp_time, nullable=False)
    updated_at = Column(DateTime, default=get_jp_time, onupdate=get_jp_time, nullable=False)

    # カラム名の設定
    # 4
    店名 = Column(String(150))
    # 1
    URL = Column(Text)
    # 2
    公式_非公式 = Column(Text)
    # 3
    ネット予約可否 = Column(String(10))
    # 5
    旧店名 = Column(Text)
    # 6
    最寄り駅 = Column(String(50))
    # 7
    ジャンル = Column(Text)
    # 8
    予約_お問合せ = Column(Text)
    # 9
    電話番号 = Column(String(20))
    # 10
    予約可否 = Column(Text)
    # 11
    住所 = Column(String(250))
    # 12
    交通手段 = Column(Text)
    # 13
    営業時間_定休日 = Column(Text)
    # 14
    予算 = Column(Text)
    # 15
    予算_口コミ = Column(Text)
    # 16
    支払方法 = Column(Text)
    # 17
    領収書_適格簡易請求書 = Column(Text)
    # 18
    サービス料_チャージ = Column(Text)
    # 19
    席数 = Column(Text)
    # 20
    最大予約可能人数 = Column(Text)
    # 21
    個室 = Column(Text)
    # 22
    禁煙_喫煙 = Column(Text)
    # 23
    貸切 = Column(Text)
    # 24
    駐車場 = Column(Text)
    # 25
    空間_設備 = Column(Text)
    # 26
    ドリンク = Column(Text)
    # 27
    料理 = Column(Text)
    # 28
    携帯電話 = Column(Text)
    # 29
    利用シーン = Column(Text)
    # 30
    ロケーション = Column(Text)
    # 31
    サービス = Column(Text)
    # 32
    お子様連れ = Column(Text)
    # 33
    ホームページ = Column(Text)
    # 34
    公式アカウント = Column(Text)
    # 35
    備考 = Column(Text)
    # 36
    オープン日 = Column(Text)
    # 37
    チェーン名 = Column(Text)
    # 38
    初投稿者 = Column(Text)
    # 39
    最近の編集者 = Column(Text)
    # 40
    閉店タグ = Column(Text)
    # 41
    掲載保留タグ = Column(String(10))
    # 42
    移転タグ = Column(String(10))
    # 43
    業態変更タグ = Column(String(10))
    # 44
    評価 = Column(String(10))
    # 45
    口コミ数 = Column(Text)
    # 46
    保存数 = Column(Text)
    # 47
    受賞_選出歴 = Column(Text)
    # 48
    感染症対策 = Column(Text)
    # 49
    移転後店舗URL = Column(Text)
    # 50
    取得日 = Column(Text)
    # 51
    ユーザーの評価平均_分布_総合 = Column(String(10))
    # 52
    ユーザーの評価平均_分布_料理_味 = Column(String(10))
    # 53
    ユーザーの評価平均_分布_サービス = Column(String(10))
    # 54
    ユーザーの評価平均_分布_雰囲気 = Column(String(10))
    # 55
    ユーザーの評価平均_分布_酒_ドリンク = Column(String(10))
    # 56
    ユーザーの評価平均_分布_コストパフォーマンス = Column(String(10))

    # 複数カラムにユニーク制約を追加
    __table_args__ = (
        UniqueConstraint("店名", "住所", "最寄り駅", "電話番号", name="dupli"),
    )

    def __repr__(self) -> str:
        return f"<DbTestModel(id={self.id}, some_column={self.店名})>"

with engine.connect() as connection:
    connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
    log.logger.info(f"[Drop_Table]: {table_name}")

Base.metadata.create_all(engine, checkfirst=True)

log.logger.info("[Create_Table]")
