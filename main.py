#coding:utf-8
from clc99 import *
import argparse
import os

def getFileContent(filename, encoding='utf-8'):
    print_status("正在读取文件...")
    # 检查文件是否存在
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} 不存在")
    
    # 检查是否为文件
    if not os.path.isfile(filename):
        raise ValueError(f"路径不是文件: {filename}")
    
    with open(filename, 'r', encoding=encoding) as file:
        content = file.read()
    return content

def main(quiet=False):

    #检查参数是否合法
    if args.paragraph_spacing >= args.perrow:
        print_error("段落缩进不能大于等于每行字数！")
        if quiet:
            err99(text="段落缩进不能大于等于每行字数！")
        return

    #读取文件！
    try:
        data = getFileContent(args.filename, args.encoding)
    except Exception as e:
        print_error("读取文件时出错:", str(e))
        if quiet:
            err99(text = str(e))
        return
    print_good("已读取文件！初始字符数量:",len(data))

    print_status("正在分析文件内容...")

    prev_char = ""
    cnt = 0                # 已占用格子总数
    line_idx = 0           # 当前行已用格子数（0-based）
    checked_title = False  # 是否已检查标题
    new_paragraph = False   # 是否是新段落开始
    
    for i, char in enumerate(data):
        # 空格不占格子
        if char == " ":
            if not args.space_yes:
                continue

        # 1. 处理换行符（段落分隔）
        if char in ["\n", "\r"]:
            # 如果是第一个换行符，之前的是标题
            if not checked_title:
                checked_title = True
                title_length = line_idx  # 标题长度
                print_status(f"标题检查完毕！共{title_length}字符")
                cnt += title_length
            
            #减去换行符本身
            cnt -= 2

            # 当前行剩余格子浪费掉
            remaining_in_line = args.perrow - line_idx
            cnt += remaining_in_line
            
            # 重置状态(换行)
            line_idx = 0
            new_paragraph = True  # 换行后是新段落

            continue
        
        # 2. 新段落开头：添加缩进
        if new_paragraph and line_idx == 0:
            indent = args.indent if hasattr(args, 'indent') else 2
            if indent > 0:
                # 检查当前行是否能放下缩进
                if indent <= args.perrow:
                    if checked_title:
                        cnt += indent
                        line_idx += indent
                        print_status(f"段落缩进: +{indent}格")
                else:
                    print(f"警告: 缩进{indent}格超过行宽{args.perrow}")
            new_paragraph = False
        
        # 3. 普通字符：占用1格
        cnt += 1
        line_idx += 1
        
        free_bar_in_row = args.perrow - line_idx
        
        # 4. 如果一行满了，换行
        if line_idx >= args.perrow:
            print("一行已满，换行")
            line_idx = 0
            # 换行后如果是段落中间，不需要缩进
            new_paragraph = False

    return cnt



@loading99("正在检查作文，请稍候...")
def mainq():
    return main(True)


single_point_symbol = ["。", "！", "？", "；", "，", "、", "：", "」", "』", "）", "】", "》"]
double_point_symbol = ["……", "——"]
merge_point_symbol = ["“", "‘", "（", "【", "《","”", "’", "）", "】", "》"]

parser = argparse.ArgumentParser(description="99作文字数检查器")

parser.epilog = """
这是一个可以检测你的作文能否填入作文纸的工具。\n
使用示例：
    python main.py example.txt -r 20 -p 1000 -n
"""

parser.add_argument("filename", help="要被检查的文件")
parser.add_argument("-q", "--quiet", action="store_true", help="安静模式，只输出能否写下")
parser.add_argument("-r", "--perrow", type=int, default=20, help="每行的最大字数，默认值为20")
parser.add_argument("-p", "--perpage", type=int, default=1000, help="每页的最大字数，默认值为1000")
parser.add_argument("-n", "--normal", action="store_true", help="以普通作文格式检查")
parser.add_argument("-sy", "--space-yes", action="store_true", help="空格算字符")
parser.add_argument("-ps", "--paragraph-spacing", type=int, default=2,
                    metavar="SPACES", help="段落开头空格数（默认：2）")
parser.add_argument("-nm","--no-merge", action="store_true", help="不合并引号与标点符号，例如 \"。“\" 不会被合并为一个格")
#parser.add_argument("-tl","--title-line",action="store_true", help="标题占一行")
parser.add_argument("-allow-isolated", nargs="*", default=[], help="允许在行首的孤标点（默认无，例：-allow-isolated ， 、）")
parser.add_argument("-encoding", default="utf-8", help="文件编码格式（默认utf-8，兼容中文文档，可选gbk等）")

args = parser.parse_args()

print_admin("欢迎使用99作文字数检查器！")

if args.quiet:
    result = mainq()
else:
    result = main()

print_finish(result)