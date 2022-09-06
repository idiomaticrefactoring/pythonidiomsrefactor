import sys,ast,os,copy
import tokenize
pro_root="/".join(os.path.abspath(__file__).split("/")[:-1])+"/"
sys.path.append(pro_root+"code/")
import util,github_util

# try:
'''
star=[">3500","2000..3500","1800..2000"]
beiyong_star=["900..1800","550..899","400..549","310..399","250..309","202..249",
              "170..201","145..169","125..144","110..124","100..109"]
res_list=[]
for e in star:

    url='https://api.github.com/search/repositories?q='+"language:Python+stars:"+e+"&sort=stars"


    #url='https://api.github.com/search/repositories?q='+"language:Python&sort=stars"
    res_list.extend(github_util.get_repos_top_k_star(url))
'''

# print("res: ",len(res["items"]))
##'''
# repos_list=[]
# count=0
# for res in res_list:
#     repos_list.extend(res["items"])
#     count+=len(res["items"])
# print("count: ",count)
# #util.save_json(util.data_root, "python3_star_10_repos_info", repos_list)
# util.save_json(util.data_root, "python3_star_2000_repos_info", repos_list)
star=[">3521","2000..3521","1400..2000"]+["1100..1400","880..1100","730..880","630..730","555..630","500..555",
              "450..500","408..450"]
# beiyong_star=["1100..1400","880..1100","730..880","630..730","555..630","500..555",
#
#               "450..500","408..450"]

res_list=[]
for e in star[:]:

    url='https://api.github.com/search/repositories?q='+"language:Python+stars:"+e+"&sort=stars"

    res_list.append(url)
repos_list=[]
count=0
for url in res_list:
    repos_list.extend(github_util.get_repos_top_k_star(url))

count+=len(repos_list)
print("count: ",count)
util.save_json(util.data_root, "python3_star_10000_repos_info", repos_list)

# repo=util.load_json(util.data_root,"python3_star_10000_repos_info")
# print(repo)
# util.save_json(util.data_root, "python3_star_2000_repos_info", repos_list)
# util.save_json(util.data_root, "python3_star_10000_repos_info", repos_list)


#'''
    # print(res)
    # util.save_json(save_repo_info_dir + res['full_name'].split("/")[0] + "/", res['name'], res)
    # print("save successfully ", url)
    # util.save_json(save_repo_info_dir + res[''], str(res["id"]), res)
# except:
#     print("the url is not saved!", url)

