import calendar
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG, TAB_SIZE


def load_calendar(year: int, month: int) -> str:
    cal = calendar.month(year, month)
    space = "\n" + " " * TAB_SIZE * 2
    return textwrap.dedent(
        f"""
        ```
        {space.join(cal.splitlines())}
        ```
        ```
        {terminal_mode.current_path()}
        ```
        """
    )


def get_calendar_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info("calendar")

    if msg.startswith("get"):
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info("calendar_get")

        split_msg = msg.split("/")
        if len(split_msg) != 2:
            return terminal_mode.handle_command_error("get", "format", msg)

        try:
            year, month = map(int, split_msg)
        except ValueError:
            return terminal_mode.handle_command_error("get", "format", msg)

        return load_calendar(year, month)

    else:
        return terminal_mode.command_not_found(msg)
