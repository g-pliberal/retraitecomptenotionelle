import glob, collections, yaml
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
R = "data/reference"
inter = {}
for p in sorted(glob.glob(f"{R}/regles/*.yaml")):
    d = yaml.load(open(p), Loader=Loader)
    c = d.get("code") or {}
    if isinstance(c, dict):
        for k in (c.get("interrupteurs") or {}):
            inter.setdefault(k, []).append(d["id"])
regs = {}
for p in sorted(glob.glob(f"{R}/regimes/*.yaml")):
    name = p.split("/")[-1][:-5]
    if name.startswith("_") or name in ("inventaire", "pivots"): continue
    d = yaml.load(open(p), Loader=Loader)
    if isinstance(d, dict) and "periodes" in d: regs[name] = d
sortes = collections.Counter(); par = collections.defaultdict(collections.Counter)
annees = collections.Counter()
for name, d in regs.items():
    pers = d["periodes"] or []
    for k in inter:
        vals = [per.get(k) if per.get(k) not in (None, False, [], {}, "") else None for per in pers]
        if not any(v is not None for v in vals): continue
        for i in range(1, len(vals)):
            a, b = vals[i - 1], vals[i]
            if repr(a) == repr(b): continue
            sorte = "commence" if a is None else ("cesse" if b is None else "change de valeur")
            sortes[sorte] += 1; par[k][sorte] += 1
            au_jour = bool(pers[i].get("date_effet"))
            annees["au jour" if au_jour else "à l'année"] += 1
print(dict(sortes), "total", sum(sortes.values()))
print(dict(annees))
for k in ("age_ouverture_par_generation", "age_taux_plein_par_generation", "duree_requise_par_generation"):
    print(k, dict(par[k]))
