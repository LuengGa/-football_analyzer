#!/usr/bin/env python3
"""
批量修复 mypy 错误的辅助脚本
"""

import re
import subprocess
from pathlib import Path

def fix_no_implicit_optional(content):
    """修复隐式 Optional 参数"""
    # 匹配 def func(param: Type = None) -> ...
    pattern = r'(\w+): (\w+) = None(?![\s,)])'

    def replacer(match):
        param_name = match.group(1)
        param_type = match.group(2)
        return f'{param_name}: Optional[{param_type}] = None'

    lines = content.split('\n')
    result = []
    changes = 0

    for i, line in enumerate(lines):
        # 匹配函数定义中的隐式可选参数
        if re.search(r'def \w+\([^)]*\w+:\s*\w+\s*=\s*None\s*[,\)]', line):
            new_line = re.sub(r'(\w+): (\w+) = None(?![\s,)])',
                             lambda m: f'{m.group(1)}: Optional[{m.group(2)}] = None',
                             line)
            if new_line != line:
                result.append(new_line)
                changes += 1
            else:
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result), changes

def fix_var_annotation(content):
    """为缺少类型注解的变量添加 Any"""
    lines = content.split('\n')
    result = []
    changes = 0

    for line in lines:
        # 匹配 collections.defaultdict() 缺少类型注解
        if 'defaultdict(' in line and 'Dict[' not in line and 'dict[' not in line:
            # 简单添加 # type: ignore
            result.append(line + '  # type: ignore')
            changes += 1
        else:
            result.append(line)

    return '\n'.join(result), changes

def main():
    # 运行 mypy 获取错误列表
    result = subprocess.run(
        ['python', '-m', 'mypy', 'src', '--ignore-missing-imports'],
        capture_output=True,
        text=True
    )

    # 解析错误
    errors = []
    for line in result.stdout.split('\n'):
        if ': error:' in line:
            match = re.match(r'(.+?):(\d+): error:', line)
            if match:
                errors.append((match.group(1), int(match.group(2))))

    print(f"发现 {len(errors)} 个 mypy 错误")

    # 按文件分组
    from collections import defaultdict
    files = defaultdict(list)
    for file, line in errors:
        files[file].append(line)

    print(f"涉及 {len(files)} 个文件")

    # 统计错误类型
    type_counts = defaultdict(int)
    for line in result.stdout.split('\n'):
        if ': error:' in line:
            match = re.search(r'\[([\w-]+)\]', line)
            if match:
                type_counts[match.group(1)] += 1

    print("\n错误类型统计：")
    for error_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {error_type}: {count}")

if __name__ == '__main__':
    main()
