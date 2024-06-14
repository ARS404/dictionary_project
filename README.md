# Dictionary project

## Project info
Hmmm?

## Installation
For setting up this bot you only need to setup `venv` according to `requirements.txt`.

## Usage
### Bot interface
You can get all info in chat with bot.
### Possible extensions
This bot is designed to be easy extendable with other dictionaries. To do so you only have to:
- Add `.xml` file into `data/dictionaries` directory;
- Add Extend `LanguagePairs` class in `constants' file with new pair. **TODO: turn into config parameter**.

## TODO:
- Add partly match support
- Turn main part of constants into configuration parameters
- Handle cases with no predicted translations (may be we want to suggest some other variants of spelling)
- Optimize translation output (and probably `Answer` format) for specific types of dictionary lines (i.e. no example, few variants of translation, etc), especially `info` field
- Figure out what does "itl" mean (lol)
- Fill README