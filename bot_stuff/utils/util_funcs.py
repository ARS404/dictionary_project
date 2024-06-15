import os
import pathlib
import io

import xml.etree.ElementTree as ElementTree

from typing import List

from .constants import *
from .util_classes import *



def log_message(txt: str) -> None:
    """
        Функция для логирования технических сообщений бота
    """
    log_file = os.environ.get("BOT_LOG_FILE")
    if log_file is None:
        return
    with open(log_file, "a") as f:
        print(txt, file=f, flush=True)


def _get_dct(lang_pair: LangPairs) -> ElementTree:
    """
        Поиск и считывание нужного словаря среди файлов
    """
    dct_file_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(),
        "..", "..", "data", "dictionaries",
        f"{lang_pair[0]}-{lang_pair[1]}.xml"
    )
    if not os.path.exists(dct_file_path):
        return None
    return ElementTree.parse(dct_file_path)


def _get_translation(dct: ElementTree, source_text: str) -> str:
    """
        Поиск термина по словарю
    """
    root = dct.getroot()
    for line in root.findall("line"):
        term = line.find("term")
        if term is None:
            continue
        if term.text == source_text:
            return line


def _get_variants(source_lang: str, source_text: str) -> List[str]:
    """
        Поиск терминов по словарю
    """
    return source_text # TODO: finish implementation


def get_translation(to_look: str, source_lang: LangPairs, full_match: bool = True) -> List[Translation]:
    """
        Поиск термина по словарю и сборка ответов
    """
    dct = _get_dct(source_lang)
    if dct is None:
        return [] # TODO: handle this case

    source_texts = [to_look]
    if not full_match:
        source_texts = _get_variants(source_lang[0], to_look)
    result = []

    for text in source_texts:
        tr_line = _get_translation(dct, text)
        if tr_line is not None:
            translation = Translation()
            translation.init_from_xml_line(source_lang, tr_line)
            result.append(translation)
    return result