import streamlit as st
import json
import anthropic
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Coast Mountain College Agreement Assistant",
    page_icon="⚖️",
    layout="wide"
)

def load_builtin_agreements() -> tuple:
    """Load the built-in agreements from JSON files"""
    try:
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            local_agreement = json.load(f)
        
        with open('complete_common.json', 'r', encoding='utf-8') as f:
            common_agreement = json.load(f)
        
        # Debug: Show what's actually in the loaded JSON
        st.write("**JSON Loading Debug:**")
        if local_agreement and 'articles' in local_agreement:
            st.write(f"**Local JSON Articles Found:** {len(local_agreement['articles'])} articles")
            st.write(f"**Local Article Keys:** {sorted(list(local_agreement['articles'].keys()))}")
            # Check if Article 17 exists
            if '17' in local_agreement['articles']:
                st.write("**Article 17 found in Local Agreement ✓**")
                # Show Article 17 title if available
                if isinstance(local_agreement['articles']['17'], dict) and 'title' in local_agreement['articles']['17']:
                    st.write(f"**Article 17 Title:** {local_agreement['articles']['17']['title']}")
            else:
                st.write("**Article 17 NOT found in Local Agreement ❌**")
        else:
            st.write("**Local Agreement has no articles section**")
            
        if common_agreement and 'articles' in common_agreement:
            st.write(f"**Common JSON Articles Found:** {len(common_agreement['articles'])} articles")
        
        return local_agreement, common_agreement
        
    except FileNotFoundError as e:
        st.error(f"JSON files not found: {str(e)}")
        st.error("Please ensure 'complete_local.json' and 'complete_common.json' are in the same directory as this app.")
        return None, None
    except Exception as e:
        st.error(f"Error loading built-in agreements: {e}")
        return None, None

def format_agreement_for_context(agreement: dict, agreement_name: str) -> str:
    """Convert agreement JSON to formatted text for Claude context"""
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
    """Generate response using Claude with complete agreement context"""
    
    # Build context based on selected scope
    context = ""
    if agreement_scope == "Local Agreement Only":
        context = format_agreement_for_context(local_agreement, "Coast Mountain College Local Agreement")
    elif agreement_scope == "Common Agreement Only":
        context = format_agreement_for_context(common_agreement, "BCGEU Common Agreement")
    else:  # Both agreements
        context = format_agreement_for_context(local_agreement, "Coast Mountain College Local Agreement")
        context += "\n\n" + format_agreement_for_context(common_agreement, "BCGEU Common Agreement")
    
    # Debug: Show what's being loaded based on scope
    st.write(f"**Debug Info:** Selected Scope: {agreement_scope}")
    st.write(f"**Context length:** {len(context)} characters")
    
    # Show which agreement(s) are being processed
    if agreement_scope == "Local Agreement Only":
        st.write("**Processing:** Local Agreement Only")
        if local_agreement and 'articles' in local_agreement:
            st.write(f"**Local Agreement Articles Available:** {list(local_agreement['articles'].keys())}")
        else:
            st.write("**ERROR:** Local agreement not loaded or has no articles")
    elif agreement_scope == "Common Agreement Only":
        st.write("**Processing:** Common Agreement Only")
        if common_agreement and 'articles' in common_agreement:
            st.write(f"**Common Agreement Articles Available:** {list(common_agreement['articles'].keys())}")
        else:
            st.write("**ERROR:** Common agreement not loaded or has no articles")
    else:  # Both agreements
        st.write("**Processing:** Both Agreements")
        if local_agreement and 'articles' in local_agreement:
            st.write(f"**Local Agreement Articles:** {list(local_agreement['articles'].keys())}")
        if common_agreement and 'articles' in common_agreement:
            st.write(f"**Common Agreement Articles:** {list(common_agreement['articles'].keys())}")
    
    # Debug: Show what context actually contains
    if "COAST MOUNTAIN COLLEGE LOCAL AGREEMENT" in context and "BCGEU COMMON AGREEMENT" in context:
        st.write("**Context Contains:** Both Local AND Common Agreement (unexpected for Local-only selection)")
    elif "COAST MOUNTAIN COLLEGE LOCAL AGREEMENT" in context:
        st.write("**Context Contains:** Local Agreement Only ✓")
    elif "BCGEU COMMON AGREEMENT" in context:
        st.write("**Context Contains:** Common Agreement Only ✓")
    else:
        st.write("**Context Contains:** Unknown content")
    
    # Debug: Show a sample of the context content
    st.write("**Context Preview (first 1000 chars):**")
    st.text(context[:1000] + "..." if len(context) > 1000 else context)
    
    # Check if vacation-related content exists
    vacation_keywords = ["vacation", "annual leave", "leave of absence", "holiday"]
    found_keywords = [kw for kw in vacation_keywords if kw.lower() in context.lower()]
    st.write(f"**Vacation-related keywords found:** {found_keywords}")
    
    # Additional debug: Check if vacation content is in a specific agreement
    if "vacation" in context.lower():
        st.write("**Vacation content found in context**")
        # Find which sections contain vacation
        vacation_lines = [line for line in context.split('\n') if 'vacation' in line.lower()]
        st.write(f"**Vacation mentions (first 5):** {vacation_lines[:5]}")
    else:
        st.write("**No vacation content found in context - this might be why Claude can't answer**")
    
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

IMPORTANT: You have access to the complete collective agreement content above. If you cannot find specific information about a topic (like vacation), please:
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
        # Load agreements when user submits question
        with st.spinner("Loading agreements..."):
            local_agreement, common_agreement = load_builtin_agreements()
            
            if not local_agreement or not common_agreement:
                st.error("❌ Could not load agreement files. Please check that the JSON files are available.")
                st.stop()
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing {agreement_scope.lower()} and generating management guidance..."):
                response = generate_response(
                    prompt, 
                    local_agreement, 
                    common_agreement, 
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
    
    # Simple stats at bottom
    if st.session_state.total_queries > 0:
        st.markdown("---")
        st.caption(f"💬 Queries processed: {st.session_state.total_queries} | 🎯 Scope: {agreement_scope} | 🤖 Powered by Claude")

if __name__ == "__main__":
    main()
