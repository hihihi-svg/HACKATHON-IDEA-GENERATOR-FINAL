import docx2txt
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import streamlit as st
import os

def create_vector_db(docx_path, persist_directory="vectorstore/chroma_db"):
    """
    Creates a vector database from a DOCX file using LangChain and Chroma.
    """
    try:
        # 1. Extract text from DOCX
        text = docx2txt.process(docx_path)
        
        if not text or len(text.strip()) == 0:
            st.error("❌ No text found in the document.")
            return None
        
        # 2. Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_text(text)
        
        if not chunks:
            st.error("❌ No chunks created from the document.")
            return None
        
        st.info(f"📄 Processing {len(chunks)} text chunks...")
        
        # 3. Create embeddings (using lightweight model)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},  # Use CPU for compatibility
            encode_kwargs={'normalize_embeddings': True}  # Normalize for better similarity
        )
        
        # 4. Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # 5. Store in Chroma vector DB
        vectordb = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="hackathon_topics"
        )
        
        # Note: .persist() is deprecated in newer Chroma versions
        # Data is automatically persisted when persist_directory is specified
        
        st.success(f"✅ Vector database created with {len(chunks)} chunks!")
        return vectordb
    
    except Exception as e:
        st.error(f"❌ Error creating vector database: {str(e)}")
        return None


def retrieve_relevant_topics(query, persist_directory="vectorstore/chroma_db", top_k=5):
    """
    Retrieves the most relevant topics from the vector database based on the query.
    """
    try:
        # Check if vector database exists
        if not os.path.exists(persist_directory):
            st.warning("⚠️ Vector database not found. Please upload topics and create the database first.")
            return []
        
        # Load embeddings model
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load existing vector database
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name="hackathon_topics"
        )
        
        # Perform similarity search
        results = vectordb.similarity_search(query, k=top_k)
        
        # Extract and return relevant content
        relevant_topics = [result.page_content for result in results]
        
        return relevant_topics
    
    except Exception as e:
        st.error(f"❌ Error retrieving topics: {str(e)}")
        return []


def retrieve_relevant_topics_with_scores(query, persist_directory="vectorstore/chroma_db", top_k=5):
    """
    Retrieves relevant topics along with their similarity scores.
    Useful for debugging or displaying confidence levels.
    """
    try:
        if not os.path.exists(persist_directory):
            st.warning("⚠️ Vector database not found.")
            return []
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name="hackathon_topics"
        )
        
        # Get results with scores
        results_with_scores = vectordb.similarity_search_with_score(query, k=top_k)
        
        # Format results
        formatted_results = [
            {
                "content": doc.page_content,
                "score": score
            }
            for doc, score in results_with_scores
        ]
        
        return formatted_results
    
    except Exception as e:
        st.error(f"❌ Error retrieving topics with scores: {str(e)}")
        return []