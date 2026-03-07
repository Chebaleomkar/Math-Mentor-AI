import math
from langchain_core.tools import tool

@tool
def execute_python(code: str) -> str:
    """Executes safe Python math operations for numerical calculations."""
    allowed_globals = {"math": math, "__builtins__": {}}
    try:
        result = eval(code, allowed_globals)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
