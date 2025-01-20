import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import sys
import time
import tkinter.font as tkFont

def main():
    try:
        # Create server discovery window
        discovery_window = tk.Tk()
        discovery_window.title("Connect to Server")
        discovery_window.geometry("400x300")
        
        frame = tk.Frame(discovery_window)
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(frame, text="Available Servers:", font=('Helvetica', 12)).pack(pady=(0, 10))
        
        # Available servers list
        servers_frame = tk.Frame(frame)
        servers_frame.pack(fill='both', expand=True)
        
        servers_list = tk.Listbox(servers_frame, width=40, height=8, font=('Helvetica', 10))
        servers_list.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(servers_frame, orient="vertical", command=servers_list.yview)
        scrollbar.pack(side='right', fill='y')
        
        servers_list.configure(yscrollcommand=scrollbar.set)
        
        # Manual IP entry
        entry_frame = tk.Frame(frame)
        entry_frame.pack(fill='x', pady=10)
        
        tk.Label(entry_frame, text="Or enter IP manually:").pack(side='left')
        ip_entry = tk.Entry(entry_frame)
        ip_entry.pack(side='left', padx=5, fill='x', expand=True)
        ip_entry.insert(0, "localhost")
        
        # Dictionary to store server info
        available_servers = {}
        
        def refresh_servers():
            # Clear existing servers
            servers_list.delete(0, tk.END)
            available_servers.clear()
            
            # Create UDP socket for discovery
            discover_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            discover_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            discover_socket.settimeout(1)
            
            # Broadcast discovery message
            discover_socket.sendto(b"CHAT_DISCOVER", ('<broadcast>', 5556))
            
            # Wait for responses
            start_time = time.time()
            while time.time() - start_time < 2:  # Search for 2 seconds
                try:
                    data, addr = discover_socket.recvfrom(1024)
                    try:
                        server_info = json.loads(data.decode())
                        server_name = f"{server_info['name']} ({addr[0]}) - Users: {server_info['users']}"
                        available_servers[server_name] = addr[0]
                        servers_list.insert(tk.END, server_name)
                    except:
                        pass
                except socket.timeout:
                    continue
            
            discover_socket.close()
            
            if not available_servers:
                servers_list.insert(tk.END, "No servers found")
        
        def on_server_select(event):
            selection = servers_list.get(servers_list.curselection())
            if selection in available_servers:
                ip_entry.delete(0, tk.END)
                ip_entry.insert(0, available_servers[selection])
        
        def connect():
            server_ip = ip_entry.get().strip()
            if server_ip:
                discovery_window.destroy()
                client = ChatClient()
                client.connect_to_server(server_ip, 5555)
        
        # Bind server selection
        servers_list.bind('<<ListboxSelect>>', on_server_select)
        
        # Add buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(fill='x', pady=10)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=refresh_servers)
        refresh_btn.pack(side='left', padx=5)
        
        connect_btn = ttk.Button(button_frame, text="Connect", command=connect)
        connect_btn.pack(side='right', padx=5)
        
        # Initial server search
        refresh_servers()
        
        discovery_window.mainloop()
        
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

