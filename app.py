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

Remember: You are not a neutral arbitrator. You are MANAGEMENT'S advisor. Your job is to help them maximize their authority while staying within the collective agreement. Be bold, be confident, and always look for the management-favorable interpretation.

IMPORTANT: You have access to COMPLETE agreement content. The agreements contain extensive detailed provisions. When you reference articles, sections, or clauses, you should be able to find the specific content and quote it directly."""

    return system_prompt

def create_comprehensive_context(collective_agreement, common_agreement):
    """Create comprehensive context with full agreement structure and key content"""
    
    # Extract metadata
    collective_metadata = collective_agreement.get('agreement_metadata', {})
    common_metadata = common_agreement.get('agreement_metadata', {})
    
    collective_title = collective_metadata.get('title', 'Local Collective Agreement')
    common_title = common_metadata.get('title', 'Common Agreement')
    
    context = f"""
COMPLETE COLLECTIVE AGREEMENTS LOADED:

=== LOCAL AGREEMENT ===
Title: {collective_title}
Effective: {collective_metadata.get('effective_dates', {}).get('start', 'N/A')} to {collective_metadata.get('effective_dates', {}).get('end', 'N/A')}

DEFINITIONS:
{json.dumps(collective_agreement.get('definitions', {}), indent=2)}

ARTICLE STRUCTURE:
"""
    
    # Add all articles with their structure
    local_articles = collective_agreement.get('articles', {})
    for article_num in sorted(local_articles.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        article_data = local_articles[article_num]
        if isinstance(article_data, dict):
            title = article_data.get('title', 'No Title')
            context += f"Article {article_num}: {title}\n"
            
            # Add sections structure
            sections = article_data.get('sections', {})
            if sections:
                for section_key, section_data in sections.items():
                    if isinstance(section_data, dict):
                        section_title = section_data.get('title', '')
                        context += f"  - {section_key}: {section_title}\n"

    context += f"""

=== COMMON AGREEMENT ===
Title: {common_title}
Effective: {common_metadata.get('effective_dates', {}).get('start', 'N/A')} to {common_metadata.get('effective_dates', {}).get('end', 'N/A')}

DEFINITIONS:
{json.dumps(common_agreement.get('definitions', {}), indent=2)}

ARTICLE STRUCTURE:
"""
    
    # Add common agreement articles
    common_articles = common_agreement.get('articles', {})
    for article_num in sorted(common_articles.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        article_data = common_articles[article_num]
        if isinstance(article_data, dict):
            title = article_data.get('title', 'No Title')
            context += f"Article {article_num}: {title}\n"
            
            # Add sections structure
            sections = article_data.get('sections', {})
            if sections:
                for section_key, section_data in sections.items():
                    if isinstance(section_data, dict):
                        section_title = section_data.get('title', '')
                        context += f"  - {section_key}: {section_title}\n"

    context += """

CRITICAL INSTRUCTION: The complete content of all articles is available to you. When you reference any article, section, or clause, you can access the full detailed content including:
- Exact text of provisions
- Subsections and detailed requirements
- Specific procedures and time limits
- Definitions and interpretations
- Appendices and schedules

You MUST provide specific citations and quotes from the actual agreement text to support your management-focused advice."""

    return context

def get_article_content(article_ref, collective_agreement, common_agreement):
    """Retrieve specific article content for detailed analysis"""
    
    # Parse article reference (e.g., "Local-10", "Common-6.5")
    try:
        if article_ref.startswith('Local'):
            agreement = collective_agreement
            agreement_name = "Local Agreement"
        elif article_ref.startswith('Common'):
            agreement = common_agreement
            agreement_name = "Common Agreement"
        else:
            return None
            
        article_num = article_ref.split('-')[1]
        articles = agreement.get('articles', {})
        
        if article_num in articles:
            article_data = articles[article_num]
            return {
                'agreement': agreement_name,
                'article': article_num,
                'title': article_data.get('title', ''),
                'content': article_data
            }
    except:
        pass
    
    return None

def make_multiple_api_calls(user_message, collective_agreement, common_agreement, api_key):
    """Make multiple smaller API calls to handle large content"""
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # First call: Get initial analysis and identify needed articles
        initial_prompt = f"""Based on this question: "{user_message}"

Which specific articles from the Local Agreement (2019-2022) and Common Agreement (2022-2025) should I examine to provide comprehensive management-focused advice?

Available Local Agreement Articles (1-35):
{', '.join([f"Article {num}: {data.get('title', '')}" for num, data in collective_agreement.get('articles', {}).items()])}

