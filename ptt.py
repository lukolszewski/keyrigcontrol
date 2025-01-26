import socket
import evdev
from evdev import InputDevice, ecodes

# Hamlib rigctld connection details
RIGCTL_HOST = "127.0.0.1"
RIGCTL_PORT = 4535

# Connect to rigctld and keep the connection open
def open_rigctl_connection():
    try:
        conn = socket.create_connection((RIGCTL_HOST, RIGCTL_PORT))
        print("Connected to rigctld.")
        return conn
    except Exception as e:
        print(f"Error connecting to rigctld: {e}")
        exit(1)

# Send a command to rigctld
def send_rigctl_command(conn, command):
    try:
        conn.sendall(f"{command}\n".encode())
        response = conn.recv(1024).decode()
        return response.strip()
    except Exception as e:
        print(f"Error sending command to rigctld: {e}")
        return None

# Retrieve the current PTT state
def get_ptt_state(conn):
    response = send_rigctl_command(conn, "t")  # 't' retrieves the current PTT state
    if response is not None:
        return response == "1"  # "1" means PTT is ON
    else:
        print("Failed to retrieve PTT state.")
        return False

# Input device selection by number
devices = [InputDevice(path) for path in evdev.list_devices()]
print("Available devices:")
for i, device in enumerate(devices):
    print(f"[{i}] {device.path}: {device.name}")

while True:
    try:
        device_index = int(input("Enter the number of the device to monitor: "))
        if 0 <= device_index < len(devices):
            device = devices[device_index]
            break
        else:
            print("Invalid selection. Try again.")
    except ValueError:
        print("Please enter a valid number.")

print(f"Selected device: {device.path} ({device.name})")
print(f"Listening for keystrokes on {device.name}...")

# Open rigctld connection
rigctl_conn = open_rigctl_connection()
ptt_state = get_ptt_state(rigctl_conn)  # Get initial PTT state
print(f"Initial PTT state: {'ON' if ptt_state else 'OFF'}")

# Key tracking
keys_pressed = set()

try:
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            keycode = event.code
            keystate = event.value  # 1 = key down, 0 = key up

            if keystate == 1:  # Key down
                keys_pressed.add(keycode)
            elif keystate == 0:  # Key up
                keys_pressed.discard(keycode)

            # Detect "Left Control + Space"
            if ecodes.KEY_LEFTCTRL in keys_pressed and ecodes.KEY_SPACE in keys_pressed:
                ptt_state = not ptt_state  # Toggle PTT state
                command = f"T {int(ptt_state)}"
                response = send_rigctl_command(rigctl_conn, command)
                if response is not None:
                    print(f"PTT {'ON' if ptt_state else 'OFF'}")
                else:
                    print("Failed to toggle PTT.")

            # Debugging: Print key press
            if keystate == 1:  # Key down
                print(f"Key pressed: {ecodes.KEY[keycode]}")

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    rigctl_conn.close()
    print("Closed connection to rigctld.")

