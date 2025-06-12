#!/usr/bin/env python3
"""
Script to validate bcgeu_local_data.py file for syntax errors
"""

import ast
import sys

def validate_python_file(filename):
    """Validate a Python file for syntax errors"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file
        ast.parse(content)
        print(f"✅ {filename} is syntactically valid!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error in {filename}:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        if e.offset:
            print(f"   Position: {' ' * (e.offset-1)}^")
        return False
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return False
        
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return False

def check_brackets(filename):
    """Check for unmatched brackets"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for i, char in enumerate(content):
            if char in brackets:
                stack.append((char, i))
            elif char in brackets.values():
                if not stack:
                    line_num = content[:i].count('\n') + 1
                    print(f"❌ Unmatched closing bracket '{char}' at line {line_num}")
                    return False
                    
                open_bracket, pos = stack.pop()
                if brackets[open_bracket] != char:
                    line_num = content[:i].count('\n') + 1
                    print(f"❌ Mismatched bracket: expected '{brackets[open_bracket]}', got '{char}' at line {line_num}")
                    return False
        
        if stack:
            for bracket, pos in stack:
                line_num = content[:pos].count('\n') + 1
                print(f"❌ Unmatched opening bracket '{bracket}' at line {line_num}")
            return False
            
        print("✅ All brackets are properly matched!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking brackets: {e}")
        return False

def check_quotes(filename):
    """Check for unmatched quotes"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        issues = []
        for line_num, line in enumerate(lines, 1):
            # Count single quotes (excluding escaped ones)
            single_quotes = line.count("'") - line.count("\\'")
            double_quotes = line.count('"') - line.count('\\"')
            
            if single_quotes % 2 != 0:
                issues.append(f"Line {line_num}: Unmatched single quotes")
            if double_quotes % 2 != 0:
                issues.append(f"Line {line_num}: Unmatched double quotes")
        
        if issues:
            print("❌ Quote issues found:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"   {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")
            return False
        else:
            print("✅ All quotes appear to be properly matched!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking quotes: {e}")
        return False

if __name__ == "__main__":
    filename = "bcgeu_local_data.py"
    
    print("🔍 Validating bcgeu_local_data.py...")
    print("=" * 50)
    
    # Run all checks
    syntax_ok = validate_python_file(filename)
    brackets_ok = check_brackets(filename)
    quotes_ok = check_quotes(filename)
    
    print("=" * 50)
    if syntax_ok and brackets_ok and quotes_ok:
        print("🎉 File validation successful! No issues found.")
    else:
        print("🚨 Issues found. Please fix the errors above.")
        
    # Try to import the data
    if syntax_ok:
        try:
            import bcgeu_local_data
            print("✅ File imports successfully!")
            print(f"✅ AGREEMENT_DATA contains {len(bcgeu_local_data.AGREEMENT_DATA)} top-level keys")
        except Exception as e:
            print(f"❌ Import error: {e}")
