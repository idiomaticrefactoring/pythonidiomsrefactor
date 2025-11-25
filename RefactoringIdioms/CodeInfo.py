from typing import List, Optional

class CodeInfo:
    """
    用于存储单个重构项详细信息的类。
    包含了文件位置、上下文（类/方法）、代码对比以及行号信息。
    """
    def __init__(
        self, 
        file_path: str, 
        idiom: str, 
        class_name: str, 
        method_name: str,
        complicated_code: str, 
        simple_code: str, 
        lineno: List[List[int]]
    ):
        self.file_path = file_path
        self.idiom = idiom
        self.class_name = class_name
        self.method_name = method_name
        self.complicated_code = complicated_code
        self.simple_code = simple_code
        self.lineno = lineno

    def lineno_str(self) -> str:
        """
        生成格式化的行号字符串，并自动合并相邻的行号段。
        例如: [[1, 2], [3, 4]] -> "lines 1 to 4"
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
        """生成代码对比部分的字符串"""
        lineno_info = self.lineno_str()
        return f"***{lineno_info}\n{self.complicated_code}\n-----is refactored into----->\n{self.simple_code}"

    def full_info(self) -> str:
        """
        生成完整的报告字符串，供 main.py 打印日志使用。
        格式: Filepath***Class***Method***Idiom***CodeDetails
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

