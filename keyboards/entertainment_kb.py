from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON

# ------- Создаем клавиатуру через InlineKeyboardBuilder -------

# Создаем кнопки
button_1: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['rsp_game'],
                                                      callback_data='rsp_game')
button_2: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['jokes'],
                                                      callback_data='jokes')
button_3: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['shotgun'],
                                                      callback_data='shotgun')


# Инициализируем билдер для клавиатуры
entertainment_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

# Добавляем кнопку rsp_game
entertainment_builder.row(button_1, width=1)

# Добавляем кнопку jokes в следующий ряд
entertainment_builder.row(button_2, width=1)

# Добавляем кнопку shotgun в следующий ряд
entertainment_builder.row(button_3, width=1)

# Создаем клавиатуру
entertainment_kb: InlineKeyboardMarkup = entertainment_builder.as_markup(
                                                one_time_keyboard=False,
                                                resize_keyboard=True)
