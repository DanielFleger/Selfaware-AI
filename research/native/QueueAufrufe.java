// Fuer jeden Aufruf von queueCommand (0x00489100): steht in den 20 Anweisungen davor
// "PUSH SHC_NR" (hex), dann 30 Anweisungen davor ausgeben + Funktionsname.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
public class QueueAufrufe extends GhidraScript {
  public void run() throws Exception {
    String nr = System.getenv("SHC_NR").toLowerCase();
    Address q = currentProgram.getAddressFactory().getAddress("0x00489100");
    ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(q);
    Listing l = currentProgram.getListing();
    while (ri.hasNext()) {
      Reference r = ri.next(); if (!r.getReferenceType().isCall()) continue;
      Address c = r.getFromAddress();
      Instruction i = l.getInstructionAt(c); if (i == null) continue;
      Instruction p = i.getPrevious(); boolean treffer = false;
      for (int k = 0; k < 6 && p != null; k++) { if (p.toString().toLowerCase().equals("push " + nr)) treffer = true; p = p.getPrevious(); }
      if (!treffer) continue;
      Function f = getFunctionContaining(c);
      println("=== Aufruf bei " + c + " in " + (f == null ? "?" : f.getName() + " @ " + f.getEntryPoint()));
      Instruction s = i; for (int k = 0; k < 30 && s.getPrevious() != null; k++) s = s.getPrevious();
      while (s != null && s.getAddress().compareTo(c) <= 0) { println("  " + s.getAddress() + "  " + s.toString()); s = s.getNext(); }
    }
  }
}
