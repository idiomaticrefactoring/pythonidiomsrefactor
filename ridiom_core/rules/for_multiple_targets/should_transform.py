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
    max_unpack = config.get("max-elements-to-unpack", False)

    if max_unpack and isinstance(max_unpack, int):
        var_list = context.get("var_list")
        if var_list and isinstance(var_list, list):
            if len(var_list) > max_unpack:
                return False

    return True
