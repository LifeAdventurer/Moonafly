import json
import random
import textwrap

import responses
import terminal_mode
from command import command_help

# Constants
HELP_FLAG = '--help'

random_vocab_testing = False
vocab_index = 0
previous_index = -1


def load_vocabulary_items() -> dict:
    try:
        with open(
            '../data/json/vocabulary_items.json', 'r', encoding='utf-8'
        ) as file:
            vocabulary_items = json.load(file)
    except FileNotFoundError:
        vocabulary_items = {}
        with open(
            '../data/json/vocabulary_items.json', 'w', encoding='utf-8'
        ) as file:
            json.dump(vocabulary_items, file, indent=4)

    return vocabulary_items


def write_vocabulary_items(vocabulary_items):
    with open(
        '../data/json/vocabulary_items.json', 'w', encoding='utf-8'
    ) as file:
        json.dump(vocabulary_items, file, indent=4, ensure_ascii=False)


def get_random_vocab_test(msg) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('random_vocab_test')

    global random_vocab_testing, vocab_index, previous_index

    vocabulary_items = load_vocabulary_items()
    username = responses.terminal_mode_current_using_user

    if msg.lower() == 'g':
        if username in vocabulary_items:
            list_len = len(vocabulary_items[username])
            if list_len == 0:
                return textwrap.dedent(
                    f"""
                    ```
                    You have cleared all the words.
                    {terminal_mode.current_path()}
                    ```
                    """
                )
            else:
                random_vocab_testing = True

                random_index = random.randint(0, list_len - 1)
                while list_len > 1 and random_index == previous_index:
                    random_index = random.randint(0, list_len - 1)

                previous_index = vocab_index
                vocab_index = random_index

                write_vocabulary_items(vocabulary_items)

                return textwrap.dedent(
                    f"""
                    ```
                    {vocabulary_items[username][vocab_index]['word']}
                    ```
                    """
                )

        else:
            return textwrap.dedent(
                f"""
                ```
                You have never use dict feature before. 
                Try it to save vocabulary items in Moonafly, then
                use ~/random/vocab/test to examine yourself
                {terminal_mode.current_path()}
                ```
                """
            )

    elif random_vocab_testing:
        if msg in vocabulary_items[username][vocab_index]['word_in_zh_TW']:
            random_vocab_testing = False

            vocabulary_items[username][vocab_index]['count'] -= 1
            word = vocabulary_items[username][vocab_index]['word']
            word_in_zh_TW = vocabulary_items[username][vocab_index][
                'word_in_zh_TW'
            ]

            if vocabulary_items[username][vocab_index]['count'] == 0:
                del vocabulary_items[username][vocab_index]

            write_vocabulary_items(vocabulary_items)

            return textwrap.dedent(
                f"""
                ```
                Correct!
                {word}
                {word_in_zh_TW}
                {terminal_mode.current_path()}
                ```
                """
            )

        else:
            random_vocab_testing = False
            vocabulary_items[username][vocab_index]['count'] += 1
            word = vocabulary_items[username][vocab_index]['word']
            word_in_zh_TW = vocabulary_items[username][vocab_index][
                'word_in_zh_TW'
            ]

            write_vocabulary_items(vocabulary_items)

            return textwrap.dedent(
                f"""
                ```
                Oops! Wrong answer
                {word}
                {word_in_zh_TW}
                {terminal_mode.current_path()}
                ```
                """
            )

    else:
        return terminal_mode.command_not_found(msg)
