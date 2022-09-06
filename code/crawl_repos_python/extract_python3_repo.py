import sys,ast,os,copy
import tokenize
pro_root="/".join(os.path.abspath(__file__).split("/")[:-1])+"/"
sys.path.append(pro_root+"code/")
import util

new_pro_1000_info_python_list=util.load_json(util.data_root,"all_crawl_python_pros")[:]
print("len repo info: ",len(new_pro_1000_info_python_list),new_pro_1000_info_python_list[0])
dict_repo_name_html_url=dict()
for e in new_pro_1000_info_python_list:
    dict_repo_name_html_url[e["name"]]=e['html_url']



pro_path=util.pro_path
dict_repo_file_python=dict()
for repo_name in os.listdir(pro_path):
    repo_html = dict_repo_name_html_url[repo_name]
    repo_path_dir = pro_path + repo_name + "/"
    flag, count = util.get_python3_repos(repo_path_dir)
    if flag:
        dict_repo_file_python[repo_name] = []
        for root,dirs,files in os.walk(repo_path_dir):
            #print(root)
            for file in files:
                if file.endswith(".py") and ("__init__" in file or "setup.py" in file):
                    continue
                if file.endswith(".py"):
                    # print("file: ",dirs,file)
                    # break
                    file_path=root+"/"+file
                    file_html =repo_html+ "/tree/master/" +"/".join(file_path.split("/")[7:])
                    dict_repo_file_python[repo_name].append({"file_path":file_path,"file_html":file_html})
        #             print("file_html: ",file_html)
        #             #     break
        #             break
        #     break
        # break
print("number of python3 repos: ",len(list(dict_repo_file_python.keys())))
util.save_json(util.data_root,"python3_repos_files_info",dict_repo_file_python)



# file_html = "https://github.com/" + "/".join(
#                             file_path.split("/")[4:6]) + "/tree/master/" + "/".join(file_path.split("/")[6:])




