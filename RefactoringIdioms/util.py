
import json,os,csv,tokenize,token,pickle
root="/mnt/zejun/smp/"
data_root="/mnt/zejun/smp/data/"
code_root="/mnt/zejun/smp/code1/"
all_repos_dir="/mnt/zejun/smp/data/2021-4-20-github-top-10000stars/"
pro_path=data_root+"python_repo_1000/"
#root="/data/zzj/so/"#'/Users/sally/Downloads/xiaxin/third_html/dataset/Trans_Simpl_Compl/'
#data_dir=root+"data/"
test_case_list=[]
test_paras=[]
me_list=[]
import shutil
built_in=['abs','delattr','hash','memoryview','set','all','dict','help','min','setattr','any','dir','hex','next','slice','ascii','divmod','id','object','sorted','bin',
    'enumerate','input','oct','staticmethod','bool','eval','int','open','str','breakpoint','exec','isinstance','ord','sum','bytearray','filter','issubclass','pow','super',
    'bytes','float','iter','print','tuple','callable','format','len','property','type','chr','frozenset','list','range','vars','classmethod','getattr','locals','repr',
    'zip','compile','globals','map','reversed','__import__','complex','hasattr','max','round']
def mkdirs(save_for_else_methods_dir):
    if not os.path.exists(save_for_else_methods_dir):
        os.makedirs(save_for_else_methods_dir)
    else:
        shutil.rmtree(save_for_else_methods_dir)  # Removes all the subdirectories!
        os.makedirs(save_for_else_methods_dir)
def save_pkl(file_path,file_name,data):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path + file_name + '.pkl', 'wb') as file:
        return pickle.dump(data,file)
def load_pkl(file_path,file_name):
    with open(file_path +  file_name+'.pkl', 'rb') as file:
        return pickle.load(file)
def load_json(file_path,file_name):

    with open(file_path + file_name+'.json', 'r') as json_file:
        return json.load( json_file)
def save_json(file_path,file_name,data):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path + file_name+'.json', 'w') as json_file:
        json.dump(data, json_file)
def save_json_file_path(file_path,data):
    # if not os.path.exists(file_path):
    #     os.makedirs(file_path)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)
def load_file(file_path,file_name):
    with open(file_path + file_name, 'rb') as file:

        return file.read()
def load_file_path(file_path):
    with open(file_path, 'r') as file:

        return file.read()
def load_file_path_lines(file_path):
    with open(file_path, 'r') as file:

        return file.readlines()
def save_file_path(file_path,content,format="",w="w"):
    path_dir="/".join(file_path.split("/")[:-1])
    if not os.path.exists(path_dir) and path_dir:
        os.makedirs(path_dir)
    with open(file_path, w) as file:

        file.write(content)
def save_file(file_path,file_name,content,format="",w="w"):
    path_dir="/".join(file_path.split("/")[:-1])
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
    with open(file_path + file_name+format, w) as file:

        file.write(content)
def save_csv(file_path,data, head=[]):
    dir_path="/".join(file_path.split("/")[:-1])
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, 'w', encoding='utf-8', newline="") as file:
        writer = csv.writer(file)
        if head:
            writer.writerow(head)
        for item in data:
            writer.writerow(item)
def do_file(fname):
    """ Run on just one file.

    """
    source = open(fname)
    #mod = open(fname + ",strip", "w")
    new_str=""

    prev_toktype = token.INDENT
    first_line = None
    last_lineno = -1
    last_col = 0

    tokgen = tokenize.generate_tokens(source.readline)
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        if 0:   # Change to if 1 to see the tokens fly by.
            print("%10s %-14s %-20r %r" % (
                tokenize.tok_name.get(toktype, toktype),
                "%d.%d-%d.%d" % (slineno, scol, elineno, ecol),
                ttext, ltext
                ))
        if slineno > last_lineno:
            last_col = 0
        if scol > last_col:
            new_str+=" " * (scol - last_col)
            #mod.write(" " * (scol - last_col))
            pass
        if toktype == token.STRING and prev_toktype == token.INDENT:
            # Docstring
            #mod.write("#--")
            #new_str+="#--"
            pass
        elif toktype == tokenize.COMMENT:
            # Comment
           # mod.write("##\n")
            #new_str += "\n"
            pass
        else:
            #mod.write(ttext)
            new_str += ttext
        prev_toktype = toktype
        last_col = ecol
        last_lineno = elineno
    return new_str
def get_python3_repos(repo_path_dir):

    count=0
    flag=1
    for root,dirs,files in os.walk(repo_path_dir):
        #print(root)
        for file in files:
            if file.endswith(".py") and ("__init__" in file or "setup.py" in file):
                continue
            if file.endswith(".py"):
                parse_file_path = root + "/" + file


                try:
                    #content = load_file(parse_file_path)
                    content = do_file(parse_file_path)
                    # if "validate_rst_title_capitalization.py" in parse_file_path:
                    #     print("content: ",content)

                except:
                    print("the file do not be read!!!!!")
                    continue

                if "    print " in content or "\nprint " in content:
                    # print(parse_file_path)
                    # print(content)
                    flag=0
                    break

                count+=1
        if flag==0:
            break
    # print("num of python file in the repo: ",count)
    return flag,count

def load_csv(file_path):
    csvFile = open(file_path, "r")
    reader = csv.reader(csvFile)
    return list(reader)