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
# default: pi raspberry
# set password to "none"
echo -ne "none\nnone\n" | sudo passwd pi
echo -ne "none\nnone\n" | sudo passwd root

### hostname ###
sudo nano /etc/hosts
sudo nano /etc/hostname
sudo /etc/init.d/hostname.sh
sudo reboot

### info ###
cat /proc/cpuinfo

### config ###
# update, set hostname to rpi, set localisation timezone to asia jerusalem, advanced expand filesystem
sudo raspi-config
sudo sh -c "echo 'dtparam=audio=off' >> /boot/config.txt"
sudo sh -c "echo 'max_usb_current=1' >> /boot/config.txt"
sudo sh -c "echo 'pi3-disable-bt' >> /boot/config.txt"
sudo sh -c "echo 'dtoverlay=pi3-disable-wifi' >> /boot/config.txt"
sudo sh -c "echo 'enable_uart=1' >> /boot/config.txt"
sudo sh -c "echo 'consoleblank=0' >> /boot/config.txt"
sudo sh -c "echo 'audio_pwm_mode=2' >> /boot/config.txt"
sudo sh -c "echo 'display_rotate=2' >> /boot/config.txt"

### aliases ###
sudo nano /home/pi/.bash_aliases
alias sudo='sudo '
alias ll='ls -lhA'
alias ..='cd ..'
alias df='df -H'
alias du='du -ch'
alias read_cpu_temperature='/opt/vc/bin/vcgencmd measure_temp'

### wifi ###
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
network={
	ssid="Mada_WiFi_1"
	psk="madaorgil"
	# key_mgmt=NONE
	# key_mgmt=WPA-PSK
}

### volume ###
aplay -l
amixer set PCM 96%
amixer set Speaker 96%
sudo nano /etc/asound.conf
pcm.!default {
    type hw
    card 1
}
ctl.!default {
    type hw           
    card 1
}
alsamixer

### upgrade ###
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y
sudo rpi-update

### chmodes ###
sudo chmod +x *.sh

### apps ###
sudo apt-get install fswebcam ffmpeg ssmtp mpack git samba samba-common-bin i2c-tools python3-pip oracle-java8-jdk -y
for i in "kodi" "vlc" "tortoisehg" "openjdk-8-jre" "bluetooth" "bluez"; do
	sudo apt-get install "$i" -y
done

### python3.6 ###
RELEASE=3.6.5
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
sudo rm -rf ~/python3/
cd ~

### python3 packages ###
pip3 install --upgrade pip pep8 autopep8
pip3 install --upgrade ipython rpyc pyserial pygsheets pyshorteners speedtest-cli rpi.gpio PiCamera smbus2 pyalsaaudio
pip3 install --upgrade gpac bluepy	
sudo apt-get install libsdl-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev python3-dev python3-numpy -y
pip3 install --upgrade Pillow pygame PyOpenGL plumbum
python3 -m pip install django

### systemd service ###
sudo sh -c "cat > /lib/systemd/system/uv_bicycle.service <<EOF
[Unit]
Description=UV Bicycle
After=multi-user.target
[Service]
Type=simple
ExecStart=/bin/bash /home/pi/Public/uv_bicycle/run_gsm_to_arduino.sh --interface rpyc
Restart=on-abort
[Install]
WantedBy=multi-user.target
EOF"
# after changing uv_bicycle.service run daemon-reload
sudo chmod 644 /lib/systemd/system/uv_bicycle.service
sudo systemctl daemon-reload
sudo systemctl enable uv_bicycle.service
sudo systemctl start uv_bicycle.service
# save journalctl logs
sudo mkdir /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo sh -c "cat >> /etc/systemd/journald.conf <<EOF
SystemMaxUse=10M
EOF"
sudo systemctl restart systemd-journald
# check status
sudo systemctl status uv_bicycle.service -l
# retart service
sudo systemctl restart uv_bicycle.service
# stop service
sudo systemctl stop uv_bicycle.service
# check service's log
sudo journalctl --no-tail --no-pager -m -o cat -u uv_bicycle.service
# Output file's content while it change
tail -f /home/pi/Public/sms_log.txt

