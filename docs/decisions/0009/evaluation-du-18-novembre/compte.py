import sys, glob, os, collections, datetime
import yaml
try:
    Loader = yaml.CSafeLoader
except AttributeError:
    Loader = yaml.SafeLoader
R = "data/reference"
fiches = {}
for p in sorted(glob.glob(f"{R}/regles/*.yaml")) + sorted(glob.glob(f"{R}/regles/proposition/*.yaml")):
    with open(p) as f:
        d = yaml.load(f, Loader=Loader)
    fiches[p] = d
top = [p for p in fiches if "/proposition/" not in p]
print("fiches haut niveau:", len(top), "proposition:", len(fiches) - len(top), "total:", len(fiches))
sans = [p for p in fiches if not fiches[p].get("versions")]
print("sans versions (total):", len(sans), "dont haut niveau:", len([p for p in sans if p in top]))
etats = collections.Counter(fiches[p].get("etat") for p in fiches)
print("etats:", dict(etats))
# bornes par date
dates = collections.Counter()
fiches_par_date = collections.defaultdict(set)
nver = 0
for p, d in fiches.items():
    for v in d.get("versions") or []:
        nver += 1
        for nom in (v.get("bornes") or {}):
            dates[nom] += 1
            fiches_par_date[nom].add(d["id"])
print("versions:", nver)
for nom, n in dates.most_common(40):
    print(f"  {nom}: {n} versions, {len(fiches_par_date[nom])} fiches")
# dates_qui_decident multiples
multi = [d["id"] for d in fiches.values() if len(d.get("dates_qui_decident") or []) > 1]
print("fiches à plusieurs dates qui décident:", len(multi))
# code field form
import re
avec_code = [d for d in fiches.values() if d.get("code")]
print("fiches avec code:", len(avec_code))
js = [d for d in avec_code if isinstance(d["code"], dict) and d["code"].get("javascript")]
print("  avec code.javascript:", len(js))
inter = collections.Counter()
for d in fiches.values():
    c = d.get("code") or {}
    if isinstance(c, dict):
        for k in (c.get("interrupteurs") or {}):
            inter[k] += 1
print("interrupteurs déclarés par les fiches:", len(inter), "noms ; fiches qui en déclarent:", len([d for d in fiches.values() if isinstance(d.get('code'), dict) and d['code'].get('interrupteurs')]))
# exemples
avec_ex = 0
for d in fiches.values():
    ex = bool(d.get("exemples"))
    for v in d.get("versions") or []:
        e = v.get("exemples")
        if isinstance(e, list) and e:
            ex = True
    avec_ex += ex
print("fiches avec au moins un exemple:", avec_ex)
