import asyncio
import logging
import os

from typing import Optional
from contextlib import suppress

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from utils import *



logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ.get("TOKEN"))
dp = Dispatcher()

users_config = {}
users_answer = {}


class UserInfo():
    """
        Класс для хранения пользовательской информации
    """
    dictionary: str = DEFAULT_DICTIONARY
    match: str = DEFAULT_MATCH


class Dictionary_form(StatesGroup):
    """
        FSM класс для выбора словаря
    """
    dictionary = State()


class Match_form(StatesGroup):
    """
        FSM класс для выбора настроек
    """
    match = State()

def get_start_keyboard():
    """
        Сборка главного меню
    """
    kb = [[KeyboardButton(text='/Dictionaries')], [KeyboardButton(text='/Settings')],
          [KeyboardButton(text='/Alphabet')], [KeyboardButton(text='/Alphabet_special')]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="",
        one_time_keyboard=True)
    answer = ("Добро пожаловать! Для выбора используемого словаря нажмите кнопку /Dictionaries.\n" +
    "Для настройки поиска нажмите кнопку /Settings.\n" +
    "Для получения tap-to-copy всех или только специальных символов алфавита нажмите кнопку" +
    "/Alphabet или /Alphabet_special соответственно.\n" +
    "Для получения перевода просто отправьте слово в чат.")

    return keyboard, answer


@dp.message(Command("start"))
@dp.message(Command("help"))
@dp.message(Command("menu"))
async def cmd_start(message: types.Message):
    """
        Вывод главного меню
    """
    k, a = get_start_keyboard()
    await message.answer(
        a,
        reply_markup=k
        )


@dp.message(Command("Dictionaries"))
async def cmd_dict(message: types.Message, state: FSMContext):
    """
        Инициализация смены словаря
    """
    await state.set_state(Dictionary_form.dictionary)
    kb = []
    for dictionary in DICTIONARIES.keys():
        kb.append([KeyboardButton(text=dictionary)])

    kb.append([KeyboardButton(text="/cancel")])
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Доступные словари:",
        one_time_keyboard=True)
    await message.answer(
        "Выберите словарь, который вы хотели бы использовать",
        reply_markup=keyboard
        )


@dp.message(Command("Settings"))
async def cmd_match(message: types.Message, state: FSMContext):
    """
        Инициализация смены настроек
    """
    await state.set_state(Match_form.match)
    kb = []
    for match in MATCHES.keys():
        kb.append([KeyboardButton(text=match)])
    kb.append([KeyboardButton(text="/cancel")])
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Доступные режимы:",
        one_time_keyboard=True)
    await message.answer(
        "Какой режим поиска вы хотели бы использовать?",
        reply_markup=keyboard
        )


@dp.message(Command("Alphabet"))
async def cmd_alpha(message: types.Message):
    """
        Вывод полного алфавита
    """
    dictio = users_config.get(message.from_user.id, UserInfo()).dictionary
    alphabet = get_alphabet(DICTIONARIES[dictio][0])
    answer_msg = '`' + ('` `').join(alphabet) + '`'
    await message.answer(
        answer_msg,
        parse_mode=ParseMode.MARKDOWN
        )


@dp.message(Command("Alphabet_special"))
async def cmd_alpha_spec(message: types.Message):
    """
        Вывод специальных символов алфавита
    """
    dictio = users_config.get(message.from_user.id, UserInfo()).dictionary
    alphabet = get_alphabet(DICTIONARIES[dictio][0])
    rus_alphabet = get_alphabet('rus')

    alphabet = sorted(list(set(alphabet).difference(set(rus_alphabet))))
    answer_msg = '`' + ('` `').join(alphabet) + '`'

    if len(alphabet) == 0:
        answer_msg = 'В данном алфавите нет специальных символов, отличных от русского алфавита'
    await message.answer(
        answer_msg,
        parse_mode=ParseMode.MARKDOWN
        )


@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
        Отмена действия, возвращение в исходную ноду FSM
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()

    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )

    k, a = get_start_keyboard()
    await message.answer(
        a,
        reply_markup=k)


@dp.message(Dictionary_form.dictionary)
async def process_dictionary(message: Message, state: FSMContext) -> None:
    """
        Обработка выбора словаря
    """
    await state.update_data(dictionary=message.text)
    ans = None
    if message.text in DICTIONARIES.keys():
        users_config[message.from_user.id] = users_config.get(message.from_user.id, UserInfo())
        users_config[message.from_user.id].dictionary = message.text
        ans = message.text + ' теперь используется'
    else:
        ans = 'Словарь не найден'

    await state.clear()
    await message.answer(ans)

    k, a = get_start_keyboard()
    await message.answer(
        a,
        reply_markup=k)


@dp.message(Match_form.match)
async def process_dictionary(message: Message, state: FSMContext) -> None:
    """
        Обработка выбора настроек
    """
    await state.update_data(dictionary=message.text)
    ans = None
    if message.text in MATCHES.keys():
        users_config[message.from_user.id] = users_config.get(message.from_user.id, UserInfo())
        users_config[message.from_user.id].match = message.text
        ans = message.text + ' теперь используется'
    else:
        ans = 'Словарь не найден'

    await state.clear()
    await message.answer(ans)


class AnswerCallbackFactory(CallbackData, prefix="fabnum"):
    """
        Класс-фабрика для коллбэков
    """
    action: str
    value: Optional[int] = None


def print_answer(answer: Answer):
    """
        Вывод ответа
    """
    translation = answer.get_item()
    cur_iter = answer.get_iter()
    len_trans = answer.len()

    main_text = translation.form_message()
    page = f'\n\nСтраница {cur_iter + 1}/{len_trans}\n'

    return main_text + page


def get_keyboard_answer():
    """
        Сборка клавиатуры для ответа
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Пред.", callback_data=AnswerCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="Закрыть", callback_data=AnswerCallbackFactory(action="close")
    )
    builder.button(
        text="След.", callback_data=AnswerCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="Вернуться в меню", callback_data=AnswerCallbackFactory(action="menu")
    )
    builder.adjust(3)
    return builder.as_markup()


@dp.message(F.text)
async def translate(message: types.Message):
    """
        Обработчик текстового запроса
    """
    user_info = users_config.get(message.from_user.id, UserInfo())
    translations = get_translation(
        to_look=message.text,
        source_lang=DICTIONARIES[user_info.dictionary],
        full_match=MATCHES[user_info.match]
    )
    if len(translations) == 0:
        await message.reply("По данному запросу результатов не найдено")
        return
    users_answer[message.from_user.id] = Answer(translations)

    await message.reply(print_answer(users_answer[message.from_user.id]), parse_mode=ParseMode.MARKDOWN, reply_markup=get_keyboard_answer())


async def update_translation(message: types.Message, new_text: str):
    """
        Обновление ответа на запрос
    """
    with suppress(TelegramBadRequest):
        await message.edit_text(
            new_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard_answer()
        )


@dp.callback_query(AnswerCallbackFactory.filter())
async def callbacks_anwer_change(
        callback: types.CallbackQuery,
        callback_data: AnswerCallbackFactory
):
    """
        Обработка коллбэков для обновления ответа
    """
    if callback_data.action == "change":
        users_answer[callback.from_user.id].move_iter(callback_data.value)
        await update_translation(callback.message, print_answer(users_answer[callback.from_user.id]))
    else:
        if callback_data.action == "menu":
            k, a = get_start_keyboard()
            await message.answer(
                a,
                reply_markup=k)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer()


async def main():
    log_message("===== Bot started =====")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())