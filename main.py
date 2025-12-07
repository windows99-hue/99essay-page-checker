#coding:utf-8
from clc99 import *
import argparse
import os
import sys
from docx import Document
from PyPDF2 import PdfReader


def getFileContent(filename, encoding='utf-8'):
    print_status("正在读取文件...")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} 不存在")
    
    if not os.path.isfile(filename):
        raise ValueError(f"路径不是文件: {filename}")
    
    # 新增：Word文档（.docx）解析
    if filename.endswith('.docx'):
        doc = Document(filename)
        content = '\n'.join([para.text for para in doc.paragraphs])
        return content
    # 新增：PDF文档解析
    elif filename.endswith('.pdf'):
        reader = PdfReader(filename)
        content = ''
        for page in reader.pages:
            page_text = page.extract_text() or ''  # 处理空白页
            content += page_text + '\n'
        return content
    # 保留原有TXT文件读取
    elif filename.endswith('.txt'):
        with open(filename, 'r', encoding=encoding, errors='ignore') as file:
            content = file.read()
        return content
    else:
        raise ValueError(f"不支持的文件格式！仅支持 .txt、.docx、.pdf")

def is_punctuation(char):
    single_point_symbol = ["。", "！", "？", "；", "，", "、", "：", "」", "』", "）", "】", "》"]
    double_point_symbol_start = ["……", "——"]
    merge_point_symbol_open = ["“", "‘", "（", "【", "《"]
    merge_point_symbol_close = ["”", "’", "）", "】", "》"]
    
    return (char in single_point_symbol or 
            any(char == s[0] for s in double_point_symbol_start) or
            char in merge_point_symbol_open or
            char in merge_point_symbol_close)

def should_merge_with_next(current_char, next_char):
    # 双字节标点的第一部分
    double_symbols = ["……", "——"]
    
    for symbol in double_symbols:
        if len(symbol) == 2 and current_char == symbol[0] and next_char == symbol[1]:
            return True
    
    # 处理左引号（不合并的情况）
    if not args.no_merge and current_char in ["“", "‘", "（", "【", "《"]:
        # 如果后一个字符是标点，考虑合并
        if next_char in ["。", "！", "？", "；", "，", "：", "）", "】", "》"]:
            return True
    
    return False

