import time
import busio
import digitalio
import board
import adafruit_rfm9x
import csv
from datetime import datetime
import os
import serial

# -----------------------------
# CONFIG
# -----------------------------
LOG_FILE = 'lora_log.csv'
PHONE_NUMBER = "+91xxxxxxxxxx"   # Replace with your number
BV_THRESHOLD = 5.0               # Trigger if battery voltage < 5V

# -----------------------------
# GSM SETUP (SIM800L)
# -----------------------------
ser = serial.Serial(
    port='/dev/ttyS0',   # Check /dev/ttyAMA0 or /dev/serial0 on your Pi
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

def send_at_command(command, expected_response="OK"):
    ser.write((command + '\r\n').encode())
    time.sleep(1)
    response = ser.read_all().decode(errors="ignore")
    print(f"Sent: {command}, Received: {response.strip()}")
    return expected_response in response

def send_sms(phone_number, message):
    """Send SMS via SIM800L"""
    print(f"Sending SMS to {phone_number}...")
    ser.write(('AT+CMGS="' + phone_number + '"\r').encode())
    time.sleep(1)
    ser.write(message.encode() + b"\x1A")  # Ctrl+Z to send
    time.sleep(5)
    response = ser.read_all().decode(errors="ignore")
    if "OK" in response:
        print("SMS sent successfully! ✅")
    else:
        print(f"Failed to send SMS. Response: {response.strip()}")

print("Initializing SIM800L modem...")
time.sleep(10)  # Give SIM800L time to boot and connect
if not send_at_command("AT"):
    print("Modem not responding. Exiting...")
    exit()
send_at_command("AT+CMGF=1")  # Set SMS to text mode

# -----------------------------
# LoRa SETUP
# -----------------------------
CS = digitalio.DigitalInOut(board.D16)
RESET = digitalio.DigitalInOut(board.D5)
spi = busio.SPI(board.D21, MOSI=board.D20, MISO=board.D19)

file_exists = os.path.isfile(LOG_FILE)
try:
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'message', 'rssi'])
except IOError as e:
    print(f"Error: Unable to open or write to log file {LOG_FILE}. {e}")
    exit()

try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 433.0)
    print("RFM9x LoRa radio initialized on SPI1.")
except Exception as e:
    print(f"Error initializing RFM9x radio: {e}")
    exit()

print("Waiting for LoRa packets... (Logging + SMS Alerts Enabled)")

# -----------------------------
# MAIN LOOP
# -----------------------------
alert_sent = False  # Tracks if SMS already sent for current low voltage

try:
    while True:
        packet = rfm9x.receive()

        if packet is not None:
            rssi = rfm9x.last_rssi
            try:
                packet_text = str(packet, "utf-8").strip()
                print(f"Received: '{packet_text}' | RSSI: {rssi}")

                # Log packet
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(LOG_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, packet_text, rssi])

                # -----------------------------
                # PARSE BATTERY VOLTAGE (BV)
                # -----------------------------
                if "BV:" in packet_text:
                    try:
                        bv_part = [field for field in packet_text.split(",") if field.startswith("BV:")][0]
                        batt_voltage = float(bv_part.replace("BV:", "").replace("V", ""))
                        print(f"Battery Voltage = {batt_voltage:.2f} V")

                        # Low-voltage alert
                        if batt_voltage < BV_THRESHOLD and not alert_sent:
                            alert_msg = f"⚠️ ALERT: Battery voltage {batt_voltage:.2f}V (below {BV_THRESHOLD}V) at {timestamp}"
                            print(alert_msg)
                            send_sms(PHONE_NUMBER, alert_msg)
                            alert_sent = True

                        # Recovery alert
                        elif batt_voltage >= BV_THRESHOLD and alert_sent:
                            recovery_msg = f"✅ Battery recovered: {batt_voltage:.2f}V at {timestamp}"
                            print(recovery_msg)
                            send_sms(PHONE_NUMBER, recovery_msg)
                            alert_sent = False

                    except Exception as e:
                        print(f"Error parsing BV: {e}")

            except UnicodeDecodeError:
                print(f"Received non-text data: {packet} | RSSI: {rssi}")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nReceiver stopped.")
    ser.close()
