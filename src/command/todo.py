import json
import re
import textwrap
from datetime import datetime

import responses
import terminal_mode
from command import command_help
from constants import HELP_FLAG, ROUTINE_FLAGS, TAB_SIZE


def load_todo_list() -> dict:
    try:
        with open('../data/json/todo_list.json', 'r') as file:
            todo_list = json.load(file)
    except FileNotFoundError:
        todo_list = {}
        write_todo_list(todo_list)

    return todo_list


def write_todo_list(todo_list):
    with open('../data/json/todo_list.json', 'w') as file:
        json.dump(todo_list, file, indent=4)


def init_todo_list_for_user(username: str) -> dict:
    todo_list = load_todo_list()
    todo_list[username] = {
        'uncompleted_items': [],
        'completed_items': [],
        'daily_routine': {},
    }
    write_todo_list(todo_list)
    return todo_list


def add_todo_item(
    todo_item: str, task_status: str = 'uncompleted_items'
) -> str:
    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)

    if task_status != 'daily_routine':
        todo_item_pattern = re.compile('^(\[.*?\])\s*(.*)$')
        match = todo_item_pattern.search(todo_item)
        label = match.group(1)
        description = match.group(2)

        if not match:
            return terminal_mode.handle_command_error('add', 'format')

        formatted_todo_item = f"{label} {description}"
        if formatted_todo_item in todo_list[username].setdefault(
            task_status, []
        ):
            return terminal_mode.handle_command_error('add', 'duplicated')
        else:
            todo_list[username][task_status].append(formatted_todo_item)
    else:
        todo_list[username].setdefault(task_status, {}).setdefault(
            todo_item, "1970-01-01"
        )

    write_todo_list(todo_list)

    return textwrap.dedent(
        f"""
        ```
        '{todo_item}' added to todo list
        {terminal_mode.current_path()}
        ```
        """
    )


def check_todo_item(msg: str, task_status: str = 'uncompleted_items') -> str:
    try:
        todo_item_numbers = [int(index) - 1 for index in msg.split(',')]
    except ValueError:
        return terminal_mode.handle_command_error('check', 'format')

    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)

    user_todo_list = todo_list[username][task_status]
    checked_items = []
    for todo_item_number in todo_item_numbers:
        if 0 <= todo_item_number < len(user_todo_list):
            if task_status == 'uncompleted_items':
                todo_item = user_todo_list[todo_item_number]
                checked_items.append(todo_item)
                todo_list[username]['completed_items'].append(todo_item)
            else:
                current_date = datetime.now()
                todo_item = list(user_todo_list.keys())[todo_item_number]
                user_todo_list[todo_item] = current_date.strftime("%Y-%m-%d")

    for checked_item in checked_items:
        user_todo_list.remove(checked_item)

    write_todo_list(todo_list)

    checked_items_str = ('\n' + ' ' * TAB_SIZE * 2).join(
        [f"'{item}' has been checked" for item in checked_items]
    )

    return textwrap.dedent(
        f"""
        ```
        {checked_items_str}
        {terminal_mode.current_path()}
        ```
        """
    )


def delete_todo_item(msg: str, task_status: str = 'uncompleted_items') -> str:
    if not msg:
        return terminal_mode.handle_command_error('del', 'format')

    try:
        todo_item_number = int(msg) - 1
    except ValueError:
        return terminal_mode.handle_command_error('del', 'format')

    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)
    user_todo_list = todo_list[username][task_status]
    if 0 <= todo_item_number < len(user_todo_list):
        if task_status == 'uncompleted_items':
            del user_todo_list[todo_item_number]
        else:
            key_to_delete = list(user_todo_list.keys())[todo_item_number]
            del user_todo_list[key_to_delete]

        write_todo_list(todo_list)

        return terminal_mode.handle_command_success('deleted')
    else:
        return terminal_mode.handle_command_error('del', 'index')


