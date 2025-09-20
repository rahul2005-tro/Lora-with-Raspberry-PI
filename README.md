# Lora-with-Raspberry-PI
I have Developed an project for reciving the data which is sent via lora sx1278 and recived using an pi 4 the important is this i had diasbled the SPI 1 which is default in PI and enabled SPI 2 for the Usage

The Steps and in readmefile
-------Enabiling SPI-----
1. sudo raspi-config
2.interface -> SPI -> Enable ->Finish


------SPI 2-------------
1.sudo nano /boot/firmware/config.txt
2.Scroll to the very bottom and add this new line
dtoverlay=spi1-3cs

3.sudo reboot

------ Installing---------
1.Download the git hub repo

2.python3 -m venv lora_env

3.source lora_env/bin/activate



# Pin Layout

LoRa SX1278 Pin	Raspberry Pi Pin (Board #)	GPIO #
VCC	Pin 1 (3.3V)	3.3V
GND	Pin 6 (Ground)	Ground
MISO	Pin 35	GPIO19
MOSI	Pin 38	GPIO20
SCK	Pin 40	GPIO21
CS / NSS	Pin 36	GPIO16
RESET	Pin 29 (GPIO5)	GPIO5
