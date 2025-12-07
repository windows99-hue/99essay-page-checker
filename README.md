# 99 Essay Page Checker

> 我不想写作文唔姆，想玩vrc

### 这是一个可以帮你算算你的作文能否塞入作文纸的小程序！

~~~bash
PS E:\>  python -u "e:\99的github\99essay-page-checker\main.py" -h
usage: main.py [-h] [-q] [-r PERROW] [-p PERPAGE] [-sy] [-ps SPACES] [-nm] [-allow-isolated [ALLOW_ISOLATED ...]]
               [-encoding ENCODING]
               filename

99作文字数检查器

positional arguments:
  filename              要被检查的文件

options:
  -h, --help            show this help message and exit
  -q, --quiet           安静模式，只输出能否写下
  -r, --perrow PERROW   每行的最大字数，默认值为20
  -p, --perpage PERPAGE
                        每页的最大字数，默认值为1000
  -sy, --space-yes      空格算字符
  -ps, --paragraph-spacing SPACES
                        段落开头空格数（默认：2）
  -nm, --no-merge       不合并引号与标点符号，例如 "。“" 不会被合并为一个格
  -allow-isolated [ALLOW_ISOLATED ...]
                        允许在行首的孤标点（默认无，例：-allow-isolated ， 、）
  -encoding ENCODING    文件编码格式（默认utf-8，兼容中文文档，可选gbk等）

这是一个可以检测你的作文能否填入作文纸的工具。 使用示例： python main.py example.txt -r 20 -p 1000
PS E:\> 
~~~

运行效果演示：

