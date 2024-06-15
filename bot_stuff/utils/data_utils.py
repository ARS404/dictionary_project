import io
import os
import pathlib

from typing import List

from .util_classes import *
from .util_funcs import _get_dct



def get_alphabet(source_lang: str) -> List[str]:

    """
        Функция для получения алфавита для текущего исходного языка
        
        args:
        source_lang: str - исходный язык

        return:
        Список символов алфавита в нижнем регистре
    """

    alphabet_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(),
        "..", "..", "data", "alphabets",
        f"{source_lang}.txt"
    )

    if not os.path.exists(alphabet_path):
        return []

    with io.open(alphabet_path, 'r', encoding='utf-8') as f:
        alphabet = f.read().split('\n')

    return alphabet


def parse_alphabet(lang_pair: LangPairs):

    """
        Функция для парсинга алфавита исходного языка из словаря
        
        args:
        lang_pair: LangPairs - словарь, который хотим распарсить

        return:
        None
    """
    alphabet = set(get_alphabet(lang_pair[0]))
    dct = _get_dct(lang_pair)
    root = dct.getroot()
    for line in root.findall("line"):
        term = line.find("term").text
        if term is None:
            continue
        alphabet = alphabet.union(set(map(lambda x: x.lower(), [*term])))

    alphabet = sorted(list(alphabet))

    alphabet = list(filter(lambda x: x.isalpha(), alphabet))

    alphabet = ('\n').join(alphabet)

    alphabet_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(),
        "..", "..", "data", "alphabets",
        f"{lang_pair[0]}.txt"
    )

    print(alphabet_path)
    print(alphabet)
    with io.open(alphabet_path, 'w', encoding='utf-8') as f:
        f.write(alphabet)