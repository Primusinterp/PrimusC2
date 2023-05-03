
import winim/clr
import sugar
import strformat



echo "[*] Installed .NET versions"
for v in clrVersions():
    echo fmt"    \--- {v}"
echo "\n"

echo ""

var assembly = load(buf)
dump assembly


var arr = toCLRVariant([""], VT_BSTR) # Passing no arguments
#assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))

arr = toCLRVariant(["-h"], VT_BSTR) # Actually passing some args
assembly.EntryPoint.Invoke(nil, toCLRVariant([arr]))