### bluetooth ###
# https://www.cnet.com/how-to/how-to-setup-bluetooth-on-a-raspberry-pi-3/
sudo bluetoothctl
[bluetooth]# agent on
[bluetooth]# default-agent
[bluetooth]# scan on
[bluetooth]# pair 98:D3:31:B2:CA:59
[bluetooth]# quit
# create serial dev for bt connection
sudo rfcomm bind 0 98:D3:31:90:30:3A
sudo rfcomm connect hci0 98:D3:31:90:30:3A &
sudo rfcomm release 0
ls /dev/rfcomm*
# update bluez
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.48.tar.xz
tar xvf bluez-5.48.tar.xz
cd bluez-5.48/
export LDFLAGS=-lrt
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var --enable-library -disable-systemd
make
sudo make install
# sudo cp attrib/gatttool /usr/bin/
sudo hcitool lescan
sudo gatttool -b 28:37:37:1A:D3:CF -I
[30:AE:A4:21:75:A6][LE]> connect
[30:AE:A4:21:75:A6][LE]> char-write-cmd 0x002d 55555555555555555555555555555555
[30:AE:A4:21:75:A6][LE]> char-read-hnd 0x002a
# http://www.instructables.com/id/Control-Bluetooth-LE-Devices-From-A-Raspberry-Pi/ https://www.elinux.org/RPi_Bluetooth_LE
sudo blescan

### serial ports ###
# print dev info
udevadm info -q path -n /dev/ttyUSB1
# auto serial port shortcuts
sudo sh -c 'cat > /etc/udev/rules.d/90-usb-serial.rules <<EOF
SUBSYSTEM=="tty",KERNELS=="1-1.2:1.0",SYMLINK+="ttyGsmUart"
SUBSYSTEM=="tty",KERNELS=="1-1.4:1.0",SYMLINK+="ttyUvBicycle"
EOF'
# ttyUSB
sudo chmod 666 /dev/ttyUSB0
lsmod | grep cp210x
dmesg
ls -la /dev/ttyUSB*
sudo nano /etc/udev/rules.d/ttyUSB.rules
KERNEL=="ttyUSB[0 … 9]" SYMLINK+="%k" GROUP="lab" MODE="0666"
# reset bus power
for i in "unbind" "bind"; do sudo sh -c "echo 1-1 > /sys/bus/usb/drivers/usb/$i" && sleep 5; done

### miniterm ###
python3 /usr/local/lib/python3.6/site-packages/serial/tools/miniterm.py /dev/ttyUSB0 38400 --eol CRLF

### arduino ###
~/Public/arduino/arduino --board arduino:avr:pro --port /dev/ttyUSB0 --upload ~/Public/uv_bicycle/src/arduino_to_uv/arduino_to_uv.ino
~/Public/arduino/arduino --board arduino:avr:pro --verify ~/Public/uv_bicycle/src/arduino_to_uv/arduino_to_uv.ino

### samba ###
mkdir /home/pi/Public
sudo chmod a+w /home/pi/Public
echo -ne "\n\n" | sudo smbpasswd -a pi
sudo nano /etc/samba/smb.conf
force user = pi
wins support = yes

[Public]
 comment = Shared Public
 path = /home/pi/Public
 browseable = Yes
 writeable = Yes
 guest ok = yes
 read only = no
 guest ok = yes
 create mask = 0777
 directory mask = 0777
 public = yes
 force user = pi

sudo /etc/init.d/samba restart

### dataplicity ###
curl https://www.dataplicity.com/n8ccp0y7.py | sudo python
# remove agent
sudo rm -f /etc/supervisor/conf.d/tuxtunnel.conf
sudo service supervisor restart
sudo rm -r /var/log/supervisor
sudo apt-get purge supervisor -y
sudo rm -r /opt/dataplicity
sudo rm -r /etc/supervisor
sudo userdel dataplicity
sudo reboot
# video stream
ls /dev | grep vid
sudo apt-get install libjpeg8-dev imagemagick libv4l-dev
wget http://terzo.acmesystems.it/download/webcam/mjpg-streamer.tar.gz
tar -xvzf mjpg-streamer.tar.gz
sudo ln -s /usr/include/libv4l1-videodev.h /usr/include/linux/videodev.h
cd mjpg-streamer/
nano Makefile # PLUGINS += input_gspcav1.so
make
sudo ./mjpg_streamer -i "./input_uvc.so -f 10 -r 640x480 -n -y" -o "./output_http.so -w ./www -p 80"
https://<YOUR_ID>.dataplicity.io/stream_simple.html
http://192.168.1.108:80/?action=stream

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

