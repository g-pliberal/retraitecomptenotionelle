"""La durée requise du régime général, écrite une fois pour les deux calculs.

Lue dans la fiche `duree_requise_par_generation` (ses versions, leurs bornes au
jour de la date d'effet, leurs lignes de table et leurs renvois à une
rédaction antérieure) et dans sa table `duree_requise_par_version.csv`, comme
`DureesRequises.deLaPension` du moteur ; puis la pratique de la Cnav que le
moteur garde au code (`DUREES_AVANT_LE_DECRET`, lue par `moteur.mjs`), comme
`ouvrir.js`. La date d'effet s'écrit ``AAAAMMJJ`` ; la génération, au mois."""
from __future__ import annotations

import csv
from pathlib import Path

import yaml

from .calcul import Py, dans

FICHE = "data/reference/regles/duree_requise_par_generation.yaml"
TABLE = "data/reference/legislation/duree_requise_par_version.csv"
AUCUNE = 0          # « la version ne dit rien » (aucune durée ne vaut 0)
# Sans version qui parle de la génération, le moteur oppose
# `periode.duree_requise_trimestres || 160` (`ouvrir.js`) : c'est ce que reçoivent
# les nés avant 1900, que la table ne couvre pas (l'écart connu des cas attendus).
DEFAUT = 160


def _jour(d):
    return None if d is None else d.year * 10000 + d.month * 100 + d.day


def lire_versions(racine) -> list[dict]:
    racine = Path(racine)
    fiche = yaml.safe_load((racine / FICHE).read_text(encoding="utf-8"))
    lignes = [l for l in (racine / TABLE).read_text(encoding="utf-8").splitlines()
              if not l.startswith("#")]
    table = list(csv.DictReader(lignes))
    mois = lambda g: round(float(g) * 12)
    ids = [v["id"] for v in fiche["versions"]]
    versions = []
    for v in fiche["versions"]:
        debut, fin = v["bornes"]["liquidation.date_effet"]
        c = v.get("contenu", {})
        lig = (c.get("table") or {}).get("lignes") or {}
        rangs = [r for r in table
                 if all(r[k] in [str(x) for x in vals] for k, vals in lig.items())] if lig else []
        ant = c.get("redaction_anterieure")
        renvoi = None
        if ant is not None:
            n0, n1 = ant["naissance"]
            renvoi = (ids.index(ant["version"]),
                      None if n0 is None else n0.year * 12 + n0.month - 1,
                      None if n1 is None else n1.year * 12 + n1.month - 1)
        versions.append(dict(
            id=v["id"], debut=_jour(debut), fin=_jour(fin),
            table=[(mois(r["generation"]), mois(r["generation_fin"]), int(r["trimestres"]))
                   for r in rangs],
            pour_tous=(c.get("parametres") or {}).get("trimestres"), renvoi=renvoi))
    return versions


def regle(versions, B, pratique=()):
    """La fonction (g, d) -> durée requise, dans le calcul B. ``pratique`` :
    les lignes de `DUREES_AVANT_LE_DECRET` [première génération, génération
    suivante, [année, mois] de la dernière date d'effet, trimestres], lues
    dans l'ordre, la première qui baisse la durée l'emportant."""
    memo = {}

    def dans_la_version(i, g, profondeur=10):
        if B is Py:   # un terme Z3 n'est pas une clé
            cle = (i, g, profondeur)
            if cle not in memo:
                memo[cle] = _dans_la_version(i, g, profondeur)
            return memo[cle]
        return _dans_la_version(i, g, profondeur)

    def _dans_la_version(i, g, profondeur):
        v = versions[i]
        valeur = AUCUNE if v["pour_tous"] is None else v["pour_tous"]
        for (a, b, t) in reversed(v["table"]):
            valeur = B.If(dans(B, a, b, g), t, valeur)
        if v["renvoi"] is not None and profondeur > 0:
            j, a, b = v["renvoi"]
            valeur = B.If(dans(B, a, b, g), dans_la_version(j, g, profondeur - 1), valeur)
        return valeur

    def de_la_pension(d, g):
        resultat = AUCUNE
        for i in reversed(range(len(versions))):
            v = versions[i]
            # la version du jour ; muette, la première suivante qui parle
            val = AUCUNE
            for j in reversed(range(i, len(versions))):
                lue = dans_la_version(j, g)
                val = B.If(lue != AUCUNE, lue, val)
            resultat = B.If(dans(B, v["debut"], v["fin"], d), val, resultat)
        return resultat

    def regime_general(g, d):
        lue = de_la_pension(d, g)
        avec = lue
        for premiere, suivante, (an, mo), trimestres in reversed(list(pratique)):
            # la date d'effet au plus tard dans le mois (an, mo)
            limite = (an + mo // 12) * 10000 + (mo % 12 + 1) * 100 + 1
            avec = B.If(B.And(premiere * 12 <= g, g < suivante * 12, d < limite,
                              trimestres < lue), trimestres, avec)
        return B.If(lue == AUCUNE, DEFAUT, avec)

    return regime_general

