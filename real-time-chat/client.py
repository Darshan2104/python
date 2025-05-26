# WebSocket Chat Client
# client.py

import asyncio
import websockets
import json
import threading
import sys

class ChatClient:
    def __init__(self, username="Anonymous"):
        self.username = username
        self.websocket = None
        self.running = False

    async def connect(self, uri="ws://localhost:8765"):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(uri)
            self.running = True
            print(f"Connected to chat server as '{self.username}'")
            print("Type your messages and press Enter. Type 'quit' to exit.\n")
            
            # Start listening for messages
            await asyncio.gather(
                self.listen_for_messages(),
                self.send_messages()
            )
            
        except Exception as e:
            print(f"Failed to connect: {e}")

    async def listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                self.display_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server")
            self.running = False
        except Exception as e:
            print(f"Error receiving message: {e}")
            self.running = False

    async def send_messages(self):
        """Handle sending messages"""
        while self.running:
            try:
                # Get user input (this is a simplified approach)
                message = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )
                
                if message.lower() == 'quit':
                    self.running = False
                    break
                
                if message.strip():
                    msg_data = {
                        "username": self.username,
                        "message": message
                    }
                    await self.websocket.send(json.dumps(msg_data))
                    
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error sending message: {e}")
                break

    def display_message(self, data):
        """Display received message"""
        msg_type = data.get("type", "")
        
        if msg_type == "system":
            print(f"[SYSTEM] {data.get('message', '')}")
        elif msg_type == "message":
            username = data.get("username", "Unknown")
            message = data.get("message", "")
            is_ai = data.get("is_ai", False)
            
            # Don't display our own messages
            if username != self.username:
                if is_ai:
                    print(f"🤖 [AI Assistant] {message}")
                else:
                    print(f"[{username}] {message}")
        elif msg_type == "error":
            print(f"[ERROR] {data.get('message', '')}")

    async def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()

def main():
    # Get username from user
    username = input("Enter your username: ").strip()
    if not username:
        username = "Anonymous"
    
    print("\nChat Commands:")
    print("- Use '@ai <question>' to ask the AI assistant")
    print("- Use '@ai clear memory' to reset AI memory")
    print("- Type 'quit' to exit")
    print("=" * 50)
    
    # Create and run client
    client = ChatClient(username)
    
    try:
        asyncio.run(client.connect())
    except KeyboardInterrupt:
        print("\nExiting chat...")
    except Exception as e:
        print(f"Client error: {e}")

if __name__ == "__main__":
    main()