import responses
import terminal_mode


from cmd import command_help


import textwrap
import json


# constants
HELP_FLAG = '--help'


roles = [
    "developers",
    "guests"
]


def show_pending_role_list() -> str:
    try:
        with open('../data/json/pending_role_list.json') as file:
            pending_role_list = json.load(file)
    except FileNotFoundError:
        pending_role_list = {
            "developers": [],
            "guests": []
        }
        with open('../data/json/pending_role_list.json', 'w') as file:
            json.dump(pending_role_list, file)
    
    content = ['pending role list:', ' ']

    for role in roles:
        if len(pending_role_list[role]) == 0:
            continue

        content.append(role + ':' + ' ' * (32 - len(role)) + 'index')

        for index, data in enumerate(pending_role_list[role]):
            # discord usernames must be between 2 and 32
            content.append(data['username'] + ' ' * (35 - len(data['username'])) + str(index))

        content.append(' ')

    if len(content) == 2:
        return textwrap.dedent(f"""
            ```
            no user pending for roles
            {terminal_mode.current_path()}
            ```
        """)

    content = ('\n' + ' ' * 4 * 2).join(content)

    return textwrap.dedent(f"""
        ```
        {content}
        {terminal_mode.current_path()}
        ```
    """)


def approve_pending(msg: str) -> str:
    try:
        with open('../data/json/pending_role_list.json') as file:
            pending_role_list = json.load(file)
    except FileNotFoundError:
        pending_role_list = {
            "developers": [],
            "guests": []
        }
        with open('../data/json/pending_role_list.json', 'w') as file:
            json.dump(pending_role_list, file)

    with open('../data/json/user_identity.json') as file:
        user_identity = json.load(file)
    
    for role in roles:
        if msg.startswith(role):
            msg = msg[len(role):].strip()
            
            list_len = len(pending_role_list[role])

            if list_len == 0:
                return textwrap.dedent(f"""
                    ```
                    no one applying for {role}
                    {terminal_mode.current_path()}
                    ```
                """)

            if msg.isdigit() and 0 <= int(msg) <= list_len - 1:
                index = int(msg)
                username = pending_role_list[role][index]['username']
                user_identity[role].append(username)

                with open('../data/json/user_identity.json', 'w') as file:
                    json.dump(user_identity, file, indent=4)

                responses.load_user_identity_list()

                pending_role_list[role].pop(index)

                with open('../data/json/pending_role_list.json', 'w') as file:
                    json.dump(pending_role_list, file, indent=4)
                
                return textwrap.dedent(f"""
                    ```
                    {username} has been added to role '{role}'
                    {terminal_mode.current_path()}
                    ```
                """)

            else:
                return textwrap.dedent(f"""
                    ```
                    enter a integer between 0 and {list_len - 1}
                    {terminal_mode.current_path()}
                    ```
                """)
    
    return textwrap.dedent(f"""
        ```
        no role: {msg.split()[0]}
        {terminal_mode.current_path()}
        ```
    """)


def approve_requests(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('approve')


    if msg[:4] == 'show':
        msg = msg[4:].strip()
        
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('approve_show')

        return show_pending_role_list()

    elif msg[:7] == 'approve':
        msg = msg[7:].strip()

        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('approve_approve')

        return approve_pending(msg)
    
    else:
        return terminal_mode.command_not_found(msg)