import streamlit as st
import os
import re

st.title("🔧 Fix Syntax Error in bcgeu_local_data.py")

# File path
file_path = "bcgeu_local_data.py"

if os.path.exists(file_path):
    st.success(f"✅ Found file: {file_path}")
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        st.write(f"📄 File has {len(lines)} lines")
        
        # Show the problematic area around line 2385
        error_line = 2385
        start_line = max(1, error_line - 10)
        end_line = min(len(lines), error_line + 10)
        
        st.subheader(f"🔍 Lines around {error_line} (where syntax error occurs):")
        
        # Display the problematic area
        problem_lines = []
        for i in range(start_line - 1, end_line):
            line_num = i + 1
            line_content = lines[i].rstrip()
            
            # Count quotes in this line
            single_quotes = line_content.count("'")
            double_quotes = line_content.count('"')
            
            # Check for unmatched quotes
            quote_issue = ""
            if single_quotes % 2 != 0:
                quote_issue += " ⚠️ UNMATCHED SINGLE QUOTES"
            if double_quotes % 2 != 0:
                quote_issue += " ⚠️ UNMATCHED DOUBLE QUOTES"
            
            if line_num == error_line:
                st.error(f"❌ {line_num:4d}: {line_content}{quote_issue}")
                problem_lines.append((line_num, line_content, quote_issue))
            else:
                if quote_issue:
                    st.warning(f"⚠️  {line_num:4d}: {line_content}{quote_issue}")
                    problem_lines.append((line_num, line_content, quote_issue))
                else:
                    st.text(f"   {line_num:4d}: {line_content}")
        
        # Analyze the specific problems
        st.subheader("🔧 Automatic Fixes")
        
        if st.button("🛠️ Attempt Automatic Fix"):
            fixed_lines = lines.copy()
            fixes_made = []
            
            # Common fixes for unterminated string literals
            for i in range(max(0, error_line - 20), min(len(lines), error_line + 20)):
                line = fixed_lines[i]
                original_line = line
                line_num = i + 1
                
                # Fix 1: Replace smart quotes with regular quotes
                line = line.replace('"', '"').replace('"', '"')
                line = line.replace(''', "'").replace(''', "'")
                
                # Fix 2: Escape apostrophes in strings
                # Find strings and escape apostrophes within them
                def fix_apostrophes_in_strings(text):
                    # Pattern to find strings (both single and double quoted)
                    pattern = r'("(?:[^"\\]|\\.)*")|\'([^\'\\\\]|\\\\.)*\''
                    
                    def replace_func(match):
                        full_match = match.group(0)
                        if full_match.startswith('"'):
                            # Double quoted string - escape any unescaped apostrophes
                            return full_match.replace("\\'", "TEMP_ESCAPED").replace("'", "\\'").replace("TEMP_ESCAPED", "\\'")
                        else:
                            # Single quoted string - escape any unescaped apostrophes
                            inner = full_match[1:-1]  # Remove quotes
                            inner = inner.replace("\\'", "TEMP_ESCAPED").replace("'", "\\'").replace("TEMP_ESCAPED", "\\'")
                            return f"'{inner}'"
                    
                    return re.sub(pattern, replace_func, text)
                
                # Apply the fix
                new_line = fix_apostrophes_in_strings(line)
                
                # Fix 3: Handle common problematic patterns
                # Fix unmatched quotes at end of lines
                if new_line.rstrip().endswith('"') and new_line.count('"') % 2 != 0:
                    # Add missing quote at beginning of content
                    content_start = new_line.find(':') + 1
                    if content_start > 0:
                        before_content = new_line[:content_start].strip()
                        after_content = new_line[content_start:].strip()
                        if not after_content.startswith('"'):
                            new_line = before_content + ' "' + after_content
                
                # Fix 4: Handle lines with odd number of quotes
                if "'" in new_line:
                    single_quote_count = new_line.count("'")
                    if single_quote_count % 2 != 0:
                        # Try to fix by escaping apostrophes in likely text content
                        if '": "' in new_line or "': '" in new_line:
                            # This looks like a key-value pair
                            parts = new_line.split('": "' if '": "' in new_line else "': '", 1)
                            if len(parts) == 2:
                                key_part = parts[0]
                                value_part = parts[1]
                                # Escape apostrophes in the value part
                                value_part = value_part.replace("'", "\\'")
                                separator = '": "' if '": "' in new_line else "': '"
                                new_line = key_part + separator + value_part
                
                if new_line != original_line:
                    fixed_lines[i] = new_line
                    fixes_made.append(f"Line {line_num}: Fixed quote issues")
            
            # Show what fixes were made
            if fixes_made:
                st.success("🎉 Fixes applied:")
                for fix in fixes_made:
                    st.write(f"  ✅ {fix}")
                
                # Save the fixed file
                try:
                    # Backup original file
                    backup_path = file_path.replace('.py', '_backup.py')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    st.info(f"💾 Original file backed up as: {backup_path}")
                    
                    # Save fixed file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(fixed_lines)
                    st.success(f"✅ Fixed file saved as: {file_path}")
                    
                    # Test the fixed file
                    st.write("🧪 Testing the fixed file...")
                    try:
                        import ast
                        with open(file_path, 'r', encoding='utf-8') as f:
                            fixed_content = f.read()
                        ast.parse(fixed_content)
                        st.success("🎉 SUCCESS! The file now has valid Python syntax!")
                        st.balloons()
                    except SyntaxError as e:
                        st.error(f"❌ Still has syntax error at line {e.lineno}: {e.msg}")
                        st.write("You may need to manually fix remaining issues.")
                    except Exception as e:
                        st.error(f"❌ Other error: {e}")
                        
                except Exception as e:
                    st.error(f"❌ Error saving fixed file: {e}")
            else:
                st.warning("⚠️ No automatic fixes could be applied. Manual editing may be required.")
        
        # Manual fix suggestions
        st.subheader("🛠️ Manual Fix Instructions")
        st.write("If automatic fix doesn't work, here's how to manually fix the most common issues:")
        
        st.write("**1. Unmatched Quotes:**")
        st.code('''
# Wrong (causes syntax error):
"content": "Coast Mountain College's programs"

# Right (escaped apostrophe):
"content": "Coast Mountain College\\'s programs"
        ''')
        
        st.write("**2. Multi-line Strings:**")
        st.code('''
# Wrong (line break in string):
"content": "This is a very long
line that breaks"

# Right (escaped or triple quotes):
"content": "This is a very long\\nline that breaks"
        ''')
        
        st.write("**3. Smart Quotes:**")
        st.code('''
# Wrong (smart quotes):
"content": "Coast Mountain College's programs"

# Right (regular quotes):
"content": "Coast Mountain College's programs"
        ''')
        
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        
else:
    st.error(f"❌ File not found: {file_path}")
    st.write("Make sure the file exists in the same directory as this script.")
