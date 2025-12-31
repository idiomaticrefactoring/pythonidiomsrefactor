import argparse
import os
import sys
import toml
import fnmatch
from typing import List, Dict, Callable, Any, Tuple

# ==========================================
# 0. 环境设置与依赖导入
# ==========================================
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
if project_root not in sys.path:
    sys.path.append(project_root)

import RefactoringIdioms.util as util
import RefactoringIdioms.CodeInfo as CodeInfo
# 导入具体的重构逻辑模块
from RefactoringIdioms.extract_complicate_code import (
    extract_assign_multiple as assign_multi_mod,
    extract_chain_compare as chain_compare_mod,
    extract_for_else as for_else_mod,
    extract_for_multiple_target as for_multi_target_mod,
    extract_star_call as star_call_mod,
    extract_truth_value as truth_value_mod
)
from RefactoringIdioms.extract_complicate_code.comprehension import (
    extract_dict_comprehension as dict_comp_mod,
    extract_list_comprehension as list_comp_mod,
    extract_set_comprehension as set_comp_mod
)

# ==========================================
# 1. 辅助函数
# ==========================================

def load_config(config_path="ridiom.toml"):
    """加载 TOML 配置文件"""
    if os.path.exists(config_path):
        try:
            return toml.load(config_path)
        except Exception as e:
            raise RuntimeError(f"配置文件损坏: {e}") from e
    return {}

def check_noqa(file_lines: List[str], lineno_list: List[List[int]]) -> bool:
    """
    检查指定行号范围内是否存在 '# noqa' 注释。
    """
    if not file_lines:
        return False
        
    for start, end in lineno_list:
        # lineno 是 1-based，列表索引是 0-based
        # 使用 max/min 防止行号越界
        start_idx = max(0, start - 1)
        end_idx = min(len(file_lines), end)
        
        for i in range(start_idx, end_idx):
            if "# noqa" in file_lines[i]:
                return True
    return False

def get_target_files(base_paths: List[str], exclude_patterns: List[str]) -> List[str]:
    """
    根据 include (base_paths) 和 exclude 模式扫描所有 .py 文件
    """
    target_files = []
    
    for base_path in base_paths:
        if base_path == ".":
            base_path = os.getcwd()
            
        if os.path.isfile(base_path):
            target_files.append(base_path)
            continue

        for root, dirs, files in os.walk(base_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pat) for pat in exclude_patterns)]
            
            for file in files:
                if not file.endswith(".py"):
                    continue
                
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, os.getcwd())
                
                # 过滤文件
                if any(fnmatch.fnmatch(relpath, pat) or fnmatch.fnmatch(file, pat) for pat in exclude_patterns):
                    continue
                
                target_files.append(filepath)
                
    return target_files

# ==========================================
# 2. 规则映射与装饰器 (Rule Mapping)
# ==========================================

def wrap_idiom_func(func, name):
    """
    闭包装饰器：
    1. 统一调用接口，支持传入配置
    2. 自动插入 Idiom 名称
    """
    def wrapper(code_frag, config: Dict[str, Any] = None):
        print(f">>> Checking {name}...")
        # 尝试将细粒度配置 (config) 传递给底层函数
        
        if config is not None:
            results = func(code_frag, config=config)
        else:
            results = func(code_frag)

        # 统一处理结果格式，确保第一项是 Idiom 名称
        if results:
            for item in results:
                if item and item[0] != name:
                    item.insert(0, name)
        return results
    return wrapper

# 核心映射表
IDIOM_MAPPING: Dict[str, List[Callable]] = {
    "list-comprehension": [wrap_idiom_func(list_comp_mod.get_list_compreh, "List Comprehension")],
    "set-comprehension": [wrap_idiom_func(set_comp_mod.get_set_compreh, "Set Comprehension")],
    "dict-comprehension": [wrap_idiom_func(dict_comp_mod.get_dict_compreh, "Dict Comprehension")],
    "chain-comparison": [wrap_idiom_func(chain_compare_mod.get_chain_compare, "Chain Compare")],
    "truth-value-test": [wrap_idiom_func(truth_value_mod.get_truth_value_test_code, "Truth Value Test")],
    "for-else": [wrap_idiom_func(for_else_mod.transform_for_else_code, "For Else")],
    "assign-multiple-targets": [wrap_idiom_func(assign_multi_mod.transform_multiple_assign_code, "Assign Multi Targets")],
    "star-in-func-call": [wrap_idiom_func(star_call_mod.transform_star_call_code, "Call Star")],
    "for-multiple-targets": [wrap_idiom_func(for_multi_target_mod.transform_for_multiple_targets_code, "For Multi Targets")]
}

# ==========================================
# 3. 处理逻辑 (Core Logic)
# ==========================================

