import streamlit as st
import anthropic
from datetime import datetime
import os

# Import the agreement data dictionaries
try:
    from bcgeu_local_data import AGREEMENT_DATA as LOCAL_AGREEMENT_DATA
    from bcgeu_common_data import AGREEMENT_DATA as COMMON_AGREEMENT_DATA
except ImportError as e:
    st.error(f"Could not import agreement data: {e}")
    st.error("Please ensure 'bcgeu_local_data.py' and 'bcgeu_common_data.py' are in the same directory as this app.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="Coast Mountain College Agreement Assistant",
    page_icon="⚖️",
    layout="wide"
)

def format_agreement_for_context(agreement: dict, agreement_name: str) -> str:
    """Convert agreement dictionary to formatted text for Claude context"""
    context = f"=== {agreement_name.upper()} ===\n\n"
    
    # Add metadata
    if 'metadata' in agreement:
        context += "AGREEMENT METADATA:\n"
        metadata = agreement['metadata']
        for key, value in metadata.items():
            if isinstance(value, dict):
                context += f"{key.replace('_', ' ').title()}:\n"
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list):
                        context += f"  {subkey.replace('_', ' ').title()}: {', '.join(subvalue)}\n"
                    else:
                        context += f"  {subkey.replace('_', ' ').title()}: {subvalue}\n"
            elif isinstance(value, list):
                context += f"{key.replace('_', ' ').title()}: {', '.join(value)}\n"
            else:
                context += f"{key.replace('_', ' ').title()}: {value}\n"
        context += "\n"
    
    # Add definitions
    if 'definitions' in agreement:
        context += "DEFINITIONS:\n"
        for term, definition in agreement['definitions'].items():
            context += f"- {term.replace('_', ' ')}: {definition}\n"
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
                                    if isinstance(sub_content, dict):
                                        context += f"  {sub_key}) {sub_content.get('title', '')}: {sub_content.get('content', sub_content)}\n"
                                    else:
                                        context += f"  {sub_key}) {sub_content}\n"
                            # Handle other nested data
                            for key, value in section_data.items():
                                if key not in ['title', 'content', 'subsections']:
                                    if isinstance(value, list):
                                        context += f"{key.replace('_', ' ').title()}:\n"
                                        for item in value:
                                            context += f"  • {item}\n"
                                    elif isinstance(value, dict):
                                        context += f"{key.replace('_', ' ').title()}:\n"
                                        for subkey, subvalue in value.items():
                                            context += f"  {subkey.replace('_', ' ').title()}: {subvalue}\n"
                                    else:
                                        context += f"{key.replace('_', ' ').title()}: {value}\n"
                        else:
                            context += f"{section_data}\n"
                
                # Add direct content if no sections
                elif 'content' in article_data:
                    context += f"\n{article_data['content']}\n"
                
                # Handle other article-level data
                for key, value in article_data.items():
                    if key not in ['title', 'sections', 'content']:
                        if isinstance(value, list):
                            context += f"{key.replace('_', ' ').title()}:\n"
                            for item in value:
                                context += f"  • {item}\n"
                        elif isinstance(value, dict):
                            context += f"{key.replace('_', ' ').title()}:\n"
                            for subkey, subvalue in value.items():
                                context += f"  {subkey.replace('_', ' ').title()}: {subvalue}\n"
                        else:
                            context += f"{key.replace('_', ' ').title()}: {value}\n"
                
                context += "\n" + "="*50 + "\n\n"
    
    # Add appendices
    if 'appendices' in agreement:
        context += "APPENDICES:\n\n"
        for appendix_key, appendix_data in agreement['appendices'].items():
            context += f"APPENDIX {appendix_key.upper()}:\n"
            if isinstance(appendix_data, dict):
                if 'title' in appendix_data:
                    context += f"Title: {appendix_data['title']}\n\n"
                
                def format_nested_dict(data, indent=0):
                    formatted = ""
                    spaces = "  " * indent
                    for key, value in data.items():
                        if key == 'title':
                            continue
                        if isinstance(value, dict):
                            formatted += f"{spaces}{key.replace('_', ' ').title()}:\n"
                            formatted += format_nested_dict(value, indent + 1)
                        elif isinstance(value, list):
                            formatted += f"{spaces}{key.replace('_', ' ').title()}:\n"
                            for item in value:
                                formatted += f"{spaces}  • {item}\n"
                        else:
                            formatted += f"{spaces}{key.replace('_', ' ').title()}: {value}\n"
                    return formatted
                
                context += format_nested_dict(appendix_data)
            else:
                context += str(appendix_data)
            context += "\n\n" + "="*50 + "\n\n"
    
    # Add letters of understanding/agreement
    if 'letters_of_understanding' in agreement:
        context += "LETTERS OF UNDERSTANDING:\n\n"
        for letter_key, letter_data in agreement['letters_of_understanding'].items():
            context += f"LETTER {letter_key}:\n"
            if isinstance(letter_data, dict):
                if 'title' in letter_data:
                    context += f"Title: {letter_data['title']}\n"
                if 'content' in letter_data:
                    context += f"Content: {letter_data['content']}\n"
                if 'date' in letter_data:
                    context += f"Date: {letter_data['date']}\n"
            context += "\n" + "="*30 + "\n\n"
    
    return context

