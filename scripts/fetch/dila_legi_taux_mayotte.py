#!/usr/bin/env python3
"""Le taux propre de l'indépendant de Mayotte, lu dans l'article 4-2 du décret
n° 2011-2085.

    python scripts/fetch/dila_legi_taux_mayotte.py

POURQUOI IL EXISTE. Depuis le 1er juillet 2012, l'artisan et le commerçant de
Mayotte sont affiliés au régime de base de la caisse de sécurité sociale de
Mayotte (ordonnance n° 2002-411, articles 23-1 et 23-4). Depuis 2019, leur
cotisation de vieillesse de base a son taux, que l'article 4-2 du décret
n° 2011-2085, créé par le décret n° 2019-632 « au titre des périodes courant à
compter du 1er janvier 2019 », fixe « pour chaque année civile de 2019 à
2036 » dans un tableau : 5,85 % en 2019, 0,70 point de plus chaque année,
17,75 % en 2036. Elle est assise sur le revenu « dans la limite du plafond » :
aucune part sur la totalité. Le dépôt lui prêtait la série du régime général,
celle du salarié et de son employeur (action 177, étape 8).

UNE ÉCRITURE, ET RIEN D'AUTRE : au I de l'article, le tableau « Année
Cotisation au régime d'assurance vieillesse obligatoire de base 2019 5,85 %
2020 6,55 % … », dans une cotisation assise « dans la limite du plafond ». Une
rédaction sans tableau au I, ou dont le I parle de la totalité du revenu,
arrête le récupérateur : rien n'est écrit plutôt qu'un taux deviné.

LA RÈGLE DE DATE est celle du dépôt : le taux d'une année est celui de la
rédaction qui s'applique au 1er janvier : sa date d'application quand elle
l'écrit — « au titre des périodes courant à compter du 1er janvier 2019 »,
dans la rédaction entrée en vigueur le 25 juin 2019 —, sa date d'entrée en
vigueur sinon. La série s'arrête à l'année en cours,
comme celle de D. 633-3 : le tableau de 2027 à 2036 reste au texte.

Sortie : ``data/brut/dila_taux_mayotte.json``, que
``scripts/verifier_donnees.py`` confronte aux mesures ``taux_plafonne_non_salarie``
et ``taux_deplafonne_non_salarie`` de ``cssm_mayotte``.
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
SORTIE = RACINE / "data" / "brut" / "dila_taux_mayotte.json"
ARTICLE = "4-2"
TEXTE = "Décret n° 2011-2085 du 30 décembre 2011"
#: La première année du tableau, et la dernière qu'il faut dater.
PREMIERE_ANNEE = 2019
DERNIERE_ANNEE = date.today().year

APPLICATION = re.compile(r"périodes courant à compter du 1er janvier (\d{4})")
ALINEA_I = re.compile(r"(?<![IVX])I\s*\.\s*-")
ALINEA_II = re.compile(r"(?<![IVX])II\s*\.\s*-")
TABLEAU = re.compile(r"\bAnnée Cotisation\b")
LIGNE = re.compile(r"\b(\d{4}) (\d+,\d+) %")


def _taux(texte: str) -> float:
    return round(float(texte.replace(",", ".")) / 100, 6)


def lire_redaction(ident: str, debut: str, texte: str) -> dict:
    """Une rédaction : sa date d'application et le tableau de son I."""
    texte = texte.replace("’", "'")
    application = APPLICATION.search(texte)
    # La date qu'écrit la rédaction l'emporte, même antérieure à son entrée en
    # vigueur : celle du 25 juin 2019 vaut pour les périodes depuis le 1er janvier.
    debut_effet = f"{application.group(1)}-01-01" if application else debut
    premier, second = ALINEA_I.search(texte), ALINEA_II.search(texte)
    if premier is None or second is None or second.start() < premier.end():
        raise ValueError(f"{ident} : les alinéas I et II ne se lisent pas")
    alinea = texte[premier.end():second.start()]
    tableau = TABLEAU.search(alinea)
    if tableau is None:
        raise ValueError(f"{ident} : aucun tableau au I « {alinea[:160]} »")
    if "dans la limite du plafond" not in alinea or "totalité" in alinea:
        raise ValueError(f"{ident} : le I n'est pas une cotisation dans la limite du "
                         "plafond seule")
    plafonne = {int(a): _taux(t) for a, t in LIGNE.findall(alinea[tableau.end():])}
    if not plafonne:
        raise ValueError(f"{ident} : un tableau vide au I")
    return {"id": ident, "debut": debut, "application": debut_effet, "plafonne": plafonne}


def series(redactions: list[dict]) -> dict[str, dict]:
    """Le taux de chaque année, celui de la rédaction qui s'applique au
    1er janvier ; rien sur la totalité du revenu."""
    sortie: dict[str, dict] = {}
    for annee in range(PREMIERE_ANNEE, DERNIERE_ANNEE + 1):
        jour = f"{annee}-01-01"
        candidates = [r for r in redactions if r["application"] <= jour]
        if not candidates:
            raise ValueError(f"{annee} : aucune rédaction ne s'applique au 1er janvier")
        redaction = max(candidates, key=lambda r: (r["application"], r["debut"]))
        if annee not in redaction["plafonne"]:
            raise ValueError(f"{annee} : absente du tableau de {redaction['id']}")
        sortie[str(annee)] = {"plafonne": redaction["plafonne"][annee], "deplafonne": 0.0,
                              "article": redaction["id"]}
    return sortie


def main() -> int:
    chemin = chemin_index("legi")
    if not chemin.exists():
        print(f"{chemin} absent — python scripts/fetch/dila_index.py legi --recuperer",
              file=sys.stderr)
        return 1
    db = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    lignes = db.execute(
        "SELECT id, date, fin, texte FROM doc WHERE replace(num, ' ', '') = ?"
        " AND titre LIKE ? ORDER BY date",
        (ARTICLE, f"{TEXTE}%")).fetchall()
    if not lignes:
        print(f"article {ARTICLE} du {TEXTE} absent de l'index", file=sys.stderr)
        return 1
    redactions = [lire_redaction(ident, debut, texte) for ident, debut, _, texte in lignes]
    donnees = {
        "source": f"DILA, base LEGI, {TEXTE}, article 4-2",
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
