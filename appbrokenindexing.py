import streamlit as st
import json
import openai
from datetime import datetime
import re
import os

# Try to import fuzzywuzzy, fall back to difflib if not available
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    from difflib import SequenceMatcher
    FUZZYWUZZY_AVAILABLE = False
    st.warning("⚠️ FuzzyWuzzy not available. Using built-in matching (less accurate). Install with: pip install fuzzywuzzy[speedup]")

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

def similarity_ratio(a, b):
    """Calculate similarity ratio between two strings"""
    if FUZZYWUZZY_AVAILABLE:
        return fuzz.ratio(a, b)
    else:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def partial_ratio(a, b):
    """Calculate partial similarity ratio between two strings"""
    if FUZZYWUZZY_AVAILABLE:
        return fuzz.partial_ratio(a, b)
    else:
        a, b = a.lower(), b.lower()
        if len(a) <= len(b):
            shorter, longer = a, b
        else:
            shorter, longer = b, a
        
        best_ratio = 0
        for i in range(len(longer) - len(shorter) + 1):
            substring = longer[i:i + len(shorter)]
            ratio = SequenceMatcher(None, shorter, substring).ratio() * 100
            best_ratio = max(best_ratio, ratio)
        
        return best_ratio

def load_agreements():
    """Load the collective agreements from JSON files"""
    try:
        # Try to read the files
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            collective_agreement = json.load(f)
        
        with open('complete_common.json', 'r', encoding='utf-8') as f:
            common_agreement = json.load(f)
        
        return collective_agreement, common_agreement
        
    except FileNotFoundError as e:
        st.error(f"Could not find agreement files: {str(e)}")
        
        # Show file uploader as alternative
        st.markdown("### Upload Agreement Files")
        col1, col2 = st.columns(2)
        
        with col1:
            local_file = st.file_uploader("Upload complete_local.json", type="json", key="local")
        with col2:
            common_file = st.file_uploader("Upload complete_common.json", type="json", key="common")
        
        if local_file and common_file:
            try:
                collective_agreement = json.load(local_file)
                common_agreement = json.load(common_file)
                return collective_agreement, common_agreement
            except Exception as e:
                st.error(f"Error loading uploaded files: {str(e)}")
                return None, None
        
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

