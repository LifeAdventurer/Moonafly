import terminal_mode


import textwrap
import os


on_remote = False
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


def load_remote_file(file_path: str, identity: str, username: str = None) -> str:

    global on_remote

    remote_status = ''
    if identity == 'author':
        remote_status = terminal_mode.current_path()
    elif identity == 'developer':
        remote_status = f"{username}@Moonafly: using remote"

    try:
        if identity == 'author':
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        elif identity == 'developer':
            load_allowed_paths(terminal_mode.Moonafly_structure)

            if file_path in allowed_paths:
                with open('../' + file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            else:
                return textwrap.dedent(f"""\
                    ```
                    remote: You don't have permission to access file "{file_path}".
                    {remote_status}
                    ```
                """)

        parts = file_path.split('.')
        global file_language

        file_language = parts[-1] if len(parts) > 1 else ''
        indentation = ' ' * 4 * 3
        output = '\n'
        content = content.splitlines()
        lines_str_len = len(str(len(content)))

        for index, line in enumerate(content):
            output += f"{indentation}{(' ' * lines_str_len + str(index + 1))[-lines_str_len:]}│ {line}\n"

        on_remote = True

        return textwrap.dedent(f"""\
            ```
            {file_path}
            ```
            ```{file_language}
            {output}
            ```
            ```
            {remote_status}
            ```
        """)

    except FileNotFoundError:
        return textwrap.dedent(f"""\
            ```
            remote: File "{file_path}" not found.
            {remote_status}
            ```
        """)