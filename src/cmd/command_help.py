def load_help_command_information(command: str) -> str:
    information = ''
    space = ' ' * 4 * 2
    path_to_txt = f"../data/txt/help_commands_information/{command}.txt"

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
        {response_terminal.current_path()}
        ```
    """)