### cameras ###
# sudo raspi-config -> Interfacing Options -> Camera -> YES
sudo modprobe bcm2835-v4l2 # map pi camera to /dev/videoX
fswebcam --no-banner -r 2592x1944 -d /dev/video0 ~/Public/pi_camera.jpg
fswebcam --no-banner -r 640x480 -d /dev/video1 ~/Public/usb_camera.jpg
ffmpeg -y -f video4linux2 -s 640x480 -t 5.7 -i /dev/video0 /home/pi/Public/pi_camera.avi
ffmpeg -y -f video4linux2 -s 640x480 -t 5.7 -i /dev/video1 /home/pi/Public/usb_camera.avi
raspivid -f -t 6000000

### display ###
# https://www.raspberrypi.org/forums/viewtopic.php?t=5851
tvservice -e 'dmt 58 hdmi'
sudo sh -c "cat >> /boot/config.txt <<EOF
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=800 480 60 6 0 0 0
hdmi_drive=1
# Enable touchscreen on Elecrow HDMI interface.
dtparam=spi=on
dtparam=i2c_arm=on
dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900
dtoverlay=w1-gpio-pullup,gpiopin=4,extpullup=1
EOF"
sudo apt-get install xinput-calibrator -y
# Click the Men button on the task bar, choose Preference -> Calibrate Touchscreen.
sudo apt-get install xserver-xorg-input-evdev
# be sure that evdev.conf has a higher number than 40-libinput.conf:
sudo mv /usr/share/X11/xorg.conf.d/10-evdev.conf /usr/share/X11/xorg.conf.d/45-evdev.conf
sudo reboot
sudo sh -c 'cat >> /usr/share/X11/xorg.conf.d/99-calibration.conf <<EOF
Section "InputClass"
        Identifier      "calibration"
        MatchProduct    "ADS7846 Touchscreen"
        Option  "Calibration"   "125 3981 193 3936"
        Option  "SwapAxes"      "0"
EndSection
EOF'
# terminal
sudo xauth add $(xauth list $DISPLAY)
export DISPLAY=:0

### email ###
sudo sh -c "cat > /etc/ssmtp/ssmtp.conf <<EOF
root=mada.drive1@gmail.com
mailhub=smtp.gmail.com:587
FromLineOverride=YES
AuthUser=mada.drive1@gmail.com
AuthPass=PASSWORD
UseSTARTTLS=YES
UseTLS=YES
EOF"
echo "This is a test" | ssmtp arad.rgb@gmail.com
mpack -s "New Camera" ~/Public/usb_camera_02.jpg arad.rgb@gmail.com

### infra ###
mkdir ~/Public
touch ~/Public/__init__.py
cd ~/Public && git clone https://github.com/arduino12/infra

### change visudo editor ###
sudo update-alternatives --config editor

### MPR121 ###
sudo sh -c "echo 'dtoverlay=i2c-bcm2708' >> /boot/config.txt"
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus
cd ~/Public
git clone https://github.com/adafruit/Adafruit_Python_MPR121.git
cd Adafruit_Python_MPR121
sudo python setup.py install

sudo apt-get install i2c-tools libi2c-dev python3-dev -y
sudo pip3 install smbus2

### links ###
# https://mtantawy.com/quick-tip-how-to-update-to-latest-kodi-16-jarvis-on-raspberry-pi/
# http://g8ogj.org/files/Using%20USB%20serial%20ports%20under%20wine%20howwto%20ipb.pdf
# https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx
# https://www.silabs.com/Support%20Documents/Software/Linux_CP210x_VCP_3.x.x_Release_Notes.txt
# http://www.oracle.com/webfolder/technetwork/tutorials/obe/java/RaspberryPiFX/raspberryfx.html
# http://pblog.ebaker.me.uk/2014/01/uploading-arduino-sketch-from-raspberry.html
