import hashlib
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG, TAB_SIZE


def get_hash(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info("hash")

    if msg.startswith("list"):
        msg = msg[5:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info("hash_list")

        hash_algorithms = ("\n" + " " * TAB_SIZE * 3).join(
            sorted(hashlib.algorithms_available)
        )
        return textwrap.dedent(
            f"""
            ```
            {hash_algorithms}
            ```
            ```
            {terminal_mode.current_path()}
            ```
            """
        )

    parts = msg.split(maxsplit=1)

    if len(parts) != 2:
        return command_help.load_help_cmd_info("hash_algo")

    hash_algorithm, user_input = parts[0].lower(), parts[1]

    if hash_algorithm not in hashlib.algorithms_available:
        return textwrap.dedent(
            f"""
            ```
            Invalid hash algorithm.
            {terminal_mode.current_path()}
            ```
            """
        )

    hash_object = hashlib.new(hash_algorithm)
    hash_object.update(user_input.encode("utf-8"))

    return textwrap.dedent(
        f"""
        ```
        {hash_object.hexdigest()}
        ```
        ```
        {terminal_mode.current_path()}
        ```
        """
    )
