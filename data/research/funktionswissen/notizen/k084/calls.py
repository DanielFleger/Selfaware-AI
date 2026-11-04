import json,sys,os,re
base=r"C:/Users/danie/Documents/ChatGPT/Village Studio/work/engine-knowledge/exports/reference/functions"
a=sys.argv[1]
d=json.load(open(os.path.join(base,a+'.json'),encoding='utf-8'))
seen={}
for ins in d['assembly']:
    m=re.match(r'CALL (0x[0-9a-f]+)',ins['text'])
    if m:
        t=m.group(1)[2:].zfill(8)
        seen.setdefault(t,[]).append(ins['address'])
for t,addrs in sorted(seen.items()):
    fn=os.path.join(base,t+'.json')
    nm='?'
    sig=''
    if os.path.exists(fn):
        dd=json.load(open(fn,encoding='utf-8'))
        nm=dd['name'].split('::')[-1]; sig=dd['signature']
    print(t,nm,len(addrs),'x',addrs[:3],'|',sig[:150])
