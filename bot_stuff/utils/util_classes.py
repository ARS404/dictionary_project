from .constants import *


class Translation(object):
    lang_pair: LangPairs
    source: str
    target: str
    usage_example: str
    info: str

    def __init__(self, lang_pair, source, target, usage_example, info):
        self.lang_pair, self.source, self.target, self.usage_example, self.info = lang_pair, source, target, usage_example, info


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