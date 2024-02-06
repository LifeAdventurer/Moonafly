import terminal_mode


from command import command_help


import textwrap
from googletrans import Translator


# Constants
TAB_SIZE = 4
HELP_FLAG = '--help'


def get_translated_text(msg: str) -> str:

    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('translate')

    return textwrap.dedent(f"""
        ```
        {Translator().translate(msg, src='en', dest='zh-tw').text}
        {terminal_mode.current_path()}
        ```
    """)