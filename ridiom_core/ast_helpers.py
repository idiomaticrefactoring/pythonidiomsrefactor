# -*- coding: utf-8 -*-
"""
AST helper classes and functions.

Migrated from RefactoringIdioms/extract_simp_cmpl_data/ast_util.py
and DeIdiom/util.py.
"""

import ast
from typing import List, Tuple, Any, Optional


class FunAnalyzer(ast.NodeVisitor):
    """
    AST visitor that collects function and method definitions.

    This is used to find all callable units in a module for analysis.
    Each entry in func_def_list is [node, class_name] where class_name
    is empty string for top-level functions.
    """

    def __init__(self, class_name: str = ""):
        self.func_def_list: List[Tuple[ast.AST, str]] = []
        self.class_name = class_name

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.func_def_list.append((node, self.class_name))
        ast.NodeVisitor.generic_visit(self, node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.func_def_list.append((node, self.class_name))
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Create a new analyzer for the class body
        class_analyzer = FunAnalyzer(node.name)
        for stmt in node.body:
            class_analyzer.visit(stmt)
        self.func_def_list.extend(class_analyzer.func_def_list)

    def visit_If(self, node: ast.If) -> None:
        # Treat if __name__ == '__main__' as a pseudo-function
        try:
            if ast.unparse(node.test) == "__name__ == '__main__'":
                self.func_def_list.append((node, ""))
        except Exception:
            pass

    def generic_visit(self, node: ast.AST) -> None:
        ast.NodeVisitor.generic_visit(self, node)


def get_basic_count(node: ast.AST) -> int:
    """
    Count the number of basic elements in a tuple/list expression.

    For example, (a, b, c) returns 3, while a returns 1.
    """
    if isinstance(node, (ast.Tuple, ast.List)):
        count = 0
        for elt in node.elts:
            count += get_basic_count(elt)
        return count
    return 1


def get_basic_objects(node: ast.AST, var_list: Optional[List[str]] = None) -> List[str]:
    """
    Extract all variable names from a tuple/list expression.

    For example, (a, b, c) returns ['a', 'b', 'c'].
    """
    if var_list is None:
        var_list = []

    if isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            get_basic_objects(elt, var_list)
    else:
        var_list.append(ast.unparse(node))

    return var_list


def visit_vars(target: ast.AST, var_list: Optional[List[str]] = None) -> List[str]:
    """
    Recursively extract all variable references from an AST node.

    Includes Names, Subscripts, and Attributes.
    """
    if var_list is None:
        var_list = []

    if isinstance(target, (ast.Name, ast.Subscript, ast.Attribute)):
        var_list.append(ast.unparse(target))
        for child in ast.iter_child_nodes(target):
            visit_vars(child, var_list)
    else:
        for child in ast.iter_child_nodes(target):
            visit_vars(child, var_list)

    return var_list


def visit_vars_real(target: ast.AST, var_list: Optional[List[str]] = None) -> List[str]:
    """
    Extract variable references, handling Call nodes specially.

    For method calls like obj.method(arg), extracts 'obj' and the arguments.
    """
    if var_list is None:
        var_list = []

    if isinstance(target, (ast.Name, ast.Subscript, ast.Attribute)):
        var_list.append(ast.unparse(target))
    elif isinstance(target, ast.Call):
        if isinstance(target.func, ast.Attribute):
            var_list.append(ast.unparse(target.func.value))
            for arg in target.args:
                visit_vars_real(arg, var_list)
        else:
            for arg in target.args:
                visit_vars_real(arg, var_list)
    else:
        for child in ast.iter_child_nodes(target):
            visit_vars_real(child, var_list)

    return var_list


def visit_func_calls(
    target: ast.AST, func_list: Optional[List[str]] = None
) -> List[str]:
    """
    Extract all function/method call names from an AST node.
    """
    if func_list is None:
        func_list = []

    if isinstance(target, ast.Call):
        func_list.append(ast.unparse(target.func))
        for arg in target.args:
            visit_func_calls(arg, func_list)
    else:
        for child in ast.iter_child_nodes(target):
            visit_func_calls(child, func_list)

    return func_list


# ==========================================
# Python Keywords (from ast_util.py)
# ==========================================

PYTHON_KEYWORDS = [
    "False",
    "await",
    "else",
    "import",
    "pass",
    "None",
    "break",
    "except",
    "in",
    "raise",
    "True",
    "class",
    "finally",
    "is",
    "return",
    "and",
    "continue",
    "for",
    "lambda",
    "try",
    "as",
    "def",
    "from",
    "nonlocal",
    "while",
    "assert",
    "del",
    "global",
    "not",
    "with",
    "async",
    "elif",
    "if",
    "or",
    "yield",
]

# Legacy alias for backward compatibility
Keywords = PYTHON_KEYWORDS


# ==========================================
# Additional AST Utilities (from ast_util.py)
# ==========================================


def set_dict_class_code_list(
    tree: ast.AST, dict_class: dict, class_name: str, new_code_list: List[Any]
) -> None:
    """
    Helper function to organize code by class and method.
    """
    me_name = tree.name if hasattr(tree, "name") else "if_main_my"
    me_lineno = tree.lineno
    me_id = f"{me_name}${me_lineno}"

    if class_name not in dict_class:
        dict_class[class_name] = {}
    dict_class[class_name][me_id] = new_code_list


def extract_ast_block_node(node: ast.AST, node_list: List[Any]) -> None:
    """
    Recursively extract AST block nodes into a list.
    """
    for k in node._fields:
        v = getattr(node, k)
        if isinstance(v, list):
            a = []
            for e in v:
                a.append(e)
                if isinstance(e, ast.AST):
                    extract_ast_block_node(e, node_list)
            node_list.append(a)
        elif isinstance(v, ast.AST):
            if v._fields:
                extract_ast_block_node(v, node_list)


def extract_ast_cur_layer_node(node: ast.AST, node_list: List[Any]) -> None:
    """
    Extract AST nodes at the current layer into a list.
    """
    for k in node._fields:
        v = getattr(node, k)
        if isinstance(v, list):
            a = []
            for e in v:
                a.append(e)
            node_list.append(a)
            for e in v:
                if hasattr(e, "_fields") and e._fields:
                    extract_ast_block_node(e, node_list)
        elif isinstance(v, ast.AST):
            if v._fields:
                extract_ast_block_node(v, node_list)


# ==========================================
# Truth Value Test Utilities
# (from extract_compli_truth_value_test_code.py)
# ==========================================


def decide_compare_complicate_truth_value(test: ast.Compare) -> int:
    """
    Determine if a comparison is a 'complicated' truth value test.

    Returns 1 if the comparison can be simplified using truth value testing,
    0 otherwise.

    A comparison is considered 'complicated' if it compares against
    falsy values like None, True, False, 0, empty collections, etc.
    """
    flag = 0
    ops = test.ops
    left = ast.unparse(test.left)
    comparators = test.comparators
    comp_str = ast.unparse(comparators[0])

    # Falsy values that can use truth value testing
    empty_list = [
        "None",
        "True",
        "False",
        "0",
        "0.0",
        "0j",
        "Decimal(0)",
        "Fraction(0, 1)",
        "",
        "()",
        "[]",
        "{}",
        "dict()",
        "set()",
        "range(0)",
    ]

    if len(ops) == 1 and isinstance(ops[0], (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
        if left in empty_list or comp_str in empty_list:
            flag = 1

    return flag


# ==========================================
# Legacy Aliases for Backward Compatibility
# ==========================================

# Alias for old ast_util.py class name
Fun_Analyzer = FunAnalyzer
Analyzer = FunAnalyzer

# Alias for old function names
get_basic_object = get_basic_objects
