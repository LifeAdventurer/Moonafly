import responses
import terminal_mode


import textwrap
import json


roles = [
    "developers",
    "guests"
]


def show_pending_role_list() -> str:

    with open('../data/json/pending_role_list.json') as file:
        pending_role_list = json.load(file)
    
    content = ['pending role list:', ' ']

    for role in roles:
        content.append(role + ':' + ' ' * (32 - len(role)) + 'index')

        for index, data in enumerate(pending_role_list[role]):
            # discord usernames must be between 2 and 32
            content.append(data['username'] + ' ' * (35 - len(data['username'])) + str(index))

        content.append(' ')

    content = ('\n' + ' ' * 4 * 2).join(content)

    return textwrap.dedent(f"""
        ```
        {content}
        {terminal_mode.current_path()}
        ```
    """)


def approve_pending(msg: str) -> str:
    with open('../data/json/pending_role_list.json') as file:
        pending_role_list = json.load(file)

    with open('../data/json/user_identity.json') as file:
        user_identity = json.load(file)
    
    for role in roles:
        if msg.startswith(role):
            msg = msg[len(role):].strip()
            
            list_len = len(pending_role_list[role])

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
    if msg == 'show':
        return show_pending_role_list()

    elif msg[:7] == 'approve':
        return approve_pending(msg[7:].strip())
    
    else:
        return terminal_mode.command_not_found(msg)