from colorama import Fore, Back, Style



def help():
    help_var = Fore.CYAN + '''
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
    sleep <milliseconds>          --> Adjust callback time [Default 5000] - HTTP only
    persist <k_name> <payload>  --> Deploy registry persistance to run a payload on startup(OPSEC: RISKY) - HTTP only
    download <file>             --> Download file from target(dont use "" around file name or path) - HTTP only
    '''
    print(help_var)
    return help_var

def help_implant():
    help_var = Fore.CYAN +'''
    ------------------------------------------------------------------------------------------------------
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
    sleep <milliseconds>          --> Adjust callback time [Default 5000] - HTTP only
    persist <k_name> <payload>  --> Deploy registry persistance to run a payload on startup(OPSEC: RISKY) - HTTP only
    download <file>             --> Download file from implant(dont use "" around file name or path) - HTTP only
    '''
    print(help_var)
    return help_var

def help_implant_GUI():
    help_var = '''
    ------------------------------------------------------------------------------------------------------
    Implant Commands
    ------------------------------------------------------------------------------------------------------
    help <command>              --> Get help for a specific command
    exit                        --> Terminate current session
    GetAV                       --> Get the current AV running
    pwsh <COMMAND>              --> Load CLR and run powershell in unmanaged runspace 
    execute-ASM <file> <args>   --> Execute .NET assembly from memory
    ls                          --> List files in current directory
    cd <dir>                    --> Change current working directory
    pwd                         --> Print current working directory
    payloads                    --> List payloads available on for either transfer or execution
    shell <COMMAND>             --> Run Windows CMD commands on target
    sleep <milliseconds>          --> Adjust callback time [Default 5000] - HTTP only
    persist <k_name> <payload>  --> Deploy registry persistance to run a payload on startup(OPSEC: RISKY) - HTTP only
    download <file>             --> Download file from implant(dont use "" around file name or path) - HTTP only
    '''
    print(help_var)
    return help_var


def background_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: background
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Backgrounds the current session
{Fore.YELLOW}Usage:{Fore.RESET} background
'''
    print(help_var)
    return help_var
    
def persist_help():
    var_help = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: persist
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Deploy registry persistence to run a payload on startup
{Fore.YELLOW}Usage:{Fore.RESET} persist <k_name> <payload>
{Fore.YELLOW}Note:{Fore.RESET} HTTP only 
{Fore.YELLOW}OPSEC:{Fore.RESET} RISKY

          
{Fore.YELLOW}Example:{Fore.RESET} persist myregkey mypayload.exe
'''
    print(var_help)
    return var_help


    
def exit_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: exit
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Terminates the current session
{Fore.YELLOW}Usage:{Fore.RESET} exit
'''
    print(help_var)
    return help_var
    
def callbacks_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: callbacks
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} List callbacks
{Fore.YELLOW}Usage:{Fore.RESET} callbacks
'''
    print(help_var)
    return help_var

def use_help():
    help_var = Fore.YELLOW + f'''   
------------------------------------------------------------------------------------------------------
Synopsis: use
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Interact with a specific callback
{Fore.YELLOW}Usage:{Fore.RESET} use <callback ID>
    
{Fore.YELLOW}Example:{Fore.RESET} use 0
'''
    print(help_var)
    return help_var

def pwsh_cradle_help():
    help_var = Fore.YELLOW + f'''   
------------------------------------------------------------------------------------------------------
Synopsis: pwsh_cradle
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Generate pwsh cradles for the payload on the payloads server. This can be used to transfer payloads to the target.
{Fore.YELLOW}Usage:{Fore.RESET} pwsh_cradle
'''
    print(help_var)
    return help_var

    

def sleep_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: sleep
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Adjust callback time for the implant [Default 5000] 
{Fore.YELLOW}Usage:{Fore.RESET} sleep <milliseconds>
{Fore.YELLOW}Note:{Fore.RESET} HTTP only
          
{Fore.YELLOW}Example:{Fore.RESET} sleep 10000
'''
    print(help_var)
    return help_var

    
def download_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: download
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Download file from implant
{Fore.YELLOW}Usage:{Fore.RESET} download <file>
{Fore.YELLOW}Note:{Fore.RESET} HTTP only - can be unstable and error out on some file types.\ndont use "" around file name or path

          
{Fore.YELLOW}Example:{Fore.RESET} download password.txt
'''
    print(help_var)
    return help_var
    
def kill_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: kill
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Terminate active callback
{Fore.YELLOW}Usage:{Fore.RESET} kill <callback ID>
          
{Fore.YELLOW}Example:{Fore.RESET} kill 0
'''
    print(help_var)
    return help_var

def nimplant_help():
    help_var = Fore.YELLOW + f'''  
