class LangPairs(object):
    rus_itl = ("rus", "itl")
    itl_rus = ("itl", "rus")
    # may be extended

    pair_names = {
        rus_itl: "Русско-ительменский словарь",
        itl_rus: "Ительменско-русский словарь",
    }


DICTIONARIES = dict(
    (val, key) for key, val in LangPairs.pair_names.items()
)

DEFAULT_DICTIONARY = "Русско-ительменский словарь"

MATCHES = {"Полное совпадение": True, "Частичное совпадение": False}
DEFAULT_MATCH = "Полное совпадение"