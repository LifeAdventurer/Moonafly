import responses


from cmd import remote
from cmd import command_help
from cmd import tree


import textwrap
import json


develop_mode_directory_structure = []
# initialed when bot started via init_files() in `bot.py`
def load_develop_mode_directory_structure():
    global develop_mode_directory_structure
    with open('../data/json/develop_mode_directory_structure.json') as file:
        develop_mode_directory_structure = json.load(file)['structure']


Moonafly_structure = []
# initialed when bot started via init_files() in `bot.py`
def load_Moonafly_structure():
    global Moonafly_structure
    with open('../data/json/Moonafly_structure.json') as file:
        Moonafly_structure = json.load(file)['structure']


path_stack = []
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


def get_response_in_develop_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global path_stack

    if msg == 'help':
        return textwrap.dedent(f"""\
            ```
            Moonafly {responses.Moonafly_version}
            
            - normal mode
            - terminal mode 
            - develop mode (current)

             cd [dir]
             tree [-M]
            ```
        """)

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

        current_directory = develop_mode_directory_structure

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
                return textwrap.dedent(f"""
                    ```
                    Moonafly: cd: {msg}: No such file or directory
                    {current_path()}
                    ```
                """)

        path_stack = temporary_path_stack
        return f"```{current_path()}```"

    # tree command
    elif msg[:4] == 'tree':
        msg = msg[4:].lstrip()

        if msg[:6] == '--help':
            return command_help.load_help_cmd_info('tree')

        if msg[:8] == 'Moonafly':
            return tree.visualize_structure(Moonafly_structure, 'develop', username)

        # copy the directory structure
        current_structure = develop_mode_directory_structure
        # and move it to the current directory
        for folder in path_stack:
            current_structure = current_structure[folder]

        return tree.visualize_structure(current_structure, 'develop', username)
    
    if len(path_stack) > 1 and path_stack[1] == 'remote':
        if len(path_stack) > 2 and path_stack[2] == 'file': 
            if msg[:6] == '--help':
                return command_help.load_help_cmd_info('remote_file')

            return remote.load_remote_file(msg, 'developer', username)
    
    else:
        return command_not_found(msg)