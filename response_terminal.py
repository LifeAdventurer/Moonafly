import json
import random
import requests
from search_dict import search_dict
from search_weather import get_weather_info
from math_calc import safe_eval
from command_help import get_help_information
import responses
import os
import re
import textwrap

directory_structure = []

def get_directory_structure():
    global directory_structure
    with open('./data/json/directory_structure.json') as directory_structure_file:
        directory_structure = json.load(directory_structure_file)['directory_structure']

def command_not_found(msg) -> str:
    space = ' ' * 4 * 2
    msg = '\n'.join([space + line if index > 0 else line for index, line in enumerate(msg.split('\n'))])
    return textwrap.dedent(f"""
        ```
        {msg}: command not found
        {current_path()}
        ```
    """)

def get_ls_command_output(files, tab_size, tab_count) -> str:
    output = ""
    columns = 3;
    column_len = [0] * columns
    for column_index in range(min(columns, len(files))):
        grouped_files = [file for index, file in enumerate(files) if index % columns == column_index]
        column_len[column_index] = max(len(file_name) for file_name in grouped_files)

    for index, file in enumerate(files):
        output += file + ' ' * (column_len[index % columns] - len(file) + 2 if index % columns != columns - 1 else 0)
        if index % columns == columns - 1 and index != len(files) - 1:
            output += '\n' + ' ' * tab_size * tab_count

    return output

def visualize_directory_structure(data, tab_size, tab_count, indent = 0) -> str:
    tree = ""
    if isinstance(data, dict):
        for key, value in sorted(data.items()):
            tree += ' ' * tab_size * indent + '\-- ' + key + '\n' + ' ' * tab_size * tab_count
            tree += visualize_directory_structure(value, tab_size, tab_count, indent + 1)
    return tree 

path_stack = []

# generating the current working directory
def current_path() -> str:
    global path_stack
    path = f"{responses.current_using_user}@Moonafly:"
    for folder in path_stack:
        if folder != '~':
            path += '/'
        path += folder
    return path + "$"

