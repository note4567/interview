from typing import Dict

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import set_log

log = set_log.Log("database_Logging", "./log/database_log.text")
log.set_level(2)

# 環境変数からデータベース接続設定を取得
env_path = "./my_modules/.env"
env: Dict = dotenv_values(env_path, verbose=True)

# SQLAlchemy 用の接続 URL
DATABASE_URL: str = f"mysql+pymysql://{env['DB_USER']}:{env['DB_PASS']}@{env['DB_HOST']}/{env['DB_NAME']}?charset=utf8"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

log.logger.info(f"[database]: {session}")
