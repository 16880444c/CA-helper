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
            print("\n🔍 Investigating truncation issue...")
            
            # Check if this is a truncation issue during parsing
            if 'articles' in data:
                print(f"Articles found: {len(data['articles'])} articles")
                last_article = max(data['articles'].keys(), key=int)
                print(f"Last article parsed: Article {last_article}")
                
                # Look at the end of articles section in raw text
                articles_end_pos = content.find('  },\n  "appendices"')
                if articles_end_pos == -1:
                    articles_end_pos = content.find('},\n  "appendices"')
                if articles_end_pos == -1:
                    articles_end_pos = content.find('}\n  },\n  "appendices"')
                
                if articles_end_pos > 0:
                    print(f"Found articles-to-appendices transition at position: {articles_end_pos}")
                    
                    # Show more context around the transition
                    start = max(0, articles_end_pos - 200)
                    end = min(len(content), articles_end_pos + 300)
                    context = content[start:end]
                    print(f"\nExtended context around transition:")
                    print("=" * 60)
                    print(context)
                    print("=" * 60)
                else:
                    print("Could not find articles-to-appendices transition")
            
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
        
        # Try to find common JSON issues
        print("\nCommon JSON issues to check:")
        print("1. Missing commas between object properties")
        print("2. Extra trailing commas")
        print("3. Unescaped quotes in strings")
        print("4. Mismatched brackets/braces")
        print("5. Invalid escape sequences")
        
        return None
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def find_appendices_manually(filename):
    """
    Manually search for appendices in the file to see if it exists as text
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Search for appendices mentions
        appendices_pos = content.find('"appendices"')
        appendix_3_pos = content.find('"appendix_3"')
        
        print(f"\n📍 Manual search results:")
        print(f"'appendices' found at position: {appendices_pos}")
        print(f"'appendix_3' found at position: {appendix_3_pos}")
        
        if appendices_pos > 0:
            # Show context around appendices
            start = max(0, appendices_pos - 100)
            end = min(len(content), appendices_pos + 200)
            print(f"\nContext around 'appendices':")
            print(f"...{content[start:end]}...")
            
    except Exception as e:
        print(f"Error in manual search: {e}")

if __name__ == "__main__":
    filename = "complete_local.json"
    
    print("🔍 Validating JSON file...")
    print("=" * 60)
    
    # First try to validate the JSON
    data = validate_json_file(filename)
    
    # Also do a manual search
    find_appendices_manually(filename)
    
    print("\n" + "=" * 60)
    print("Validation complete!")
    
    if data is None:
        print("\n💡 Next steps:")
        print("1. Fix the JSON syntax error shown above")
        print("2. Re-run this validator")
        print("3. Once valid, your Streamlit app should find Appendix 3")
