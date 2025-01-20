import socket
import threading
import json

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        
        # Setup discovery socket
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.discovery_socket.bind(('', 5556))
        
        self.server_name = socket.gethostname()
        
        # Start discovery listener
        discovery_thread = threading.Thread(target=self.handle_discovery)
        discovery_thread.daemon = True
        discovery_thread.start()
        
        self.clients = {}  # {client_socket: (username, current_room)}
        self.rooms = {
            'General': {
                'password': None, 
                'members': set(),
                'owner': None,
                'background': None
            }
        }
        
        # Get and display the server's local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Server running on:")
        print(f"Local IP: {local_ip}:{port}")
        print(f"Hostname: {hostname}")
        print("\nShare one of these addresses with clients to connect.")
        print("If connecting from the same network, use the Local IP.")
        print("Note: You may need to configure your firewall to allow connections on port 5555")
        
    def broadcast(self, message, room, sender_socket=None):
        for client_socket, (_, client_room) in self.clients.items():
            if client_room == room and client_socket != sender_socket:
                try:
                    client_socket.send(json.dumps(message).encode())
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")  # Debug print
                    self.remove_client(client_socket)

    def handle_client(self, client_socket, address):
        print(f"New connection from {address}")  # Debug print
        try:
            # Set timeout for initial connection
            client_socket.settimeout(10)
            
            # Receive username
            data = client_socket.recv(1024).decode()
            print(f"Received initial data from {address}: {data}")  # Debug print
            
            username_data = json.loads(data)
            if not username_data or username_data.get('type') != 'username':
                print(f"Invalid initial message from {address}")  # Debug print
                return
                
            username = username_data.get('username')
            print(f"User {username} connected from {address}")  # Debug print
            
            # Remove timeout after initial connection
            client_socket.settimeout(None)
            
            # Add client to tracking
            self.clients[client_socket] = (username, 'General')
            self.rooms['General']['members'].add(client_socket)
            
            # Send initial room list
            try:
                room_list = {
                    'type': 'room_list',
                    'rooms': list(self.rooms.keys()),
                    'protected_rooms': [room for room, info in self.rooms.items() if info.get('password')]
                }
                client_socket.send(json.dumps(room_list).encode())
                print(f"Sent initial room list to {username}")  # Debug print
            except Exception as e:
                print(f"Error sending initial room list to {username}: {e}")  # Debug print
                return
            
            # Send welcome message
            welcome = {
                'type': 'message',
                'sender': 'Server',
                'content': f'{username} joined the chat',
                'room': 'General'
            }
            self.broadcast(welcome, 'General')
            
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        print(f"Client {username} disconnected")  # Debug print
                        break
                    
                    message_data = json.loads(data)
                    print(f"Received {message_data['type']} from {username}")  # Debug print
                    
                    message_type = message_data.get('type')
                    
                    if message_type == 'message':
                        current_room = self.clients[client_socket][1]
                        self.broadcast(message_data, current_room)
                    
                    elif message_type == 'room_background':
                        room = message_data.get('room')
                        if room in self.rooms and self.rooms[room]['owner'] == username:
                            self.rooms[room]['background'] = message_data.get('color')
                            self.broadcast(message_data, room)
                    
                    elif message_type == 'create_room':
                        room_name = message_data.get('room')
                        password = message_data.get('password')
                        
                        if room_name not in self.rooms:
                            self.rooms[room_name] = {
                                'password': password,
                                'members': set(),
                                'owner': username,
                                'background': None
                            }
                            response = {
                                'type': 'room_created',
                                'success': True,
                                'room': room_name
                            }
                            # Broadcast updated room list to all clients
                            self.broadcast_room_list()
                        else:
                            response = {
                                'type': 'room_created',
                                'success': False,
                                'message': 'Room already exists'
                            }
                        client_socket.send(json.dumps(response).encode())
                    
                    elif message_type == 'join_room':
                        new_room = message_data.get('room')
                        provided_password = message_data.get('password')
                        
                        if new_room in self.rooms:
                            room_password = self.rooms[new_room]['password']
                            if room_password is None or room_password == provided_password:
                                # Remove from old room
                                old_room = self.clients[client_socket][1]
                                self.rooms[old_room]['members'].remove(client_socket)
                                
                                # Add to new room
                                self.rooms[new_room]['members'].add(client_socket)
                                self.clients[client_socket] = (username, new_room)
                                
                                response = {
                                    'type': 'room_joined',
                                    'success': True,
                                    'room': new_room
                                }
                                
                                # Notify room changes
                                change_message = {
                                    'type': 'message',
                                    'sender': 'Server',
                                    'content': f'{username} moved to {new_room}',
                                    'room': new_room
                                }
                                self.broadcast(change_message, new_room)
                            else:
                                response = {
                                    'type': 'room_joined',
                                    'success': False,
                                    'message': 'Incorrect password'
                                }
                        else:
                            response = {
                                'type': 'room_joined',
                                'success': False,
                                'message': 'Room does not exist'
                            }
                        client_socket.send(json.dumps(response).encode())
                        
                except json.JSONDecodeError as e:
                    print(f"JSON decode error from {username}: {e}")  # Debug print
                    break
                except Exception as e:
                    print(f"Error handling message from {username}: {e}")  # Debug print
                    break
                    
        except Exception as e:
            print(f"Error in handle_client: {e}")  # Debug print
        finally:
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            username, room = self.clients[client_socket]
            leave_message = {
                'type': 'message',
                'sender': 'Server',
                'content': f'{username} left the chat',
                'room': room
            }
            self.rooms[room]['members'].remove(client_socket)
            del self.clients[client_socket]
            self.broadcast(leave_message, room)
            client_socket.close()

    def broadcast_room_list(self):
        """Send updated room list to all clients"""
        room_list = {
            'type': 'room_list',
            'rooms': list(self.rooms.keys()),
            'protected_rooms': [room for room, info in self.rooms.items() if info.get('password')]
        }
        # Send to all connected clients
        for client_socket in self.clients:
            try:
                client_socket.send(json.dumps(room_list).encode())
            except Exception as e:
                print(f"Error broadcasting room list to client: {e}")  # Debug print
                pass

    def handle_discovery(self):
        while True:
            try:
                data, addr = self.discovery_socket.recvfrom(1024)
                if data == b"CHAT_DISCOVER":
                    # Send server info
                    server_info = {
                        "name": self.server_name,
                        "users": len(self.clients),
                        "rooms": len(self.rooms)
                    }
                    self.discovery_socket.sendto(
                        json.dumps(server_info).encode(),
                        addr
                    )
            except Exception as e:
                print(f"Discovery error: {e}")
                continue

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    print("Chat server started. Press Ctrl+C to stop.")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")