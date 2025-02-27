# PDF RAG Chatbot

A Python-based application that uses AI/ML techniques to create a chatbot capable of answering user questions based on information extracted from PDF documents. The application enables users to upload documents and interact with the chatbot through multiple interfaces.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technologies Used](#-technologies-used)
- [Setup Instructions](#-setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running Locally](#running-locally)
  - [Running with Docker](#running-with-docker)
- [API Documentation](#-api-documentation)
- [User Interfaces](#-user-interfaces)
  - [Web Interface (Gradio)](#web-interface-gradio)
  - [API Interface](#api-interface)
  - [Telegram Bot](#telegram-bot)
- [Project Structure](#-project-structure)
- [Acknowledgments](#-acknowledgments)
- [Contributing](#-contributing)

## ✨ Features

- **PDF Document Processing**:
  - Upload and process multiple PDF documents
  - Extract text and create searchable vector embeddings
  - Store documents for future reference

- **Intelligent Chatbot**:
  - Answer questions based on the content of uploaded documents
  - Contextual awareness for follow-up questions
  - Support for multiple chat sessions

- **Multiple User Interfaces**:
  - Web-based UI using Gradio
  - RESTful API endpoints
  - Telegram bot integration

- **RAG (Retrieval Augmented Generation)**:
  - Uses Google's Gemini AI model for generation
  - FAISS vector database for efficient document retrieval
  - Context-aware responses with conversation history

## 🏗️ Architecture

The application follows a three-tier architecture:

1. **User Interfaces Layer**: Gradio web UI, FastAPI endpoints, and Telegram bot
2. **Application Logic Layer**: RAG chain, PDF processing, and chat session management
3. **Storage Layer**: Vector database storage and PDF file storage

## 🔧 Technologies Used

- **FastAPI**: Modern API framework for backend services
- **Gradio**: Simple web interface framework
- **LangChain**: Framework for building LLM applications
- **Google Generative AI**: Gemini model for text generation
- **FAISS**: Vector similarity search for document retrieval
- **PyTelegramBotAPI**: Telegram bot integration
- **PyPDF**: PDF processing library
- **Docker**: Containerization for easy deployment

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- Google API key for Gemini model
- Telegram Bot token (optional, for Telegram integration)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/radwanism/testChat2.git
   cd testChat2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the root directory with the following variables:
   ```
   GOOGLE_API_KEY=your_google_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token  # Optional, only if using Telegram
   ```

2. Ensure the `uploads` directory exists or will be created by the application:
   ```bash
   mkdir -p uploads
   ```

### Running Locally

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. Start the Gradio web interface:
   ```bash
   python gradio_app.py
   ```

3. (Optional) Start the Telegram bot:
   ```bash
   # The bot can be started by importing and running TelegramBot from the application
   ```


### Running with Docker

Build the Docker image:
```bash
docker build -t pdf-rag-chatbot .
```

Run the container with both API and Gradio:
```bash
docker run -p 8000:8000 -p 7860:7860 --env-file .env pdf-rag-chatbot
```

Or run only the API:
```bash
docker run -p 8000:8000 --env-file .env pdf-rag-chatbot api
```

Or run only Gradio:
```bash
docker run -p 7860:7860 --env-file .env pdf-rag-chatbot gradio
```


## API Endpoints

- POST /api/upload-pdfs: Upload PDF files
- GET /api/pdfs: Get list of available PDFs
- DELETE /api/pdfs/{filename}: Delete a specific PDF
- DELETE /api/pdfs: Delete all PDFs
- POST /api/chat: Chat with the loaded PDFs
- DELETE /api/chat/{session_id}: Clear chat history for a session


## 👥 User Interfaces

### Web Interface (Gradio)

The web interface provides a user-friendly way to interact with the chatbot and upload documents.

- **Access**: Navigate to `http://localhost:7860` in your web browser
- **Features**:
  - Upload multiple PDF files
  - Chat with the bot about the content
  - Clear conversation history
  - User-friendly interface

### API Interface

The API interface allows for programmatic access to the chatbot functionality.

- **Access**: Send HTTP requests to `http://localhost:8000`
- **Documentation**: Interactive API documentation available at `http://localhost:8000/docs`

### Telegram Bot

The Telegram bot allows users to interact with the chatbot through Telegram.

- **Setup**: Configure the Telegram bot token in the `.env` file
- **Start**: The bot will be started when the application runs

## 📁 Project Structure

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [Google Gemini](https://ai.google.dev/) for the AI models
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Gradio](https://gradio.app/) for the web interface
## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

