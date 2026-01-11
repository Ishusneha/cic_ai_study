import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()


class RAGPipeline:
    def __init__(self):
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.llm_model = os.getenv("LLM_MODEL", "llama3.2:latest")
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Initialize embeddings - use local embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model
        )
        
        # Initialize LLM with Ollama
        self.llm = ChatOllama(
            model=self.llm_model,
            temperature=0.7,
            base_url=self.ollama_base_url
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize vector store
        self.vector_store = None
        self._load_vector_store()
    
    def _load_vector_store(self):
        """Load or create the Chroma vector store"""
        try:
            embedding_function = HuggingFaceEmbeddings(model_name=self.embedding_model)
            
            self.vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=embedding_function,
            )
        except Exception as e:
            print(f"Error loading vector store: {e}")
            # Create new vector store if it doesn't exist
            embedding_function = HuggingFaceEmbeddings(model_name=self.embedding_model)
            
            self.vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=embedding_function,
            )
    
    def load_document(self, file_path: str, file_type: str) -> List[Document]:
        """Load document based on file type"""
        try:
            if file_type == "pdf":
                loader = PyPDFLoader(file_path)
            elif file_type == "txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif file_type == "docx":
                loader = Docx2txtLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            documents = loader.load()
            return documents
        except Exception as e:
            raise Exception(f"Error loading document: {str(e)}")
    
    def process_and_index_documents(self, file_path: str, file_type: str, metadata: Dict[str, Any] = None):
        """Process document, chunk it, and add to vector store"""
        # Load document
        documents = self.load_document(file_path, file_type)
        
        # Add metadata
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        if self.vector_store is None:
            self._load_vector_store()
        
        self.vector_store.add_documents(chunks)
        # Note: Chroma 0.4.x automatically persists, no need to call persist()
        
        return len(chunks)
    
    def answer_question(self, question: str, k: int = 4) -> Dict[str, Any]:
        """Answer a question using RAG"""
        if self.vector_store is None:
            return {
                "answer": "No documents have been uploaded yet. Please upload study materials first.",
                "sources": []
            }
        
        # Create retrieval chain
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        # Create prompt template
        prompt_template = """You are an AI study assistant helping students understand their study materials.

Use the following pieces of context from the student's uploaded documents to answer the question.
If you don't know the answer based on the provided context, say that you don't know. 
Do not make up information that is not in the context.

Context:
{context}

Question: {input}

Provide a clear, detailed answer based only on the context provided:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Create QA chain
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        
        # Create document chain
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # Create retrieval chain
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        # Get answer
        result = retrieval_chain.invoke({"input": question})
        
        # Extract sources - get documents from retriever
        sources = []
        retrieved_docs = retriever.get_relevant_documents(question)
        for doc in retrieved_docs[:3]:  # Limit to top 3 sources
            source_info = {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
            }
            sources.append(source_info)
        
        return {
            "answer": result.get("answer", "No answer generated"),
            "sources": sources
        }
    
    def get_relevant_chunks(self, query: str, k: int = 10) -> List[Document]:
        """Get relevant document chunks for a query"""
        if self.vector_store is None:
            return []
        
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        return retriever.get_relevant_documents(query)
    
    def clear_vector_store(self):
        """Clear all documents from the vector store"""
        # Delete the persistent directory
        import shutil
        if os.path.exists(self.vector_store_path):
            shutil.rmtree(self.vector_store_path)
        
        # Recreate vector store
        self._load_vector_store()