------------------------------------------------------------------------------------------------------
Synopsis: nimplant -g
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Generate a compiled .exe payload written in Nim with advanced capabilities for windows for either TCP or HTTP.
{Fore.YELLOW}Usage:{Fore.RESET} nimplant -g <TYPE>
{Fore.YELLOW}Options:{Fore.RESET}
  >>TCP
  >>HTTP
{Fore.YELLOW}Note:{Fore.RESET} The HTTP implant is stable and reliable. The TCP implant can be unstable and unreliable.

          
{Fore.YELLOW}Example:{Fore.RESET} nimplant -g HTTP
'''
    print(help_var)
    
def listener_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: listener -g
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Generate a listener for the server to listen for incoming callbacks
{Fore.YELLOW}Usage:{Fore.RESET} listener -g <TYPE>
{Fore.YELLOW}Options:{Fore.RESET}
  >>TCP
  >>HTTP
{Fore.YELLOW}Note:{Fore.RESET} The HTTP listener is stable and reliable. The TCP listener can be unstable and unreliable.
          

{Fore.YELLOW}Example:{Fore.RESET} listener -g HTTP

------------------------------------------------------------------------------------------------------
{Fore.YELLOW}HTTPS Redirector listener:{Fore.RESET}
{Fore.YELLOW}Prerequisites:{Fore.RESET}
    1. DigitalOcean account + API key.
    2. Cloudflare account + API TOKEN with Zone.DNS permissions.
    3. Own a Domain name.
    4. Add domain(s) as a site on cloudflare and add the custom nameservers to the domain registrar.{Fore.RESET}

{Fore.YELLOW}Syntax: listener -g HTTP{Fore.RESET}
        choose option 2. 
        Enter the domain name with a subdomain: foo.example.com
    
{Fore.YELLOW}Wait for VPS to be created and the listener to be generated.{Fore.RESET}
    run: nimplant -g HTTP
        Choose option 3.
'''
    print(help_var)
    return help_var


def GetAV_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: GetAV
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Get the current AV running on the target
{Fore.YELLOW}Usage:{Fore.RESET} GetAV
'''
    print(help_var)
    return help_var

def pwsh_help():
    help_var = Fore.YELLOW + f'''  
------------------------------------------------------------------------------------------------------
Synopsis: pwsh 
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Load CLR and run powershell in unmanaged runspace. This enables you to deploy powershell functionality without the need for powershell.exe.
{Fore.YELLOW}Usage:{Fore.RESET} pwsh <COMMAND>
{Fore.YELLOW}Note:{Fore.RESET} Use "" around paths with space. 
          
{Fore.YELLOW}Example:{Fore.RESET} pwsh whoami /all
'''
    print(help_var)
    return help_var
    
def execute_ASM_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: execute-ASM 
------------------------------------------------------------------------------------------------------

{Fore.YELLOW}Description:{Fore.RESET} 
Enables the operator to execute .NET assembly from memory without the need to drop anything to disk. The implementation handles the conversion to a byte array automatically.
Place the .NET assembly in the generated 'PrimusC2/C2/Payloads' directory. The assembly can now be executed from memory remotely with the syntax below.

{Fore.YELLOW}Usage:{Fore.RESET} execute-ASM <file> <args>
{Fore.YELLOW}Note:{Fore.RESET}  Run the 'Payloads' command to add all assemblies in the Payloads folder to the autocomplete list.
          
{Fore.YELLOW}Example:{Fore.RESET} execute-ASM Rubeus.exe kerberoast
'''
    print(help_var)
    return help_var
    
def ls_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: ls
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} List files in the current directory
{Fore.YELLOW}Usage:{Fore.RESET} ls
'''
    print(help_var)
    return help_var
    
def cd_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: cd
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Change the current working directory
{Fore.YELLOW}Usage:{Fore.RESET} cd <dir>
'''
    print(help_var)
    return help_var
    
def pwd_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: pwd
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Print the current working directory
{Fore.YELLOW}Usage:{Fore.RESET} pwd
'''
    print(help_var)
    return help_var
    
def payloads_help():
    help_var = Fore.YELLOW + f'''   
------------------------------------------------------------------------------------------------------
Synopsis: payloads
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} 
List payloads available in 'PrimusC2/C2/Payloads'. The 'Payloads' folder is the base for the payloads server, pwsh_cradle and execute-ASM. This means-
that this is the location that you should place your payloads for either transfer or in-memory execution with 'execute-ASM'.

{Fore.YELLOW}Usage:{Fore.RESET} payloads
'''
    print(help_var)
    return help_var
    
def shell_help():
    help_var = Fore.YELLOW + f'''
------------------------------------------------------------------------------------------------------
Synopsis: shell
------------------------------------------------------------------------------------------------------
{Fore.YELLOW}Description:{Fore.RESET} Run Windows CMD commands on target
{Fore.YELLOW}Usage:{Fore.RESET} shell <COMMAND>
          
{Fore.YELLOW}Example:{Fore.RESET} shell ipconfig
'''
    print(help_var)
    return help_var
    

    

          
          
    