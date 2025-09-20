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

