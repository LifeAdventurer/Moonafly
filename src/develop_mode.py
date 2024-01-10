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

    if msg == 'help':
        return textwrap.dedent(f"""\
            ```
            Moonafly {responses.Moonafly_version}
            
            - normal mode
            - terminal mode 
            - develop mode (current)

             remote [file]
             tree [-M]
            ```
        """)

    if msg[:6] == 'remote':
        msg = msg[6:].strip()

        if msg[:6] == '--help':
            return command_help.load_help_cmd_info('remote_file')
        
        return remote.load_remote_file(msg, 'developer', username)
    
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
    


    
    else:
        return command_not_found(msg)