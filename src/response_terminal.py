import responses
from cmd.dict import search_dict
from cmd.weather import get_weather_info
from cmd.math_calc import safe_eval
from cmd.command_help import load_help_command_information

import json
import random
import requests
import os
import re
import textwrap
import time


directory_structure = []


# initialed when bot started via init_files() in `bot.py`
def load_directory_structure():
    global directory_structure
    with open('../data/json/directory_structure.json') as directory_structure_file:
        directory_structure = json.load(directory_structure_file)['directory_structure']


Moonafly_structure = []


# initialed when bot started via init_files() in `bot.py`
def load_Moonafly_structure():
    global Moonafly_structure
    with open('../data/json/Moonafly_structure.json') as Moonafly_structure_file:
        Moonafly_structure = json.load(Moonafly_structure_file)['Moonafly_structure']


def load_game_1A2B_ranks():
    global game_1A2B_ranks
    with open('../data/json/game_1A2B_ranks.json') as game_1A2B_ranks:
        game_1A2B_ranks = json.load(game_1A2B_ranks)

    return game_1A2B_ranks


def save_game_1A2B_result(length, attempts):
    # you must get the ranks every time due to the user might play several times
    records = load_game_1A2B_ranks()
    # set the group if there isn't one in the data
    records.setdefault(str(length), [])

    # save the record data including attempts, user, timestamp
    records[str(length)].append(
        {
            'attempts': attempts,
            'user': responses.current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
    )
    # sort the rank by attempts first then timestamp
    records[str(length)].sort(key=lambda x: (x['attempts'], x['timestamp']))

    rank = 0
    for record in records[str(length)]:
        # the first position of the next attempts = the last position of the user attempt + 1
        # which can match the rank starts with 0
        if record['attempts'] > attempts:
            break
        rank += 1

    # save the result to json file
    with open('.../data/json/game_1A2B_ranks.json', 'w') as game_1A2B_ranks:
        json.dump(records, game_1A2B_ranks, indent=4)

    return rank


def show_1A2B_every_length_ranking(tab_size, tab_count):
    records = load_game_1A2B_ranks()

    indentation = ' ' * tab_size * tab_count
    ranking = 'length | attempts | user\n' + indentation
    ranking += '------------------------\n'
    for length in range(4, 11):
        ranking += indentation + f"  {(' ' + str(length))[-2:]}"
        if len(records[str(length)]) == 0:
            ranking += '   | no data  | no data\n'
            continue

        ranking += f"   |    {('  ' + str(records[str(length)][0]['attempts']))[-max(3, len(str(length))):]}   | {records[str(length)][0]['user']}\n"

    return ranking


def show_1A2B_certain_length_ranking(length, tab_size, tab_count):
    records = load_game_1A2B_ranks()[str(length)]

    indentation = ' ' * tab_size * tab_count
    ranking = f"length - {length}\n{indentation}"
    if len(records) == 0:
        ranking += 'no data'
        return ranking

    ranking += 'attempts | user\n' + indentation
    ranking += '----------------\n'
    for index, record in enumerate(records):
        if index >= 10:
            break

        ranking += (
            indentation
            + f"  {('  ' + str(record['attempts']))[-max(3, len(str(length))):]}    | {record['user']}\n"
        )

    return ranking


def show_1A2B_certain_user_ranking(username, tab_size, tab_count):
    records = load_game_1A2B_ranks()

    indentation = ' ' * tab_size * tab_count
    ranking = f"user - {username}\n{indentation}"
    ranking += 'length | attempts\n' + indentation
    ranking += '-------------------\n'
    for length in range(4, 11):
        ranking += indentation + f"  {(' ' + str(length))[-2:]}"

        no_data = True
        for index, record in enumerate(records[str(length)]):
            if record['user'] == username:
                no_data = False
                ranking += f"   | {('  ' + str(record['attempts']))[-max(3, len(str(length))):]} (rank {index + 1})\n"
                break

        if no_data:
            ranking += '   |  no data\n'
            continue

    return ranking


def command_not_found(msg) -> str:
    space = ' ' * 4 * 2
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


def get_ls_command_output(files, tab_size, tab_count) -> str:
    output = ""
    columns = 3
    column_len = [0] * columns
    for column_index in range(min(columns, len(files))):
        # group the files with vertical lines and {columns} groups
        grouped_files = [
            file for index, file in enumerate(files) if index % columns == column_index
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


def visualize_structure(data, tab_size, tab_count, indent=0) -> str:
    tree = ""
    # just make sure the structure file is always a dict
    for key, value in sorted(data.items()):
        #           structure indentation     folder      output indentation
        tree += f"{' ' * tab_size * indent}\-- {key}\n{' ' * tab_size * tab_count}"
        tree += visualize_structure(value, tab_size, tab_count, indent + 1)
    return tree


path_stack = []


# generating the current working directory
def current_path() -> str:
    global path_stack
    # show the current using user
    path = f"{responses.current_using_user}@Moonafly:"
    for folder in path_stack:
        if folder != '~':
            path += '/'
        path += folder
    return path + "$"


# for game commands
playing_game_1A2B = False
target_number = ''
target_number_len = 0
attempts = 0
# for random vocab test
random_vocab_testing = False
vocab_index = 0


def get_response_in_terminal_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    # for directory
    global path_stack
    # for game commands
    global playing_game_1A2B, target_number, target_number_len, attempts
    # for random vocab test
    global random_vocab_testing, vocab_index

    # you can comment messages without digits during the game
    if playing_game_1A2B:
        if len(path_stack) > 2 and path_stack[2] == '1A2B':
            if (
                msg[:4] != 'stop'
                and msg[:4] != 'Stop'
                and not all(char.isdigit() for char in msg)
            ):
                return ''

    else:
        if msg[:3] == 'cat':
            msg = msg[3:].strip()

            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('cat', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            if username != responses.author:
                return textwrap.dedent(
                    f"""\
                    ```
                    permission denied
                    * this command requires the highest authority
                    {current_path()}
                    ```
                """
                )

            filename = msg
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()

                parts = filename.split('.')
                global file_language
                file_language = parts[-1] if len(parts) > 1 else ''
                indentation = ' ' * 4 * 5
                output = '\n'
                content = content.splitlines()
                lines_str_len = len(str(len(content)))
                for index, line in enumerate(content):
                    output += f"{indentation}{(' ' * lines_str_len + str(index + 1))[-lines_str_len:]}│ {line}\n"
                return textwrap.dedent(
                    f"""\
                    ```
                    {filename}
                    ```
                    ```{file_language}
                    {output}
                    ```
                    ```
                    {current_path()}
                    ```
                """
                )

            except FileNotFoundError:
                return textwrap.dedent(
                    f"""\
                    ```
                    Error: File "{filename}" not found.
                    {current_path()}
                    ```
                """
                )

        # cd command
        elif msg[:2] == 'cd':
            msg = msg[2:].lstrip()
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('cd', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            path = msg

            # blank or ~ should go directly to ~
            if path == '' or path == '~':
                path_stack = ['~']
                return f"```{current_path()}```"

            # go to the root directory
            if path[0] == '/' and username != responses.author:
                return textwrap.dedent(
                    f"""\
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
                        space = ' ' * 4 * 7
                        # multi-line adjustment
                        msg = '\n'.join(
                            [
                                space + line if index > 0 else line
                                for index, line in enumerate(msg.split('\n'))
                            ]
                        )
                        return textwrap.dedent(
                            f"""\
                            ```
                            Moonafly: cd: {msg}: No such file or directory
                            {current_path()}
                            ```
                        """
                        )

                else:
                    temporary_path_stack.append(folder)

            current_directory = directory_structure

            for folder in temporary_path_stack:
                if folder in list(current_directory):
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
                    return textwrap.dedent(
                        f"""\
                        ```
                        Moonafly: cd: {msg}: No such file or directory
                        {current_path()}
                        ```
                    """
                    )

            path_stack = temporary_path_stack
            return f"```{current_path()}```"

        # ls command
        elif msg[:2] == 'ls':
            msg = msg[3:].lstrip()
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('ls', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            # copy the directory_structure
            current_directory = directory_structure
            # and move it to the current directory
            for folder in path_stack:
                current_directory = current_directory[folder]

            # sort the folders alphabetically
            files_in_current_directory = sorted(list(current_directory))

            return textwrap.dedent(
                f"""\
                ```
                {get_ls_command_output(files_in_current_directory, 4, 4)}
                {current_path()}
                ```
            """
            )

        # return the full pathname of the current working directory
        elif msg[:3] == 'pwd':
            msg = msg[3:].lstrip()
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('pwd', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            # delete the prefix 'Moonafly:' and the suffix '$'
            path = current_path()[(10 + len(username)) : -1]
            # delete the prefix no matter it is '~' or '/' path_stack still has the data
            path = path[1:]

            if path_stack[0] == '~':
                path = 'home/Moonafly' + path

            return textwrap.dedent(
                f"""\
                ```
                /{path}
                {current_path()}
                ```
            """
            )

        # show the directory_structure
        elif msg[:4] == 'tree':
            msg = msg[4:].lstrip()
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('tree', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            if msg[:8] == 'Moonafly':
                return textwrap.dedent(
                    f"""
                    ```
                    {visualize_structure(Moonafly_structure, 4, 5)}
                    {current_path()}
                    ```
                """
                )

            # copy the directory structure
            current_structure = directory_structure
            # and move it to the current directory
            for folder in path_stack:
                current_structure = current_structure[folder]

            return textwrap.dedent(
                f"""
                ```
                {visualize_structure(current_structure, 4, 4)}
                {current_path()}
                ```
            """
            )

        elif msg[:4] == 'help':
            msg = msg[4:].lstrip()
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('help', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            return textwrap.dedent(
                f"""
                ```
                Moonafly, version {responses.project_version}
                
                a star(*) in front of the command means that it requires the highest authority

                *cat [file]
                 cd [dir]
                 help
                 ls 
                 pwd
                 tree
                {current_path()}
                ```
            """
            )

    # commands in certain directory
    if len(path_stack) > 1 and path_stack[1] == 'math':
        if path_stack[-1] == 'calc':
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('math_calc', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            return textwrap.dedent(
                f"""
                ```
                {safe_eval(msg)}
                {current_path()}
                ```
            """
            )

        elif path_stack[-1] == 'count':
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('math_count', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            words = msg.split()
            return textwrap.dedent(
                f"""
                ```
                {str(len(words))}
                {current_path()}
                ```
            """
            )

    elif len(path_stack) > 1 and path_stack[1] == 'gen':
        # my generators repo on github.io
        if path_stack[-1] == 'fortune':
            if msg == 'get':
                return textwrap.dedent(
                    f"""
                    https://lifeadventurer.github.io/generators/fortune_generator
                    ```
                    {current_path()}
                    ```
                """
                )

            else:
                return command_not_found(msg)

        elif path_stack[-1] == 'quote':
            if msg == 'get':
                return textwrap.dedent(
                    f"""
                    https://lifeadventurer.github.io/generators/quote_generator
                    ```
                    {current_path()}
                    ```
                """
                )

            else:
                return command_not_found(msg)

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
                    return textwrap.dedent(
                        f"""
                        ```
                        please enter a valid number
                        {current_path()}
                        ```
                    """
                    )

                url += handle
                response = requests.get(url)
                if response.status_code == 404:
                    return textwrap.dedent(
                        f"""
                        ```
                        The handle {handle} is not found
                        {current_path()}
                        ```
                    """
                    )

                else:
                    return textwrap.dedent(
                        f"""
                        {url}
                        ```
                        {current_path()}
                        ```
                    """
                    )

            else:
                return textwrap.dedent(
                    f"""
                    ```
                    please type the right command format, using help to see what are the available options
                    {current_path()}
                    ```
                """
                )

        # just a google search -> must improve this more
        elif len(path_stack) > 2 and path_stack[2] == 'google':
            return textwrap.dedent(
                f"""
                https://www.google.com/search?q={msg}
                ```
                {current_path()}
                ```
            """
            )

        # same as above -> need improvement
        elif len(path_stack) > 2 and path_stack[2] == 'youtube':
            return textwrap.dedent(
                f"""
                https://www.youtube.com/results?search_query={msg}
                ```
                {current_path()}
                ```
            """
            )

        # search for github repos or profiles -> because url
        elif len(path_stack) > 2 and path_stack[2] == 'github':
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

        elif len(path_stack) > 2 and path_stack[2] == 'greek':
            if msg == 'get':
                return textwrap.dedent(
                    f"""\
                    ```
                    Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
                    α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
                    {current_path()}
                    ```
                """
                )

            else:
                return command_not_found(msg)

    # weather API
    elif len(path_stack) > 1 and path_stack[1] == 'weather':
        if msg[:6] == '--help':
            return textwrap.dedent(
                f"""\
                ```
                {load_help_command_information('weather', 4, 6)}
                {current_path()}
                ```
            """
            )

        if msg == 'get':
            return textwrap.dedent(
                f"""\
                ```
                {get_weather_info(4, 4)}
                {current_path()}
                ```
            """
            )

        else:
            return command_not_found(msg)

    # roll a random number
    elif len(path_stack) > 1 and path_stack[1] == 'random':
        if len(path_stack) > 2 and path_stack[2] == 'number':
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('random_number', 4, 5)}
                    {current_path()}
                    ```
                """
                )

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

        elif len(path_stack) > 2 and path_stack[2] == 'vocab':
            if len(path_stack) > 3 and path_stack[3] == 'test':
                if msg[:6] == '--help':
                    return textwrap.dedent(
                        f"""\
                        ```
                        {load_help_command_information('random_vocab_test', 4, 6)}
                        {current_path()}
                        ```
                    """
                    )

                if msg.lower() == 'g':
                    global vocabulary_list
                    with open(
                        '../data/json/vocabulary_items.json', 'r', encoding='utf-8'
                    ) as file:
                        vocabulary_list = json.load(file)

                    if username in vocabulary_list:
                        if len(vocabulary_list[username]) == 0:
                            return textwrap.dedent(
                                f"""
                                ```
                                You have cleared all the words.
                                {current_path()}
                                ```
                            """
                            )
                        else:
                            random_vocab_testing = True
                            vocab_index = random.randint(
                                0, len(vocabulary_list[username]) - 1
                            )
                            return textwrap.dedent(
                                f"""
                                ```
                                {vocabulary_list[username][vocab_index]['word']}
                                ```
                            """
                            )

                    else:
                        return textwrap.dedent(
                            f"""
                            ```
                            You have never use dict feature before. 
                            Try it to save vocabulary items in Moonafly, then
                            use ~/random/vocab/test to examine yourself
                            {current_path()}
                            ```
                        """
                        )

                elif random_vocab_testing:
                    if msg in vocabulary_list[username][vocab_index]['word_in_zh_TW']:
                        random_vocab_testing = False
                        vocabulary_list[username][vocab_index]['count'] -= 1
                        word = vocabulary_list[username][vocab_index]['word']
                        word_in_zh_TW = vocabulary_list[username][vocab_index][
                            'word_in_zh_TW'
                        ]
                        if vocabulary_list[username][vocab_index]['count'] == 0:
                            del vocabulary_list[username][vocab_index]
                        with open(
                            '../data/json/vocabulary_items.json', 'w', encoding='utf-8'
                        ) as file:
                            json.dump(
                                vocabulary_list, file, indent=4, ensure_ascii=False
                            )
                        return textwrap.dedent(
                            f"""
                            ```
                            Correct!
                            {word}
                            {word_in_zh_TW}
                            {current_path()}
                            ```
                        """
                        )

                    else:
                        random_vocab_testing = False
                        vocabulary_list[username][vocab_index]['count'] += 1
                        with open(
                            '../data/json/vocabulary_items.json', 'w', encoding='utf-8'
                        ) as file:
                            json.dump(
                                vocabulary_list, file, indent=4, ensure_ascii=False
                            )
                        return textwrap.dedent(
                            f"""
                            ```
                            Oops! Wrong
                            {vocabulary_list[username][vocab_index]['word']}
                            {vocabulary_list[username][vocab_index]['word_in_zh_TW']}
                            {current_path()}
                            ```
                        """
                        )

                else:
                    return command_not_found(msg)

    # return the definition and example of the enter word from a dictionary
    elif len(path_stack) > 1 and path_stack[1] == 'dict':
        # different languages
        # en
        if len(path_stack) > 2 and path_stack[2] == 'en':
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('dict_en', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            # LIMIT example count
            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return textwrap.dedent(
                    f"""
                    {search_dict('en', match.group(1), int(match.group(2)), 4, 5)}
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
                    {search_dict('en', msg, 3, 4, 5)}
                    ```
                    {current_path()}
                    ```
                """
                )

        # en-zh_TW
        elif len(path_stack) > 2 and path_stack[2] == 'en-zh_TW':
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('dict_en-zh_TW', 4, 5)}
                    {current_path()}
                    ```
                """
                )
            # LIMIT example count
            match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
            if match:
                return textwrap.dedent(
                    f"""
                    {search_dict('en-zh_TW', match.group(1), int(match.group(2)), 4, 5, username)}
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
                    {search_dict('en-zh_TW', msg, 3, 4, 5, username)}
                    ```
                    {current_path()}
                    ```
                """
                )

    # games
    elif len(path_stack) > 1 and path_stack[1] == 'game':
        if len(path_stack) > 2 and path_stack[2] == '1A2B':
            if msg[:6] == '--help':
                return textwrap.dedent(
                    f"""\
                    ```
                    {load_help_command_information('game_1A2B', 4, 5)}
                    {current_path()}
                    ```
                """
                )

            if not playing_game_1A2B:
                if msg[:5] == 'start' or msg[:5] == 'Start':
                    playing_game_1A2B = True
                    attempts = 0
                    msg = msg[6:].strip()
                    if msg[:6] == '--help':
                        return textwrap.dedent(
                            f"""\
                            ```
                            {load_help_command_information('game_1A2B_start', 4, 6)}
                            {current_path()}
                            ```
                        """
                        )

                    # choose the length you want to start playing
                    if len(msg) > 0:
                        if msg.isdigit() and 4 <= int(msg) <= 10:
                            target_number_len = int(msg)
                            # the numbers won't be duplicated
                            target_number = ''.join(
                                random.sample('0123456789', target_number_len)
                            )

                        else:
                            return textwrap.dedent(
                                f"""
                                ```
                                please enter a valid number between 4 to 10
                                {current_path()}
                                ```
                            """
                            )

                    else:
                        # the default length for this game
                        target_number_len = 4
                        # the numbers won't be duplicated
                        target_number = ''.join(
                            random.sample('123456', target_number_len)
                        )
                    print(target_number)
                    return textwrap.dedent(
                        f"""
                        ```
                        {target_number_len}-digit number generated.
                        ```
                    """
                    )

                elif msg[:4] == 'rank' or msg[:4] == 'Rank':
                    msg = msg[5:].strip()

                    if msg[:6] == '--help':
                        return textwrap.dedent(
                            f"""\
                            ```
                            {load_help_command_information('game_1A2B_rank', 4, 6)}
                            {current_path()}
                            ```
                        """
                        )

                    # show certain length ranking
                    if len(msg) > 0:
                        if msg.isdigit():
                            if 4 <= int(msg) <= 10:
                                search_rank_length = int(msg)
                                return textwrap.dedent(
                                    f"""
                                    ```
                                    {show_1A2B_certain_length_ranking(search_rank_length, 4, 9)}
                                    {current_path()}
                                    ```
                                """
                                )

                            else:
                                return textwrap.dedent(
                                    f"""
                                    ```
                                    please enter a valid number between 4 to 10
                                    {current_path()}
                                    ```
                                """
                                )

                        # search user ranking
                        else:
                            certain_user = msg
                            if msg == '-p':
                                certain_user = username
                            return textwrap.dedent(
                                f"""
                                ```
                                {show_1A2B_certain_user_ranking(certain_user, 4, 8)}
                                {current_path()}
                                ```
                            """
                            )

                    # show every length ranking
                    return textwrap.dedent(
                        f"""
                        ```
                        {show_1A2B_every_length_ranking(4, 6)}
                        {current_path()}
                        ```
                    """
                    )

            elif playing_game_1A2B:
                # stop the game if you want
                if msg[:4] == 'stop' or msg[:4] == 'Stop':
                    playing_game_1A2B = False
                    msg = msg[5:].strip()
                    if msg[:6] == '--help':
                        return textwrap.dedent(
                            f"""\
                            ```
                            {load_help_command_information('game_1A2B_stop', 4, 7)}
                            {current_path()}
                            ```
                        """
                        )

                    # use `stop start` to restart the game if you want
                    # any other commands can be add after that
                    if len(msg) > 0:
                        message.content = msg
                        return responses.get_response(message)

                    return textwrap.dedent(
                        f"""
                        ```
                        Game ended.
                        {current_path()}
                        ```
                    """
                    )
                guess = msg

                if len(guess) == target_number_len and guess.isdigit():
                    # A means the number is correct and the position is correct
                    A_cnt = sum(t == g for t, g in zip(target_number, guess))

                    # B means the number is correct, but the position is incorrect
                    B_cnt = (
                        sum(
                            min(target_number.count(digit), guess.count(digit))
                            for digit in target_number
                        )
                        - A_cnt
                    )

                    attempts += 1

                    # User got the target number
                    if A_cnt == target_number_len:
                        playing_game_1A2B = False

                        # save game records for the rank board
                        user_rank = save_game_1A2B_result(target_number_len, attempts)

                        return textwrap.dedent(
                            f"""
                            ```
                            Congratulations! You guessed the target number {target_number} in {attempts} attempts.
                            Your got rank {user_rank} in length {target_number_len} !!!
                            {current_path()}
                            ```
                        """
                        )

                    else:
                        return textwrap.dedent(
                            f"""
                            ```
                            {A_cnt}A{B_cnt}B
                            ```
                        """
                        )

                else:
                    return textwrap.dedent(
                        f"""
                        ```
                        please enter a valid input with only numbers and the correct length
                        ```
                    """
                    )

            else:
                return command_not_found(msg)

        elif len(path_stack) > 2 and path_stack[2] == 'CTF':
            return function_developing()

    else:
        return command_not_found(msg)
