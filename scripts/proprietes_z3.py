#!/usr/bin/env python3
"""Le contrôle Z3 des propriétés du droit (action 194).

    python scripts/proprietes_z3.py                    # tout : comparaisons et propriétés
    python scripts/proprietes_z3.py --resultats DOSSIER --github   # comme sur GitHub
    python scripts/proprietes_z3.py --sans-moteur      # les propriétés seules
    python scripts/proprietes_z3.py --seulement duree  # celles dont le nom commence ainsi
    python scripts/proprietes_z3.py --liste            # les noms des propriétés

Ce qu'il fait. Les règles de `scripts/regles_z3/` — la durée requise, l'âge
légal, l'âge du taux plein, la carrière longue, la pension du régime général
avec décote, proratisation et surcote —, lues dans les fiches et le paquet,
sont d'abord exécutées et comparées au moteur (toutes les générations de 1900
à 2010, toutes les dates d'effet au mois, et des carrières avec surcote
rejouées dans le moteur complet) : c'est ce qui fait que les propriétés
prouvées parlent du moteur. Puis Z3 cherche, pour chaque propriété — couverture
des dates de toute fiche datée par la date d'effet, monotonies des âges et des
durées, « partir plus tard ne baisse pas la pension »… —, un contre-exemple
hors des cas attendus (`tests/cliquets_de_justesse/proprietes_attendues.yaml`).

Ce qu'il rend. Un rapport (`rapport.md` dans `--resultats`, et la sortie) ;
avec `--github`, une annotation d'avertissement par surprise. Sortie 0 : rien
d'inattendu ; 1 : une surprise (propriété fausse hors des cas attendus, cas
attendu disparu, règle qui s'écarte du moteur, question indécise) ; autre
chose : le contrôle a cassé. Le workflow `.github/workflows/proprietes.yml` le
lance après chaque course de la suite, et ne bloque rien : il avertit.

Ce qu'il ne fait pas. Il ne prouve pas la lecture du droit : une fiche qui se
tromperait de chiffre de façon cohérente passe. Z3 ne garde pas de preuve, il
dit « aucun contre-exemple ».
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

from regles_z3 import controle, duree, fiches, moteur, questions  # noqa: E402
from regles_z3.calcul import AUCUN, Py, ecrire_jour, ecrire_mois, rang_du_jour  # noqa: E402

ATTENDUS = RACINE / "tests" / "cliquets_de_justesse" / "proprietes_attendues.yaml"
CARRIERES_SURCOTE = 250


# ------------------------------------------------------------ comparaisons
def comparer_durees(extrait) -> tuple[str, int, list]:
    rg = duree.regle(duree.lire_versions(RACINE), Py, extrait["durees_avant_le_decret"])
    lignes = ((int(g), int(d), int(t)) for g, d, t in moteur.lignes(RACINE, "durees"))
    n, ecarts = controle.comparer(rg, lignes)
    return "Durée requise (générations 1900 à 1999, dates d'effet 1980 à 2040)", n, [
        f"né en {ecrire_mois(g)}, pension du {ecrire_jour(d)} : moteur {m}, règle {r}"
        for (g, d), m, r in ecarts]


def comparer_fiches() -> list[tuple[str, int, list]]:
    """L'âge légal, l'âge du taux plein et les portes de la carrière longue,
    chaque mois de 1980 à 2045, et l'âge de la personne."""
    F = fiches.charger(RACINE)
    cles = fiches.cles_des_portes(F)
    indices: dict = {}

    def indice(nom, d):
        for i, v in enumerate(fiches.versions_triees(F[nom])):
            a, b = v["bornes"]["liquidation.date_effet"]
            if (a is None or rang_du_jour(a) <= d) and (b is None or d < rang_du_jour(b)):
                return i
        return -1

    def memo(regle, noms):
        """La règle, gardée par génération et versions en vigueur : elle ne
        change qu'aux bornes des versions."""
        cache = {}

        def f(g, d):
            if d not in indices:
                indices[d] = {n: indice(n, d) for n in
                              ("age_legal_par_generation", "age_annulation_decote", "carriere_longue")}
            cle = (g,) + tuple(indices[d][n] for n in noms)
            if cle not in cache:
                cache[cle] = regle(g, d)
            return cache[cle]
        return f

    L = memo(fiches.age_legal(Py, F), ["age_legal_par_generation"])
    T = memo(fiches.age_taux_plein(Py, F), ["age_legal_par_generation", "age_annulation_decote"])
    P = {c: memo(fiches.porte(Py, F, c), ["age_legal_par_generation", "carriere_longue"]) for c in cles}

    def personne(regle, g):
        for d in range(max(1980 * 12, g), 2120 * 12):
            a = regle(g, d)
            if a != AUCUN and d >= g + 1 + a:
                return a
        return AUCUN

    n = {"legal": 0, "plein": 0, "portes": 0, "personne": 0}
    e: dict = {k: [] for k in n}

    def ecart(cle, texte):
        if len(e[cle]) < 20:
            e[cle].append(texte)
        else:
            e[cle].append(None)

    for x in moteur.lignes(RACINE, "fiches"):
        if x[0] == "P":
            g, l, t = map(int, x[1:])
            if g + 1 + 60 * 12 < 1980 * 12:      # l'âge atteint avant la grille
                continue
            for nom, regle, lu in (("âge légal", L, l), ("taux plein", T, t)):
                n["personne"] += 1
                if personne(regle, g) != lu:
                    ecart("personne", f"{nom} de la personne née en {ecrire_mois(g)} : moteur {lu}, "
                                      f"règle {personne(regle, g)} mois")
            continue
        g, d, l, t = map(int, x[1:5])
        n["legal"] += 1; n["plein"] += 1; n["portes"] += 1
        if L(g, d) != l:
            ecart("legal", f"né en {ecrire_mois(g)}, 1er {ecrire_mois(d)} : moteur {l}, règle {L(g, d)} mois")
        if T(g, d) != t:
            ecart("plein", f"né en {ecrire_mois(g)}, 1er {ecrire_mois(d)} : moteur {t}, règle {T(g, d)} mois")
        nous = ",".join(sorted(f"{c[0]}:{c[1]}:{P[c](g, d)}" for c in cles if P[c](g, d) != AUCUN))
        lu = "" if x[5] == "-" else x[5]
        if nous != lu:
            ecart("portes", f"né en {ecrire_mois(g)}, 1er {ecrire_mois(d)} : moteur {lu or 'aucune'}, "
                            f"règle {nous or 'aucune'}")
    titres = {"legal": "Âge légal (générations 1900 à 2010, dates d'effet 1980 à 2045)",
              "plein": "Âge du taux plein (mêmes cas)",
              "portes": "Portes de la carrière longue (mêmes cas)",
              "personne": "Âge légal et âge du taux plein de la personne"}
    return [(titres[k], n[k], [x for x in e[k] if x]) for k in n]


