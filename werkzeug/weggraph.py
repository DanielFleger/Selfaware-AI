"""Kostensuche nur ueber native, gerichtete Weglinks; Hoehenregeln stammen aus dem Spiel.

Die native Routine 0x4999c0 prueft HeightLayer und Nachbarhoehen beim Setzen
jedes Richtungsbits. Gebietsgleichheit allein erlaubt keinen Klippensprung.
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

RICHTUNGEN=((1,0,-1),(2,1,-1),(4,1,0),(8,1,1),(16,0,1),(32,-1,1),(64,-1,0),(128,-1,-1))

class LinkSuche:
    def __init__(self, kosten, links, start):
        self.form=kosten.shape
        nx,ny=self.form
        xs,ys=np.indices(self.form)
        src=[];dst=[];werte=[]
        for bit,dx,dy in RICHTUNGEN:
            mask=((links & bit)!=0)&(kosten>=0)&(xs+dx>=0)&(xs+dx<nx)&(ys+dy>=0)&(ys+dy<ny)
            x,y=np.nonzero(mask);xx,yy=x+dx,y+dy
            ok=kosten[xx,yy]>=0;x,y,xx,yy=x[ok],y[ok],xx[ok],yy[ok]
            src.append(x*ny+y);dst.append(xx*ny+yy)
            werte.append((kosten[x,y]+kosten[xx,yy])*.5*(2**.5 if dx and dy else 1))
        graph=csr_matrix((np.concatenate(werte),(np.concatenate(src),np.concatenate(dst))),shape=(nx*ny,nx*ny))
        self.start=start[0]*ny+start[1]
        kum,self.vor=dijkstra(graph,directed=True,indices=self.start,return_predecessors=True)
        self.kum=kum.reshape(self.form)
    def traceback(self,ziel):
        i=ziel[0]*self.form[1]+ziel[1]
        if not np.isfinite(self.kum[ziel]):raise ValueError('Kein nativer Weg')
        pfad=[]
        while True:
            pfad.append(divmod(i,self.form[1]))
            if i==self.start:return pfad[::-1]
            i=int(self.vor[i])
            if i<0:raise ValueError('Unvollstaendige Wegkette')

def linie_erlaubt(pfad,links):
    bits={(dx,dy):bit for bit,dx,dy in RICHTUNGEN}
    for a,b in zip(pfad,pfad[1:]):
        delta=(b[0]-a[0],b[1]-a[1])
        if delta==(0,0):continue
        bit=bits.get(delta)
        if bit is None or not (int(links[a]) & bit):return False
    return True
