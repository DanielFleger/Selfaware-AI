// B-114 (19.10.2026): Wie fuehrt das Spiel einen eingereihten Spielbefehl aus, und fuer welchen Spieler?
// Sucht alle Schreibzugriffe auf protocolInvokerPlayerID (GameSynchronyState 0x0191D768 + 0x109E70 = 0x01A275D8) und
// listet alle Zugriffe auf currentPlayerSlotID (+0x109E74 = 0x01A275DC); dekompiliert jede Funktion, die den Ausloeser
// setzt. Nur lesen (-readOnly). Ausgabe in die Datei aus der Umgebung DUMP_AUS.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class DumpBefehlAusfuehren extends GhidraScript {
    PrintWriter aus;

    void zeile(String s) { aus.println(s); }

    public void run() throws Exception {
        aus = new PrintWriter(new OutputStreamWriter(new FileOutputStream(System.getenv("DUMP_AUS")), "UTF-8"));
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        Set<Function> setzer = new LinkedHashSet<>();
        String[][] ziele = { { "0x01A275D8", "protocolInvokerPlayerID" }, { "0x01A275DC", "currentPlayerSlotID" },
                             { "0x01A275D4", "Nachbar -4 (DPLAYX_ReceivedPlayerID?)" } };
        for (String[] z : ziele) {
            Address a = currentProgram.getAddressFactory().getAddress(z[0]);
            zeile("### Zugriffe auf " + z[0] + " " + z[1]);
            for (Reference r : getReferencesTo(a)) {
                Function f = getFunctionContaining(r.getFromAddress());
                zeile("   " + r.getFromAddress() + "  " + r.getReferenceType() + "  " + (f != null ? f.getName(true) + " @ " + f.getEntryPoint() : "-"));
                if (z[0].equals("0x01A275D8") && r.getReferenceType().isWrite() && f != null) setzer.add(f);
            }
            zeile("");
        }
        for (Function f : setzer) {
            zeile("// ================= " + f.getName(true) + " @ " + f.getEntryPoint() + " =================");
            DecompileResults res = dec.decompileFunction(f, 120, monitor);
            zeile(res.decompileCompleted() ? res.getDecompiledFunction().getC() : "(Dekompilieren fehlgeschlagen)");
        }
        aus.close();
    }
}
