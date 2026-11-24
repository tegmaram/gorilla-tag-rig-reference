import sys, UnityPy
path=sys.argv[1]
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
for o in env.objects:
    if o.type.name!="SkinnedMeshRenderer": continue
    d=rd(o)
    m=rd(getattr(d,"m_Mesh",None)) if getattr(d,"m_Mesh",None) else None
    if not m or getattr(m,"m_Name",None)!="gorilla": continue
    g=rd(d.m_GameObject); t=t_of(g); chain=[]
    while t is not None and len(chain)<4:
        chain.append(getattr(rd(t.m_GameObject),"m_Name",None)); f=getattr(t,"m_Father",None); t=rd(f) if f else None
    if "Gorilla Player Networked" not in chain: continue
    b=m.m_LocalAABB; vd=getattr(m,"m_VertexData",None)
    print("renderer pid",o.path_id,"mesh pid",d.m_Mesh.path_id,"name",m.m_Name,"verts",getattr(vd,"m_VertexCount",None))
    print("  size",(round(2*b.m_Extent.x,4),round(2*b.m_Extent.y,4),round(2*b.m_Extent.z,4)),"center",(round(b.m_Center.x,3),round(b.m_Center.y,3),round(b.m_Center.z,3)))
    print("  chain",chain)
    print("  bones",len(getattr(d,"m_Bones",[]) or []))
