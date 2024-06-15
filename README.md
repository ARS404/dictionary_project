# Dictionary Bot

___

## Что в этом репозитории?

Данный репозиторий посвящен проекту по созданию удобного и расширяемого Telegram бота для работы со словарями малоресурсных языков. Репозиторий содержит исходный код полного пайплайна для удобной работы с произвольным словарем, начиная с парсера данных из формата XML и заканчивая реализацией асихронного бота с легким и комфортным для пользователя интерфейса.

Ссылка на бота:
https://t.me/Dictiory_bot

## Содержание
1. [Установка](#установка)
2. [Расширение](#расширение)
3. [Использование](#использование)

### Установка
Для запуска данного бота на собственной системе необходимо склонировать данный репозиторий, а затем настроить среду окружения.
Для корректной работы бота следует установить все необходимые зависимости при помощи выполнения из папки проекта команды

```shell
pip install -r requirements.txt
```

Также необходимо проинициализировать в среде окружения переменную `TOKEN` собственным токеном TelegramBotAPI, а также проинициализировать переменную `BOT_LOG_FILE` путем к файлу для логирования технических сообщений бота.

После данных шагов бот может быть запущен в работу при помощи выполнения команды
```shell
python3 bot_stuff/bot.py
```

### Расширение

Для расширения текущей библиотеки доступных словарей необходимо добавть в директорию `data/dictionaries` файл расширения `.xml` с названием `source-target.xml`, где `source` и `target` - ISO 639-3 коды исходного и целевого языков словаря соответственно.
После этого необходимо изменить файл `bot_stuff/utils/constants.py`, добавив в класс LangPairs новое поле со значением `('source', 'target')` и положив по ключу данного поля в `dict` `pair_names` название нового словаря, которое будет отображаться пользователю.

Пример данных манипуляций:

```python3

class LangPairs(object):
	...
+   new_dictionary = ('src', 'tgt')

    pair_names = {
    	...
+   	new_dictionary: 'Сорско-таргетский словарь'
    }

```

Для обновления списка доступных алфавитов необходимо выполнить команду

```shell
python3 bot_stuff/parse_alpha.py
```


### Использование

Бот реагирует на текстовые сообщения, отправленные пользователем, выполняя поиск считанного текста в текущем словаре. После выполнения поиска бот ответит пользователю сообщением с найденными результатами.

Для выбора текущего словаря используется команда `/Dictionaries`. Для настройки параметров поиска используется команда `/Settings`. Для упрощенного ввода некириллических символов доступны команды `/Alphabet` и `/Alphabet_special` для получения полного списка символов или списка специальных символов алфавита исходного языка текущего словаря.
