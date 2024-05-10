import json
import re
import textwrap

import responses
import terminal_mode
from command import command_help
from constants import HELP_FLAG, TAB_SIZE


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
    todo_list[username] = {'uncompleted_items': [], 'completed_items': []}
    write_todo_list(todo_list)
    return todo_list


def add_todo_item(todo_item: str) -> str:
    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)

    todo_item_pattern = re.compile(f'^(\[.*?\])\s*(.*)$')

    if not todo_item_pattern.match(todo_item):
        return terminal_mode.handle_command_error('add', 'format')

    todo_list[username]['uncompleted_items'].append(todo_item)
    write_todo_list(todo_list)

    return textwrap.dedent(
        f"""
        ```
        '{todo_item}' added to todo list
        {terminal_mode.current_path()}
        ```
        """
    )


def check_todo_item(todo_item_number: str) -> str:
    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)

    if todo_item_number.isdigit() and 0 <= int(todo_item_number) <= len(
        todo_list[username]['uncompleted_items']
    ):
        todo_item = todo_list[username]['uncompleted_items'][
            int(todo_item_number) - 1
        ]
        del todo_list[username]['uncompleted_items'][int(todo_item_number) - 1]
        todo_list[username]['completed_items'].append(todo_item)
        write_todo_list(todo_list)

        return textwrap.dedent(
            f"""
            ```
            '{todo_item}' has been checked!
            {terminal_mode.current_path()}
            ```
            """
        )
    else:
        return textwrap.dedent(
            f"""
            ```
            the number should be between 1 and {len(todo_list[username]['uncompleted_items'])}
            {terminal_mode.current_path()}
            ```
            """
        )


def delete_todo_item(msg: str) -> str:
    if not msg:
        return terminal_mode.handle_command_error('del', 'format')

    try:
        index = int(msg) - 1
    except ValueError:
        return terminal_mode.handle_command_error('del', 'format')

    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)
    if 0 <= index < len(todo_list[username]['uncompleted_items']):
        del todo_list[username]['uncompleted_items'][index]
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

    todo_item_pattern = re.compile(f'^(\[.*?\])\s*(.*)$')

    if todo_list[username][task_status]:
        max_label_length = max(
            len(todo_item_pattern.search(todo_item).group(1))
            for todo_item in todo_list[username][task_status]
        )

    todo_list_len = len(todo_list[username][task_status])
    mx_index_len = len(str(todo_list_len + 1))

    sorted_todo_items = todo_list[username][task_status].copy()

    if sort_method == 'label':
        sorted_todo_items.sort(
            key=lambda x: todo_item_pattern.match(x).group(1)
        )

    user_todo_list = [f"total: {todo_list_len}", '']
    for todo_item in sorted_todo_items:
        index = todo_list[username][task_status].index(todo_item) + 1
        label_match = todo_item_pattern.search(todo_item)
        label = label_match.group(1)
        description = label_match.group(2)
        user_todo_item = f"{str(index).rjust(mx_index_len)}. {label.ljust(max_label_length)} {description}"
        if len(user_todo_item) > 80:
            user_todo_item = user_todo_item[:79] + '>'

        user_todo_list.append(user_todo_item)

    space = '\n' + ' ' * TAB_SIZE * 2
    user_todo_list = f"```{space.join(user_todo_list)}{space}```"
    return textwrap.dedent(
        f"""
        {user_todo_list}
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
        return add_todo_item(msg)

    elif msg.startswith('check'):
        msg = msg[6:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_check')
        return check_todo_item(msg)

    elif msg.startswith('del'):
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_del')
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
