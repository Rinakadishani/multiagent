from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import os

class HealthcareDocumentLoader:
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_documents(self):
        print(f"Loading documents from {self.data_dir}...")
        
        loader = DirectoryLoader(
            self.data_dir,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        
        documents = loader.load()
        print(f"✓ Loaded {len(documents)} document pages")
        return documents
    
    def split_documents(self, documents):
        print("Splitting documents into chunks...")
        
        chunks = self.text_splitter.split_documents(documents)
        
        for idx, chunk in enumerate(chunks):
            chunk.metadata['chunk_id'] = f"chunk_{idx:04d}"
            
            source = chunk.metadata.get('source', '')
            chunk.metadata['doc_name'] = Path(source).stem
        
        print(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    def process_all(self):
        """Load and split all documents"""
        docs = self.load_documents()
        chunks = self.split_documents(docs)
        
        print(f"\nSummary:")
        print(f"   Total pages: {len(docs)}")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Avg chunks per page: {len(chunks)/len(docs):.1f}")
        
        return chunks


if __name__ == "__main__":
    loader = HealthcareDocumentLoader()
    chunks = loader.process_all()
    

    if chunks:
        print(f"\n Sample chunk:")
        print(f"   Document: {chunks[0].metadata['doc_name']}")
        print(f"   Page: {chunks[0].metadata.get('page', 'N/A')}")
        print(f"   Chunk ID: {chunks[0].metadata['chunk_id']}")
        print(f"   Content: {chunks[0].page_content[:200]}...")