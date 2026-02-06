import ast
from typing import Dict, Any


def check(context: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """
    Check if transformation should proceed based on context and config.

    Args:
        context: Match context dictionary.
        config: Configuration dictionary.

    Returns:
        True if transformation should proceed, False otherwise.
    """
    max_operands = config.get("max-operands-to-refactor", False)

    if max_operands and isinstance(max_operands, int):
        new_node = context.get("new_node")
        if new_node and isinstance(new_node, ast.Compare):
            operand_count = len(new_node.ops) + 1
            if operand_count > max_operands:
                return False

    return True
