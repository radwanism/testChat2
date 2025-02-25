import os
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains import create_history_aware_retriever
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

class RAGChain:
    def __init__(self, api_key: str = None):
        """Initialize the RAG chain with Google API key."""
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        elif "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("Google API key is required")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        
        self.embedding = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.session_store = {}
        self.vectorstore = None
        self.conversational_rag_chain = None
        
    def load_pdfs(self, pdf_paths: List[str]) -> None:
        """Load PDF documents and create vector store."""
        docs = []
        for pdf_path in pdf_paths:
            loader = PyPDFLoader(pdf_path)
            docs.extend(loader.load())
            
        splits = self.text_splitter.split_documents(docs)
        
        self.vectorstore = FAISS.from_documents(documents=splits, embedding=self.embedding)
        retriever = MultiQueryRetriever.from_llm(
            retriever=self.vectorstore.as_retriever(), llm=self.llm
        )
        
        # Create history-aware retriever
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )
        
        # Create question-answering chain
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise. Make your response in the same language that the user asked with. "
            "Answer the user greeting in a friendly manner.\n\n"
            "{context}"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        # Setup stateful chat history
        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in self.session_store:
                self.session_store[session_id] = ChatMessageHistory()
            return self.session_store[session_id]
        
        self.conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
    
    def query(self, message: str, session_id: str) -> str:
        """Process a user message and return the response."""
        if not self.vectorstore or not self.conversational_rag_chain:
            return "Please load PDF documents first."
        
        response = self.conversational_rag_chain.invoke(
            {"input": message}, 
            config={"configurable": {"session_id": session_id}}
        )
        return response["answer"]
    
    def clear_session(self, session_id: str) -> None:
        """Clear the chat history for a specific session."""
        if session_id in self.session_store:
            self.session_store[session_id] = ChatMessageHistory()
            
    def clear_all_sessions(self) -> None:
        """Clear all chat histories."""
        self.session_store = {}