def get_response_in_terminal_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()
    
    global path_stack

    # cd command
    if msg[:2] == 'cd':
        msg = msg[2:].lstrip()
        if msg[:6] == '--help':
            return textwrap.dedent(f"""\
                ```
                {get_help_information('cd', 4, 4)}
                {current_path()}
                ```
            """)

        path = msg
        
        # blank or ~ should go directly to ~
        if not path or path == '~':
            path_stack = ['~']
            return f"```{current_path()}```"

        # go to the root directory
        if path[0] == '/':
            return textwrap.dedent(f"""\
                ```
                permission denied
                * this command requires the highest authority
                {current_path()}
                ```
            """)
        
        # skip all the '\' and split the path into a folder list
        path = path.replace('\\', '').split('/')

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
                    msg = msg.replace("\\'", "'").replace("\\\"", "\"")
                    space = ' ' * 4 * 6
                    msg = '\n'.join([space + line if index > 0 else line for index, line in enumerate(msg.split('\n'))])
                    return textwrap.dedent(f"""\
                        ```
                        Moonafly: cd: {msg}: No such file or directory
                        {current_path()}
                        ```
                    """)

            else:
                temporary_path_stack.append(folder)
                
        current_directory = directory_structure

        for folder in temporary_path_stack:
            if folder in list(current_directory):
                current_directory = current_directory[folder]
            else:
                msg = msg.replace("\\'", "'").replace("\\\"", "\"")
                space = ' ' * 4 * 5
                msg = '\n'.join([space + line if index > 0 else line for index, line in enumerate(msg.split('\n'))])
                return textwrap.dedent(f"""\
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
            return textwrap.dedent(f"""\
                ```
                {get_help_information('ls', 4, 4)}
                {current_path()}
                ```
            """)

        current_directory = directory_structure
        for folder in path_stack:
            current_directory = current_directory[folder]

        files_in_current_directory = sorted(list(current_directory))

        return textwrap.dedent(f"""\
            ```
            {get_ls_command_output(files_in_current_directory, 4, 3)}
            {current_path()}
            ```
        """)

    # return the full pathname of the current working directory
    elif msg[:3] == 'pwd':
        msg = msg[3:].lstrip()
        if msg[:6] == '--help':
            return textwrap.dedent(f"""\
                ```
                {get_help_information('pwd', 4, 4)}
                {current_path()}
                ```
            """)

        # delete the prefix 'Moonafly:' and the suffix '$'
        path = current_path()[(10 + len(username)):-1]
        # delete the prefix no matter it is '~' or '/' path_stack still has the data
        path = path[1:]

        if path_stack[0] == '~':
            path = 'home/Moonafly' + path 

        return textwrap.dedent(f"""\
            ```
            /{path}
            {current_path()}
            ```
        """)
    
    # show the directory_structure
    elif msg[:4] == 'tree':
        msg = msg[4:].lstrip()
        if msg[:6] == '--help':
            return textwrap.dedent(f"""\
                ```
                {get_help_information('tree', 4, 4)}
                {current_path()}
                ```
            """)

        current_structure = directory_structure
        for folder in path_stack:
            current_structure = current_structure[folder]
        return textwrap.dedent(f"""
            ```
            {visualize_directory_structure(current_structure, 4, 3)}
            {current_path()}
            ```
        """)
    
    elif msg[:4] == 'help':
        msg = msg[4:].lstrip()
        if msg[:6] == '--help':
            return textwrap.dedent(f"""\
                ```
                {get_help_information('help', 4, 4)}
                {current_path()}
                ```
            """)

        return textwrap.dedent(f"""
            ```
            Moonafly, version {responses.terminal_version}

             cd [dir]
             help
             ls 
             pwd
             tree
            {current_path()}
            ```
        """)
    
    # commands in certain directory
    if len(path_stack) >= 2 and path_stack[-2] == 'math':
        if path_stack[-1] == 'calc':
            return textwrap.dedent(f"""
                ```
                {safe_eval(msg)}
                {current_path()}
                ```
            """)
        elif path_stack[-1] == 'count':
            words = msg.split()
            return textwrap.dedent(f"""
                ```
                {str(len(words))}
                {current_path()}
                ```
            """)

    elif len(path_stack) >= 2 and path_stack[-2] == 'gen':
        # my generators repo on github.io
        if path_stack[-1] == 'fortune':
            if msg == 'get':
                return textwrap.dedent(f"""
                    https://lifeadventurer.github.io/generators/fortune_generator
                    ```
                    {current_path()}
                    ```
                """)
            else:
                return command_not_found(msg)
        
        elif path_stack[-1] == 'quote':
            if msg == 'get':
                return textwrap.dedent(f"""
                    https://lifeadventurer.github.io/generators/quote_generator
                    ```
                    {current_path()}
                    ```
                """)
            else:
                return command_not_found(msg)

        else:
            return command_not_found(msg)
    
    elif len(path_stack) >= 2 and path_stack[-2] == 'search':
        # search for a handle in different online judges
        if path_stack[-1] == 'online-judge':
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

        # just a google search -> must improve this more
        elif path_stack[-1] == 'google':
            return textwrap.dedent(f"""
                https://www.google.com/search?q={msg}
                ```
                {current_path()}
                ```
            """)

        # same as above -> need improvement
        elif path_stack[-1] == 'youtube':
            return textwrap.dedent(f"""
                https://www.youtube.com/results?search_query={msg}
                ```
                {current_path()}
                ```
            """)

        # search for github repos or profiles -> because url
        elif path_stack[-1] == 'github':
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
        elif path_stack[-1] == 'git':
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
                return textwrap.dedent(f"""
                    ```
                    sorry, this function is still developing
                    {current_path()}
                    ```
                """)
            # TO-DO
            # elif msg == 'setup':

        elif path_stack[-1] == 'greek':
            if msg == 'get':
                return textwrap.dedent(f"""\
                    ```
                    Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
                    α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
                    {current_path()}
                    ```
                """)
            else:
                return command_not_found(msg)

        else:
            return command_not_found(msg)
    
    elif path_stack[-1] == 'weather':
        if msg == 'get':
            return textwrap.dedent(f"""\
                ```
                {get_weather_info(4, 4)}
                {current_path()}
                ```
            """)
        else:
            return command_not_found(msg)

    # roll a random number
    elif path_stack[-1] == 'roll':
        if not all(char.isdigit() for char in msg):
            return textwrap.dedent(f"""
                ```
                please enter a valid number
                {current_path()}
                ```
            """)
        else:
            return textwrap.dedent(f"""
                ```
                {random.randint(1, int(msg))}
                {current_path()}
                ```
            """)

    # return the definition and example of the enter word from a dictionary
    elif path_stack[-1] == 'dict':
        match = re.search(r'^(\w+)\s+LIMIT\s+(\d+)$', msg)
        if match:
            return textwrap.dedent(f"""
                {search_dict(match.group(1), int(match.group(2)), 4, 4)}
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
                {search_dict(msg, 3, 4, 4)}
                ```
                {current_path()}
                ```
            """)
    
    elif path_stack[-1] == 'game':

        return textwrap.dedent(f"""
            ```
            sorry, this function is still developing
            {current_path()}
            ```
        """)

    else:
        return command_not_found(msg)