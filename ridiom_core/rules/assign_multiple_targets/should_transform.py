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
    max_assignments = config.get("max-assignments-to-refactor", False)

    if max_assignments and isinstance(max_assignments, int) and max_assignments > 0:
        assigns = context.get("assigns")
        if assigns and isinstance(assigns, list):
            if len(assigns) > max_assignments:
                return False

    return True
