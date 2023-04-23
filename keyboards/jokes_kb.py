from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON

# ------- Создаем клавиатуру через InlineKeyboardBuilder -------

# Создаем кнопки
button_1: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['chuk_norris'],
                                                      callback_data='chuk_norris')
button_2: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['insult'],
                                                      callback_data='insult')
button_3: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['programming'],
                                                      callback_data='Programming')
button_4: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['dark'],
                                                      callback_data='Dark')
button_5: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['pun'],
                                                      callback_data='Pun')
button_6: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['spooky'],
                                                      callback_data='Spooky')
button_7: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['random'],
                                                      callback_data='random')
button_8: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['back'],
                                                      callback_data='back')
button_9: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['translate'],
                                                      callback_data='translate')



# Инициализируем билдер для клавиатуры
jokes_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

# Добавляем кнопки
jokes_builder.row(button_3, button_5, width=2)
jokes_builder.row(button_4, button_6, width=2)
jokes_builder.row(button_2, button_1, width=2)
jokes_builder.row(button_7, width=1)
jokes_builder.row(button_9, width=1)
jokes_builder.row(button_8, width=1)

# Создаем клавиатуру
jokes_kb: InlineKeyboardMarkup = jokes_builder.as_markup(
                                                one_time_keyboard=False,
                                                resize_keyboard=True)
