import random
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG


def is_prime(num: int, k: int) -> bool:
    """
    Check if a given number is a prime number using the Miller-Rabin primality test.

    Args:
        num (int): The number to be checked for primality.
        k (int): The number of iterations for the Miller-Rabin test.

    Returns:
        bool: True if the number is likely prime, False otherwise.
    """
    if num < 2:
        return False
    if num == 2 or num == 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False

    r, d = 0, num - 1
    while d % 2 == 0:
        r, d = r + 1, d // 2

    for _ in range(k):
        a = random.randint(2, num - 2)
        x = pow(a, d, num)
        if x == 1 or x == num - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, num)
            if x == num - 1:
                break

        else:
            return False

    return True


def check_prime(msg: str) -> str:
    """
    Check if a given message represents a positive integer and whether it is a prime number.

    Args:
        msg (str): The input message.

    Returns:
        str: A formatted string with the result of primality test and current terminal path.
    """
    if msg.isdigit() and int(msg) > 0:
        return textwrap.dedent(
            f"""
            ```
            {is_prime(int(msg), 100)}
            {terminal_mode.current_path()}
            ```
            """
        )

    return textwrap.dedent(
        f"""
        ```
        please enter a positive integer
        {terminal_mode.current_path()}
        ```
        """
    )


def get_primes_response(msg: str) -> str:
    """
    Get the response for prime-related commands.

    Args:
        msg (str): The input message.

    Returns:
        str: The formatted response based on the command and current terminal path.
    """
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info("primes")

    if msg.startswith("check"):
        msg = msg[6:].strip()
        if msg.startswith(HELP_FLAG):
            return command_help.load_help_cmd_info("primes_check")

        return check_prime(msg)

    return terminal_mode.command_not_found(msg)
