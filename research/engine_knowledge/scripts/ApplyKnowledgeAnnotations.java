// Applies reviewed names/comments only in a work copy. Explicit old values prevent lost annotations.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.address.AddressRange;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
public class ApplyKnowledgeAnnotations extends GhidraScript {
    public void run()throws Exception {
        JsonObject root=JsonParser.parseString(Files.readString(Paths.get(getScriptArgs()[0]))).getAsJsonObject();
        if(!currentProgram.getExecutableSHA256().equals(root.get("reference_sha256").getAsString()))throw new IllegalArgumentException("Wrong program");
        JsonArray entries=root.getAsJsonArray("annotations");
        // Validate the entire batch before mutation.
        for(JsonElement e:entries){
            JsonObject a=e.getAsJsonObject();Function f=getFunctionAt(toAddr(a.get("address").getAsString()));
            if(f==null||!f.getName().equals(a.get("expected_name").getAsString()))throw new IllegalArgumentException("Function/name conflict");
            String expected=a.get("expected_comment").isJsonNull()?null:a.get("expected_comment").getAsString();
            if(!Objects.equals(f.getComment(),expected))throw new IllegalArgumentException("Comment conflict");
            MessageDigest md=MessageDigest.getInstance("SHA-256");
            for(AddressRange r:f.getBody().getAddressRanges()){
                byte[] b=new byte[(int)r.getLength()];currentProgram.getMemory().getBytes(r.getMinAddress(),b);md.update(b);
            }
            if(!HexFormat.of().formatHex(md.digest()).equals(a.get("function_sha256").getAsString()))throw new IllegalArgumentException("Changed function");
        }
        int tx=currentProgram.startTransaction("Reviewed knowledge annotations");boolean ok=false;
        try{
            for(JsonElement e:entries){JsonObject a=e.getAsJsonObject();Function f=getFunctionAt(toAddr(a.get("address").getAsString()));
                if(a.has("name"))f.setName(a.get("name").getAsString(),SourceType.USER_DEFINED);
                if(a.has("comment"))f.setComment(a.get("comment").getAsString());
            }
            ok=true;
        }finally{currentProgram.endTransaction(tx,ok);}
        println("ANNOTATIONS_APPLIED "+entries.size());
    }
}
