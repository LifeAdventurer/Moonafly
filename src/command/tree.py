import textwrap

import develop_mode
import responses
import terminal_mode

# constants
TAB_SIZE = 4


def traverse(data: dict, indent: int, bypass: list) -> str:
    tree = ""
    # just make sure the structure file is always a dict
    for key, value in sorted(data.items()):
        if key in bypass:
            continue
        #       structure indentation  folder   output indentation
        tree += f"{' ' * TAB_SIZE * indent}\-- {key}\n{' ' * TAB_SIZE * 2}"
        tree += traverse(value, indent + 1, bypass)

    return tree


def visualize_structure(data: dict) -> str:

    current_path = ''
    if responses.is_terminal_mode == True:
        current_path = terminal_mode.current_path()
    elif responses.is_develop_mode == True:
        current_path = develop_mode.current_path()

    bypass = []
    if (
        responses.is_terminal_mode == True
        and responses.terminal_mode_current_using_user != responses.author
    ):
        bypass.append('author')

    return textwrap.dedent(
        f"""
        ```
        {traverse(data, 0, bypass)}
        {current_path}
        ```
    """
    )
