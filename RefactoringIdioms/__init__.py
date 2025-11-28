import sys
import os

# 确保能找到 RefactoringIdioms 包
# 将当前文件的上两级目录加入 path (即项目根目录)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#from RefactoringIdioms import main

def run_main():
    """
    RIdiom 包的入口函数。
    它直接调用 main.py 中的 main() 函数，
    参数解析和配置加载全部由 main.py 内部处理。
    """
    try:
        main.main()
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    run_main()