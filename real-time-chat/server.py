# WebSocket Chat Server with Gemini AI and Memory
# server.py

import asyncio
import websockets
import json
import google.generativeai as genai
import os
from datetime import datetime
from collections import defaultdict, deque

# Configure Gemini AI
# Set your API key as an environment variable: export GOOGLE_API_KEY="your_api_key_here"
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Store connected clients
connected_clients = set()

# AI Memory - stores conversation history
# Using deque with maxlen to limit memory usage
conversation_memory = deque(maxlen=50)  # Keep last 50 messages for context
user_context = defaultdict(lambda: deque(maxlen=10))  # Per-user context

class AIMemory:
    def __init__(self):
        self.global_memory = deque(maxlen=50)
        self.user_memories = defaultdict(lambda: deque(maxlen=10))
    
    def add_message(self, username, message, is_ai=False):
        """Add a message to memory"""
        entry = {
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "is_ai": is_ai
        }
        
        # Add to global memory
        self.global_memory.append(entry)
        
        # Add to user-specific memory if not AI
        if not is_ai:
            self.user_memories[username].append(entry)
    
    def get_context_for_user(self, username, message):
        """Get relevant context for generating AI response"""
        context_messages = []
        
        # Get recent global conversation (last 10 messages)
        recent_global = list(self.global_memory)[-10:]
        
        # Get user's recent messages
        user_history = list(self.user_memories[username])[-5:]
        
        # Build context string
        context = "Recent conversation context:\n"
        
        for msg in recent_global:
            speaker = "AI Assistant" if msg["is_ai"] else msg["username"]
            context += f"{speaker}: {msg['message']}\n"
        
        if user_history:
            context += f"\n{username}'s recent messages:\n"
            for msg in user_history:
                context += f"{msg['message']}\n"
        
        return context
    
    def clear_memory(self):
        """Clear all memory"""
        self.global_memory.clear()
        self.user_memories.clear()

# Initialize AI memory
ai_memory = AIMemory()

async def generate_ai_response(message, username):
    """Generate AI response using Gemini with memory context"""
    try:
        # Remove @ai from the message for processing
        clean_message = message.replace("@ai", "").strip()
        
        # Get conversation context
        context = ai_memory.get_context_for_user(username, clean_message)
        
        # Create a comprehensive prompt with context
        prompt = f"""You are a helpful AI assistant in a chat room. You have memory of recent conversations.

{context}

Current user '{username}' is asking: "{clean_message}"

Please provide a helpful, friendly, and conversational response. Keep it concise but engaging.
Use the conversation context to provide more relevant and personalized responses.
If this is a follow-up to a previous conversation, acknowledge that context.
"""
        
        # Generate response
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: model.generate_content(prompt)
        )
        
        ai_response = response.text.strip()
        
        # Add AI response to memory
        ai_memory.add_message("AI Assistant", ai_response, is_ai=True)
        
        return ai_response
        
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Sorry, I'm having trouble processing your request right now."

async def handle_client(websocket):
    """Handle a new client connection"""
    # Add client to connected clients
    connected_clients.add(websocket)
    print(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "message": "Welcome to the AI-powered chat! Use @ai to ask questions or get help from the AI assistant. Example: '@ai What is Python?'",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_msg))
        
        # Listen for messages from this client
        async for message in websocket:
            try:
                # Parse the received message
                data = json.loads(message)
                username = data.get("username", "Anonymous")
                user_message = data.get("message", "")
                
                # Add user message to memory
                ai_memory.add_message(username, user_message, is_ai=False)
                
                # Create user message for broadcasting
                user_broadcast_msg = {
                    "type": "message",
                    "username": username,
                    "message": user_message,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"Broadcasting user message: {user_broadcast_msg}")
                
                # Broadcast user message to all connected clients
                await broadcast_message(json.dumps(user_broadcast_msg))
                
                # Check if message contains @ai
                if "@ai" in user_message.lower():
                    print(f"AI trigger detected in message: {user_message}")
                    
                    # Generate AI response
                    ai_response = await generate_ai_response(user_message, username)
                    
                    if ai_response:
                        ai_broadcast_msg = {
                            "type": "message",
                            "username": "AI Assistant",
                            "message": ai_response,
                            "timestamp": datetime.now().isoformat(),
                            "is_ai": True
                        }
                        
                        print(f"Broadcasting AI response: {ai_broadcast_msg}")
                        
                        # Small delay before AI response for more natural feel
                        await asyncio.sleep(1)
                        await broadcast_message(json.dumps(ai_broadcast_msg))
                
                # Handle special commands
                if user_message.lower().strip() == "@ai clear memory":
                    ai_memory.clear_memory()
                    system_msg = {
                        "type": "system",
                        "message": "AI memory has been cleared.",
                        "timestamp": datetime.now().isoformat()
                    }
                    await broadcast_message(json.dumps(system_msg))
                
            except json.JSONDecodeError:
                error_msg = {
                    "type": "error",
                    "message": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(error_msg))
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove client from connected clients
        connected_clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")

async def broadcast_message(message):
    """Broadcast message to all connected clients"""
    if connected_clients:
        # Create a list of tasks to send message to all clients
        tasks = []
        for client in connected_clients.copy():
            try:
                tasks.append(client.send(message))
            except websockets.exceptions.ConnectionClosed:
                connected_clients.discard(client)
        
        # Execute all send operations concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    """Main function to start the server"""
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("ERROR: Please set your Google API key as an environment variable:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return
    
    print("Starting AI-powered WebSocket chat server with memory on localhost:8765")
    print("AI will respond only when @ai is mentioned in messages")
    
    # Start the server
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server is running with Gemini AI integration and memory... Press Ctrl+C to stop")
        print("\nCommands:")
        print("- Use '@ai <question>' to ask the AI")
        print("- Use '@ai clear memory' to reset AI memory")
        # Keep the server running forever
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
