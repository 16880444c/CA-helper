import streamlit as st
import json
import openai
from datetime import datetime
import re
import os

# Set page config
st.set_page_config(
    page_title="Collective Agreement Assistant",
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
    # Debug: Show current working directory and files
    current_dir = os.getcwd()
    files_in_dir = os.listdir(current_dir)
    
    st.write(f"**Debug Info:**")
    st.write(f"Current working directory: `{current_dir}`")
    st.write(f"Files in directory: {files_in_dir}")
    
    # Check if files exist
    local_exists = os.path.exists('complete_local.json')
    common_exists = os.path.exists('complete_common.json')
    
    st.write(f"complete_local.json exists: {local_exists}")
    st.write(f"complete_common.json exists: {common_exists}")
    
    try:
        # Try to read the files
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            collective_agreement = json.load(f)
        
        with open('complete_common.json', 'r', encoding='utf-8') as f:
            common_agreement = json.load(f)
        
        st.success("✅ Files loaded successfully from directory!")
        return collective_agreement, common_agreement
        
    except FileNotFoundError as e:
        st.error(f"FileNotFoundError: {str(e)}")
        
        # Show file uploader as alternative
        st.markdown("### Alternative: Upload Files")
        col1, col2 = st.columns(2)
        
        with col1:
            local_file = st.file_uploader("Upload complete_local.json", type="json", key="local")
        with col2:
            common_file = st.file_uploader("Upload complete_common.json", type="json", key="common")
        
        if local_file and common_file:
            try:
                collective_agreement = json.load(local_file)
                common_agreement = json.load(common_file)
                st.success("✅ Files loaded successfully from upload!")
                return collective_agreement, common_agreement
            except Exception as e:
                st.error(f"Error loading uploaded files: {str(e)}")
                return None, None
        
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

def create_system_prompt(collective_agreement, common_agreement):
    """Create the system prompt for the HR advisor"""
    
    # Safely extract metadata with fallbacks
    collective_metadata = collective_agreement.get('agreement_metadata', {})
    common_metadata = common_agreement.get('agreement_metadata', {})
    
    collective_title = collective_metadata.get('title', 'Local Collective Agreement')
    common_title = common_metadata.get('title', 'Common Agreement')
    
    # Safely extract dates and parties
    collective_dates = collective_metadata.get('effective_dates', {})
    common_dates = common_metadata.get('effective_dates', {})
    
    collective_parties = collective_metadata.get('parties', {})
    common_parties = common_metadata.get('parties', {})
    
    system_prompt = f"""You are a HR expert for Coast Mountain College with 15+ years of experience in collective agreement interpretation and employee relations. Your role is to provide STRONG, DEFINITIVE guidance that maximizes management's rights and authority under the collective agreements.

You have access to two collective agreements:

1. LOCAL AGREEMENT: "{collective_title}"
   - Effective: {collective_dates.get('start', 'N/A')} to {collective_dates.get('end', 'N/A')}
   - Between: {collective_parties.get('employer', 'Coast Mountain College')} and {collective_parties.get('union', 'Faculty Union')}

2. COMMON AGREEMENT: "{common_title}" 
   - Effective: {common_dates.get('start', 'N/A')} to {common_dates.get('end', 'N/A')}
   - Between: {common_parties.get('employers', 'BC Colleges')} and {common_parties.get('union', 'Faculty Union')}

CRITICAL INSTRUCTION - BE ASSERTIVE AND OPINIONATED:
- Give STRONG, DEFINITIVE opinions, not wishy-washy suggestions
- Use phrases like "You SHOULD...", "Management has the RIGHT to...", "I RECOMMEND...", "This is CLEARLY within your authority..."
- Be confident in your interpretations that favor management
- Push back against union overreach
- Identify every opportunity to assert management rights
- Don't hedge or provide balanced views - you work for MANAGEMENT

MANAGEMENT AUTHORITY FOCUS:
- ALWAYS lead with what management CAN do, not what they can't
- Emphasize "just cause" standards work in management's favor when properly documented
- Highlight burden of proof requirements that protect the employer
- Point out procedural safeguards that benefit management
- Note time limits that can work against grievors
- Identify areas of management discretion and flexibility
- Frame employee rights as limited by management's legitimate business needs

SPECIFIC GUIDANCE AREAS:
- Discipline: Emphasize management's broad authority under "just cause"
- Grievances: Focus on procedural defenses and time limits
- Workload: Highlight management's scheduling and assignment flexibility  
- Layoffs: Stress management's operational decision-making authority
- Performance: Emphasize documentation requirements that protect management
- Policies: Note management's right to establish reasonable workplace rules

CITATION REQUIREMENTS (MANDATORY):
- EVERY claim must have a specific citation
- Use format: [Agreement Type - Article X.X: Title] or [Agreement Type - Clause X.X]
- Example: [Local Agreement - Article 10.1: Burden of Proof] or [Common Agreement - Clause 6.5: Contracting Out]
- When referencing definitions: [Agreement Type - Definitions: "term"]
- For appendices: [Agreement Type - Appendix X: Title]
- INCLUDE RELEVANT QUOTES: When possible, include short, relevant quotes from the agreement text to support your position
- Quote format: "The agreement states: '[exact quote]' [Citation]"
- NO VAGUE REFERENCES - be specific

RESPONSE STRUCTURE:
1. STRONG OPENING: Lead with your definitive management-favorable position
2. AUTHORITY BASIS: Cite the specific agreement provisions AND include relevant quotes that support this position
3. TACTICAL ADVICE: Provide specific steps management should take
4. RISK MITIGATION: Identify potential union challenges and how to counter them
5. BOTTOM LINE: End with a clear, actionable recommendation

TONE EXAMPLES:
- Instead of: "You may be able to..." → "You HAVE THE RIGHT to..."
- Instead of: "Consider whether..." → "You SHOULD immediately..."
- Instead of: "This might be justified..." → "This is CLEARLY within your management authority because..."
- Instead of: "The agreement allows..." → "Management is EXPLICITLY authorized to..."

Remember: You are not a neutral arbitrator. You are MANAGEMENT'S advisor. Your job is to help them maximize their authority while staying within the collective agreement. Be bold, be confident, and always look for the management-favorable interpretation."""

    return system_prompt

def create_essential_context(collective_agreement, common_agreement):
    """Create context with essential agreement information"""
    
    # Safely extract metadata
    collective_metadata = collective_agreement.get('agreement_metadata', {})
    common_metadata = common_agreement.get('agreement_metadata', {})
    
    collective_title = collective_metadata.get('title', 'Local Collective Agreement')
    common_title = common_metadata.get('title', 'Common Agreement')
    
    collective_dates = collective_metadata.get('effective_dates', {})
    common_dates = common_metadata.get('effective_dates', {})
    
    collective_parties = collective_metadata.get('parties', {})
    common_parties = common_metadata.get('parties', {})
    
    context = f"""
COLLECTIVE AGREEMENTS AVAILABLE:

LOCAL AGREEMENT: "{collective_title}"
- Effective: {collective_dates.get('start', 'N/A')} to {collective_dates.get('end', 'N/A')}
- Parties: {collective_parties.get('employer', 'Coast Mountain College')} and {collective_parties.get('union', 'Faculty Union')}

COMMON AGREEMENT: "{common_title}" 
- Effective: {common_dates.get('start', 'N/A')} to {common_dates.get('end', 'N/A')}
- Parties: {common_parties.get('employers', 'BC Colleges')} and {common_parties.get('union', 'Faculty Union')}

KEY DEFINITIONS FROM LOCAL AGREEMENT:
{json.dumps(collective_agreement.get('definitions', {}), indent=2)}

KEY DEFINITIONS FROM COMMON AGREEMENT:
{json.dumps(common_agreement.get('definitions', {}), indent=2)}

ARTICLE STRUCTURE - LOCAL AGREEMENT:
"""
    
    # Safely add article structure from local agreement
    if 'articles' in collective_agreement and isinstance(collective_agreement['articles'], dict):
        for article_num, article_data in collective_agreement['articles'].items():
            if isinstance(article_data, dict):
                article_title = article_data.get('title', 'No Title')
                context += f"Article {article_num}: {article_title}\n"
                
                if 'sections' in article_data and isinstance(article_data['sections'], dict):
                    for section_num, section_data in article_data['sections'].items():
                        if isinstance(section_data, dict):
                            section_title = section_data.get('title', 'No Title')
                            context += f"  - Section {section_num}: {section_title}\n"
            else:
                context += f"Article {article_num}: [Structure varies]\n"
    
    context += "\nARTICLE STRUCTURE - COMMON AGREEMENT:\n"
    
    # Safely add article structure from common agreement
    if 'articles' in common_agreement and isinstance(common_agreement['articles'], dict):
        for article_num, article_data in common_agreement['articles'].items():
            if isinstance(article_data, dict):
                article_title = article_data.get('title', 'No Title')
                context += f"Article {article_num}: {article_title}\n"
                
                if 'sections' in article_data and isinstance(article_data['sections'], dict):
                    for section_num, section_data in article_data['sections'].items():
                        if isinstance(section_data, dict):
                            section_title = section_data.get('title', 'No Title')
                            context += f"  - Section {section_num}: {section_title}\n"
            else:
                context += f"Article {article_num}: [Structure varies]\n"
    
    context += """

IMPORTANT: You have access to the complete content of both agreements. When responding to questions:
1. Reference specific articles, sections, and clauses accurately
2. Provide proper citations in the format [Agreement Type - Article X.X: Title]
3. Focus on management rights and authority
4. If you need specific content from an article, refer to it by number and title
"""
    
    return context

def get_ai_response(user_message, collective_agreement, common_agreement, api_key):
    """Get response from OpenAI API"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        system_prompt = create_system_prompt(collective_agreement, common_agreement)
        # Use essential context with structure overview
        agreement_context = create_essential_context(collective_agreement, common_agreement)
        
        # Prepare messages for the API
        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + agreement_context}
        ]
        
        # Add conversation history (limit to last 6 exchanges to save tokens)
        recent_messages = st.session_state.messages[-12:] if len(st.session_state.messages) > 12 else st.session_state.messages
        for msg in recent_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using 3.5-turbo for better rate limits
            messages=messages,
            max_tokens=1000,  
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except openai.RateLimitError as e:
        return "⚠️ **Rate limit exceeded.** Please wait a moment and try again. Consider upgrading your OpenAI plan for higher limits."
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

def main():
    st.title("⚖️ Collective Agreement Assistant")
    st.markdown("*Management-focused guidance for Coast Mountain College collective agreements*")
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("Configuration")
        
        # Try to get API key from secrets first, then environment, then user input
        api_key = None
        try:
            # First try Streamlit secrets (for cloud deployment)
            api_key = st.secrets["OPENAI_API_KEY"]
            st.success("✅ API key loaded from secrets")
        except:
            try:
                # Then try environment variables (for local development)
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    st.success("✅ API key loaded from environment")
            except:
                pass
        
        # If no API key found, ask user to input it
        if not api_key:
            api_key = st.text_input("OpenAI API Key", type="password", 
                                   help="Enter your OpenAI API key, add it to Streamlit secrets, or set OPENAI_API_KEY environment variable")
        
        st.markdown("---")
        st.header("About")
        st.markdown("""
        This tool provides HR guidance based on:
        - Coast Mountain College Collective Agreement (2019-2022)
        - Common Agreement (2022-2025)
        
        **Perspective**: Management rights and authority
        **Citations**: All responses include specific agreement references
        """)
        
        if st.button("🆕 New Topic"):
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
