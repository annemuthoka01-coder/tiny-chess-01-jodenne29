import json,os,sys,urllib.request
E=os.environ.get("MAKEFUN_ENV_URL")
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0}
def parse_fen(f):
 p=f.split();b=['.']*64
 for r,w in enumerate(p[0].split('/')):
  c=0
  for ch in w:
   if ch.isdigit():c+=int(ch)
   else:b[r*8+c]=ch;c+=1
 ep=p[3]
 ep_idx=ord(ep[0])-ord('a')+(8-int(ep[1]))*8 if ep!='-' else -1
 return [b,p[1],p[2],ep_idx]
fs=lambda s:s%8
rs=lambda s:s//8
uc=lambda m:"abcdefgh"[m[1]]+str(8-m[0])+"abcdefgh"[m[3]]+str(8-m[2])+m[4]

def ia(b,s,bw):
 for d in [-17,-15,-10,-6,6,10,15,17]:
  ts=s+d
  if 0<=ts<64 and abs(fs(s)-fs(ts))<=2 and b[ts]==('N' if bw else 'n'):return 1
 for d in [-9,-8,-7,-1,1,7,8,9]:
  ts=s+d
  if 0<=ts<64 and abs(fs(s)-fs(ts))<=1 and b[ts]==('K' if bw else 'k'):return 1
 for ts in ([s+9,s+7] if bw else [s-7,s-9]):
  if 0<=ts<64 and abs(fs(s)-fs(ts))==1 and b[ts]==('P' if bw else 'p'):return 1
 for d,pc in [(-8,'RQ'),(8,'RQ'),(-1,'RQ'),(1,'RQ'),(-9,'BQ'),(9,'BQ'),(-7,'BQ'),(7,'BQ')]:
  ts=s+d
  while 0<=ts<64:
   if abs(d) in [7,9] and abs(fs(ts)-fs(ts-d))!=1:break
   if abs(d)==1 and rs(ts)!=rs(ts-d):break
   p=b[ts]
   if p!='.':
    if p in (pc if bw else pc.lower()):return 1
    break
   ts+=d
 return 0

def gm(P):
 b,t,c,e=P;w=(t=='w');m=[]
 for sq in range(64):
  p=b[sq]
  if p=='.' or p.isupper()!=w:continue
  fr,fc=rs(sq),fs(sq);pt=p.lower()
  if pt=='p':
   dr=-1 if w else 1;sr=6 if w else 1;ts=sq+dr*8
   if 0<=ts<64 and b[ts]=='.':
    if rs(ts)==(0 if w else 7):
     for q in 'qrbn':m.append((fr,fc,rs(ts),fs(ts),q))
    else:m.append((fr,fc,rs(ts),fs(ts),''))
    if fr==sr and b[sq+dr*16]=='.':m.append((fr,fc,rs(sq+dr*16),fs(sq+dr*16),''))
   for dc in (-1,1):
    nc=fc+dc
    if 0<=nc<8:
     ts=sq+dr*8+dc
     if 0<=ts<64:
      tp=b[ts]
      if (tp!='.' and tp.isupper()!=w)or ts==e:
       if rs(ts)==(0 if w else 7):
        for q in 'qrbn':m.append((fr,fc,rs(ts),fs(ts),q))
       else:m.append((fr,fc,rs(ts),fs(ts),''))
  elif pt in 'nk':
   for d in ([-17,-15,-10,-6,6,10,15,17] if pt=='n' else [-9,-8,-7,-1,1,7,8,9]):
    ts=sq+d
    if 0<=ts<64 and abs(fs(sq)-fs(ts))<=(2 if pt=='n' else 1):
     tp=b[ts]
     if tp=='.' or tp.isupper()!=w:m.append((fr,fc,rs(ts),fs(ts),''))
  else:
   for d in ([-9,-7,7,9] if pt=='b' else ([-8,-1,1,8] if pt=='r' else [-9,-8,-7,-1,1,7,8,9])):
    ts=sq
    while True:
     nxt=ts+d
     if not(0<=nxt<64):break
     if abs(d) in [7,9] and abs(fs(nxt)-fs(ts))!=1:break
     if abs(d)==1 and rs(nxt)!=rs(ts):break
     tp=b[nxt]
     if tp=='.' or tp.isupper()!=w:m.append((fr,fc,rs(nxt),fs(nxt),''))
     if tp!='.':break
     ts=nxt
 if w:
  if 'K' in c and b[61]=='.' and b[62]=='.' and not ia(b,60,0) and not ia(b,61,0) and not ia(b,62,0):m.append((7,4,7,6,''))
  if 'Q' in c and b[59]=='.' and b[58]=='.' and b[57]=='.' and not ia(b,60,0) and not ia(b,59,0) and not ia(b,58,0):m.append((7,4,7,2,''))
 else:
  if 'k' in c and b[5]=='.' and b[6]=='.' and not ia(b,4,1) and not ia(b,5,1) and not ia(b,6,1):m.append((0,4,0,6,''))
  if 'q' in c and b[3]=='.' and b[2]=='.' and b[1]=='.' and not ia(b,4,1) and not ia(b,3,1) and not ia(b,2,1):m.append((0,4,0,2,''))
 lg=[]
 for mv in m:
  u=mk(P,mv);kch='K' if w else 'k'
  if kch in P[0]:
   ksq=P[0].index(kch)
   if not ia(P[0],ksq,not w):lg.append(mv)
  else:
   lg.append(mv)
  um(P,mv,u)
 return lg

