import sys,ast,os
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/transform_c_s")


def transform_c_s_truth_value_test_no_len(node):
    def convert_func_var(node):
        # left_str = ast.unparse(node)
        func_name = ast.unparse(node.func)
        if func_name in ["bool"]:
            c =  ast.Name(ast.unparse(node.args[0]))
            # c=ast.Call(  ast.Name('list'),args=[node.args[0]],keywords=[])

            return c#node.args[0]
        return node
    empty_set=["None", "False", "0", "0.0", "0j", "Decimal(0)", "Fraction(0, 1)", '', "()","[]", "{}", "dict()", "set()", "range(0)"]
    true_set=["True"]
    op = node.ops[0]
    comp_code_node=None
    left = node.left
    comparator = node.comparators[0]
    if isinstance(left, ast.Call):

        left_node = convert_func_var(left)
        comparator_node = comparator
        # print("come here call: ", ast.unparse(left),ast.unparse(left_node),ast.unparse(comparator_node))
    elif isinstance(comparator, ast.Call):
        left_node = left
        comparator_node = convert_func_var(comparator)
    else:
        left_node = left
        comparator_node = comparator
    left_str=ast.unparse(left_node)
    comparator_str=ast.unparse(comparator_node)
    if left_str in empty_set:
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node=ast.UnaryOp()
            comp_code_node.op=ast.Not()
            comp_code_node.operand=comparator_node
            complicate_code = "not " + comparator_str
        else:
            comp_code_node=comparator_node
            complicate_code = comparator_str
    elif comparator_str in empty_set:
        # print("come here")
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node = ast.UnaryOp()
            comp_code_node.op = ast.Not()
            comp_code_node.operand = left_node
            complicate_code = "not " + left_str
        else:
            comp_code_node = left_node
            complicate_code = left_str
    elif left_str in true_set:
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node=comparator
        else:
            comp_code_node = ast.UnaryOp()
            comp_code_node.op = ast.Not()
            comp_code_node.operand = comparator_node
    elif comparator_str in true_set:
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node=left
        else:
            comp_code_node = ast.UnaryOp()
            comp_code_node.op = ast.Not()
            comp_code_node.operand = left_node



    return comp_code_node
def transform_c_s_truth_value_test(node):
    def convert_func_var(node):
        # left_str = ast.unparse(node)
        func_name = ast.unparse(node.func)
        if func_name in ["len", "bool"]:
            # left_str = ast.unparse(node.args[0])
            c=ast.Call(  ast.Name('list'),args=[node.args[0]],keywords=[])

            return c#node.args[0]
        return node
    empty_set=["None", "False", "0", "0.0", "0j", "Decimal(0)", "Fraction(0, 1)", '', "()","[]", "{}", "dict()", "set()", "range(0)"]
    true_set=["True"]
    op = node.ops[0]
    comp_code_node=None
    left = node.left
    comparator = node.comparators[0]
    if isinstance(left, ast.Call):

        left_node = convert_func_var(left)
        comparator_node = comparator
        # print("come here call: ", ast.unparse(left),ast.unparse(left_node),ast.unparse(comparator_node))
    elif isinstance(comparator, ast.Call):
        left_node = left
        comparator_node = convert_func_var(comparator)
    else:
        left_node = left
        comparator_node = comparator
    left_str=ast.unparse(left_node)
    comparator_str=ast.unparse(comparator_node)
    if left_str in empty_set:
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node=ast.UnaryOp()
            comp_code_node.op=ast.Not()
            comp_code_node.operand=comparator_node
            complicate_code = "not " + comparator_str
        else:
            comp_code_node=comparator_node
            complicate_code = comparator_str
    elif comparator_str in empty_set:
        # print("come here")
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node = ast.UnaryOp()
            comp_code_node.op = ast.Not()
            comp_code_node.operand = left_node
            complicate_code = "not " + left_str
        else:
            comp_code_node = left_node
            complicate_code = left_str
    elif left_str in true_set:
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node=comparator
        else:
            comp_code_node = ast.UnaryOp()
            comp_code_node.op = ast.Not()
            comp_code_node.operand = comparator_node
    elif comparator_str in true_set:
        if isinstance(op, (ast.Eq, ast.Is)):
            comp_code_node=left
        else:
            comp_code_node = ast.UnaryOp()
            comp_code_node.op = ast.Not()
            comp_code_node.operand = left_node



    return comp_code_node
