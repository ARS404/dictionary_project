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
        """
        source = line.find("term").text
        tt = line.find("tt")
        target = tt.find("t").text

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


    def form_message(self) -> str:

        """
            Сборка сообщения для вывода
        """
        message = textwrap.dedent("""
            **Словарь:** {}
            **Запрос:** {}
            **Перевод:** {}
        """.format(
            LangPairs.pair_names[self.lang_pair],
            self.source,
            self.target
        ))
        if len(self.info.items()) > 0:
            message += "\nДополнительная информация:"
            for key, val in self.info.items():
                message += "\n"
                message += f" **- {key}:** {val}"
        return message


class Answer(object):

    """
        Класс для итерации по переводам
    """
    def __init__(self, translations):
        self.translations = translations
        self.iterator = 0

    def move_iter(self, value):
        """
            Циклическая итерация по переводам
        """
        if len(self.translations):
            self.iterator = (self.iterator + value) % len(self.translations)

    def get_item(self) -> Translation:
        """
            Извлечение текущего перевода
        """
        if self.iterator < len(self.translations):
            return self.translations[self.iterator]

    def get_iter(self):
        """
            Получение номера текущей страницы
        """
        return self.iterator

    def len(self):
        """
            Получение общего количества страниц
        """
        return len(self.translations)