def comparer_surcote(extrait, nombre: int) -> tuple[str, int, list]:
    """Le taux de liquidation du modèle avec surcote contre le moteur complet,
    par le pont du dépôt (sans écrire dans le témoin figé), sur des carrières
    continues tirées au hasard, à graine fixe."""
    import z3
    sys.path.insert(0, str(RACINE / "tests"))
    import test_oracle as oracle
    from outils_pont import DROIT_DU_PORTAGE
    from regles_z3.pension import Modele

    def direct(appels, parametres=None):
        return DROIT_DU_PORTAGE(appels, parametres, None)

    M = Modele(RACINE, extrait)
    gv, mv, Tv = z3.Ints("cmp_g cmp_m cmp_T")
    _, X = M.pension(gv, mv, Tv)
    hasard = random.Random(21112026)
    cas = []
    while len(cas) < nombre:
        a, mo = hasard.randint(1940, 1966), hasard.randint(1, 12)
        g = a * 12 + mo - 1
        age = hasard.randint(62 * 12, 70 * 12)
        m = g + age
        if m < 2004 * 12 or m >= 2036 * 12:
            continue
        cas.append((g, m, hasard.randint(150, 4 * (age // 12 - 16))))
    ecarts = []
    for g, m, T in cas:
        s = z3.Solver()
        s.add(gv == g, mv == m, Tv == T)
        s.check()
        mod = s.model()
        nous = float(mod.eval(X["taux_liquidation"], model_completion=True).as_fraction())
        ex = {"id": "z3", "carriere": {"naissance": f"{g // 12}-{g % 12 + 1:02d}-01", "sexe": "H",
              "affiliation": "salarie_prive_non_cadre", "liquidation": f"{m // 12}-{m % 12 + 1:02d}",
              "trimestres_valides": T}, "attendu": {"taux_liquidation": 0}}
        _, r = oracle._carriere_exemple(ex, droit=direct)
        if r["trimestres_valides"] != T or abs(r["taux_liquidation"] - nous) > 1e-9:
            ecarts.append(f"né en {ecrire_mois(g)}, effet {ecrire_mois(m)}, {T} trimestres "
                          f"(moteur {r['trimestres_valides']}) : taux du moteur "
                          f"{r['taux_liquidation']:.6f}, du modèle {nous:.6f}")
    return f"Pension avec surcote, {nombre} carrières rejouées dans le moteur complet", len(cas), ecarts[:20]


# -------------------------------------------------------------- le rapport
ETIQUETTES = {"prouvee": "prouvée", "attendue": "prouvée hors des cas attendus",
              "surprise": "**SURPRISE**", "indecise": "**indécise** (délai dépassé)"}


def _rapport(comparaisons, resultats, duree_totale) -> tuple[str, list[str]]:
    lignes, alertes = [], []
    lignes += ["# Contrôle Z3 des propriétés du droit", ""]
    lignes += [f"{len(resultats)} propriétés, {len(comparaisons)} comparaisons au moteur, "
               f"en {duree_totale:.0f} s.", ""]
    lignes += ["## La règle écrite pour Z3 contre le moteur", ""]
    for titre, n, ecarts in comparaisons:
        lignes.append(f"- {titre} : {n} cas, " + ("aucun écart" if not ecarts else f"**{len(ecarts)} écart(s)**"))
        for e in ecarts:
            lignes.append(f"  - {e}")
        if ecarts:
            alertes.append(f"La règle écrite pour Z3 s'écarte du moteur — {titre} : {ecarts[0]}")
    lignes += ["", "## Les propriétés", "", "| Propriété | Verdict | Durée |", "|---|---|---|"]
    for r in resultats:
        lignes.append(f"| {r.propriete.titre} (`{r.propriete.id}`) | {ETIQUETTES[r.statut]} | {r.duree:.1f} s |")
    surprises = [r for r in resultats if r.surprises or r.disparus or r.statut == "indecise"]
    if surprises:
        lignes += ["", "## Les surprises", ""]
    for r in surprises:
        lignes += [f"### {r.propriete.titre}", "", f"`{r.propriete.id}`", ""]
        for s in r.surprises:
            lignes.append(f"- contre-exemple : {s['texte']}")
            alertes.append(f"{r.propriete.titre} — contre-exemple : {s['texte']}")
        for a in r.disparus:
            lignes.append(f"- cas attendu que plus rien ne réalise : {a['titre'].strip()}")
            alertes.append(f"{r.propriete.titre} — cas attendu disparu : {a['titre'].strip()}")
        if r.statut == "indecise":
            lignes.append("- Z3 n'a pas répondu dans le délai")
            alertes.append(f"{r.propriete.titre} — indécise : Z3 n'a pas répondu dans le délai")
        lignes.append("")
    avec = [r for r in resultats if r.attendus]
    if avec:
        lignes += ["", "## Les cas attendus, chacun avec un exemple", ""]
    for r in avec:
        for a, ex in r.attendus:
            nature = "voulu par la loi" if a["nature"] == "legal" else "écart connu, non corrigé"
            lignes += [f"- **{a['titre'].strip()}** ({nature}, `{r.propriete.id}`)",
                       f"  - exemple : {ex['texte']}", f"  - source : {a['source'].strip()}"]
    return "\n".join(lignes) + "\n", alertes


def _annotation(texte: str) -> str:
    """Une ligne `::warning` : GitHub y lit `%`, les retours à la ligne et `::`."""
    texte = texte.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
    return f"::warning title=Contrôle Z3::{texte}"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--resultats", type=Path)
    p.add_argument("--github", action="store_true", help="une annotation d'avertissement par surprise")
    p.add_argument("--sans-moteur", action="store_true", help="les propriétés seules")
    p.add_argument("--seulement", default="", help="les propriétés dont le nom commence ainsi")
    p.add_argument("--liste", action="store_true")
    p.add_argument("--carrieres", type=int, default=CARRIERES_SURCOTE)
    args = p.parse_args(argv)

    t0 = time.time()
    extrait = moteur.extraire(RACINE)
    props = [x for x in questions.catalogue(RACINE, extrait) if x.id.startswith(args.seulement)]
    if args.liste:
        for x in props:
            print(f"{x.id}\t{', '.join(x.champs)}\t{x.titre}")
        return 0
    attendus = yaml.safe_load(ATTENDUS.read_text(encoding="utf-8"))["attendus"]
    inconnus = {a["propriete"] for a in attendus} - {x.id for x in questions.catalogue(RACINE, extrait)}
    if inconnus:
        print(f"Cas attendus d'une propriété inconnue : {sorted(inconnus)}", file=sys.stderr)
        return 2

    comparaisons = []
    if not args.sans_moteur:
        comparaisons.append(comparer_durees(extrait))
        comparaisons += comparer_fiches()
        comparaisons.append(comparer_surcote(extrait, args.carrieres))
        for titre, n, ecarts in comparaisons:
            print(f"{titre} : {n} cas, {len(ecarts)} écart(s)", flush=True)

    resultats = []
    for x in props:
        r = controle.verifier(x, attendus)
        resultats.append(r)
        print(f"{ETIQUETTES[r.statut].strip('*'):32s} {r.duree:6.1f} s  {x.id}", flush=True)
        for s in r.surprises:
            print(f"    contre-exemple : {s['texte']}")
        for a in r.disparus:
            print(f"    cas attendu disparu : {a['titre'].strip()}")

    texte, alertes = _rapport(comparaisons, resultats, time.time() - t0)
    if args.resultats:
        args.resultats.mkdir(parents=True, exist_ok=True)
        (args.resultats / "rapport.md").write_text(texte, encoding="utf-8")
    if args.github:
        for a in alertes:
            print(_annotation(a))
    print(f"\n{len(alertes)} surprise(s) en {time.time() - t0:.0f} s")
    return 1 if alertes else 0


if __name__ == "__main__":
    sys.exit(main())
