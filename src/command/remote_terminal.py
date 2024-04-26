import subprocess
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG, TAB_SIZE


def get_remote_terminal_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('remote_terminal')

    space = '\n' + ' ' * TAB_SIZE * 3
    try:
        result = subprocess.check_output(
            msg, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        )
        result = space.join(result.splitlines())
        return textwrap.dedent(
            f"""
            ```
            {result}
            {terminal_mode.current_path()}
            ```
            """
        )
    except subprocess.CalledProcessError as e:
        error = space.join(e.output.splitlines())
        return textwrap.dedent(
            f"""
            ```
            error: {error}
            {terminal_mode.current_path()}
            ```
            """
        )
