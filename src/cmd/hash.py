import terminal_mode


from cmd import command_help


import hashlib
import textwrap


# constants
HELP_FLAG = '--help'
TAB_SIZE = 4


def get_hash(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('hash')

    if msg[:4] == 'show':
        msg = msg[4:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info('hash_show')

        hash_algorithms = ('\n' + ' ' * TAB_SIZE * 3).join(sorted(hashlib.algorithms_available))
        return textwrap.dedent(f"""
            ```
            {hash_algorithms}
            {terminal_mode.current_path()}
            ```
        """)

    parts = msg.split(maxsplit=1)

    if len(parts) != 2:
        return command_help.load_help_cmd_info('hash_algo')
    
    hash_algorithm, user_input = parts[0].lower(), parts[1]

    if hash_algorithm not in hashlib.algorithms_available:
        return textwrap.dedent(f"""
            ```
            Invalid hash algorithm.
            {terminal_mode.current_path()}
            ```
        """)

    hash_object = hashlib.new(hash_algorithm)
    hash_object.update(user_input.encode('utf-8')) 

    return textwrap.dedent(f"""
        ```
        {hash_object.hexdigest()}
        {terminal_mode.current_path()}
        ```
    """)