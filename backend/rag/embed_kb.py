import os
import sys

# Add backend directory to sys.path to allow imports from core
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from core.config import settings

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.rag import get_chroma_collection, generate_embedding
import uuid

def embed_knowledge_base():
    # 1. Get the absolute path to knowledge_base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    kb_dir = os.path.join(backend_dir, "knowledge_base")
    
    if not os.path.exists(kb_dir):
        raise FileNotFoundError(f"Knowledge base directory not found at: {kb_dir}")

    # 2. Load the documents
    print(f"Loading markdown documents from {kb_dir}...")
    loader = DirectoryLoader(kb_dir, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents.")
    
    # 3. Split the documents
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        separators=["\n## ", "\n### ", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 4. Initialize Chroma Collection
    print("Initializing ChromaDB collection...")
    collection = get_chroma_collection()

    # 5. Upload Chunks to ChromaDB
    print("Embedding and uploading chunks to ChromaDB...")
    
    # Prepare data for Chroma
    ids = []
    documents_list = []
    metadatas = []
    embeddings = []
    
    for i, chunk in enumerate(chunks):
        doc_id = str(uuid.uuid4())
        text = chunk.page_content
        metadata = chunk.metadata
        
        print(f"Generating embedding for chunk {i+1}/{len(chunks)}...")
        embedding = generate_embedding(text)
        
        ids.append(doc_id)
        documents_list.append(text)
        metadatas.append(metadata)
        embeddings.append(embedding)
        
    print(f"Adding {len(ids)} embedded chunks to ChromaDB collection `{settings.INDEX_NAME}`...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents_list
    )
    
    print("Success! Knowledge Base successfully embedded into ChromaDB!")

if __name__ == "__main__":
    embed_knowledge_base()
