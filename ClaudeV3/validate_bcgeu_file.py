import streamlit as st
import ast

st.title("BCGEU File Validator")

# Test 1: Try to read the file
st.header("1. File Reading Test")
try:
    with open('bcgeu_local_data.py', 'r', encoding='utf-8') as f:
        content = f.read()
    st.success(f"✅ File read successfully! Length: {len(content)} characters")
    
    # Show first few lines
    lines = content.split('\n')
    st.write(f"First 10 lines:")
    for i, line in enumerate(lines[:10], 1):
        st.text(f"{i:2d}: {line}")
        
except Exception as e:
    st.error(f"❌ Error reading file: {e}")
    st.stop()

# Test 2: Syntax validation
st.header("2. Syntax Validation")
try:
    ast.parse(content)
    st.success("✅ File has valid Python syntax!")
except SyntaxError as e:
    st.error(f"❌ Syntax Error:")
    st.error(f"Line {e.lineno}: {e.msg}")
    if e.text:
        st.code(e.text)
    if e.offset:
        st.write(f"Error position: {' ' * (e.offset-1)}^")

# Test 3: Import test
st.header("3. Import Test")
try:
    import bcgeu_local_data
    st.success("✅ File imports successfully!")
    
    # Test the data structure
    data = bcgeu_local_data.AGREEMENT_DATA
    st.success(f"✅ AGREEMENT_DATA loaded with {len(data)} keys")
    st.write("Top-level keys:", list(data.keys()))
    
    # Test specific coordinator data
    if 'appendices' in data and 'appendix_3' in data['appendices']:
        st.success("✅ Program Coordinator data found!")
        tables = data['appendices']['appendix_3']['workload_reduction_tables']
        st.write("Workload reduction tables:", list(tables.keys()))
    else:
        st.warning("⚠️ Program Coordinator data missing")
        
except Exception as e:
    st.error(f"❌ Import error: {e}")

# Test 4: Manual bracket check
st.header("4. Bracket Balance Check")
brackets = {'(': ')', '[': ']', '{': '}'}
stack = []
errors = []

for i, char in enumerate(content):
    if char in brackets:
        stack.append((char, i))
    elif char in brackets.values():
        if not stack:
            line_num = content[:i].count('\n') + 1
            errors.append(f"Unmatched closing bracket '{char}' at line {line_num}")
            break
        open_bracket, pos = stack.pop()
        if brackets[open_bracket] != char:
            line_num = content[:i].count('\n') + 1
            errors.append(f"Mismatched bracket at line {line_num}")
            break

if stack and not errors:
    for bracket, pos in stack[:5]:  # Show first 5 unmatched
        line_num = content[:pos].count('\n') + 1
        errors.append(f"Unmatched opening bracket '{bracket}' at line {line_num}")

if errors:
    st.error("❌ Bracket errors found:")
    for error in errors:
        st.write(f"  • {error}")
else:
    st.success("✅ All brackets properly matched!")
