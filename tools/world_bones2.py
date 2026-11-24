import sys, UnityPy, math
path=sys.argv[1]; rootname=sys.argv[2]
env=UnityPy.load(path)
cache={}
def rd(o):
    if o is None: return None
    if o.path_id in cache: return cache[o.path_id]
    try: cache[o.path_id]=o.read()
    except Exception: cache[o.path_id]=None
    return cache[o.path_id]
def comps(g):
    return [rd(c.component if hasattr(c,"component") else c) for c in (getattr(g,"m_Component",None) or [])]
def t_of(g):
    for c in comps(g):
        if c is not None and c.object_reader.type.name in ("Transform","RectTransform"): return c
    return None
def qmul(a,b):
    ax,ay,az,aw=a; bx,by,bz,bw=b
    return (aw*bx+ax*bw+ay*bz-az*by,
            aw*by-ax*bz+ay*bw+az*bx,
            aw*bz+ax*by-ay*bx+az*bw,
            aw*bw-ax*bx-ay*by-az*bz)
def qrot(q,v):
    x,y,z,w=q; vx,vy,vz=v
    tx=2*(y*vz-z*vy); ty=2*(z*vx-x*vz); tz=2*(x*vy-y*vx)
    return (vx+w*tx+(y*tz-z*ty), vy+w*ty+(z*tx-x*tz), vz+w*tz+(x*ty-y*tx))
root=None
for o in env.objects:
    if o.type.name=="GameObject":
        g=rd(o)
        if g and getattr(g,"m_Name",None)==rootname: root=g; break
print("root:",root.m_Name)
def walk(go, depth=0, wp=(0.,0.,0.), wr=(0.,0.,0.,1.), ws=(1.,1.,1.)):
    t=t_of(go)
    if t is None: return
    lp,ls,lr=t.m_LocalPosition,t.m_LocalScale,t.m_LocalRotation
    off=qrot(wr,(ws[0]*lp.x, ws[1]*lp.y, ws[2]*lp.z))
    world=(wp[0]+off[0], wp[1]+off[1], wp[2]+off[2])
    wrot=qmul(wr,(lr.x,lr.y,lr.z,lr.w))
    wsc=(ws[0]*ls.x, ws[1]*ls.y, ws[2]*ls.z)
    print(f"{'  '*depth}{go.m_Name:18s} world=({world[0]:+.4f},{world[1]:+.4f},{world[2]:+.4f}) ws=({wsc[0]:.3f},{wsc[1]:.3f},{wsc[2]:.3f})")
    if depth>=4: return
    for ch in (t.m_Children or []):
        ct=rd(ch); g=rd(ct.m_GameObject)
        if g: walk(g, depth+1, world, wrot, wsc)
walk(root)
