import re
import textwrap

import xml.etree.ElementTree as ElementTree

from .constants import *


class Translation(object):

    """
        Класс для работы с переводами: один инстанс соответствует одному вхождению в словарь
    """
    lang_pair: LangPairs
    source: str
    target: str
    info: dict

    def __init__(self) -> None:
        self.lang_pair, self.source, self.target = None, None, None
        self.info = dict()

    def init_from_xml_line(self, lang_pair: LangPairs, line: ElementTree.Element) -> None:

        """
            Инициализация от одного <line> тэга из .xml
        
            args:
            lang_pair: LangPairs - словарь
            line: ElementTree.Element - нода термина в словаре

            return:
            None
        """
        source = self._get_clear_line_from_xml(line.find("term"))
        tt = line.find("tt")
        target = self._get_clear_line_from_xml(tt.find("t"))

        self.lang_pair = lang_pair
        self.source = source
        self.target = target

        tt = line.find("tt")
        example = tt.find("example")
        if example is not None:
            self.info["Пример использования"] = f"{example.find('ex').text} -- {example.find('ex_tt').text}"

        acronyms = []
        acronyms.extend(line.findall("acronym"))
        acronyms.extend(tt.findall("acronym"))
        line_pre = line.find("pre")
        if line_pre is not None:
            acronyms.extend(line_pre.findall("acronym"))
        if len(acronyms) > 0:
            self.info["Примечания"] = ", ".join(list(map(lambda x: x.attrib["title"], acronyms)))
        print()

    def _get_clear_line_from_xml(self, element: ElementTree.Element) -> str:
        """
            return element text without tags
        """
        text = ElementTree.tostring(element, encoding="utf8").decode("utf-8")
        text = text.strip('\n')
        return re.sub("<[^>]*>", "", text)

    def form_message(self) -> str:

        """
            Сборка сообщения для вывода
        
            args:

            return:
            str - сообщения для дальнейшего вывода в боте
        """
        message = "*Словарь:* {}\n*Запрос:* {}\n*Перевод:* {}\n".format(
            LangPairs.pair_names[self.lang_pair],
            self.source,
            self.target
        )
        if len(self.info.items()) > 0:
            message += "\n*Дополнительная информация:*"
            for key, val in self.info.items():
                message += "\n"
                message += f" *- {key}:* {val}"
        return message


class Answer(object):

    """
        Класс для итерации по переводам
    """
    def __init__(self, translations):
        self.translations = translations
        self.iterator = 0

    def move_iter(self, value: int):
        """
            Циклическая итерация по переводам
        
            args:
            value: int - сдвиг по страницам
            
            return:
            None
        """
        if len(self.translations):
            self.iterator = (self.iterator + value) % len(self.translations)

    def get_item(self) -> Translation:
        """
            Извлечение текущего перевода
        
            args:
            
            return:
            Translation - текущая страница перевода
        """
        if self.iterator < len(self.translations):
            return self.translations[self.iterator]

    def get_iter(self):
        """
            Получение номера текущей страницы
        
            args:
            
            return:
            int - номер текущей страницы
        """
        return self.iterator

    def len(self):
        """
            Получение общего количества страниц
        
            args:
            
            return:
            int - общее количество страниц
        """
        return len(self.translations)