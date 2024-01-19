import terminal_mode 


from cmd import command_help


import textwrap
import random


# constants
HELP_FLAG = '--help'


def is_prime(num: int, k: int) -> bool:
    if num < 2:
        return False
    if num == 2 or num == 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    
    r = 0
    d = num - 1
    while d % 2 == 0:
        r += 1
        d //= 2

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
    if msg.startswith(HELP_FLAG):
        return command_help('primes')

    if msg.isdigit() and int(msg) > 0:
        return textwrap.dedent(f"""
            ```
            {is_prime(int(msg), 100)}
            {terminal_mode.current_path()}
            ```
        """)    

    else:
        return textwrap.dedent(f"""
            ```
            please enter a positive integer
            {terminal_mode.current_path()}
            ```
        """)