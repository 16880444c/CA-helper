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

def search_for_relevant_content(user_message, collective_agreement, common_agreement):
    """Comprehensive search that finds relevant content by analyzing all articles and content"""
    
    relevant_articles = {}
    query_lower = user_message.lower()
    query_words = set(query_lower.split())
    
    # Extract meaningful keywords from the query (remove common words)
    stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 
                  'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with',
                  'can', 'could', 'should', 'would', 'have', 'had', 'this', 'they', 'them', 'their',
                  'what', 'when', 'where', 'how', 'why', 'who', 'which', 'does', 'do', 'did'}
    
    meaningful_keywords = query_words - stop_words
    
    def search_in_content(content, keywords):
        """Search for keywords in content recursively"""
        if isinstance(content, str):
            content_lower = content.lower()
            return any(keyword in content_lower for keyword in keywords)
        elif isinstance(content, dict):
            return any(search_in_content(value, keywords) for value in content.values())
        elif isinstance(content, list):
            return any(search_in_content(item, keywords) for item in content)
        return False
    
    def calculate_relevance_score(article_data, keywords):
        """Calculate how relevant an article is to the query"""
        score = 0
        
        # Check title relevance (higher weight)
        title = article_data.get('title', '').lower()
        for keyword in keywords:
            if keyword in title:
                score += 3
        
        # Check content relevance
        if search_in_content(article_data, keywords):
            score += 1
        
        # Boost score for exact phrase matches
        query_phrases = [query_lower]
        if len(query_lower.split()) > 1:
            # Create 2-word and 3-word phrases
            words = query_lower.split()
            for i in range(len(words) - 1):
                query_phrases.append(' '.join(words[i:i+2]))
                if i < len(words) - 2:
                    query_phrases.append(' '.join(words[i:i+3]))
        
        article_text = json.dumps(article_data, ensure_ascii=False).lower()
        for phrase in query_phrases:
            if phrase in article_text:
                score += 5
        
        return score
    
    # Search through all articles in both agreements
    article_scores = []
    
    for agreement_name, agreement in [('Local', collective_agreement), ('Common', common_agreement)]:
        articles = agreement.get('articles', {})
        for article_num, article_data in articles.items():
            if isinstance(article_data, dict):
                score = calculate_relevance_score(article_data, meaningful_keywords)
                if score > 0:
                    article_scores.append({
                        'agreement': agreement_name,
                        'article_num': article_num,
                        'article_data': article_data,
                        'score': score,
                        'title': article_data.get('title', '')
                    })
    
    # Sort by relevance score and take top articles
    article_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Include top relevant articles (at least 3, up to 8 depending on scores)
    min_articles = 3
    max_articles = 8
    
    for i, article_info in enumerate(article_scores):
        if i < min_articles or (i < max_articles and article_info['score'] >= 2):
            key = f"{article_info['agreement']} Agreement - Article {article_info['article_num']}: {article_info['title']}"
            relevant_articles[key] = article_info['article_data']
    
    # If we still don't have enough relevant content, add some key articles
    if len(relevant_articles) < 2:
        # Add employer rights and grievance procedure as they're often relevant
        for agreement_name, agreement in [('Local', collective_agreement), ('Common', common_agreement)]:
            articles = agreement.get('articles', {})
            
            # Look for employer/management rights articles
            for article_num, article_data in articles.items():
                if isinstance(article_data, dict):
                    title = article_data.get('title', '').lower()
                    if any(word in title for word in ['employer', 'management', 'rights']):
                        key = f"{agreement_name} Agreement - Article {article_num}: {article_data.get('title', '')}"
                        relevant_articles[key] = article_data
                        break
    
    # Also search appendices for relevant content
    for agreement_name, agreement in [('Local', collective_agreement), ('Common', common_agreement)]:
        appendices = agreement.get('appendices', {})
        for appendix_key, appendix_data in appendices.items():
            if isinstance(appendix_data, dict):
                score = calculate_relevance_score(appendix_data, meaningful_keywords)
                if score > 2:  # Higher threshold for appendices
                    key = f"{agreement_name} Agreement - {appendix_key}: {appendix_data.get('title', '')}"
                    relevant_articles[key] = appendix_data
    
    return relevant_articles

