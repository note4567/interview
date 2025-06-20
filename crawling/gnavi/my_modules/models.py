from datetime import datetime

import pytz
import set_log
from database import engine
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

log = set_log.Log("models_Logging", "...path... /log/models_log.text")
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
    updated_at = Column(
        DateTime, default=get_jp_time, onupdate=get_jp_time, nullable=False
    )

    # カラム名の設定
    # 1
    URL = Column(Text)
    # 2
    店名 = Column(String(150))
    # 3
    電話番号 = Column(String(20))
    # 4
    FAX = Column(String(20))
    # 5
    郵便番号 = Column(String(20))
    # 6
    住所 = Column(String(250))
    # 7
    アクセス = Column(Text)
    # 8
    駐車場 = Column(Text)
    # 9
    営業時間 = Column(Text)
    # 10
    定休日 = Column(String(250))
    # 11
    平均予算 = Column(String(250))
    # 12
    電子マネー_その他 = Column(String(250))
    # 13
    クレジットカード = Column(Text)
    # 14
    キャンセルについて = Column(Text)
    # 15
    お店のホームページ = Column(String(250))
    # 16
    開店年月日 = Column(String(50))
    # 17
    備考 = Column(Text)
    # 18
    総席数 = Column(String(250))
    # 19
    禁煙_喫煙 = Column(String(250))
    # 20
    お子様連れ = Column(String(250))
    # 21
    ペット同伴 = Column(String(150))
    # 22
    携帯_WiFi_電源 = Column(String(250))
    # 23
    化粧室 = Column(String(250))
    # 24
    メニューのサービス = Column(Text)
    # 25
    その他の設備_サービス = Column(Text)
    # 26
    テイクアウト = Column(Text)
    # 27
    ドレスコード = Column(String(150))
    # 28
    利用シーン = Column(Text)
    # 29
    お店のウリ = Column(String(250))
    # 30
    評価 = Column(String(10))
    # 31
    口コミ数 = Column(String(10))

    # 複数カラムにユニーク制約を追加
    __table_args__ = (
        UniqueConstraint(
            "店名",
            "住所",
            "FAX",
            "電話番号",
            "定休日",
            "開店年月日",
            "お子様連れ",
            name="dupli",
        ),
    )

    def __repr__(self) -> str:
        return f"<DbTestModel(id={self.id}, some_column={self.店名})>"

with engine.connect() as connection:
    connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
    log.logger.info(f"[Drop_Table]: {table_name}")

Base.metadata.create_all(engine, checkfirst=True)

log.logger.info("[Create_Table]")
