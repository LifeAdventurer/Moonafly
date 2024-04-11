import json
import textwrap
import time
from datetime import timedelta

import psutil
import pyautogui

import bot
import develop_mode
import normal_mode
import terminal_mode
from command import approve, clipboard, game_1A2B, random_vocab_test, translate

Moonafly_version = 'v2.12.0'


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
        login_records = {"history": []}
        with open('../data/json/terminal_mode_login_history.json', 'w') as file:
            json.dump(login_records, file, indent=4)

    return login_records


def save_terminal_mode_login_record():
    # you must get the record every time since the user might enter several times
    records = get_terminal_mode_login_record()

    records['history'].append(
        {
            'user': terminal_mode_current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
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
        login_records = {"history": []}
        with open('../data/json/develop_mode_login_history.json', 'w') as file:
            json.dump(login_records, file, indent=4)

    return login_records


def save_develop_mode_login_record():
    # you must get the record every time since the user might enter several times
    records = get_develop_mode_login_record()

    records['history'].append(
        {
            'user': develop_mode_current_using_user,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
    )

    # save the record to json file
    with open('../data/json/develop_mode_login_history.json', 'w') as file:
        json.dump(records, file, indent=4)


# prevent multiple user using terminal or develop mode at the same time
terminal_mode_current_using_user = ''
develop_mode_current_using_user = ''
start_using_timestamp = None

# in which mode status
is_normal_mode = True
is_terminal_mode = False
is_develop_mode = False

ignore_capitalization = False

enter_terminal_mode_cmd = ['-t', 'moonafly -t', 'Moonafly -t']
enter_develop_mode_cmd = ['-d', 'moonafly -d', 'Moonafly -d']
ignore_capitalization_option = ['--ic', '--ignore-capitalization']


mouseX, mouseY = pyautogui.position()


async def get_response(message) -> str:
    username = str(message.author)
    msg = str(message.content)
    # prevent ' and " separating the string
    msg = msg.replace("'", "\\'").replace("\"", "\\\"")
    # remove the leading and trailing spaces
    msg = msg.strip()

    global is_normal_mode, is_terminal_mode, is_develop_mode
    global terminal_mode_current_using_user, develop_mode_current_using_user, start_using_timestamp
    global enter_terminal_mode_cmd, enter_develop_mode_cmd, ignore_capitalization
    global mouseX, mouseY

    if is_normal_mode == True and any(
        msg.startswith(cmd) for cmd in enter_terminal_mode_cmd
    ):
        if username in special_guests:
            is_normal_mode = False
            is_terminal_mode = True

            terminal_mode_current_using_user = username
            start_using_timestamp = message.created_at - timedelta(seconds=0.1)

            # after terminal_mode_current_using_user has been assigned
            # ignore author login
            if terminal_mode_current_using_user != author:
                save_terminal_mode_login_record()

            # don't use append or it might cause double '~' when using recursion -t -t... command
            terminal_mode.path_stack = ['~']
            print('swap to terminal mode')
            msg = msg[(2 if msg.startswith('-t') else 11) :].strip()

            for cmd in ignore_capitalization_option:
                if msg.startswith(cmd):
                    msg = msg[len(cmd) :].strip()
                    ignore_capitalization = True
                    break

            if len(msg) > 0:
                message.content = msg
                return await get_response(message)

            user_pending = []
            if username == author:
                pending_role_list = approve.load_pending_role_list()
                for role in approve.roles:
                    pending_count = len(pending_role_list[role])
                    if pending_count > 0:
                        user_pending.append(
                            f"{pending_count} user{'s are' if pending_count > 1 else ' is'} pending for the role: '{role}'"
                        )

            space = '\n' + ' ' * TAB_SIZE * 4

            return textwrap.dedent(
                f"""
                ```
                {space.join(user_pending)}
                {terminal_mode.current_path()}
                ```
                """
            )

        else:
            return textwrap.dedent(
                f"""
                ```
                you don't have the permission to access terminal mode
                ```
                """
            )

    elif is_normal_mode == True and any(
        msg.startswith(cmd) for cmd in enter_develop_mode_cmd
    ):
        if username in developers:
            is_normal_mode = False
            is_develop_mode = True

            develop_mode_current_using_user = username
            start_using_timestamp = message.created_at - timedelta(seconds=0.1)

            # after develop_mode_current_using_user has been assigned
            # ignore author login
            if develop_mode_current_using_user != author:
                save_develop_mode_login_record()

            develop_mode.path_stack = ['~']
            print('swap to develop mode')
            msg = msg[(2 if msg.startswith('-d') else 11) :].strip()

            for cmd in ignore_capitalization_option:
                if msg.startswith(cmd):
                    msg = msg[len(cmd) :].strip()
                    ignore_capitalization = True
                    break

            if len(msg) > 0:
                message.content = msg
                return await get_response(message)

            return textwrap.dedent(
                f"""
                ```
                Welcome, developer {username}!
                {develop_mode.current_path()}
                ```
                """
            )

        else:
            return textwrap.dedent(
                f"""
                ```
                you don't have the permission to access develop mode
                ```
                """
            )

    else:
        # make sure no other user can exit the terminal
        if msg == 'exit':
            if is_terminal_mode:
                is_terminal_mode = False
                is_normal_mode = True

                clipboard.checking_clipboard_keyword_override = False
                game_1A2B.playing_game_1A2B = False
                random_vocab_test.random_vocab_testing = False
                translate.from_language = 'en'
                translate.to_language = 'zh-tw'

                terminal_mode.path_stack.clear()
                terminal_mode_current_using_user = ''

            elif is_develop_mode:
                is_develop_mode = False
                is_normal_mode = True

                develop_mode.path_stack.clear()
                develop_mode_current_using_user = ''

            # Before setting `start_using_timestamp` back to None
            await bot.clear_msgs(message, start_using_timestamp)

            # global variables that affect all modes
            ignore_capitalization = False
            start_using_timestamp = None

            return '```exited successfully```'

        elif msg.startswith('status'):
            msg = msg[6:].strip()

            mode = ''
            if is_terminal_mode:
                mode = 'terminal_mode'
            elif is_develop_mode:
                mode = 'develop_mode'
            else:
                mode = 'normal_mode'

            # battery
            battery = psutil.sensors_battery()
            percent = battery.percent
            is_charging = battery.power_plugged

            # mouse move
            mouse_moved = ''

            # cpu core usages
            aligned_cpu_core_usages = []
            # network_connections = []
            if username == author and msg.startswith('detail'):
                # cpu usage per core
                cpu_usage_per_core = psutil.cpu_percent(interval=1, percpu=True)

                cpu_core_usages = []
                for i, usage in enumerate(cpu_usage_per_core):
                    cpu_core_usages.append(
                        f"Core {(' ' + str(i + 1))[-2:]}: {usage}%"
                    )

                for i in range(0, len(cpu_core_usages), 4):
                    aligned_cpu_core_usages.append(
                        ''.join(
                            [
                                core.ljust(16)
                                for core in cpu_core_usages[i : i + 4]
                            ]
                        )
                    )

                # mouse move
                new_mouseX, new_mouseY = pyautogui.position()
                if new_mouseX != mouseX or new_mouseY != mouseY:
                    mouse_moved = 'mouse moved'
                    mouseX, mouseY = new_mouseX, new_mouseY

                # net_connections = psutil.net_connections()

                # for conn in net_connections:
                #     network_connections.append(
                #         f"{conn.laddr} -> {conn.raddr}, Status: {conn.status}"
                #     )
                #     print(f"{conn.laddr} -> {conn.raddr}, Status: {conn.status}")

            aligned_cpu_core_usages = ('\n' + ' ' * TAB_SIZE * 4).join(
                aligned_cpu_core_usages
            )
            # network_connections = ('\n' + ' ' * TAB_SIZE * 4).join(network_connections)

            return textwrap.dedent(
                f"""
                ```
                Moonafly {Moonafly_version}
                {mode}
                server battery percentage: {percent}% ({'' if is_charging == True else 'not '}charging)
                {'mouse moved' if mouse_moved else ''}
                {aligned_cpu_core_usages}
                ```
                """
            )

        else:
            if ignore_capitalization:
                message.content = msg[0].lower() + msg[1:]

            if is_terminal_mode:
                return await terminal_mode.get_response_in_terminal_mode(
                    message
                )
            elif is_develop_mode:
                return await develop_mode.get_response_in_develop_mode(message)
            else:
                return normal_mode.get_response_in_normal_mode(message)