def list_todo_items(task_status: str, sort_method: str) -> str:
    sort_methods = ['index', 'label']
    if sort_method not in sort_methods:
        return terminal_mode.handle_command_error('list', 'format')

    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)

    todo_item_pattern = re.compile('^(\[.*?\])\s*(.*)$')

    if todo_list[username][task_status]:
        max_label_length = max(
            len(todo_item_pattern.search(todo_item).group(1))
            for todo_item in todo_list[username][task_status]
        )

    daily_routine_length = len(todo_list[username]['daily_routine'])
    todo_list_length = len(todo_list[username][task_status])
    max_index_length = max(
        len(str(daily_routine_length + 1)), len(str(todo_list_length + 1))
    )

    sorted_todo_items = todo_list[username][task_status].copy()

    if sort_method == 'label':
        sorted_todo_items.sort(
            key=lambda x: todo_item_pattern.match(x).group(1)
        )

    user_daily_routine_list = [
        f"daily routine items: {daily_routine_length}",
        '',
    ]

    for index, (key, value) in enumerate(
        todo_list[username]['daily_routine'].items(), start=1
    ):
        current_date = datetime.now()
        last_complete_date = datetime.strptime(value, "%Y-%m-%d")
        if (
            last_complete_date.year,
            last_complete_date.month,
            last_complete_date.day,
        ) < (current_date.year, current_date.month, current_date.day):
            user_daily_routine_item = (
                f"{str(index).rjust(max_index_length)}. {key}"
            )
            if len(user_daily_routine_item) > 80:
                user_daily_routine_item = user_daily_routine_item[:79] + '>'
            user_daily_routine_list.append(user_daily_routine_item)

    user_todo_list = [f"todo list items: {todo_list_length}", '']
    for todo_item in sorted_todo_items:
        index = todo_list[username][task_status].index(todo_item) + 1
        match = todo_item_pattern.search(todo_item)
        label = match.group(1)
        description = match.group(2)
        user_todo_item = f"{str(index).rjust(max_index_length)}. {label.ljust(max_label_length)} {description}"
        if len(user_todo_item) > 80:
            user_todo_item = user_todo_item[:79] + '>'

        user_todo_list.append(user_todo_item)

    space = '\n' + ' ' * TAB_SIZE * 2
    return textwrap.dedent(
        f"""
        ```
        {space.join(user_daily_routine_list)}

        {space.join(user_todo_list)}
        ```
        ```
        {terminal_mode.current_path()}
        ```
        """
    )


def get_todo_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('todo')

    if msg.startswith('add'):
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_add')
        for flag in ROUTINE_FLAGS:
            if msg.startswith(flag):
                msg = msg[len(flag) + 1 :].strip()
                return add_todo_item(msg, 'daily_routine')
        return add_todo_item(msg)

    elif msg.startswith('check'):
        msg = msg[6:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_check')
        for flag in ROUTINE_FLAGS:
            if msg.startswith(flag):
                msg = msg[len(flag) + 1 :].strip()
                return check_todo_item(msg, 'daily_routine')
        return check_todo_item(msg)

    elif msg.startswith('del'):
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_del')
        for flag in ROUTINE_FLAGS:
            if msg.startswith(flag):
                msg = msg[len(flag) + 1 :].strip()
                return delete_todo_item(msg, 'daily_routine')
        return delete_todo_item(msg)

    elif msg.startswith('list'):
        msg = msg[5:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_list')
        if msg.startswith('-c'):
            msg = msg[3:].strip()
            if msg.startswith('--sort='):
                msg = msg[7:].strip()
                return list_todo_items('completed_items', msg)
            return list_todo_items('completed_items', 'index')
        if msg.startswith('--sort='):
            msg = msg[7:].strip()
            return list_todo_items('uncompleted_items', msg)
        return list_todo_items('uncompleted_items', 'index')
    else:
        return terminal_mode.command_not_found(msg)
