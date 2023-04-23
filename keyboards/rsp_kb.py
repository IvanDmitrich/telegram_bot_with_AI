from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON

# ------- Создаем клавиатуру через InlineKeyboardBuilder -------

# Создаем кнопки
button_1: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['rock'],
                                                      callback_data='rock')
button_2: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['scissors'],
                                                      callback_data='scissors')
button_3: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['papper'],
                                                      callback_data='papper')
button_4: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['statistic'],
                                                      callback_data='statistic')
button_5: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['drop_data'],
                                                      callback_data='drop_data')
button_6: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['back'],
                                                      callback_data='back')

# Инициализируем билдер для клавиатуры
game_rsp_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

# Добавляем кнопки rock scissors paper в один ряд
game_rsp_builder.row(button_1, button_2, button_3, width=3)

# Добавляем кнопку statistic в следующий ряд
game_rsp_builder.row(button_4, width=1)

# Добавляем кнопку drop_data в следующий ряд
game_rsp_builder.row(button_5, width=1)

# Добавляем кнопку back в следующий ряд
game_rsp_builder.row(button_6, width=1)



# Создаем клавиатуру
game_rsp_kb: InlineKeyboardMarkup = game_rsp_builder.as_markup(
                                                one_time_keyboard=False,
                                                resize_keyboard=True)
