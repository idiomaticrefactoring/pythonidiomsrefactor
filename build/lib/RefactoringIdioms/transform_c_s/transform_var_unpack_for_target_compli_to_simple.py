import sys,ast,traceback,os

abs_path=os.path.abspath(os.path.dirname(__file__))
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)



def create_list(num):
    # if num>1:
        a=[]
        for i in range(num-1):
            if a:
                a[-1].apppend([])
            else:
                a.append([])
        return a
def get_subscript_num(node):
    # count=0
    if isinstance(node.value,ast.Subscript):
        # print("count: ",count)
        return 1+get_subscript_num(node.value)
    else:
        return 1
    # return count
def get_subscript_index_not_last(node):
    # print("node: ",ast.unparse(node))
    if isinstance(node.value,ast.Subscript):
        a=[ast.unparse(node.slice)]
        a.extend(get_subscript_index_not_last(node.value))
        return a
    else:
        return [ast.unparse(node.slice)]


def build_node_list(node_list):

    pre_index=[]
    new_node_list=[]
    for ind, node in enumerate(node_list):
        cur_num=get_subscript_num(node)
        cur_index_list = get_subscript_index_not_last(node)[1:][::-1]
        last_ele = new_node_list
        list_num=cur_num-1
        for ind,cur_ind in enumerate(cur_index_list):
            if len(pre_index)>ind:
                if cur_ind!=pre_index[ind]:
                    break
                else:
                    list_num-=1
                    last_ele=last_ele[-1]
        for i in range(list_num):
            last_ele.append([])
            last_ele = last_ele[-1]


        last_ele.append(node)
        pre_index = cur_index_list
    return new_node_list
            # new list and then add it to the new list

def sort_node_list(node_list):
    map_dict=dict()
    node_str_list=[]
    for node in node_list:
        node_str=ast.unparse(node)
        node_str_list.append(node_str)
        map_dict[node_str]=node
    map_dict=sorted(map_dict.items(), key=lambda kv: (len(kv[0]),kv[0]))
    new_node_list=[]
    for e1,e2 in map_dict:
        new_node_list.append(e2)

    return build_node_list(new_node_list)





def build_pre_var_name(node):

    value = node.value
    var_name = ""
    if isinstance(value, ast.Subscript):
        var_name += build_pre_var_name(value)


    else:
        var_name = ast.unparse(value)

    return var_name
def get_beg(slice):
    if isinstance(slice,ast.Constant):
        return int(ast.unparse(slice)),int(ast.unparse(slice))
    elif isinstance(slice,ast.Slice):
        upper = int(ast.unparse(slice.upper)) if slice.upper else 'len'
        lower = int(ast.unparse(slice.lower)) if slice.lower else 0
        # step = ast.unparse(slice.step) if slice.step else '1'
        beg= lower

        return beg,upper
def add_node_before_beg(node,beg):
    pre_node=None
    cur_beg, cur_end = get_beg(node.slice)
    # print("beg: ",beg)
    # print("cur_beg, cur_end: ",cur_beg,beg, cur_end)
    if beg < cur_beg:
        pre_node_var_name = build_var(node).split("_")
        pre_node_var_name[-1] = str(cur_beg - 1)

        if cur_beg - beg > 1:
            pre_node = ast.Starred()
            pre_node.value = ast.Name("_".join(pre_node_var_name))

        else:
            pre_node = ast.Name("_".join(pre_node_var_name))
            # cur_end += 1
        # node_list.append(ast.unparse(pre_node))
    if cur_end == "len":
        print("the code1 need to be tested!")
        # break
        beg=cur_end
        # pre_node=None
        # return None,None,None
        # return beg, cur_beg, pre_node
    else:
        # beg = cur_end + 1
        beg = cur_end + 1
    return beg,cur_beg,pre_node
def get_slice(slice):
    if isinstance(slice,ast.Constant):
        return "_"+ast.unparse(slice)
    elif isinstance(slice,ast.Slice):
        upper=ast.unparse(slice.upper) if slice.upper else 'len'
        lower=ast.unparse(slice.lower) if slice.lower else '0'
        step=ast.unparse(slice.step) if slice.step else '1'

        return "_".join(["",lower,step,upper])
    else:
        return ""
def build_var(node):
    slice=node.slice
    value=node.value
    var_name=""
    if isinstance(value,ast.Subscript):
        var_name+=build_var(value)
        var_name+=get_slice(slice)

    else:
        var_name=ast.unparse(value)+get_slice(slice)
    return var_name
def add_cur_node(node):
    slice = node.slice
    var_name = build_var(node)
    if isinstance(slice, ast.Slice):
        var = ast.Starred()
        var.value = ast.Name(var_name)
    else:
        var = ast.Name(var_name)
    return var


def connect_slice_name(node):
    if isinstance(node, ast.Subscript):
        return [node]+connect_slice_name(node.value)
    else:
        return []
def get_first_node(node):
            if isinstance(node, list):

                return get_first_node(node[0])

            else:

                return node
