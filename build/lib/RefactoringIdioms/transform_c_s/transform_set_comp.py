import sys, ast, copy, os

# ==========================================
# 最小化修改：路径与导入修复
# ==========================================
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if project_root not in sys.path:
    sys.path.append(project_root)

from RefactoringIdioms import util


def copy_compre(node):
    compr = ast.comprehension()
    compr.target = node.target
    compr.iter = node.iter
    compr.ifs = []
    # 兼容性修复：防止在 Python 3.8+ 中报错
    compr.is_async = getattr(node, 'is_async', 0)
    return compr

def for_transform(node, listcompre):
    if isinstance(node, ast.For):
        body = node.body[0]
        listcompre.generators.append(copy_compre(node))
        for_transform(body, listcompre)

    elif isinstance(node, ast.If):
        body = node.body[0]
        if not node.orelse:
            listcompre.generators[-1].ifs.append(node.test)
            for_transform(body, listcompre)
        else:
            def if_else_transform(node):
                if isinstance(node, ast.If):
                    ifexpr = ast.IfExp()
                    ifexpr.test = node.test
                    ifexpr.body = node.body[0].value.args[0]
                    ifexpr.orelse = if_else_transform(node.orelse[0])
                    return ifexpr
                else:
                    return node.value.args[0]

            listcompre.elt = if_else_transform(node)
    else:
        # 处理 set.add(x) 的情况
        listcompre.elt = node.value.args[0]

def test_fun(a):
    a.id = "change"
    print()

def transform(for_node, assign_node):
    """
    核心转换函数：生成 SetComp 节点
    """
    new_code = copy.deepcopy(assign_node)
    
    # 这里明确创建的是 SetComp (集合推导式)
    listcompre = ast.SetComp()
    listcompre.generators = []
    listcompre.elt = None
    for_transform(for_node, listcompre)
    new_code.value = listcompre
    return new_code

def replace_file_content(for_node, assign_stmt, new_code, real_file_html, repo_name):
    # 保留原有功能，增加安全检查
    if util is None:
        return "", ""
        
    rela_path = "/".join(real_file_html.split("/")[6:])
    data_root = getattr(util, 'data_root', '')
    file_path = "".join([data_root, "python_star_2000repo/", repo_name, "/", rela_path])
    
    try:
        content = util.load_file_path(file_path)
        res_copy = content.split("\n")
        indent = ""
        for ind, e in enumerate(res_copy[for_node.lineno - 1]):
            if e != " ":
                indent = " " * ind
                break

        res_copy[assign_stmt.lineno - 1] = indent + ast.unparse(new_code)
        res_copy[for_node.lineno - 2:for_node.end_lineno] = res_copy[for_node.lineno - 2:for_node.lineno - 1]
        return content, "\n".join(res_copy)
    except Exception:
        return "", ""

def traverse(node, complicate_code, assign_str):
    if isinstance(node, ast.For):
        target = node.target
        iter = node.iter
        body = node.body[0]
        complicate_code.append("for " + ast.unparse(target) + " in " + ast.unparse(iter) + " ")
        traverse(body, complicate_code, assign_str)

    elif isinstance(node, ast.If):
        test = node.test
        body = node.body[0]
        if not node.orelse:
            complicate_code.append("if " + ast.unparse(test) + " ")
            traverse(body, complicate_code, assign_str)
        else: 
            if isinstance(body, ast.Expr) and isinstance(body.value, ast.Call):
                args_if = ast.unparse(body.value.args)

            or_else = node.orelse[0]
            if isinstance(or_else, ast.Expr) and isinstance(or_else.value, ast.Call):
                args_or_else = ast.unparse(or_else.value.args)
                assign_str.append(args_if + " if " + ast.unparse(test) + " else " + args_or_else + " ")
            else:
                assign_str.append(args_if + " if " + ast.unparse(test) + " else ")
                traverse(or_else, complicate_code, assign_str)

    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        assign_str.append(ast.unparse(node.value.args) + " ")

if __name__ == '__main__':
    pass






