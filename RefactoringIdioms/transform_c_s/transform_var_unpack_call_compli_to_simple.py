import sys,ast,os

abs_path=os.path.abspath(os.path.dirname(__file__))
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)
# sys.path.append("/mnt/zejun/smp/code1/")
import util
from sympy import *

def build_star_node(arg_value_list,step):
    # star_node = ast.Starred()
    # star_node.value = ast.Subscript()
    # print("star node: ", ast.unparse(star_node))
    # star_node.value.value = arg_value_list[0].value
    star_node=None

    # star_node.value.slice = ast.Slice()
    # star_node.value.slice.lower = arg_value_list[0].slice
    # star_node.value.slice.upper = arg_value_list[-1].slice
    # star_node.value.slice.step = step
    # print("star node: ",ast.unparse(star_node))
    end=ast.unparse(arg_value_list[-1].slice)
    # if end.isdigit():
    #     end=str(int(end)+1)
    # else:
    end = str(sympify(end + '+'+str(step)))
        # end=end+"+1"
    a=["*",ast.unparse(arg_value_list[0].value),"[",ast.unparse(arg_value_list[0].slice),":",end,":",str(step),"]"]
    star_node=ast.parse("".join(a)).body[0]
    # print("star node: ", star_node,ast.unparse(star_node))
    return star_node
def transform_var_unpack_call_each_args(arg_info_list):

    # all_ind_list=item[0]
    # step=item[2]
        '''
           remove corresponding elements in the args of ind_list
           and insert  replaced them with a starred node
        '''
        bia = 0
    # for ind,arg_info_list in enumerate(item):
        step = arg_info_list[3]
        ind_list=arg_info_list[1]
        # node=arg_info_list[-2]
        node=arg_info_list[2]
        # print("node: ",node,ind_list,step)
        args = node.args

        beg=ind_list[0]+bia
        arg_value_list=[]
        for i in range(len(ind_list)):
            arg_value_list.append(args.pop(beg))


        # print("args: ", arg_value_list)
        star_node= build_star_node(arg_value_list,step)


        # print("star_node: ", ast.unparse(star_node))
        return star_node
    #     args.insert(beg,star_node)
    #     bia+=1-len(ind_list)
    #
    # print("code1: ",ast.unparse(node))


def transform_var_unpack_call(node,item):

    # all_ind_list=item[0]
    # step=item[2]
    '''
       remove corresponding elements in the args of ind_list
       and insert  replaced them with a starred node
    '''
    bia = 0
    for ind,arg_info_list in enumerate(item):
        step = arg_info_list[3]
        ind_list=arg_info_list[1]
        # node=arg_info_list[2]
        # print("node: ",node,ind_list,step)
        args = node.args
        # print("args: ", args)
        beg=ind_list[0]+bia
        arg_value_list=[]
        for i in range(len(ind_list)):
            arg_value_list.append(args.pop(beg))
        star_node= build_star_node(arg_value_list,step)

        args.insert(beg,star_node)
        bia+=1-len(ind_list)

    # print("code1: ",ast.unparse(node))

    pass


if __name__ == '__main__':
    code='''
upfirdn2d_native(input, kernel, up, up, down, down, pad[0], pad[1], pad[0], pad[1])
ConvBNLayer(out_channels[1], out_channels[1], 3, 1, act='relu', name='fpn_up_g1_1')
sort_by_key_ir(ins[0], ins[1], outs[0], outs[1], outs[2], outs[3], axis, is_ascend)
a=axes.text( rect.xy[1],rect.xy[0], rect.xy[1], labels[I:],labels[i+1],labels[2],bbox=dict(facecolor=color, lw=0))
# a=axes.text( rect.xy[0],rect.xy[1], rect.xy[1], labels[I:],labels[i+1],labels[2],bbox=dict(facecolor=color, lw=0))
# b=func(a[i],a[i+1],c[1])
# b=func(a[i+1],a[i],a[i+1],c[1])
# b=func(a['1'],a[i],a[i+1],c[2],c[0],c[1])
b=func(a['1'],a[i],a[i+1],c[2],c['1'],c[0],c[1])
# b=func(a,b,c[1])
self.ds_opt_adam.adam_update_copy(self.opt_id, state['step'], group['lr'], beta1, beta2, group['eps'], group['weight_decay'], group['bias_correction'], p.data, p.grad.data, state['exp_avg'], state['exp_avg_sq'], fp16_param_groups[group_id][param_id].data)
'''
    # 对找到的代码片段不断进行转换直至不可以转换
    code_list=[
        ["user_check = self.run_function('file.get_user', [check])","mode_check = self.run_function('file.get_mode', [check])"],
        ["name = obj.find('name').text.strip()","bbox = obj.find('bndbox')"],
        ["self._tmp_path = tmp_path","self._config = config","self.location = str(tmp_path)"]]
    # while 1:
    save_complicated_code_dir = util.data_root + "complicated_code_dir/var_unpack_func_call_only_same_dengcha_subscript_complicated_pkl/"
    for file_name in os.listdir(save_complicated_code_dir):
        complicate_code = util.load_pkl(save_complicated_code_dir, file_name[:-4])
        for each_file in complicate_code:
            # for code_list, file_path,file_html in each_file:
            #
            #     print("count: ",code_list)
            code_map = each_file[0]
            for node, item in code_map.items():
                print(">>>>>>>old code1: ", ast.unparse(node))
                transform_var_unpack_call(node, item)
                break


    # test_save_complicated_code_dir = util.data_root + "test_complicated_code_dir/"
    # file_name = "var_unpack_func_call_only_same_dengcha_subscript_complicated"
    # map_code=util.load_pkl(test_save_complicated_code_dir,file_name)
    # for node, item in map_code.items():
    #     print(">>>>>>>old code1: ", ast.unparse(node))
    #     transform_var_unpack_call(node,item)
