Available Common Agreement Articles:
{', '.join([f"Article {num}: {data.get('title', '')}" for num, data in common_agreement.get('articles', {}).items()])}

Respond with ONLY a list of specific article numbers in this format:
Local: [article numbers]
Common: [article numbers]"""

        response1 = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": initial_prompt}],
            max_tokens=300,
            temperature=0.1
        )
        
        # Parse the response to get article numbers
        article_response = response1.choices[0].message.content
        
        # Second call: Get detailed response with specific articles
        system_prompt = create_system_prompt(collective_agreement, common_agreement)
        comprehensive_context = create_comprehensive_context(collective_agreement, common_agreement)
        
        # Add specific article content based on first response
        detailed_content = "\n\nDETAILED ARTICLE CONTENT:\n"
        
        # Extract mentioned articles and add their full content
        if "Local:" in article_response:
            local_articles_mentioned = re.findall(r'Local:.*?(\d+(?:,\s*\d+)*)', article_response)
            if local_articles_mentioned:
                for article_num in local_articles_mentioned[0].split(','):
                    article_num = article_num.strip()
                    if article_num in collective_agreement.get('articles', {}):
                        article_data = collective_agreement['articles'][article_num]
                        detailed_content += f"\n=== LOCAL AGREEMENT - ARTICLE {article_num}: {article_data.get('title', '')} ===\n"
                        detailed_content += json.dumps(article_data, indent=2)[:4000] + "\n"
        
        if "Common:" in article_response:
            common_articles_mentioned = re.findall(r'Common:.*?(\d+(?:,\s*\d+)*)', article_response)
            if common_articles_mentioned:
                for article_num in common_articles_mentioned[0].split(','):
                    article_num = article_num.strip()
                    if article_num in common_agreement.get('articles', {}):
                        article_data = common_agreement['articles'][article_num]
                        detailed_content += f"\n=== COMMON AGREEMENT - ARTICLE {article_num}: {article_data.get('title', '')} ===\n"
                        detailed_content += json.dumps(article_data, indent=2)[:4000] + "\n"
        
        # Final response with all context
        final_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": comprehensive_context + detailed_content + f"\n\nBased on the complete agreement content above, provide strong management-focused advice for this question: {user_message}"}
        ]
        
        # Add recent conversation history
        recent_messages = st.session_state.messages[-6:] if len(st.session_state.messages) > 6 else st.session_state.messages
        for msg in recent_messages:
            final_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response2 = client.chat.completions.create(
            model="gpt-4",
            messages=final_messages,
            max_tokens=1500,
            temperature=0.3
        )
        
        return response2.choices[0].message.content
        
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def get_ai_response(user_message, collective_agreement, common_agreement, api_key):
    """Get response using multiple API calls approach"""
    return make_multiple_api_calls(user_message, collective_agreement, common_agreement, api_key)

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
        **Complete Access**: All agreement content available via multi-stage analysis
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
                st.success("✅ Complete collective agreements loaded successfully!")
                
                # Show ACCURATE stats about loaded content
                local_articles = collective_agreement.get('articles', {})
                common_articles = common_agreement.get('articles', {})
                local_count = len(local_articles)
                common_count = len(common_articles)
                
                # Show article ranges
                local_nums = sorted([int(num) for num in local_articles.keys() if num.isdigit()])
                common_nums = sorted([int(num) for num in common_articles.keys() if num.isdigit()])
                
                st.info(f"📊 Loaded: {local_count} Local Agreement articles (Articles {min(local_nums)}-{max(local_nums)}), {common_count} Common Agreement articles")
                
                # Show definitions count
                local_defs = len(collective_agreement.get('definitions', {}))
                common_defs = len(common_agreement.get('definitions', {}))
                st.info(f"📚 Definitions: {local_defs} Local Agreement definitions, {common_defs} Common Agreement definitions")
                
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
            with st.spinner("Analyzing complete agreements (multi-stage analysis)..."):
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
                    "content": "What are management's rights regarding employee discipline and dismissal? Include specific citations and quotes from the agreements."
                })
                st.rerun()
                
            if st.button("Layoff Procedures"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What authority does management have in layoff situations? Provide specific provisions and management protections."
                })
                st.rerun()
        
        with col2:
            if st.button("Grievance Process"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are the time limits and procedures for grievances that protect management? Include specific deadlines and procedural requirements."
                })
                st.rerun()
                
            if st.button("Workload Management"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What flexibility does management have in assigning instructor workloads? Include specific provisions from both agreements."
                })
                st.rerun()

if __name__ == "__main__":
    main()
