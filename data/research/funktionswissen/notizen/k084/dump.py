import json,sys,os
base=r"C:/Users/danie/Documents/ChatGPT/Village Studio/work/engine-knowledge/exports/reference/functions"
for a in ['0054e6c0','0054f860','00550a50','00550d70','00551980']:
    d=json.load(open(os.path.join(base,a+'.json'),encoding='utf-8'))
    open(a+'.pc.txt','w',encoding='utf-8').write(d['pseudocode'])
    with open(a+'.asm.txt','w',encoding='utf-8') as f:
        for ins in d['assembly']:
            f.write("%s  %-24s %s\n"%(ins['address'],ins['bytes'],ins['text']))
    print(a,len(d['pseudocode']),len(d['assembly']))