def main(quiet=False):
    # 检查参数是否合法
    if args.paragraph_spacing >= args.perrow:
        print_error("段落缩进不能大于等于每行字数！")
        if quiet:
            err99(text="段落缩进不能大于等于每行字数！")
        return

    # 读取文件
    try:
        data = getFileContent(args.filename, args.encoding)
    except Exception as e:
        print_error("读取文件时出错:", str(e))
        if quiet:
            err99(text=str(e))
        return
    
    print_good("已读取文件！初始字符数量:", len(data))
    print_status("正在分析文件内容...")

    prev_char = ""         # 上一个字符
    next_char = ""         # 下一个字符
    cnt = 0                # 已占用格子总数
    line_idx = 0           # 当前行已用格子数（0-based）
    checked_title = False  # 是否已检查标题
    new_paragraph = False  # 是否是新段落开始
    skip_next = False      # 是否跳过下一个字符（用于双字节标点）
    lines_processed = 0    # 已处理的行数
    
    i = 0
    while i < len(data):
        if skip_next:
            skip_next = False
            i += 1
            continue
            
        char = data[i]
        next_char = data[i+1] if i+1 < len(data) else ""
        
        # 空格不占格子（除非设置了空格算字符）
        if char == " ":
            if not args.space_yes:
                i += 1
                continue
        
        # 1. 处理换行符（段落分隔）
        if char in ["\n", "\r"]:
            # 跳过回车符，等待换行符处理
            if char == "\r" and i+1 < len(data) and data[i+1] == "\n":
                i += 2
            else:
                i += 1
            
            # 如果是第一个换行符，之前的是标题
            if not checked_title:
                checked_title = True
                print_status(f"标题检查完毕！共{line_idx}字符")
            
            # 当前行剩余格子浪费掉
            if line_idx > 0:
                remaining_in_line = args.perrow - line_idx
                # 如果不是最后一行，加上剩余空格
                if i < len(data):  # 还有后续内容
                    cnt += remaining_in_line
                lines_processed += 1
            
            # 重置状态(换行)
            line_idx = 0
            new_paragraph = True  # 换行后是新段落
            is_first_line = False  # 不再是第一行
            continue
        
        #添加缩进
        if new_paragraph and line_idx == 0:
            indent = args.paragraph_spacing if hasattr(args, 'paragraph_spacing') else 2
            if indent > 0:
                if checked_title:  # 只有标题后的段落才缩进
                    cnt += indent
                    line_idx += indent
                    print_status(f"段落缩进: +{indent}格")
            new_paragraph = False
        
        # 3. 检查是否需要合并标点
        should_merge = False
        
        # 检查与前一个字符合并
        if prev_char and is_punctuation(char) and is_punctuation(prev_char) and not args.no_merge:
            should_merge = True
        
        # 检查与后一个字符合并（双字节标点）
        elif next_char and should_merge_with_next(char, next_char) and not args.no_merge:
            # 如果是双字节标点，两个字符占1格
            cnt += 1
            line_idx += 1
            skip_next = True  # 跳过下一个字符
            prev_char = char + next_char  # 记录合并后的标点
            i += 2
            continue
        else:
            # 普通字符或标点：占用1格
            cnt += 1
            line_idx += 1
        
        # 如果不是合并情况，正常处理当前字符
        if not should_merge:
            # 检查是否允许孤标点在行首
            if line_idx == 1 and is_punctuation(char) and char not in args.allow_isolated:
                print_warning(f"行首出现孤标点 '{char}'，不计数")
                # 回退计数
                cnt -= 1
                line_idx -= 1
        
        prev_char = char
        
        # 如果一行满了，换行
        if line_idx >= args.perrow:
            lines_processed += 1
            line_idx = 0
            new_paragraph = False
        
        i += 1

    return cnt

@loading99("正在检查作文，请稍候...")
def mainq():
    return main(True)

parser = argparse.ArgumentParser(description="99作文字数检查器")

parser.epilog = """
这是一个可以检测你的作文能否填入作文纸的工具。\n
使用示例：
    python main.py example.txt -r 20 -p 1000
"""

parser.add_argument("filename", help="要被检查的文件")
parser.add_argument("-q", "--quiet", action="store_true", help="安静模式，只输出能否写下")
parser.add_argument("-r", "--perrow", type=int, default=20, help="每行的最大字数，默认值为20")
parser.add_argument("-p", "--perpage", type=int, default=1000, help="每页的最大字数，默认值为1000")
parser.add_argument("-sy", "--space-yes", action="store_true", help="空格算字符")
parser.add_argument("-ps", "--paragraph-spacing", type=int, default=2,
                    metavar="SPACES", help="段落开头空格数（默认：2）")
parser.add_argument("-nm", "--no-merge", action="store_true", help="不合并引号与标点符号，例如 \"。“\" 不会被合并为一个格")
parser.add_argument("-allow-isolated", nargs="*", default=[], help="允许在行首的孤标点（默认无，例：-allow-isolated ， 、）")
parser.add_argument("-encoding", default="utf-8", help="文件编码格式（默认utf-8，兼容中文文档，可选gbk等）")

args = parser.parse_args()

print_admin("欢迎使用99作文字数检查器！")

if args.quiet:
    result = mainq()
else:
    result = main()

if result == None:
    sys.exit(1)

print("*"*50)

# 计算页数
pages = result // args.perpage
if result % args.perpage > 0:
    pages += 1

print_finish("分析完成！总占格：",result)
print_status(f"估计页数: {pages} (每页{args.perpage}格)")

if args.perpage - result >= 0:
    print_good("作文可以写下！还剩:", args.perpage - result, "个格子~")
else:
    print_error("ohno！一页塞不下，您还需要减少", result - args.perpage, "个字或者再拿一张纸~")