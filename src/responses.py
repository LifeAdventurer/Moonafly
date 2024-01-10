import normal_mode
import terminal_mode
import develop_mode


from cmd import clipboard
from cmd import random_vocab_test
from cmd import game_1A2B


import json
import textwrap
import time
import psutil


Moonafly_version = 'v2.4.0'


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
            'user': terminal_mode_current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    # save the record to json file
    with open('../data/json/terminal_login_history.json', 'w') as file:
        json.dump(records, file, indent=4)


# prevent multiple user using terminal or develop mode at the same time
terminal_mode_current_using_user = ''
develop_mode_current_using_user = ''

# in which mode status
is_normal_mode = True
is_terminal_mode = False
is_develop_mode = False


def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_normal_mode, is_terminal_mode, is_develop_mode
    global terminal_mode_current_using_user, develop_mode_current_using_user

    if (
        is_normal_mode == True
        and (
            msg[:2] == '-t'
            or msg[:11] == 'moonafly -t'
            or msg[:11] == 'Moonafly -t'
        )
    ):
        if username in special_guests:
            is_normal_mode = False
            is_terminal_mode = True
            
            terminal_mode_current_using_user = username

            # call this function after terminal_mode_current_using_user has been assigned
            # ignore author login
            if terminal_mode_current_using_user != author:
                save_terminal_login_record()
            
            # don't use append or it might cause double '~' when using recursion -t -t... command
            terminal_mode.path_stack = ['~']
            print('swap to terminal mode')
            msg = msg[(2 if msg[:2] == '-t' else 11):].strip()
            if len(msg) > 0:
                message.content = msg
                return get_response(message)

            return textwrap.dedent(f"""
                ```
                {terminal_mode.current_path()}
                ```
            """)
        
        else:
            return textwrap.dedent(f"""
                ```
                you don't have the permission to access terminal mode
                ```
            """) 
    
    elif (
        is_normal_mode == True
        and (
            msg[:2] == '-d'
            or msg[:11] == 'moonafly -d'
            or msg[:11] == 'Moonafly -d'
        )
    ):
        if username in developers:
            is_normal_mode = False
            is_develop_mode = True

            develop_mode_current_using_user = username
            
            develop_mode.path_stack = ['~']
            print('swap to develop mode')
            msg = msg[(2 if msg[:2] == '-d' else 11):].strip()
            if len(msg) > 0:
                message.content = msg
                return get_response(message)

            return textwrap.dedent(f"""
                ```
                Welcome, developer {username}!
                {develop_mode.current_path()}
                ```
            """)
        
        else:
            return textwrap.dedent(f"""
                ```
                you don't have the permission to access develop mode
                ```
            """) 

    else:
        # make sure no other user can exit the terminal 
        if msg == 'exit':
            if is_terminal_mode:
                is_terminal_mode = False
                is_normal_mode = True
                
                clipboard.checking_clipboard_keyword_override = False
                game_1A2B.playing_game_1A2B = False
                random_vocab_test.random_vocab_testing = False

                terminal_mode.path_stack.clear()
                terminal_mode_current_using_user = ''

            elif is_develop_mode:
                is_develop_mode = False
                is_normal_mode = True

                develop_mode.path_stack.clear()
                develop_mode_current_using_user = ''

            return 'exited successfully'

        elif msg == 'status':
            mode = ''
            if is_terminal_mode:
                mode = 'terminal_mode'
            elif is_develop_mode:
                mode = 'develop_mode'
            else:
                mode = 'normal_mode'
            battery = psutil.sensors_battery()
            percent = battery.percent
            is_charging = battery.power_plugged

            return textwrap.dedent(f"""
                ```
                Moonafly {Moonafly_version}
                {mode}
                server battery percentage: {percent}% ({'' if is_charging == True else 'not '}charging)
                ```
            """)

        else:
            if is_terminal_mode:
                return terminal_mode.get_response_in_terminal_mode(message)
            elif is_develop_mode:
                return develop_mode.get_response_in_develop_mode(message)
            else:
                return normal_mode.get_response_in_normal_mode(message)