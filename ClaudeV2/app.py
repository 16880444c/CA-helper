import json

def validate_json_file(filename):
    """
    Validates a JSON file and shows exactly where any syntax errors occur
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File size: {len(content)} characters")
        print(f"File lines: {len(content.split('\n'))}")
        
        # Try to parse the JSON
        data = json.loads(content)
        
        print("✅ JSON is valid!")
        print(f"Top-level keys found: {list(data.keys())}")
        
        # Check if appendices exist
        if 'appendices' in data:
            print("✅ Appendices section found!")
            appendices_keys = list(data['appendices'].keys())
            print(f"Appendices found: {appendices_keys}")
            
            if 'appendix_3' in data['appendices']:
                print("✅ Appendix 3 found!")
                print(f"Appendix 3 content preview: {str(data['appendices']['appendix_3'])[:200]}...")
            else:
                print("❌ Appendix 3 not found in appendices")
        else:
            print("❌ No appendices section found")
            
        return data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error at line {e.lineno}, column {e.colno}")
        print(f"Error message: {e.msg}")
        
        # Show the problematic area
        lines = content.split('\n')
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        
        print("\nProblematic area:")
        print("-" * 50)
        for i in range(start, end):
            marker = " >>> " if i == e.lineno - 1 else "     "
            print(f"{marker}{i+1:4d}: {lines[i]}")
        print("-" * 50)
        
        return None
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def find_truncation_issue(filename):
    """
    Specifically investigate why JSON parsing truncates before appendices
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n🔍 Investigating truncation issue...")
        
        # Find the exact position where articles end and appendices begin
        patterns_to_try = [
            '  },\n  "appendices"',
            '},\n  "appendices"', 
            '}\n  },\n  "appendices"',
            '  }\n  },\n  "appendices"',
            '    }\n  },\n  "appendices"'
        ]
        
        transition_pos = -1
        found_pattern = ""
        
        for pattern in patterns_to_try:
            pos = content.find(pattern)
            if pos > 0:
                transition_pos = pos
                found_pattern = pattern
                break
        
        if transition_pos > 0:
            print(f"Found transition pattern: {repr(found_pattern)}")
            print(f"Transition at position: {transition_pos}")
            
            # Show context around transition
            start = max(0, transition_pos - 300)
            end = min(len(content), transition_pos + 400)
            context = content[start:end]
            
            print("\nContext around articles->appendices transition:")
            print("=" * 70)
            print(context)
            print("=" * 70)
            
            # Check for invisible characters
            transition_text = content[transition_pos:transition_pos+50]
            print(f"\nTransition bytes: {transition_text.encode('utf-8')}")
            
        else:
            print("Could not find articles-to-appendices transition")
            
    except Exception as e:
        print(f"Error in truncation investigation: {e}")

def test_partial_parsing(filename):
    """
    Test parsing parts of the JSON to isolate the issue
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n🧪 Testing partial parsing...")
        
        # Find where appendices starts
        appendices_pos = content.find('"appendices"')
        if appendices_pos > 0:
            # Try parsing just up to appendices
            partial_content = content[:appendices_pos-10] + '\n  }\n}'
            
            try:
                partial_data = json.loads(partial_content)
                print("✅ Partial parsing (up to appendices) works")
                print(f"Partial keys: {list(partial_data.keys())}")
            except Exception as e:
                print(f"❌ Partial parsing failed: {e}")
            
            # Try parsing just the appendices section
            appendices_start = content.find('"appendices": {')
            if appendices_start > 0:
                # Find the end of appendices (before letters_of_agreement)
                appendices_end = content.find('"letters_of_agreement"', appendices_start)
                if appendices_end == -1:
                    appendices_end = len(content) - 10
                else:
                    appendices_end = content.rfind('},', appendices_start, appendices_end)
                
                appendices_only = '{\n  ' + content[appendices_start:appendices_end] + '\n  }\n}'
                
                try:
                    appendices_data = json.loads(appendices_only)
                    print("✅ Appendices-only parsing works")
                    print(f"Appendices keys: {list(appendices_data['appendices'].keys())}")
                except Exception as e:
                    print(f"❌ Appendices-only parsing failed: {e}")
                    print("Sample appendices content:")
                    print(appendices_only[:500])
        
    except Exception as e:
        print(f"Error in partial parsing test: {e}")

if __name__ == "__main__":
    filename = "complete_local.json"
    
    print("🔍 Validating JSON file...")
    print("=" * 60)
    
    # Validate the JSON
    data = validate_json_file(filename)
    
    # If no appendices found, investigate further
    if data and 'appendices' not in data:
        find_truncation_issue(filename)
        test_partial_parsing(filename)
    
    print("\n" + "=" * 60)
    print("Validation complete!")
