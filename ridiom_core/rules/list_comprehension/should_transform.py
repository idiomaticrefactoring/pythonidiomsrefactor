import ast
from typing import Dict, Any


def _has_if_node(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.If):
            return True
    return False


def check(context: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """
    Check if transformation should proceed based on context and config.

    Args:
        context: Match context dictionary.
        config: Configuration dictionary.

    Returns:
        True if transformation should proceed, False otherwise.
    """
    refactor_with_if = config.get("refactor-with-if", True)

    # Calculate has_if here instead of relying on context
    for_node = context.get("for_node")
    has_if = False
    if for_node:
        has_if = _has_if_node(for_node)

    # If not allowing transforms with 'if', but code has 'if', skip
    if not refactor_with_if and has_if:
        return False

    return True
