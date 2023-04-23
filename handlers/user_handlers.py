from aiogram import Router
from aiogram import Bot
from aiogram.filters import Command, CommandStart, StateFilter, Text, or_f
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

# from filters.filters import
from keyboards.entertainment_kb import entertainment_kb
from keyboards.rsp_kb import game_rsp_kb
from keyboards.jokes_kb import jokes_kb
from lexicon.lexicon import LEXICON
from services.rsp_game import (rsp_process,
                               rsp_statistic,
                               rps_statistic_who_better)
from services.jokes_requests import (genre_joke,
                                     insult_joke,
                                     chuk_norris_joke,
                                     random_joke)
from services.yandex_translator import translate_ru
from database.database import user_data_drop
import time
from config_data.config import Config, load_config

config: Config = load_config()

# указываем переменную пути к БД
PATH = config.data_base.path

# создаем объект роутера
router: Router = Router()


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMEnterteinmentType(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    main_menu = State()        # Нахождение в главном меню
    rsp = State()              # Нахождение в меню игры камень-ножницы-бумага
    jokes = State()            # Нахождение в меню шуток
    joke_received = State()    # Нахождение в меню шуток c полученной шуткой


# Этот хэндлер будет срабатывать на команду "/start"
# при первом запуске и из главного меню
# отправлять приветственное сообщение
# отправлять клавиатуру главного меню
# переводить бота в состояние главного меню
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, bot: Bot):
    # удаляем старое сообщение, если есть
    try:
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id - 1)
    except:
        pass
    # удаляем сообщение '/start'
    await message.delete()
    # обновляем клавиатуру и приветствие
    await message.answer(LEXICON['/start'], reply_markup=entertainment_kb)
    await state.set_state(FSMEnterteinmentType.main_menu)


# ------ ХЭНДЛЕРЫ В ГЛАВНОМ МЕНЮ (НАЧАЛО) ------
# у всех состояние нахождения в главном меню

# Этот хэндлер будет срабатывать на кнопку [Игра камень-ножницы-бумага]
# присылать клавиатуру игры
# присылать сообщение по игре
# переводить бота в состояние нахождения в меню игры камень-ножницы-бумага
@router.callback_query(Text(text='rsp_game'),
                       StateFilter(FSMEnterteinmentType.main_menu))
async def process_jokes_game_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON['rsp_game_menu'],
                                     reply_markup=game_rsp_kb)
    # Устанавливаем состояние нахождения в меню  игры камень-ножницы-бумага
    await state.set_state(FSMEnterteinmentType.rsp)


# Этот хэндлер будет срабатывать на кнопку [Случайные шутки по жанрам]
# присылать клавиатуру жанров шуток
# переводить бота в состояние нахождения в меню шуток
@router.callback_query(Text(text='jokes'),
                       StateFilter(FSMEnterteinmentType.main_menu))
async def process_jokes_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON['jokes_menu'],
                                     reply_markup=jokes_kb)
    # Устанавливаем состояние нахождения в меню шуток
    await state.set_state(FSMEnterteinmentType.jokes)


# Этот хэндлер будет срабатывать на кнопку [Потянуться к дальней полке с дробовиком]
# присылает песню из терминатора и сообщение
# при каждом новом нажатии на кнопку затирает старые сообщения
@router.callback_query(Text(text='shotgun'),
                       StateFilter(FSMEnterteinmentType.main_menu))
async def process_shotgun(callback: CallbackQuery,
                          state: FSMContext,
                          bot: Bot):
    # удаляем старую клавиатуру с сообщением
    await callback.message.delete()
    # получаем id ранее отправленного audio сообщения (если есть)
    message_dict = await state.get_data()
    # удаляем ранее отправленный аудиофайл, если такой был
    if len(message_dict) > 0:
        message_id = message_dict['message_id']
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=message_id)
    audio = await bot.send_audio(
            chat_id=callback.message.chat.id,
            audio='CQACAgIAAxkBAAIDsGRFAQwBzgIY_NbgTYzIz38x_Pt9AAI_KQACj5MpSvMGc7VruUzXLwQ')
    # запоминаем номер сообщения с аудиофайлом по ключу 'message_id'
    await state.update_data(message_id=audio.message_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=LEXICON['shotgun_choice'],
                           reply_markup=entertainment_kb)


