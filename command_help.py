def load_help_command_information(command, tab_size, tab_count) -> str:
    information = ''
    space = ' ' * tab_size * tab_count
    path_to_txt = f"./data/txt/help_commands_information/{command}.txt"

    with open(path_to_txt, 'r') as information_file:
        lines = information_file.readlines()

    information = '\n'.join([space + line.rstrip() if index > 0 else line.rstrip() for index, line in enumerate(lines)])
    
    return information