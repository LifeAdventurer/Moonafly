import terminal_mode


import textwrap


def load_remote_file(filename: str) -> str:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        parts = filename.split('.')
        global file_language

        file_language = parts[-1] if len(parts) > 1 else ''
        indentation = ' ' * 4 * 3
        output = '\n'
        content = content.splitlines()
        lines_str_len = len(str(len(content)))

        for index, line in enumerate(content):
            output += f"{indentation}{(' ' * lines_str_len + str(index + 1))[-lines_str_len:]}│ {line}\n"

        return textwrap.dedent(f"""\
            ```
            {filename}
            ```
            ```{file_language}
            {output}
            ```
            ```
            {terminal_mode.current_path()}
            ```
        """)

    except FileNotFoundError:
        return textwrap.dedent(f"""\
            ```
            remote: File "{filename}" not found.
            {terminal_mode.current_path()}
            ```
        """)