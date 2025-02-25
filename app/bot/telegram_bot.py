import os
import threading
import telebot
from telebot.types import Message
from dotenv import load_dotenv

from app.bot.rag_chain import RAGChain

class TelegramBot:
    def __init__(self, rag_chain: RAGChain = None, token: str = None):
        """Initialize the Telegram bot with a RAG chain."""
        load_dotenv()
        
        # Get the token from environment or parameter
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not self.token:
            raise ValueError("Telegram bot token is required")
            
        self.bot = telebot.TeleBot(self.token)
        self.rag_chain = rag_chain or RAGChain()
        self.stop_flag = threading.Event()
        self.thread = None
        
        # Set up message handler
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message: Message):
            if self.stop_flag.is_set():
                return
                
            session_id = str(message.chat.id)  # Use chat ID as session identifier
            user_input = message.text
            
            response = self.rag_chain.query(user_input, session_id)
            self.bot.send_message(message.chat.id, response)
    
    def start(self):
        """Start the Telegram bot."""
        if self.thread and self.thread.is_alive():
            return  # Bot is already running
            
        print("Telegram bot is running...")
        self.stop_flag.clear()
        self.thread = threading.Thread(
            target=self.bot.polling, 
            kwargs={"none_stop": True}
        )
        self.thread.start()
        
    def stop(self):
        """Stop the Telegram bot."""
        if not self.thread or not self.thread.is_alive():
            return  # Bot is not running
            
        self.stop_flag.set()
        if self.thread:
            self.thread.join(timeout=5)
        print("Telegram bot stopped.")
        
    def set_rag_chain(self, rag_chain: RAGChain):
        """Set or update the RAG chain."""
        self.rag_chain = rag_chain