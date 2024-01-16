import responses


import json


apply_roles = [
    "developer",
    "guest"
]


def add_user_to_list(username: str, role: str):
    with open('../data/json/pending_role_list.json') as file:
        pending_role_list = json.load(file)
    
    pending_role_list[role].append(
        {
            "username": username
        }
    )

    with open('../data/json/pending_role_list.json', 'w') as file:
        json.dump(pending_role_list, file, indent=4)

def apply_for_role(msg: str, username: str) -> str:
    if msg in apply_roles:
        if msg == 'guest':
            if username in responses.special_guests:
                return 'you are already a special guest'
            else:
                add_user_to_list(username, 'guests')
                responses.load_user_identity_list()
                return 'added to pending list'

        elif msg == 'developer':
            if username in responses.developers:
                return 'you are already a developer'
            else:
                add_user_to_list(username, 'developers')
                responses.load_user_identity_list()
                return 'added to pending list'
        
    else:
        return f"no role: '{msg}'"