import streamlit as st
import os
import re

st.title("🔧 Find and Fix bcgeu_local_data.py Syntax Error")

# Search for the file in multiple locations
possible_paths = [
    "bcgeu_local_data.py",
    "./bcgeu_local_data.py", 
    "../bcgeu_local_data.py",
    "ClaudeV3/bcgeu_local_data.py",
    "../ClaudeV3/bcgeu_local_data.py"
]

# Also search in current directory and parent directories
current_dir = os.getcwd()
st.write(f"Current directory: {current_dir}")

# List all files in current directory
st.subheader("📁 Files in Current Directory:")
try:
    files = os.listdir(".")
    for file in sorted(files):
        if file.endswith('.py'):
            st.write(f"🐍 **{file}**")
        else:
            st.write(f"📄 {file}")
except Exception as e:
    st.error(f"Error listing files: {e}")

# Check if ClaudeV3 directory exists
if os.path.exists("ClaudeV3"):
    st.subheader("📁 Files in ClaudeV3 Directory:")
    try:
        files = os.listdir("ClaudeV3")
        for file in sorted(files):
            if file.endswith('.py'):
                st.write(f"🐍 **ClaudeV3/{file}**")
                possible_paths.append(f"ClaudeV3/{file}")
    except Exception as e:
        st.error(f"Error listing ClaudeV3 files: {e}")

# Find the file
file_path = None
st.subheader("🔍 Searching for bcgeu_local_data.py...")

for path in possible_paths:
    if os.path.exists(path):
        st.success(f"✅ Found file at: {path}")
        file_path = path
        break
    else:
        st.write(f"❌ Not found at: {path}")

# Manual file selection
st.subheader("📝 Manual File Path")
manual_path = st.text_input("Enter the full path to your bcgeu_local_data.py file:", 
                           placeholder="e.g., ClaudeV3/bcgeu_local_data.py")

if manual_path and os.path.exists(manual_path):
    file_path = manual_path
    st.success(f"✅ Using manual path: {file_path}")
elif manual_path:
    st.error(f"❌ File not found at manual path: {manual_path}")

# Process the file if found
if file_path:
    st.success(f"🎯 Processing file: {file_path}")
    
    try:
        # Get file info
        file_size = os.path.getsize(file_path)
        st.write(f"📊 File size: {file_size:,} bytes")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        st.write(f"📄 File has {len(lines):,} lines")
        
        # Try to parse the file to find the exact error
        st.subheader("🔍 Syntax Check")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import ast
            ast.parse(content)
            st.success("✅ File has valid Python syntax! No fix needed.")
            
        except SyntaxError as e:
            st.error(f"❌ Syntax Error Found!")
            st.write(f"**Line:** {e.lineno}")
            st.write(f"**Error:** {e.msg}")
            if e.text:
                st.code(f"Problematic line: {e.text.strip()}")
            
            # Show context around the error
            error_line = e.lineno
            start_line = max(1, error_line - 5)
            end_line = min(len(lines), error_line + 5)
            
            st.subheader(f"📋 Context around line {error_line}:")
            
            for i in range(start_line - 1, end_line):
                line_num = i + 1
                line_content = lines[i].rstrip()
                
                if line_num == error_line:
                    st.error(f"❌ {line_num:4d}: {line_content}")
                else:
                    st.text(f"   {line_num:4d}: {line_content}")
            
            # Analyze the specific error
            if "unterminated string literal" in e.msg.lower():
                st.subheader("🛠️ Fixing Unterminated String Literal")
                
                error_line_content = lines[error_line - 1] if error_line <= len(lines) else ""
                
                st.write("**Common causes and fixes:**")
                
                # Check for unmatched quotes
                single_quotes = error_line_content.count("'")
                double_quotes = error_line_content.count('"')
                
                if single_quotes % 2 != 0:
                    st.warning("⚠️ Unmatched single quotes detected")
                    st.write("**Fix:** Escape apostrophes with backslash")
                    st.code("Before: \"Coast Mountain College's programs\"\nAfter:  \"Coast Mountain College\\'s programs\"")
                
                if double_quotes % 2 != 0:
                    st.warning("⚠️ Unmatched double quotes detected")
                
                # Show potential fixes
                if st.button("🔧 Apply Automatic Fix"):
                    fixed_lines = lines.copy()
                    
                    # Focus on the error line and surrounding lines
                    for i in range(max(0, error_line - 3), min(len(lines), error_line + 3)):
                        line = fixed_lines[i]
                        original_line = line
                        
                        # Fix smart quotes
                        line = line.replace('"', '"').replace('"', '"')
                        line = line.replace(''', "'").replace(''', "'")
                        
                        # Fix unescaped apostrophes in strings
                        # Simple pattern: find content between quotes and escape apostrophes
                        def fix_apostrophes(match):
                            quote_char = match.group(0)[0]  # First character (quote type)
                            content = match.group(1)
                            
                            if quote_char == '"':
                                # In double quotes, escape any unescaped single quotes
                                content = re.sub(r"(?<!\\)'", "\\'", content)
                            else:
                                # In single quotes, escape any unescaped single quotes
                                content = re.sub(r"(?<!\\)'", "\\'", content)
                            
                            return f"{quote_char}{content}{quote_char}"
                        
                        # Apply fixes to quoted strings
                        line = re.sub(r'"([^"]*)"', fix_apostrophes, line)
                        line = re.sub(r"'([^']*)'", fix_apostrophes, line)
                        
                        if line != original_line:
                            fixed_lines[i] = line
                            st.write(f"✅ Fixed line {i+1}")
                    
                    # Save the fixed file
                    try:
                        # Create backup
                        backup_path = file_path.replace('.py', '_backup.py')
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        st.info(f"💾 Backup created: {backup_path}")
                        
                        # Save fixed version
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(fixed_lines)
                        
                        st.success("🎉 File has been fixed!")
                        
                        # Test the fix
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                test_content = f.read()
                            ast.parse(test_content)
                            st.success("✅ SUCCESS! File now has valid syntax!")
                            st.balloons()
                        except SyntaxError as test_error:
                            st.error(f"❌ Still has syntax error: {test_error.msg} at line {test_error.lineno}")
                        
                    except Exception as save_error:
                        st.error(f"❌ Error saving file: {save_error}")
            
        except Exception as other_error:
            st.error(f"❌ Error checking syntax: {other_error}")
    
    except Exception as read_error:
        st.error(f"❌ Error reading file: {read_error}")

else:
    st.error("❌ Could not find bcgeu_local_data.py file")
    st.write("**Try these steps:**")
    st.write("1. Make sure the file exists")
    st.write("2. Check if it's in a subdirectory")
    st.write("3. Enter the correct path in the manual input above")
    st.write("4. Or copy the file to the same directory as this script")
