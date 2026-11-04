import json,sys,os
base=r"C:\Users\danie\Documents\ChatGPT\Village Studio\work\engine-knowledge\exports\reference\functions"
mode='p'
args=sys.argv[1:]
if args and args[0] in ('-a','-p','-b'):
    mode=args[0][1]; args=args[1:]
for a in args:
    a=a.lower().replace('0x','').zfill(8)
    fn=os.path.join(base,a+'.json')
    if not os.path.exists(fn):
        print('=== %s: nicht vorhanden'%a); continue
    d=json.load(open(fn,encoding='utf-8'))
    print('=== %s %s | %s | size=%s'%(a,d.get('name'),d.get('signature'),d.get('size')))
    if mode in 'pb':
        print(d['pseudocode'])
    if mode in 'ab':
        refs={}
        for r in d['references']:
            refs.setdefault(r.get('from'),[]).append(r)
        for x in d['assembly']:
            t=f"{x['address']}  {x['text']}"
            rr=refs.get(x['address'])
            if rr:
                t+="    ; "+" | ".join(f"{r.get('kind','')}->{r.get('to','')}" for r in rr)
            print(t)
