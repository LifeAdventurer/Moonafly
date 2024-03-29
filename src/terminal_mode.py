import json
import os
import random
import re
import textwrap
import time

import requests

import responses
from command import (
    approve,
    clipboard,
    command_help,
    dict,
    game_1A2B,
    hash,
    jump,
    math_calc,
    news,
    online_judge,
    primes,
    random_vocab_review,
    random_vocab_test,
    remote,
    translate,
    tree,
    weather,
)

# from typing import Dict


# constants
HELP_FLAG = '--help'
TAB_SIZE = 4


def load_terminal_mode_directory_structure() -> dict:
    with open('../data/json/terminal_mode_directory_structure.json') as file:
        return json.load(file)['structure']


def load_Moonafly_structure() -> dict:
    with open('../data/json/Moonafly_structure.json') as file:
        return json.load(file)['structure']


def command_not_found(msg: str) -> str:
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


def function_developing() -> str:
    return textwrap.dedent(
        f"""
        ```
        sorry, this function is still developing
        {current_path()}
        ```
        """
    )


def get_ls_command_output(files: dict, tab_size: int, tab_count: int) -> str:
    output = ""
    columns = 3
    column_len = [0] * columns
    for column_index in range(min(columns, len(files))):
        # group the files with vertical lines and {columns} groups
        grouped_files = [
            file
            for index, file in enumerate(files)
            if index % columns == column_index
        ]
        column_len[column_index] = max(
            len(file_name) for file_name in grouped_files
        )

    for index, file in enumerate(files):
        output += file + ' ' * (
            column_len[index % columns] - len(file) + 2
            if index % columns != columns - 1
            else 0
        )
        if index % columns == columns - 1 and index != len(files) - 1:
            output += '\n' + ' ' * tab_size * tab_count

    return output


path_stack = []


def path_stack_match(index: int, cur_dir_name: str) -> bool:
    global path_stack
    return len(path_stack) > index and path_stack[index] == cur_dir_name


# generating the current working directory
def current_path() -> str:
    global path_stack
    # show the current using user
    path = f"{responses.terminal_mode_current_using_user}@Moonafly:"
    for folder in path_stack:
        if folder != '~':
            path += '/'
        path += folder
    return path + "$"


def in_interaction() -> bool:
    directory_statuses = [
        game_1A2B.playing_game_1A2B,
        clipboard.checking_clipboard_keyword_override,
        random_vocab_test.random_vocab_testing,
    ]
    return any(directory_statuses) == True


