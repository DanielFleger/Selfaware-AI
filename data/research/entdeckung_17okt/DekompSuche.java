// Dekompiliert alle Funktionen zwischen SHC_VON und SHC_BIS und schreibt nach SHC_OUT nur die Zeilen (mit 2 Zeilen Umfeld),
// die eines der Woerter aus SHC_WORTE (Komma-Liste) enthalten. 17.10.2026: Wo wird eine Assassine sichtbar?
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.PrintWriter;

public class DekompSuche extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address von = toAddr(System.getenv("SHC_VON")), bis = toAddr(System.getenv("SHC_BIS"));
        String[] worte = System.getenv("SHC_WORTE").split(",");
        PrintWriter w = new PrintWriter(System.getenv("SHC_OUT"), "UTF-8");
        DecompInterface d = new DecompInterface();
        d.openProgram(currentProgram);
        int n = 0, treffer = 0;
        for (Function f : currentProgram.getFunctionManager().getFunctions(new AddressSet(von, bis), true)) {
            n++;
            DecompileResults r = d.decompileFunction(f, 60, monitor);
            if (!r.decompileCompleted()) continue;
            String[] z = r.getDecompiledFunction().getC().split("\n");
            boolean kopf = false;
            for (int i = 0; i < z.length; i++) {
                boolean hit = false;
                for (String wo : worte) if (z[i].contains(wo.trim())) { hit = true; break; }
                if (!hit) continue;
                if (!kopf) { w.println("// ===== " + f.getName() + " @ " + f.getEntryPoint()); kopf = true; treffer++; }
                for (int k = Math.max(0, i - 2); k <= Math.min(z.length - 1, i + 2); k++) w.println((k == i ? ">> " : "   ") + z[k]);
                w.println("   --");
            }
            w.flush();
        }
        w.close();
        println("[DekompSuche] " + n + " Funktionen, " + treffer + " mit Treffer");
    }
}