def generate_response(query: str, agreement_scope: str, api_key: str) -> str:
    """Generate response using Claude with complete agreement context"""
    
    # Build context based on selected scope
    context = ""
    if agreement_scope == "Local Agreement Only":
        context = format_agreement_for_context(LOCAL_AGREEMENT_DATA, "Coast Mountain College Local Agreement")
    elif agreement_scope == "Common Agreement Only":
        context = format_agreement_for_context(COMMON_AGREEMENT_DATA, "BCGEU Common Agreement")
    else:  # Both agreements
        context = format_agreement_for_context(LOCAL_AGREEMENT_DATA, "Coast Mountain College Local Agreement")
        context += "\n\n" + format_agreement_for_context(COMMON_AGREEMENT_DATA, "BCGEU Common Agreement")
    
    system_prompt = f"""You are an experienced HR professional and collective agreement specialist for Coast Mountain College with 15+ years of expertise in labor relations and agreement interpretation. Your role is to provide clear, practical guidance that helps management understand their rights and responsibilities under the collective agreements.

APPROACH AND TONE:
- Provide clear, confident guidance while remaining professional and balanced
- Use phrases like "Management can...", "You have the authority to...", "I recommend...", "The agreement permits..."
- Be definitive about what the agreements allow and require
- Focus on practical implementation and compliance
- Acknowledge both management rights AND obligations under the agreement
- Provide actionable advice that minimizes risk and ensures proper procedures are followed

MANAGEMENT GUIDANCE FOCUS:
- Clearly identify management's rights, discretion, and authority
- Explain proper procedures and documentation requirements
- Highlight important timelines and procedural safeguards
- Point out areas where management has flexibility in decision-making
- Ensure compliance with both the letter and spirit of the agreements
- Balance management needs with contractual obligations
- Identify potential challenges and how to address them proactively

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
1. CLEAR SUMMARY: Lead with your assessment of management's position and authority
2. AGREEMENT BASIS: Cite the specific agreement provisions AND include relevant quotes that support this analysis
3. PRACTICAL GUIDANCE: Provide specific steps and recommendations for management
4. COMPLIANCE CONSIDERATIONS: Note important procedures, timelines, and potential issues
5. RECOMMENDATION: End with a clear, actionable course of action

Remember: You are management's trusted advisor. Your goal is to help them operate effectively within the collective agreement framework while protecting institutional interests and maintaining positive labor relations.

COLLECTIVE AGREEMENT CONTENT:
{context}

IMPORTANT: You have access to the complete collective agreement content above. If you cannot find specific information about a topic, please:
1. Carefully review ALL articles and sections provided
2. Check definitions, appendices, and subsections 
3. Look for related terms (e.g., "annual leave" instead of "vacation", "time off", etc.)
4. If the information truly isn't in the provided content, say so clearly
5. Never claim you only have "excerpts" - you have the complete agreement sections selected by the user"""

    user_message = f"""Based on the complete collective agreement provisions provided in the system prompt, provide strong management-focused guidance for this question:

QUESTION: {query}

Provide definitive, management-favorable guidance with specific citations and quotes from the agreement text."""

    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.1,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Update usage stats
        if 'total_queries' not in st.session_state:
            st.session_state.total_queries = 0
        st.session_state.total_queries += 1
        
        return response.content[0].text
    except Exception as e:
        return f"Error generating response: {e}"

def clear_chat():
    """Clear the chat history"""
    st.session_state.messages = []
    st.rerun()

