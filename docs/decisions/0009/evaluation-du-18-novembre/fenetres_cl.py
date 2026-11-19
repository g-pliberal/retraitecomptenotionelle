"""La carrière longue : la porte lue au texte de la date déclarée, puis reportée à son âge,
contre la première date d'effet dont le texte ouvre le droit. Âge seul (durée supposée acquise).
Lit data/reference/legislation/carriere_longue.csv, textes de 2012, 2023 et 2026."""
import csv, datetime as dt, sys
import fenetres as f

def jour_de(decimal):
    an = int(decimal); mois = round((decimal - an) * 12) + 1
    return dt.date(an, mois, 1)

portes = []
with open(sys.argv[1], encoding="utf-8") as fichier:
    lignes = [l for l in fichier if not l.startswith("#")]
for l in csv.DictReader(lignes):
    portes.append((float(l["date_effet"]), jour_de(float(l["generation"])), jour_de(float(l["generation_fin"])),
                   int(l["age_debut_maximum"]), round(float(l["age_depart"]) * 12)))
textes = sorted({p[0] for p in portes})
EFFET = {t: jour_de(t) for t in textes}

def texte_a(e):
    t = None
    for x in textes:
        if e >= EFFET[x]: t = x
    return t

def age(texte, n, cat):
    ages = [a for (t, g0, g1, c, a) in portes if t == texte and g0 <= n < g1 and c >= cat]
    return min(ages) if ages else None

def ouvert(n, cat, e):
    a = age(texte_a(e), n, cat)
    return a is not None and f.atteint(n, a) <= e

def suivant(d):
    return dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)

bilan = {}
exemples = {}
for bascule in (dt.date(2023, 9, 1), dt.date(2026, 9, 1)):
    declare = dt.date(bascule.year, bascule.month - 1, 1)
    for cat in (16, 18, 20, 21):
        jour = dt.date(1957, 1, 1)
        while jour <= dt.date(1972, 12, 31):
            n = jour; jour += dt.timedelta(days=1)
            if ouvert(n, cat, declare):
                continue
            a = age(texte_a(declare), n, cat)
            if a is None:
                continue
            moteur = f.premier_du_mois_a_partir(f.atteint(n, a))      # l'âge du texte de la date déclarée
            vrai = None; e = suivant(declare)
            for _ in range(12 * 9):
                if ouvert(n, cat, e): vrai = e; break
                e = suivant(e)
            cle = (bascule.isoformat(), cat)
            b = bilan.setdefault(cle, {"essayees": 0, "egales": 0, "trop_tot": 0, "trop_tard": 0})
            b["essayees"] += 1
            if vrai == moteur: b["egales"] += 1
            elif vrai is None or moteur < vrai:
                b["trop_tot"] += 1; exemples.setdefault((cle, "trop_tot"), (n, moteur, vrai))
            else:
                b["trop_tard"] += 1; exemples.setdefault((cle, "trop_tard"), (n, moteur, vrai))
for cle, b in sorted(bilan.items()):
    print(cle, b)
for cle, ex in sorted(exemples.items()):
    print("  exemple", cle, "né le", ex[0], "âge du texte déclaré →", ex[1], "; première date qui ouvre →", ex[2])

# droits ouverts puis refermés au fil des dates d'effet, tous textes depuis 2012
refermes = 0; ex = None
for cat in (16, 18, 20, 21):
    jour = dt.date(1952, 1, 1)
    while jour <= dt.date(1972, 12, 31):
        n = jour; jour += dt.timedelta(days=1)
        avant = False; e = dt.date(2012, 11, 1)
        while e <= dt.date(2036, 1, 1):
            ok = ouvert(n, cat, e)
            if avant and not ok:
                refermes += 1; ex = ex or (cat, n, e)
            avant = ok; e = suivant(e)
print("droits ouverts puis refermés :", refermes, ex)
