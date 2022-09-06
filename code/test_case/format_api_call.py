import os
import sys
import json
import ast
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")

import util
from multiprocessing import Pool
from func_calls_visitor import get_func_calls
def get_path_by_extension(root_dir, flag='.py'):
    paths = []
    for root, dirs, files in os.walk(root_dir):
        files = [f for f in files if not f[0] == '.']  # skip hidden files such as git files
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for f in files:
            if f.endswith(flag):
                paths.append(os.path.join(root, f))
    return paths
# visit assignment statements
class AssignVisitor(ast.NodeVisitor):
    def __init__(self):
        self.class_obj = {}
    def visit_Assign(self, node):
        call_name = get_func_calls(node.value)
        # for an assignment and its right side has a function call
        # map this function call to its left
        if len(call_name)>0 and isinstance(node.targets[0],ast.Name):
            self.class_obj[node.targets[0].id] = call_name[-1][0]
        return node

def get_api_ref_id(tree):
    id2fullname  = {}  # key is the imported module while the value is the prefix
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            items = [nn.__dict__ for nn in node.names]
            for d in items:
                if d['asname'] is None:  # alias name not found, use its imported name
                    id2fullname[d['name']] = d['name']
                else:
                    id2fullname[d['asname']] = d['name'] # otherwise , use alias name
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            # for import from statements
            # module names are the head of a API name
            items = [nn.__dict__ for nn in node.names]
            for d in items:
                if d['asname'] is None: # alias name not found
                    id2fullname[d['name']] = node.module+'.'+d['name']
                else:
                    id2fullname[d['asname']] = node.module+'.'+d['name']
    return id2fullname

# formating function calls
def func_call_format(func_call_names, id2fullname):
    result = []
    for elt in func_call_names:
        name = elt[0]
        kw = elt[1]
        name_parts = name.split('.')
        if name_parts[0] in id2fullname:
            full_name = id2fullname[name_parts[0]] + '.'+ ".".join(name_parts[1:])
            result += [full_name.rstrip('.')]#+":"+kw
        else:
            result += [name]#+":"+kw
    return result

def get_API_calls(tree,id2fullname,class2obj):
    try:
        # tree = ast.parse(code, mode='exec')

        func_calls_names = get_func_calls(tree)
        new_func_calls_names = []
        for name, param in func_calls_names:
            name_parts = name.split('.')  # object value
            if name_parts[0] in class2obj and len(name_parts)==2:
                new_func_calls_names +=[(class2obj[name_parts[0]]+'.'+'.'.join(name_parts[1:]), param)]
            else:
                new_func_calls_names.append((name,param))

        func_calls_names = func_call_format(new_func_calls_names, id2fullname)
        return func_calls_names
    except (SyntaxError,ValueError):  # to avoid non-python code
        return []
def get_call(file_tree,tree):
    id2fullname = get_api_ref_id(file_tree)
    visitor = AssignVisitor()
    visitor.visit(file_tree)
    class2obj = visitor.class_obj
    func_calls_names = get_API_calls(tree, id2fullname, class2obj)
    return func_calls_names

if __name__ == '__main__':
    file_path=util.data_root +'python_star_2000repo/edx-platform/openedx/tests/completion_integration/test_views.py'
    # try:
    if 1:
        content = util.load_file_path(file_path)
        file_tree = ast.parse(content, mode='exec')
        id2fullname = get_api_ref_id(file_tree)
        visitor = AssignVisitor()
        visitor.visit(file_tree)
        class2obj = visitor.class_obj
        # id2fullname = get_api_ref_id(file_tree)
        # func_calls_names = get_API_calls(file_tree,id2fullname,class2obj)
        # for call in func_calls_names:
        #     print("call: ",call)
        # print()
        # ana_py = ast_util.Analyzer()
        # ana_py.visit(file_tree)
        # code_list = []
        # print("func number: ", len(ana_py.func_def_list))
        # count = 0
        # for tree in ana_py.func_def_list:
        #     if hasattr(tree, "name"):
        #         print("fun name: ", tree.name)
        #     func_calls_names=get_API_calls(tree,id2fullname,class2obj)
        #     for call in func_calls_names:
        #         print("call: ",call)
    # except:
    #     print(f"{file_path} is not existed!")

