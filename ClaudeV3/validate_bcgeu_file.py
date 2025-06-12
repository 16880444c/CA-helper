import streamlit as st
import os
import sys

st.title("BCGEU File Debug Helper")

# Check current working directory
st.header("1. Directory Information")
current_dir = os.getcwd()
st.write(f"Current working directory: `{current_dir}`")

# List all files in current directory
st.header("2. Files in Current Directory")
try:
    files = os.listdir(current_dir)
    st.write("All files:")
    for file in sorted(files):
        if file.endswith('.py'):
            st.write(f"📄 **{file}**")
        else:
            st.write(f"📁 {file}")
except Exception as e:
    st.error(f"Error listing files: {e}")

# Check if the specific file exists
st.header("3. BCGEU File Check")
file_paths_to_check = [
    'bcgeu_local_data.py',
    './bcgeu_local_data.py',
    os.path.join(current_dir, 'bcgeu_local_data.py')
]

for path in file_paths_to_check:
    if os.path.exists(path):
        st.success(f"✅ Found file at: `{path}`")
        
        # Get file info
        file_size = os.path.getsize(path)
        st.write(f"File size: {file_size:,} bytes")
        
        # Try to read first few lines
        try:
            with open(path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline().strip() for _ in range(5)]
            st.write("First 5 lines:")
            for i, line in enumerate(first_lines, 1):
                st.code(f"{i}: {line}")
        except Exception as e:
            st.error(f"Error reading file: {e}")
        break
    else:
        st.write(f"❌ Not found at: `{path}`")

# Check Python path
st.header("4. Python Path")
st.write("Python is looking for modules in these directories:")
for i, path in enumerate(sys.path):
    st.write(f"{i+1}. `{path}`")

# Try different import methods
st.header("5. Import Tests")

# Test 1: Direct import
try:
    import bcgeu_local_data
    st.success("✅ Direct import successful!")
    st.write(f"Module file location: `{bcgeu_local_data.__file__}`")
except Exception as e:
    st.error(f"❌ Direct import failed: {e}")

# Test 2: Import with explicit path
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("bcgeu_local_data", "bcgeu_local_data.py")
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        st.success("✅ Explicit path import successful!")
        if hasattr(module, 'AGREEMENT_DATA'):
            st.success("✅ AGREEMENT_DATA found!")
        else:
            st.error("❌ AGREEMENT_DATA not found in module")
    else:
        st.error("❌ Could not create module spec")
except Exception as e:
    st.error(f"❌ Explicit import failed: {e}")

# Test 3: Check file content structure
if os.path.exists('bcgeu_local_data.py'):
    st.header("6. File Content Analysis")
    try:
        with open('bcgeu_local_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        st.write(f"Total characters: {len(content):,}")
        st.write(f"Total lines: {content.count(chr(10)) + 1:,}")
        
        # Check for AGREEMENT_DATA
        if 'AGREEMENT_DATA' in content:
            st.success("✅ AGREEMENT_DATA found in file")
        else:
            st.error("❌ AGREEMENT_DATA not found in file")
            
        # Check for syntax issues
        import ast
        try:
            ast.parse(content)
            st.success("✅ File has valid Python syntax")
        except SyntaxError as e:
            st.error(f"❌ Syntax error at line {e.lineno}: {e.msg}")
            if e.text:
                st.code(e.text)
                
    except Exception as e:
        st.error(f"Error analyzing file: {e}")
