// Aufrufkette nach oben (B-95 Abschnitt "Takt", 20.10.2026): fuer jede Funktion aus DUMP_NAMEN (Teilstring, durch Komma)
// alle Aufrufer bis zur Tiefe DUMP_TIEFE (Standard 6), je Ebene eingerueckt, mit Aufrufstelle. Dazu je Aufrufer die
// Reihenfolge seiner eigenen Aufrufe (was davor und danach im selben Takt laeuft). Nur lesen (-readOnly).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import java.io.*;
import java.util.*;

public class DumpAufrufer extends GhidraScript {
    PrintWriter aus;
    FunctionManager fm;
    Set<Address> gesehen = new HashSet<>();
    int tiefeMax;

    public void run() throws Exception {
        aus = new PrintWriter(new OutputStreamWriter(new FileOutputStream(System.getenv("DUMP_AUS")), "UTF-8"));
        String t = System.getenv("DUMP_TIEFE");
        tiefeMax = t == null ? 6 : Integer.parseInt(t);
        fm = currentProgram.getFunctionManager();
        String[] namen = System.getenv("DUMP_NAMEN").split(",");
        for (Function f : fm.getFunctions(true)) {
            for (String s : namen) {
                if (!s.trim().isEmpty() && f.getName(true).contains(s.trim())) {
                    aus.println("=== Aufrufer von " + f.getName(true) + " @ " + f.getEntryPoint());
                    gesehen.clear();
                    hoch(f, 1);
                    aus.println();
                }
            }
        }
        aus.println("=== Reihenfolge der Aufrufe in den gefundenen Aufrufern");
        for (Address a : new TreeSet<>(alleAufrufer)) {
            Function f = fm.getFunctionAt(a);
            if (f == null) continue;
            aus.println("--- " + f.getName(true) + " @ " + a);
            InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
            while (it.hasNext()) {
                Instruction ins = it.next();
                if (!ins.getFlowType().isCall()) continue;
                for (Address z : ins.getFlows()) {
                    Function g = fm.getFunctionAt(z);
                    aus.println("    " + ins.getAddress() + "  ruft " + (g == null ? z.toString() : g.getName(true)));
                }
            }
        }
        aus.close();
    }

    Set<Address> alleAufrufer = new HashSet<>();

    void hoch(Function f, int tiefe) {
        if (tiefe > tiefeMax || !gesehen.add(f.getEntryPoint())) return;
        for (Reference r : getReferencesTo(f.getEntryPoint())) {
            if (!r.getReferenceType().isCall() && !r.getReferenceType().isData()) continue;
            Function g = fm.getFunctionContaining(r.getFromAddress());
            String name = g == null ? "(keine Funktion)" : g.getName(true) + " @ " + g.getEntryPoint();
            aus.println("  ".repeat(tiefe) + name + "   [" + r.getReferenceType() + " bei " + r.getFromAddress() + "]");
            if (g != null) {
                alleAufrufer.add(g.getEntryPoint());
                hoch(g, tiefe + 1);
            }
        }
    }
}