def transform(node_list,new_list,depth,Map_var=None):
    beg=0
    last_node=None
    cannot_trans_list=[]
    star_count=0
    for node in node_list:
        if isinstance(node,list):
            first_node = get_first_node(node)

            cur_node = connect_slice_name(first_node)[::-1][depth - 1]
            # print("cur_node: ",ast.unparse(first_node),ast.unparse(cur_node),cur_node)
            beg, cur_beg,pre_node = add_node_before_beg(cur_node, beg)
            # if (not beg) and (not cur_beg) and (not pre_node):
            #     # cannot_trans_flag=1
            #     cannot_trans_list.append(node)
            #     new_list=[None]
            #     break


            if pre_node:
                if isinstance(pre_node,ast.Starred):
                    star_count+=1
                new_list.append(pre_node)
            new_list_2=[]
            the_cur_star_count=transform(node, new_list_2, depth+1,Map_var)
            if the_cur_star_count>1:
                return the_cur_star_count
            new_list.append(new_list_2)
        else:
            beg, cur_beg,pre_node = add_node_before_beg(node, beg )
            if pre_node:
                if isinstance(pre_node,ast.Starred):
                    star_count+=1

                new_list.append(pre_node)
            cur_node=add_cur_node(node)
            # Map_var[ast.unparse(cur_node)] = ast.unparse(node)
            Map_var[ast.unparse(node)] = cur_node

            new_list.append(cur_node)
            # new_list.append(ast.unparse(add_cur_node(node)))
    if beg!="len":
        # print("come here")
        fir_node = get_first_node(node_list[0])
        end_node = connect_slice_name(fir_node)[::-1][depth - 1]
        var_name=build_var(end_node).split("_")
        var_name[-1] = "len"
        last_node=ast.Starred()
        last_node.value=ast.Name("_".join(var_name))
        star_count += 1
        # new_list.append(ast.unparse(last_node))
        new_list.append(last_node)
    return star_count

def build_elts(new_node_list,tuple_list):
        for node in new_node_list:
            if isinstance(node,list):
                tuple = ast.Tuple()
                tuple.elts = []
                build_elts(node,tuple.elts )
                tuple_list.append(tuple)
            else:
                tuple_list.append(node)

class RewriteName(ast.NodeTransformer):
        def __init__(self,Map_var):
            self.Map_var=Map_var
        # def visit_Subscript(self, node):
        #     # print("visit_Subscript node: ", ast.unparse(node))
        #     if ast.unparse(node) in self.Map_var:
        #         # print("yes: ",ast.unparse(node))
        #         return self.Map_var[ast.unparse(node)]
        #     else:
        #         # node=RewriteName().visit(node)
        #         if isinstance(node.value,ast.Subscript):
        #             node.value=self.visit_Subscript(node.value)
        #         if isinstance(node.slice,ast.Subscript):
        #             node.slice = self.visit_Subscript(node.slice)
        #         return node
        def generic_visit(self, node):

            if ast.unparse(node) in self.Map_var:
                return self.Map_var[ast.unparse(node)]
            #
            for ind_field,k in enumerate(node._fields):
                # print("transfrom: ", k)
                try:

                # if 1:
                    v = getattr(node, k)
                    # print("here: ", k,v )
                    if isinstance(v,ast.AST):
                        if v._fields:
                            setattr(node, k, self.generic_visit(v))
                        # node._fields[k] = self.generic_visit(v)
                        pass
                    elif isinstance(v, list):

                        for ind,e in enumerate(v):
                            if hasattr(e,'_fields'):
                                v[ind]=self.generic_visit(e)
                        setattr(node, k, v)
                                # node._fields[k][ind]=self.generic_visit(e)
                                # pass
                except:
                    continue
                #     print("error: ", ast.unparse(v))
                #     if ast.unparse(v) in self.Map_var:
                #         setattr(node, k, self.Map_var[ast.unparse(v)])
                # #         # node._fields[k]= self.Map_var[ast.unparse(v)]
                #     continue
            #
            #
            return node


def transform_for_node_var_unpack(for_node,node_list,Map_var):
    try:
        node_list = sort_node_list(node_list)
        # print("node_list: ",node_list)
        # for node in node_list:
        #     print("node: ", ast.unparse(node))
        new_node_list = []

        star_count=transform(node_list, new_node_list, 1, Map_var)
        if star_count>1:
            return None
        tuple = ast.Tuple()
        tuple.elts = []
        build_elts(new_node_list, tuple.elts)
        # print("Map_var: ",Map_var)
        # for a in ast.walk(for_node):
        #     if ast.unparse(a) in Map_var:
        #         a = Map_var[ast.unparse(a)]
        #         print("yes: ", a)
        # print(ast.unparse(for_node))
        for_node.target = tuple
        # tree = ast.parse('foo', mode='eval')
        new_tree = RewriteName(Map_var).visit(for_node)
        return new_tree
    except:
        traceback.print_exc()
        return None
        # if None in new_node_list:
        #     print("come here")
        #     return None

        # print(ast.unparse(new_tree))

