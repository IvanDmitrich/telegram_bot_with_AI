import random
import copy
import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression


# ---------- функция создания новых признаков ----------
def _features_maker(df: pd.DataFrame, max_lag: int = 10) -> pd.DataFrame:
    df_upd = copy.deepcopy(df)
    # зададим функцию определяющую результаты игры

    def _game_result(x):
        if any([(x == [0, 1]).all(),
                (x == [1, 2]).all(),
                (x == [2, 0]).all()]):
            return 'user_vin'
        elif any([(x == [0, 0]).all(),
                  (x == [1, 1]).all(),
                  (x == [2, 2]).all()]):
            return 'draw'
        elif any([(x == [1, 0]).all(),
                  (x == [2, 1]).all(),
                  (x == [0, 2]).all()]):
            return 'user_loss'

    # добавляем признаки выборов и результат предыдущих шагов
    for lag in range(1, max_lag+1):
        df_upd[f'user_lag_{lag}'] = df_upd['user'].shift(lag)
        df_upd[f'bot_lag_{lag}'] = df_upd['bot'].shift(lag)
        df_upd[f'lag_{lag}_result'] = df_upd[[f'user_lag_{lag}',
                                              f'bot_lag_{lag}']]\
            .apply(lambda x: _game_result(x), axis=1)
    # определяем названия столбцов с лагом пользователя и бота
    user_lag_columns = df_upd.columns[df_upd.columns.str.contains('user_lag')]
    bot_lag_columns = df_upd.columns[df_upd.columns.str.contains('bot_lag')]
    # добавляем признак первая мода лагов пользователя и бота
    df_upd['user_mode'] = df_upd[user_lag_columns].mode(axis=1)[0]
    df_upd['bot_mode'] = df_upd[bot_lag_columns].mode(axis=1)[0]
    # добавляем признак частоты выборов классов в предыдущих шагах
    # for choice in [0, 1, 2]:
    #     df_upd[f'user_choice_{choice}_share'] = df_upd[user_lag_columns]\
    #         .apply(lambda x: sum(x == choice) / x.count(), axis=1)
    #     df_upd[f'bot_choice_{choice}_share'] = df_upd[bot_lag_columns]\
    #         .apply(lambda x: sum(x == choice) / x.count(), axis=1)
    return df_upd


# ---------- функция создания признаков и разделения на X, y ----------
def _data_preparation(data: list[list[int]]):
    '''
    input: results [[user_choice, bot_choice],
                    ...]
    output: X, y
    '''
    # представим данные в табличном виде
    df = pd.DataFrame(data, columns=(['user', 'bot']))
    # добавим признаки, глубину лагов ограничим количеством проведенных игр-1
    df = _features_maker(df=df, max_lag=min(df.shape[0]-1, 6))
    # удалим первую строку (пока нет информации, боту не на чем предсказывать)
    # сбросим индекс чтобы при кодировке корректно соединить датафреймы
    df = df[1:].reset_index(drop=True)
    # --- разделим признаки на X и y ---
    X = df.drop(['user', 'bot'], axis=1)
    y = df['user']
    return X, y


# ---------- функция кодирования признаков ----------
def _data_ohe(features: pd.DataFrame, category_columns: list) -> pd.DataFrame:
    # создадим копию исходных признаков
    features_duplicate = copy.deepcopy(features)
    # инициализируем кодировщик
    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore', drop=None)
    # выполним кодировку
    features_ohe = ohe.fit_transform(features_duplicate[category_columns])
    # добавим новые названия закодированых столбцов
    features_ohe = pd.DataFrame(features_ohe,
                                columns=ohe.get_feature_names_out())
    # добавим закодированые столбцы к остальным столбцам
    features_duplicate[ohe.get_feature_names_out()] = features_ohe
    # удалим старые столбцы до кодировки
    features_duplicate.drop(columns=category_columns, inplace=True)
    return features_duplicate


# ---------- функция предсказания следующего выбора пользователя ----------
# LogisticRegression
def _next_step_log_reg_predictor(data: list[list[int]],
                                 random_first_steps: int = 3,
                                 best_features='all',
                                 regularization: float = 1.0) -> int:
    '''
    на входе:
    - последовательность выборов пользователя и
    бота в формате [[user, bot], ...]
    - количество первых шагов, для которых будет использоваться
    стратегия случайного прогноза (min=4)
    на выходе:
    - предсказание следующего выбора пользователя
    '''
    # создадим копию исходных данных
    data_copy = copy.deepcopy(data)

    # если данных для предсказания мало, выбор генерируется случайно
    if len(data_copy) <= random_first_steps:
        return random.randint(0, 2)
    else:
        # добавляем пустую пару выборов для предсказания
        data_copy.append([None, None])
        # подготовка признаков: создание новых признаков, разделение на X и y
        X, y = _data_preparation(data_copy)
        # кодируем признаки
        X = _data_ohe(
            X,
            category_columns=X.columns[~X.columns.str.contains('share')])
        # отберем лучшие признаки (работает только при количестве наблюдений 10+
        if len(data_copy) >= 10:
            feature_selector = SelectKBest(mutual_info_classif,
                                           k=best_features)
            # фитуем за исключением последнего наблюдения,
            # т.к. так нулы у целевого признака
            feature_selector.fit(X[:-1], y[:-1])
            X = feature_selector.transform(X)
        else:
            pass
        # инициализируем модель
        clf = LogisticRegression(random_state=123,
                                 penalty='l2',
                                 dual=False,
                                 C=regularization,
                                 solver='liblinear',
                                 multi_class='auto',
                                 verbose=0,
                                 warm_start=False,
                                 n_jobs=1)
        # обучим модель на всех наблюдениях, кроме последнего
        clf.fit(X[:-1], y[:-1])
        # предскажем следующий выбор
        prediction = int(clf.predict(X[-1:])[0])
        return prediction


# ---------- функция выбора робота на основании предсказания ----------
def _vin_choice(user_choice: int):
    '''
    0 - камень --> 2
    1 - ножницы --> 0
    2 - бумага --> 1
    '''
    if user_choice == 0:
        return 2
    elif user_choice == 1:
        return 0
    elif user_choice == 2:
        return 1


# ---------- функция расчета результатов игры ----------
def prediction(data: list[list[int]],
               random_first_steps=3,
               best_features=20,
               regularization=1.0):
    '''
    на входе:
    - последовательность предыдущих выборов пользователя и
    бота в формате [[user, bot], ...]
    - количество первых шагов, для которых будет использоваться
    стратегия случайного прогноза (min=3)
    - ограничение количества признаков, использующихся для прогнозирования
    - сила регуляризации логистической регрессии

    на выходе:
    - выбор бота
    '''
    # делаем предсказание бота
    # обходим ошибку классификатора, когда представлен только один класс
    if len(np.unique(np.array(data)[:, 0])) == 1 \
            and len(data) > random_first_steps:
        user_choice_prediction = np.unique(np.array(data)[:, 0][0])
    else:
        user_choice_prediction = _next_step_log_reg_predictor(
                                        data,
                                        random_first_steps,
                                        best_features,
                                        regularization)
    # делаем выбор бота
    bot_choice = _vin_choice(user_choice_prediction)
    return bot_choice

# print(prediction(data=[[1, 1],
#                        [1, 2],
#                        [1, 2],
#                        [1, 2],
#                        [1, 2],
#                        [2, 2],
#                        [2, 2],
#                        [2, 2],
#                        [2, 2],
#                        [2, 2],]))
