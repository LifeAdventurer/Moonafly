import response_public
import response_terminal 
import json

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

def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.lstrip().rstrip()

    global is_public_mode, entering_password, incorrect_count, password, special_guest_using_terminal

    if entering_password and incorrect_count < 3 and username not in special_guests:
        if msg == password:
            password = password[::-1]
            incorrect_count = 0
            entering_password = False
            is_public_mode = False
            response_terminal.path_stack.append("~")
            print('swap to terminal mode')
            print('Moonafly:~$')
            return '```Moonafly:~$```'
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

    if not is_public_mode and (msg == 'moonafly -p' or msg == 'Moonafly -p'):
        is_public_mode = True
        print('swap to public mode')
        return 'Successfully swap to public mode!'
    elif msg == 'moonafly -t' or msg == 'Moonafly -t':
        if username not in special_guests:
            entering_password = True
            return '```please enter password```'
        else:
            special_guest_using_terminal = True
        is_public_mode = False
        response_terminal.path_stack.append("~")
        print('swap to terminal mode')
        print('Moonafly:~$')
        return '```Moonafly:~$```'

    else:
        if msg == 'exit' and not is_public_mode:
            if username in special_guests:
                special_guest_using_terminal = False
            is_public_mode = True
            incorrect_count = 0
            response_terminal.path_stack.clear()
            return
        elif msg == 'status':
            if is_public_mode:
                return 'public mode v1.0.1'
            else:
                return f'```terminal mode v1.1.0\n{response_terminal.current_path()}```'
        if is_public_mode:
            return response_public.get_response_in_public_mode(message)
        else:
            return response_terminal.get_response_in_terminal_mode(message)