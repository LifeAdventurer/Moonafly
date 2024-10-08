import ast
import json
import textwrap

import terminal_mode
from command import command_help
from constants import HELP_FLAG

# define the whitelist of allowed commands
math_calc_allow_names = []


def load_math_calc_allow_names():
    global math_calc_allow_names
    with open("../data/json/math_calc_allow_names.json") as file:
        math_calc_allow_names = json.load(file)["math_calc_allow_names"]


def safe_eval(msg: str) -> str:
    load_math_calc_allow_names()
    # parse the expression into an AST
    try:
        parsed_expr = ast.parse(msg, mode="eval")
    except SyntaxError:
        return "SyntaxError"

    # !IMPORTANT check that only allowed names and functions are used
    for node in ast.walk(parsed_expr):
        if isinstance(node, ast.Name):
            if not (
                hasattr(node, "id")
                and node.id is not None
                and node.id in math_calc_allow_names
            ):
                return f"Name '{getattr(node, 'id', 'Unknown')}' is not allowed"

    # Evaluate the expression
    try:
        result = eval(compile(parsed_expr, filename="<string>", mode="eval"))
        return str(result)
    except (SyntaxError, ValueError) as e:
        return f"Error during evaluation: {e}"


def get_math_calc_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info("math_calc")

    return textwrap.dedent(
        f"""
        ```
        {safe_eval(msg)}
        {terminal_mode.current_path()}
        ```
        """
    )
