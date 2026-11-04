import json,sys,os,re
base=r"C:/Users/danie/Documents/ChatGPT/Village Studio/work/engine-knowledge/exports/reference/functions"
pat=re.compile(sys.argv[1])
maxn=int(sys.argv[2]) if len(sys.argv)>2 else 60
n=0
for fn in sorted(os.listdir(base)):
    if not fn.endswith('.json'): continue
    try:
        d=json.load(open(os.path.join(base,fn),encoding='utf-8'))
    except Exception as e:
        continue
    pc=d.get('pseudocode') or ''
    for ln in pc.split('\n'):
        if pat.search(ln):
            print(fn[:8], d.get('name'), '|', ln.strip()[:200])
            n+=1
            if n>=maxn: sys.exit()
