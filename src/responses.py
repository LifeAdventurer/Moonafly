import response_normal
import response_terminal 
import json
import textwrap
import time


project_version = 'v2.1.0'


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

def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_normal_mode, current_using_user

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
            response_terminal.path_stack = ['~']
            print('swap to terminal mode')
            print('Moonafly:~$')
            msg = msg[(2 if msg[:2] == '-t' else 11):].strip()
            if len(msg) > 0:
                message.content = msg
                return get_response(message)

            return textwrap.dedent(f"""\
                ```
                {response_terminal.current_path()}
                ```
            """)
        
        else:
            return textwrap.dedent(f"""\
                ```
                you don't have the permission to access terminal mode
                ```
            """) 

    else:
        # make sure no other user can exit the terminal 
        if msg == 'exit' and not is_normal_mode:
            is_normal_mode = True
            incorrect_count = 0
            response_terminal.playing_game_1A2B = False
            response_terminal.random_vocab_testing = False
            response_terminal.path_stack.clear()
            current_using_user = ''
            return ''
        elif msg == 'status':
            return textwrap.dedent(f"""\
                ```
                Moonafly {project_version}
                {'normal mode' if is_normal_mode else 'terminal mode'}
                ```
            """)

        else:
            if is_normal_mode:
                return response_normal.get_response_in_normal_mode(message)
            else:
                return response_terminal.get_response_in_terminal_mode(message)