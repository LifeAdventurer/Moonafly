import responses


from cmd import remote
from cmd import tree
from cmd import command_help

from cmd import dict
from cmd import weather
from cmd import math_calc
from cmd import random_vocab_test
from cmd import game_1A2B
from cmd import clipboard


import json
import random
import requests
import os
import re
import textwrap
import time
# from typing import Dict


terminal_mode_directory_structure = []
# initialed when bot started via init_files() in `bot.py`
def load_terminal_mode_directory_structure():
    global terminal_mode_directory_structure
    with open('../data/json/terminal_mode_directory_structure.json') as file:
        terminal_mode_directory_structure = json.load(file)['structure']


Moonafly_structure = []
# initialed when bot started via init_files() in `bot.py`
def load_Moonafly_structure():
    global Moonafly_structure
    with open('../data/json/Moonafly_structure.json') as file:
        Moonafly_structure = json.load(file)['structure']


def command_not_found(msg: str) -> str:
    space = ' ' * 4 * 2
    # unify the indentation of multiline
    msg = '\n'.join(
        [
            space + line if index > 0 else line
            for index, line in enumerate(msg.split('\n'))
        ]
    )
    return textwrap.dedent(f"""
        ```
        {msg}: command not found
        {current_path()}
        ```
    """)


def function_developing() -> str:
    return textwrap.dedent(f"""
        ```
        sorry, this function is still developing
        {current_path()}
        ```
    """)


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
        column_len[column_index] = max(len(file_name) for file_name in grouped_files)

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
        random_vocab_test.random_vocab_testing
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
        # cd command
        if msg[:2] == 'cd':
            msg = msg[2:].lstrip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('cd')

            path = msg

            # blank or ~ should go directly to ~
            if path == '' or path == '~':
                path_stack = ['~']
                return f"```{current_path()}```"

            # go to the root directory
            if path[0] == '/' and username != responses.author:
                return textwrap.dedent(f"""
                    ```
                    permission denied
                    * this command requires the highest authority
                    {current_path()}
                    ```
                """)

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
                        space = ' ' * 4 * 7
                        # multi-line adjustment
                        msg = '\n'.join(
                            [
                                space + line if index > 0 else line
                                for index, line in enumerate(msg.split('\n'))
                            ]
                        )
                        return textwrap.dedent(f"""
                            ```
                            Moonafly: cd: {msg}: No such file or directory
                            {current_path()}
                            ```
                        """)

                else:
                    temporary_path_stack.append(folder)

            current_directory = terminal_mode_directory_structure

            for folder in temporary_path_stack:
                if folder in list(current_directory):
                    if folder == 'author':
                        if username == responses.author:
                            current_directory = current_directory[folder]
                        else:
                            return textwrap.dedent(f"""
                                ```
                                permission denied
                                your command path contains certain directory that requires the highest authority
                                {current_path()}
                                ```
                            """)
                    else:
                        current_directory = current_directory[folder]

                else:
                    # reverse the message to original command by removing the escape character
                    msg = msg.replace("\\'", "'").replace("\\\"", "\"")
                    space = ' ' * 4 * 6
                    # multi-line adjustment
                    msg = '\n'.join(
                        [
                            space + line if index > 0 else line
                            for index, line in enumerate(msg.split('\n'))
                        ]
                    )
                    return textwrap.dedent(f"""
                        ```
                        Moonafly: cd: {msg}: No such file or directory
                        {current_path()}
                        ```
                    """)

            path_stack = temporary_path_stack
            return f"```{current_path()}```"

        # ls command
        elif msg[:2] == 'ls':
            msg = msg[3:].lstrip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('ls')

            # copy the terminal_mode_directory_structure
            current_directory = terminal_mode_directory_structure
            # and move it to the current directory
            for folder in path_stack:
                current_directory = current_directory[folder]

            # sort the folders alphabetically
            files_in_current_directory = sorted(list(current_directory))
            if username != responses.author and 'author' in files_in_current_directory:
                files_in_current_directory.remove('author')

            return textwrap.dedent(f"""
                ```
                {get_ls_command_output(files_in_current_directory, 4, 4)}
                {current_path()}
                ```
            """)

        # return the full pathname of the current working directory
        elif msg[:3] == 'pwd':
            msg = msg[3:].lstrip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('pwd')

            # delete the prefix 'Moonafly:' and the suffix '$'
            path = current_path()[(10 + len(username)):-1]
            # delete the prefix no matter it is '~' or '/' path_stack still has the data
            path = path[1:]
            
            if path_stack[0] == '~':
                path = 'home/Moonafly' + path

            return textwrap.dedent(f"""
                ```
                /{path}
                {current_path()}
                ```
            """)

        # show the terminal_mode_directory_structure
        elif msg[:4] == 'tree':
            msg = msg[4:].lstrip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('tree')

            if msg[:8] == 'Moonafly' and username == responses.author:
                return tree.visualize_structure(Moonafly_structure, 'terminal', username)

            # copy the directory structure
            current_structure = terminal_mode_directory_structure
            # and move it to the current directory
            for folder in path_stack:
                current_structure = current_structure[folder]

            return tree.visualize_structure(current_structure, 'terminal', username)

        elif msg[:4] == 'help':
            msg = msg[4:].lstrip()
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('help')

            return textwrap.dedent(f"""
                ```
                Moonafly, version {responses.Moonafly_version}
                
                - normal mode
                - terminal mode (current)
                - develop mode

                a star(*) in front of the command means that it requires the highest authority

                 cd [dir]
                 help
                 ls
                 pwd
                 tree [-M]
                {current_path()}
                ```
            """)

    # only author can access this part
    if len(path_stack) > 1 and path_stack[1] == 'author':
        if len(path_stack) > 2 and path_stack[2] == 'remote':
            if len(path_stack) > 3 and path_stack[3] == 'file':
                if msg[:6] == '--help':
                    return command_help.load_help_cmd_info('remote_file')

                return remote.load_remote_file(msg, 'author')

    # commands in certain directory
    if len(path_stack) > 1 and path_stack[1] == 'math':
        if path_stack[-1] == 'calc':
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('math_calc')

            return textwrap.dedent(f"""
                ```
                {math_calc.safe_eval(msg)}
                {current_path()}
                ```
            """)

        elif path_stack[-1] == 'count':
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('math_count')

            words = msg.split()
            return textwrap.dedent(f"""
                ```
                {str(len(words))}
                {current_path()}
                ```
            """)


    elif len(path_stack) > 1 and path_stack[1] == 'clipboard':
        return clipboard.get_clipboard_response(message)

    
    elif len(path_stack) > 1 and path_stack[1] == 'search':
        # search for a handle in different online judges
        if len(path_stack) > 2 and path_stack[2] == 'online-judge':
            # -{number} handle
            # search for certain pattern
            pattern = r'^-(\d+)\s+(\w+)$'
            match = re.search(pattern, msg)

            if match:
                number = int(match.group(1))
                handle = match.group(2)
                url = ""
                # TODO: make this as a file or at least a list
                if number == 1:
                    url = "https://atcoder.jp/users/"
                elif number == 2:
                    url = "https://www.codechef.com/users/"
                elif number == 3:
                    url = "https://codeforces.com/profile/"
                elif number == 4:
                    url = "https://csacademy.com/user/"
                elif number == 5:
                    url = "https://dmoj.ca/user/"
                elif number == 6:
                    url = "https://leetcode.com/"
                elif number == 7:
                    url = "https://profiles.topcoder.com/"
                else:
                    return textwrap.dedent(f"""
                        ```
                        please enter a valid number
                        {current_path()}
                        ```
                    """)

                url += handle
                response = requests.get(url)
                if response.status_code == 404:
                    return textwrap.dedent(f"""
                        ```
                        The handle {handle} is not found
                        {current_path()}
                        ```
                    """)

                else:
                    return textwrap.dedent(f"""
                        {url}
                        ```
                        {current_path()}
                        ```
                    """)

            else:
                return textwrap.dedent(f"""
                    ```
                    please type the right command format, using help to see what are the available options
                    {current_path()}
                    ```
                """)

        # search for github repos or profiles -> because url
        elif len(path_stack) > 2 and path_stack[2] == 'github':
            github_url = "https://github.com/" + msg
            response = requests.get(github_url)
            if response.status_code == 404:
                return textwrap.dedent(f"""
                    The url {github_url} is not found (404 Not Found).
                    ```
                    {current_path()}
                    ```
                """)

            else:
                return textwrap.dedent(f"""
                    {github_url}
                    ```
                    {current_path()}
                    ```
                """)

        # search for git commands
        elif len(path_stack) > 2 and path_stack[2] == 'git':
            # msg = msg[4:]
            # if msg[:2] == 'ls':
            #     return textwrap.dedent(f"""\
            #         ```
            #         setup              -1
            #         init               -2
            #         stage & snapshot   -3  
            #         branch & merge     -4
            #         inspect & compare  -5
            #         share & update     -6
            #         {current_path()}
            #         ```
            #     """)

            # pattern = r'^-(\d+)\s+(\w+)$'
            # match = re.search(pattern, msg)
            # if match:
            #     number = int(match.group(1))
            #     command = match.group(2)

            # msg = msg[1:]
            # if msg > '6' or msg < '1':
            #     return 'no such command'
            # else:
                return function_developing()
            # TO-DO
            # elif msg == 'setup':
    
    elif len(path_stack) > 1 and path_stack[1] == 'weather':
        if msg[:6] == '--help':
            return command_help.load_help_cmd_info('weather')
            
        if msg == 'get':
            return weather.get_weather_info()

        else:
            return command_not_found(msg)

    # roll a random number
    elif len(path_stack) > 1 and path_stack[1] == 'random':
        if len(path_stack) > 2 and path_stack[2] == 'number':
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('random_number')

            if msg.isdigit():
                return textwrap.dedent(f"""
                    ```
                    {random.randint(1, int(msg))}
                    {current_path()}
                    ```
                """)

            else:
                return textwrap.dedent(f"""
                    ```
                    please enter a valid number
                    {current_path()}
                    ```
                """)
        
        elif len(path_stack) > 2 and path_stack[2] == 'vocab':
            if len(path_stack) > 3 and path_stack[3] == 'test':
                if msg[:6] == '--help':
                    return command_help.load_help_cmd_info('random_vocab_test')

                return random_vocab_test.get_random_vocab_test(message)


    # return the definition and example of the enter word from a dictionary
    elif len(path_stack) > 1 and path_stack[1] == 'dict':
        # different languages
        # en
        if len(path_stack) > 2 and path_stack[2] == 'en':
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('dict_en')

            # LIMIT example count
            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return textwrap.dedent(f"""
                    {dict.search_dict('en', match.group(1), int(match.group(2)), 4, 5)}
                    ```
                    {current_path()}
                    ```
                """)
            elif 'LIMIT' in msg:
                return textwrap.dedent(f"""
                    ```
                    please type a number after the command LIMIT
                    {current_path()}
                    ```
                """)
            else:
                return textwrap.dedent(f"""
                    {dict.search_dict('en', msg, 3, 4, 5)}
                    ```
                    {current_path()}
                    ```
                """)

        # en-zh_TW
        elif len(path_stack) > 2 and path_stack[2] == 'en-zh_TW':
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('dict_en-zh_TW')

            # LIMIT example count
            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return textwrap.dedent(f"""
                    {dict.search_dict('en-zh_TW', match.group(1), int(match.group(2)), 4, 5, username)}
                    ```
                    {current_path()}
                    ```
                """)
            elif 'LIMIT' in msg:
                return textwrap.dedent(f"""
                    ```
                    please type a number after the command LIMIT
                    {current_path()}
                    ```
                """)
            else:
                return textwrap.dedent(f"""
                    {dict.search_dict('en-zh_TW', msg, 3, 4, 5, username)}
                    ```
                    {current_path()}
                    ```
                """)
    
    # games
    elif len(path_stack) > 1 and path_stack[1] == 'game':
        if len(path_stack) > 2 and path_stack[2] == '1A2B':
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('game_1A2B')

            return game_1A2B.play_game_1A2B(message)

    else:
        return command_not_found(msg)