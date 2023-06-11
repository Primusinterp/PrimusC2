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

curl https://nim-lang.org/choosenim/init.sh -sSf | sh -s -- -y


export PATH=$HOME/.nimble/bin:$PATH
echo export PATH=$HOME/.nimble/bin:$PATH >> ~/.profile


echo '[+] Nim Installed'

source ~/.profile


echo -e '\n'
echo '########################################################################'
echo '[*] Installing mingW64 compiler...'
echo '########################################################################'
sudo apt -y install mingw-w64



echo -e '\n'
echo '########################################################################'
echo '[*] Installing python requirements...'
echo '########################################################################'
pip3 install -r ~/PrimusC2/requirements.txt

echo -e '\n'
echo '[*] Please reload the terminal or source "~/.profile" to make nim availble in PATH'
