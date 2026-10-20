// B-95 (19.10.2026): Datenstrukturen aus der OpenSHC-Referenz fuer die Spielkarte.
// DUMP_NAMEN leer -> Liste aller Strukturen (Name, Groesse) mit Treffern fuer DUMP_SUCHE (Komma-Teilstrings);
// DUMP_NAMEN gesetzt -> je genau benannter Struktur alle Felder (Abstand, Groesse, Typ, Name, Kommentar).
// Dazu die globalen Variablen (Symbole), deren Datentyp eine der Strukturen ist. Nur lesen. Ausgabe nach DUMP_AUS.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class DumpStrukturen extends GhidraScript {
    public void run() throws Exception {
        PrintWriter aus = new PrintWriter(new OutputStreamWriter(new FileOutputStream(System.getenv("DUMP_AUS")), "UTF-8"));
        String namen = System.getenv("DUMP_NAMEN");
        String suche = System.getenv("DUMP_SUCHE");
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        List<Structure> alle = new ArrayList<>();
        Iterator<Structure> it = dtm.getAllStructures();
        while (it.hasNext()) alle.add(it.next());
        if (namen == null || namen.isEmpty()) {
            String[] s = (suche == null ? "" : suche).split(",");
            for (Structure st : alle) {
                for (String t : s) {
                    if (!t.isEmpty() && st.getName().toLowerCase().contains(t.trim().toLowerCase())) {
                        aus.println(String.format("%-60s %8d  %s", st.getName(), st.getLength(), st.getCategoryPath()));
                        break;
                    }
                }
            }
        } else {
            Set<String> gewollt = new HashSet<>(Arrays.asList(namen.split(",")));
            for (Structure st : alle) {
                if (!gewollt.contains(st.getName())) continue;
                aus.println("### " + st.getName() + "  Groesse " + st.getLength() + "  " + st.getCategoryPath());
                for (DataTypeComponent c : st.getDefinedComponents()) {
                    aus.println(String.format("   +0x%05X %6d  %-34s %-40s %s", c.getOffset(), c.getLength(),
                        c.getDataType().getDisplayName(), c.getFieldName() == null ? "-" : c.getFieldName(),
                        c.getComment() == null ? "" : c.getComment().replace("\n", " ")));
                }
                aus.println("   -- globale Variablen dieses Typs:");
                DataIterator di = currentProgram.getListing().getDefinedData(true);
                int n = 0;
                while (di.hasNext() && n < 20) {
                    Data d = di.next();
                    DataType t = d.getDataType();
                    if (t.getName().equals(st.getName()) || (t instanceof Array && ((Array) t).getDataType().getName().equals(st.getName()))) {
                        aus.println("   " + d.getAddress() + "  " + t.getDisplayName() + "  " + (d.getLabel() == null ? "" : d.getLabel()));
                        n++;
                    }
                }
                aus.println();
            }
        }
        aus.close();
    }
}
