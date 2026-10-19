// Listet alle Funktionen, deren Name (ohne Gross/Klein) eines der Muster aus SHC_MUSTER (kommagetrennt) enthaelt.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
public class FnMuster extends GhidraScript {
  public void run() throws Exception {
    String[] m = System.getenv("SHC_MUSTER").toLowerCase().split(",");
    FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
    while (it.hasNext()) { Function f = it.next(); String n = f.getName(true).toLowerCase();
      for (String s : m) if (n.contains(s.trim())) { println("FN " + f.getEntryPoint() + " " + f.getName(true)); break; } }
  }
}
