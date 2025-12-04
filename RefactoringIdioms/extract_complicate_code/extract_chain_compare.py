import sys
import ast
import os
import copy
import traceback

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if project_root not in sys.path:
    sys.path.append(project_root)

# ==========================================
# 模块导入
# ==========================================
from RefactoringIdioms.extract_simp_cmpl_data import ast_util

# ==========================================
# 核心逻辑: AST 合并与变换
# ==========================================
def get_pos(ele, one_var):
    """判断公共变量在比较式中的位置（左还是右）"""
    if one_var[0] == ele:
        return "l"
    else:
        return "r"

def merge(node1, node2):
    """合并两个比较节点：node1.ops + node2.ops"""
    ops = node2.ops
    comparator = node2.comparators
    for op, e in zip(ops, comparator):
        node1.ops.append(op)
        node1.comparators.append(e)
    return ast.unparse(node1)

def change_compare_node(node1):
    """翻转比较节点：a > b  -->  b < a"""
    new_node = copy.deepcopy(node1)
    # 交换左右
    new_node.left = node1.comparators[-1]
    new_node.comparators = node1.comparators[::-1][1:]
    new_node.comparators.append(node1.left)
    
    # 反转操作符
    for ind, op in enumerate(node1.ops[::-1]):
        if isinstance(op, ast.Gt):
            new_node.ops[ind] = ast.Lt()
        elif isinstance(op, ast.Lt):
            new_node.ops[ind] = ast.Gt()
        elif isinstance(op, ast.GtE):
            new_node.ops[ind] = ast.LtE()
        elif isinstance(op, ast.LtE):
            new_node.ops[ind] = ast.GtE()
        else:
            continue
    return new_node

