import os
import gradio as gr
import uuid
from dotenv import load_dotenv

# Import the RAG chain implementation
from app.bot.rag_chain import RAGChain

# Load environment variables
load_dotenv()

# Initialize RAG chain with API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
rag_chain = RAGChain(api_key=api_key)

# Dictionary to store chat sessions
chat_sessions = {}

def process_pdfs(pdf_files):
    """Process uploaded PDF files."""
    if not pdf_files:
        return "No PDF files uploaded"
        
    # Save PDFs to temporary directory
    pdf_paths = [pdf_file.name for pdf_file in pdf_files]
    
    # Load PDFs into RAG chain
    rag_chain.load_pdfs(pdf_paths)
    
    return f"Processed {len(pdf_paths)} PDF files: {', '.join(os.path.basename(path) for path in pdf_paths)}"

def respond(message, chat_history, session_id):
    """Stream response while updating chat history."""
    if not session_id:
        session_id = str(uuid.uuid4())

    chat_history.append((message, ""))  # Append user message with empty bot response
    
    response_generator = rag_chain.query(message, session_id)  # Streaming response
    
    bot_response = ""
    for chunk in response_generator:
        bot_response += chunk
        chat_history[-1] = (message, bot_response)  # Update chat history in real-time
        yield "", chat_history, session_id  # Stream response updates

def clear_chat(chat_history, session_id):
    """Clear the chat history for the current session."""
    if session_id:
        rag_chain.clear_session(session_id)
    return [], session_id

# Create Gradio interface
with gr.Blocks(title="PDF RAG Chatbot") as demo:
    gr.Markdown("# 📚 PDF RAG Chatbot")
    gr.Markdown("Upload PDF files and chat with them using RAG (Retrieval Augmented Generation)")
    
    with gr.Row():
        with gr.Column(scale=2):
            # PDF upload section
            pdf_files = gr.File(
                label="Upload PDF Files",
                file_types=[".pdf"],
                file_count="multiple"
            )
            upload_button = gr.Button("Process PDFs")
            pdf_status = gr.Textbox(label="Upload Status", interactive=False)
            
            # Connect the upload button
            upload_button.click(
                process_pdfs,
                inputs=[pdf_files],
                outputs=[pdf_status]
            )
            
        with gr.Column(scale=3):
            # Chat section
            session_id = gr.State("")
            chatbot = gr.Chatbot(label="Chat with your PDFs")  # Enable streaming
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your message",
                    placeholder="Ask something about your PDFs...",
                    scale=9
                )
                submit = gr.Button("Send", scale=1)
            
            clear = gr.Button("Clear chat")
            
            # Connect the chat components
            submit.click(
                respond,
                inputs=[msg, chatbot, session_id],
                outputs=[msg, chatbot, session_id]
            )
            
            msg.submit(
                respond,
                inputs=[msg, chatbot, session_id],
                outputs=[msg, chatbot, session_id]
            )
            
            clear.click(
                clear_chat,
                inputs=[chatbot, session_id],
                outputs=[chatbot, session_id]
            )
    
    gr.Markdown("## How to use")
    gr.Markdown("""
    1. Upload one or more PDF files using the upload section
    2. Click "Process PDFs" to load them into the system
    3. Start chatting with your documents in the chat section
    4. Click "Clear chat" to start a new conversation
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
