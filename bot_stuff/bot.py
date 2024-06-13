import asyncio
import logging
import json
import typing
from typing import Literal
from typing import Optional
from contextlib import suppress
import types
from enum import Enum
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
import os
import sys

class LangPairs(Enum):
    rus_udm = Literal["rus", "udm"]
    udm_rus = Literal["udm", "rus"]
    # may be extended

class Translation(object):
    lang_pair: LangPairs
    source: str
    target: str
    usage_example: str
    info: str

    def __init__(self, lang_pair, source, target, usage_example, info):
        self.lang_pair, self.source, self.target, self.usage_example, self.info = lang_pair, source, target, usage_example, info
 
def get_translation(to_look: str, source_lang: LangPairs, full_match: bool = True) -> [Translation]:
    return [Translation(lang_pair=source_lang, source=to_look, target='я ниче не нашел', usage_example='примера нет', info=''),
            Translation(lang_pair=source_lang, source=to_look, target='ну и фиг с ним', usage_example='', info='мужской род, а может и женский'),
            ]

class Answer(object):
    def __init__(self, translations):
        self.translations = translations
        self.iterator = 0

    def move_iter(self, value):
        if len(self.translations):
            self.iterator = (self.iterator + value) % len(self.translations)

    def get_item(self):
        if self.iterator < len(self.translations):
            return self.translations[self.iterator]

    def get_iter(self):
        return self.iterator

    def len(self):
        return len(self.translations)


logging.basicConfig(level=logging.INFO)
bot = Bot(token="")
dp = Dispatcher()

users_config = {}
users_answer = {}

dictionaries = {'Русско-удмуртский словарь': LangPairs.rus_udm}
matches = {"Полное совпадение": True, "Частичное совпадение": False}

default_dictionary = 'Русско-удмуртский словарь'
default_config = "Полное совпадение"


class UserInfo():
    dictionary: str = default_dictionary
    match: str = default_config

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
    for dictionary in dictionaries.keys():
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
    for match in matches.keys():
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
    if message.text in dictionaries.keys():
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
    if message.text in matches.keys():
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
        source_lang=dictionaries[user_info.dictionary], 
        full_match=matches[user_info.match]
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
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())