def process_single_file(
    filepath: str, 
    active_rules_map: Dict[str, List[Callable]], 
    tool_config: Dict, 
    output_list: List
):
    """
    对单个文件运行所有激活的重构规则，并在此处显式处理 noqa 过滤
    """
    print(f"************ Processing {os.path.basename(filepath)} ************")
    # 1. 加载 AST (用于分析)
    try:
        code_frag = util.load_file_path(file_path=filepath)
    except Exception as e:
        raise RuntimeError(f"Failed to load AST for {filepath}: {e}") from e

    # 2. 读取源码行 (用于 noqa 检查)
    file_lines = []
    enable_noqa = tool_config.get("enable-noqa", True)
    if enable_noqa:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_lines = f.readlines()
        except FileNotFoundError:
            print(f"⚠️  Warning: Cannot read {filepath} for noqa check (file not found)")
        except PermissionError:
            print(f"⚠️  Warning: Cannot read {filepath} for noqa check (permission denied)")
        except Exception as e:
            print(f"⚠️  Warning: Cannot read {filepath} for noqa check: {e}")

    file_results = []
    rules_config = tool_config.get("rules", {})

    # 3. 遍历规则并执行
    for rule_name, func_list in active_rules_map.items():
        # 获取该规则在配置文件中的细粒度配置
        specific_config = rules_config.get(rule_name, {})
        
        for func in func_list:
            try:
                # 传入配置参数运行检测
                results = func(code_frag, config=specific_config)
                
                if results:
                    # 如果启用了 noqa，过滤掉包含禁止注释的结果
                    if enable_noqa and file_lines:
                        valid_results = []
                        for res in results:
                            # 结果解包: [Idiom, cl, me, old, new, lineno_list]
                            # lineno_list 通常在最后
                            *_, lineno_list = res
                            
                            # 只有当该范围内没有 noqa 时才保留
                            if not check_noqa(file_lines, lineno_list):
                                valid_results.append(res)
                        file_results.extend(valid_results)
                    else:
                        # 没启用 noqa 或没读到源码，直接保留所有结果
                        file_results.extend(results)
                        
            except Exception as e:
                print(f"Error executing rule '{rule_name}' on {filepath}: {e}")

    # 4. 格式化并输出
    if file_results:
        print(f"************ Result Summary of {os.path.basename(filepath)} ************")
        for ind, res in enumerate(file_results):
            idiom, cl, me, oldcode, new_code, *rest = res
            lineno_list = rest[0] if rest else []
            
            # 使用关键字参数构造 CodeInfo
            code_info = CodeInfo.CodeInfo(
                file_path=filepath, 
                idiom=idiom, 
                class_name=cl, 
                method_name=me, 
                complicated_code=oldcode, 
                simple_code=new_code, 
                lineno=lineno_list
            )
            print(f">>> Result {ind+1} \n{code_info.full_info()}")
            output_list.append(code_info.__dict__)
        print(f"************ End of {os.path.basename(filepath)} ************\n")

# ==========================================
# 4. 主程序入口
# ==========================================

def main():
    parser = argparse.ArgumentParser(description='RefactoringIdioms: Detect and refactor non-idiomatic Python code.')
    parser.add_argument('--config', type=str, default='ridiom.toml', help='Path to ridiom.toml config file')
    parser.add_argument('--filepath', type=str, help='Override target path (file or directory)')
    parser.add_argument('--outputpath', type=str, default='result.json', help='Output JSON file path')
    args = parser.parse_args()

    # --- 加载配置 ---
    config = load_config(args.config)
    tool_conf = config.get("ridiom", {})
    rules_conf = tool_conf.get("rules", {})

    # --- 扫描文件 ---
    include_paths = [args.filepath] if args.filepath else tool_conf.get("include", ["."])
    exclude_patterns = tool_conf.get("exclude", [])
    target_files = get_target_files(include_paths, exclude_patterns)
    print(f"Found {len(target_files)} python files to analyze.")

    # --- 激活规则 ---
    select_rules = rules_conf.get("select", [])
    ignore_rules = rules_conf.get("ignore", [])
    active_rules_map = {}
    
    if not select_rules or "All" in select_rules:
        candidate_keys = IDIOM_MAPPING.keys()
    else:
        candidate_keys = select_rules

    for key in candidate_keys:
        if key in ignore_rules:
            continue
        if key in IDIOM_MAPPING:
            active_rules_map[key] = IDIOM_MAPPING[key]
        else:
            print(f"Warning: Unknown rule '{key}' in configuration.")

    if not active_rules_map:
        print("No active rules selected. Exiting.")
        return

    # --- 执行分析 ---
    all_results = []
    for filepath in target_files:
        process_single_file(filepath, active_rules_map, tool_conf, all_results)

    # --- 保存结果 ---
    util.save_json_file_path(args.outputpath, all_results)
    print(f"Analysis finished! Results saved to {args.outputpath}")

if __name__ == '__main__':
    main()