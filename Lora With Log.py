import time
import busio
import digitalio
import board
import adafruit_rfm9x
import csv  # --- NEW: Import library for CSV logging
from datetime import datetime  # --- NEW: Import library for timestamps
import os   # --- NEW: Import library to check if file exists

# --- NEW: Define the name of our log file ---
LOG_FILE = 'lora_log.csv'

# --- Lora Radio Configuration (for SPI1) ---
CS = digitalio.DigitalInOut(board.D16)
RESET = digitalio.DigitalInOut(board.D5)
spi = busio.SPI(board.D21, MOSI=board.D20, MISO=board.D19)

# --- NEW: Create the log file and write the header if it doesn't exist ---
file_exists = os.path.isfile(LOG_FILE)
try:
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write the header row only once
            writer.writerow(['timestamp', 'message', 'rssi'])
except IOError as e:
    print(f"Error: Unable to open or write to log file {LOG_FILE}. {e}")
    exit()

# Initialize RFM9x radio
try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)
    print("RFM9x LoRa radio initialized on SPI1.")
except Exception as e:
    print(f"Error initializing RFM9x radio: {e}")
    exit()

print("Waiting for LoRa packets... (Now logging to lora_log.csv)")

# Main loop to listen for packets
try:
    while True:
        packet = rfm9x.receive()

        if packet is not None:
            rssi = rfm9x.last_rssi
            try:
                packet_text = str(packet, "utf-8")
                print(f"Received Message: '{packet_text}' | RSSI: {rssi}")
                
                # --- NEW: Log the received data to the CSV file ---
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(LOG_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, packet_text, rssi])
                    
            except UnicodeDecodeError:
                print(f"Received non-text data: {packet} | RSSI: {rssi}")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nReceiver stopped.")