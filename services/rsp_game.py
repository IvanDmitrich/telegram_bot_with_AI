from ML_model.predictor import prediction
from database.database import (get_user_data_for_model_from_bd,
                               get_user_data_for_statistic_from_bd,
                               put_games_results_to_bd)
import pandas as pd


# функция конвертирования выбора в класс и обратно
def _choice_to_class_and_back(choice: str | int) -> int | str:
    '''
    :rock <--> 0
    :scissors <--> 1
    :papper <--> 2
    '''
    dictionary = {'rock': 0,
                  'scissors': 1,
                  'papper': 2,
                  0: 'rock',
                  1: 'scissors',
                  2: 'papper'}
    return dictionary[choice]


# функция определения победителя
def _vinner(user_bot_choices: list[int]):
    '''
    1 - пользователь победил
    0 - ничья
    -1 - бот победил
    '''
    dict_user_vins = {-1: [[0, 2], [1, 0], [2, 1]],
                      0: [[0, 0], [1, 1], [2, 2]],
                      1: [[2, 0], [0, 1], [1, 2]]}
    for flag_user_vin in dict_user_vins:
        if user_bot_choices in dict_user_vins[flag_user_vin]:
            return flag_user_vin


# функция конвертирования флага победы  в текст
def _flag_user_vin_to_text(flag_user_vin: int):
    dictionary = {-1: 'bot_vin',
                  0: 'draw',
                  1: 'user_vin'}
    return dictionary[flag_user_vin]


# функция вывода и сохраниения результатов игры
def rsp_process(user_choice: str, user_id: int, PATH: str):
    '''
    на входе:
    :текстовое значение выбора пользователя ['rock', 'scissors', 'papper']
    :идентификатор пользователя [user_id]
    :путь PATH к базе данных

    сохраняет в бд результаты игры в формате:
    :[user_id, user_choice, bot_choise, flag_user_vin]

    на выходе:
    :[выбор бота, победитель]
    '''
    # вытягиваем из бд инфо о предыдущих играх пользователя
    hist_data = get_user_data_for_model_from_bd(user_id, PATH)
    # определяем класс, выбранный ботом на основе предсказания
    bot_choice_class = prediction(hist_data)
    # определяем класс, выбранный пользователем
    user_choice_class = _choice_to_class_and_back(user_choice)
    # определяем победителя
    flag_user_vin = _vinner([user_choice_class, bot_choice_class])
    # записываем результаты в бд
    results = [user_id, user_choice_class, bot_choice_class, flag_user_vin]
    put_games_results_to_bd(results, PATH)

    return (_choice_to_class_and_back(bot_choice_class),
            _flag_user_vin_to_text(flag_user_vin))


# функция расчета статистики по данным из бд
def rsp_statistic(user_id: int, PATH: str):
    # получим данные по играм
    data = get_user_data_for_statistic_from_bd(user_id, PATH)
    # рассчитаем статистику
    # установим значения по умолчанию на случай отсутствия данных
    if len(data) == 0:
        total_plays = 0
        vin_rate = 0
        draw_rate = 0
        loose_rate = 0
        favourite_choice = 'неизвестно'
    else:
        total_plays = data.count()[0]
        vin_rate = round(
            data[data['flag_user_vin'] == 1].count()[0] / total_plays, 3
            )
        draw_rate = round(
            data[data['flag_user_vin'] == 0].count()[0] / total_plays, 3
            )
        loose_rate = round(
            data[data['flag_user_vin'] == -1].count()[0] / total_plays, 3
            )
        favourite_choice_class = data.mode()['user_choice_class'][0]
        favourite_choice = _choice_to_class_and_back(favourite_choice_class)
    return (total_plays,
            vin_rate,
            draw_rate,
            loose_rate,
            favourite_choice)


# функция определения кто лучше по статистике
def rps_statistic_who_better(vin_rate: float,
                             loose_rate: float,
                             favourite_choice: str):
    # проверяем на отсутствие статистики
    if favourite_choice == 'неизвестно':
        return 'statistic_absent'
    elif vin_rate > loose_rate:
        return 'statistic_user_better'
    elif vin_rate < loose_rate:
        return 'statistic_bot_better'
    elif vin_rate == loose_rate:
        return 'statistic_equal'
