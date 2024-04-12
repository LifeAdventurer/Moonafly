import random
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG


def get_random_number_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('random_number')

    if msg.isdigit():
        return textwrap.dedent(
            f"""
            ```
            {random.randint(1, int(msg))}
            {terminal_mode.current_path()}
            ```
            """
        )

    else:
        return textwrap.dedent(
            f"""
            ```
            please enter a valid number
            {terminal_mode.current_path()}
            ```
            """
        )