def make_multiple_api_calls(user_message, collective_agreement, common_agreement, api_key):
    """Make efficient API calls with proper token management"""
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Enhanced search for relevant content
        relevant_articles = search_for_relevant_content(user_message, collective_agreement, common_agreement)
        
        # Limit the number of articles to prevent token overflow
        max_articles = 3  # Start with fewer articles to stay within limits
        limited_articles = dict(list(relevant_articles.items())[:max_articles])
        
        # Create concise content from relevant articles
        detailed_content = "\n\nRELEVANT AGREEMENT PROVISIONS:\n"
        
        for article_key, article_data in limited_articles.items():
            detailed_content += f"\n=== {article_key} ===\n"
            # Create a more concise representation
            formatted_content = format_article_content_concise(article_data)
            detailed_content += formatted_content + "\n"
        
        # Include only essential definitions
        essential_definitions = get_essential_definitions(user_message, collective_agreement, common_agreement)
        if essential_definitions:
            detailed_content += f"\n\nESSENTIAL DEFINITIONS:\n{essential_definitions}\n"
        
        # Create the system prompt
        system_prompt = create_system_prompt(collective_agreement, common_agreement)
        
        # Build a more focused prompt
        full_context = f"""RELEVANT COLLECTIVE AGREEMENT CONTENT:

{detailed_content}

CRITICAL INSTRUCTIONS:
1. Analyze ONLY the specific provisions shown above
2. Provide exact citations with article and section numbers
3. Quote directly from the agreement text provided
4. Focus on management rights and specific requirements
5. Be definitive and assertive in your management-focused advice

Question: {user_message}

Provide strong management guidance based on the specific provisions above."""

        # Check approximate token count and truncate if needed
        estimated_tokens = len(full_context.split()) * 1.3  # Rough estimate
        max_context_tokens = 6000  # Leave room for response
        
        if estimated_tokens > max_context_tokens:
            # Truncate the content
            words = full_context.split()
            truncated_words = words[:int(max_context_tokens / 1.3)]
            full_context = ' '.join(truncated_words) + "\n\n[Content truncated to fit limits - analysis based on key provisions above]"
        
        # Make the API call with conservative settings
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use 3.5-turbo to stay within limits
            messages=[
                {"role": "system", "content": system_prompt[:1000]},  # Limit system prompt
                {"role": "user", "content": full_context}
            ],
            max_tokens=800,  # Conservative response length
            temperature=0.2
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def format_article_content_concise(article_data):
    """Format article content concisely to save tokens"""
    formatted = ""
    
    if 'title' in article_data:
        formatted += f"TITLE: {article_data['title']}\n"
    
    # Handle sections more efficiently
    if 'sections' in article_data:
        sections = article_data['sections']
        for section_key, section_data in sections.items():
            formatted += f"\n{section_key}. "
            if isinstance(section_data, dict):
                if 'title' in section_data:
                    formatted += f"{section_data['title']}\n"
                if 'content' in section_data:
                    content = str(section_data['content'])
                    # Limit content length
                    if len(content) > 300:
                        content = content[:300] + "..."
                    formatted += f"   {content}\n"
                # Handle subsections briefly
                if 'subsections' in section_data:
                    subsections = section_data['subsections']
                    for sub_key, sub_content in subsections.items():
                        sub_str = str(sub_content)
                        if len(sub_str) > 150:
                            sub_str = sub_str[:150] + "..."
                        formatted += f"   {sub_key}) {sub_str}\n"
            else:
                content = str(section_data)
                if len(content) > 200:
                    content = content[:200] + "..."
                formatted += f"{content}\n"
    
    # Handle other content briefly
    if 'content' in article_data and 'sections' not in article_data:
        content = str(article_data['content'])
        if len(content) > 400:
            content = content[:400] + "..."
        formatted += f"\nCONTENT: {content}\n"
    
    return formatted

def get_essential_definitions(user_message, collective_agreement, common_agreement):
    """Get only definitions relevant to the query"""
    query_lower = user_message.lower()
    essential_defs = {}
    
    # Check local definitions
    local_defs = collective_agreement.get('definitions', {})
    for term, definition in local_defs.items():
        if term.lower() in query_lower or any(word in str(definition).lower() for word in query_lower.split()):
            essential_defs[f"Local - {term}"] = definition
    
    # Check common definitions
    common_defs = common_agreement.get('definitions', {})
    for term, definition in common_defs.items():
        if term.lower() in query_lower or any(word in str(definition).lower() for word in query_lower.split()):
            essential_defs[f"Common - {term}"] = definition
    
    # Limit to most relevant
    if len(essential_defs) > 5:
        # Keep only exact matches
        exact_matches = {k: v for k, v in essential_defs.items() 
                        if any(term in k.lower() for term in query_lower.split())}
        return json.dumps(exact_matches, indent=2) if exact_matches else ""
    
    return json.dumps(essential_defs, indent=2) if essential_defs else ""

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
                
                # Show article ranges - handle both string and numeric keys
                local_keys = list(local_articles.keys())
                common_keys = list(common_articles.keys())
                
                # Debug: Show what keys we actually have
                st.write(f"**Debug - Local Article Keys Found:** {sorted(local_keys)}")
                st.write(f"**Debug - Common Article Keys Found:** {sorted(common_keys)}")
                
                local_nums = []
                common_nums = []
                
                for key in local_keys:
                    try:
                        if key.isdigit():
                            local_nums.append(int(key))
                        elif isinstance(key, str) and '.' in key:
                            local_nums.append(float(key))
                    except:
                        pass
                
                for key in common_keys:
                    try:
                        if key.isdigit():
                            common_nums.append(int(key))
                        elif isinstance(key, str) and '.' in key:
                            common_nums.append(float(key))
                    except:
                        pass
                
                if local_nums:
                    local_nums.sort()
                    st.info(f"📊 Loaded: {local_count} Local Agreement articles (Articles {min(local_nums)}-{max(local_nums)}), {common_count} Common Agreement articles")
                else:
                    st.info(f"📊 Loaded: {local_count} Local Agreement articles, {common_count} Common Agreement articles")
                
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
