import streamlit as st
import json
import openai
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Coast Mountain College Agreement Assistant",
    page_icon="⚖️",
    layout="wide"
)

def load_agreement_from_file(file) -> dict:
    """Load agreement from uploaded file"""
    try:
        content = file.read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def load_builtin_agreements() -> tuple:
    """Load the built-in agreements from JSON files"""
    try:
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            local_agreement = json.load(f)
        
        with open('complete_common.json', 'r', encoding='utf-8') as f:
            common_agreement = json.load(f)
        
        return local_agreement, common_agreement
        
    except FileNotFoundError as e:
        st.error(f"JSON files not found: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"Error loading built-in agreements: {e}")
        return None, None

def format_agreement_for_context(agreement: dict, agreement_name: str) -> str:
    """Convert agreement JSON to formatted text for GPT context"""
    context = f"=== {agreement_name.upper()} ===\n\n"
    
    # Add metadata
    if 'agreement_metadata' in agreement:
        context += "AGREEMENT METADATA:\n"
        context += json.dumps(agreement['agreement_metadata'], indent=2) + "\n\n"
    
    # Add definitions
    if 'definitions' in agreement:
        context += "DEFINITIONS:\n"
        for term, definition in agreement['definitions'].items():
            context += f"- {term}: {definition}\n"
        context += "\n"
    
    # Add articles
    if 'articles' in agreement:
        context += "ARTICLES:\n\n"
        for article_num, article_data in agreement['articles'].items():
            if isinstance(article_data, dict):
                title = article_data.get('title', f'Article {article_num}')
                context += f"ARTICLE {article_num}: {title}\n"
                
                # Add sections
                if 'sections' in article_data:
                    for section_key, section_data in article_data['sections'].items():
                        context += f"\nSection {section_key}:\n"
                        if isinstance(section_data, dict):
                            if 'title' in section_data:
                                context += f"Title: {section_data['title']}\n"
                            if 'content' in section_data:
                                context += f"Content: {section_data['content']}\n"
                            if 'subsections' in section_data:
                                context += "Subsections:\n"
                                for sub_key, sub_content in section_data['subsections'].items():
                                    context += f"  {sub_key}) {sub_content}\n"
                        else:
                            context += f"{section_data}\n"
                
                # Add other content if no sections
                if 'sections' not in article_data and 'content' in article_data:
                    context += f"\n{article_data['content']}\n"
                
                context += "\n" + "="*50 + "\n\n"
    
    # Add appendices
    if 'appendices' in agreement:
        context += "APPENDICES:\n\n"
        for appendix_key, appendix_data in agreement['appendices'].items():
            context += f"APPENDIX {appendix_key.upper()}:\n"
            if isinstance(appendix_data, dict):
                if 'title' in appendix_data:
                    context += f"Title: {appendix_data['title']}\n\n"
                context += json.dumps(appendix_data, indent=2)
            else:
                context += str(appendix_data)
            context += "\n\n" + "="*50 + "\n\n"
    
    return context

def generate_response(query: str, local_agreement: dict, common_agreement: dict, agreement_scope: str, api_key: str) -> str:
    """Generate response using GPT-4o-mini with complete agreement context"""
    
    # Build context based on selected scope
    context = ""
    if agreement_scope == "Local Agreement Only":
        context = format_agreement_for_context(local_agreement, "Coast Mountain College Local Agreement")
    elif agreement_scope == "Common Agreement Only":
        context = format_agreement_for_context(common_agreement, "BCGEU Common Agreement")
    else:  # Both agreements
        context = format_agreement_for_context(local_agreement, "Coast Mountain College Local Agreement")
        context += "\n\n" + format_agreement_for_context(common_agreement, "BCGEU Common Agreement")
    
    system_prompt = f"""You are a HR expert for Coast Mountain College with 15+ years of experience in collective agreement interpretation and employee relations. Your role is to provide STRONG, DEFINITIVE guidance that maximizes management's rights and authority under the collective agreements.

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

    user_prompt = f"""Based on the complete collective agreement provisions below, provide strong management-focused guidance for this question:

QUESTION: {query}

COMPLETE COLLECTIVE AGREEMENT CONTENT:
{context}

Provide definitive, management-favorable guidance with specific citations and quotes from the agreement text."""

    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Much more cost-effective
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.1
        )
        
        # Update usage stats
        if 'total_queries' not in st.session_state:
            st.session_state.total_queries = 0
        st.session_state.total_queries += 1
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {e}"

def main():
    st.title("⚖️ Coast Mountain College Agreement Assistant")
    st.markdown("*Complete collective agreement analysis with management-focused guidance*")
    
    # Initialize session state
    if 'agreements_loaded' not in st.session_state:
        st.session_state.agreements_loaded = False
    if 'local_agreement' not in st.session_state:
        st.session_state.local_agreement = None
    if 'common_agreement' not in st.session_state:
        st.session_state.common_agreement = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'total_queries' not in st.session_state:
        st.session_state.total_queries = 0
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key handling
        api_key = None
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            st.success("✅ API key loaded from secrets")
        except:
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    st.success("✅ API key loaded from environment")
            except:
                pass
        
        if not api_key:
            api_key = st.text_input("OpenAI API Key", type="password", 
                                   help="Enter your OpenAI API key")
            if not api_key:
                st.warning("Please provide your OpenAI API key to continue")
                st.stop()
        
        st.markdown("---")
        
        # Agreement Selection
        st.header("📋 Agreement Selection")
        agreement_scope = st.radio(
            "Which agreement(s) do you need to query?",
            ["Both Agreements (Complete Analysis)", 
             "Local Agreement Only", 
             "Common Agreement Only"],
            help="Select specific agreement to focus analysis"
        )
        
        # File loading
        st.header("📁 Load Agreements")
        
        # Check for built-in files
        builtin_available = os.path.exists('complete_local.json') and os.path.exists('complete_common.json')
        
        if builtin_available:
            use_builtin = st.checkbox("Use built-in JSON files", value=True)
        else:
            use_builtin = False
            st.info("💡 Place 'complete_local.json' and 'complete_common.json' in the app directory")
        
        if use_builtin and builtin_available:
            if st.button("🔄 Load Built-in Agreements"):
                with st.spinner("Loading agreements..."):
                    local_agreement, common_agreement = load_builtin_agreements()
                    
                    if local_agreement and common_agreement:
                        st.session_state.local_agreement = local_agreement
                        st.session_state.common_agreement = common_agreement
                        st.session_state.agreements_loaded = True
                        st.success("✅ Agreements loaded successfully!")
                        st.rerun()
        else:
            local_file = st.file_uploader("Local Agreement JSON", type="json", key="local")
            common_file = st.file_uploader("Common Agreement JSON", type="json", key="common")
            
            if st.button("🔄 Load Uploaded Agreements"):
                if local_file and common_file:
                    with st.spinner("Loading agreements..."):
                        local_agreement = load_agreement_from_file(local_file)
                        common_agreement = load_agreement_from_file(common_file)
                        
                        if local_agreement and common_agreement:
                            st.session_state.local_agreement = local_agreement
                            st.session_state.common_agreement = common_agreement
                            st.session_state.agreements_loaded = True
                            st.success("✅ Agreements loaded successfully!")
                            st.rerun()
                else:
                    st.error("Please upload both agreement files")
        
        # Stats
        if st.session_state.agreements_loaded:
            st.markdown("---")
            st.header("📊 Status")
            st.success("✅ Agreements Loaded")
            st.info(f"🔍 Queries made: {st.session_state.total_queries}")
            st.info(f"📋 Scope: {agreement_scope}")
            
            # Estimate context size
            if agreement_scope == "Both Agreements (Complete Analysis)":
                st.info("📄 Full agreements loaded")
            else:
                st.info(f"📄 {agreement_scope} loaded")
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        **Complete Agreement Analysis**
        - Full agreement context loaded
        - GPT-4o-mini for cost efficiency
        - Management-focused guidance
        - Specific article citations
        """)
    
    # Main interface
    if not st.session_state.agreements_loaded:
        st.info("👆 Please load the collective agreement files in the sidebar to begin.")
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
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing complete agreements and generating response..."):
                response = generate_response(
                    prompt, 
                    st.session_state.local_agreement, 
                    st.session_state.common_agreement, 
                    agreement_scope,
                    api_key
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick start questions based on scope
    if len(st.session_state.messages) == 0:
        st.markdown("### 🚀 Quick Start Questions")
        
        if agreement_scope in ["Both Agreements (Complete Analysis)", "Local Agreement Only"]:
            st.markdown("**Local Agreement Questions:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 Faculty Workload Limits"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What are the specific contact hour and class size limits for different programs? What authority does management have in workload assignment?"
                    })
                    st.rerun()
                    
                if st.button("💰 Salary Scale Authority"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What control does management have over instructor salary placement and progression? Include specific rules and management rights."
                    })
                    st.rerun()
            
            with col2:
                if st.button("📚 Professional Development Control"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What authority does management have over professional development funding and approval? What are the requirements and limitations?"
                    })
                    st.rerun()
                    
                if st.button("🏫 Program Coordination Authority"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What are management's rights in appointing and managing program coordinators? Include workload reduction and evaluation authority."
                    })
                    st.rerun()
        
        if agreement_scope in ["Both Agreements (Complete Analysis)", "Common Agreement Only"]:
            st.markdown("**Common Agreement Questions:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("⚖️ Discipline & Dismissal Rights"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What are management's rights regarding employee discipline and dismissal? Include burden of proof and procedural protections for management."
                    })
                    st.rerun()
                    
                if st.button("📅 Grievance Time Limits"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What time limits and procedural requirements protect management in grievance situations? Include deadlines and defenses."
                    })
                    st.rerun()
            
            with col2:
                if st.button("🔄 Layoff Authority"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What authority does management have in layoff situations? What are the specific procedures and management rights?"
                    })
                    st.rerun()
                    
                if st.button("📊 Job Security Provisions"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What flexibility does management have regarding job security, contracting out, and workforce management?"
                    })
                    st.rerun()

if __name__ == "__main__":
    main()
