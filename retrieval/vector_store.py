from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()

class HealthcareVectorStore:
    
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        # Use free local embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document]):
        print(f"Creating vector store with {len(documents)} documents...")
        print("Using local embeddings (this may take a few minutes)...")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="healthcare_docs"
        )
        
        print(f"✓ Vector store created and saved to {self.persist_directory}")
        return self.vectorstore
    
    def load_vectorstore(self):
        if os.path.exists(self.persist_directory):
            print(f"Loading existing vector store from {self.persist_directory}...")
            
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="healthcare_docs"
            )
            
            print("✓ Vector store loaded")
            return self.vectorstore
        else:
            raise FileNotFoundError(
                f"Vector store not found at {self.persist_directory}. "
                "Create it first using create_vectorstore()."
            )
    
    def similarity_search(self, query: str, k: int = 5):
        if not self.vectorstore:
            self.load_vectorstore()
        
        print(f"Searching for: '{query}'")
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        print(f"✓ Found {len(results)} results")
        return results


if __name__ == "__main__":
    from document_loader import HealthcareDocumentLoader
    
    print("=" * 80)
    print("VECTOR STORE SETUP")
    print("=" * 80)
    
    loader = HealthcareDocumentLoader()
    chunks = loader.process_all()
    
    print("\n" + "=" * 80)
    vs = HealthcareVectorStore()
    vs.create_vectorstore(chunks)
    
    print("\n" + "=" * 80)
    print("TESTING SEARCH")
    print("=" * 80)
    
    results = vs.similarity_search("diabetes treatment options", k=3)
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Similarity Score: {score:.3f}")
        print(f"   Source: {doc.metadata['doc_name']}")
        print(f"   Page: {doc.metadata.get('page', 'N/A')}")
        print(f"   Chunk: {doc.metadata['chunk_id']}")
        print(f"   Preview: {doc.page_content[:150]}...")
    
    print("\n" + "=" * 80)
    print("✓ SETUP COMPLETE!")
    print("=" * 80)
