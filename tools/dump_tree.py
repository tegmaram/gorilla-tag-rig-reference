import sys, UnityPy, json

path = sys.argv[1]
root_name = sys.argv[2] if len(sys.argv) > 2 else "Gorilla Player Networked"
maxdepth = int(sys.argv[3]) if len(sys.argv) > 3 else 8

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
    out = []
    for comp in (getattr(go, "m_Component", None) or []):
        c = comp.component if hasattr(comp, "component") else comp
        cd = rd(c)
        if cd is None:
            continue
        out.append(cd)
    return out

def t_of(go):
    for cd in comps(go):
        if cd.object_reader.type.name in ("Transform", "RectTransform"):
            return cd
    return None

def desc(cd):
    tn = cd.object_reader.type.name
    if tn in ("Transform", "RectTransform"):
        p, s = cd.m_LocalPosition, cd.m_LocalScale
        return f"T pos=({p.x:.3f},{p.y:.3f},{p.z:.3f}) scale=({s.x:.4f},{s.y:.4f},{s.z:.4f})"
    if tn in ("CapsuleCollider", "SphereCollider", "BoxCollider"):
        bits = [tn]
        for a in ("m_Height", "m_Radius", "m_Size", "m_Center", "m_IsTrigger"):
            if hasattr(cd, a):
                v = getattr(cd, a)
                if hasattr(v, "x"):
                    bits.append(f"{a}=({v.x:.3f},{v.y:.3f},{v.z:.3f})")
                else:
                    bits.append(f"{a}={v}")
        return " ".join(bits)
    if tn in ("SkinnedMeshRenderer", "MeshRenderer", "MeshFilter"):
        m = getattr(cd, "m_Mesh", None)
        md = rd(m) if m else None
        s = f"{tn} mesh={getattr(md,'m_Name',None)!r}"
        if tn == "SkinnedMeshRenderer":
            rb = getattr(cd, "m_RootBone", None)
            s += f" rootBone={getattr(rd(rb),'m_Name',None) if rb else None}"
            try:
                b = cd.m_LocalAABB
                s += f" aabbExt=({b.m_Extent.x:.4f},{b.m_Extent.y:.4f},{b.m_Extent.z:.4f})"
            except Exception:
                pass
        return s
    if tn == "MonoBehaviour":
        sc = getattr(cd, "m_Script", None)
        s = getattr(rd(sc), "m_Name", None) if sc else None
        return f"MB {s}"
    return tn

root = None
for o in env.objects:
    if o.type.name == "GameObject":
        g = rd(o)
        if g and getattr(g, "m_Name", None) == root_name:
            root = g
            print("found root pid", o.path_id)
            break
if root is None:
    sys.exit("root not found")

def walk(go, depth=0):
    t = t_of(go)
    print("  " * depth + f"- {go.m_Name}")
    for cd in comps(go):
        if cd.object_reader.type.name in ("Transform", "RectTransform"):
            continue
        print("  " * depth + "    . " + desc(cd))
    if t is None or depth >= maxdepth:
        return
    for ch in (t.m_Children or []):
        ct = rd(ch)
        cgo = rd(ct.m_GameObject)
        if cgo is not None:
            walk(cgo, depth + 1)

walk(root)
