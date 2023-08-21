#!/bin/bash
echo '########################################################################'
echo '[+] Installing dependecies...'
echo '########################################################################'
sudo apt update -y

sudo apt upgrade -y

sudo apt install curl -y

sudo apt install python3-pip -y


echo -e '\n'
echo '########################################################################'
echo '[*] Installing nim...'
echo '########################################################################'

sudo apt install nim -y


echo '[+] Nim Installed'

source ~/.profile


echo -e '\n'
echo '########################################################################'
echo '[*] Installing mingW64 compiler...'
echo '########################################################################'
sudo apt -y install mingw-w64

echo -e '\n'
echo '########################################################################'
echo '[*] Installing Terraform...'
echo '########################################################################'
sudo apt -y install terraform



echo -e '\n'
echo '########################################################################'
echo '[*] Installing python requirements...'
echo '########################################################################'
pip3 install -r requirements.txt

