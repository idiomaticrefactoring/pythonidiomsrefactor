# -*- coding: utf-8 -*-
"""
Consolidated utility functions for file I/O and text processing.

Migrated from RefactoringIdioms/util.py and DeIdiom/util.py.
"""

import os
import json
import csv
import pickle
import tokenize
import token
from typing import List, Any, Optional


# ==========================================
# File I/O Functions
# ==========================================


def load_file_path(file_path: str, encoding: str = "utf-8") -> str:
    """Load file content as a string."""
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def load_file_path_lines(file_path: str, encoding: str = "utf-8") -> List[str]:
    """Load file content as a list of lines."""
    with open(file_path, "r", encoding=encoding) as f:
        return f.readlines()


def save_file_path(
    file_path: str, content: str, mode: str = "w", encoding: str = "utf-8"
) -> None:
    """Save content to a file, creating parent directories if needed."""
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, mode, encoding=encoding) as f:
        f.write(content)


def load_json_file_path(file_path: str) -> Any:
    """Load JSON from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file_path(file_path: str, data: Any, indent: int = 4) -> None:
    """Save data as JSON to a file."""
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_pkl(file_path: str) -> Any:
    """Load a pickle file."""
    with open(file_path, "rb") as f:
        return pickle.load(f)


def save_pkl(file_path: str, data: Any) -> None:
    """Save data to a pickle file."""
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


def load_csv(file_path: str) -> List[List[str]]:
    """Load a CSV file as a list of rows."""
    with open(file_path, "r", encoding="utf-8") as f:
        return list(csv.reader(f))


def save_csv(
    file_path: str, data: List[List[Any]], header: Optional[List[str]] = None
) -> None:
    """Save data to a CSV file."""
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        for row in data:
            writer.writerow(row)


# ==========================================
# Code Processing Functions
# ==========================================


def strip_comments_and_docstrings(source_path: str) -> str:
    """
    Strip comments and docstrings from a Python source file.

    This is useful for normalizing code before comparison.
    Originally from RefactoringIdioms/util.py:do_file()
    """
    with open(source_path, "r", encoding="utf-8") as source:
        new_str = ""
        prev_toktype = token.INDENT
        last_lineno = -1
        last_col = 0

        try:
            tokgen = tokenize.generate_tokens(source.readline)
            for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
                if slineno > last_lineno:
                    last_col = 0
                if scol > last_col:
                    new_str += " " * (scol - last_col)

                # Skip docstrings and comments
                if toktype == token.STRING and prev_toktype == token.INDENT:
                    pass  # Docstring
                elif toktype == tokenize.COMMENT:
                    pass  # Comment
                else:
                    new_str += ttext

                prev_toktype = toktype
                last_col = ecol
                last_lineno = elineno
        except tokenize.TokenizeError:
            # If tokenization fails, return empty string
            return ""

        return new_str


# ==========================================
# Python Built-in Names (for reference)
# ==========================================

PYTHON_BUILTINS = [
    "abs",
    "delattr",
    "hash",
    "memoryview",
    "set",
    "all",
    "dict",
    "help",
    "min",
    "setattr",
    "any",
    "dir",
    "hex",
    "next",
    "slice",
    "ascii",
    "divmod",
    "id",
    "object",
    "sorted",
    "bin",
    "enumerate",
    "input",
    "oct",
    "staticmethod",
    "bool",
    "eval",
    "int",
    "open",
    "str",
    "breakpoint",
    "exec",
    "isinstance",
    "ord",
    "sum",
    "bytearray",
    "filter",
    "issubclass",
    "pow",
    "super",
    "bytes",
    "float",
    "iter",
    "print",
    "tuple",
    "callable",
    "format",
    "len",
    "property",
    "type",
    "chr",
    "frozenset",
    "list",
    "range",
    "vars",
    "classmethod",
    "getattr",
    "locals",
    "repr",
    "zip",
    "compile",
    "globals",
    "map",
    "reversed",
    "__import__",
    "complex",
    "hasattr",
    "max",
    "round",
]

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