def build_comprehensive_index(agreement, agreement_type):
    """Build a comprehensive searchable index with detailed content mapping"""
    index = {}
    
    if 'articles' not in agreement:
        return index
    
    articles = agreement['articles']
    
    for article_num, article_data in articles.items():
        if isinstance(article_data, dict):
            title = article_data.get('title', '').lower()
            
            # Collect all content hierarchically
            content_hierarchy = {
                'title': title,
                'main_content': '',
                'sections': {},
                'all_text': [],
                'keywords': set()
            }
            
            # Add title to searchable text
            content_hierarchy['all_text'].append(title)
            
            # Extract main article content
            if 'content' in article_data:
                main_content = str(article_data['content']).lower()
                content_hierarchy['main_content'] = main_content
                content_hierarchy['all_text'].append(main_content)
            elif 'text' in article_data:
                main_content = str(article_data['text']).lower()
                content_hierarchy['main_content'] = main_content
                content_hierarchy['all_text'].append(main_content)
            
            # Process sections
            if 'sections' in article_data and isinstance(article_data['sections'], dict):
                for section_num, section_data in article_data['sections'].items():
                    section_info = {'content': '', 'subsections': {}}
                    
                    if isinstance(section_data, dict):
                        # Section title
                        if 'title' in section_data:
                            section_title = str(section_data['title']).lower()
                            content_hierarchy['all_text'].append(section_title)
                            section_info['title'] = section_title
                        
                        # Section content
                        if 'content' in section_data:
                            section_content = str(section_data['content']).lower()
                            content_hierarchy['all_text'].append(section_content)
                            section_info['content'] = section_content
                        elif 'text' in section_data:
                            section_content = str(section_data['text']).lower()
                            content_hierarchy['all_text'].append(section_content)
                            section_info['content'] = section_content
                        
                        # Process subsections
                        if 'subsections' in section_data and isinstance(section_data['subsections'], dict):
                            for sub_num, sub_data in section_data['subsections'].items():
                                if isinstance(sub_data, dict):
                                    if 'title' in sub_data:
                                        content_hierarchy['all_text'].append(str(sub_data['title']).lower())
                                    if 'content' in sub_data:
                                        content_hierarchy['all_text'].append(str(sub_data['content']).lower())
                                    elif 'text' in sub_data:
                                        content_hierarchy['all_text'].append(str(sub_data['text']).lower())
                                elif isinstance(sub_data, str):
                                    content_hierarchy['all_text'].append(sub_data.lower())
                    elif isinstance(section_data, str):
                        content_hierarchy['all_text'].append(section_data.lower())
                        section_info['content'] = section_data.lower()
                    
                    content_hierarchy['sections'][section_num] = section_info
            
            # ALSO process direct subsections at article level (for cases like 17.8)
            if 'subsections' in article_data and isinstance(article_data['subsections'], dict):
                for sub_num, sub_data in article_data['subsections'].items():
                    if isinstance(sub_data, dict):
                        if 'title' in sub_data:
                            content_hierarchy['all_text'].append(str(sub_data['title']).lower())
                        if 'content' in sub_data:
                            content_hierarchy['all_text'].append(str(sub_data['content']).lower())
                        elif 'text' in sub_data:
                            content_hierarchy['all_text'].append(str(sub_data['text']).lower())
                    elif isinstance(sub_data, str):
                        content_hierarchy['all_text'].append(sub_data.lower())
            
            # Extract keywords from all content
            all_content = ' '.join(content_hierarchy['all_text'])
            
            # Generate keywords from content
            keywords = set()
            # Common workplace terms
            workplace_terms = ['discipline', 'dismissal', 'grievance', 'layoff', 'recall', 'seniority', 
                             'workload', 'vacation', 'leave', 'sick', 'benefits', 'salary', 'overtime',
                             'holiday', 'evaluation', 'harassment', 'union', 'safety', 'pension',
                             'probation', 'termination', 'suspension', 'arbitration', 'hours',
                             'steward', 'representative', 'collective bargaining', 'just cause',
                             'burden of proof', 'time limit', 'notice', 'appeal', 'classification',
                             'regularization', 'contracting out', 'job security', 'technological change']
            
            for term in workplace_terms:
                if term in all_content:
                    keywords.add(term)
            
            content_hierarchy['keywords'] = keywords
            content_hierarchy['full_content'] = all_content
            content_hierarchy['agreement_type'] = agreement_type
            
            index[article_num] = content_hierarchy
    
    return index

def calculate_article_relevance(user_message, article_info, article_num):
    """Calculate relevance score for an article based on multiple factors"""
    user_message_lower = user_message.lower()
    search_terms = [term for term in user_message_lower.split() if len(term) > 2]
    
    score = 0
    matching_factors = []
    
    # Direct article number reference (highest priority)
    if f"article {article_num}" in user_message_lower or f"article{article_num}" in user_message_lower:
        score += 100
        matching_factors.append(f"Direct article reference: {article_num}")
    
    # Title matching (high priority)
    title_score = 0
    for term in search_terms:
        if term in article_info['title']:
            title_score += 15
            matching_factors.append(f"Title match: {term}")
        elif partial_ratio(term, article_info['title']) > 80:
            title_score += 10
            matching_factors.append(f"Similar title match: {term}")
    score += title_score
    
    # Keyword matching (medium-high priority)
    keyword_score = 0
    for keyword in article_info['keywords']:
        for term in search_terms:
            if keyword == term:
                keyword_score += 12
                matching_factors.append(f"Exact keyword: {keyword}")
            elif similarity_ratio(keyword, term) > 85:
                keyword_score += 8
                matching_factors.append(f"Similar keyword: {keyword}")
    score += keyword_score
    
    # Content frequency (medium priority)
    content_score = 0
    for term in search_terms:
        frequency = article_info['full_content'].count(term)
        if frequency > 0:
            content_score += min(frequency * 3, 15)  # Cap at 15 to prevent single-term dominance
            matching_factors.append(f"Content frequency for '{term}': {frequency}")
    score += content_score
    
    # Semantic relationships (lower priority but important for comprehensive coverage)
    semantic_bonus = 0
    semantic_relationships = {
        'discipline': ['misconduct', 'performance', 'termination', 'suspension', 'dismissal', 'just cause', 'burden'],
        'grievance': ['complaint', 'dispute', 'arbitration', 'resolution', 'appeal', 'steward'],
        'layoff': ['reduction', 'downsizing', 'redundancy', 'restructuring', 'job security'],
        'leave': ['vacation', 'absence', 'time off', 'holiday', 'sick', 'bereavement'],
        'salary': ['wage', 'pay', 'compensation', 'remuneration', 'increment'],
        'workload': ['hours', 'schedule', 'assignment', 'teaching load', 'contact hours'],
        'benefits': ['health', 'dental', 'insurance', 'pension', 'welfare'],
        'evaluation': ['appraisal', 'review', 'assessment', 'performance', 'probation'],
        'union': ['steward', 'representative', 'collective bargaining', 'dues', 'recognition'],
        'safety': ['health', 'hazard', 'injury', 'workplace', 'occupational'],
        'probation': ['trial period', 'initial employment', 'temporary', 'new employee'],
        'harassment': ['discrimination', 'sexual', 'personal', 'workplace', 'complaint'],
        'seniority': ['length of service', 'continuous service', 'recall', 'bumping'],
        'overtime': ['extra hours', 'time and half', 'callout', 'premium'],
        'technological': ['change', 'automation', 'equipment', 'methods']
    }
    
    for main_term, related_terms in semantic_relationships.items():
        if main_term in article_info['keywords']:
            for term in search_terms:
                if term in related_terms:
                    semantic_bonus += 5
                    matching_factors.append(f"Semantic relationship: {term} -> {main_term}")
    score += semantic_bonus
    
    # Boost score for articles that contain multiple search terms
    terms_found = sum(1 for term in search_terms if term in article_info['full_content'])
    if terms_found > 1:
        score += terms_found * 3
        matching_factors.append(f"Multiple terms found: {terms_found}")
    
    return score, matching_factors

def identify_relevant_articles_comprehensive(user_message, collective_agreement, common_agreement):
    """Comprehensive article identification that ensures balanced coverage"""
    
    # Build indexes
    local_index = build_comprehensive_index(collective_agreement, 'local')
    common_index = build_comprehensive_index(common_agreement, 'common')
    
    # Calculate scores for all articles
    article_scores = {}
    
    # First, check for direct article references in the user message
    direct_references = set()
    article_pattern = r'article\s*(\d+(?:\.\d+)?)'
    matches = re.findall(article_pattern, user_message.lower())
    direct_references.update(matches)
    
    # Also check for pattern like "17.8" without "article"
    decimal_pattern = r'\b(\d+\.\d+)\b'
    decimal_matches = re.findall(decimal_pattern, user_message)
    direct_references.update(decimal_matches)
    
    # Score local agreement articles
    for article_num, article_info in local_index.items():
        score, factors = calculate_article_relevance(user_message, article_info, article_num)
        if score > 0:
            article_scores[f"local_{article_num}"] = {
                'score': score,
                'factors': factors,
                'type': 'local',
                'num': article_num
            }
    
    # Score common agreement articles
    for article_num, article_info in common_index.items():
        score, factors = calculate_article_relevance(user_message, article_info, article_num)
        if score > 0:
            article_scores[f"common_{article_num}"] = {
                'score': score,
                'factors': factors,
                'type': 'common',
                'num': article_num
            }
    
    # Ensure directly referenced articles are included with high priority
    for ref_article in direct_references:
        # Check if this article exists in either agreement
        local_content = extract_article_content_enhanced(collective_agreement, ref_article)
        common_content = extract_article_content_enhanced(common_agreement, ref_article)
        
        if local_content.strip():
            article_scores[f"local_{ref_article}"] = {
                'score': 150,  # Very high score for direct references
                'factors': [f"Direct reference in user message: {ref_article}"],
                'type': 'local',
                'num': ref_article
            }
        
        if common_content.strip():
            article_scores[f"common_{ref_article}"] = {
                'score': 150,  # Very high score for direct references
                'factors': [f"Direct reference in user message: {ref_article}"],
                'type': 'common',
                'num': ref_article
            }
    
    # Sort by score and select balanced representation
    sorted_articles = sorted(article_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    selected_articles = set()
    local_count = 0
    common_count = 0
    max_per_agreement = 8  # Prevent one agreement from dominating
    
    # Select top articles with balanced representation
    for article_key, article_data in sorted_articles:
        if len(selected_articles) >= 15:  # Total limit
            break
            
        if article_data['type'] == 'local' and local_count < max_per_agreement:
            selected_articles.add(article_data['num'])
            local_count += 1
        elif article_data['type'] == 'common' and common_count < max_per_agreement:
            selected_articles.add(article_data['num'])
            common_count += 1
    
    # Always include essential procedural articles for context
    essential_articles = {
        'local': ['8', '9', '10'],  # Grievance, Arbitration, Discipline
        'common': ['3', '6']        # Employer/Union Relations, Job Security
    }
    
    for article_set in essential_articles.values():
        for article in article_set:
            selected_articles.add(article)
    
    # Ensure minimum coverage if we found very few relevant articles
    if len(selected_articles) < 5:
        # Add some high-scoring articles regardless of balance
        for article_key, article_data in sorted_articles[:10]:
            selected_articles.add(article_data['num'])
            if len(selected_articles) >= 8:
                break
    
    return list(selected_articles)

def extract_article_content_enhanced(agreement, article_num):
    """Enhanced article content extraction with better formatting"""
    content = ""
    
    if 'articles' not in agreement:
        return content
    
    articles = agreement['articles']
    if not isinstance(articles, dict):
        return content
    
    # Try exact match first
    article_data = None
    if article_num in articles:
        article_data = articles[article_num]
    else:
        # Try to find partial matches (e.g., "17.8" or within Article 17, Section 8)
        matching_articles = []
        
        # Direct match with dot notation
        if article_num in articles:
            matching_articles = [article_num]
        else:
            # Look for articles that start with the number
            for key in articles.keys():
                if key.startswith(article_num + '.') or key == article_num:
                    matching_articles.append(key)
            
            # If looking for something like "17.8", also check within Article 17's sections
            if '.' in article_num:
                main_article, sub_section = article_num.split('.', 1)
                if main_article in articles:
                    main_article_data = articles[main_article]
                    if isinstance(main_article_data, dict) and 'sections' in main_article_data:
                        sections = main_article_data['sections']
                        if isinstance(sections, dict):
                            # Look for the subsection
                            if sub_section in sections or f"{main_article}.{sub_section}" in sections:
                                # Extract this specific section
                                section_key = sub_section if sub_section in sections else f"{main_article}.{sub_section}"
                                section_data = sections[section_key]
                                
                                title = main_article_data.get('title', 'No Title')
                                content += f"**Article {main_article}: {title}**\n\n"
                                
                                if isinstance(section_data, dict):
                                    section_title = section_data.get('title', '')
                                    if section_title:
                                        content += f"  **{article_num}: {section_title}**\n"
                                    else:
                                        content += f"  **Section {article_num}:**\n"
                                    
                                    if 'content' in section_data:
                                        content += f"  {section_data['content']}\n\n"
                                    elif 'text' in section_data:
                                        content += f"  {section_data['text']}\n\n"
                                elif isinstance(section_data, str):
                                    content += f"  **{article_num}:** {section_data}\n\n"
                                
                                return content
        
        if matching_articles:
            article_data = articles[matching_articles[0]]
    
    if not article_data:
        return content
    
    if isinstance(article_data, dict):
        title = article_data.get('title', 'No Title')
        content += f"**Article {article_num}: {title}**\n\n"
        
        # Add article-level content
        if 'content' in article_data:
            content += f"{article_data['content']}\n\n"
        elif 'text' in article_data:
            content += f"{article_data['text']}\n\n"
        
        # Add direct subsections at article level (for cases like 17.8)
        if 'subsections' in article_data and isinstance(article_data['subsections'], dict):
            for subsection_num, subsection_data in article_data['subsections'].items():
                if isinstance(subsection_data, dict):
                    subsection_title = subsection_data.get('title', '')
                    if subsection_title:
                        content += f"  **{subsection_num}: {subsection_title}**\n"
                    else:
                        content += f"  **{subsection_num}:**\n"
                    if 'content' in subsection_data:
                        content += f"  {subsection_data['content']}\n\n"
                    elif 'text' in subsection_data:
                        content += f"  {subsection_data['text']}\n\n"
                elif isinstance(subsection_data, str):
                    content += f"  **{subsection_num}:** {subsection_data}\n\n"
        
        # Add sections with improved formatting
        if 'sections' in article_data and isinstance(article_data['sections'], dict):
            for section_num, section_data in article_data['sections'].items():
                if isinstance(section_data, dict):
                    section_title = section_data.get('title', '')
                    if section_title:
                        content += f"  **{section_num}: {section_title}**\n"
                    else:
                        content += f"  **Section {section_num}:**\n"
                    
                    if 'content' in section_data:
                        content += f"  {section_data['content']}\n\n"
                    elif 'text' in section_data:
                        content += f"  {section_data['text']}\n\n"
                    
                    # Add subsections
                    if 'subsections' in section_data and isinstance(section_data['subsections'], dict):
                        for subsection_num, subsection_data in section_data['subsections'].items():
                            if isinstance(subsection_data, dict):
                                subsection_title = subsection_data.get('title', '')
                                if subsection_title:
                                    content += f"    **{subsection_num}: {subsection_title}**\n"
                                if 'content' in subsection_data:
                                    content += f"    {subsection_data['content']}\n\n"
                                elif 'text' in subsection_data:
                                    content += f"    {subsection_data['text']}\n\n"
                            elif isinstance(subsection_data, str):
                                content += f"    **{subsection_num}:** {subsection_data}\n\n"
                elif isinstance(section_data, str):
                    content += f"  **{section_num}:** {section_data}\n\n"
    elif isinstance(article_data, str):
        content += f"**Article {article_num}:** {article_data}\n\n"
    
    return content

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
    
    system_prompt = f"""You are a senior HR expert for Coast Mountain College with 15+ years of experience in collective agreement interpretation and employee relations. Your role is to provide STRONG, DEFINITIVE guidance that maximizes management's rights and authority under the collective agreements.

You have access to two collective agreements:

1. LOCAL AGREEMENT: "{collective_title}"
   - Effective: {collective_dates.get('start', 'N/A')} to {collective_dates.get('end', 'N/A')}
   - Between: {collective_parties.get('employer', 'Coast Mountain College')} and {collective_parties.get('union', 'Faculty Union')}

2. COMMON AGREEMENT: "{common_title}" 
   - Effective: {common_dates.get('start', 'N/A')} to {common_dates.get('end', 'N/A')}
   - Between: {common_parties.get('employers', 'BC Colleges')} and {common_parties.get('union', 'Faculty Union')}

CRITICAL INSTRUCTIONS - COMPREHENSIVE ANALYSIS:
- ANALYZE ALL RELEVANT ARTICLES provided, not just one or two
- Look for COMPLEMENTARY PROVISIONS across both agreements
- Identify OVERLAPPING AUTHORITY from multiple sources
- Cross-reference RELATED ARTICLES that strengthen management's position
- Consider the INTERACTION between local and common agreement provisions

RESPONSE APPROACH - MULTI-LAYERED ANALYSIS:
1. **PRIMARY AUTHORITY**: Lead with the strongest, most direct provision
2. **SUPPORTING PROVISIONS**: Cite additional articles that reinforce your position
3. **PROCEDURAL ADVANTAGES**: Highlight process requirements that favor management
4. **RISK MITIGATION**: Address potential union arguments using multiple articles
5. **TACTICAL SYNTHESIS**: Combine provisions from both agreements for maximum effect

MANAGEMENT AUTHORITY FOCUS:
- ALWAYS lead with what management CAN do, not what they can't
- Emphasize "just cause" standards work in management's favor when properly documented
- Highlight burden of proof requirements that protect the employer
- Point out procedural safeguards and time limits that benefit management
- Identify areas of management discretion and flexibility
- Frame employee rights as limited by management's legitimate business needs
- Show how MULTIPLE articles work together to support management authority

CITATION REQUIREMENTS (MANDATORY):
- CITE MULTIPLE RELEVANT ARTICLES, not just one
- Use format: [Agreement Type - Article X.X: Title]
- Example: [Local Agreement - Article 10.1: Burden of Proof] AND [Common Agreement - Article 2.4: Findings]
- INCLUDE RELEVANT QUOTES from multiple sources when possible
- Quote format: "The local agreement states: '[exact quote]' [Citation], while the common agreement reinforces this with '[exact quote]' [Citation]"
- Show how provisions WORK TOGETHER

TONE - CONFIDENT AND COMPREHENSIVE:
- "Management has MULTIPLE sources of authority here..."
- "Both agreements support your position by..."
- "You can rely on several overlapping provisions..."
- "The combination of these articles gives you..."
- "While Article X provides the primary authority, Articles Y and Z strengthen your position by..."

Remember: You are MANAGEMENT'S advisor. Analyze ALL relevant provisions to build the strongest possible case. Don't focus on just one article when multiple articles support management's position. Show how the agreements work together to maximize management authority."""

    return system_prompt

def create_balanced_context(user_message, collective_agreement, common_agreement):
    """Create comprehensive context ensuring balanced coverage of both agreements"""
    
    # Use comprehensive article identification
    relevant_articles = identify_relevant_articles_comprehensive(user_message, collective_agreement, common_agreement)
    
    # Basic metadata
    collective_metadata = collective_agreement.get('agreement_metadata', {})
    common_metadata = common_agreement.get('agreement_metadata', {})
    
    collective_title = collective_metadata.get('title', 'Local Collective Agreement')
    common_title = common_metadata.get('title', 'Common Agreement')
    
    collective_dates = collective_metadata.get('effective_dates', {})
    common_dates = common_metadata.get('effective_dates', {})
    
    collective_parties = collective_metadata.get('parties', {})
    common_parties = common_metadata.get('parties', {})
    
    context = f"""
COLLECTIVE AGREEMENTS ANALYSIS:

LOCAL AGREEMENT: "{collective_title}"
- Effective: {collective_dates.get('start', 'N/A')} to {collective_dates.get('end', 'N/A')}
- Parties: {collective_parties.get('employer', 'Coast Mountain College')} and {collective_parties.get('union', 'Faculty Union')}

COMMON AGREEMENT: "{common_title}" 
- Effective: {common_dates.get('start', 'N/A')} to {common_dates.get('end', 'N/A')}
- Parties: {common_parties.get('employers', 'BC Colleges')} and {common_parties.get('union', 'Faculty Union')}

=== RELEVANT ARTICLES FOR COMPREHENSIVE ANALYSIS ===

LOCAL AGREEMENT PROVISIONS:
"""
    
    # Separate articles by agreement type for balanced presentation
    local_articles = []
    common_articles = []
    
    for article_num in relevant_articles:
        local_content = extract_article_content_enhanced(collective_agreement, article_num)
        common_content = extract_article_content_enhanced(common_agreement, article_num)
        
        if local_content.strip():
            local_articles.append((article_num, local_content))
        if common_content.strip():
            common_articles.append((article_num, common_content))
    
    # Add local articles
    for article_num, content in local_articles:
        context += f"\n[LOCAL AGREEMENT]\n{content}\n"
    
    context += "\nCOMMON AGREEMENT PROVISIONS:\n"
    
    # Add common articles
    for article_num, content in common_articles:
        context += f"\n[COMMON AGREEMENT]\n{content}\n"
    
    # Add definitions for reference
    context += f"""

=== KEY DEFINITIONS ===

LOCAL AGREEMENT DEFINITIONS:
{json.dumps(collective_agreement.get('definitions', {}), indent=2)}

COMMON AGREEMENT DEFINITIONS:
{json.dumps(common_agreement.get('definitions', {}), indent=2)}

=== ANALYSIS INSTRUCTIONS ===

IMPORTANT FOR COMPREHENSIVE RESPONSE:
1. ANALYZE ALL articles provided above from BOTH agreements
2. Look for OVERLAPPING and COMPLEMENTARY provisions
3. Identify how LOCAL and COMMON agreement articles work TOGETHER
4. Consider PROCEDURAL requirements from multiple sources
5. Build the STRONGEST possible management position using ALL relevant provisions
6. Do NOT focus on just one article - synthesize multiple sources of authority

The articles above represent the most relevant provisions for this query. Use them comprehensively to provide robust, multi-faceted guidance that maximizes management's position under both agreements.
"""
    
    return context

def get_ai_response(user_message, collective_agreement, common_agreement, api_key):
    """Get response from OpenAI API with enhanced prompting"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        system_prompt = create_system_prompt(collective_agreement, common_agreement)
        agreement_context = create_balanced_context(user_message, collective_agreement, common_agreement)
        
        # Enhanced user message to encourage comprehensive analysis
        enhanced_user_message = f"""Query: {user_message}

Please provide a comprehensive analysis that:
1. Examines ALL relevant articles from both the Local and Common agreements
2. Shows how multiple provisions work together to support management's position
3. Identifies overlapping authority and complementary requirements
4. Addresses potential union arguments using multiple sources
5. Provides tactical guidance based on the full scope of management's rights

Focus on building the strongest possible management position using all available provisions, not just one primary article."""
        
        # Prepare messages for the API
        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + agreement_context}
        ]
        
        # Add conversation history (limit to last 6 exchanges to save tokens)
        recent_messages = st.session_state.messages[-12:] if len(st.session_state.messages) > 12 else st.session_state.messages
        for msg in recent_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add enhanced user message
        messages.append({"role": "user", "content": enhanced_user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2500,  # Increased for comprehensive responses
            temperature=0.2   # Lower temperature for more consistent analysis
        )
        
        return response.choices[0].message.content
        
    except openai.RateLimitError as e:
        return "⚠️ **Rate limit exceeded.** Please wait a moment and try again. Consider upgrading your OpenAI plan for higher limits."
    except Exception as e:
        return f"Error getting AI response: {str(e)}"

def main():
    st.title("⚖️ Collective Agreement Assistant")
    st.markdown("*Comprehensive management guidance for Coast Mountain College collective agreements*")
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("Configuration")
        
        # Try to get API key from secrets first, then environment, then user input
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
                st.success("✅ Collective agreements loaded and indexed successfully!")
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
            with st.spinner("Analyzing comprehensive agreement provisions..."):
                response = get_ai_response(
                    prompt, 
                    st.session_state.collective_agreement,
                    st.session_state.common_agreement,
                    api_key
                )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Enhanced quick question buttons
    if len(st.session_state.messages) == 0:
        st.markdown("### Quick Start Questions:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Employee Discipline Authority"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What comprehensive authority does management have for employee discipline, including procedures, burden of proof, and supporting provisions across both agreements?"
                })
                st.rerun()
                
            if st.button("⚖️ Grievance Defense Strategy"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are all the procedural defenses, time limits, and management protections available in the grievance process?"
                })
                st.rerun()
        
        with col2:
            if st.button("🔄 Layoff and Restructuring Rights"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What comprehensive authority does management have in layoff situations, including operational flexibility and employee placement?"
                })
                st.rerun()
                
            if st.button("📚 Workload Management Flexibility"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What flexibility does management have in assigning instructor workloads, schedules, and duties across all relevant provisions?"
                })
                st.rerun()

if __name__ == "__main__":
    main()
