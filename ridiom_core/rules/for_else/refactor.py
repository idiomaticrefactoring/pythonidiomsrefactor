# -*- coding: utf-8 -*-
"""
For-Else - Refactor transformation (fully self-contained).

The transform is already computed in extractor, just returns the new_code from context.
"""

import ast
from typing import Dict, Any

from ...base_rule import Match


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform flag+for+if pattern to for-else (already computed in detect)."""
    return match.context.get("new_code", match.old_code)
