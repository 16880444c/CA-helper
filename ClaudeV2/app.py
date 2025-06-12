import streamlit as st
import json
import json_validator  # Import your validator functions

# Your existing Streamlit app code here...

def load_agreement_data():
    """Load the collective agreement data from JSON file"""
    try:
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
        return data
    except Exception as e:
        st.error(f"Error loading agreement data: {e}")
        return None

def main():
    st.title("Coast Mountain College Collective Agreement Assistant")
    
    # Add a sidebar option for JSON validation
    st.sidebar.title("Debug Tools")
    if st.sidebar.button("🔍 Validate JSON File"):
        st.sidebar.write("Running JSON validation...")
        
        # Capture the output from your validator
        import io
        import sys
        from contextlib import redirect_stdout
        
        # Redirect stdout to capture print statements
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            data = json_validator.validate_json_file("complete_local.json")
            json_validator.find_appendices_manually("complete_local.json")
        
        # Display the validation results
        validation_output = output_buffer.getvalue()
        st.sidebar.code(validation_output, language="text")
        
        if data:
            st.sidebar.success("✅ JSON is valid!")
            if 'appendices' in data:
                st.sidebar.success("✅ Appendices found!")
            else:
                st.sidebar.error("❌ Appendices missing from parsed data")
        else:
            st.sidebar.error("❌ JSON validation failed")
    
    # Your existing app logic
    data = load_agreement_data()
    
    if data is None:
        st.error("Could not load agreement data. Please check the JSON file.")
        st.info("Use the 'Validate JSON File' button in the sidebar to debug.")
        return
    
    # Show what sections are available
    st.sidebar.write("**Available sections:**")
    for key in data.keys():
        st.sidebar.write(f"- {key}")
    
    # Test appendices access
    if st.sidebar.button("🧪 Test Appendix 3 Access"):
        st.sidebar.write("Testing Appendix 3 access...")
        
        if 'appendices' in data:
            st.sidebar.success("✅ Found 'appendices' section")
            
            if 'appendix_3' in data['appendices']:
                st.sidebar.success("✅ Found 'appendix_3'!")
                st.sidebar.json(data['appendices']['appendix_3'])
            else:
                st.sidebar.error("❌ 'appendix_3' not found")
                st.sidebar.write("Available appendices:")
                for key in data['appendices'].keys():
                    st.sidebar.write(f"- {key}")
        else:
            st.sidebar.error("❌ 'appendices' section not found")
    
    # Your main chat interface
    user_input = st.text_input("Ask me about the collective agreement:")
    
    if user_input:
        # Your existing chat logic here
        if "appendix 3" in user_input.lower():
            if data and 'appendices' in data and 'appendix_3' in data['appendices']:
                appendix_3 = data['appendices']['appendix_3']
                st.write("## Appendix 3: Program Coordinator")
                st.write(f"**Purpose:** {appendix_3.get('purpose', 'Not specified')}")
                
                if 'workload_reduction_tables' in appendix_3:
                    st.write("### Workload Reduction Tables:")
                    for table_name, table_data in appendix_3['workload_reduction_tables'].items():
                        st.write(f"**{table_name.replace('_', ' ').title()}:**")
                        for criteria, reduction in table_data.items():
                            st.write(f"- {criteria.replace('_', ' ')}: {reduction}")
                
            else:
                st.error("Appendix 3 content is not available in the loaded data.")
                st.info("This might be due to a JSON syntax error. Use the debug tools in the sidebar.")
        else:
            st.write("I can help you find information about the collective agreement. Try asking about 'Appendix 3' or other topics.")

if __name__ == "__main__":
    main()
