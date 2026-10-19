// Maschinenbefehle (mit Bytes) von Funktionen nach Namen (Umgebung DUMP_NAMEN, Komma) in DUMP_AUS; dazu die Aufrufer
// (Adresse + 3 Befehle davor), damit die Aufrufart sichtbar ist. Nur lesen. Angelegt fuer B-94 (19.10.2026).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;

public class DumpAsm extends GhidraScript {
    PrintWriter aus;

    String befehl(Instruction i) throws Exception {
        StringBuilder b = new StringBuilder();
        for (byte x : i.getBytes()) b.append(String.format("%02X ", x));
        return String.format("   %s  %-24s %s", i.getAddress(), b.toString(), i.toString());
    }

    public void run() throws Exception {
        aus = new PrintWriter(new OutputStreamWriter(new FileOutputStream(System.getenv("DUMP_AUS")), "UTF-8"));
        String[] namen = System.getenv("DUMP_NAMEN").split(",");
        Listing l = currentProgram.getListing();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            String n = f.getName(true);
            boolean treffer = false;
            for (String s : namen) if (!s.isEmpty() && n.contains(s.trim())) treffer = true;
            if (!treffer) continue;
            aus.println("### " + n + " @ " + f.getEntryPoint() + "  Aufrufart: " + f.getCallingConventionName()
                        + "  Stapelbereinigung: " + f.getStackPurgeSize());
            for (Instruction i : l.getInstructions(f.getBody(), true)) aus.println(befehl(i));
            aus.println("   -- Aufrufer:");
            for (Reference r : getReferencesTo(f.getEntryPoint())) {
                Instruction i = l.getInstructionAt(r.getFromAddress());
                if (i == null) continue;
                Function g = getFunctionContaining(r.getFromAddress());
                aus.println("   " + r.getFromAddress() + " in " + (g != null ? g.getName(true) : "-"));
                Instruction v = i;
                for (int k = 0; k < 3 && v.getPrevious() != null; k++) v = v.getPrevious();
                for (int k = 0; k < 5 && v != null; k++) { aus.println("     " + befehl(v)); v = v.getNext(); }
            }
            aus.println();
        }
        aus.close();
    }
}
