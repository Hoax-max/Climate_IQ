"""
RAG (Retrieval-Augmented Generation) system for climate knowledge
"""
import os
import logging
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from backend.watsonx_integration.watsonx_client import WatsonXClient
from config import settings

logger = logging.getLogger(__name__)

class ClimateRAGSystem:
    """RAG system specialized for climate action knowledge"""
    
    def __init__(self):
        self.watsonx_client = WatsonXClient()
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.chroma_client = None
        self.collection = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB vector database"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="climate_knowledge",
                metadata={"description": "Climate action and environmental knowledge base"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the knowledge base"""
        try:
            texts = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(documents):
                # Split document into chunks
                chunks = self.text_splitter.split_text(doc['content'])
                
                for j, chunk in enumerate(chunks):
                    texts.append(chunk)
                    metadatas.append({
                        'source': doc.get('source', 'unknown'),
                        'title': doc.get('title', 'Untitled'),
                        'category': doc.get('category', 'general'),
                        'chunk_id': f"{i}_{j}"
                    })
                    ids.append(f"doc_{i}_chunk_{j}")
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} chunks from {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant information"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def retrieve_and_generate(self, query: str, user_profile: Dict[str, Any] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Retrieve relevant knowledge and generate response"""
        try:
            # Enhance query with user context
            enhanced_query = self._enhance_query(query, user_profile)
            
            # Search for relevant documents
            relevant_docs = self.search_knowledge(enhanced_query, n_results=5)
            
            # Prepare context from retrieved documents
            context = self._prepare_context(relevant_docs)
            
            # Generate response using watsonx
            response = self.watsonx_client.generate_response(query, context)
            
            return response, relevant_docs
            
        except Exception as e:
            logger.error(f"Error in retrieve_and_generate: {e}")
            return f"I apologize, but I encountered an error: {str(e)}", []
    
    def _enhance_query(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Enhance query with user context"""
        if not user_profile:
            return query
        
        location = user_profile.get('location', '')
        lifestyle = user_profile.get('lifestyle', '')
        
        enhanced = query
        if location:
            enhanced += f" in {location}"
        if lifestyle:
            enhanced += f" for {lifestyle} lifestyle"
        
        return enhanced
    
    def _prepare_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        
        for doc in relevant_docs:
            source = doc['metadata'].get('source', 'Unknown')
            title = doc['metadata'].get('title', 'Untitled')
            content = doc['content']
            
            context_parts.append(f"Source: {source} - {title}\n{content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "climate_knowledge",
                "embedding_model": settings.EMBEDDING_MODEL
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def initialize_with_sample_data(self):
        """Initialize the knowledge base with sample climate data"""
        sample_documents = [
            {
                "title": "Renewable Energy Transition",
                "content": """Renewable energy sources like solar, wind, and hydroelectric power are crucial for reducing greenhouse gas emissions. Solar panels can reduce household carbon footprint by 3-4 tons of CO2 per year. Wind energy is one of the fastest-growing renewable sources globally. The transition to renewable energy requires investment but provides long-term cost savings and environmental benefits. Government incentives and falling technology costs make renewable energy increasingly accessible to individuals and businesses.""",
                "source": "Climate Action Guide",
                "category": "energy"
            },
            {
                "title": "Sustainable Transportation",
                "content": """Transportation accounts for approximately 29% of greenhouse gas emissions in the United States. Electric vehicles can reduce emissions by 60-70% compared to gasoline vehicles. Public transportation, cycling, and walking are highly effective ways to reduce personal carbon footprint. Carpooling and ride-sharing can significantly reduce per-person emissions. For long-distance travel, trains are generally more environmentally friendly than planes or cars.""",
                "source": "EPA Transportation Guide",
                "category": "transportation"
            },
            {
                "title": "Energy Efficiency at Home",
                "content": """Home energy efficiency improvements can reduce energy consumption by 20-30%. LED lighting uses 75% less energy than incandescent bulbs. Proper insulation can reduce heating and cooling costs by up to 40%. Smart thermostats can save 10-15% on heating and cooling bills. Energy-efficient appliances with ENERGY STAR ratings use 10-50% less energy than standard models. Sealing air leaks around windows and doors is a cost-effective way to improve efficiency.""",
                "source": "Energy Efficiency Guide",
                "category": "energy_efficiency"
            },
            {
                "title": "Sustainable Food Choices",
                "content": """Food production accounts for about 26% of global greenhouse gas emissions. Plant-based diets can reduce food-related emissions by up to 73%. Reducing meat consumption, especially beef, has significant environmental impact. Local and seasonal food choices reduce transportation emissions. Reducing food waste is crucial - about 1/3 of food produced globally is wasted. Composting food scraps reduces methane emissions from landfills and creates valuable soil amendment.""",
                "source": "Sustainable Food Guide",
                "category": "food"
            },
            {
                "title": "Water Conservation",
                "content": """Water conservation reduces energy consumption for water treatment and distribution. Low-flow fixtures can reduce water usage by 20-60%. Fixing leaks promptly prevents waste - a single dripping faucet can waste over 3,000 gallons per year. Rainwater harvesting can reduce municipal water demand. Drought-resistant landscaping reduces irrigation needs. Shorter showers and full loads in dishwashers and washing machines maximize efficiency.""",
                "source": "Water Conservation Guide",
                "category": "water"
            },
            {
                "title": "Waste Reduction and Recycling",
                "content": """The waste sector contributes about 5% of global greenhouse gas emissions. Reducing, reusing, and recycling materials prevents emissions from manufacturing new products. Composting organic waste reduces methane emissions from landfills. Proper recycling of electronics prevents toxic materials from entering the environment. Choosing products with minimal packaging reduces waste. Buying durable, repairable products reduces long-term waste generation.""",
                "source": "Waste Management Guide",
                "category": "waste"
            }
        ]
        
        # Check if collection is empty
        if self.collection.count() == 0:
            logger.info("Initializing knowledge base with sample data...")
            self.add_documents(sample_documents)
            logger.info("Sample data added successfully")
        else:
            logger.info("Knowledge base already contains data")