import response_public
import response_terminal 
import json
import textwrap

# versions
public_version = 'v1.0.2'
terminal_version = 'v1.3.1'

# password
password = ""
def load_password_for_terminal():
    global password
    with open('./json/passwords.json') as passwords_file:
        password = json.load(passwords_file)['terminal_password']

# special guest
special_guests = []
def special_guest_list():
    global special_guests
    with open('./json/special_guests.json') as special_guest_file:
        special_guests = json.load(special_guest_file)['guests']

special_guest_using_terminal = False
entering_password = False
incorrect_count = 0
is_public_mode = True
current_using_user = ''

def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_public_mode, entering_password, incorrect_count, password, special_guest_using_terminal, current_using_user

    if entering_password and incorrect_count < 3 and username not in special_guests:
        if msg == password:
            incorrect_count = 0
            entering_password = False
            is_public_mode = False
            response_terminal.path_stack.append("~")
            current_using_user = username
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

    if special_guest_using_terminal and username not in special_guests:
        return

    if not is_public_mode and (msg == 'moonafly -p' or msg == 'Moonafly -p' or msg == '-p'):
        is_public_mode = True
        print('swap to public mode')
        return 'Successfully swap to public mode!'
    elif msg[:11] == 'moonafly -t' or msg[:11] == 'Moonafly -t' or msg[:2] == '-t':
        if username not in special_guests:
            entering_password = True
            return '```please enter password```'
        else:
            special_guest_using_terminal = True
            is_public_mode = False
            response_terminal.path_stack.append("~")
            current_using_user = username
            print('swap to terminal mode')
            print('Moonafly:~$')
            if len(msg) > 0:
                message.content = msg[(2 if msg[:2] == '-t' else 11):].strip()
                get_response(message)

            return textwrap.dedent(f"""\
                ```
                {response_terminal.current_path()}
                ```
            """)

    else:
        if msg == 'exit' and not is_public_mode and username == current_using_user:
            special_guest_using_terminal = False
            is_public_mode = True
            incorrect_count = 0
            response_terminal.path_stack.clear()
            current_using_user = ''
            return
        elif msg == 'status':
            if is_public_mode:
                return f"public mode {public_version}"
            else:
                return textwrap.dedent(f"""\
                    ```
                    terminal mode {terminal_version}
                    {response_terminal.current_path()}
                    ```
                """)

        if is_public_mode:
            return response_public.get_response_in_public_mode(message)
        else:
            return response_terminal.get_response_in_terminal_mode(message)