class Settings:
    def __init__(self, client):
        self.client = client
        self.dark_mode = False
        self.font_size = 10
        self.font_family = "Arial"  # Add default font family
        self.chat_bg = "white"
        self.themes = {
            "light": {
                "bg": "white",
                "fg": "black",
                "my_message": "blue",
                "other_message": "black",
                "server_message": "gray",
                "input_bg": "white",
                "button_bg": "#f0f0f0",
                "frame_bg": "#f0f0f0",
                "entry_bg": "white",
                "entry_fg": "black",
                "chat_bg": "white",
                "menu_bg": "white",
                "menu_fg": "black",
                "scrollbar_bg": "#f0f0f0",
                "scrollbar_fg": "#c1c1c1"
            },
            "dark": {
                "bg": "#1a1a1a",         # Darker background
                "fg": "#ffffff",
                "my_message": "#7cb4f5",
                "other_message": "#e0e0e0",
                "server_message": "#808080",
                "input_bg": "#2d2d2d",
                "button_bg": "#2d2d2d",   # Darker buttons
                "frame_bg": "#1a1a1a",    # Darker frames
                "entry_bg": "#2d2d2d",
                "entry_fg": "#ffffff",
                "chat_bg": "#1a1a1a",     # Darker chat background
                "menu_bg": "#1a1a1a",     # Darker menu
                "menu_fg": "#ffffff",
                "scrollbar_bg": "#2d2d2d", # Darker scrollbar
                "scrollbar_fg": "#404040"  # Scrollbar thumb
            }
        }

    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        theme = self.themes["dark" if self.dark_mode else "light"]
        self.client.current_theme = theme  # Update current theme
        
        # Configure root window
        self.client.root.configure(bg=theme["bg"])
        
        # Update all widgets recursively
        def update_widget_colors(widget):
            try:
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=theme["bg"])
                
                elif isinstance(widget, tk.Label):
                    widget.configure(bg=theme["bg"], fg=theme["fg"])
                
                elif isinstance(widget, tk.Entry):
                    widget.configure(
                        bg=theme["entry_bg"],
                        fg=theme["entry_fg"],
                        insertbackground=theme["fg"],
                        selectbackground=theme["button_bg"],
                        selectforeground=theme["fg"]
                    )
                
                elif isinstance(widget, tk.Button):
                    widget.configure(
                        bg=theme["button_bg"],
                        fg=theme["fg"],
                        activebackground=theme["input_bg"],
                        activeforeground=theme["fg"]
                    )
                
                elif isinstance(widget, scrolledtext.ScrolledText):
                    widget.configure(
                        bg=theme["chat_bg"],
                        fg=theme["fg"],
                        insertbackground=theme["fg"],
                        selectbackground=theme["button_bg"],
                        selectforeground=theme["fg"]
                    )
                    # Configure scrollbar colors
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Scrollbar):
                            child.configure(
                                bg=theme["scrollbar_bg"],
                                activebackground=theme["scrollbar_bg"],
                                troughcolor=theme["bg"]
                            )
                
                elif isinstance(widget, tk.Menu):
                    widget.configure(
                        bg=theme["menu_bg"],
                        fg=theme["menu_fg"],
                        activebackground=theme["button_bg"],
                        activeforeground=theme["fg"]
                    )
                
                # Recursively update all child widgets
                for child in widget.winfo_children():
                    update_widget_colors(child)
                    
            except:
                pass  # Skip widgets that don't support certain configurations
        
        # Update all widgets starting from root
        update_widget_colors(self.client.root)
        
        # Update all existing message tags
        for tag in self.client.chat_display.tag_names():
            if tag.startswith('msg_'):
                if 'right' in self.client.chat_display.tag_cget(tag, 'justify'):
                    self.client.chat_display.tag_config(tag, foreground=theme["my_message"])
                elif 'center' in self.client.chat_display.tag_cget(tag, 'justify'):
                    self.client.chat_display.tag_config(tag, foreground=theme["server_message"])
                else:
                    self.client.chat_display.tag_config(tag, foreground=theme["other_message"])
        
        # Update room buttons
        self.client.update_room_buttons()
        
        # Force update
        self.client.root.update_idletasks()