# def traverse(node, complicate_code, assign_str):
#     if isinstance(node, ast.For):
#         target = node.target
#         iter = node.iter
#         body = node.body[0]
#         complicate_code.append("for " + ast.unparse(target) + " in " + ast.unparse(iter) + " ")
#         traverse(body, complicate_code, assign_str)
#
#
#
#     elif isinstance(node, ast.If):
#         test = node.test
#         body = node.body[0]
#         if not node.orelse:
#
#             complicate_code.append("if " + ast.unparse(test) + " ")
#             traverse(body, complicate_code, assign_str)
#         else:  # 这个是一个赋值语句
#             if isinstance(body, ast.Expr) and isinstance(body.value, ast.Call):
#                 args_if = ast.unparse(body.value.args)
#
#             or_else = node.orelse[0]
#             if isinstance(or_else, ast.Expr) and isinstance(or_else.value, ast.Call):
#                 args_or_else = ast.unparse(or_else.value.args)
#
#                 assign_str.append(args_if + " if " + ast.unparse(test) + " else " + args_or_else + " ")
#             else:
#                 assign_str.append(args_if + " if " + ast.unparse(test) + " else ")
#                 traverse(or_else, complicate_code, assign_str)
#             # print(args_or_else)
#             # complicate_code.insert(0,args_if+" if " + ast.unparse(test) + " else "+args_or_else+" ")
#
#     elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
#         assign_str.append(ast.unparse(node.value.args) + " ")
        # complicate_code.insert(0,args_assign_expr)
if __name__ == '__main__':
    code='''
ri[0].methods == []
#a==0
#pipfile_path is None
#self.top_freq == 0.0
#config['offscreen_rendering'] is True
#len(np.sum(np.abs(image[..., 0] - image[..., 1]))) == 0
# 0 != len(np.sum(np.abs(image[..., 0] - image[..., 1]))) 

# inpaint_iter!= 0
'''
    empty_set=["None", "False", "0", "0.0", "0j", "Decimal(0)", "Fraction(0, 1)", '', "()","[]", "{}", "dict()", "set()", "range(0)"]

    tree= ast.parse(code)

    complicate_code=""
    def convert_func_var(node):
        left_str = ast.unparse(node)
        func_name = ast.unparse(node.func)
        if func_name in ["len", "bool"]:
            left_str = ast.unparse(node.args[0])
        return left_str


    for node in ast.walk(tree):

        if isinstance(node,ast.Compare):
            complicate_code=transform_c_s_truth_value_test(node)
            # op=node.ops[0]
            # left=node.left
            # comparator=node.comparators[0]
            # if isinstance(left,ast.Call):
            #     left_str=convert_func_var(left)
            #     comparator_str = ast.unparse(comparator)
            # elif isinstance(comparator,ast.Call):
            #     left_str=ast.unparse(left)
            #     comparator_str = convert_func_var(comparator)
            # else:
            #     left_str=ast.unparse(left)
            #     comparator_str=ast.unparse(comparator)
            #
            # if left_str in empty_set:
            #     if isinstance(op,(ast.Eq,ast.Is)):
            #         complicate_code="not "+comparator_str
            #     else:
            #         complicate_code = comparator_str
            # else:
            #     # print("come here")
            #     if isinstance(op,(ast.Eq,ast.Is)):
            #         complicate_code="not "+left_str
            #     else:
            #         complicate_code = left_str
    print(ast.unparse(complicate_code))















