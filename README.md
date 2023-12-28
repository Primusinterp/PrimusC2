# PrimusC2
*For educational use only*

<p align="center">
  <img width="512" height="512" src="https://github.com/Primusinterp/PrimusC2/assets/65064450/837351fa-2bfe-43a4-ad83-034e985a6bcd">
</p>


A C2 framework built for my bachelors thesis at KEA - Københavns Erhvervsakademi - **WORK IN PROGRESS - expect bugs and missing features**

I work on this project in my spare time when i am not working or doing other security stuff, i am by no means a skilled coding genuis, but i love to learn and improve :) If you have any suggetions for me or feedback i would love to hear it, you can reach me on my socials. 


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
sudo nimble install -y winim 
sudo nimble install -y strenc 
sudo nimble install -y shlex 
sudo nimble install -y terminaltables
```
Run the server from the C2 folder:
```bash
python3 server.py
```

## Features
- Python C2 server 
- Nim Implant 
- Bypass AMSI
- Directory Operations
- Execute .NET assembly - *Unstable and Risky*
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
    listener -g <TYPE>          --> Generate a HTTP or TCP listener
    nimplant -g <TYPE>          --> Generate a compiled exe payload written in nim with advanced capabilities for windows for either TCP or HTTP
    callbacks                   --> List callbacks
    use <callback ID> [use 0]   --> Enter a callback session
    pwsh_cradle                 --> Generate a pwsh cradle for a payload on the payloads server
    kill <sessions_val>         --> Terminate active callback
    payloads                    --> List payloads available on for either transfer or execution
    exit                        --> exit from the server

    Implant Commands
    ------------------------------------------------------------------------------------------------------
    background                  --> Backgrounds current sessions
    exit                        --> Terminate current session
    GetAV                       --> Get the current AV running
    pwsh <COMMAND>              --> Load CLR and run powershell in unmanged runspace 
    execute-ASM <file> <args>   --> Execute .NET assembly from memory   
    ls                          --> List files in current directory
    cd <dir>                    --> Change current working directory
    pwd                         --> Print current working directory
    payloads                    --> List payloads available on for either transfer or execution
    shell <COMMAND>             --> Run Windows CMD commands on target
    sleep <milseconds>          --> Adjust callback time [Default 5000] - HTTP only
    persist <k_name> <payload>  --> Deploy regsitry persistance to run a payload on startup(OPSEC: RISKY) - HTTP only
    download <file>             --> Download file from target(dont use "" around file name or path) - HTTP only

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
- [x] Execute-Assembly 
- [ ] Inline-Assembly
- [x] Encryption of data streams
- [ ] Implementation of smart pipe redirectors with automation
- [x] Download functionality for the implant
- [ ] Upload functionality for the implant
- [x] Directory operations
- [x] HTTP C2 channel 
- [ ] Improve OPSEC
- [ ] Evasion techniques
- [ ] Custom Term Rewriting Macro