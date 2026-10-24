"""Remove only unavailable unpackaged development modules from UCP configurations."""
from pathlib import Path
import argparse,copy,json,datetime,os
import yaml

def repaired(data,unavailable):
 result=copy.deepcopy(data);changes=[]
 for section in ('config-sparse','config-full'):
  block=result.get(section,{})
  for kind in ('modules','plugins'):
   for name in unavailable:
    if name in block.get(kind,{}):
     del block[kind][name];changes.append(section+'.'+kind+'.'+name)
  order=block.get('load-order')
  if isinstance(order,list):
   kept=[x for x in order if x.get('extension') not in unavailable]
   if kept!=order:block['load-order']=kept;changes.append(section+'.load-order')
 return result,changes

def repair(root,apply=False):
 root=Path(root).resolve();p=root/'ucp-config.yml'
 old=p.read_bytes();data=yaml.safe_load(old)
 unavailable={name for name in ('villagestudio',) if (root/'ucp/modules'/f'{name}-0.1.0').is_dir() and not(root/'ucp/modules'/f'{name}-0.1.0.zip').is_file()}
 new,changes=repaired(data,unavailable)
 report={'game':str(root),'changes':changes,'applied':False}
 if changes and apply:
  backup=p.with_name(p.name+'.before-startup-repair-'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
  with backup.open('xb') as f:f.write(old)
  text=yaml.safe_dump(new,sort_keys=False,allow_unicode=True)
  if yaml.safe_load(text)!=new:raise ValueError('Configuration roundtrip changed values')
  tmp=p.with_name(p.name+'.repair.tmp');tmp.write_text(text,encoding='utf-8');os.replace(tmp,p)
  report.update(applied=True,backup=str(backup))
 return report

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('game',nargs='+');a.add_argument('--apply',action='store_true');args=a.parse_args()
 print(json.dumps([repair(g,args.apply) for g in args.game],indent=2))
