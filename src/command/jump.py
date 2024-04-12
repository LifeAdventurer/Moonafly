import textwrap

import develop_mode
import responses
import terminal_mode
from command import command_help
from constants import HELP_FLAG

path_stack = []


def traverse(data: dict, target_folder: str, bypass: list) -> bool:
    if len(data) == 0:
        return False
    for key, value in sorted(data.items()):
        if key in bypass:
            continue

        path_stack.append(key)
        if key == target_folder or (
            target_folder[-1] == '>' and key.startswith(target_folder[:-1])
        ):
            return True
        if traverse(value, target_folder, bypass) == True:
            return True
        path_stack.pop()

    return False


def jump_to_folder(msg: str) -> str:

    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('jump')

    global path_stack

    current_path = ''
    bypass = []

    if responses.is_terminal_mode == True:
        directory = terminal_mode.load_terminal_mode_directory_structure()

        if responses.terminal_mode_current_using_user != responses.author:
            bypass.append('author')

        if traverse(directory, msg, bypass) == True:
            terminal_mode.path_stack = path_stack
            current_path = terminal_mode.current_path()
        else:
            path_stack = []
            return textwrap.dedent(
                f"""
                ```
                jump: {msg}: No such file or directory
                {terminal_mode.current_path()}
                ```
                """
            )

    elif responses.is_develop_mode == True:
        directory = develop_mode.load_develop_mode_directory_structure()

        if traverse(directory, msg, bypass) == True:
            develop_mode.path_stack = path_stack

            current_path = develop_mode.current_path()
        else:
            path_stack = []
            return textwrap.dedent(
                f"""
                ```
                jump: {msg}: No such file or directory
                {develop_mode.current_path()}
                ```
                """
            )

    path_stack = []
    return textwrap.dedent(
        f"""
        ```
        {current_path}
        ```
        """
    )
