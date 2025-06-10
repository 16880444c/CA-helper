import json
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SearchResult:
    source: str
    number: str
    article: Dict[str, Any]
    score: int

class CollectiveAgreementAssistant:
    def __init__(self):
        self.local_agreement = None
        self.common_agreement = None
        self.stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 
            'did', 'she', 'use', 'way', 'will', 'from', 'they', 'know', 'want', 
            'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 
            'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 
            'them', 'well', 'were'
        }

    def load_agreements(self, local_path: str, common_path: str) -> bool:
        """Load both agreement JSON files."""
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                self.local_agreement = json.load(f)
            print(f"✅ Local Agreement loaded ({len(self.local_agreement)} articles)")
            
            with open(common_path, 'r', encoding='utf-8') as f:
                self.common_agreement = json.load(f)
            print(f"✅ Common Agreement loaded ({len(self.common_agreement)} articles)")
            
            return True
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False

    def extract_keywords(self, query: str) -> Dict[str, List[str]]:
        """Extract article numbers and key terms from the query."""
        # Extract article numbers (e.g., "17.8", "Article 17.8")
        article_pattern = r'(?:article\s+)?(\d+(?:\.\d+)?)'
        article_matches = re.findall(article_pattern, query, re.IGNORECASE)
        
        # Extract key terms
        words = re.sub(r'[^\w\s\.]', ' ', query.lower()).split()
        terms = [word for word in words 
                if len(word) > 2 and word not in self.stop_words]
        
        return {
            'article_numbers': article_matches,
            'terms': terms,
            'original_query': query.lower()
        }

    def get_article_text(self, article: Dict[str, Any]) -> str:
        """Extract all text content from an article."""
        text_parts = []
        
        # Add title
        if 'title' in article:
            text_parts.append(article['title'])
        
        # Add direct content
        if 'content' in article and isinstance(article['content'], str):
            text_parts.append(article['content'])
        
        # Handle direct subsections (like Article 17.8)
        if 'subsections' in article:
            for subsection_content in article['subsections'].values():
                if isinstance(subsection_content, str):
                    text_parts.append(subsection_content)
        
        # Handle sections with subsections
        if 'sections' in article:
            for section in article['sections'].values():
                if isinstance(section, str):
                    text_parts.append(section)
                elif isinstance(section, dict):
                    if 'title' in section:
                        text_parts.append(section['title'])
                    if 'content' in section:
                        text_parts.append(section['content'])
                    if 'subsections' in section:
                        for subsection_content in section['subsections'].values():
                            if isinstance(subsection_content, str):
                                text_parts.append(subsection_content)
        
        return ' '.join(text_parts)

    def score_article_relevance(self, article: Dict[str, Any], keywords: Dict[str, List[str]], article_number: str) -> int:
        """Calculate relevance score for an article."""
        score = 0
        content = self.get_article_text(article).lower()
        title = article.get('title', '').lower()
        
        # Exact article number match (highest priority)
        if article_number in keywords['article_numbers']:
            score += 1000
        
        # Title matches (high priority)
        for term in keywords['terms']:
            if term in title:
                score += 50
            # Count term frequency in content
            term_count = content.count(term)
            score += term_count * 10
        
        # Phrase matching
        if keywords['original_query'] in content:
            score += 100
        
        return score

    def find_relevant_articles(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Find and rank articles relevant to the query."""
        if not self.local_agreement or not self.common_agreement:
            print("❌ Please load both agreement files first!")
            return []
        
        keywords = self.extract_keywords(query)
        results = []
        
        # Search local agreement
        for article_num, article in self.local_agreement.items():
            score = self.score_article_relevance(article, keywords, article_num)
            if score > 0:
                results.append(SearchResult(
                    source='Local Agreement',
                    number=article_num,
                    article=article,
                    score=score
                ))
        
        # Search common agreement
        for article_num, article in self.common_agreement.items():
            score = self.score_article_relevance(article, keywords, article_num)
            if score > 0:
                results.append(SearchResult(
                    source='Common Agreement',
                    number=article_num,
                    article=article,
                    score=score
                ))
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Return top results
        return results[:max_results]

    def format_article_content(self, article: Dict[str, Any]) -> str:
        """Format article content for display."""
        content_parts = []
        
        # Add direct content
        if 'content' in article and isinstance(article['content'], str):
            content_parts.append(f"Content: {article['content']}")
        
        # Handle direct subsections (like Article 17.8)
        if 'subsections' in article:
            content_parts.append("Subsections:")
            for key, content in article['subsections'].items():
                content_parts.append(f"  ({key}) {content}")
        
        # Handle sections with subsections
        if 'sections' in article:
            for section_key, section in article['sections'].items():
                if isinstance(section, str):
                    content_parts.append(f"Section {section_key}: {section}")
                elif isinstance(section, dict):
                    section_title = section.get('title', f'Section {section_key}')
                    content_parts.append(f"Section {section_key}: {section_title}")
                    
                    if 'content' in section:
                        content_parts.append(f"  {section['content']}")
                    
                    if 'subsections' in section:
                        for sub_key, sub_content in section['subsections'].items():
                            content_parts.append(f"  ({sub_key}) {sub_content}")
        
        return '\n'.join(content_parts) if content_parts else "No content available"

    def search(self, query: str, max_results: int = 5) -> str:
        """Perform a search and return formatted results."""
        print(f"\n🔍 Searching for: '{query}'")
        print("=" * 60)
        
        results = self.find_relevant_articles(query, max_results)
        
        if not results:
            return "❌ No relevant articles found. Try different keywords or check spelling."
        
        output = []
        output.append(f"📋 Found {len(results)} relevant articles:\n")
        
        for i, result in enumerate(results, 1):
            output.append(f"🔸 Result {i}: Article {result.number} - {result.source}")
            output.append(f"   Title: {result.article.get('title', 'Untitled')}")
            output.append(f"   Relevance Score: {result.score}")
            output.append(f"   Content:")
            
            # Format and indent content
            formatted_content = self.format_article_content(result.article)
            for line in formatted_content.split('\n'):
                output.append(f"   {line}")
            
            output.append("")  # Empty line between articles
        
        # Add debug info
        keywords = self.extract_keywords(query)
        output.append("🔧 Debug Information:")
        output.append(f"   Keywords: {', '.join(keywords['terms'])}")
        output.append(f"   Article Numbers: {', '.join(keywords['article_numbers']) if keywords['article_numbers'] else 'None'}")
        
        return '\n'.join(output)

    def get_article_by_number(self, article_number: str) -> str:
        """Get a specific article by number."""
        # Check local agreement first
        if self.local_agreement and article_number in self.local_agreement:
            article = self.local_agreement[article_number]
            output = []
            output.append(f"📄 Article {article_number} - Local Agreement")
            output.append(f"Title: {article.get('title', 'Untitled')}")
            output.append("Content:")
            output.append(self.format_article_content(article))
            return '\n'.join(output)
        
        # Check common agreement
        if self.common_agreement and article_number in self.common_agreement:
            article = self.common_agreement[article_number]
            output = []
            output.append(f"📄 Article {article_number} - Common Agreement")
            output.append(f"Title: {article.get('title', 'Untitled')}")
            output.append("Content:")
            output.append(self.format_article_content(article))
            return '\n'.join(output)
        
        return f"❌ Article {article_number} not found in either agreement."

def main():
    """Interactive command-line interface."""
    assistant = CollectiveAgreementAssistant()
    
    print("🏛️  Collective Agreement Assistant")
    print("=" * 50)
    print("This tool searches collective agreements using complete JSON files.")
    print("No indexing required - every article is always available!\n")
    
    # Load agreement files
    while True:
        local_path = input("📁 Enter path to Local Agreement JSON file: ").strip()
        common_path = input("📁 Enter path to Common Agreement JSON file: ").strip()
        
        if assistant.load_agreements(local_path, common_path):
            break
        else:
            print("Please check your file paths and try again.\n")
    
    print("\n✅ Ready to search! Type 'quit' to exit, 'help' for commands.\n")
    
    # Interactive search loop
    while True:
        try:
            query = input("🔍 Enter your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\n📖 Available commands:")
                print("  • Ask questions: 'What is the vacation carryover limit?'")
                print("  • Get specific articles: 'Show me Article 17.8'")
                print("  • Search by keywords: 'vacation policy'")
                print("  • Type 'quit' to exit")
                print("  • Type 'help' for this message\n")
                continue
            
            # Check if asking for specific article
            article_match = re.search(r'(?:article\s+)?(\d+(?:\.\d+)?)', query, re.IGNORECASE)
            if article_match and ('show' in query.lower() or 'article' in query.lower()):
                article_num = article_match.group(1)
                result = assistant.get_article_by_number(article_num)
                print(result)
            else:
                result = assistant.search(query)
                print(result)
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# Example usage as a module
def example_usage():
    """Example of how to use the assistant programmatically."""
    assistant = CollectiveAgreementAssistant()
    
    # Load agreements
    if assistant.load_agreements('local_agreement.json', 'common_agreement.json'):
        
        # Search for vacation carryover
        print(assistant.search("vacation carryover limit"))
        
        # Get specific article
        print(assistant.get_article_by_number("17.8"))
        
        # Search for management rights
        print(assistant.search("management rights employer authority"))

if __name__ == "__main__":
    main()
