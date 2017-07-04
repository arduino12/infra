
# upgrade
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y
sudo rpi-update

# apps
sudo apt-get install git samba samba-common-bin -y

# python3.6
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

# python3 packages
sudo pip3 install --upgrade pip
sudo pip3 install ipython rpyc pygame Pillow
sudo pip3 install --upgrade pyserial

# audo serial port naming
sudo nano /etc/udev/rules.d/90-usb-serial.rules
SUBSYSTEM=="tty",KERNELS=="1-1.2:1.0",SYMLINK+="arduino_uv"
SUBSYSTEM=="tty",KERNELS=="1-1.4:1.0",SYMLINK+="gsm_a6"

# chmodes
sudo chmod +x *.sh
