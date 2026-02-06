# -*- coding: utf-8 -*-
"""
ridiom_core - Unified core package for Ridiom refactoring tool.

This package provides:
- BaseRule: Abstract base class for all idiom rules
- RuleRegistry: Automatic rule discovery and registration
- Config: Global configuration context
- Utility functions for file I/O and AST processing
"""

from .base_rule import BaseRule, RuleResult, Match
from .registry import RuleRegistry
from .config import Config, load_config
from .utils import load_file_path, save_json_file_path, load_file_path_lines
from .ast_helpers import (
    FunAnalyzer,
    Fun_Analyzer,
    Keywords,
    PYTHON_KEYWORDS,
    get_basic_count,
    get_basic_objects,
    get_basic_object,
    set_dict_class_code_list,
    extract_ast_block_node,
    extract_ast_cur_layer_node,
    decide_compare_complicate_truth_value,
)
from .code_info import CodeInfo

__all__ = [
    "BaseRule",
    "RuleResult",
    "Match",
    "RuleRegistry",
    "Config",
    "load_config",
    "load_file_path",
    "save_json_file_path",
    "load_file_path_lines",
    "FunAnalyzer",
    "Fun_Analyzer",
    "Keywords",
    "PYTHON_KEYWORDS",
    "get_basic_count",
    "get_basic_objects",
    "get_basic_object",
    "set_dict_class_code_list",
    "extract_ast_block_node",
    "extract_ast_cur_layer_node",
    "decide_compare_complicate_truth_value",
    "CodeInfo",
]
