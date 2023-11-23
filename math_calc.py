import ast
import math

# define the whitelist of allowed commands
allowed_names = {'sum', 'min', 'max', 'abs', 'round', 'math', 'pow', 'sqrt', 'sin', 'cos', 'tan', 'ceil', 'floor', 'exp', 'log', 'log10', 'degrees', 'radians', 'fabs', 'prod', 'remainder', 'cbrt'}

def safe_eval(msg) -> str:
  # parse the expression into an AST
  try:
    parsed_expr = ast.parse(msg, mode = 'eval')
  except SyntaxError:
    return 'SyntaxError'

  # !IMPORTANT check that only allowed names and functions are used
  for node in ast.walk(parsed_expr):
    if isinstance(node, ast.Name):
      if not (hasattr(node, 'id') and node.id is not None and node.id in allowed_names):
        return f"Name '{getattr(node, 'id', 'Unknown')}' is not allowed"
  
  # Evaluate the expression
  try:
    result = eval(compile(parsed_expr, filename="<string>", mode="eval"))
    return str(result)
  except (SyntaxError, ValueError) as e:
    return f"Error during evaluation: {e}"
