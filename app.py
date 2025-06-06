import streamlit as st
import json
import openai
from datetime import datetime
import re

# Set page config
st.set_page_config(
    page_title="HR Advisor - Collective Agreement Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'agreements_loaded' not in st.session_state:
    st.session_state.agreements_loaded = False

def load_agreements():
    """Load the collective agreements from JSON files"""
    try:
        # You'll need to upload these JSON files to your Streamlit app
        with open('collective_agreement_json.json', 'r') as f:
            collective_agreement = json.load(f)
        
        with open('common_agreement_json.json', 'r') as f:
            common_agreement = json.load(f)
        
        return collective_agreement, common_agreement
    except FileNotFoundError:
        st.error("Agreement files not found. Please ensure both JSON files are uploaded.")
        return None, None

def create_system_prompt(collective_agreement, common_agreement):
    """Create the system prompt for the HR advisor"""
    
    # Extract key information for the prompt
    collective_title = collective_agreement['agreement_metadata']['title']
    common_title = common_agreement['agreement_metadata']['title']
    
    system_prompt = f"""You are an experienced HR advisor for Coast Mountain College with expertise in collective agreement interpretation. Your role is to provide guidance that ensures management rights are properly asserted while remaining compliant with the collective agreements.

You have access to two collective agreements:

1. LOCAL AGREEMENT: "{collective_title}"
   - Effective: {collective_agreement['agreement_metadata']['effective_dates']['start']} to {collective_agreement['agreement_metadata']['effective_dates']['end']}
   - Between: {collective_agreement['agreement_metadata']['parties']['employer']} and {collective_agreement['agreement_metadata']['parties']['union']}

2. COMMON AGREEMENT: "{common_title}" 
   - Effective: {common_agreement['agreement_metadata']['effective_dates']['start']} to {common_agreement['agreement_metadata']['effective_dates']['end']}
   - Between: {common_agreement['agreement_metadata']['parties']['employers']} and {common_agreement['agreement_metadata']['parties']['union']}

MANAGEMENT PERSPECTIVE GUIDELINES:
- Always look for opportunities to assert legitimate management rights
- Identify areas where management has discretion or authority
- Point out procedural requirements that protect the employer
- Highlight burden of proof requirements that favor management
- Note time limits and procedural safeguards
- Emphasize "just cause" standards and employer authority
- Look for language that gives management flexibility

CITATION REQUIREMENTS:
- ALWAYS provide specific citations for every claim
- Use format: [Agreement Type - Article X.X: Title] or [Agreement Type - Clause X.X]
- Example: [Local Agreement - Article 10.1: Burden of Proof] or [Common Agreement - Clause 6.5: Contracting Out]
- When referencing definitions, cite them as: [Agreement Type - Definitions: "term"]
- For appendices: [Agreement Type - Appendix X: Title]

RESPONSE STYLE:
- Be conversational but professional
- Start with the management-favorable interpretation
- Acknowledge employee rights but frame them within management's authority
- Provide practical guidance for implementation
- Be thorough but accessible

Always structure responses as:
1. Direct answer highlighting management position
2. Specific citation(s)
3. Practical implementation advice
4. Any cautions or procedural requirements

The agreements contain the complete text and you should reference them accurately."""

    return system_prompt

def format_agreements_for_context(collective_agreement, common_agreement):
    """Format the agreements as context for the AI"""
    context = f"""
COLLECTIVE AGREEMENT DATA:
{json.dumps(collective_agreement, indent=2)}

COMMON AGREEMENT DATA:
{json.dumps(common_agreement, indent=2)}
"""
    return context

def get_ai_response(user_message, collective_agreement, common_agreement, api_key):
    """Get response from OpenAI API"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        system_prompt = create_system_prompt(collective_agreement, common_agreement)
        agreement_context = format_agreements_for_context(collective_agreement, common_agreement)
        
        # Prepare messages for the API
        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + agreement_context}
        ]
        
        # Add conversation history
        for msg in st.session_state.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for cost savings
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

def main():
    st.title("⚖️ HR Advisor - Collective Agreement Assistant")
    st.markdown("*Management-focused guidance for Coast Mountain College collective agreements*")
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key", type="password")
        
        st.markdown("---")
        st.header("About")
        st.markdown("""
        This tool provides HR guidance based on:
        - Coast Mountain College Collective Agreement (2019-2022)
        - Common Agreement (2022-2025)
        
        **Perspective**: Management rights and authority
        **Citations**: All responses include specific agreement references
        """)
        
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Load agreements
    if not st.session_state.agreements_loaded:
        with st.spinner("Loading collective agreements..."):
            collective_agreement, common_agreement = load_agreements()
            if collective_agreement and common_agreement:
                st.session_state.collective_agreement = collective_agreement
                st.session_state.common_agreement = common_agreement
                st.session_state.agreements_loaded = True
                st.success("Collective agreements loaded successfully!")
            else:
                st.stop()
    
    # Main chat interface
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to begin.")
        st.stop()
    
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about collective agreement provisions..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing collective agreements..."):
                response = get_ai_response(
                    prompt, 
                    st.session_state.collective_agreement,
                    st.session_state.common_agreement,
                    api_key
                )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick question buttons
    if len(st.session_state.messages) == 0:
        st.markdown("### Quick Start Questions:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Employee Discipline Process"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are management's rights regarding employee discipline and dismissal?"
                })
                st.rerun()
                
            if st.button("Layoff Procedures"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What authority does management have in layoff situations?"
                })
                st.rerun()
        
        with col2:
            if st.button("Grievance Process"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are the time limits and procedures for grievances that protect management?"
                })
                st.rerun()
                
            if st.button("Workload Management"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What flexibility does management have in assigning instructor workloads?"
                })
                st.rerun()

if __name__ == "__main__":
    main()