def get_response_in_terminal_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    # for directory
    global path_stack

    if in_interaction() == False:
        if msg[:4] == 'help':
            msg = msg[4:].lstrip()
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('help')

            return textwrap.dedent(
                f"""
                ```
                Moonafly, version {responses.Moonafly_version}
                
                - normal mode
                - terminal mode (current)
                - develop mode

                a star(*) in front of the command means that it requires the highest authority

                 cd [dir]
                 help
                 jump [folder]
                 ls
                 pwd
                 tree [-M]
                {current_path()}
                ```
                """
            )

        # cd command
        elif msg[:2] == 'cd':
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
                return textwrap.dedent(
                    f"""
                    ```
                    permission denied
                    * this command requires the highest authority
                    {current_path()}
                    ```
                    """
                )

            # skip all the '\' and split the path into a folder list
            path = path.replace('\\', '').split('/')

            # using [:] to prevent temporary_path_stack and path_stack affecting each other
            temporary_path_stack = path_stack[:]

            for folder in path:
                # if the folder is empty or . then nothing happens with the
                if folder == '' or folder == '.':
                    continue

                # move up one directory
                elif folder == '..':
                    if len(temporary_path_stack) > 1:
                        temporary_path_stack.pop()

                    elif temporary_path_stack[0] == '~':
                        # reverse the message to original command by removing the escape character
                        msg = msg.replace("\\'", "'").replace("\\\"", "\"")
                        space = ' ' * TAB_SIZE * 7
                        # multi-line adjustment
                        msg = '\n'.join(
                            [
                                space + line if index > 0 else line
                                for index, line in enumerate(msg.split('\n'))
                            ]
                        )
                        return textwrap.dedent(
                            f"""
                            ```
                            Moonafly: cd: {msg}: No such file or directory
                            {current_path()}
                            ```
                            """
                        )

                else:
                    temporary_path_stack.append(folder)

            current_directory = load_terminal_mode_directory_structure()

            for folder in temporary_path_stack:
                if folder[-1] == '>':
                    for item in list(current_directory):
                        if item.startswith(folder[:-1]):
                            current_directory = current_directory[item]
                            temporary_path_stack[
                                temporary_path_stack.index(folder)
                            ] = item
                            break

                    else:
                        return textwrap.dedent(
                            f"""
                            ```
                            Moonafly: cd: {msg}: No such file or directory
                            {current_path()}
                            ```
                            """
                        )

                elif folder in list(current_directory):
                    if folder == 'author':
                        if username == responses.author:
                            current_directory = current_directory[folder]
                        else:
                            return textwrap.dedent(
                                f"""
                                ```
                                permission denied
                                your command path contains certain directory that requires the highest authority
                                {current_path()}
                                ```
                                """
                            )
                    else:
                        current_directory = current_directory[folder]

                else:
                    # reverse the message to original command by removing the escape character
                    msg = msg.replace("\\'", "'").replace("\\\"", "\"")
                    space = ' ' * TAB_SIZE * 6
                    # multi-line adjustment
                    msg = '\n'.join(
                        [
                            space + line if index > 0 else line
                            for index, line in enumerate(msg.split('\n'))
                        ]
                    )
                    return textwrap.dedent(
                        f"""
                        ```
                        Moonafly: cd: {msg}: No such file or directory
                        {current_path()}
                        ```
                        """
                    )

            path_stack = temporary_path_stack
            return f"```{current_path()}```"

        elif msg[:4] == 'jump':
            msg = msg[4:].strip()
            return jump.jump_to_folder(msg)

        # ls command
        elif msg[:2] == 'ls':
            msg = msg[3:].lstrip()
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('ls')

            current_directory = load_terminal_mode_directory_structure()
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

            return textwrap.dedent(
                f"""
                ```
                {get_ls_command_output(files_in_current_directory, TAB_SIZE, 4)}
                {current_path()}
                ```
                """
            )

        # return the full pathname of the current working directory
        elif msg[:3] == 'pwd':
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

        # show the terminal_mode_directory_structure
        elif msg[:4] == 'tree':
            msg = msg[4:].lstrip()
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('tree')

            if msg[:8] == 'Moonafly' and username == responses.author:
                return tree.visualize_structure(load_Moonafly_structure())

            current_structure = load_terminal_mode_directory_structure()
            # and move it to the current directory
            for folder in path_stack:
                current_structure = current_structure[folder]

            return tree.visualize_structure(current_structure)

    # only author can access this part
    if path_stack_match(1, 'author'):
        if path_stack_match(2, 'approve'):
            return approve.approve_requests(msg)

        elif path_stack_match(2, 'remote'):
            if path_stack_match(3, 'file'):
                if msg.startswith(HELP_FLAG):
                    return command_help.load_help_cmd_info('remote_file')

                return remote.load_remote_file(msg, 'author')

    # commands in certain directory
    if path_stack_match(1, 'clipboard'):
        return clipboard.get_clipboard_response(message)

    elif path_stack_match(1, 'dict'):
        # different languages
        # en
        if path_stack_match(2, 'en'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('dict_en')

            # LIMIT example count
            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return textwrap.dedent(
                    f"""
                    {dict.search_dict('en', match.group(1), int(match.group(2)), TAB_SIZE, 5)}
                    ```
                    {current_path()}
                    ```
                    """
                )
            elif 'LIMIT' in msg:
                return textwrap.dedent(
                    f"""
                    ```
                    please type a number after the command LIMIT
                    {current_path()}
                    ```
                    """
                )
            else:
                return textwrap.dedent(
                    f"""
                    {dict.search_dict('en', msg, 3, TAB_SIZE, 5)}
                    ```
                    {current_path()}
                    ```
                    """
                )

        # en-zh_TW
        elif path_stack_match(2, 'en-zh_TW'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('dict_en-zh_TW')

            # LIMIT example count
            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return textwrap.dedent(
                    f"""
                    {dict.search_dict('en-zh_TW', match.group(1), int(match.group(2)), TAB_SIZE, 5, username)}
                    ```
                    {current_path()}
                    ```
                    """
                )
            elif 'LIMIT' in msg:
                return textwrap.dedent(
                    f"""
                    ```
                    please type a number after the command LIMIT
                    {current_path()}
                    ```
                    """
                )
            else:
                return textwrap.dedent(
                    f"""
                    {dict.search_dict('en-zh_TW', msg, 3, TAB_SIZE, 5, username)}
                    ```
                    {current_path()}
                    ```
                    """
                )

    # games
    elif path_stack_match(1, 'game'):
        if path_stack_match(2, '1A2B'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('game_1A2B')

            return game_1A2B.play_game_1A2B(message)

    elif path_stack_match(1, 'hash'):
        return hash.get_hash(msg)

    elif path_stack_match(1, 'math'):
        if path_stack_match(2, 'calc'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('math_calc')

            return textwrap.dedent(
                f"""
                ```
                {math_calc.safe_eval(msg)}
                {current_path()}
                ```
                """
            )

        elif path_stack_match(2, 'count'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('math_count')

            words = msg.split()
            return textwrap.dedent(
                f"""
                ```
                {str(len(words))}
                {current_path()}
                ```
                """
            )

        elif path_stack_match(2, 'primes'):
            return primes.get_primes_response(msg)

    elif path_stack_match(1, 'news'):
        return news.get_news(msg)

    # roll a random number
    elif path_stack_match(1, 'random'):
        if path_stack_match(2, 'number'):
            if msg.startswith(HELP_FLAG):
                return command_help.load_help_cmd_info('random_number')

            if msg.isdigit():
                return textwrap.dedent(
                    f"""
                    ```
                    {random.randint(1, int(msg))}
                    {current_path()}
                    ```
                    """
                )

            else:
                return textwrap.dedent(
                    f"""
                    ```
                    please enter a valid number
                    {current_path()}
                    ```
                    """
                )

        elif path_stack_match(2, 'vocab'):
            if path_stack_match(3, 'review'):
                return random_vocab_review.get_random_vocab_review(message)

            elif path_stack_match(3, 'test'):
                if msg.startswith(HELP_FLAG):
                    return command_help.load_help_cmd_info('random_vocab_test')

                return random_vocab_test.get_random_vocab_test(message)

    elif path_stack_match(1, 'search'):
        # search for github repos or profiles -> because url
        if path_stack_match(2, 'github'):
            github_url = "https://github.com/" + msg
            response = requests.get(github_url)
            if response.status_code == 404:
                return textwrap.dedent(
                    f"""
                    The url {github_url} is not found (404 Not Found).
                    ```
                    {current_path()}
                    ```
                    """
                )

            else:
                return textwrap.dedent(
                    f"""
                    {github_url}
                    ```
                    {current_path()}
                    ```
                    """
                )

        # search for a handle in different online judges
        elif path_stack_match(2, 'online-judge'):
            return online_judge.get_online_judge_info(msg)

    elif path_stack_match(1, 'translate'):
        return translate.get_translated_text(msg)

    elif path_stack_match(1, 'weather'):
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('weather')

        if msg == 'get':
            return weather.get_weather_info()

        else:
            return command_not_found(msg)

    else:
        return command_not_found(msg)
