def format_agreement_for_context(agreement, agreement_name):
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
    
    # Debug appendices section
    if 'appendices' in agreement:
        context += "APPENDICES:\n\n"
        context += f"DEBUG: Found {len(agreement['appendices'])} appendices\n"
        context += f"DEBUG: Appendix keys: {list(agreement['appendices'].keys())}\n\n"
        
        for appendix_key, appendix_data in agreement['appendices'].items():
            # Convert appendix_3 to "APPENDIX 3" for better readability
            display_key = appendix_key.replace('_', ' ').upper()
            context += f"{display_key}:\n"
            context += f"DEBUG: Type of appendix_data: {type(appendix_data)}\n"
            
            if isinstance(appendix_data, dict):
                if 'title' in appendix_data:
                    context += f"Title: {appendix_data['title']}\n\n"
                
                # Try to format the content more readably instead of just JSON dump
                for key, value in appendix_data.items():
                    if key == 'title':
                        continue  # Already handled above
                    context += f"{key.replace('_', ' ').title()}: "
                    if isinstance(value, dict):
                        context += "\n"
                        for sub_key, sub_value in value.items():
                            context += f"  - {sub_key.replace('_', ' ').title()}: {sub_value}\n"
                    elif isinstance(value, list):
                        context += "\n"
                        for item in value:
                            context += f"  - {item}\n"
                    else:
                        context += f"{value}\n"
                    context += "\n"
            else:
                context += str(appendix_data)
            context += "\n" + "="*50 + "\n\n"
    else:
        context += "DEBUG: No 'appendices' key found in agreement\n\n"
    
    return context
