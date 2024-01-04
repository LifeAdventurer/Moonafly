import normal_mode
import terminal_mode
import develop_mode


import json
import textwrap
import time


Moonafly_version = 'v2.2.0'


# user identity
author = ''
developers = []
special_guests = []
# initialed when bot started via init_files() in `bot.py`
def load_user_identity_list():
    global author, developers, special_guests
    with open('../data/json/user_identity.json') as file:
        data = json.load(file)
    # author has the highest authority
    # only one author
    author = data['author'][0] 
    developers = data['developers']
    special_guests = data['guests']


def get_terminal_login_record() -> dict:
    global login_records
    with open('../data/json/terminal_login_history.json') as file:
        login_records = json.load(file)

    return login_records


def save_terminal_login_record():
    # you must get the record every time since the user might enter several times
    records = get_terminal_login_record()

    records['history'].append(
        {
            'user': current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    # save the record to json file
    with open('../data/json/terminal_login_history.json', 'w') as file:
        json.dump(records, file, indent=4)


# prevent multiple user using the terminal at once
current_using_user = ''


is_normal_mode = True
is_develop_mode = False


def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_normal_mode, is_develop_mode, current_using_user

    if (
        msg[:2] == '-t'
        or msg[:11] == 'moonafly -t'
        or msg[:11] == 'Moonafly -t'
    ):
        if username in special_guests:
            is_normal_mode = False
            current_using_user = username

            # call this function after current_using_user has been assigned
            # ignore author login
            if current_using_user != author:
                save_terminal_login_record()
            
            # don't use append or it might cause double '~' when using recursion -t -t... command
            terminal_mode.path_stack = ['~']
            print('swap to terminal mode')
            print('Moonafly:~$')
            msg = msg[(2 if msg[:2] == '-t' else 11):].strip()
            if len(msg) > 0:
                message.content = msg
                return get_response(message)

            return textwrap.dedent(f"""\
                ```
                {terminal_mode.current_path()}
                ```
            """)
        
        else:
            return textwrap.dedent(f"""\
                ```
                you don't have the permission to access terminal mode
                ```
            """) 
    
    elif (
        msg[:2] == '-d'
        or msg[:11] == 'moonafly -d'
        or msg[:11] == 'Moonafly -d'
    ):
        if username in developers:
            is_normal_mode = False
            is_develop_mode = True
            
            # don't use append or it might cause double '~' when using recursion -t -t... command
            print('swap to develop mode')
            msg = msg[(2 if msg[:2] == '-d' else 11):].strip()
            if len(msg) > 0:
                message.content = msg
                return get_response(message)

            return textwrap.dedent(f"""\
                ```
                Welcome, developer {username}!
                ```
            """)
        
        else:
            return textwrap.dedent(f"""\
                ```
                you don't have the permission to access develop mode
                ```
            """) 

    else:
        # make sure no other user can exit the terminal 
        if msg == 'exit' and not is_normal_mode:
            is_normal_mode = True
            is_develop_mode = False
            incorrect_count = 0
            terminal_mode.playing_game_1A2B = False
            terminal_mode.random_vocab_testing = False
            terminal_mode.path_stack.clear()
            current_using_user = ''
            return ''
        elif msg == 'status':
            mode = ''
            if is_normal_mode:
                mode = 'normal_mode'
            elif is_develop_mode:
                mode = 'develop_mode'
            else:
                mode = 'terminal_mode'
            return textwrap.dedent(f"""\
                ```
                Moonafly {Moonafly_version}
                {mode}
                ```
            """)

        else:
            if is_normal_mode:
                return normal_mode.get_response_in_normal_mode(message)
            elif is_develop_mode:
                return develop_mode.get_response_in_develop_mode(message)
            else:
                return terminal_mode.get_response_in_terminal_mode(message)