// Dekompiliert alle Funktionen, deren Name auf das Muster SHC_MUSTER (Regex, ohne Gross/Klein) passt, nach SHC_OUT.
// 07.10.2026: Steuer-Einzug suchen (Gibt es eine Regel, ab der kein Steuergold mehr kommt?)
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.PrintWriter;
import java.util.regex.Pattern;

public class DekompMuster extends GhidraScript {
    @Override
    public void run() throws Exception {
        Pattern p = Pattern.compile(System.getenv("SHC_MUSTER"), Pattern.CASE_INSENSITIVE);
        PrintWriter w = new PrintWriter(System.getenv("SHC_OUT"), "UTF-8");
        DecompInterface d = new DecompInterface();
        d.openProgram(currentProgram);
        FunctionIterator fi = currentProgram.getFunctionManager().getFunctions(true);
        int n = 0;
        while (fi.hasNext()) {
            Function f = fi.next();
            String name = f.getName(true);
            if (!p.matcher(name).find()) continue;
            n++;
            w.println("// ================= " + name + " @ " + f.getEntryPoint() + " =================");
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            if (r.decompileCompleted()) w.println(r.getDecompiledFunction().getC());
            else w.println("// nicht dekompiliert: " + r.getErrorMessage());
        }
        w.println("// Treffer: " + n);
        w.close();
        println("DekompMuster: " + n + " Funktionen");
    }
}
