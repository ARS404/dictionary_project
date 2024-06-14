import asyncio
import logging
import os

from typing import Optional
from contextlib import suppress

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums.content_type import ContentType
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
    dictionary: str = DEFAULT_DICTIONARY
    match: str = DEFAULT_MATCH

class Dictionary_form(StatesGroup):
    dictionary = State()

class Match_form(StatesGroup):
    match = State()

@dp.message(Command("start"))
@dp.message(Command("help"))
@dp.message(Command("menu"))
async def cmd_start(message: types.Message):
    kb = [[KeyboardButton(text='/Dictionaries')], [KeyboardButton(text='/Settings')]]
    keyboard = ReplyKeyboardMarkup(keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="",
        one_time_keyboard=True)
    await message.answer(
        "Добро пожаловать! Для выбора используемого словаря нажмите кнопку /Dictionaries.\n" +
        "Для настройки поиска нажмите кнопку /Settings.\n" +
        "Для получения перевода просто отправьте слово в чат.",
        reply_markup=keyboard
        )

@dp.message(Command("Dictionaries"))
async def cmd_dict(message: types.Message, state: FSMContext):
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

@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
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

@dp.message(Dictionary_form.dictionary)
async def process_dictionary(message: Message, state: FSMContext) -> None:
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

@dp.message(Match_form.match)
async def process_dictionary(message: Message, state: FSMContext) -> None:
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
    action: str
    value: Optional[int] = None

def print_answer(answer: Answer):
    translation = answer.get_item()
    cur_iter = answer.get_iter()
    len_trans = answer.len()

    meta = f'Словарь: {translation.lang_pair}\nЗапрос: {translation.source}\n'
    main_info = f'Перевод: {translation.target}\nИнформация: {translation.info}\nПримеры использования: {translation.usage_example}\n'
    page = f'\nСтраница {cur_iter + 1}/{len_trans}\n'

    return meta + main_info + page

def get_keyboard_answer():
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

    await message.reply(print_answer(users_answer[message.from_user.id]), reply_markup=get_keyboard_answer())

async def update_translation(message: types.Message, new_text: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            new_text,
            reply_markup=get_keyboard_answer()
        )

@dp.callback_query(AnswerCallbackFactory.filter())
async def callbacks_anwer_change(
        callback: types.CallbackQuery,
        callback_data: AnswerCallbackFactory
):
    if callback_data.action == "change":
        users_answer[callback.from_user.id].move_iter(callback_data.value)
        await update_translation(callback.message, print_answer(users_answer[callback.from_user.id]))
    else:
        if callback_data.action == "menu":
            kb = [[KeyboardButton(text='/Dictionaries')], [KeyboardButton(text='/Settings')]]
            keyboard = ReplyKeyboardMarkup(keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder="",
                one_time_keyboard=True)
            await callback.message.answer(
                "Добро пожаловать! Для выбора используемого словаря нажмите кнопку /Dictionaries.\n" +
                "Для настройки поиска нажмите кнопку /Settings.\n" +
                "Для получения перевода просто отправьте слово в чат.",
                reply_markup=keyboard
            )
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer()


async def main():
    log_message("===== Bot started =====")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())