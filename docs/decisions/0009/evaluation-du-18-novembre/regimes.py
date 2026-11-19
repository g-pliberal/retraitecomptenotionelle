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
print("interrupteurs:", len(inter))
regs = {}
for p in sorted(glob.glob(f"{R}/regimes/*.yaml")):
    name = p.split("/")[-1][:-5]
    if name.startswith("_") or name in ("inventaire", "pivots"):
        continue
    d = yaml.load(open(p), Loader=Loader)
    if isinstance(d, dict) and "periodes" in d:
        regs[name] = d
print("régimes avec périodes:", len(regs), "périodes:", sum(len(d["periodes"] or []) for d in regs.values()))
tot = 0
par = collections.Counter()
for name, d in regs.items():
    for per in d["periodes"] or []:
        for k, v in per.items():
            if k in inter and v not in (None, False, [], {}, ""):
                tot += 1
                par[k] += 1
print("renvois par interrupteur (périodes × interrupteurs renseignés):", tot)
for k, n in par.most_common(12):
    print("  ", k, n, inter[k])
# âges
for champ, repli in (("age_ouverture_par_generation", "age_ouverture"), ("age_taux_plein_par_generation", "age_taux_plein")):
    n = 0; regimes = set(); replis = collections.Counter()
    debut_renvoi = {}
    for name, d in regs.items():
        pers = d["periodes"] or []
        for i, per in enumerate(pers):
            if per.get(champ):
                n += 1; regimes.add(name); replis[per.get(repli)] += 1
                debut_renvoi.setdefault(name, (per.get("debut"), i))
    print(champ, ": périodes", n, "régimes", len(regimes), "replis", dict(replis))
    des_le_debut = [r for r, (deb, i) in debut_renvoi.items() if i == 0]
    print("   renvoient dès leur première période:", len(des_le_debut), "; après une période sans renvoi:", len(debut_renvoi) - len(des_le_debut))

print("\n--- bascules")
paires = 0; bascules = 0; bascules_apres_debut = 0
par_inter = collections.Counter()
for name, d in regs.items():
    pers = d["periodes"] or []
    for k in inter:
        vals = [per.get(k) if per.get(k) not in (None, False, [], {}, "") else None for per in pers]
        if not any(v is not None for v in vals):
            continue
        paires += 1
        prev = "∅"
        for i, v in enumerate(vals):
            cle = repr(v)
            if cle != prev:
                if v is not None or prev != "∅":
                    bascules += 1
                    par_inter[k] += 1
                    if i > 0:
                        bascules_apres_debut += 1
                prev = cle
print("paires régime × interrupteur:", paires)
print("changements de valeur d'un interrupteur d'une période à la suivante (début compris):", bascules, "; hors première période:", bascules_apres_debut)
print(par_inter.most_common(10))
# périodes : bornes distinctes
bornes = sum(max(0, len(d["periodes"] or []) - 1) for d in regs.values())
print("frontières entre périodes consécutives:", bornes)
# date_effet au jour
avec_date_effet = sum(1 for d in regs.values() for per in d["periodes"] or [] if per.get("date_effet"))
print("périodes avec date_effet au jour:", avec_date_effet)
champs = collections.Counter(k for d in regs.values() for per in d["periodes"] or [] for k in per)
print("champs distincts des périodes:", len(champs))
