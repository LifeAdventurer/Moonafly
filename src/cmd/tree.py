import terminal_mode


import textwrap


def traverse(data: dict, indent: int) -> str:
    tree = ""
    # just make sure the structure file is always a dict
    for key, value in sorted(data.items()):
        #       structure indentation  folder   output indentation
        tree += f"{' ' * 4 * indent}\-- {key}\n{' ' * 4 * 2}"
        tree += traverse(value, indent + 1)
    
    return tree


def visualize_structure(data: dict) -> str:
    
    return textwrap.dedent(f"""
        ```
        {traverse(data, 0)}
        {terminal_mode.current_path()}
        ```
    """) 
