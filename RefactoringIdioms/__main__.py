# import RefactoringIdioms,argparse,os
# abs_path=os.path.abspath(os.path.dirname(__file__))
# # print("abs_path: ",abs_path)
# parser = argparse.ArgumentParser(description='RefactoringIdioms')
# parser.add_argument('--envname', type=str,
#                     help='envname', default="CartPole-v0")
# parser.add_argument('--filepath', type=str,
#                     help='filepath', default=abs_path+"/main.py")
# parser.add_argument('--idiom', type=str,
#                     help='idiom', default="All")
# parser.add_argument('--outputpath', type=str,
#                     help='outputpath', default="result.json")
# args = parser.parse_args()
# RefactoringIdioms.run_main(args)