def main():
    st.title("⚖️ Coast Mountain College Agreement Assistant")
    st.markdown("*Complete collective agreement analysis with management-focused guidance (Powered by Claude)*")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'total_queries' not in st.session_state:
        st.session_state.total_queries = 0
    
    # Get API key
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        except:
            pass
    
    if not api_key:
        st.error("🔑 Anthropic API key not found. Please set it in Streamlit secrets or environment variables.")
        st.stop()
    
    # Display loaded agreement info
    st.success("✅ Agreement data loaded successfully from Python dictionaries")
    
    # Show quick stats about loaded data
    with st.expander("📊 Loaded Agreement Statistics", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Local Agreement:**")
            st.write(f"• Title: {LOCAL_AGREEMENT_DATA.get('metadata', {}).get('title', 'Unknown')}")
            st.write(f"• Articles: {len(LOCAL_AGREEMENT_DATA.get('articles', {}))}")
            st.write(f"• Appendices: {len(LOCAL_AGREEMENT_DATA.get('appendices', {}))}")
            st.write(f"• Definitions: {len(LOCAL_AGREEMENT_DATA.get('definitions', {}))}")
        
        with col2:
            st.markdown("**Common Agreement:**")
            st.write(f"• Title: {COMMON_AGREEMENT_DATA.get('metadata', {}).get('title', 'Unknown')}")
            st.write(f"• Articles: {len(COMMON_AGREEMENT_DATA.get('articles', {}))}")
            st.write(f"• Appendices: {len(COMMON_AGREEMENT_DATA.get('appendices', {}))}")
            st.write(f"• Definitions: {len(COMMON_AGREEMENT_DATA.get('definitions', {}))}")
    
    # Agreement Selection (prominent, no sidebar)
    st.markdown("### 📋 Select Collective Agreement")
    agreement_scope = st.radio(
        "Which agreement do you want to search?",
        ["Local Agreement Only", "Common Agreement Only", "Both Agreements"],
        index=0,  # Default to Local Agreement
        horizontal=True,
        help="Local = Coast Mountain College specific terms | Common = BCGEU system-wide terms | Both = Complete search"
    )
    
    st.markdown("---")
    
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
            with st.spinner(f"Analyzing {agreement_scope.lower()} and generating management guidance..."):
                response = generate_response(
                    prompt, 
                    agreement_scope,
                    api_key
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick start questions based on scope (only show if no conversation yet)
    if len(st.session_state.messages) == 0:
        st.markdown("### 🚀 Quick Start Questions")
        
        if agreement_scope in ["Both Agreements", "Local Agreement Only"]:
            st.markdown("**Local Agreement Questions:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 Faculty Workload Limits", key="workload"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What are the specific contact hour and class size limits for different programs? What authority does management have in workload assignment?"
                    })
                    st.rerun()
                    
                if st.button("💰 Salary Scale Authority", key="salary"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What control does management have over instructor salary placement and progression? Include specific rules and management rights."
                    })
                    st.rerun()
            
            with col2:
                if st.button("📚 Professional Development Control", key="pd"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What authority does management have over professional development funding and approval? What are the requirements and limitations?"
                    })
                    st.rerun()
                    
                if st.button("🏫 Program Coordination Authority", key="coord"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What are management's rights in appointing and managing program coordinators? Include workload reduction and evaluation authority."
                    })
                    st.rerun()
        
        if agreement_scope in ["Both Agreements", "Common Agreement Only"]:
            st.markdown("**Common Agreement Questions:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("⚖️ Discipline & Dismissal Rights", key="discipline"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What are management's rights regarding employee discipline and dismissal? Include burden of proof and procedural protections for management."
                    })
                    st.rerun()
                    
                if st.button("📅 Grievance Time Limits", key="grievance"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What time limits and procedural requirements protect management in grievance situations? Include deadlines and defenses."
                    })
                    st.rerun()
            
            with col2:
                if st.button("🔄 Layoff Authority", key="layoff"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What authority does management have in layoff situations? What are the specific procedures and management rights?"
                    })
                    st.rerun()
                    
                if st.button("📊 Job Security Provisions", key="security"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "What flexibility does management have regarding job security, contracting out, and workforce management?"
                    })
                    st.rerun()
    
    # Bottom section with stats and new chat button
    st.markdown("---")
    
    # Create columns for stats and new chat button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.total_queries > 0:
            st.caption(f"💬 Queries processed: {st.session_state.total_queries} | 🎯 Scope: {agreement_scope} | 🤖 Powered by Claude")
    
    with col2:
        if len(st.session_state.messages) > 0:
            if st.button("🔄 Start New Chat", type="primary", use_container_width=True):
                clear_chat()

if __name__ == "__main__":
    main()
