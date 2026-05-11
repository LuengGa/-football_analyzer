
#!/usr/bin/env python3
"""
Fix HTML encoded characters in Python files (like -&gt; instead of ->)
"""

import os
import re

def fix_file(file_path):
    """Fix HTML encoded characters in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace HTML entities with their actual characters
        original = content
        content = content.replace('-&gt;', '->')
        content = content.replace('&gt;', '>')
        content = content.replace('&lt;', '<')
        content = content.replace('&amp;', '&')
        content = content.replace('&quot;', '"')
        content = content.replace('&#39;', "'")
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in src directory"""
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    count = 0
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    count += 1
    
    print(f"\nTotal files fixed: {count}")

if __name__ == "__main__":
    main()
