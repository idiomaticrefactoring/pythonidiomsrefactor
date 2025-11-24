import sys,ast, copy

# sys.path.append("/mnt/zejun/smp/code1/")

'''
变量映射函数，
对于当前的赋值语句的左边变量在后面赋值语句的右边变量中存在依赖关系，对当前赋值语句建立Map, 之后对后面所有赋值语句的变量进行变量替换
记录 第i个赋值语句，遍历后面赋值表达式进行节点替换，然后简化为多赋值语句
'''


class RewriteName(ast.NodeTransformer):
    def __init__(self, Map_var):
        super(RewriteName, self).__init__()
        self.Map_var = Map_var
    def visit_Name(self, node):

        # print("visit_Subscript node: ", ast.unparse(node))
        if ast.unparse(node) in self.Map_var:
            # print("yes: ",ast.unparse(node))
            return self.Map_var[ast.unparse(node)]
        else:

            return node

    def visit_Attribute(self, node):
        if ast.unparse(node) in self.Map_var:
            # print("yes: ",ast.unparse(node))
            return self.Map_var[ast.unparse(node)]
        else:

            if isinstance(node.value, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)):
                node.value = self.visit(node.value)
            # if node.attr in self.Map_var:
            #     node.attr = self.Map_var[node.attr]
            return node

    def visit_Subscript(self, node):
        if ast.unparse(node) in self.Map_var:
            # print("yes: ",ast.unparse(node))
            return self.Map_var[ast.unparse(node)]
        else:

            if isinstance(node.value, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)):
                node.value = self.visit(node.value)
            if isinstance(node.slice, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)):
                node.slice = self.visit(node.slice)

            return node

    def visit_Slice(self, node):
        if ast.unparse(node) in self.Map_var:
            return self.Map_var[ast.unparse(node)]
        else:
            if isinstance(node.lower, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)):
                node.lower = self.visit(node.lower)
            if isinstance(node.upper, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)):
                node.upper = self.visit(node.upper)
            if isinstance(node.step, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)):
                node.step = self.visit(node.step)
            return node
def is_depend(pre_tar, next_tar):
        pre_tar_str = ast.unparse(pre_tar)
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1

        return 0
def transform_multiple_assign(old_ass_list):
    # print("ass_list: ",ass_list)
    ass_list=copy.deepcopy(old_ass_list)
    remove_ind_list=set([])
    Map_var=dict()
    for ind, pre_ass in enumerate(ass_list[:-1]):

        for ind_e, next_ass in enumerate(ass_list[ind+1:]):
            # print("pre_ass,next_ass: ", ast.unparse(pre_ass),ast.unparse(next_ass))
            pre_tar=pre_ass.targets[0]
            next_value=next_ass.value
            if is_depend(pre_tar, next_value):
                # print("is depend: ")
                remove_ind_list.add(ind)
                pre_value =pre_ass.value
                Map_var={**Map_var,ast.unparse(pre_tar):pre_value}
                # ass_list[ind_e+ind+1] =RewriteName(Map_var).visit(next_ass)

    left=[]
    right=[]
    # print("remove_ind_list: ",remove_ind_list,Map_var)
    for ind,assign in enumerate(ass_list):
        if ind in remove_ind_list:
            continue
        # for key in Map_var:
        #     print("value: ",ast.unparse(Map_var[key]))
        # print("old_assign: ", assign,ast.unparse(assign),Map_var)
        # assign.value=RewriteName(Map_var).visit(assign.value)
        assign.value=RewriteName(Map_var).visit(assign.value)

        # print("assign: ",ast.unparse(assign.value))
        assign_str=ast.unparse(assign)
        # print("assign_str: ",assign_str,assign_str.split("="))
        vars=ast.unparse(assign).split("=")
        left.append(vars[0])
        right.append(ast.unparse(assign.value))
    return ", ".join(left)+" = "+", ".join(right)



if __name__ == '__main__':
    code='''
# self._tmp_path = tmp_path
# self._config = config
# self.location = str(tmp_path)

# print("split1")
# user_check = self.run_function('file.get_user', [check])
# mode_check = self.run_function('file.get_mode', [check])
# print("split2")
# name = obj.find('name').text.strip()
# bbox = obj.find('bndbox')
# pts = ['xmin', 'ymin', 'xmax', 'ymax']
# bndbox = []
# print("split3")
tmp_real = data[ii]
tmp_imag = data[ii + 1]
data[ii] = data[jj]
data[ii + 1] = data[jj + 1]
data[jj] = tmp_real
data[jj + 1] = tmp_imag
'''
    # 对找到的代码片段不断进行转换直至不可以转换
    code_list=[
        ["user_check = self.run_function('file.get_user', [check])","mode_check = self.run_function('file.get_mode', [check])"],
        ["name = obj.find('name').text.strip()","bbox = obj.find('bndbox')"],
        ["self._tmp_path = tmp_path","self._config = config","self.location = str(tmp_path)"]]
    # while 1:
    ass_list=[]
    tree=ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            ass_list.append(node)
    new_code = transform_multiple_assign(ass_list)
    print(new_code)

    # for code_frag in code_list:
    #         new_code=transform_multiple_assign(code_frag)
    #         print(new_code)















