# -*- coding: utf-8 -*-
"""
Rules subpackage - contains all idiom detection rules.

Each rule is registered automatically when the module is imported.
All rules now use the new modular architecture.
"""

# Import all modular rule packages to trigger registration
from .list_comprehension import ListComprehensionRule
from .dict_comprehension import DictComprehensionRule
from .set_comprehension import SetComprehensionRule
from .chain_comparison import ChainComparisonRule
from .truth_value_test import TruthValueTestRule
from .for_else import ForElseRule
from .assign_multiple_targets import AssignMultipleTargetsRule
from .star_in_func_call import StarInFuncCallRule
from .for_multiple_targets import ForMultipleTargetsRule

__all__ = [
    "ListComprehensionRule",
    "DictComprehensionRule",
    "SetComprehensionRule",
    "ChainComparisonRule",
    "TruthValueTestRule",
    "ForElseRule",
    "AssignMultipleTargetsRule",
    "StarInFuncCallRule",
    "ForMultipleTargetsRule",
]
