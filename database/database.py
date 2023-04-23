import pandas as pd
import os
from config_data.config import Config, load_config

config: Config = load_config()

# если бд пустая, инициализируем ее, добавив заголовки
if os.stat(config.data_base.path).st_size == 0:
    headers = pd.DataFrame(columns=['user_id',
                                    'user_choice_class',
                                    'bot_choice_class',
                                    'flag_user_vin'])
    with open(config.data_base.path, mode='w+')\
            as games_results_headers:
        headers.to_csv(games_results_headers, header=True, index=False)

# очистка бд при отладке
# games_results = open(config.data_base.path,
#                      mode='w+')
# games_results.close()


# функция загрузки данных из базы для моделирования
def get_user_data_for_model_from_bd(user_id: int,
                                    PATH: str) -> list[list[int]]:
    games_results = pd.read_csv(PATH)
    user_data_for_model = games_results.query('user_id == @user_id')
    # если данных нет, возвращаем двумерный пустой массив
    if len(user_data_for_model) == 0:
        user_data_for_model = [[None, None]]
    else:
        user_data_for_model = list(user_data_for_model[['user_choice_class',
                                                        'bot_choice_class']]
                                    .apply(lambda x: list(x), axis=1))
    return user_data_for_model


# функция заливки данных в базу
def put_games_results_to_bd(results: list,
                            PATH: str):
    '''
    input:

    results['user_id',
    'user_choice_class',
    'bot_choice_class',
    'flag_user_vin']

    PATH to db games_results.csv

    '''
    with open(PATH, mode='a') as games_results:
        df_to_export = pd.DataFrame(columns=['user_id',
                                             'user_choice_class',
                                             'bot_choice_class',
                                             'flag_user_vin'])
        df_to_export.loc[len(df_to_export.index)] = results
        df_to_export.to_csv(games_results, header=False, index=False)


# функция загрузки данных из базы для статистики
def get_user_data_for_statistic_from_bd(user_id: int,
                                        PATH: str):
    games_results = pd.read_csv(PATH)
    user_data_for_statistic = games_results.query('user_id == @user_id')
    # если данных нет, присвоим пустой список
    if len(user_data_for_statistic) == 0:
        user_data_for_statistic = []
    else:
        user_data_for_statistic = user_data_for_statistic[['user_choice_class',
                                                           'bot_choice_class',
                                                           'flag_user_vin']]
    return user_data_for_statistic


# функция удаления записей из бд по юзеру
def user_data_drop(user_id: int,
                   PATH: str):
    # вытащим данные из файла
    data = pd.read_csv(PATH)
    data_without_user = data.query('user_id != @user_id')
    # перезапишем файл уже без выбранного юзера юзера
    with open(PATH, mode='w+') as games_results:
        data_without_user.to_csv(games_results, header=True, index=False)


# ручное добавление записей в games_results для отладки
# with open(config.data_base.path, mode='a')\
#           as games_results:
#     df_to_export = pd.DataFrame(columns=['user_id',
#                                          'user_choice',
#                                          'bot_choice',
#                                          'flag_user_vin'])
#     # добавляем строку
#     df_to_export.loc[len(df_to_export.index)] = [112, 2, 0, 0]
#     df_to_export.to_csv(games_results, header=False, index=False)
