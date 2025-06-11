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
           # Convert appendix_3 to "APPENDIX 3" for better readability
           display_key = appendix_key.replace('_', ' ').upper()
           context += f"{display_key}:\n"
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

   user_message = f"""Based on the complete collective agreement pr
