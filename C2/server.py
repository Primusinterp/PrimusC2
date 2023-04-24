import socket
import subprocess
import os


def listener_handler(): # Function to handle incoming connections and send bytes over the socket
    sock.bind((host_ip, host_port))
    print('[+] Awaiting connection from client...')
    sock.listen()
    remote_target, remote_ip = sock.accept()
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

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '127.0.0.1'
host_port = 4444
listener_handler()

