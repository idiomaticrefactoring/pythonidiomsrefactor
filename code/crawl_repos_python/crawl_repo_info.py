import sys,os
pro_root="/".join(os.path.abspath(__file__).split("/")[:-1])+"/"
sys.path.append(pro_root+"code/")
sys.path.append("../..")
sys.path.append("../../../")

import github_util,util

from pathos.multiprocessing import ProcessingPool as newPool
def merge_all_repo_info(data_dir):
    pass

if __name__ == '__main__':
    data_dir=util.data_root
    pro_api_url_list=[]

    only_pro_name_list=util.load_json(data_dir+"github/","star_proj_get")
    for e in only_pro_name_list:
        pro_api_url_list.append("https://api.github.com/repos/"+e['name'])
    print(only_pro_name_list[0])
    save_repo_info_dir=data_dir+"repo_info_new_dir/"
    def save_repo_info(url):
        try:
            res = github_util.get_request(url)
            # print(res)
            util.save_json(save_repo_info_dir+res['full_name'].split("/")[0]+"/", res['name'], res)
            print("save successfully ",url)
            #util.save_json(save_repo_info_dir + res[''], str(res["id"]), res)
        except:
            print("the url is not saved!", url)
    import time
    start=time.time()
    '''
    remain_url=[]
    for repo_url in pro_api_url_list:
        repo_name=repo_url.split("/")[-1]
        repo_usr=repo_url.split("/")[-2]
        if not os.path.exists(save_repo_info_dir+repo_usr+repo_name+".json") and not os.path.exists(save_repo_info_dir+repo_usr+"/"+repo_name+".json"):
            remain_url.append(repo_url)
            # save_repo_info(repo_url)
            # break

        # else:
        #     print("the url is existed!")

            
    
    print("remaining file num: ",len(remain_url))
    '''
    # save_repo_info(pro_api_url_list[0])
    print("len file: ",len(os.listdir(save_repo_info_dir)))
    #
    #     res=github_util.get_request(url)
    #
    #
    #     util.save_json(save_repo_info_dir,str(res["id"]),res)
    #     # print("repo info: ",res)
    '''
    pool = newPool(nodes=20)
    pool.map(save_repo_info, remain_url)  # sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    print("save all files successfully!")
    end = time.time()
    print("all time: ", end - start)
    '''
    #for
    '''
    
    for repo in new_pro_info_python_list[:]:
    res=[]
    for file in os.listdir(save_repo_info_dir):
        repo_name=repo_url.split("/")[-1]
        repo_usr=repo_url.split("/")[-2]
        res.append(util.load_json(save_repo_info_dir+repo_usr+"/",repo_name))
    all_repo_info_name = "star_proj_info"
    util.save_json(data_dir, all_repo_info_name, res)
    '''

    '''
    
    count=0
    res=[]
    for root,dirs,files in os.walk(save_repo_info_dir):
        #print(root)
        for file in files:
            if file.endswith(".json"):
                res.append(util.load_json(root+"/", file[:-5]))
                count+=1
    print("total number: ", count)
    all_repo_info_name = "star_proj_info"
    util.save_json(data_dir, all_repo_info_name, res)
    '''

    dict_repo_file_python = util.load_json(util.data_root, "python3_repos_files_info")
    save_repo_info_dir=data_dir+"repo_info_new_dir/"
    dict_repo_info=dict()
    count=0
    count_json=0
    for repo in os.listdir(save_repo_info_dir):
        if repo.endswith(".json"):
            repo_info = util.load_json(save_repo_info_dir, repo[:-5])
            repo_name=repo_info["name"]
            if repo_name in dict_repo_file_python:
                dict_repo_info[repo_name]=repo_info
            count_json+=1

    print("count: ",count,count_json)
    util.save_json(data_dir , "dict_star_1000_repo_name_repo_info", dict_repo_info)

    # for key in dict_repo_file_python:





