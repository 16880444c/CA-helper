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

def test_json_loading():
    """Test JSON loading to diagnose the issue"""
    st.write("🔧 JSON LOADING DIAGNOSTICS:")
    try:
        # Check file existence and size
        import os
        if os.path.exists('complete_local.json'):
            file_size = os.path.getsize('complete_local.json')
            st.write(f"- File exists, size: {file_size:,} bytes")
        else:
            st.error("❌ complete_local.json file not found!")
            return
            
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            content = f.read()
            st.write(f"- File content length: {len(content):,} characters")
            
            # Check for key sections in raw text
            if '"appendices"' in content:
                st.write("✅ Found 'appendices' key in raw file content")
                appendices_pos = content.find('"appendices"')
                st.write(f"- Appendices section starts at character {appendices_pos}")
                
                # Show content around appendices
                start = max(0, appendices_pos - 50)
                end = min(len(content), appendices_pos + 300)
                st.write("Raw content around appendices:")
                st.code(content[start:end])
            else:
                st.write("❌ No 'appendices' key found in raw file content")
            
            if '"appendix_3"' in content:
                st.write("✅ Found 'appendix_3' key in raw file content")
                appendix_3_pos = content.find('"appendix_3"')
                st.write(f"- Appendix 3 section starts at character {appendix_3_pos}")
            else:
                st.write("❌ No 'appendix_3' key found in raw file content")
            
            st.write(f"- Last 300 characters of file:")
            st.code(content[-300:])
            
            # Now try to parse JSON
            st.write("🔍 Attempting JSON parse...")
            data = json.loads(content)
            st.write(f"✅ JSON parsed successfully!")
            st.write(f"- Top level keys after JSON parse: {list(data.keys())}")
            
            if 'appendices' in data:
                st.write(f"✅ Appendices found in parsed data: {list(data['appendices'].keys())}")
                if 'appendix_3' in data['appendices']:
                    st.write("✅ Appendix 3 found in parsed JSON!")
                    st.write(f"- Appendix 3 keys: {list(data['appendices']['appendix_3'].keys())}")
                    st.write(f"- Appendix 3 title: {data['appendices']['appendix_3'].get('title', 'No title')}")
                else:
                    st.write("❌ Appendix 3 NOT found in parsed JSON")
            else:
                st.write("❌ No appendices section in parsed JSON - THIS IS THE PROBLEM!")
                
            # Check if appendices content is elsewhere
            full_text = json.dumps(data).lower()
            if "program coordination" in full_text:
                st.write("✅ 'program coordination' text found somewhere in parsed JSON")
            if "appendix 3" in full_text:
                st.write("✅ 'appendix 3' text found somewhere in parsed JSON")
                
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parsing error: {e}")
        st.write(f"Error at line {e.lineno}, column {e.colno}")
    except Exception as e:
        st.error(f"❌ File reading error: {e}")

def load_builtin_agreements() -> tuple:
    """Load the built-in agreements from JSON files"""
    st.write("🔍 LOADING AGREEMENTS...")
    
    # First run the diagnostic
    test_json_loading()
    
    try:
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            local_agreement = json.load(f)
        
        with open('complete_common.json', 'r', encoding='utf-8') as f:
            common_agreement = json.load(f)
        
        # DEBUG: Print what we loaded
        st.write("🔍 LOAD RESULTS:")
        st.write(f"- Local agreement type: {type(local_agreement)}")
        st.write(f"- Local agreement top-level keys: {list(local_agreement.keys())}")
        
        if 'appendices' in local_agreement:
            st.write(f"✅ Appendices found: {list(local_agreement['appendices'].keys())}")
            if 'appendix_3' in local_agreement['appendices']:
                st.write("✅ Appendix 3 found in local agreement!")
                st.write(f"- Appendix 3 title: {local_agreement['appendices']['appendix_3'].get('title', 'No title')}")
                st.write(f"- Appendix 3 keys: {list(local_agreement['appendices']['appendix_3'].keys())}")
            else:
                st.write("❌ Appendix 3 NOT found in local agreement")
        else:
            st.write("❌ No appendices section found in local agreement")
            
            # EXTENSIVE SEARCH for where appendix content might be hiding
            st.write("🔍 SEARCHING ENTIRE AGREEMENT for appendix content...")
            full_text = json.dumps(local_agreement, indent=2)
            
            # Find all occurrences of "appendix"
            appendix_positions = []
            search_text = full_text.lower()
            start = 0
            while True:
                pos = search_text.find("appendix", start)
                if pos == -1:
                    break
                appendix_positions.append(pos)
                start = pos + 1
            
            st.write(f"Found 'appendix' at {len(appendix_positions)} positions: {appendix_positions[:10]}...")
            
            # Show context around each appendix mention
            for i, pos in enumerate(appendix_positions[:5]):  # Show first 5
                start = max(0, pos - 100)
                end = min(len(full_text), pos + 200)
                context_snippet = full_text[start:end]
                st.write(f"**Appendix occurrence #{i+1} at position {pos}:**")
                st.code(context_snippet)
                
            # Search for "program coordination" specifically
            prog_coord_pos = search_text.find("program coordination")
            if prog_coord_pos >= 0:
                st.write(f"Found 'program coordination' at position {prog_coord_pos}")
                start = max(0, prog_coord_pos - 150)
                end = min(len(full_text), prog_coord_pos + 300)
                context_snippet = full_text[start:end]
                st.write("**Program Coordination context:**")
                st.code(context_snippet)
        
        return local_agreement, common_agreement
        
    except FileNotFoundError as e:
        st.error(f"JSON files not found: {str(e)}")
        st.error("Please ensure 'complete_local.json' and 'complete_common.json' are in the same directory as this app.")
        return None, None
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        return None, None
    except Exception as e:
        st.error(f"Error loading built-in agreements: {e}")
        return None, None

def format_agreement_for_context(agreement: dict, agreement_name: str) -> str:
    """Convert agreement JSON to formatted text for Claude context"""
    st.write(f"🔍 FORMATTING CONTEXT FOR: {agreement_name}")
    
    context = f"=== {agreement_name.upper()} ===\n\n"
    
    # Add metadata
    if 'agreement_metadata' in agreement:
        context += "AGREEMENT METADATA:\n"
        context += json.dumps(agreement['agreement_metadata'], indent=2) + "\n\n"
        st.write("✅ Added metadata")
    
    # Add definitions
    if 'definitions' in agreement:
        context += "DEFINITIONS:\n"
        for term, definition in agreement['definitions'].items():
            context += f"- {term}: {definition}\n"
        context += "\n"
        st.write(f"✅ Added {len(agreement['definitions'])} definitions")
    
    # Add articles
    if 'articles' in agreement:
        context += "ARTICLES:\n\n"
        article_count = 0
        for article_num, article_data in agreement['articles'].items():
            if isinstance(article_data, dict):
                title = article_data.get('title', f'Article {article_num}')
                context += f"ARTICLE {article_num}: {title}\n"
                article_count += 1
                
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
        
        st.write(f"✅ Added {article_count} articles")
    
    # Add appendices with extensive debug info
    if 'appendices' in agreement:
        st.write(f"🔍 PROCESSING APPENDICES...")
        context += "APPENDICES:\n\n"
        appendices = agreement['appendices']
        st.write(f"- Appendices type: {type(appendices)}")
        st.write(f"- Appendices keys: {list(appendices.keys())}")
        
        appendix_count = 0
        for appendix_key, appendix_data in appendices.items():
            st.write(f"- Processing appendix: '{appendix_key}' (type: {type(appendix_data)})")
            
            # Convert appendix_3 to "APPENDIX 3" for better readability
            display_key = appendix_key.replace('_', ' ').upper()
            context += f"{display_key}:\n"
            st.write(f"  - Display key: '{display_key}'")
            
            if isinstance(appendix_data, dict):
                if 'title' in appendix_data:
                    context += f"Title: {appendix_data['title']}\n\n"
                    st.write(f"  - Title: {appendix_data['title']}")
                
                # Add the full appendix content
                context += json.dumps(appendix_data, indent=2)
                st.write(f"  - Added {len(str(appendix_data))} characters of content")
            else:
                context += str(appendix_data)
                st.write(f"  - Added non-dict content: {type(appendix_data)}")
            
            context += "\n\n" + "="*50 + "\n\n"
            appendix_count += 1
            
            # Special debug for Appendix 3
            if appendix_key == 'appendix_3':
                st.write("✅ SUCCESS: Processed Appendix 3!")
                st.write(f"  - Final display key: '{display_key}'")
                st.write(f"  - Content preview: {str(appendix_data)[:200]}...")
        
        st.write(f"✅ Processed {appendix_count} appendices total")
    else:
        st.write(f"❌ NO APPENDICES SECTION in {agreement_name}")
        # Check if appendices might be stored elsewhere
        st.write("🔍 Searching entire agreement for appendix-related content...")
        full_agreement_text = json.dumps(agreement).lower()
        if "appendix" in full_agreement_text:
            st.write("✅ Found 'appendix' text somewhere in agreement")
            # Count occurrences
            appendix_count = full_agreement_text.count("appendix")
            st.write(f"  - 'appendix' appears {appendix_count} times")
        if "program coordination" in full_agreement_text:
            st.write("✅ Found 'program coordination' text in agreement")
    
    # Final context debug
    final_length = len(context)
    st.write(f"🔍 FINAL CONTEXT STATS:")
    st.write(f"- Total context length: {final_length:,} characters")
    
    # Search for key terms in final context
    context_lower = context.lower()
    if "appendix 3" in context_lower:
        st.write("✅ 'appendix 3' found in final context")
        appendix_3_positions = []
        start = 0
        while True:
            pos = context_lower.find("appendix 3", start)
            if pos == -1:
                break
            appendix_3_positions.append(pos)
            start = pos + 1
        st.write(f"  - Found at positions: {appendix_3_positions}")
    else:
        st.write("❌ 'appendix 3' NOT found in final context")
    
    if "program coordination" in context_lower:
        st.write("✅ 'program coordination' found in final context")
    else:
        st.write("❌ 'program coordination' NOT found in final context")
    
    # Show context sample around appendices
    appendices_pos = context_lower.find("appendices:")
    if appendices_pos >= 0:
        st.write("🔍 CONTEXT AROUND APPENDICES SECTION:")
        sample_start = max(0, appendices_pos - 100)
        sample_end = min(len(context), appendices_pos + 500)
        sample = context[sample_start:sample_end]
        st.code(sample)
    
    return context

def generate_response(query: str, local_agreement: dict, common_agreement: dict, agreement_scope: str, api_key: str) -> str:
    """Generate response using Claude with complete agreement context"""
    
    st.write(f"🔍 GENERATING RESPONSE for scope: {agreement_scope}")
    
    # Build context based on selected scope
    context = ""
    if agreement_scope == "Local Agreement Only":
        st.write("🔍 Building context from Local Agreement only")
        context = format_agreement_for_context(local_agreement, "Coast Mountain College Local Agreement")
    elif agreement_scope == "Common Agreement Only":
        st.write("🔍 Building context from Common Agreement only")
        context = format_agreement_for_context(common_agreement, "BCGEU Common Agreement")
    else:  # Both agreements
        st.write("🔍 Building context from both agreements")
        context = format_agreement_for_context(local_agreement, "Coast Mountain College Local Agreement")
        context += "\n\n" + format_agreement_for_context(common_agreement, "BCGEU Common Agreement")
    
    # Final pre-send debug
    st.write(f"🔍 PRE-SEND FINAL CHECK:")
    st.write(f"- Final context length: {len(context):,} characters")
    st.write(f"- Query contains 'appendix 3': {'appendix 3' in query.lower()}")
    st.write(f"- Context contains 'appendix 3': {'appendix 3' in context.lower()}")
    st.write(f"- Context contains 'program coordination': {'program coordination' in context.lower()}")
    
    # Show first and last parts of context
    st.write("🔍 CONTEXT PREVIEW:")
    st.write("First 300 chars:")
    st.code(context[:300])
    st.write("Last 300 chars:")
    st.code(context[-300:])
    
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
