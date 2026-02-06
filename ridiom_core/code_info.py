# -*- coding: utf-8 -*-
"""
CodeInfo class for storing refactoring result details.

Migrated from utils/CodeInfo.py.
"""

from typing import List


class CodeInfo:
    """
    Class for storing detailed information about a single refactoring result.
    Contains file location, context (class/method), code comparison, and line numbers.
    """

    def __init__(
        self,
        file_path: str,
        idiom: str,
        class_name: str,
        method_name: str,
        old_code: str,
        new_code: str,
        lineno: List[List[int]],
    ):
        self.file_path = file_path
        self.idiom = idiom
        self.class_name = class_name
        self.method_name = method_name
        self.old_code = old_code
        self.new_code = new_code
        self.lineno = lineno

    def lineno_str(self) -> str:
        """
        Generate a formatted line number string, merging adjacent line ranges.
        Example: [[1, 2], [3, 4]] -> "lines 1 to 4"
        """
        if not self.lineno:
            return ""

        # 确保行号是按顺序排列的
        sorted_lines = sorted(self.lineno, key=lambda x: x[0])
        merged = []

        for start, end in sorted_lines:
            if not merged:
                merged.append([start, end])
            else:
                last_start, last_end = merged[-1]
                # 如果当前段的开始行 紧接在 上一段结束行之后（或重叠），则合并
                if start <= last_end + 1:
                    merged[-1][1] = max(last_end, end)
                else:
                    merged.append([start, end])

        return ", ".join([f"lines {start} to {end}" for start, end in merged])

    def code_str(self) -> str:
        """Generate the string representation of the code comparison."""
        lineno_info = self.lineno_str()
        return f"***{lineno_info}\n{self.old_code}\n-----is refactored into----->\n{self.new_code}"

    def full_info(self) -> str:
        """
        Generate the full report string for logging in main.py.
        Format: Filepath***Class***Method***Idiom***CodeDetails
        """
        parts = [f"Filepath: {self.file_path}"]

        if self.class_name:
            parts.append(f"Class: {self.class_name}")

        if self.method_name:
            parts.append(f"Method: {self.method_name}")

        parts.append(f"Idiom: {self.idiom}")
        parts.append(self.code_str())

        return "***".join(parts)

    def __str__(self):
        return self.full_info()
