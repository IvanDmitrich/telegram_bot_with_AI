import requests
from config_data.config import Config, load_config


# функция перевода входящего текста на русский
def translate_ru(text: str) -> str:
    # Загружаем iam_token и folder_id для доступа к API переводчика
    # https://cloud.yandex.ru/docs/translate/operations/translate
    config: Config = load_config()
    iam_token = config.yandex_tr.iam_token
    folder_id = config.yandex_tr.folder_id

    # конфигурируем запрос
    body = {
        "targetLanguageCode": 'ru',
        "texts": [text],
        "folderId": folder_id}

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(iam_token)}

    response = requests.post(
        'https://translate.api.cloud.yandex.net/translate/v2/translate',
        json=body,
        headers=headers).json()

    return response['translations'][0]['text']
