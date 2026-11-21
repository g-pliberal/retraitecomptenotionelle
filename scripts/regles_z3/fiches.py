"""L'âge légal, l'âge du taux plein et la carrière longue, écrits une fois
pour les deux calculs.

La règle se lit dans le paquet que le moteur lit (`moteur/donnees.json`,
`fiches_datees`), que la fabrique tire des fiches YAML du dépôt : les versions,
leurs bornes de date d'effet, leurs tables, leurs renvois. Comme
`AgesOuverture`, `AgesAnnulationDecote` et `CarriereLongue.portes` du moteur.
Tout en mois : les tables du paquet, en années décimales, sont ramenées au mois
le plus proche."""
from __future__ import annotations

import json
from pathlib import Path

from .calcul import AUCUN, dans, mois, rang_du_jour


def charger(racine) -> dict:
    return json.loads((Path(racine) / "moteur" / "donnees.json").read_text(encoding="utf-8"))["fiches_datees"]


def versions_triees(fiche):
    return sorted(fiche["versions"],
                  key=lambda v: rang_du_jour(v["bornes"]["liquidation.date_effet"][0]) or -10**9)


def par_date(B, fiche, d, valeur_de):
    """La valeur que donne la version en vigueur au mois d ; AUCUN hors de toute version."""
    r = AUCUN
    for v in reversed(versions_triees(fiche)):
        debut, fin = v["bornes"]["liquidation.date_effet"]
        r = B.If(dans(B, rang_du_jour(debut), rang_du_jour(fin), d), valeur_de(v), r)
    return r


# ---------------------------------------------------------------- âge légal
def age_dans_la_version(B, fiche, v, g, nom="age", profondeur=5):
    """ageDansLaVersion du moteur : renvoi à la rédaction antérieure, puis la
    table, puis le paramètre écrit pour tous."""
    val = AUCUN if v["parametres"].get(nom) is None else mois(v["parametres"][nom])
    for (a, b, age, _f) in reversed(v.get("table") or []):
        val = B.If(dans(B, mois(a), mois(b), g), mois(age), val)
    ant = v.get("redaction_anterieure")
    if ant is not None and profondeur > 0:
        a, b = ant.get("generations") or [None, None]
        cible = next(x for x in fiche["versions"] if x["id"] == ant["version"])
        val = B.If(dans(B, mois(a), mois(b), g),
                   age_dans_la_version(B, fiche, cible, g, nom, profondeur - 1), val)
    return val


def age_legal(B, fiches):
    f = fiches["age_legal_par_generation"]
    return lambda g, d: par_date(B, f, d, lambda v: age_dans_la_version(B, f, v, g))


# ------------------------------------------------------- âge du taux plein
def valeur_du_renvoi(B, fiches, renvoi, g, d):
    """valeurDuRenvoi : dans la version de la fiche nommée à la même date, le
    paramètre nommé, ou l'âge de la génération ; plus les mois du renvoi."""
    cible = fiches[renvoi["fiche"]]

    def lue(v):
        p = v["parametres"].get(renvoi["valeur"])
        base = mois(p) if p is not None else (
            age_dans_la_version(B, cible, v, g) if renvoi["valeur"] == "age" else AUCUN)
        return B.If(base == AUCUN, AUCUN, base + renvoi["mois"])
    return par_date(B, cible, d, lue)


def age_taux_plein(B, fiches):
    f = fiches["age_annulation_decote"]

    def de_la_version(v, g, d):
        if "age" in v["parametres"]:
            return AUCUN if v["parametres"]["age"] is None else mois(v["parametres"]["age"])
        (r,) = v["renvois"]
        return valeur_du_renvoi(B, fiches, r, g, d)
    return lambda g, d: par_date(B, f, d, lambda v: de_la_version(v, g, d))


# --------------------------------------------------------- carrière longue
COLONNES = ["gen", "fin", "age_debut_maximum", "trimestres_debut", "age_depart",
            "supplement", "assurance", "fiabilite"]


def lignes_de_la_version(v):
    """Les portes de la version et celles que ses renvois écrivent (à l'âge
    près, que le renvoi lit à la date) : (gen, fin, ageMax, tdebut, renvoi ou
    âge en mois, supplément, assurance)."""
    lignes = [(mois(p[0]), mois(p[1]), p[2], p[3], mois(p[4]), p[5], p[6]) for p in v.get("portes") or []]
    for r in v.get("renvois") or []:
        modele = next(p for p in v["portes"] if p[0] == 1900.0 and all(
            p[COLONNES.index(k)] == val for k, val in r["ligne"].items()))
        a, b = r["generations"]
        lignes.append((mois(a), mois(b), modele[2], modele[3], r, modele[5], modele[6]))
    return lignes


def cles_des_portes(fiches):
    """Toutes les portes (borne d'entrée, supplément) qu'une version écrit."""
    cles = set()
    for v in fiches["carriere_longue"]["versions"]:
        for l in lignes_de_la_version(v):
            cles.add((l[2], l[5]))
    return sorted(cles)


def porte(B, fiches, cle):
    """(g, d) -> l'âge de départ de la porte `cle` (borne d'entrée, supplément)
    à la date d, AUCUN si la version ne l'ouvre pas à cette génération : parmi
    les lignes qui couvrent la génération, celle de la plus haute génération
    de début (D. 351-1-1, II, comme CarriereLongue.portes)."""
    f = fiches["carriere_longue"]

    def de_la_version(v, g, d):
        lignes = [(i, l) for i, l in enumerate(lignes_de_la_version(v)) if (l[2], l[5]) == cle]
        # la plus haute génération l'emporte ; à égalité, la première écrite
        lignes = [l for _, l in sorted(lignes, key=lambda il: (il[1][0], -il[0]))]
        val = AUCUN
        for (a, b, _m, _t, age, _s, _as) in lignes:
            if isinstance(age, dict):
                lu = valeur_du_renvoi(B, fiches, age, g, d)
            else:
                lu = age
            val = B.If(dans(B, a, b, g), lu, val)
        return val
    return lambda g, d: par_date(B, f, d, lambda v: de_la_version(v, g, d))


def meilleur_age(B, fiches, debut_avant):
    """Le plus petit âge de départ qu'ouvrent les portes dont la borne d'entrée
    est au moins `debut_avant` (qui a commencé avant la fin de l'année de ses
    `debut_avant` ans entre par toutes ces portes), toutes durées réunies.
    AUCUN si aucune ne s'ouvre."""
    portes = [porte(B, fiches, c) for c in cles_des_portes(fiches) if c[0] >= debut_avant]

    def f(g, d):
        best = AUCUN
        for p in portes:
            x = p(g, d)
            best = B.If(x == AUCUN, best, B.If(B.Or(best == AUCUN, x < best), x, best))
        return best
    return f
