import json
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


def list_todo_items(task_status: str = 'uncompleted_items') -> str:
    todo_list = load_todo_list()
    username = responses.terminal_mode_current_using_user
    if username not in todo_list:
        todo_list = init_todo_list_for_user(username)

    user_todo_list = []
    mx_index_len = len(str(len(todo_list[username][task_status]) + 1))
    for index, todo_item in enumerate(todo_list[username][task_status]):
        user_todo_item = f"{str(index + 1).rjust(mx_index_len)}. {todo_item}"
        if len(user_todo_item) > 80:
            user_todo_item = user_todo_item[:79] + '>'

        user_todo_list.append(user_todo_item)
    space = '\n' + ' ' * TAB_SIZE * 2
    return textwrap.dedent(
        f"""
        ```
        {space.join(user_todo_list)}
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

    elif msg.startswith('list'):
        msg = msg[5:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('todo_list')
        if msg.startswith('-c'):
            return list_todo_items('completed_items')
        return list_todo_items()
    else:
        return terminal_mode.command_not_found(msg)