class ChatClient:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("Multi-Room Chat")
            self.root.geometry("600x800")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self.username = None
            self.current_room = "General"
            self.client_socket = None
            self.available_rooms = []
            self.room_passwords = {}
            self.protected_rooms = set()
            self.room_backgrounds = {"General": None}
            self.settings = Settings(self)  # Pass self reference to Settings
            
            # Set initial theme
            self.current_theme = self.settings.themes["light"]
            
            # Create clock
            self.clock_label = None
            
            self.setup_gui()
            self.update_clock()
        except Exception as e:
            print(f"Error initializing chat client: {e}")
            raise

    def on_closing(self):
        """Handle window closing"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.root.destroy()
        sys.exit(0)

    def setup_gui(self):
        # Get current theme
        theme = self.current_theme
        
        # Configure the main window
        self.root.configure(bg=theme["bg"])
        
        # Create main container frame
        main_frame = tk.Frame(self.root, bg=theme["bg"])
        main_frame.pack(expand=True, fill='both')
        
        # Add clock at the top
        self.clock_label = tk.Label(main_frame, font=('Helvetica', 12), 
                                  bg=theme["bg"],
                                  fg=theme["fg"])
        self.clock_label.pack(pady=5)
        
        # Add menu bar
        menubar = tk.Menu(self.root, bg=theme["menu_bg"], fg=theme["menu_fg"])
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0, bg=theme["menu_bg"], fg=theme["menu_fg"])
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_checkbutton(label="Dark Mode", command=self.settings.toggle_dark_mode)
        
        # Add Font submenu
        font_menu = tk.Menu(settings_menu, tearoff=0, bg=theme["menu_bg"], fg=theme["menu_fg"])
        settings_menu.add_cascade(label="Font", menu=font_menu)
        
        # Font size submenu
        font_menu.add_command(label="Size", command=self.change_font_size)
        
        # Font family submenu
        self.font_family_menu = tk.Menu(font_menu, tearoff=0, bg=theme["menu_bg"], fg=theme["menu_fg"])
        font_menu.add_cascade(label="Family", menu=self.font_family_menu)
        
        # Add import fonts option
        font_menu.add_command(label="Import System Fonts", command=self.import_system_fonts)
        
        # Add font options
        self.fonts = [
            "Arial",
            "Helvetica",
            "Times New Roman",
            "Courier New",
            "Verdana",
            "Tahoma",
            "Segoe UI",
            "Consolas"
        ]
        
        self.update_font_menu(self.font_family_menu)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=30,
                                                    bg=theme["chat_bg"], fg=theme["fg"],
                                                    insertbackground=theme["fg"],
                                                    selectbackground=theme["button_bg"],
                                                    selectforeground=theme["fg"])
        self.chat_display.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Configure message colors and tags
        self.chat_display.tag_config('my_message', foreground=theme["my_message"])
        self.chat_display.tag_config('other_message', foreground=theme["other_message"])
        self.chat_display.tag_config('server_message', foreground=theme["server_message"])
        
        # Room controls frame
        self.room_frame = tk.Frame(main_frame, bg=theme["bg"])
        self.room_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(self.room_frame, text="Room:", bg=theme["bg"], fg=theme["fg"]).pack(side=tk.LEFT)
        self.room_entry = tk.Entry(self.room_frame, width=15,
                                 bg=theme["entry_bg"], fg=theme["entry_fg"],
                                 insertbackground=theme["fg"])
        self.room_entry.pack(side=tk.LEFT, padx=5)
        self.room_entry.insert(0, "General")
        
        tk.Button(self.room_frame, text="Create Room", command=self.create_room,
                 bg=theme["button_bg"], fg=theme["fg"],
                 activebackground=theme["input_bg"],
                 activeforeground=theme["fg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(self.room_frame, text="Join Room", command=self.join_room,
                 bg=theme["button_bg"], fg=theme["fg"],
                 activebackground=theme["input_bg"],
                 activeforeground=theme["fg"]).pack(side=tk.LEFT)
        
        # Message input frame
        self.input_frame = tk.Frame(main_frame, bg=theme["bg"])
        self.input_frame.pack(fill='x', padx=5, pady=5)
        
        self.message_input = tk.Entry(self.input_frame,
                                    bg=theme["entry_bg"], fg=theme["entry_fg"],
                                    insertbackground=theme["fg"])
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
        tk.Button(self.input_frame, text="Send", command=self.send_message,
                 bg=theme["button_bg"], fg=theme["fg"],
                 activebackground=theme["input_bg"],
                 activeforeground=theme["fg"]).pack(side=tk.RIGHT)
        
        # Room buttons frame
        self.rooms_frame = tk.Frame(main_frame, bg=theme["bg"])
        self.rooms_frame.pack(fill='x', padx=5, pady=5)
        
        # Configure scrollbar colors
        for scrollbar in self.chat_display.winfo_children():
            if isinstance(scrollbar, tk.Scrollbar):
                scrollbar.configure(bg=theme["scrollbar_bg"], 
                                 activebackground=theme["scrollbar_bg"],
                                 troughcolor=theme["bg"])
        
        # Initial update of room buttons
        self.update_room_buttons()

    def update_room_buttons(self):
        """Update the room buttons display"""
        try:
            theme = self.settings.themes["dark" if self.settings.dark_mode else "light"]
            
            # Clear existing buttons
            for widget in self.rooms_frame.winfo_children():
                widget.destroy()
            
            # Create new buttons for each room
            for room in self.available_rooms:
                btn = tk.Button(
                    self.rooms_frame, 
                    text=room + (" 🔒" if room in self.protected_rooms else ""),
                    command=lambda r=room: self.quick_switch_room(r),
                    width=15,
                    bg=theme["button_bg"],
                    fg=theme["fg"],
                    activebackground=theme["input_bg"],
                    activeforeground=theme["fg"],
                    state='disabled' if room == self.current_room else 'normal'
                )
                btn.pack(side=tk.LEFT, padx=2, pady=2)
            
            # Force update the frame
            self.rooms_frame.update()
        except Exception as e:
            print(f"Error updating room buttons: {e}")

    def create_room(self):
        room_name = self.room_entry.get().strip()
        if room_name:
            if messagebox.askyesno("Password Protection", "Do you want to add a password to this room?"):
                password_window = tk.Toplevel(self.root)
                password_window.title("Set Room Password")
                password_window.geometry("300x100")
                password_window.transient(self.root)
                
                # Apply theme
                theme = self.settings.themes["dark" if self.settings.dark_mode else "light"]
                password_window.configure(bg=theme["bg"])
                
                password = tk.StringVar()
                
                frame = tk.Frame(password_window, bg=theme["bg"])
                frame.pack(expand=True, fill='both', padx=10, pady=5)
                
                tk.Label(frame, text="Enter room password:", 
                        bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
                password_entry = tk.Entry(frame, textvariable=password, show="*",
                                       bg=theme["entry_bg"], fg=theme["entry_fg"],
                                       insertbackground=theme["fg"])
                password_entry.pack(pady=5)
                password_entry.focus()
                
                def submit_password():
                    if password.get().strip():
                        password_window.destroy()
                
                tk.Button(frame, text="Set Password", command=submit_password,
                         bg=theme["button_bg"], fg=theme["fg"],
                         activebackground=theme["input_bg"],
                         activeforeground=theme["fg"]).pack(pady=5)
                self.root.wait_window(password_window)
                room_password = password.get().strip()
            else:
                room_password = None

            create_data = {
                'type': 'create_room',
                'room': room_name,
                'password': room_password
            }
            try:
                self.client_socket.send(json.dumps(create_data).encode())
            except:
                messagebox.showerror("Error", "Could not create room")

    def join_room(self):
        room_name = self.room_entry.get().strip()
        if room_name:
            stored_password = self.room_passwords.get(room_name)
            join_data = {
                'type': 'join_room',
                'room': room_name,
                'password': stored_password
            }
            try:
                self.client_socket.send(json.dumps(join_data).encode())
            except:
                messagebox.showerror("Error", "Could not join room")

    def connect_to_server(self, host, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            print(f"Connected to server at {host}:{port}")  # Debug print
            
            self.username = self.get_username()
            if not self.username:
                print("No username provided")  # Debug print
                self.root.destroy()
                return
            
            print(f"Sending username: {self.username}")  # Debug print    
            username_data = {
                'type': 'username',
                'username': self.username
            }
            self.client_socket.send(json.dumps(username_data).encode())
            
            # Wait for initial response from server
            try:
                initial_data = self.client_socket.recv(1024).decode()
                if initial_data:
                    print(f"Received initial data: {initial_data}")  # Debug print
                    message_data = json.loads(initial_data)
                    if message_data['type'] == 'room_list':
                        self.available_rooms = message_data['rooms']
                        if 'protected_rooms' in message_data:
                            self.protected_rooms = set(message_data['protected_rooms'])
                        self.root.after(100, self.update_room_buttons)
            except Exception as e:
                print(f"Error receiving initial data: {e}")  # Debug print
                raise
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.root.mainloop()
            
        except Exception as e:
            print(f"Connection error: {e}")  # Debug print
            messagebox.showerror("Error", f"Could not connect to server: {str(e)}")
            self.root.destroy()

    def get_username(self):
        username_window = tk.Toplevel(self.root)
        username_window.title("Enter Username")
        username_window.geometry("300x150")
        username_window.resizable(False, False)
        username_window.transient(self.root)
        username_window.grab_set()
        username_window.configure(bg=self.settings.themes["light"]["bg"])
        
        result = [None]  # Store the result
        
        def submit():
            name = entry.get().strip()
            if name:
                result[0] = name
                username_window.destroy()
            else:
                messagebox.showerror("Error", "Username cannot be empty")
        
        # Create and pack widgets
        frame = tk.Frame(username_window, bg=self.settings.themes["light"]["bg"])
        frame.pack(expand=True, fill='both', padx=20, pady=20)  # Using pack parameters instead of padding
        
        label = tk.Label(frame, 
                        text="Enter your username:", 
                        font=('Helvetica', 12),
                        bg=self.settings.themes["light"]["bg"],
                        fg=self.settings.themes["light"]["fg"])
        label.pack(pady=(0, 10))
        
        entry = tk.Entry(frame, 
                        font=('Helvetica', 11),
                        bg=self.settings.themes["light"]["entry_bg"],
                        fg=self.settings.themes["light"]["entry_fg"],
                        insertbackground=self.settings.themes["light"]["fg"])
        entry.pack(pady=(0, 15), fill='x', padx=20)
        entry.focus()
        
        submit_button = tk.Button(frame, 
                                text="Join Chat", 
                                command=submit,
                                bg=self.settings.themes["light"]["button_bg"],
                                fg=self.settings.themes["light"]["fg"])
        submit_button.pack(pady=(0, 10))
        
        # Bind enter key
        entry.bind("<Return>", lambda e: submit())
        
        # Center the window
        username_window.update_idletasks()
        width = username_window.winfo_width()
        height = username_window.winfo_height()
        x = (username_window.winfo_screenwidth() // 2) - (width // 2)
        y = (username_window.winfo_screenheight() // 2) - (height // 2)
        username_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Wait for window to close
        username_window.wait_window()
        
        if result[0]:
            return result[0]
        else:
            if messagebox.askyesno("Retry", "No username provided. Try again?"):
                return self.get_username()
            return None

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    print("No data received from server")  # Debug print
                    break
                    
                message_data = json.loads(data)
                print(f"Received message type: {message_data['type']}")  # Debug print
                
                # Handle room list updates first
                if message_data['type'] == 'room_list':
                    print(f"Updating rooms: {message_data['rooms']}")  # Debug print
                    self.available_rooms = message_data['rooms']
                    if 'protected_rooms' in message_data:
                        self.protected_rooms = set(message_data['protected_rooms'])
                    self.root.after(100, self.update_room_buttons)
                
                elif message_data['type'] == 'message':
                    sender = message_data['sender']
                    content = message_data['content']
                    room = message_data['room']
                    
                    if room == self.current_room:
                        if sender == 'Server':
                            self.display_message(sender, content, 'server_message')
                        elif sender != self.username:
                            self.display_message(sender, content, 'other_message')
                
                elif message_data['type'] == 'room_joined':
                    if message_data['success']:
                        self.current_room = message_data['room']
                        self.chat_display.insert(tk.END, f"--- Joined {self.current_room} room ---\n", 'server_message')
                        self.update_room_buttons()  # Just update buttons, don't modify available_rooms
                    else:
                        if message_data['message'] == 'Incorrect password':
                            # Mark room as protected when password prompt appears
                            room_name = self.room_entry.get().strip()
                            self.protected_rooms.add(room_name)
                            self.update_room_buttons()
                            self.prompt_password_and_retry()
                        else:
                            messagebox.showerror("Error", message_data['message'])
                
                elif message_data['type'] == 'room_created':
                    if message_data['success']:
                        room_name = self.room_entry.get().strip()
                        if room_name in self.room_passwords:
                            self.protected_rooms.add(room_name)
                        self.join_room()
                    else:
                        messagebox.showerror("Error", message_data['message'])
                
                elif message_data['type'] == 'room_background':
                    if message_data['room'] == self.current_room:
                        self.room_backgrounds[self.current_room] = message_data['color']
                        self.chat_display.configure(bg=message_data['color'])
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        
        try:
            messagebox.showerror("Error", "Lost connection to server")
            self.root.destroy()
        except:
            pass

    def prompt_password_and_retry(self):
        password_window = tk.Toplevel(self.root)
        password_window.title("Room Password")
        password_window.geometry("300x100")
        password_window.transient(self.root)
        
        # Apply theme
        theme = self.settings.themes["dark" if self.settings.dark_mode else "light"]
        password_window.configure(bg=theme["bg"])
        
        password = tk.StringVar()
        
        frame = tk.Frame(password_window, bg=theme["bg"])
        frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        tk.Label(frame, text="Enter room password:", 
                bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        password_entry = tk.Entry(frame, textvariable=password, show="*",
                               bg=theme["entry_bg"], fg=theme["entry_fg"],
                               insertbackground=theme["fg"])
        password_entry.pack(pady=5)
        password_entry.focus()
        
        def submit():
            if password.get().strip():
                room_name = self.room_entry.get().strip()
                password_value = password.get().strip()
                self.room_passwords[room_name] = password_value
                join_data = {
                    'type': 'join_room',
                    'room': room_name,
                    'password': password_value
                }
                try:
                    self.client_socket.send(json.dumps(join_data).encode())
                except:
                    messagebox.showerror("Error", "Could not join room")
                password_window.destroy()
                
        tk.Button(frame, text="Join Room", command=submit,
                 bg=theme["button_bg"], fg=theme["fg"],
                 activebackground=theme["input_bg"],
                 activeforeground=theme["fg"]).pack(pady=5)
        password_entry.bind("<Return>", lambda e: submit())

    def display_message(self, sender, content, message_type='other_message'):
        """Display message with proper alignment"""
        # Add newline before message for spacing
        self.chat_display.insert(tk.END, "\n")
        
        # Create a new tag for each message to handle alignment
        tag_name = f"msg_{self.chat_display.index(tk.END)}"
        
        if message_type == 'my_message':
            # For sent messages (right-aligned)
            self.chat_display.tag_config(tag_name, justify='right', foreground=self.current_theme["my_message"])
            self.chat_display.insert(tk.END, f"{content} :{sender}\n", tag_name)
        elif message_type == 'server_message':
            # For server messages (centered)
            self.chat_display.tag_config(tag_name, justify='center', foreground=self.current_theme["server_message"])
            self.chat_display.insert(tk.END, f"--- {content} ---\n", tag_name)
        else:
            # For received messages (left-aligned)
            self.chat_display.tag_config(tag_name, justify='left', foreground=self.current_theme["other_message"])
            self.chat_display.insert(tk.END, f"{sender}: {content}\n", tag_name)
        
        # Scroll to the bottom
        self.chat_display.see(tk.END)
        
        # Add extra spacing after server messages
        if message_type == 'server_message':
            self.chat_display.insert(tk.END, "\n")

    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            message_data = {
                'type': 'message',
                'sender': self.username,
                'content': message,
                'room': self.current_room
            }
            try:
                self.client_socket.send(json.dumps(message_data).encode())
                self.display_message(self.username, message, 'my_message')
                self.message_input.delete(0, tk.END)
            except:
                messagebox.showerror("Error", "Could not send message")

    def quick_switch_room(self, room_name):
        """Quickly switch to selected room"""
        if room_name != self.current_room:
            self.room_entry.delete(0, tk.END)
            self.room_entry.insert(0, room_name)
            self.join_room()

    def update_clock(self):
        """Update the clock display"""
        current_time = time.strftime('%H:%M:%S')
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def apply_font_to_all(self, font_family=None, font_size=None):
        """Apply font changes to all UI elements"""
        if font_family is None:
            font_family = self.settings.font_family
        if font_size is None:
            font_size = self.settings.font_size
            
        # Update all labels, entries, and buttons recursively
        def update_widget_fonts(widget):
            try:
                # Update widget font if it's a supported type
                if isinstance(widget, (tk.Label, tk.Entry, tk.Button, tk.Listbox, scrolledtext.ScrolledText)):
                    widget.configure(font=(font_family, font_size))
                
                # Update menu items
                elif isinstance(widget, tk.Menu):
                    widget.configure(font=(font_family, font_size))
                    
                # Recursively update all child widgets
                for child in widget.winfo_children():
                    update_widget_fonts(child)
            except:
                pass  # Skip widgets that don't support font changes
        
        # Update all widgets starting from root
        update_widget_fonts(self.root)
        
        # Update room buttons
        self.update_room_buttons()

    def change_font_size(self):
        """Open dialog to change font size"""
        size = simpledialog.askinteger("Font Size", "Enter font size (8-20):", 
                                     minvalue=8, maxvalue=20, 
                                     initialvalue=self.settings.font_size)
        if size:
            self.settings.font_size = size
            self.apply_font_to_all(font_size=size)

    def update_font_menu(self, font_menu):
        """Update the font menu with current font list"""
        # Clear existing menu items
        font_menu.delete(0, tk.END)
        
        # Add fonts to menu
        for font in self.fonts:
            font_menu.add_command(
                label=font,
                command=lambda f=font: self.change_font_family(f),
                font=(font, 10)
            )

    def change_font_family(self, font_family):
        """Change font family and update settings"""
        self.settings.font_family = font_family  # Update settings
        self.apply_font_to_all(font_family=font_family)

    def import_system_fonts(self):
        """Import available system fonts"""
        # Create font selection window
        font_window = tk.Toplevel(self.root)
        font_window.title("Import System Fonts")
        font_window.geometry("400x500")
        font_window.transient(self.root)
        
        # Apply theme
        theme = self.current_theme
        font_window.configure(bg=theme["bg"])
        
        # Get system fonts
        system_fonts = list(tkFont.families())
        system_fonts.sort()
        
        # Create frame for list and scrollbar
        list_frame = tk.Frame(font_window, bg=theme["bg"])
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create listbox with scrollbar
        font_list = tk.Listbox(list_frame, 
                              selectmode=tk.MULTIPLE,
                              bg=theme["entry_bg"],
                              fg=theme["entry_fg"],
                              selectbackground=theme["button_bg"],
                              selectforeground=theme["fg"])
        font_list.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=font_list.yview)
        scrollbar.pack(side='right', fill='y')
        
        font_list.configure(yscrollcommand=scrollbar.set)
        
        # Add fonts to listbox
        for font in system_fonts:
            font_list.insert(tk.END, font)
            try:
                # Show each font in its own style
                font_list.itemconfig(font_list.size()-1, font=(font, 10))
            except:
                pass  # Skip if font can't be displayed
        
        def import_selected():
            selected_indices = font_list.curselection()
            if selected_indices:
                selected_fonts = [font_list.get(i) for i in selected_indices]
                # Add new fonts to the list if they're not already there
                for font in selected_fonts:
                    if font not in self.fonts:
                        self.fonts.append(font)
                self.fonts.sort()
                # Update the font menu
                self.update_font_menu(self.font_family_menu)
                font_window.destroy()
        
        # Add buttons
        button_frame = tk.Frame(font_window, bg=theme["bg"])
        button_frame.pack(fill='x', pady=10, padx=10)
        
        tk.Button(button_frame,
                 text="Import Selected",
                 command=import_selected,
                 bg=theme["button_bg"],
                 fg=theme["fg"]).pack(side='right', padx=5)
        
        tk.Button(button_frame,
                 text="Cancel",
                 command=font_window.destroy,
                 bg=theme["button_bg"],
                 fg=theme["fg"]).pack(side='right', padx=5)

if __name__ == "__main__":
    main()