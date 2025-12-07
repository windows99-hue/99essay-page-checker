with open("test.txt", "r", encoding="utf-8") as f:
    data = f.read()

# 显示每个字符的详细信息
print("=== 字符详细分析 ===")
for i, char in enumerate(data):
    char_display = char
    if char == '\n':
        char_display = '\\n'
    elif char == '\r':
        char_display = '\\r'
    elif char == '\t':
        char_display = '\\t'
    elif char == ' ':
        char_display = '[空格]'
    elif ord(char) < 32 or ord(char) > 126:
        char_display = f'[非ASCII:{ord(char):04d}]'
    
    print(f"位置 {i:2d}: '{char_display}' (ASCII: {ord(char):3d})")
print("===")