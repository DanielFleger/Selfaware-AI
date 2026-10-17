// Mehrere Tabellen auf einmal: je Adresse (SHC_AS, Komma-Liste "name:adresse:anzahl") die Werte und wer sie liest.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

public class DumpArrListe extends GhidraScript {
    public void run() throws Exception {
        for (String teil : System.getenv("SHC_AS").split(",")) {
            String[] p = teil.split(":");
            Address a = currentProgram.getAddressFactory().getAddress(p[1]);
            int n = Integer.parseInt(p[2]);
            println("== " + p[0] + " @ " + a);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) {
                int v;
                try { v = getInt(a.add((long) i * 4)); } catch (Exception e) { v = -999999; }
                sb.append(i).append("=").append(v).append(" ");
            }
            println("   WERTE " + sb.toString());
            Set<String> ge = new LinkedHashSet<>();
            for (int i = 0; i < n; i++) {
                for (Reference r : getReferencesTo(a.add((long) i * 4))) {
                    Function f = getFunctionContaining(r.getFromAddress());
                    ge.add("[" + i + "] " + (f == null ? "?" : f.getName() + " @" + f.getEntryPoint()) + "  " + r.getReferenceType() + " von " + r.getFromAddress());
                }
            }
            for (String x : ge) println("   " + x);
        }
    }
}