def transform_left_right(pos1, pos2, node1, node2):
    """根据公共变量位置决定合并策略"""
    code = "" 
    node1_still_flag = 0

    # 特殊处理：如果包含 None 检查 (is/is not)，通常不能随意交换位置
    if isinstance(node1.ops[0], (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
        if pos1 == 'l' and ast.unparse(node1.comparators[0]) == 'None':
            node1.left, node1.comparators[0] = node1.comparators[0], node1.left
            pos1 = 'r'
            node1_still_flag = 1
            
    elif isinstance(node2.ops[0], (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
        if pos2 == 'l' and ast.unparse(node2.comparators[0]) == 'None':
            node2.left, node2.comparators[0] = node2.comparators[0], node2.left
            node1, node2 = node2, node1
            pos1, pos2 = 'r', pos1 
            node1_still_flag = 1

    # 策略表
    if pos1 == 'r' and pos2 == 'l':  # ... a < b AND b < c ...
        code = merge(node1, node2)
        
    elif pos1 == 'l' and pos2 == 'r':  # ... b > a AND b < c ...
        if node1_still_flag: return ""
        code = merge(node2, node1) # 尝试交换顺序合并
        
    elif pos1 == 'l' and pos2 == 'l':  # ... b > a AND c > b ...
        if isinstance(node1.ops[-1], (ast.NotIn, ast.In)) and isinstance(node2.ops[-1], (ast.NotIn, ast.In)):
            return ""
        elif isinstance(node1.ops[-1], (ast.NotIn, ast.In)):
            if node1_still_flag: return ""
            new_node = change_compare_node(node2)
            code = merge(new_node, node1)
        else:
            new_node = change_compare_node(node1)
            code = merge(new_node, node2)
            
    else:  # 右右: ... a < b AND c < b ...
        if isinstance(node1.ops[-1], (ast.NotIn, ast.In)) and isinstance(node2.ops[-1], (ast.NotIn, ast.In)):
            return ""
        elif isinstance(node2.ops[-1], (ast.NotIn, ast.In)):
            if node1_still_flag: return ""
            new_node = change_compare_node(node1)
            code = merge(node2, new_node)
        else:
            new_node = change_compare_node(node2)
            code = merge(node1, new_node)
            
    return code

def transform_remain_code(remain_vars_list, ignore_ind_list):
    """重新组装剩余未合并的代码"""
    code = []
    flag = 0 # 0表示放在后面
    for ind, e in enumerate(remain_vars_list):
        if ind in ignore_ind_list:
            continue
        if ind == 0:
            flag = 1
        code.append(ast.unparse(e[1]))
    return " and ".join(code), flag

def transform_chained_comparison(node):
    """尝试对 BoolOp(And) 进行一次合并"""
    if not (isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)):
        return 0, node

    vars_list = []
    values = node.values
    other_code = []
    
    for value in values:
        if isinstance(value, ast.Compare):
            left = value.left
            comparator = value.comparators[-1]
            vars = [[ast.unparse(left), ast.unparse(comparator)], value]
            vars_list.append(vars)

        else:
            other_code.append(ast.unparse(value))

            
    other_code_str = " and ".join(other_code) if other_code else ""
    remain_vars_list = copy.deepcopy(vars_list)
    
    # 两两比较寻找合并机会
    for ind, one_var in enumerate(vars_list):
        for ind_next in range(ind + 1, len(vars_list)):
            another_var = vars_list[ind_next]
            
            # 检查是否有公共变量
            common = set(one_var[0]) & set(another_var[0])
            if common:
                ele = list(common)[0]
                one_pos = get_pos(ele, one_var[0])
                another_pos = get_pos(ele, another_var[0])

                transform_code = transform_left_right(one_pos, another_pos, one_var[1], another_var[1])
                
                if not transform_code:
                    continue # 无法合并，尝试下一对

                # 组装新代码
                remain_code, pos_flag = transform_remain_code(remain_vars_list, [ind, ind_next])
                
                if remain_code:
                    if pos_flag:
                        remain_code = remain_code + " and " + transform_code
                    else:
                        remain_code = transform_code + " and " + remain_code
                else:
                    remain_code = transform_code
                
                if other_code_str:
                    final_code_str = remain_code + " and " + other_code_str
                else:
                    final_code_str = remain_code


                for node in ast.walk(ast.parse(remain_code  + other_code_str)):
                    if isinstance(node,ast.BoolOp) and isinstance(node.op, ast.And):

                        return 1, node
                    elif isinstance(node,ast.Compare):
                        return 1,node
                    
    return 0, node

def check_chained_comparison(tree, new_code_list, max_operands=False):
    """递归遍历 AST，迭代执行合并"""
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            old_node = copy.deepcopy(node)
            curr_node = node
            has_change = False
            
            # 迭代合并：因为 a<b and b<c and c<d 需要多次合并
            while True:
                flag, new_node = transform_chained_comparison(curr_node)
                if not flag:
                    break
                curr_node = new_node
                has_change = True
            
            if has_change:
                # [配置检查] 检查操作数数量限制
                if max_operands and isinstance(max_operands, int):
                    # 计算操作数数量 (ops 数量 + 1)
                    # 只有当结果是纯 Compare 节点时才方便计算
                    if isinstance(curr_node, ast.Compare):
                        operand_count = len(curr_node.ops) + 1
                        if operand_count > max_operands:
                            continue # 超过限制，跳过此重构
                
                new_code_list.append([old_node, curr_node])

# ==========================================
# 主入口函数 (适配 main.py)
# ==========================================

def get_chain_compare(content, config=None):
    if config is None:
        config = {}
        
    # 读取配置：最大操作数限制 (例如 a<b<c 是3个操作数)
    max_operands = config.get("max-operands-to-refactor", False)

    code_pair_list = []
    try:
        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)

        search_targets = ana_py.func_def_list if ana_py.func_def_list else [(file_tree, "Module")]

        for tree, class_name in search_targets:
            method_name = getattr(tree, "name", "")
            if isinstance(tree, ast.Module): method_name = "Global"
            
            new_code_list = []
            check_chained_comparison(tree, new_code_list, max_operands)

            for old_node, new_node in new_code_list:
                line_list = [[old_node.lineno, old_node.end_lineno]] if hasattr(old_node, "lineno") else []
                
                code_pair_list.append([
                    class_name,
                    method_name,
                    ast.unparse(old_node),
                    ast.unparse(new_node),
                    line_list
                ])
                
        return code_pair_list

    except Exception:
        traceback.print_exc()
        return []

if __name__ == '__main__':
    # 简单测试
    code = "if a < b and b < c and d > c: pass"
    print(get_chain_compare(code))
    print(get_chain_compare(code,config={"max-operands-to-refactor":2}))
    print(get_chain_compare(code,config={"max-operands-to-refactor":4}))



