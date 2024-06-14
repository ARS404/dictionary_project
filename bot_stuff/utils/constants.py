class LangPairs(object):
    rus_udm = ("rus", "udm")
    udm_rus = ("udm", "rus")
    rus_itl = ("rus", "itl")
    itl_rus = ("itl", "rus")
    # may be extended

    pair_names = {
        rus_udm: "Русско-удмуртский словарь",
        udm_rus: "Удмуртско-русский словарь",
        rus_itl: "rus-itl",
        itl_rus: "itl-rus",
    }
    

DICTIONARIES = dict(
    (val, key) for key, val in LangPairs.pair_names.items()
)

DEFAULT_DICTIONARY = "itl-rus"

MATCHES = {"Полное совпадение": True, "Частичное совпадение": False}
DEFAULT_MATCH = "Полное совпадение"