if __name__ == '__main__':
    code='''
# a[0]
# a[1]
# a[2]

# a[3][1:3]
# a[3][3]
# a[5][0][1]
# # a[3][5:][2][2]
# # a[3][1]
# # a[3][5:][2][2]
# # a[4][3]
# # a[2]
# # a[3][1:3]
# # a[3][5:][2][2]
# for quad in quads:
#     upper_edge_len = np.linalg.norm(quad[0] - quad[1])
#     upper_edge_list.append(upper_edge_len)
# for quad in poly_quads:
#     quad_h = (np.linalg.norm(quad[0] - quad[3]) + np.linalg.norm(quad[2] - quad[1])) / 2.0
#     height_list.append(quad_h)
# 这个不可以
# for e in mitie_entities:
#     if len(e[0]):
#         start = tokens[e[0][0]].start
#         end = tokens[e[0][-1]].end
#         entities.append({ENTITY_ATTRIBUTE_TYPE: e[1], ENTITY_ATTRIBUTE_VALUE: text[start:end], ENTITY_ATTRIBUTE_START: start, ENTITY_ATTRIBUTE_END: end, ENTITY_ATTRIBUTE_CONFIDENCE: None})

# for joint in annos:
#     if x <= joint[0][0] < x + target_size[0] and y <= joint[0][1] < y + target_size[1]:
#         break
# for point in joint:
#     if point[0] < -10 or point[1] < -10:
#         adjust_joint.append((-1000, -1000))
#         continue
#     (new_x, new_y) = (point[0] - x, point[1] - y)
#     if new_x > w - 1 or new_y > h - 1:
#         adjust_joint.append((-1000, -1000))
#         continue
#     adjust_joint.append((new_x, new_y))
# 这个不可以（有val[1]还有val[1][0],val[1][0]）
for val in sorted(npz.items()):
    logging.info('  Loading %s in %s' % (str(val[1][0].shape), val[0]))
    logging.info('  Loading %s in %s' % (str(val[1][1].shape), val[0]))
    weights.extend(val[1])
    if len(model.all_weights) == len(weights):
        break
'''

    tree=ast.parse(code)
    for_node=None
    node_list=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Subscript):
            print("node: ",ast.unparse(node))
            node_list.append(node)
        if isinstance(node,ast.For):
            for_node=node
    print(node_list)
    node_list = node_list[:2]#+node_list[5:6]
    Map_var = dict()
    transform_for_node_var_unpack(for_node, node_list,Map_var)
    '''
    test all code1
    print(sort_node_list(node_list))
    node_list=sort_node_list(node_list)
    new_node_list=[]
    Map_var=dict()
    transform(node_list, new_node_list, 1,Map_var)
    print("Map_var: ",Map_var)
    print("node_list: ",new_node_list)
    tuple = ast.Tuple()
    tuple.elts = []
    build_elts(new_node_list, tuple.elts)
    print("tuple: ",tuple,ast.unparse(tuple))
    new_code_tree=for_node
    for a in ast.walk(for_node):
        if a in Map_var:
            a=Map_var[a]
            print("yes: ",a)
    print("new_for: ",ast.unparse(for_node))
    for_node.target=tuple
    new_tree = RewriteName().visit(tree)
    print(ast.unparse(new_tree))
    '''

    '''
    test sort list
    node_list = [node_list[0], node_list[1], node_list[2]]
    node_list=sort_node_list(node_list)
    
    print_list(e_list)
    # for e,code1 in node_list:
    #     print(e,code1)
    '''

    # print(ast.unparse(build_target(node_list)))
    # 对找到的代码片段不断进行转换直至不可以转换
    # code_list=[
    #     ["user_check = self.run_function('file.get_user', [check])","mode_check = self.run_function('file.get_mode', [check])"],
    #     ["name = obj.find('name').text.strip()","bbox = obj.find('bndbox')"],
    #     ["self._tmp_path = tmp_path","self._config = config","self.location = str(tmp_path)"]]
    # # while 1:
    # save_complicated_code_dir = util.data_root + "complicated_code_dir/var_unpack_func_call_only_same_dengcha_subscript_complicated_pkl/"
    # for file_name in os.listdir(save_complicated_code_dir):
    #     complicate_code = util.load_pkl(save_complicated_code_dir, file_name[:-4])
    #     for each_file in complicate_code:
    #         # for code_list, file_path,file_html in each_file:
    #         #
    #         #     print("count: ",code_list)
    #         code_map = each_file[0]
    #         for node, item in code_map.items():
    #             print(">>>>>>>old code1: ", ast.unparse(node))
    #             transform_var_unpack_call(node, item)
    #
    #
    # test_save_complicated_code_dir = util.data_root + "test_complicated_code_dir/"
    # file_name = "var_unpack_func_call_only_same_dengcha_subscript_complicated"
    # map_code=util.load_pkl(test_save_complicated_code_dir,file_name)
    # for node, item in map_code.items():
    #     print(">>>>>>>old code1: ", ast.unparse(node))
    #     transform_var_unpack_call(node,item)
















