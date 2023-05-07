# Bachelor_C2
A C2 framework build for my bachelors thesis


## Installation 
To get the dependencies installed and the server ready to go, it's needed to run the setup script and a few manual commands.

git clone `PrimusC2`
```bash
git clone https://github.com/Primusinterp/PrimusC2.git
```
cd into `PrimusC2` and chmod the bash script
```bash
sudo chmod +x setup.sh
```
run the setup script with source
```bash
source setup.py
```
Install nim packages:
```
sudo nimble install -y winim strenc
```
Run the server from the C2 folder:
```bash
python3 server.py
```
