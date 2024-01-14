import terminal_mode 


from cmd import command_help


import textwrap


def is_prime(num) -> bool:
    if num < 2:
        return False
    if num == 2 or num == 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    
    i = 5
    a = 2
    while i * i <= num:
        if num % i == 0:
            return False
        i += a
        a = 6 - a

    return True


def check_prime(msg: str) -> str:
    if msg[:6] == '--help':
        return command_help('primes')

    if msg.isdigit() and int(msg) > 0:
        return textwrap.dedent(f"""
            ```
            {is_prime(int(msg))}
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