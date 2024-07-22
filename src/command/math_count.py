import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG


def get_math_count_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info("math_count")

    words = msg.split()
    return textwrap.dedent(
        f"""
        ```
        {str(len(words))}
        {terminal_mode.current_path()}
        ```
        """
    )
