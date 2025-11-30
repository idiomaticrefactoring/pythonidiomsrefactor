import sys,ast, copy,os

abs_path=os.path.abspath(os.path.dirname(__file__))
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)
import util


def copy_compre(node):
    compr = ast.comprehension()
    compr.target = node.target
    compr.iter = node.iter
    compr.ifs=[]
    compr.is_async=None
    # print("compr: ",ast.unparse(compr))
    return compr


def for_transform(node,listcompre):
    # print("node: ",node,ast.unparse(node))

    if isinstance(node,ast.For):
        body = node.body[0]
        listcompre.generators.append(copy_compre(node))

        for_transform(body,listcompre)
        # print("come to the ast.For hahahha: ",ast.unparse(listcompre))

    elif isinstance(node,ast.If):
        body = node.body[0]
        if not node.orelse:
            listcompre.generators[-1].ifs.append(node.test)
            for_transform(body, listcompre)
            pass
        else:
            def if_else_transform(node,listcompre):
                if isinstance(node,ast.If):
                    ifexpr = ast.IfExp()
                    ifexpr.test = node.test
                    ifexpr.body = node.body[0].value
                    listcompre.key=node.body[0].targets[0].slice
                    ifexpr.orelse = if_else_transform(node.orelse[0],listcompre)
                    return ifexpr
                else:
                    return node.value



            listcompre.value =if_else_transform(node,listcompre)
            # ifexpr=ast.IfExp()
            # ifexpr.test=node.test
            #
            # ifexpr.body=body.value.args[0]
            # ifexpr.orelse=None
            # for_transform(node.orelse[0], ifexpr.orelse)
            #
            # # ifexpr.orelse=listcompre.elt
            # listcompre.elt = ifexpr

    else:
        # print("node:",ast.unparse(node))
        listcompre.key = node.targets[0].slice
        listcompre.value = node.value


def test_fun(a):
    a.id="change"
    print()
def transform(for_node, assign_node):
    new_code=copy.deepcopy(assign_node)

    listcompre=ast.DictComp()
    listcompre.generators=[]
    listcompre.key=None
    listcompre.value = None
    for_transform(for_node,listcompre)
    new_code.value = listcompre
    return new_code
def replace_file_content(for_node,assign_stmt,new_code,real_file_html,repo_name):
    rela_path = "/".join(real_file_html.split("/")[6:])
    file_path = "".join([util.data_root, "python_star_2000repo/", repo_name, "/", rela_path])
    content = util.load_file_path(file_path)
    res_copy = content.split("\n")
    indent = ""
    for ind, e in enumerate(res_copy[for_node.lineno - 1]):
        if e != " ":
            indent = " " * ind
            break

    res_copy[assign_stmt.lineno - 1] = indent + ast.unparse(new_code)
    res_copy[for_node.lineno - 2:for_node.end_lineno] = res_copy[for_node.lineno - 2:for_node.lineno - 1]
    return content,"\n".join(res_copy)
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
        else:  # 这个是一个赋值语句
            if isinstance(body, ast.Expr) and isinstance(body.value, ast.Call):
                args_if = ast.unparse(body.value.args)

            or_else = node.orelse[0]
            if isinstance(or_else, ast.Expr) and isinstance(or_else.value, ast.Call):
                args_or_else = ast.unparse(or_else.value.args)

                assign_str.append(args_if + " if " + ast.unparse(test) + " else " + args_or_else + " ")
            else:
                assign_str.append(args_if + " if " + ast.unparse(test) + " else ")
                traverse(or_else, complicate_code, assign_str)
            # print(args_or_else)
            # complicate_code.insert(0,args_if+" if " + ast.unparse(test) + " else "+args_or_else+" ")

    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        assign_str.append(ast.unparse(node.value.args) + " ")
        # complicate_code.insert(0,args_assign_expr)
if __name__ == '__main__':
    code='''
for (key, value) in input_dict.items():
    if 'rgb' in key or 'color' in key:
        rt_dict[key] = torch.FloatTensor(value).permute(2, 0, 1)[None, ...]
    else:
        rt_dict[key] = torch.FloatTensor(value)[None, None, ...]
'''
    tree= ast.parse(code)
    for_node = None
    ass_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            ass_node = node
        elif isinstance(node, ast.For):
            for_node = node

    new_code = transform(for_node, ass_node)
    print("new_code: ", ast.unparse(new_code))
    # complicate_code=[]
    # transform_node=[]
    # Var=""
    # #'''
    # complicate_code=[]
    # assign_left_code=[]
    # for node in ast.walk(tree):
    #     if isinstance(node,ast.Assign):
    #         left=node.targets
    #         Var=ast.unparse(left)
    #         assign_left_code.append(Var+" = [ ")
    #
    #
    #     elif isinstance(node,ast.For):
    #         assign_str=[]
    #         traverse(node, complicate_code,assign_str)
    #         complicate_code.insert(0,"".join(assign_str))
    #         complicate_code.append("]")
    #         break
    # assign_left_code.extend(complicate_code)
    # str_complicate_code="".join(assign_left_code)
    # print(str_complicate_code)
    #'''














