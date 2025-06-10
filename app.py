import streamlit as st
import json
import openai
from datetime import datetime
import os
import numpy as np
from typing import List, Dict, Tuple
import pickle
from dataclasses import dataclass
import hashlib

# For embeddings and vector search
try:
    import faiss
except ImportError:
    st.error("Please install faiss: pip install faiss-cpu")
    st.stop()

# Check if JSON files are available
BUILTIN_AGREEMENTS_AVAILABLE = os.path.exists('complete_local.json') and os.path.exists('complete_common.json')

# Set page config
st.set_page_config(
    page_title="Smart Collective Agreement Assistant",
    page_icon="⚖️",
    layout="wide"
)

@dataclass
class DocumentChunk:
    content: str
    metadata: Dict
    embedding: np.ndarray = None

class CollectiveAgreementRAG:
    def __init__(self):
        self.chunks = []
        self.index = None
        self.embeddings_cache_file = "embeddings_cache.pkl"
        
    def smart_chunk_json_agreement(self, agreement_data: Dict, agreement_name: str) -> List[DocumentChunk]:
        """Intelligently chunk the agreement by articles and sections"""
        chunks = []
        
        # Add metadata
        metadata = agreement_data.get('agreement_metadata', {})
        chunk = DocumentChunk(
            content=f"AGREEMENT METADATA for {agreement_name}:\n" + json.dumps(metadata, indent=2),
            metadata={
                'agreement': agreement_name,
                'type': 'metadata',
                'section': 'agreement_metadata'
            }
        )
        chunks.append(chunk)
        
        # Add definitions
        definitions = agreement_data.get('definitions', {})
        if definitions:
            content = f"DEFINITIONS from {agreement_name}:\n"
            for term, definition in definitions.items():
                content += f"\n{term}: {definition}\n"
            
            chunk = DocumentChunk(
                content=content,
                metadata={
                    'agreement': agreement_name,
                    'type': 'definitions',
                    'section': 'definitions'
                }
            )
            chunks.append(chunk)
        
        # Process articles
        articles = agreement_data.get('articles', {})
        for article_num, article_data in articles.items():
            if isinstance(article_data, dict):
                title = article_data.get('title', f'Article {article_num}')
                
                # Create main article chunk
                content = f"ARTICLE {article_num}: {title} ({agreement_name})\n\n"
                
                # Add sections
                sections = article_data.get('sections', {})
                if sections:
                    for section_key, section_data in sections.items():
                        content += f"\nSection {section_key}:\n"
                        if isinstance(section_data, dict):
                            if 'title' in section_data:
                                content += f"Title: {section_data['title']}\n"
                            if 'content' in section_data:
                                content += f"Content: {section_data['content']}\n"
                            if 'subsections' in section_data:
                                content += "Subsections:\n"
                                for sub_key, sub_content in section_data['subsections'].items():
                                    content += f"  {sub_key}) {sub_content}\n"
                        else:
                            content += f"{section_data}\n"
                
                # Add other content if no sections
                if not sections and 'content' in article_data:
                    content += f"\n{article_data['content']}\n"
                
                chunk = DocumentChunk(
                    content=content,
                    metadata={
                        'agreement': agreement_name,
                        'type': 'article',
                        'article_number': article_num,
                        'article_title': title,
                        'section': f'article_{article_num}'
                    }
                )
                chunks.append(chunk)
        
        # Process appendices
        appendices = agreement_data.get('appendices', {})
        for appendix_key, appendix_data in appendices.items():
            content = f"APPENDIX {appendix_key} ({agreement_name}):\n"
            if isinstance(appendix_data, dict):
                if 'title' in appendix_data:
                    content += f"Title: {appendix_data['title']}\n\n"
                content += json.dumps(appendix_data, indent=2)
            else:
                content += str(appendix_data)
            
            chunk = DocumentChunk(
                content=content,
                metadata={
                    'agreement': agreement_name,
                    'type': 'appendix',
                    'appendix_key': appendix_key,
                    'section': f'appendix_{appendix_key}'
                }
            )
            chunks.append(chunk)
            
        return chunks
    
    def create_embeddings(self, api_key: str, force_refresh: bool = False):
        """Create embeddings for all chunks"""
        
        # Check if we can load from cache
        cache_hash = self._get_content_hash()
        if not force_refresh and os.path.exists(self.embeddings_cache_file):
            try:
                with open(self.embeddings_cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if cache_data.get('hash') == cache_hash:
                        self.chunks = cache_data['chunks']
                        self._build_faiss_index()
                        return True
            except:
                pass
        
        # Create new embeddings
        client = openai.OpenAI(api_key=api_key)
        
        embeddings = []
        texts = [chunk.content for chunk in self.chunks]
        
        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            try:
                response = client.embeddings.create(
                    model="text-embedding-3-large",
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                st.error(f"Error creating embeddings: {e}")
                return False
        
        # Add embeddings to chunks
        for chunk, embedding in zip(self.chunks, embeddings):
            chunk.embedding = np.array(embedding, dtype=np.float32)
        
        # Cache the results
        self._save_embeddings_cache(cache_hash)
        
        # Build FAISS index
        self._build_faiss_index()
        return True
    
    def _get_content_hash(self) -> str:
        """Generate hash of all chunk contents for caching"""
        content = "".join([chunk.content for chunk in self.chunks])
        return hashlib.md5(content.encode()).hexdigest()
    
    def _save_embeddings_cache(self, content_hash: str):
        """Save embeddings to cache file"""
        cache_data = {
            'hash': content_hash,
            'chunks': self.chunks
        }
        try:
            with open(self.embeddings_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            st.warning(f"Could not save embeddings cache: {e}")
    
    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        if not self.chunks or self.chunks[0].embedding is None:
            return
        
        # Convert embeddings to numpy array with proper dtype
        embeddings_list = []
        for chunk in self.chunks:
            if chunk.embedding is not None:
                embeddings_list.append(chunk.embedding)
        
        if not embeddings_list:
            return
            
        embeddings = np.array(embeddings_list, dtype=np.float32)
        dimension = embeddings.shape[1]
        
        # Use IndexFlatIP for cosine similarity
        self.index = faiss.IndexFlatIP(dimension)
        
        # Ensure embeddings are contiguous and normalize
        embeddings = np.ascontiguousarray(embeddings)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
    
    def search(self, query: str, api_key: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for relevant chunks using semantic similarity"""
        if not self.index:
            return []
        
        # Create query embedding
        client = openai.OpenAI(api_key=api_key)
        try:
            response = client.embeddings.create(
                model="text-embedding-3-large",
                input=[query]
            )
            query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
            query_embedding = np.ascontiguousarray(query_embedding)
            faiss.normalize_L2(query_embedding)
        except Exception as e:
            st.error(f"Error creating query embedding: {e}")
            return []
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid index
                results.append((self.chunks[idx], float(score)))
        
        return results

def load_agreement_from_file(file) -> Dict:
    """Load agreement from uploaded file"""
    try:
        content = file.read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def load_builtin_agreements() -> Tuple[Dict, Dict]:
    """Load the built-in agreements from JSON files"""
    try:
        # Load from the JSON files directly
        with open('complete_local.json', 'r', encoding='utf-8') as f:
            local_agreement = json.load(f)
        
        with open('complete_common.json', 'r', encoding='utf-8') as f:
            common_agreement = json.load(f)
        
        return local_agreement, common_agreement
        
    except FileNotFoundError as e:
        st.error(f"JSON files not found: {str(e)}")
        st.info("Please ensure 'complete_local.json' and 'complete_common.json' are in the same directory as the app.")
        return None, None
    except Exception as e:
        st.error(f"Error loading built-in agreements: {e}")
        return None, None

def generate_response(query: str, relevant_chunks: List[Tuple[DocumentChunk, float]], api_key: str) -> str:
    """Generate response using GPT with relevant context"""
    
    # Build context from relevant chunks
    context = ""
    for chunk, score in relevant_chunks:
        context += f"\n=== {chunk.metadata.get('agreement', 'Unknown')} - {chunk.metadata.get('section', 'Unknown')} (Relevance: {score:.3f}) ===\n"
        context += chunk.content + "\n"
    
    system_prompt = f"""You are a HR expert for Coast Mountain College with 15+ years of experience in collective agreement interpretation and employee relations. Your role is to provide STRONG, DEFINITIVE guidance that maximizes management's rights and authority under the collective agreements.

You have access to two collective agreements:

1. LOCAL AGREEMENT: Coast Mountain College Local Collective Agreement
2. COMMON AGREEMENT: Common Agreement between BC Colleges and BCGEU

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

    user_prompt = f"""Based on the collective agreement provisions below, provide strong management-focused guidance for this question:

QUESTION: {query}

RELEVANT AGREEMENT PROVISIONS:
{context}

Provide definitive, management-favorable guidance with specific citations and quotes from the agreement text."""

    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {e}"

def main():
    st.title("⚖️ Smart Collective Agreement Assistant")
    st.markdown("*Advanced RAG-based guidance for Coast Mountain College collective agreements*")
    
    # Initialize session state
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = CollectiveAgreementRAG()
    if 'agreements_loaded' not in st.session_state:
        st.session_state.agreements_loaded = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
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
            if not api_key:
                st.warning("Please provide your OpenAI API key to continue")
                st.stop()
        
        st.markdown("---")
        
        # File uploads or use built-in
        st.header("📁 Load Agreements")
        
        if BUILTIN_AGREEMENTS_AVAILABLE:
            use_builtin = st.checkbox("Use built-in JSON files", value=True)
        else:
            use_builtin = False
            st.info("💡 Place 'complete_local.json' and 'complete_common.json' in the app directory to enable built-in loading")
        
        if use_builtin and BUILTIN_AGREEMENTS_AVAILABLE:
            if st.button("🔄 Load JSON Files"):
                with st.spinner("Loading agreements from JSON files..."):
                    local_agreement, common_agreement = load_builtin_agreements()
                    
                    if local_agreement and common_agreement:
                        # Create chunks
                        rag = CollectiveAgreementRAG()
                        local_chunks = rag.smart_chunk_json_agreement(local_agreement, "Local Agreement")
                        common_chunks = rag.smart_chunk_json_agreement(common_agreement, "Common Agreement")
                        
                        rag.chunks = local_chunks + common_chunks
                        
                        # Create embeddings
                        if rag.create_embeddings(api_key):
                            st.session_state.rag_system = rag
                            st.session_state.agreements_loaded = True
                            st.success(f"✅ Processed {len(rag.chunks)} chunks from JSON files!")
                            st.rerun()
                        else:
                            st.error("Failed to create embeddings")
                    else:
                        st.error("Failed to load JSON files - please upload manually")
        else:
            local_file = st.file_uploader("Local Agreement JSON", type="json", key="local")
            common_file = st.file_uploader("Common Agreement JSON", type="json", key="common")
            
            if st.button("🔄 Process Uploaded Agreements"):
                if local_file and common_file:
                    with st.spinner("Loading and processing agreements..."):
                        # Load agreements
                        local_agreement = load_agreement_from_file(local_file)
                        common_agreement = load_agreement_from_file(common_file)
                        
                        if local_agreement and common_agreement:
                            # Create chunks
                            rag = CollectiveAgreementRAG()
                            local_chunks = rag.smart_chunk_json_agreement(local_agreement, "Local Agreement")
                            common_chunks = rag.smart_chunk_json_agreement(common_agreement, "Common Agreement")
                            
                            rag.chunks = local_chunks + common_chunks
                            
                            # Create embeddings
                            if rag.create_embeddings(api_key):
                                st.session_state.rag_system = rag
                                st.session_state.agreements_loaded = True
                                st.success(f"✅ Processed {len(rag.chunks)} chunks successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to create embeddings")
                        else:
                            st.error("Failed to load agreement files")
                else:
                    st.error("Please upload both agreement files")
        
        # Stats
        if st.session_state.agreements_loaded:
            st.markdown("---")
            st.header("📊 Status")
            st.success("✅ Agreements Loaded")
            st.info(f"📄 {len(st.session_state.rag_system.chunks)} chunks indexed")
            
            if st.button("🔄 Refresh Embeddings"):
                with st.spinner("Refreshing embeddings..."):
                    if st.session_state.rag_system.create_embeddings(api_key, force_refresh=True):
                        st.success("✅ Embeddings refreshed!")
                        st.rerun()
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        **Advanced RAG System**
        - Semantic search across full agreements
        - Smart chunking by articles/sections  
        - Management-focused guidance
        - Fast vector similarity search
        """)
    
    # Main interface
    if not st.session_state.agreements_loaded:
        st.info("👆 Please upload and process your collective agreement files in the sidebar to begin.")
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
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching agreements and generating response..."):
                # Search for relevant chunks
                results = st.session_state.rag_system.search(prompt, api_key, top_k=5)
                
                if results:
                    # Generate response
                    response = generate_response(prompt, results, api_key)
                    st.markdown(response)
                    
                    # Show sources
                    with st.expander("📚 Sources Used"):
                        for chunk, score in results:
                            st.write(f"**{chunk.metadata.get('agreement')} - {chunk.metadata.get('section')}** (Score: {score:.3f})")
                            st.write(chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content)
                            st.markdown("---")
                    
                else:
                    response = "I couldn't find relevant information in the agreements for your query. Please try rephrasing your question."
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick start questions
    if len(st.session_state.messages) == 0:
        st.markdown("### 🚀 Quick Start Questions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💼 Employee Discipline Rights"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are management's rights regarding employee discipline and dismissal? Include specific citations and management protections."
                })
                st.rerun()
                
            if st.button("📋 Layoff Procedures"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What authority does management have in layoff situations? What are the specific procedural requirements?"
                })
                st.rerun()
        
        with col2:
            if st.button("⏱️ Grievance Time Limits"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What are the time limits and procedures for grievances that protect management? Include deadlines and procedural defenses."
                })
                st.rerun()
                
            if st.button("📚 Workload Management"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "What flexibility does management have in assigning instructor workloads and schedules?"
                })
                st.rerun()

if __name__ == "__main__":
    main()
