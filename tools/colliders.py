import sys, UnityPy, json

path = sys.argv[1]
env = UnityPy.load(path)
cache = {}

def rd(o):
    if o is None:
        return None
    pid = o.path_id
    if pid in cache:
        return cache[pid]
    try:
        cache[pid] = o.read()
    except Exception:
        cache[pid] = None
    return cache[pid]

def comps(go):
    return [rd(c.component if hasattr(c, "component") else c) for c in (getattr(go, "m_Component", None) or [])]

def t_of(go):
    for cd in comps(go):
        if cd is not None and cd.object_reader.type.name in ("Transform", "RectTransform"):
            return cd
    return None

def parent_chain(go, limit=8):
    t = t_of(go)
    out = []
    while t is not None and len(out) < limit:
        g = rd(t.m_GameObject)
        out.append(getattr(g, "m_Name", None))
        f = getattr(t, "m_Father", None)
        t = rd(f) if f else None
    return out

print("== colliders of interest ==")
for o in env.objects:
    if o.type.name not in ("CapsuleCollider", "SphereCollider", "BoxCollider"):
        continue
    d = rd(o)
    if d is None:
        continue
    go = rd(getattr(d, "m_GameObject", None))
    name = getattr(go, "m_Name", "?")
    chain = parent_chain(go) if go else []
    if not any(k in " ".join([str(n) for n in chain]).lower() for k in ("player", "gorilla", "rig", "head", "body", "monke")):
        continue
    info = {"go": name, "chain": chain, "type": o.type.name, "pid": o.path_id}
    for a in ("m_Height", "m_Radius", "m_Size", "m_Center", "m_IsTrigger", "m_Direction"):
        if hasattr(d, a):
            v = getattr(d, a)
            info[a] = [round(v.x, 4), round(v.y, 4), round(v.z, 4)] if hasattr(v, "x") else v
    print(json.dumps(info))
