import json
import re
import textwrap

import develop_mode
import terminal_mode
from command import command_help

# constants
TAB_SIZE = 4


on_remote = False


def load_Moonafly_structure() -> dict:
    with open('../data/json/Moonafly_structure.json') as file:
        return json.load(file)['structure']


allowed_paths = []
Moonafly_path_stack = []


def load_allowed_paths(data: dict):
    # just make sure the structure file is always a dict
    if len(data) == 0:
        allowed_paths.append('/'.join(Moonafly_path_stack))
    for key, value in sorted(data.items()):
        Moonafly_path_stack.append(key)
        load_allowed_paths(value)
        Moonafly_path_stack.pop()


def load_remote_file(msg: str, identity: str) -> str:

    global on_remote

    current_path = ''
    if identity == 'author':
        current_path = terminal_mode.current_path()
    elif identity == 'developer':
        current_path = develop_mode.current_path()

    r_file_path = re.compile(r'^([^ ]+)$')
    r_file_path_start_end = re.compile(r'^([^ ]+)\s+(\d+)\.\.(\d+)$')

    file_path = ''
    start_line = 0
    end_line = 10**9

    if r_file_path.match(msg):
        file_path = r_file_path.match(msg).group(1)

    elif r_file_path_start_end.match(msg):
        match = r_file_path_start_end.match(msg)
        file_path = match.group(1)
        start_line = int(match.group(2))
        end_line = int(match.group(3))

        if end_line < start_line:
            return textwrap.dedent(
                f"""
                ```
                end line should be large than start line
                {current_path}
                ```
                """
            )

    else:
        return command_help.load_help_cmd_info('remote_file')

    try:
        if identity == 'author':
            with open('../' + file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        elif identity == 'developer':
            load_allowed_paths(load_Moonafly_structure())

            if file_path in allowed_paths:
                with open('../' + file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            else:
                return textwrap.dedent(
                    f"""
                    ```
                    remote: You don't have permission to access file "{file_path}".
                    {current_path}
                    ```
                    """
                )

        parts = file_path.split('.')

        global file_language
        file_language = parts[-1] if len(parts) > 1 else ''

        output = []
        content = content.splitlines()
        lines_str_len = len(str(len(content)))

        for index, line in enumerate(content):
            if start_line <= index + 1 <= end_line:
                output.append(f"{str(index + 1).rjust(lines_str_len)}│ {line}")

        output = ('\n' + ' ' * TAB_SIZE * 3).join(output)

        on_remote = True

        return textwrap.dedent(
            f"""
            ```
            {file_path}
            ```
            ```{file_language}
            {output}
            ```
            ```
            {current_path}
            ```
            """
        )

    except FileNotFoundError:
        return textwrap.dedent(
            f"""
            ```
            remote: File "{file_path}" not found.
            {current_path}
            ```
            """
        )
