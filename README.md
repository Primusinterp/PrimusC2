# PrimusC2
*For educational use only*

<p align="center">
  <img width="512" height="512" src="https://github.com/Primusinterp/PrimusC2/assets/65064450/837351fa-2bfe-43a4-ad83-034e985a6bcd">
</p>


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

### Powershell
The framework is very powershell dependent - and it offers two ways of executing powershell. Either with `ExecProcess` in Nim or through Powershell in an unmanged runspace.

`ExecProcess` is utilizing `Powershell.exe` to execute commands, and it makes a lot of *noise*. Powershell in an unmanged runspace is more stealthy, but has the limitation that it only takes one parameter.

To use the `ExecProcess` method you simply need to type in the `powershell` command when you have started the interaction with the target, as seen below:

![image](https://github.com/Primusinterp/PrimusC2/assets/65064450/87f49b76-4bdb-4e95-ba1a-5eab7a1bd4f1)

To use Powershell in an unmanged runspace, you need to use the prefix `pwsh` and then the `command`, as seen below:
![image](https://github.com/Primusinterp/PrimusC2/assets/65064450/9fb146a3-a97c-467a-bfc9-f9087020a3a9)

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

    Implant Commands
    ------------------------------------------------------------------------------------------------------
    background                  --> Backgrounds current sessions
    persist                     --> Establish persistance trough registry keys(needs to be in the same
                                    dir as the implant on target disk)
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
- Implementation of smart pipe redirectors with automation
- Linux implant
- Upload/download functionality for the implant
