import sys, json, UnityPy

path = sys.argv[1]
env = UnityPy.load(path)

objs = {}
for o in env.objects:
    objs[o.path_id] = o

def rd(o):
    try:
        return o.read()
    except Exception as e:
        return None

# 1) all meshes with AABB
print("== MESH AABBs ==")
for o in env.objects:
    if o.type.name != "Mesh":
        continue
    d = rd(o)
    if not d:
        continue
    try:
        c = d.m_LocalAABB.m_Center; e = d.m_LocalAABB.m_Extent
        print(f"{o.path_id:6d} {str(d.m_Name):32s} center=({c.x:+.4f},{c.y:+.4f},{c.z:+.4f}) ext=({e.x:.5f},{e.y:.5f},{e.z:.5f}) size=({2*e.x:.5f},{2*e.y:.5f},{2*e.z:.5f})")
    except Exception as ex:
        print(o.path_id, d.m_Name, "ERR", ex)

# 2) gameobjects by name
def go_name(o):
    d = rd(o)
    return getattr(d, "m_Name", None) if d else None

name_index = {}
for o in env.objects:
    if o.type.name == "GameObject":
        n = go_name(o)
        name_index.setdefault(n, []).append(o)

print("\n== candidate GameObjects ==")
for n in sorted(name_index.keys(), key=lambda x: str(x)):
    if any(k in str(n).lower() for k in ("gorilla", "monke", "player", "rig", "skin")):
        print(f"  {n!r} -> {[o.path_id for o in name_index[n]]}")

# 3) transform chain for the skinned renderer GO
def find_transform_of_go(go_obj):
    d = rd(go_obj)
    for comp in (d.m_Component or []):
        c = comp.component if hasattr(comp, "component") else comp
        try:
            cd = c.read()
        except Exception:
            continue
        if cd and cd.object_reader.type.name == "Transform":
            return cd
    return None

def chain(t):
    out = []
    seen = 0
    while t is not None and seen < 12:
        go = rd(t.m_GameObject)
        out.append({
            "go": getattr(go, "m_Name", None),
            "pos": [t.m_LocalPosition.x, t.m_LocalPosition.y, t.m_LocalPosition.z],
            "scale": [t.m_LocalScale.x, t.m_LocalScale.y, t.m_LocalScale.z],
        })
        seen += 1
        father = getattr(t, "m_Father", None)
        if not father:
            break
        try:
            t = father.read()
        except Exception:
            break
    return out

print("\n== chain of 'Gorilla Skin And Particles' ==")
for o in name_index.get("Gorilla Skin And Particles", []):
    t = find_transform_of_go(o)
    print(o.path_id, json.dumps(chain(t), indent=1))

# 4) colliders
print("\n== Colliders near gorilla/player ==")
for o in env.objects:
    if o.type.name not in ("CapsuleCollider", "SphereCollider", "BoxCollider"):
        continue
    d = rd(o)
    if not d:
        continue
    goo = getattr(d, "m_GameObject", None)
    goname = None
    if goo is not None:
        try:
            g = goo.read()
            goname = getattr(g, "m_Name", None)
        except Exception:
            pass
    if goname and any(k in str(goname).lower() for k in ("gorilla", "monke", "player", "body", "head", "rig")):
        info = {"go": goname, "type": o.type.name}
        for attr in ("m_Height", "m_Radius", "m_Center", "m_Size"):
            if hasattr(d, attr):
                v = getattr(d, attr)
                info[attr] = [v.x, v.y, v.z] if hasattr(v, "x") else v
        print(o.path_id, info)
