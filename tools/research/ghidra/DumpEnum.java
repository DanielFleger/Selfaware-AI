// Werte eines Aufzaehlungstyps (Enum) aus der OpenSHC-Referenz: DUMP_NAMEN (Teilstrings, Komma) -> DUMP_AUS.
// Angelegt 19.10.2026 fuer die Ansicht-Werte (GameCore.currentMenuViewType) des SamurAI-Waechters. Nur lesen.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import java.io.*;
import java.util.*;

public class DumpEnum extends GhidraScript {
    public void run() throws Exception {
        PrintWriter aus = new PrintWriter(new OutputStreamWriter(new FileOutputStream(System.getenv("DUMP_AUS")), "UTF-8"));
        String[] namen = System.getenv("DUMP_NAMEN").split(",");
        Iterator<DataType> it = currentProgram.getDataTypeManager().getAllDataTypes();
        while (it.hasNext()) {
            DataType t = it.next();
            if (!(t instanceof ghidra.program.model.data.Enum)) continue;
            boolean treffer = false;
            for (String s : namen) if (!s.isEmpty() && t.getName().toLowerCase().contains(s.trim().toLowerCase())) treffer = true;
            if (!treffer) continue;
            ghidra.program.model.data.Enum e = (ghidra.program.model.data.Enum) t;
            aus.println("### " + e.getName() + "  " + e.getCategoryPath());
            long[] werte = e.getValues();
            Arrays.sort(werte);
            for (long v : werte) aus.println(String.format("   %4d  %s", v, e.getName(v)));
        }
        aus.close();
    }
}
