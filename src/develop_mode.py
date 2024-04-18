import json
import re
import textwrap

import bot
import responses
from command import command_help, issues, jump, maintenance, remote_file, tree
from constants import HELP_FLAG, TAB_SIZE


def load_develop_mode_directory_structure():
    with open('../data/json/develop_mode_directory_structure.json') as file:
        return json.load(file)['structure']


def load_Moonafly_structure() -> dict:
    with open('../data/json/Moonafly_structure.json') as file:
        return json.load(file)['structure']


def load_user_cloak() -> dict:
    try:
        with open('../data/json/user_cloak.json', 'r') as file:
            user_cloak = json.load(file)
    except FileNotFoundError:
        user_cloak = {'terminal_mode': {}, 'develop_mode': {}}
        with open('../data/json/user_cloak.json', 'w') as file:
            json.dump(user_cloak, file, indent=4)
    return user_cloak


def write_user_cloak(user_cloak: dict):
    with open('../data/json/user_cloak.json', 'w') as file:
        json.dump(user_cloak, file, indent=4)


def get_ls_command_output(files: list, tab_count: int) -> str:
    output = ""
    max_file_length = max(len(file) for file in files)
    terminal_width = 79
    min_column_width = max_file_length + 2

    columns = max(1, terminal_width // min_column_width)
    column_groups = [files[i : len(files) : columns] for i in range(columns)]
    column_widths = [
        max(len(file) for file in group) + 2 for group in column_groups
    ]

    for index, file in enumerate(files):
        group_index = index % columns
        output += file.ljust(column_widths[group_index])
        if group_index == columns - 1 and index != len(files) - 1:
            output += '\n' + ' ' * TAB_SIZE * tab_count

    return output


path_stack = []


def path_stack_match(index: int, cur_dir_name) -> bool:
    global path_stack
    return len(path_stack) > index and path_stack[index] == cur_dir_name


# generating the current working directory
def current_path() -> str:
    global path_stack
    # show the current using user
    path = f"{responses.develop_mode_current_using_user}@Moonafly:"
    for folder in path_stack:
        if folder != '~':
            path += '/'
        path += folder
    return path + "$"


def command_not_found(msg: str) -> str:
    msg = msg.replace("\\'", "'").replace("\\\"", "\"")
    space = ' ' * TAB_SIZE * 2
    # unify the indentation of multiline
    msg = '\n'.join(
        [
            space + line if index > 0 else line
            for index, line in enumerate(msg.split('\n'))
        ]
    )
    return textwrap.dedent(
        f"""
        ```
        {msg}: command not found
        {current_path()}
        ```
        """
    )


def permission_denied() -> str:
    return textwrap.dedent(
        f"""
        ```
        permission denied: requires highest authority
        {current_path()}
        ```
        """
    )


def handle_command_error(command: str, error_type: str, msg: str) -> str:
    error = ''
    if error_type == 'format':
        error = 'format error'
    elif error_type == 'path':
        path = msg.replace("\\'", "'").replace("\\\"", "\"")
        space = ' ' * TAB_SIZE * 2
        path = '\n'.join(
            [
                space + line if index > 0 else line
                for index, line in enumerate(path.split('\n'))
            ]
        )
        error = f"{path}: No such file or directory"
    return textwrap.dedent(
        f"""
        ```
        {command}: {error}
        {current_path()}
        ```
        """
    )


def check_path_exists(command: str, path: str) -> tuple[bool, list]:
    # Skip all the '\' and split the path into a folder list
    path = path.replace('\\', '').split('/')

    # Create a copy of the current path stack
    temporary_path_stack = path_stack.copy()

    for folder in path:
        if folder == '' or folder == '.':
            continue

        # move up one directory
        elif folder == '..':
            if len(temporary_path_stack) > 1:
                temporary_path_stack.pop()

            elif temporary_path_stack[0] == '~':
                return False, handle_command_error(
                    command, 'path', '/'.join(path)
                )

        else:
            temporary_path_stack.append(folder)

    current_directory = load_develop_mode_directory_structure()

    for folder in temporary_path_stack:
        if folder[-1] == '>':
            for item in list(current_directory):
                if item.startswith(folder[:-1]):
                    current_directory = current_directory[item]
                    temporary_path_stack[temporary_path_stack.index(folder)] = (
                        item
                    )
                    break

            else:
                return False, handle_command_error(
                    command, 'path', '/'.join(path)
                )

        elif folder in list(current_directory):
            if folder == 'author':
                if (
                    responses.develop_mode_current_using_user
                    == responses.author
                ):
                    current_directory = current_directory[folder]
                else:
                    return permission_denied()
            else:
                current_directory = current_directory[folder]

        else:
            return False, handle_command_error(command, 'path', '/'.join(path))

    return True, temporary_path_stack


async def get_response_in_develop_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global path_stack

    if msg == 'help':
        return textwrap.dedent(
            f"""
            ```
            Moonafly {responses.Moonafly_version}
            
            - normal mode
            - terminal mode 
            - develop mode (current)

             cd [dir]
             clear
             cloak {{+-}}h [dir]
             end
             exit [--save]
             help
             jump [folder]
             ls [-a]
             pwd
             set [time]
             tree [-aM]
            ```
            """
        )

    if msg.startswith('cd'):
        msg = msg[2:].lstrip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('cd')

        path = msg

        # blank or ~ should go directly to ~
        if path == '' or path == '~':
            path_stack = ['~']
            return f"```{current_path()}```"

        # go to the root directory
        if path[0] == '/' and username != responses.author:
            return permission_denied()

        exists, temporary_path_stack = check_path_exists('cd', path)

        if not exists:
            return temporary_path_stack

        path_stack = temporary_path_stack
        return f"```{current_path()}```"

    elif msg.startswith('clear'):
        msg = msg[5:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('clear')

        await bot.clear_msgs(message, responses.start_using_timestamp)
        return f"```{current_path()}```"

    elif msg.startswith('cloak'):
        msg = msg[5:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('cloak')

        pattern = r'^([+-])[h]\s*(.*)$'
        match = re.match(pattern, msg)
        if match:
            operation = match.group(1)
            path = match.group(2)

            exists, temporary_path_stack = check_path_exists('cloak', path)

            if not exists:
                return temporary_path_stack

            folder_name = temporary_path_stack[-1]
            user_cloak = load_user_cloak()
            user_develop_mode_cloak = user_cloak['develop_mode'].setdefault(
                username, []
            )
            if operation == '+':
                if folder_name not in user_develop_mode_cloak:
                    user_develop_mode_cloak.append(folder_name)
            else:
                if folder_name in user_develop_mode_cloak:
                    user_develop_mode_cloak.remove(folder_name)
            write_user_cloak(user_cloak)

            return textwrap.dedent(
                f"""
                ```
                folder '{folder_name}' has been successfully {'un' if operation == '-' else ''}hidden
                {current_path()}
                ```
                """
            )
        else:
            return handle_command_error('cloak', 'format', msg)

    elif msg.startswith('end'):
        msg = msg[4:].strip()
        return maintenance.end_maintenance(msg)

    elif msg.startswith('jump'):
        msg = msg[4:].strip()
        return jump.jump_to_folder(msg)

    elif msg.startswith('ls'):
        msg = msg[3:].lstrip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('ls')

        current_directory = load_develop_mode_directory_structure()
        # and move it to the current directory
        for folder in path_stack:
            current_directory = current_directory[folder]

        # sort the folders alphabetically
        files_in_current_directory = sorted(list(current_directory))
        if (
            username != responses.author
            and 'author' in files_in_current_directory
        ):
            files_in_current_directory.remove('author')

        if not msg.startswith("-a") and not msg.startswith("--all"):
            user_cloak = load_user_cloak()
            for folder in user_cloak['develop_mode'].get(username, []):
                if folder in files_in_current_directory:
                    files_in_current_directory.remove(folder)

        return textwrap.dedent(
            f"""
            ```
            {get_ls_command_output(files_in_current_directory, 4)}
            {current_path()}
            ```
            """
        )

    elif msg.startswith('pwd'):
        msg = msg[3:].lstrip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('pwd')

        # delete the prefix 'Moonafly:' and the suffix '$'
        path = current_path()[(10 + len(username)) : -1]
        # delete the prefix no matter it is '~' or '/' path_stack still has the data
        path = path[1:]

        if path_stack[0] == '~':
            path = 'home/Moonafly' + path

        return textwrap.dedent(
            f"""
            ```
            /{path}
            {current_path()}
            ```
            """
        )

    elif msg.startswith('set'):
        msg = msg[4:].strip()
        return maintenance.set_maintenance(msg)

    elif msg.startswith('tree'):
        msg = msg[4:].lstrip()

        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('tree')

        if msg.startswith('Moonafly'):
            return tree.visualize_structure(load_Moonafly_structure())

        # copy the directory structure
        current_structure = load_develop_mode_directory_structure()
        # and move it to the current directory
        for folder in path_stack:
            current_structure = current_structure[folder]

        if msg.startswith("-a") or msg.startswith("--all"):
            return tree.visualize_structure(current_structure, False)

        return tree.visualize_structure(current_structure)

    if path_stack_match(1, 'remote'):
        if path_stack_match(2, 'file'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('remote_file')

            return remote_file.load_remote_file(msg.strip(), 'developer')

    elif path_stack_match(1, 'issues'):
        return issues.get_issues(msg)

    else:
        return command_not_found(msg)
