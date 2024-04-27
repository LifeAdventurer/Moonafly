import subprocess
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG, TAB_SIZE


def get_syntax_highlighting_language_code(terminal_output: str) -> str:
    if all(token in terminal_output for token in ['---', '+++', '@@']):
        return 'patch'

    return 'markdown'


def get_remote_terminal_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('remote_terminal')

    if msg.startswith('\\'):
        msg = msg[1:]
    space = '\n' + ' ' * TAB_SIZE * 3
    try:
        result = subprocess.check_output(
            msg, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        )
        language_code = get_syntax_highlighting_language_code(result)
        if result:
            result = space.join(result.splitlines())
            result = f"```{language_code}{space}{result}{space}```"
        return textwrap.dedent(
            f"""
            {result}
            ```
            {terminal_mode.current_path()}
            ```
            """
        )
    except subprocess.CalledProcessError as e:
        space += '- '
        error = space.join(e.output.splitlines())
        return textwrap.dedent(
            f"""
            ```diff
            - {error}
            ```
            ```
            {terminal_mode.current_path()}
            ```
            """
        )
