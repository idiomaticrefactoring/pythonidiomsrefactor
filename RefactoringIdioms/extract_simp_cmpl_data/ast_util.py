import ast
Keywords=["False",      "await",      "else",       "import",     "pass",
"None",       "break",      "except",     "in",         "raise",
"True",       "class",      "finally",    "is",         "return",
"and",        "continue",   "for",        "lambda",     "try",
"as",         "def",        "from",       "nonlocal",   "while",
"assert",     "del",       "global",     "not",        "with",
"async",      "elif",       "if",         "or",         "yield"]
class Fun_Analyzer(ast.NodeVisitor):
    def __init__(self,class_name=""):
        self.func_def_list = []
        self.class_name = class_name
    def visit_FunctionDef(self, node):
        self.func_def_list.append([node, self.class_name])
        ast.NodeVisitor.generic_visit(self, node)
    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_ClassDef(self, node):

        class_ana=Fun_Analyzer(node.name)
        for stmt in node.body:
            class_ana.visit(stmt)
        self.func_def_list.extend(class_ana.func_def_list)
    def visit_If(self, node: ast.If):
        if ast.unparse(node.test) == "__name__ == '__main__'":
            self.func_def_list.append([node,""])
class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.func_def_list = []

    def visit_FunctionDef(self,node):
        self.func_def_list.append(node)
    def visit_If(self, node: ast.If):
        if ast.unparse(node.test)=="__name__ == '__main__'":
            self.func_def_list.append(node)
def set_dict_class_code_list(tree,dict_class,class_name,new_code_list):
    me_name = tree.name if hasattr(tree, "name") else "if_main_my"
    me_lineno = tree.lineno
    me_id = "".join([me_name, "$", str(me_lineno)])

    if class_name not in dict_class:
        dict_class[class_name] = dict()
        dict_class[class_name][me_id] = new_code_list
    else:

        dict_class[class_name][me_id] = new_code_list

def get_basic_count(e):

    count=0
    # print("e dict: ",e.__dict__)
    if isinstance(e, (ast.Tuple,ast.List)):
        # count += len(e.elts)
        for cur in e.elts:
            count +=get_basic_count(cur)

    else:
        # print(e.__dict__, " are not been parsed")
        count +=1


    return count
def get_basic_object(e,var_list=[]):
    if isinstance(e, (ast.Tuple,ast.List)):
        # count += len(e.elts)
        for cur in e.elts:
            get_basic_object(cur,var_list)

    else:
        # print(e.__dict__, " are not been parsed")
        var_list.append(ast.unparse(e))


def extract_ast_block_node(node,node_list):
    for k in node._fields:

        v = getattr(node, k)

        if isinstance(v, list):
            # print("come here", v)
            a=[]
            for e in v:
                a.append(e)
                if isinstance(e, ast.AST):
                    extract_ast_block_node(e, node_list)
            node_list.append(a)
        elif isinstance(v, ast.AST):
            # print("come here", v.__dict__)
            if v._fields:
                extract_ast_block_node(v,node_list)
def extract_ast_cur_layer_node(node,node_list):
    # if node._fields:
    #     node_list.append(list(node._fields))
    for k in node._fields:
        v = getattr(node, k)

        if isinstance(v, list):
            a = []
            for e in v:
                a.append(e)
            node_list.append(a)
            for e in v:
                if e._fields:
                    extract_ast_block_node(e, node_list)


        elif isinstance(v, ast.AST):
            if v._fields:
                extract_ast_block_node(v, node_list)

if __name__ == '__main__':
    code='''
a.b=2
if label_names:
    a=2
    num_tensors_in_label = len(label_names)
else:
    num_tensors_in_label = int(has_labels)
# a=1
# b=c.b+1
a=1
b=2
c,d=1,2
for i in range(2):
    a=1
    if i>1:
        if i>2:
            a=3
        a=2
        break 
if a==2:
    print(1)
print("1")   
def a():
    return 1
for i in range(5):
    a=1
    break
if a:
    print("test")
if __name__ == '__main__':
    a=1
    
'''
    tree = ast.parse(code)
    node_list=[]
    extract_ast_cur_layer_node(tree, node_list)
    for e in node_list:
        print(e)
