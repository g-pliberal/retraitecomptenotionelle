#!/usr/bin/env python3
"""Ce que le sixième cliquet de la note 0009 trouverait aujourd'hui.

    python mesures.py [AAAA-MM-JJ]

Deux comptes, sur la carte des règles et la liste de contrôle des textes du
dépôt (``data/reference/textes/redactions.csv``, tirée de l'index LEGI) :

1. les couples (fiche, rédaction en vigueur ou à venir d'un article que la
   fiche cite) auxquels la fiche n'a pas répondu, ni par une de ses versions,
   ni par une déclaration « sans effet » ;
2. les couples (fiche, réforme déclarée) sans version qui commence à la date
   de la réforme.

Ne modifie rien. Se lance depuis la racine du dépôt, le paquet installé.
"""
import collections
import sys
from datetime import date

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.regimes import charger_reformes
from retraite_notionnelle.noyau import carte, textes

jour = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
fiches = carte.fiches()
sans_version = {n for n, f in fiches.items()
                if not any(isinstance(v, dict) for v in f.get("versions") or [])}
print(f"Au {jour} : {len(fiches)} fiches, dont {len(sans_version)} sans version.")
statuts = collections.Counter(textes.statuts().values())
print(f"Liste : {sum(statuts.values())} rédactions, {dict(statuts)}")

# 1. Les rédactions sans réponse de la fiche.
cite = textes.citations(fiches)
par_article = collections.defaultdict(list)
for r in textes.redactions():
    if r["article"].strip():
        par_article[(r["texte"], r["article"])].append(r)
couples = []
for groupe in par_article.values():
    lectrices = {nom for r in groupe for nom in cite.get(r["id"], {})}
    for r in groupe:
        a_cours = textes._vit(r) and (not r["fin"] or r["fin"] > jour)
        if not a_cours or any(textes._ensemble(r, a) for a in groupe if a is not r):
            continue
        for nom in lectrices:
            dit = cite.get(r["id"], {}).get(nom)
            if dit not in ("rattachee", "sans_effet"):
                ailleurs = any(s == "rattachee" for n, s in cite.get(r["id"], {}).items() if n != nom)
                couples.append((nom, r, dit, ailleurs))
muets = [c for c in couples if c[2] is None]
print(f"\n1. Couples sans réponse : {len(couples)}, pour {len({c[0] for c in couples})} fiches "
      f"et {len({c[1]['id'] for c in couples})} rédactions.")
print(f"   La fiche cite la rédaction sans l'avoir coupée en version : {len(couples) - len(muets)}"
      f" (dont dans une fiche sans version : {sum(1 for c in couples if c[2] and c[0] in sans_version)}).")
print(f"   La fiche n'en dit rien : {len(muets)}, pour {len({c[0] for c in muets})} fiches et "
      f"{len({c[1]['id'] for c in muets})} rédactions ; qu'une autre fiche a rattachée : "
      f"{sum(1 for c in muets if c[3])}.")
recentes = {c[1]["id"] for c in muets if c[1]["debut"] >= "2026-01-01"}
print(f"   Parmi elles, rédactions qui commencent en 2026 ou après : {len(recentes)}, "
      f"pour {sum(1 for c in muets if c[1]['id'] in recentes)} couples.")
for ident in sorted(recentes, key=lambda i: next(c[1]["debut"] for c in muets if c[1]["id"] == i)):
    r = next(c[1] for c in muets if c[1]["id"] == ident)
    print(f"     {r['texte']} {r['article']}, du {r['debut']} ({ident}) : "
          + ", ".join(sorted(c[0] for c in muets if c[1]["id"] == ident)))
veille = textes.non_lues(jour=date.fromisoformat(jour))
vues = sum(1 for rs in veille.values() if any(r["vivante"] and not r["homonyme"] for r in rs))
print(f"   La veille d'aujourd'hui en montre : {vues} fiche(s).")
par_mois = collections.Counter()
for groupe in par_article.values():
    if any(cite.get(r["id"]) for r in groupe):
        for r in groupe:
            if (textes._vit(r) and r["debut"] >= "2026-01-01"
                    and not any(textes._ensemble(r, a) for a in groupe if a is not r)):
                par_mois[r["debut"][:7]] += 1
print(f"   Rédactions d'articles cités, par mois de début : {dict(sorted(par_mois.items()))}")

# 2. Les réformes déclarées et les versions.
reformes = {r.code: str(r.date) for r in charger_reformes(RACINE_DONNEES)}
cas = collections.Counter()
exemples = collections.defaultdict(list)
total = 0
for nom, fiche in fiches.items():
    debuts = sorted({str(b[0]) for v in fiche.get("versions") or [] if isinstance(v, dict)
                     for b in (v.get("bornes") or {}).values()
                     if isinstance(b, list) and b and b[0] is not None and len(str(b[0])) == 10})
    annees = {str(b[0]) for v in fiche.get("versions") or [] if isinstance(v, dict)
              for b in (v.get("bornes") or {}).values()
              if isinstance(b, list) and b and b[0] is not None and len(str(b[0])) == 4}
    for code in fiche.get("reformes") or []:
        total += 1
        d = reformes[code]
        if nom in sans_version:
            sorte = "la fiche n'a pas de version"
        elif d in debuts:
            sorte = "une version commence à la date"
        elif d[:4] in annees:
            sorte = "une version commence à l'année de la réforme, sur un axe d'année"
        elif any(x[:4] == d[:4] for x in debuts):
            sorte = "une version commence la même année, un autre jour"
        else:
            sorte = "aucune version ne commence cette année-là"
        cas[sorte] += 1
        if len(exemples[sorte]) < 3:
            exemples[sorte].append(f"{nom} / {code} ({d}) ; versions : {', '.join(debuts[-3:]) or 'aucune'}")
avec = [n for n, f in fiches.items() if f.get("reformes")]
print(f"\n2. {len(avec)} fiches déclarent {total} couples fiche-réforme "
      f"({len([n for n in avec if n in sans_version])} de ces fiches sans version).")
for sorte, nombre in cas.most_common():
    print(f"   {nombre:4d}  {sorte}")
    for exemple in exemples[sorte]:
        print(f"           {exemple}")
