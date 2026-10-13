#!/usr/bin/env python3
"""Le barème propre des artisans et des commerçants, lu dans D. 633-3.

    python scripts/fetch/dila_legi_taux_independants.py

POURQUOI IL EXISTE. Depuis 2018, l'artisan et le commerçant cotisent à la
vieillesse de base du régime général, mais à LEUR barème : 17,15 % sous le
plafond et 0,60 % sur la totalité du revenu, 0,72 % depuis 2025, quand le
salarié et son employeur versent 15,45 % et 2,30 à 2,51 %. Le dépôt leur
prêtait le second jusqu'au 13 octobre 2026 (action 138, étape 18). Ce barème
n'est pas une statistique : c'est l'article D. 633-3 du code de la sécurité
sociale, dont l'index LEGI du dépôt (``dila_index.py legi --recuperer``) garde
les rédactions successives depuis sa création, le 1er janvier 2014.

TROIS ÉCRITURES, ET RIEN D'AUTRE

* un taux par alinéa : « est fixé à 17,15 % » ;
* un calendrier : « a) 16,95 % pour l'année 2014 ; b) 17,05 % pour l'année
  2015 ; c) 17,15 % à compter de l'année 2016 » ;
* une dérogation en note : « pour l'année 2016, par dérogation […] le taux de
  la cotisation mentionné au II de l'article D. 633-3 est fixé à 0,5 % ».

Une rédaction que ces trois formes ne décrivent pas arrête le récupérateur :
rien n'est écrit plutôt qu'un taux deviné.

LA RÈGLE DE DATE est celle du dépôt : le taux d'une année est celui de la
rédaction en vigueur au 1er janvier, ou, quand la rédaction écrit sa date
d'application — « au titre des périodes courant à compter du 1er janvier
2025 » —, de celle qui s'applique à cette date.

Sortie : ``data/brut/dila_taux_independants.json``, que
``scripts/verifier_donnees.py`` confronte aux mesures ``taux_plafonne_non_salarie``
et ``taux_deplafonne_non_salarie`` du régime général.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dila_index import chemin_index, meta  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "brut" / "dila_taux_independants.json"
ARTICLE = "D633-3"
CODE = "Code de la sécurité sociale"
#: Création de l'article, et dernière année qu'il faut dater.
PREMIERE_ANNEE = 2014
DERNIERE_ANNEE = date.today().year

TAUX = r"(\d+(?:,\d+)?)\s*%"
POUR_L_ANNEE = re.compile(TAUX + r" pour l'année (\d{4})")
A_COMPTER = re.compile(TAUX + r" à compter de l'année (\d{4})")
FIXE = re.compile(r"est fixé à " + TAUX)
DEROGATION = re.compile(
    r"pour l'année (\d{4}), par dérogation .*? mentionné au (I|II) de l'article "
    r"D\. 633-3 est fixé à " + TAUX)
APPLICATION = re.compile(r"périodes courant à compter du 1er janvier (\d{4})")
ALINEA_I = re.compile(r"(?<![IVX])I\s*\.\s*-")
ALINEA_II = re.compile(r"(?<![IVX])II\s*\.\s*-")


def _taux(texte: str) -> float:
    return round(float(texte.replace(",", ".")) / 100, 6)


def _bareme(alinea: str, lieu: str) -> list[tuple[int, int, float]]:
    """Les taux d'un alinéa : (première année, dernière, taux)."""
    calendrier = [(int(a), int(a), _taux(t)) for t, a in POUR_L_ANNEE.findall(alinea)]
    calendrier += [(int(a), DERNIERE_ANNEE, _taux(t)) for t, a in A_COMPTER.findall(alinea)]
    if calendrier:
        return sorted(calendrier)
    fixes = FIXE.findall(alinea)
    if len(fixes) != 1:
        raise ValueError(f"{lieu} : ni calendrier ni taux unique dans « {alinea[:160]} »")
    return [(PREMIERE_ANNEE, DERNIERE_ANNEE, _taux(fixes[0]))]


def lire_redaction(ident: str, debut: str, texte: str) -> dict:
    """Une rédaction : sa date d'application, ses deux barèmes et ses
    dérogations."""
    texte = texte.replace("\u2019", "'")
    application = APPLICATION.search(texte)
    debut_effet = max(debut, f"{application.group(1)}-01-01") if application else debut
    premier, second = ALINEA_I.search(texte), ALINEA_II.search(texte)
    if premier is None or second is None or second.start() < premier.end():
        raise ValueError(f"{ident} : les alinéas I et II ne se lisent pas")
    note = texte[:premier.start()]
    morceaux = (texte[premier.end():second.start()], texte[second.end():])
    derogations = {(int(a), alinea): _taux(t) for a, alinea, t in DEROGATION.findall(note)}
    return {
        "id": ident,
        "debut": debut,
        "application": debut_effet,
        "plafonne": _bareme(morceaux[0], f"{ident}, I"),
        "deplafonne": _bareme(morceaux[1], f"{ident}, II"),
        "derogations": derogations,
    }


def series(redactions: list[dict]) -> dict[str, dict]:
    """Le taux de chaque année, celui de la rédaction qui s'applique au
    1er janvier."""
    sortie: dict[str, dict] = {}
    for annee in range(PREMIERE_ANNEE, DERNIERE_ANNEE + 1):
        jour = f"{annee}-01-01"
        candidates = [r for r in redactions if r["application"] <= jour]
        if not candidates:
            raise ValueError(f"{annee} : aucune rédaction ne s'applique au 1er janvier")
        redaction = max(candidates, key=lambda r: (r["application"], r["debut"]))
        taux = {}
        for cle, alinea in (("plafonne", "I"), ("deplafonne", "II")):
            valeurs = [t for premiere, derniere, t in redaction[cle]
                       if premiere <= annee <= derniere]
            if len(valeurs) != 1:
                raise ValueError(f"{annee} : {len(valeurs)} taux {cle} dans {redaction['id']}")
            taux[cle] = redaction["derogations"].get((annee, alinea), valeurs[0])
        sortie[str(annee)] = {**taux, "article": redaction["id"]}
    return sortie


def main() -> int:
    chemin = chemin_index("legi")
    if not chemin.exists():
        print(f"{chemin} absent — python scripts/fetch/dila_index.py legi --recuperer",
              file=sys.stderr)
        return 1
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    # L'article portait jusqu'en 2008 une autre règle, la déclaration des
    # revenus ; le barème y naît le 1er janvier 2014.
    lignes = db.execute(
        "SELECT id, date, fin, texte FROM doc WHERE replace(replace(upper(num), ' ', ''),"
        " '.', '') = ? AND titre = ? AND date >= ? ORDER BY date",
        (ARTICLE, CODE, f"{PREMIERE_ANNEE}-01-01")).fetchall()
    if not lignes:
        print(f"{ARTICLE} absent de l'index", file=sys.stderr)
        return 1
    redactions = [lire_redaction(ident, debut, texte) for ident, debut, _, texte in lignes]
    donnees = {
        "source": f"DILA, base LEGI, {CODE}, article D. 633-3",
        "index": f"{meta(db, 'dump')}, incréments appliqués jusqu'au "
                 f"{meta(db, 'dernier_increment')}",
        "lu_le": date.today().isoformat(),
        "redactions": [{"id": r["id"], "debut": r["debut"], "application": r["application"]}
                       for r in redactions],
        "series": series(redactions),
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(donnees, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    for annee, taux in donnees["series"].items():
        print(f"{annee}  {taux['plafonne']:.4f}  {taux['deplafonne']:.4f}  {taux['article']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
