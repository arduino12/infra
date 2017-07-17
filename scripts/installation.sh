#!/usr/bin/env bash

### burn raspbian on SD ###
# download raspbian-jessie-lite from https://www.raspberrypi.org/downloads/raspbian/
# formate 4GB+ SD using infra\tools\SD-Formatter.exe
# flash the raspbian image to SD using infra\tools\Disk-Imager.exe
# for headless pi:
#   add file named "ssh" to SD
#   after power up the pi it prints its ip
# without screen:
#   add "enable_uart=1" to config.txt in SD
#   connect USB-UART, PI pins:
#   ........................................
#   ...................................RXTXGND..(pi corner)
#   after power up the pi, login in the usb terminal as (pi, raspberry)
#   enter command "sudo raspi-config" -> Interfacing Options -> SSH -> YES
#   enter command "ifconfig" to see its ip
# now ssh to its pi@192.168.1.X

### user ###
default: pi raspberry
# set password to "none", ";" is \n
sudo passwd pi; none; none

### info ###
cat /proc/cpuinfo

### config ###
sudo raspi-config
sudo echo "display_rotate=2" >> /boot/config.txt
sudo echo "enable_uart=1" >> /boot/config.txt
sudo echo "audio_pwm_mode=2" >> /boot/config.txt

### upgrade ###
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y
sudo rpi-update

### chmodes ###
sudo chmod +x *.sh

### apps ###
sudo apt-get install git samba samba-common-bin -y
for i in "kodi" "vlc" "tortoisehg" "curl" "openjdk-8-jre" "bluetooth" "bluez"; do
	sudo apt-get install "$i" -y
done

### python3.6 ###
RELEASE=3.6.1
# install dependencies
sudo apt-get install libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev -y
# download and build Python
mkdir ~/python3
cd ~/python3
wget https://www.python.org/ftp/python/$RELEASE/Python-$RELEASE.tar.xz
tar xvf Python-$RELEASE.tar.xz
cd Python-$RELEASE
./configure
make
sudo make install
sudo rm -rf ~/python3/Python-$RELEASE
cd ~

### python3 packages ###
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade ipython rpyc pyserial
# sudo pip3 install --upgrade Pillow
python3 -m pip install django
sudo apt-get install libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev -y # python3-dev python3-numpy -y
sudo pip3 install --upgrade pygame

### systemd service ###
sudo nano /lib/systemd/system/uv_bicycle.service
[Unit]
Description=UV Bicycle
After=multi-user.target
[Service]
Type=simple
ExecStart=/bin/bash /home/pi/Public/uv_bicycle/run_gsm_to_arduino.sh --interface rpyc
Restart=on-abort
[Install]
WantedBy=multi-user.target
# after changing uv_bicycle.service run daemon-reload
sudo chmod 644 /lib/systemd/system/uv_bicycle.service
sudo systemctl daemon-reload
sudo systemctl enable uv_bicycle.service
sudo systemctl start uv_bicycle.service
# Check status
sudo systemctl status uv_bicycle.service
# Start service
sudo systemctl start uv_bicycle.service
# Stop service
sudo systemctl stop uv_bicycle.service
# Check service's log
sudo journalctl -f -u hello.service

### bluetooth ###
# https://www.cnet.com/how-to/how-to-setup-bluetooth-on-a-raspberry-pi-3/
sudo bluetoothctl
[bluetooth]# agent on
[bluetooth]# default-agent
[bluetooth]# scan on
[bluetooth]# pair 98:D3:31:B2:CA:59
[bluetooth]# trust 98:D3:31:B2:CA:59
[bluetooth]# quit
# create serial dev for bt connection
sudo rfcomm connect hci0 98:D3:31:90:30:3A &

### serial ports ###
# print dev info
udevadm info -q path -n /dev/ttyUSB1
# auto serial port shortcuts
sudo nano /etc/udev/rules.d/90-usb-serial.rules
SUBSYSTEM=="tty",KERNELS=="1-1.2:1.0",SYMLINK+="arduino_uv"
SUBSYSTEM=="tty",KERNELS=="1-1.4:1.0",SYMLINK+="gsm_a6"
# ttyUSB
sudo chmod 666 /dev/ttyUSB0
lsmod | grep cp210x
dmesg
ls -la /dev/ttyUSB*
sudo nano /etc/udev/rules.d/ttyUSB.rules
KERNEL=="ttyUSB[0 … 9]" SYMLINK+="%k" GROUP="lab" MODE="0666"

### miniterm ###
python3 /usr/local/lib/python3.6/site-packages/serial/tools/miniterm.py /dev/ttyUSB0 38400 --eol CRLF

### arduino ###
~/Public/arduino/arduino --board arduino:avr:pro --port /dev/ttyUSB0 --upload ~/Public/uv_bicycle/src/arduino_to_uv/arduino_to_uv.ino
~/Public/arduino/arduino --board arduino:avr:pro --verify ~/Public/uv_bicycle/src/arduino_to_uv/arduino_to_uv.ino

### samba ###
sudo smbpasswd -a pi; ; 
sudo nano /etc/samba/smb.conf
force user=pi
workgroup = WORKGROUP
wins support = yes

[Public]
 comment=Shared Public
 path=/home/pi/Public
 browseable=Yes
 writeable=Yes
 guest ok=yes
 create mask=0777
 directory mask=0777
 public=yes
sudo chmod a+w Public/
sudo /etc/init.d/samba restart

### usb network ###
sudo nano /etc/network/interfaces
allow-hotplug usb0
iface usb0 inet static
        address 192.168.42.1
        netmask 255.255.255.0
        network 192.168.42.0
        gateway 192.168.42.129
        broadcast 192.168.42.255
iface usb0 inet dhcp

sudo ifdown usb0; sudo ifup usb0; ping google.com

### language ###
sudo setxkbmap -option grp:switch,grp:alt_shift_toggle,grp_led:scroll de,tr,us

### wine ###
ln -s /dev/ttyUSB0 ~/.wine/dosdevices/com2
wine /home/lab/Desktop/ESP/LuaLoader/LuaLoader.exe

### kodi ###
cp <start_kodi.sh> /usr/local/bin/start_kodi.sh
sudo chmod a+x /usr/local/bin/start_kodi.sh
nano Desktop/KODI
[Desktop Entry]
Name=KODI
Comment=KODI MEDIA CENTER
Exec=/usr/local/bin/startkodi
Icon=/usr/share/kodi/media/icon256x256.png
Terminal=false
Type=Application
Categories=Sound;Video;
StartupNotify=true

### vlc youtube hack ###
sudo rm /usr/lib/vlc/lua/playlist/youtube.*
sudo curl "http://git.videolan.org/?p=vlc.git;a=blob_plain;f=share/lua/playlist/youtube.lua;hb=HEAD" -o /usr/lib/vlc/lua/playlist/youtube.lua
http://addons.videolan.org/content/show.php/+Youtube+playlist?content=149909
sudo mv Downloads/playlist_youtube.lua /usr/lib/vlc/lua/playlist/

### links ###
# https://mtantawy.com/quick-tip-how-to-update-to-latest-kodi-16-jarvis-on-raspberry-pi/
# http://g8ogj.org/files/Using%20USB%20serial%20ports%20under%20wine%20howwto%20ipb.pdf
# https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx
# https://www.silabs.com/Support%20Documents/Software/Linux_CP210x_VCP_3.x.x_Release_Notes.txt
# http://www.oracle.com/webfolder/technetwork/tutorials/obe/java/RaspberryPiFX/raspberryfx.html
# http://pblog.ebaker.me.uk/2014/01/uploading-arduino-sketch-from-raspberry.html
