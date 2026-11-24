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
for o in env.objects:
    if o.type.name!="Mesh": continue
    d=rd(o)
    if d is None or getattr(d,"m_Name",None)!="gorilla": continue
    v=getattr(d,"m_Vertices",None)
    print("mesh pid",o.path_id,"verts_attr",None if v is None else len(v)//3, "aabb", tuple(round(x,4) for x in (2*d.m_LocalAABB.m_Extent.x,2*d.m_LocalAABB.m_Extent.y,2*d.m_LocalAABB.m_Extent.z)))
