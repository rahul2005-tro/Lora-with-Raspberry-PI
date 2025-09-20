import time
import busio
import digitalio
import board
import adafruit_rfm9x

# --- Lora Radio Configuration (for SPI1) ---
CS = digitalio.DigitalInOut(board.D16)      # <-- UPDATED PIN for CS
RESET = digitalio.DigitalInOut(board.D5)    # <-- This pin stays the same
# Define the SPI bus using the specific pins for SPI1
spi = busio.SPI(board.D21, MOSI=board.D20, MISO=board.D19) # <-- UPDATED PINS

# Initialize RFM9x radio
try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)
    print("RFM9x LoRa radio initialized on SPI1.")
except Exception as e:
    print(f"Error initializing RFM9x radio: {e}")
    exit()

print("Waiting for LoRa packets...")

# Main loop to listen for packets
try:
    while True:
        # Check for a received packet
        packet = rfm9x.receive()

        if packet is not None:
            # A packet was received!
            try:
                # Attempt to decode the packet as UTF-8 text
                packet_text = str(packet, "utf-8")
                rssi = rfm9x.last_rssi
                print(f"Received Message: '{packet_text}' | RSSI: {rssi}")
            except UnicodeDecodeError:
                # Packet was not valid UTF-8
                rssi = rfm9x.last_rssi
                print(f"Received non-text data: {packet} | RSSI: {rssi}")

        # Wait a moment before checking again
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nReceiver stopped.")