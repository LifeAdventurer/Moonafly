import terminal_mode


import hashlib
import textwrap


def get_hash(msg: str) -> str:

    if msg == 'show':
        hash_algorithms = ('\n' + ' ' * 4 * 3).join(hashlib.algorithms_available)
        return textwrap.dedent(f"""
            ```
            {hash_algorithms}
            {terminal_mode.current_path()}
            ```
        """)

    parts = msg.split(maxsplit=1)

    if len(parts) != 2:
        return textwrap.dedent(f"""
            ```
            Invalid input format. Please provide the hash algorithm and string separated by space.
            {terminal_mode.current_path()}
            ```
        """)
    
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