import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import com.google.gson.Gson;
import java.nio.file.*;
import java.util.*;
public class CatalogSupplement extends GhidraScript {
    Map<String,Object> row(Object... kv){Map<String,Object> r=new LinkedHashMap<>();for(int i=0;i<kv.length;i+=2)r.put((String)kv[i],kv[i+1]);return r;}
    public void run()throws Exception{
        List<Object> external=new ArrayList<>(),classifications=new ArrayList<>(),comments=new ArrayList<>(),unowned=new ArrayList<>();
        for(Function f:currentProgram.getFunctionManager().getExternalFunctions())external.add(row("address",f.getEntryPoint().toString(),"name",f.getName(true),"signature",f.getSignature().toString(),"status","external declaration; implementation not in this executable"));
        for(Function f:currentProgram.getFunctionManager().getFunctions(true))classifications.add(row("address",f.getEntryPoint().toString(),"thunk",f.isThunk(),"external",f.isExternal(),"library_classification","unknown unless external/thunk declaration proves it"));
        for(CodeUnit c:currentProgram.getListing().getCodeUnits(true)){
            for(CommentType type:CommentType.values()){
                String text=c.getComment(type);
                if(text!=null)comments.add(row("address",c.getAddress().toString(),"type",type.toString(),"text",text));
            }
        }
        for(Instruction i:currentProgram.getListing().getInstructions(true))if(getFunctionContaining(i.getAddress())==null)unowned.add(row("address",i.getAddress().toString(),"assembly",i.toString(),"flow",i.getFlowType().toString()));
        Files.writeString(Paths.get(getScriptArgs()[0]),new Gson().toJson(row("external_functions",external,"function_classification",classifications,"comments",comments,"unowned_instructions",unowned)));
        println("CATALOG_DONE externals="+external.size()+" comments="+comments.size()+" unowned_instructions="+unowned.size());
    }
}
