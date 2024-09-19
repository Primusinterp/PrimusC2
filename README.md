# PrimusC2
*For educational use only*

<p align="center">
  <img width="512" height="512" src="https://github.com/Primusinterp/PrimusC2/assets/65064450/837351fa-2bfe-43a4-ad83-034e985a6bcd">
</p>


A C2 framework built for my bachelors thesis at KEA - Københavns Erhvervsakademi - **WORK IN PROGRESS - expect bugs and missing features**

I work on this project in my spare time when i am not working or doing other security stuff, i am by no means a skilled coding genuis, but i love to learn and improve :) If you have any suggestions for me or feedback i would love to hear it, you can reach me on my socials. 


## Installation

### The easy way
Docker shenanigans 

Clone and cd into the `PrimusC2` folder
```bash
git clone https://github.com/Primusinterp/PrimusC2.git

cd PrimusC2
```

build all the things!
```bash
sudo docker build -t primusc2 .   
```

Run all the things!
```bash
sudo docker run --network=host -v $(pwd)/C2/Generated_Implants:/app/C2/Generated_Implants/ -it primusc2
```
### The hard way
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
source setup.sh
```

Install nim (use your preferred method) -I recommend [choosenim](https://nim-lang.org/install_unix.html)

Install nim packages:
```
nimble install -y winim 
nimble install -y shlex 
nimble install -y terminaltables
nimble install -y RC4
nimble install -y puppy
nimble install -y byteutils
```
Run the server from the C2 folder:
```bash
sudo -E python3 server.py
```
*If any issues arise while running the nimplant command, try and compile the implant manually to see errors*

- - -


## Features
- Python C2 server 
- Nim Implant 
- Bypass AMSI
- Directory Operations
- Download functionality 
- Execute .NET assembly - *Risky*
- Powershell in unmanaged runspace
- GetAV - current anti-virus products installed 
- Powershell download cradle 
- Dynamic implant generation 
- .exe, .bin & .dll payload formats.
- Automated Redirector setup via Digital Ocean VPS(Smart-Pipe & Dump-Pipe)
- Web Interface
- steal_token


## Usage
The following functionality is implemented in PrimusC2's current state:

*Beware that some features are only supported with the HTTP implant*
```bash
    ------------------------------------------------------------------------------------------------------
    Menu Commands
    ------------------------------------------------------------------------------------------------------
    help <command>              --> Get help for a specific command
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
    help <command>              --> Get help for a specific command
    background                  --> Backgrounds current sessions
    exit                        --> Terminate current session
    GetAV                       --> Get the current AV running
    pwsh <COMMAND>              --> Load CLR and run powershell in unmanaged runspace 
    execute-ASM <file> <args>   --> Execute .NET assembly from memory   
    ls                          --> List files in current directory
    cd <dir>                    --> Change current working directory
    pwd                         --> Print current working directory
    payloads                    --> List payloads available on for either transfer or execution
    shell <COMMAND>             --> Run Windows CMD commands on target
    sleep <milliseconds>        --> Adjust callback time [Default 5000] - HTTP only
    persist <k_name> <payload>  --> Deploy registry persistance to run a payload on startup(OPSEC: RISKY) - HTTP only
    download <file>             --> Download file from target(dont use "" around file name or path) - HTTP only
    steal_token <PID>           --> Steal token from a process
    rev2self                    --> Revert impersonation to original context
    tShell                      --> run CMD.exe commands in the context of the stolen token
    whoami                      --> Get the current user context

```

For more detailed documentation on usage etc. please go to the [docs](https://primusinterp.com/PrimusC2/) 


### Roadmap
- [x] Execute-Assembly 
- [x] Encryption of data streams
- [x] Implementation of smart pipe redirectors with automation
- [x] Download functionality for the implant
- [ ] Upload functionality for the implant
- [x] Directory operations
- [x] HTTP C2 channel 
- [ ] Improve OPSEC
- [x] Rework backend to accommodate a database for persistent storage
- [ ] Evasion techniques
- [ ] Custom Term Rewriting Macro
- [ ] Refactor entire code base into multiple files and maybe classes 
