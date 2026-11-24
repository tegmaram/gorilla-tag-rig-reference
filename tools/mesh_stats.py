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
want={"gorilla","gorilla_Headless","MonkeSkeleton"}
for o in env.objects:
    if o.type.name!="Mesh": continue
    d=rd(o); n=getattr(d,"m_Name",None)
    if n not in want: continue
    b=d.m_LocalAABB
    vd=getattr(d,"m_VertexData",None)
    vc=getattr(vd,"m_VertexCount",None) if vd else None
    subs=len(getattr(d,"m_SubMeshes",[]) or [])
    tris=0
    for s in (getattr(d,"m_SubMeshes",[]) or []):
        try: tris += s.indexCount//3
        except Exception: pass
    print(f"{n}: verts={vc} submeshes={subs} tris={tris} center=({b.m_Center.x:+.4f},{b.m_Center.y:+.4f},{b.m_Center.z:+.4f}) size=({2*b.m_Extent.x:.4f},{2*b.m_Extent.y:.4f},{2*b.m_Extent.z:.4f})")