# Этот хэндлер будет срабатывать на команду "/help" в главном меню
# удалять старое сообщение и выводить новое
@router.message(Command(commands='help'),
                StateFilter(FSMEnterteinmentType.main_menu))
async def process_help_main_menu_command(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await message.answer(text=LEXICON['help_main_menu'],
                         reply_markup=entertainment_kb)


# Этот хэндлер будет срабатывать на любые другие команды в главном меню
# удалять старое сообщение и выводить новое
@router.message(StateFilter(FSMEnterteinmentType.main_menu))
async def process_main_menu_command_unknown(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await message.answer(text=LEXICON['unknown'],
                         reply_markup=entertainment_kb)

# ------ ХЭНДЛЕРЫ В ГЛАВНОМ МЕНЮ (КОНЕЦ) ------

# ------ ХЭНДЛЕРЫ В МЕНЮ ИГРЫ КАМЕНЬ-НОЖНИЦЫ-БУМАГА (НАЧАЛО) ------
# у всех состояние нахождения в меню игры

# Этот хэндлер будет срабатывать на кнопки [камень, ножницы, бумага]
# из меню игры камень-ножницы-бумага и возвращать результат игры
# и присылать текст в зависимости от результата
@router.callback_query(StateFilter(FSMEnterteinmentType.rsp),
                       or_f(Text(text='rock'),
                            Text(text='scissors'),
                            Text(text='papper')))
async def process_rsp_game_result(callback: CallbackQuery, state: FSMContext):
    # возвращаем ответ о подготовке результатов
    # заодно обходим ошибку о неизменяемом сообщении
    await callback.message.edit_text(text=LEXICON['rsp_protocols'])
    # Рассчитываем результаты игры
    # также функция записывает результаты в бд
    bot_choice, vinner = rsp_process(
        user_choice=callback.data,
        user_id=callback.from_user.id,
        PATH=PATH)
    # отправляем в чат результаты с комментарием
    await callback.message.edit_text(
        text=f'<b>Ты:</b> {LEXICON[callback.data]} | '
             f'<b>Я:</b> {LEXICON[bot_choice]}\n'
             '--------------------------------------------------------\n'
             f'{LEXICON[vinner]}',
        reply_markup=game_rsp_kb)


# Этот хэндлер будет срабатывать на кнопку [Статистика игр]
# и присылать статистику игр с комментарием, кто круче
@router.callback_query(StateFilter(FSMEnterteinmentType.rsp),
                       Text(text='statistic'))
async def process_rsp_game_statistic(callback: CallbackQuery,
                                     state: FSMContext):
    # сбор статистики
    (total_plays,
     vin_rate,
     draw_rate,
     loose_rate,
     favourite_choice) = rsp_statistic(
        user_id=callback.from_user.id,
        PATH=PATH)
    # комментарий кто круче
    who_better = rps_statistic_who_better(vin_rate, loose_rate,
                                          favourite_choice)
    # возвращаем ответ о подготовке статистики
    # заодно обходим ошибку о неизменяемом сообщении
    await callback.message.edit_text(text=LEXICON['statistic_gathering'])
    time.sleep(1)
    # выводим статистику
    await callback.message.edit_text(
        text='----------------------------------------------------------\n'
             f'{LEXICON["total_plays"]}{total_plays}\n'
             f'{LEXICON["vin_rate"]}{vin_rate:.1%}\n'
             f'{LEXICON["draw_rate"]}{draw_rate:.1%}\n'
             f'{LEXICON["loose_rate"]}{loose_rate:.1%}\n'
             f'{LEXICON["favourite_choice"]}{LEXICON[favourite_choice]}\n'
             '----------------------------------------------------------\n'
             f'{LEXICON[who_better]}',
        reply_markup=game_rsp_kb)


# Этот хэндлер будет срабатывать на кнопку [Сброс прогресса]
# удалять данные пользователя и выдавать сообщение о сбросе прогресса
@router.callback_query(StateFilter(FSMEnterteinmentType.rsp),
                       Text(text='drop_data'))
async def reset_progress(callback: CallbackQuery,
                         state: FSMContext):
    # удалим данные
    user_data_drop(user_id=callback.from_user.id,
                   PATH=PATH)
    await callback.message.edit_text(text=LEXICON['data_droped'],
                                     reply_markup=game_rsp_kb)


# Этот хэндлер будет срабатывать на команду "/help" в меню игры
# удалять старое сообщение и выводить новое
@router.message(Command(commands='help'),
                StateFilter(FSMEnterteinmentType.rsp))
async def process_help_rsp_command(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await message.answer(text=LEXICON['help_main_menu'],
                         reply_markup=game_rsp_kb)


# Этот хэндлер будет срабатывать на любые другие команды в меню игры
# удалять старое сообщение и выводить новое
@router.message(StateFilter(FSMEnterteinmentType.rsp))
async def process_rsp_command_unknown(message: Message, bot: Bot):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await message.answer(text=LEXICON['unknown'],
                         reply_markup=game_rsp_kb)

# ------ ХЭНДЛЕРЫ В МЕНЮ ИГРЫ КАМЕНЬ-НОЖНИЦЫ-БУМАГА (КОНЕЦ) ------

# ------ ХЭНДЛЕРЫ В МЕНЮ ШУТОК (НАЧАЛО) ------

# Этот хэндлер будет срабатывать на кнопки [Программирование, Каламбур, Черный юмор, Жуткий юмор]
# и присылать текст шутки
@router.callback_query(or_f(StateFilter(FSMEnterteinmentType.jokes),
                            StateFilter(FSMEnterteinmentType.joke_received)),
                       or_f(Text(text='Programming'),
                            Text(text='Dark'),
                            Text(text='Pun'),
                            Text(text='Spooky')))
async def process_joke_genre_result(callback: CallbackQuery,
                                    state: FSMContext):
    # возвращаем ответ о поиске шутки
    # заодно обходим ошибку о неизменяемом сообщении
    await callback.message.edit_text(text=LEXICON['searching_for_joke'],
                                     reply_markup=jokes_kb)
    time.sleep(1)
    # вытаскиваем шутку
    joke = genre_joke(callback.data)
    # отправляем шутку в чат
    await callback.message.edit_text(text=joke, reply_markup=jokes_kb)
    # Устанавливаем состояние нахождения в меню шуток c полученной шуткой
    await state.set_state(FSMEnterteinmentType.joke_received)



# Этот хэндлер будет срабатывать на кнопки [Оскорбления]
# и присылать текст шутки
@router.callback_query(or_f(StateFilter(FSMEnterteinmentType.jokes),
                            StateFilter(FSMEnterteinmentType.joke_received)),
                       Text(text='insult'))
async def process_joke_insult_result(callback: CallbackQuery,
                                     state: FSMContext):
    # возвращаем ответ о поиске шутки
    # заодно обходим ошибку о неизменяемом сообщении
    await callback.message.edit_text(text=LEXICON['searching_for_joke'],
                                     reply_markup=jokes_kb)
    time.sleep(1)
    # вытаскиваем шутку
    joke = insult_joke()
    # отправляем шутку в чат
    await callback.message.edit_text(text=joke, reply_markup=jokes_kb)
    # Устанавливаем состояние нахождения в меню шуток c полученной шуткой
    await state.set_state(FSMEnterteinmentType.joke_received)


# Этот хэндлер будет срабатывать на кнопки [Чак Норрис]
# и присылать текст шутки
@router.callback_query(or_f(StateFilter(FSMEnterteinmentType.jokes),
                            StateFilter(FSMEnterteinmentType.joke_received)),
                       Text(text='chuk_norris'))
async def process_joke_chuk_norris_result(callback: CallbackQuery,
                                          state: FSMContext):
    # возвращаем ответ о поиске шутки
    # заодно обходим ошибку о неизменяемом сообщении
    await callback.message.edit_text(text=LEXICON['searching_for_joke'],
                                     reply_markup=jokes_kb)
    time.sleep(1)
    # вытаскиваем шутку
    joke = chuk_norris_joke()
    # отправляем шутку в чат
    await callback.message.edit_text(text=joke, reply_markup=jokes_kb)
    # Устанавливаем состояние нахождения в меню шуток c полученной шуткой
    await state.set_state(FSMEnterteinmentType.joke_received)


# Этот хэндлер будет срабатывать на кнопки [Разные другие шутки]
# и присылать текст шутки
@router.callback_query(or_f(StateFilter(FSMEnterteinmentType.jokes),
                            StateFilter(FSMEnterteinmentType.joke_received)),
                       Text(text='random'))
async def process_joke_random_result(callback: CallbackQuery,
                                     state: FSMContext):
    # возвращаем ответ о поиске шутки
    # заодно обходим ошибку о неизменяемом сообщении
    await callback.message.edit_text(text=LEXICON['searching_for_joke'],
                                     reply_markup=jokes_kb)
    time.sleep(1)
    # вытаскиваем шутку
    joke = random_joke()
    # отправляем шутку в чат
    await callback.message.edit_text(text=joke, reply_markup=jokes_kb)
    # Устанавливаем состояние нахождения в меню шуток c полученной шуткой
    await state.set_state(FSMEnterteinmentType.joke_received)


# Этот хэндлер будет срабатывать на кнопки [Перевести на русский]
# в состоянии полученной шутки
# и присылать текст шутки на русском
# и устанавливать состояние нахождения в меню шуток
@router.callback_query(StateFilter(FSMEnterteinmentType.joke_received),
                       Text(text='translate'))
async def process_joke_translate_result(callback: CallbackQuery,
                                        state: FSMContext):
    # для красоты добавляем сообщение о начале перевода
    await callback.message.edit_text(text=LEXICON['translating_process'],
                                     reply_markup=jokes_kb)
    time.sleep(1)
    # переводим шутку
    joke_translated = translate_ru(callback.message.text)
    # отправляем переведенную шутку в чат
    await callback.message.edit_text(text=joke_translated,
                                     reply_markup=jokes_kb)
    await state.set_state(FSMEnterteinmentType.jokes)


# Этот хэндлер будет срабатывать на кнопки [Перевести на русский]
# в состоянии без полученной шутки
# и присылать текст об отсутствии шутки
@router.callback_query(StateFilter(FSMEnterteinmentType.jokes),
                       Text(text='translate'))
async def process_nothing_translate_result(callback: CallbackQuery,
                                           state: FSMContext):
    # отправляем промежуточное сообщение,
    # чтобы обойти ошибку неизенившегося сообщения
    await callback.message.edit_text(text=LEXICON['translating_process'],
                                     reply_markup=jokes_kb)
    time.sleep(1)
    # отправляем в чат предупреждение об отсутствии шутки
    await callback.message.edit_text(text=LEXICON['nothing_translate'],
                                     reply_markup=jokes_kb)


# Этот хэндлер будет срабатывать на команду "/help"
# в меню шуток с полученой шуткой и без
# удалять старое сообщение и выводить новое
# переводить бота в состояние с отсутствием шутки
@router.message(Command(commands='help'),
                or_f(StateFilter(FSMEnterteinmentType.jokes),
                     StateFilter(FSMEnterteinmentType.joke_received)))
async def process_help_jokes_command(message: Message,
                                     bot: Bot,
                                     state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await message.answer(text=LEXICON['help_jokes'],
                         reply_markup=jokes_kb)
    await state.set_state(FSMEnterteinmentType.jokes)


# Этот хэндлер будет срабатывать на любые другие команды
# в меню шуток с полученой шуткой и без
# удалять старое сообщение и выводить новое
# переводить бота в состояние с отсутствием шутки
@router.message(or_f(StateFilter(FSMEnterteinmentType.jokes),
                     StateFilter(FSMEnterteinmentType.joke_received)))
async def process_jokes_command_unknown(message: Message,
                                        bot: Bot,
                                        state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id - 1)
    await message.delete()
    await message.answer(text=LEXICON['unknown'],
                         reply_markup=jokes_kb)
    await state.set_state(FSMEnterteinmentType.jokes)

# ------ ХЭНДЛЕРЫ В МЕНЮ ШУТОК (КОНЕЦ) ------



# ------ ОСТАЛЬНЫЕ ХЭНДЛЕРЫ (НАЧАЛО) ------

# Этот хэндлер будет срабатывать на кнопку [назад]:
# присылать клавиатуру главного меню
# переводить бота в состояние по умолчанию
@router.callback_query(Text(text='back'),
                       or_f(StateFilter(FSMEnterteinmentType.rsp),
                            StateFilter(FSMEnterteinmentType.jokes),
                            StateFilter(FSMEnterteinmentType.joke_received)))
async def process_back_to_main_menu(callback: CallbackQuery,
                                    state: FSMContext):
    await callback.message.edit_text(text=LEXICON['back_2_main_menu'],
                                     reply_markup=entertainment_kb)
    # Устанавливаем состояние нахождения в главном меню
    await state.set_state(FSMEnterteinmentType.main_menu)

# ------ ОСТАЛЬНЫЕ ХЭНДЛЕРЫ (КОНЕЦ) ------