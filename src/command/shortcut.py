import json
import re
import textwrap

import responses
import terminal_mode
from command import command_help
from constants import HELP_FLAG


def load_user_shortcuts() -> dict:
    try:
        with open('../data/json/user_shortcuts.json', 'r') as file:
            user_shortcuts = json.load(file)
    except FileNotFoundError:
        user_shortcuts = {}
        with open('../data/json/user_shortcuts.json', 'w') as file:
            json.dump(user_shortcuts, file, indent=4)

    return user_shortcuts


def write_user_shortcuts(user_shortcuts: dict):
    with open('../data/json/user_shortcuts.json', 'w') as file:
        json.dump(user_shortcuts, file, indent=4)


def set_shortcut(msg: str) -> str:
    pattern = r'^"(.+?)"\s+to\s+"(.+?)"$'

    match = re.match(pattern, msg)
    if match:
        replace_string = match.group(1)
        shortcut_string = match.group(2)

        user_shortcuts = load_user_shortcuts()
        username = responses.terminal_mode_current_using_user
        user_shortcuts.setdefault(username, {})
        user_shortcuts[username][shortcut_string] = replace_string
        write_user_shortcuts(user_shortcuts)

        return textwrap.dedent(
            f"""
            ```
            set successfully
            {terminal_mode.current_path()}
            ```
            """
        )
    else:
        return terminal_mode.handle_command_error('set', 'format')


def get_shortcut_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('shortcut')

    if msg.startswith('set'):
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('shortcut_set')

        return set_shortcut(msg)

    return terminal_mode.command_not_found(msg)