def mk(P,m):
 b,t,c,e=P;fr1,fc1,fr2,fc2,q=m;fs,ts=fr1*8+fc1,fr2*8+fc2;p=b[fs];cap=b[ts];nep=-1;cr=None
 if p.lower()=='p' and ts==e:
  cs=ts+(8 if t=='w' else -8);cap=b[cs];b[cs]='.'
 if p.lower()=='p' and abs(fr2-fr1)==2:nep=(fs+ts)//2
 if p.lower()=='k' and abs(fc2-fc1)==2:
  if fc2==6:cr=(fs+3,fs+1,b[fs+3]);b[fs+1]=b[fs+3];b[fs+3]='.'
  elif fc2==2:cr=(fs-4,fs-1,b[fs-4]);b[fs-1]=b[fs-4];b[fs-4]='.'
 b[ts]=(q.upper() if t=='w' else q.lower()) if q else p;b[fs]='.'
 nc=c
 for ch,tk in [('K','KQ'),('k','kq')]:
  if p==ch:nc=nc.replace(ch,'').replace(tk[1],'')
 if fs==0 or ts==0:nc=nc.replace('q','')
 if fs==7 or ts==7:nc=nc.replace('k','')
 if fs==56 or ts==56:nc=nc.replace('Q','')
 if fs==63 or ts==63:nc=nc.replace('K','')
 if nc=='':nc='-'
 P[1]='b' if t=='w' else 'w';P[2]=nc;P[3]=nep
 return (cap,c,e,cr,fs,ts)

def um(P,m,u):
 cap,oc,oep,cr,fs,ts=u;b,t,_,_=P;p=b[ts]
 P[1]='w' if t=='b' else 'b';P[2]=oc;P[3]=oep
 if cr:rf,rt,rp=cr;b[rf]=rp;b[rt]='.'
 w=(P[1]=='w')
 if p.lower()=='p' and ts==oep and abs(ts-fs) in [7,9]:
  cs=ts+(8 if w else -8);b[cs]=cap;b[ts]='.';b[fs]=p
  return
 b[fs]=('P' if w else 'p') if m[4]!='' else p;b[ts]=cap

def perft(P,d):
 if d==0:return 1
 ms=gm(P)
 if d==1:return len(ms)
 n=0
 for m in ms:
  u=mk(P,m);n+=perft(P,d-1);um(P,m,u)
 return n

def ev(b,w):
 s=0;wb=0;bb=0
 for sq,p in enumerate(b):
  if p=='.':continue
  iw=p.isupper();pt=p.lower()
  s+=(V[pt]+((7-rs(sq) if iw else rs(sq))*5 if pt=='p' else 0))*(1 if iw else -1)
  if p=='B':wb+=1
  elif p=='b':bb+=1
 if wb>=2:s+=30
 if bb>=2:s-=30
 return s if w else -s

nd=0;tt={}
def qs(P,alpha,beta,w):
 global nd;nd+=1
 if nd>24000:return 0
 sp=ev(P[0],w)
 if sp>=beta:return beta
 if alpha<sp:alpha=sp
 for m in [m for m in gm(P) if P[0][m[2]*8+m[3]]!='.' or m[4]!='']:
  u=mk(P,m);sc=-qs(P,-beta,-alpha,not w);um(P,m,u)
  if nd>24000:return 0
  if sc>=beta:return beta
  if sc>alpha:alpha=sc
 return alpha

def ng(P,d,alpha,beta,w):
 global nd;nd+=1
 if nd>24000 or d==0:return qs(P,alpha,beta,w)
 key=(tuple(P[0]),P[1],P[2],P[3])
 if key in tt:
  dv,v,fl,_=tt[key]
  if dv>=d:
   if fl==0:return v
   if fl==1 and v>=beta:return v
   if fl==-1 and v<=alpha:return alpha
 ms=gm(P)
 if not ms:
  kch='K' if w else 'k'
  if kch in P[0] and ia(P[0],P[0].index(kch),not w):return -100000+d
  return 0
 ms.sort(key=lambda m: V.get(P[0][m[2]*8+m[3]].lower(),0)*10 - V.get(P[0][m[0]*8+m[1]].lower(),1),reverse=True)
 bv=-999999;bm=ms[0];fl=-1
 for m in ms:
  u=mk(P,m);val=-ng(P,d-1,-beta,-alpha,not w);um(P,m,u)
  if nd>24000:break
  if val>bv:bv=val;bm=m
  if val>alpha:alpha=val;fl=0
  if alpha>=beta:fl=1;break
 tt[key]=(d,bv,fl,bm)
 return bv

def best_move(fen,legal):
 global nd,tt;nd=0;tt.clear()
 P=parse_fen(fen);w=(P[1]=='w');bm=legal[0]
 for d in range(1,5):
  if nd>24000:break
  ms=gm(P)
  if not ms:break
  ms.sort(key=lambda m: V.get(P[0][m[2]*8+m[3]].lower(),0)*10,reverse=True)
  alpha,beta=-999999,999999;lb=ms[0];lbv=-999999
  for m in ms:
   u=mk(P,m);val=-ng(P,d-1,-beta,-alpha,not w);um(P,m,u)
   if nd>24000:break
   if val>lbv:lbv=val;lb=m
   if val>alpha:alpha=val
  if nd<=24000:bm=uc(lb)
  else:break
 if bm in legal:return bm
 for lm in legal:
  if lm[:4]==bm[:4]:return lm
 return legal[0]

def post(path,body):
 req=urllib.request.Request(E+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
 with urllib.request.urlopen(req) as res:return json.load(res)

if __name__=='__main__':
 while True:
  g=post("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   m=best_move(g["fen"],g["legal_moves"])
   g=post("/move",{"game":g["game"],"move":m})
  print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
 print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)
