import normal_mode
import terminal_mode
import develop_mode


from command import clipboard
from command import random_vocab_test
from command import game_1A2B
from command import approve


import json
import textwrap
import time
import psutil
import pyautogui


Moonafly_version = 'v2.9.0'


# constants
TAB_SIZE = 4


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
    author = data['author']
    developers = data['developers']
    special_guests = data['guests']


def get_terminal_mode_login_record() -> dict:
    try:
        with open('../data/json/terminal_mode_login_history.json') as file:
            login_records = json.load(file)
    except FileNotFoundError:
        login_records = {
            "history": []
        }
        with open('../data/json/terminal_mode_login_history.json', 'w') as file:
            json.dump(login_records, file, indent=4)

    return login_records


def save_terminal_mode_login_record():
    # you must get the record every time since the user might enter several times
    records = get_terminal_mode_login_record()

    records['history'].append(
        {
            'user': terminal_mode_current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    # save the record to json file
    with open('../data/json/terminal_mode_login_history.json', 'w') as file:
        json.dump(records, file, indent=4)


def get_develop_mode_login_record() -> dict:
    try:
        with open('../data/json/develop_mode_login_history.json') as file:
            login_records = json.load(file)
    except FileNotFoundError:
        login_records = {
            "history": []
        }
        with open('../data/json/develop_mode_login_history.json', 'w') as file:
            json.dump(login_records, file, indent=4)

    return login_records


def save_develop_mode_login_record():
    # you must get the record every time since the user might enter several times
    records = get_develop_mode_login_record()

    records['history'].append(
        {
            'user': develop_mode_current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    # save the record to json file
    with open('../data/json/develop_mode_login_history.json', 'w') as file:
        json.dump(records, file, indent=4)


# prevent multiple user using terminal or develop mode at the same time
terminal_mode_current_using_user = ''
develop_mode_current_using_user = ''

# in which mode status
is_normal_mode = True
is_terminal_mode = False
is_develop_mode = False


enter_terminal_mode_cmd = [
    '-t',
    'moonafly -t',
    'Moonafly -t'
]
enter_develop_mode_cmd = [
    '-d',
    'moonafly -d',
    'Moonafly -d'
]


mouseX, mouseY = pyautogui.position()


def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_normal_mode, is_terminal_mode, is_develop_mode
    global terminal_mode_current_using_user, develop_mode_current_using_user
    global enter_terminal_mode_cmd, enter_develop_mode_cmd
    global mouseX, mouseY

    if (
        is_normal_mode == True
        and any(msg.startswith(cmd) for cmd in enter_terminal_mode_cmd)
    ):
        if username in special_guests:
            is_normal_mode = False
            is_terminal_mode = True
            
            terminal_mode_current_using_user = username

            # after terminal_mode_current_using_user has been assigned
            # ignore author login
            if terminal_mode_current_using_user != author:
                save_terminal_mode_login_record()
            
            # don't use append or it might cause double '~' when using recursion -t -t... command
            terminal_mode.path_stack = ['~']
            print('swap to terminal mode')
            msg = msg[(2 if msg[:2] == '-t' else 11):].strip()
            if len(msg) > 0:
                message.content = msg
                return get_response(message)

            if username == author:
                pending_role_list = approve.load_pending_role_list()

                user_pending = []

                for role in approve.roles:
                    pending_count = len(pending_role_list[role])
                    if pending_count > 0:
                        user_pending.append(
                            f"{pending_count} user{'s are' if pending_count > 1 else ' is'} pending for the role: '{role}'"
                        )
                    
                space = '\n' + ' ' * TAB_SIZE * 5

                return textwrap.dedent(f"""
                    ```
                    {space.join(user_pending)}
                    {terminal_mode.current_path()}
                    ```
                """)

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
        and any(msg.startswith(cmd) for cmd in enter_develop_mode_cmd)
    ):
        if username in developers:
            is_normal_mode = False
            is_develop_mode = True

            develop_mode_current_using_user = username

            # after develop_mode_current_using_user has been assigned
            # ignore author login
            if develop_mode_current_using_user != author:
                save_develop_mode_login_record()
            
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

            return '```exited successfully```'

        elif msg[:6] == 'status':
            msg = msg[6:].strip()

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

            mouse_moved = False
            new_mouseX, new_mouseY = pyautogui.position()
            if new_mouseX != mouseX or new_mouseY != mouseY:
                mouse_moved = True
                mouseX, mouseY = new_mouseX, new_mouseY

            cpu_core_usages = []
            # network_connections = []
            if username == author and msg[:6] == 'detail':
                cpu_usage_per_core = psutil.cpu_percent(interval=1, percpu=True)

                for i in range(0, len(cpu_usage_per_core), 4):
                    usage1 = cpu_usage_per_core[i]
                    usage2 = cpu_usage_per_core[i + 1]
                    usage3 = cpu_usage_per_core[i + 2]
                    usage4 = cpu_usage_per_core[i + 3]

                    core1 = f"Core {i + 1}: {usage1}%"
                    core2 = f"Core {i + 2}: {usage2}%"
                    core3 = f"Core {i + 3}: {usage3}%"
                    core4 = f"Core {i + 4}: {usage4}%"
                    
                    cpu_core_usages.append(
                        f"{core1}{' ' * (16 - len(core1))}{core2}{' ' * (16 - len(core2))}{core3}{' ' * (16 - len(core3))}{core4}{' ' * (16 - len(core4))}"
                    )
                
                # net_connections = psutil.net_connections()

                # for conn in net_connections:
                #     network_connections.append(
                #         f"{conn.laddr} -> {conn.raddr}, Status: {conn.status}"
                #     )
                #     print(f"{conn.laddr} -> {conn.raddr}, Status: {conn.status}")

            cpu_core_usages = ('\n' + ' ' * TAB_SIZE * 4).join(cpu_core_usages)
            # network_connections = ('\n' + ' ' * TAB_SIZE * 4).join(network_connections)

            return textwrap.dedent(f"""
                ```
                Moonafly {Moonafly_version}
                {mode}
                server battery percentage: {percent}% ({'' if is_charging == True else 'not '}charging)
                {'mouse moved' if mouse_moved else ''}
                {cpu_core_usages}
                ```
            """)

        else:
            if is_terminal_mode:
                return terminal_mode.get_response_in_terminal_mode(message)
            elif is_develop_mode:
                return develop_mode.get_response_in_develop_mode(message)
            else:
                return normal_mode.get_response_in_normal_mode(message)