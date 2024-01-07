import terminal_mode


import textwrap


def load_help_cmd_info(command: str) -> str:
    space = ' ' * 4 * 2
    path_to_txt = f"../data/txt/help_cmd_info/{command}.txt"

    with open(path_to_txt, 'r') as information_file:
        lines = information_file.readlines()

    information = '\n'.join(
        [
            space + line.rstrip() if index > 0 else line.rstrip() 
            for index, line in enumerate(lines)
        ]
    )
    return textwrap.dedent(f"""\
        ```
        {information}
        {terminal_mode.current_path()}
        ```
    """)