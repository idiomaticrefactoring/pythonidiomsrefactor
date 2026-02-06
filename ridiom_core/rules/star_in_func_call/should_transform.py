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
    max_limit = config.get("max-elements-to-unpack", False)

    if max_limit and isinstance(max_limit, int):
        arg_info_list = context.get("arg_info_list")
        if arg_info_list and len(arg_info_list) > 0:
            arg_nodes = arg_info_list[0]
            if len(arg_nodes) > max_limit:
                return False

    return True
