// Local evidence export. Invoke only against a copied project with -readOnly -noanalysis.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import com.google.gson.Gson;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public class KnowledgeExport extends GhidraScript {
    Gson gson = new Gson();
    Map<String,Object> row(Object... kv) {
        Map<String,Object> m=new LinkedHashMap<>();
        for(int i=0;i<kv.length;i+=2)m.put((String)kv[i],kv[i+1]);
        return m;
    }
    void save(Path p,Object o)throws Exception {
        Path t=p.resolveSibling(p.getFileName()+".tmp");
        Files.writeString(t,gson.toJson(o),StandardCharsets.UTF_8);
        Files.move(t,p,StandardCopyOption.REPLACE_EXISTING);
    }
    String hash(byte[] b)throws Exception {return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));}
    List<Object> ranges(AddressSetView set) {
        List<Object> a=new ArrayList<>();
        for(AddressRange r:set.getAddressRanges())a.add(row("start",r.getMinAddress().toString(),"end",r.getMaxAddress().toString(),"size",r.getLength()));
        return a;
    }
    public void run()throws Exception {
        String[] args=getScriptArgs();
        Path root=Paths.get(args[0]); Files.createDirectories(root);
        int limit=args.length>1?Integer.parseInt(args[1]):0;
        String revision=args.length>2?args[2]:"unversioned";
        String identity=currentProgram.getExecutableSHA256()+"|"+revision;
        save(root.resolve("program.json"),row("name",currentProgram.getName(),"source_path",currentProgram.getExecutablePath(),"sha256",currentProgram.getExecutableSHA256(),"language",currentProgram.getLanguageID().toString(),"compiler",currentProgram.getCompilerSpec().getCompilerSpecID().toString(),"image_base",currentProgram.getImageBase().toString(),"identity",identity,"function_count",currentProgram.getFunctionManager().getFunctionCount()));
        List<Object> blocks=new ArrayList<>(); AddressSet executable=new AddressSet();
        for(MemoryBlock b:currentProgram.getMemory().getBlocks()) {
            blocks.add(row("name",b.getName(),"start",b.getStart().toString(),"end",b.getEnd().toString(),"size",b.getSize(),"execute",b.isExecute(),"initialized",b.isInitialized()));
            if(b.isExecute())executable.add(b.getStart(),b.getEnd());
        }
        save(root.resolve("blocks.json"),blocks);
        List<Object> symbols=new ArrayList<>();
        for(Symbol s:currentProgram.getSymbolTable().getAllSymbols(true))symbols.add(row("address",s.getAddress().toString(),"name",s.getName(true),"kind",s.getSymbolType().toString(),"source",s.getSource().toString()));
        save(root.resolve("symbols.json"),symbols);
        List<Object> types=new ArrayList<>();
        Iterator<DataType> ti=currentProgram.getDataTypeManager().getAllDataTypes();
        while(ti.hasNext()){DataType t=ti.next();types.add(row("path",t.getPathName(),"length",t.getLength(),"definition",t.toString()));}
        save(root.resolve("types.json"),types);
        List<Object> strings=new ArrayList<>();
        for(Data d:currentProgram.getListing().getDefinedData(true))if(d.hasStringValue())strings.add(row("address",d.getAddress().toString(),"value",String.valueOf(d.getValue()),"type",d.getDataType().getPathName()));
        save(root.resolve("strings.json"),strings);
        AddressSet covered=new AddressSet(); List<Object> index=new ArrayList<>();
        for(Function f:currentProgram.getFunctionManager().getFunctions(true)){
            covered.add(f.getBody()); index.add(row("address",f.getEntryPoint().toString(),"name",f.getName(true),"size",f.getBody().getNumAddresses(),"ranges",ranges(f.getBody())));
        }
        save(root.resolve("index.json"),index);
        save(root.resolve("unassigned-executable.json"),row("ranges",ranges(executable.subtract(covered)),"bytes",executable.subtract(covered).getNumAddresses(),"meaning","Executable addresses outside recognized function bodies; may include padding or data, not asserted code."));
        DecompInterface dec=new DecompInterface();
        if(!dec.openProgram(currentProgram))throw new IllegalStateException(dec.getLastMessage());
        Path fn=root.resolve("functions");Files.createDirectories(fn); int count=0,skipped=0;
        try {
            for(Function f:currentProgram.getFunctionManager().getFunctions(true)){
                monitor.checkCancelled(); Path out=fn.resolve(f.getEntryPoint()+".json");
                if(Files.exists(out)){
                    Map old=gson.fromJson(Files.readString(out),Map.class);
                    if(identity.equals(old.get("identity")) && Boolean.TRUE.equals(old.get("decompiled"))){skipped++;continue;}
                }
                List<Object> asm=new ArrayList<>(), refs=new ArrayList<>(), incoming=new ArrayList<>(), raw=new ArrayList<>();
                MessageDigest md=MessageDigest.getInstance("SHA-256");
                for(AddressRange r:f.getBody().getAddressRanges()){
                    byte[] b=new byte[(int)r.getLength()];currentProgram.getMemory().getBytes(r.getMinAddress(),b);md.update(b);
                    raw.add(row("start",r.getMinAddress().toString(),"hex",HexFormat.of().formatHex(b)));
                }
                for(Instruction ins:currentProgram.getListing().getInstructions(f.getBody(),true)){
                    asm.add(row("address",ins.getAddress().toString(),"bytes",HexFormat.of().formatHex(ins.getBytes()),"text",ins.toString(),"flow",ins.getFlowType().toString(),"indirect",ins.getFlowType().isComputed()));
                    for(Reference r:ins.getReferencesFrom())refs.add(row("from",r.getFromAddress().toString(),"to",r.getToAddress().toString(),"kind",r.getReferenceType().toString(),"source",r.getSource().toString()));
                }
                for(Reference r:currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint()))incoming.add(row("from",r.getFromAddress().toString(),"kind",r.getReferenceType().toString()));
                DecompileResults result=dec.decompileFunction(f,30,monitor);
                save(out,row("identity",identity,"address",f.getEntryPoint().toString(),"name",f.getName(true),"signature",f.getSignature().toString(),"size",f.getBody().getNumAddresses(),"ranges",ranges(f.getBody()),"sha256",HexFormat.of().formatHex(md.digest()),"raw",raw,"assembly",asm,"references",refs,"entry_references",incoming,"comment",f.getComment(),"decompiled",result.decompileCompleted(),"error",result.getErrorMessage(),"pseudocode",result.decompileCompleted()?result.getDecompiledFunction().getC():null,"semantic_status","unexamined"));
                count++; if(count%100==0)println("EXPORTED "+count+" SKIPPED "+skipped);
                if(limit>0&&count>=limit)break;
            }
        } finally {dec.dispose();}
        save(root.resolve("run.json"),row("exported",count,"skipped",skipped,"limit",limit,"identity",identity));
        println("KNOWLEDGE_EXPORT_DONE exported="+count+" skipped="+skipped);
    }
}
