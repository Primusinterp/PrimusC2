# PrimusC2
*For educational use only*

A C2 framework built for my bachelors thesis at KEA - Københavns Erhvervsakademi - **WORK IN PROGRESS - expect bugs and missing features**


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

## Features
- Python C2 server 
- Nim Implant 
- Bypass AMSI
- Powershell in unmanged runspace
- GetAV - current anti-virus products installed 
- Powershell download cradle 
- Dynamic implant generation 
- Automated Redirector setup via Digital Ocean VPS

## Usage
The following functionality is implemented in PrimusC2's current state:
```bash
    ------------------------------------------------------------------------------------------------------
    Menu Commands
    ------------------------------------------------------------------------------------------------------
    listeners -g                --> Generate a new listener on desired interface
    nimplant                    --> Generate a compiled exe payload written in nim with advanced capabilities for windows
    sessions -l                 --> List callbacks
    sessions -i <sessions_val>  --> Enter a callback session
    use <sessions_val>          --> Enter a callback session
    pwsh_cradle                 --> Generate a pwsh cradle for a payload on the payloads server
    kill <sessions_val>         --> Terminate active callback
    exit                        --> exit from the server

    Session Commands
    ------------------------------------------------------------------------------------------------------
    background                  --> Backgrounds current sessions
    exit                        --> Terminate current session
    GetAV                       --> Get the current AV running
    pwsh <COMMAND>              --> Load CLR and run powershell in unmanged runspace 
```

To get started(simple):
1. Generate a listener `listeners -g`
2. Generate an implant `nimplant`
3. Transfer the implant to the target and await callback
4. Happy hacking :)

To get started(redirector):
1. Generate a listener `listeners -g`
2. Choose `Listener with redirector` 
3. Input data and wait for redirector provisioning 
4. Generate an implant `nimplant`
5. Choose `Other IP` and input the public IP of the redirector (Can be found after listener generation)
6. Transfer the implant to the target and await callback.
7. Happy hacking :) 


### Roadmap
- Execute-Assembly 
- Inline-Assembly
- Encryption of data streams
- Implemneation of smart pipe redirectors with automation
- Linux implant
- Upload/download functionality for the implant
