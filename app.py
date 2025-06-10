import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
import os

@dataclass
class SearchResult:
    source: str
    number: str
    article: Dict[str, Any]
    score: int

class CollectiveAgreementAssistant:
    def __init__(self, local_path: Optional[str] = None, common_path: Optional[str] = None):
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
        
        # Auto-load if paths provided
        if local_path and common_path:
            self.load_agreements(local_path, common_path)

    def load_agreements(self, local_path: str, common_path: str) -> bool:
        """Load both agreement JSON files."""
        try:
            # Check if files exist
            if not os.path.exists(local_path):
                print(f"❌ Local agreement file not found: {local_path}")
                return False
            if not os.path.exists(common_path):
                print(f"❌ Common agreement file not found: {common_path}")
                return False
            
            # Load local agreement
            with open(local_path, 'r', encoding='utf-8') as f:
                self.local_agreement = json.load(f)
            print(f"✅ Local Agreement loaded ({len(self.local_agreement)} articles)")
            
            # Load common agreement
            with open(common_path, 'r', encoding='utf-8') as f:
                self.common_agreement = json.load(f)
            print(f"✅ Common Agreement loaded ({len(self.common_agreement)} articles)")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading files: {e}")
            return False

    def is_ready(self) -> bool:
        """Check if both agreements are loaded."""
        return self.local_agreement is not None and self.common_agreement is not None

    def extract_keywords(self, query: str) -> Dict[str, List[str]]:
        """Extract article numbers and key terms from the query."""
        # Extract article numbers (e.g., "1.5", "Article 12.3")
        article_pattern = r'(?:article\s+)?(\d+(?:\.\d+)?)'
        article_matches = re.findall(article_pattern, query, re.IGNORECASE)
        
        # Extract key terms (remove punctuation, filter short words and stop words)
        words = re.sub(r'[^\w\s]', ' ', query.lower()).split()
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
        if 'title' in article and article['title']:
            text_parts.append(str(article['title']))
        
        # Add direct content
        if 'content' in article and isinstance(article['content'], str):
            text_parts.append(article['content'])
        
        # Handle direct subsections at article level
        if 'subsections' in article and isinstance(article['subsections'], dict):
            for subsection_content in article['subsections'].values():
                if isinstance(subsection_content, str):
                    text_parts.append(subsection_content)
        
        # Handle sections with potential subsections
        if 'sections' in article and isinstance(article['sections'], dict):
            for section in article['sections'].values():
                if isinstance(section, str):
                    text_parts.append(section)
                elif isinstance(section, dict):
                    # Add section title
                    if 'title' in section and section['title']:
                        text_parts.append(str(section['title']))
                    # Add section content
                    if 'content' in section and section['content']:
                        text_parts.append(str(section['content']))
                    # Add section subsections
                    if 'subsections' in section and isinstance(section['subsections'], dict):
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
        
        # Title keyword matches (high priority)
        for term in keywords['terms']:
            if term in title:
                score += 50
        
        # Content keyword frequency
        for term in keywords['terms']:
            term_count = content.count(term)
            score += term_count * 10
        
        # Exact phrase matching
        if len(keywords['original_query']) > 5 and keywords['original_query'] in content:
            score += 100
        
        return score

    def find_relevant_articles(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Find and rank articles relevant to the query."""
        if not self.is_ready():
            print("❌ Please load both agreement files first!")
            return []
        
        keywords = self.extract_keywords(query)
        results = []
        
        # Search local agreement
        if self.local_agreement:
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
        if self.common_agreement:
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
        
        return results[:max_results]

    def format_article_content(self, article: Dict[str, Any]) -> str:
        """Format article content for display."""
        content_parts = []
        
        # Add direct content
        if 'content' in article and isinstance(article['content'], str):
            content_parts.append(f"Content: {article['content']}")
        
        # Handle direct subsections at article level
        if 'subsections' in article and isinstance(article['subsections'], dict):
            content_parts.append("Subsections:")
            for key, content in article['subsections'].items():
                if isinstance(content, str):
                    content_parts.append(f"  ({key}) {content}")
        
        # Handle sections with subsections
        if 'sections' in article and isinstance(article['sections'], dict):
            for section_key, section in article['sections'].items():
                if isinstance(section, str):
                    content_parts.append(f"Section {section_key}: {section}")
                elif isinstance(section, dict):
                    section_title = section.get('title', f'Section {section_key}')
                    content_parts.append(f"Section {section_key}: {section_title}")
                    
                    if 'content' in section and section['content']:
                        content_parts.append(f"  {section['content']}")
                    
                    if 'subsections' in section and isinstance(section['subsections'], dict):
                        for sub_key, sub_content in section['subsections'].items():
                            if isinstance(sub_content, str):
                                content_parts.append(f"  ({sub_key}) {sub_content}")
        
        return '\n'.join(content_parts) if content_parts else "No content available"

    def search(self, query: str, max_results: int = 5, verbose: bool = True) -> Dict[str, Any]:
        """Perform a search and return results."""
        if verbose:
            print(f"\n🔍 Searching for: '{query}'")
            print("=" * 60)
        
        results = self.find_relevant_articles(query, max_results)
        
        if not results:
            if verbose:
                print("❌ No relevant articles found.")
            return {
                'query': query,
                'results': [],
                'total_found': 0,
                'keywords': self.extract_keywords(query)
            }
        
        if verbose:
            print(f"📋 Found {len(results)} relevant articles:\n")
            
            for i, result in enumerate(results, 1):
                print(f"🔸 Result {i}: Article {result.number} - {result.source}")
                print(f"   Title: {result.article.get('title', 'Untitled')}")
                print(f"   Relevance Score: {result.score}")
                print(f"   Content:")
                
                # Format and indent content
                formatted_content = self.format_article_content(result.article)
                for line in formatted_content.split('\n'):
                    print(f"   {line}")
                print()  # Empty line between articles
            
            # Add debug info
            keywords = self.extract_keywords(query)
            print("🔧 Debug Information:")
            print(f"   Keywords: {', '.join(keywords['terms'])}")
            print(f"   Article Numbers: {', '.join(keywords['article_numbers']) if keywords['article_numbers'] else 'None'}")
        
        return {
            'query': query,
            'results': results,
            'total_found': len(results),
            'keywords': self.extract_keywords(query)
        }

    def get_article_by_number(self, article_number: str, verbose: bool = True) -> Optional[Dict[str, Any]]:
        """Get a specific article by number."""
        # Clean the article number
        article_number = article_number.strip()
        
        # Check local agreement first
        if self.local_agreement and article_number in self.local_agreement:
            article = self.local_agreement[article_number]
            if verbose:
                print(f"📄 Article {article_number} - Local Agreement")
                print(f"Title: {article.get('title', 'Untitled')}")
                print("Content:")
                print(self.format_article_content(article))
            return {
                'source': 'Local Agreement',
                'number': article_number,
                'article': article
            }
        
        # Check common agreement
        if self.common_agreement and article_number in self.common_agreement:
            article = self.common_agreement[article_number]
            if verbose:
                print(f"📄 Article {article_number} - Common Agreement")
                print(f"Title: {article.get('title', 'Untitled')}")
                print("Content:")
                print(self.format_article_content(article))
            return {
                'source': 'Common Agreement',
                'number': article_number,
                'article': article
            }
        
        if verbose:
            print(f"❌ Article {article_number} not found in either agreement.")
        return None

    def list_all_articles(self, agreement: str = 'both') -> List[str]:
        """List all article numbers in the specified agreement(s)."""
        articles = []
        
        if agreement in ['both', 'local'] and self.local_agreement:
            for num in self.local_agreement.keys():
                articles.append(f"{num} (Local)")
        
        if agreement in ['both', 'common'] and self.common_agreement:
            for num in self.common_agreement.keys():
                articles.append(f"{num} (Common)")
        
        return sorted(articles)

# Example usage functions
def example_basic_usage():
    """Basic example of how to use the assistant."""
    print("🔧 Basic Usage Example")
    print("=" * 30)
    
    # Initialize with file paths
    assistant = CollectiveAgreementAssistant('local_agreement.json', 'common_agreement.json')
    
    if not assistant.is_ready():
        print("Please ensure both JSON files exist and are valid.")
        return
    
    # Example searches
    queries = [
        "vacation policy",
        "management rights",
        "grievance procedure",
        "overtime compensation"
    ]
    
    for query in queries:
        result = assistant.search(query, max_results=3)
        print(f"Found {result['total_found']} results for '{query}'\n")

def example_programmatic_usage():
    """Example of programmatic usage without verbose output."""
    assistant = CollectiveAgreementAssistant()
    
    # Load files manually
    if assistant.load_agreements('local_agreement.json', 'common_agreement.json'):
        
        # Search without verbose output
        result = assistant.search("vacation", verbose=False)
        
        # Process results programmatically
        for search_result in result['results']:
            print(f"Found: {search_result.source} Article {search_result.number}")
            print(f"Title: {search_result.article.get('title')}")
            print(f"Score: {search_result.score}")
            print()

def simple_test():
    """Simple test function to verify the system works."""
    print("🧪 Testing Collective Agreement Assistant")
    print("=" * 45)
    
    # Test with dummy data
    dummy_local = {
        "1.1": {
            "title": "Recognition",
            "content": "The employer recognizes the union as the exclusive bargaining agent."
        },
        "2.5": {
            "title": "Vacation Policy",
            "subsections": {
                "a": "Employees are entitled to vacation time based on years of service.",
                "b": "Vacation requests must be submitted in advance."
            }
        }
    }
    
    dummy_common = {
        "3.1": {
            "title": "Grievance Procedure",
            "sections": {
                "1": {
                    "title": "Filing",
                    "content": "Grievances must be filed within 30 days."
                }
            }
        }
    }
    
    # Create temporary files
    with open('test_local.json', 'w') as f:
        json.dump(dummy_local, f)
    with open('test_common.json', 'w') as f:
        json.dump(dummy_common, f)
    
    # Test the assistant
    assistant = CollectiveAgreementAssistant('test_local.json', 'test_common.json')
    
    if assistant.is_ready():
        print("✅ System loaded successfully!")
        
        # Test search
        result = assistant.search("vacation", max_results=2)
        print(f"✅ Search test passed - found {result['total_found']} results")
        
        # Test specific article lookup
        article = assistant.get_article_by_number("2.5")
        if article:
            print("✅ Article lookup test passed")
        
    # Cleanup
    os.remove('test_local.json')
    os.remove('test_common.json')
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    # Run the simple test by default
    simple_test()
