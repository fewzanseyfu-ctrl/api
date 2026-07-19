import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application
import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a smart, friendly, and direct AI Assistant on Telegram. Keep your replies concise."
)

async def process_telegram_update(update_json):
    bot_token = os.environ.get("TELEGRAM_TOKEN")
    app = Application.builder().token(bot_token).build()
    
    # Process the update manually without continuous polling loops
    update = Update.de_json(update_json, app.bot)
    
    if update.message and update.message.text:
        user_text = update.message.text
        
        # Simple start command handling
        if user_text.startswith('/start'):
            await update.message.reply_text("Hello! 🤖 I am your brand new AI assistant. Ask me anything!")
            return
            
        try:
            response = model.generate_content(user_text)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text("Sorry, I hit an error thinking about that. Try again!")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_json = json.loads(post_data.decode('utf-8'))
        
        # Run the async telegram processing logic
        asyncio.run(process_telegram_update(update_json))
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot endpoint is active!")
