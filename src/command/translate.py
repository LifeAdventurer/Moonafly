import textwrap

from googletrans import LANGUAGES, Translator

import terminal_mode
from command import command_help

# Constants
TAB_SIZE = 4
HELP_FLAG = '--help'


def show_languages(line_length=80, columns=3) -> str:
    column_width = [0] * columns

    for index, (code, language) in enumerate(LANGUAGES.items()):
        column_width[index % columns] = max(
            column_width[index % columns], len(f"{code}: {language}  ")
        )

    lang_lines = []
    line = ""
    for index, (code, language) in enumerate(LANGUAGES.items()):
        if index % columns == 0:
            lang_lines.append(line)
            line = ""

        code_lang_str = f"{code}: {language}"
        line += code_lang_str + ' ' * (
            column_width[index % columns] - len(code_lang_str)
        )

    lang_lines.append(line)
    lang_lines = ('\n' + ' ' * TAB_SIZE * 2).join(lang_lines)

    return textwrap.dedent(
        f"""\
        ```
        {lang_lines}
        {terminal_mode.current_path()}
        ```
    """
    )


def get_translated_text(msg: str) -> str:

    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('translate')

    if msg[:4] == 'show':
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('translate_show')

        return show_languages()

    return textwrap.dedent(
        f"""
        ```
        {Translator().translate(msg, src='en', dest='zh-tw').text}
        {terminal_mode.current_path()}
        ```
    """
    )
