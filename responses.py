import response_public
import response_terminal 
import json
import textwrap
import time

# project version
project_version = 'v1.6.0'

# password
password = ""
# initialed when bot started via init_files() in `bot.py`
def load_password_for_terminal():
    global password
    with open('./data/json/passwords.json') as passwords_file:
        password = json.load(passwords_file)['terminal_password']

# special guest list
# author in the first line
special_guests = []
# initialed when bot started via init_files() in `bot.py`
def special_guest_list():
    global special_guests
    with open('./data/json/special_guests.json') as special_guest_file:
        special_guests = json.load(special_guest_file)['guests']

def get_terminal_login_record():
    global login_records
    with open('./data/json/terminal_login_history.json') as login_history_file:
        login_records = json.load(login_history_file)

    return login_records

def save_terminal_login_record():
    # you must get the record every time since the user might enter several times
    records = get_terminal_login_record()

    records['history'].append({'user': current_using_user, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')})
    
    # save the record to json file
    with open('./data/json/terminal_login_history.json', 'w') as login_history_file:
        json.dump(records, login_history_file, indent = 4)

# password feature for terminal mode 
entering_password = False
incorrect_count = 0
is_public_mode = True

# prevent multiple user using the terminal at once
current_using_user = ''

def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_public_mode, entering_password, incorrect_count, password, current_using_user

    if entering_password and incorrect_count < 3 and username not in special_guests:
        if msg == password:
            incorrect_count = 0
            entering_password = False
            is_public_mode = False
            current_using_user = username
            
            # call this function after current_using_user has been assigned
            save_terminal_login_record()

            # don't use append or it might cause double '~' when using recursion -t -t... command
            response_terminal.path_stack = ['~']
            print('swap to terminal mode')
            print('Moonafly:~$')
            return textwrap.dedent(f"""\
                ```
                {response_terminal.current_path()}
                ```
            """)
        else:
            incorrect_count += 1
            if incorrect_count == 3:
                incorrect_count = 0
                entering_password = False
                is_public_mode = True
                return '```the maximum number of entries has been reached\nauto exited```'
            return '```incorrect, please enter again```'

    # if current_using_user != '' and username != current_using_user:
    #     return ''

    if not is_public_mode and (msg == '-p' or msg == 'moonafly -p' or msg == 'Moonafly -p'):
        is_public_mode = True
        print('swap to public mode')
        return 'Successfully swap to public mode!'
    elif msg[:2] == '-t' or msg[:11] == 'moonafly -t' or msg[:11] == 'Moonafly -t':
        if username not in special_guests:
            entering_password = True
            return '```please enter password```'
        else:
            is_public_mode = False
            current_using_user = username

            # call this function after current_using_user has been assigned
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
        # make sure no other user can exit the terminal 
        if msg == 'exit' and not is_public_mode:
            is_public_mode = True
            incorrect_count = 0
            response_terminal.playing_game = False
            response_terminal.path_stack.clear()
            current_using_user = ''
            return ''
        elif msg == 'status':
            if is_public_mode:
                return f"Moonafly {project_version}"
            else:
                return textwrap.dedent(f"""\
                    ```
                    Moonafly {project_version}
                    {response_terminal.current_path()}
                    ```
                """)

        if is_public_mode:
            return response_public.get_response_in_public_mode(message)
        else:
            return response_terminal.get_response_in_terminal_mode(message)