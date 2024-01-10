import responses


import terminal_mode
import develop_mode


import textwrap


def traverse(data: dict, indent: int, bypass: list) -> str:
    tree = ""
    # just make sure the structure file is always a dict
    for key, value in sorted(data.items()):
        if key in bypass:
            continue
        #       structure indentation  folder   output indentation
        tree += f"{' ' * 4 * indent}\-- {key}\n{' ' * 4 * 2}"
        tree += traverse(value, indent + 1, bypass)
    
    return tree


def visualize_structure(data: dict, mode: str, username: str) -> str:

    current_path = ''
    if mode == 'terminal':
        current_path = terminal_mode.current_path()
    else:
        current_path = develop_mode.current_path()

    bypass = []
    if username != responses.author:
        bypass.append('author')

    return textwrap.dedent(f"""
        ```
        {traverse(data, 0, bypass)}
        {current_path}
        ```
    """) 
