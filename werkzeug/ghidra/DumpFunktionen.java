// Dekompiliert Funktionen nach Namen (Teilstring, Namen durch Komma in der Umgebung DUMP_NAMEN) in die Datei DUMP_AUS.
// Nur lesen (-readOnly). Angelegt fuer B-114 (19.10.2026).
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
import java.util.*;

public class DumpFunktionen extends GhidraScript {
    public void run() throws Exception {
        PrintWriter aus = new PrintWriter(new OutputStreamWriter(new FileOutputStream(System.getenv("DUMP_AUS")), "UTF-8"));
        String[] namen = System.getenv("DUMP_NAMEN").split(",");
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            String n = f.getName(true);
            for (String s : namen) {
                if (!s.isEmpty() && n.contains(s.trim())) {
                    aus.println("// ================= " + n + " @ " + f.getEntryPoint() + " =================");
                    DecompileResults r = dec.decompileFunction(f, 120, monitor);
                    aus.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "(Dekompilieren fehlgeschlagen)");
                    break;
                }
            }
        }
        aus.close();
    }
}
