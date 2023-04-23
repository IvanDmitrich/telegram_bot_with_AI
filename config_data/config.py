from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту


@dataclass
class YandexTr:
    iam_token: str
    folder_id: str


@dataclass
class DataBase:
    path: str


@dataclass
class Config:
    tg_bot: TgBot
    yandex_tr: YandexTr
    data_base: DataBase


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  yandex_tr=YandexTr(iam_token=env('IAM_TOKEN'),
                                     folder_id=env('FOLDER_ID')),
                  data_base=DataBase(path=env('DB_PATH')))
