#!/usr/bin/env python3
"""Récupération du salaire minimum ANNUEL à temps complet, 1951-2012, à l'INSEE.

    python scripts/fetch/insee_sls_smic.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
Le salaire d'une année entière au salaire minimum, à temps complet : le revenu
du cas type « salarié au niveau du SMIC ». Le modèle l'écrivait 0,55 fois le
salaire moyen, à toutes les années, quand le minimum en a valu un peu plus du
tiers à la fin des années 1960 et un peu plus de la moitié aujourd'hui
(action 147, étape 16).

Le barème horaire ne suffit pas à le dire. Il change en cours d'année — en
juillet jusqu'en 2009, plusieurs fois l'an pendant l'inflation des années 1970
— et il se multiplie par une DURÉE LÉGALE qui a changé deux fois : 40 heures
par semaine (173,33 heures par mois) jusqu'en 1981, 39 heures (169) à compter
de 1982, 35 heures (151,67) avec les lois Aubry. L'INSEE a fait ce calcul, sur
les barèmes exacts et non sur leur conversion en euros arrondie au centime,
dans ses « Séries longues sur les salaires (1950-2010) » : le tableau SM02, du
SMIG de 1951 au SMIC de 2005 sur la durée d'avant les 35 heures, et le tableau
SM01, de 2000 à 2012 sur 35 heures. Chacun donne, année par année, la durée
légale mensuelle, le salaire horaire moyen de l'année, le mensuel et l'annuel.

Au-delà de 2012, l'annuel se refait sans perte depuis la série mensuelle du
SMIC horaire de la banque de données macroéconomiques (``insee_bdm.py``,
série ``smic_horaire_mensuel``) : le SMIC se fixe au centime d'euro depuis
2002, et la série le porte donc exactement. ``scripts/verifier_donnees.py``
vérifie que les deux sources donnent le même annuel au centime sur les années
qu'elles partagent.

Le fichier produit, ``data/brut/insee_sls_smic.json``, est le document
source : il n'est pas lu par le modèle, seulement par le vérificateur, qui en
écrit ``data/reference/macro/smic_annuel.csv``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xls import feuilles  # noqa: E402

BASE = "https://www.insee.fr/fr/statistiques/fichier/2122816"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/insee_sls_smic.json")

#: Les deux tableaux, sous leur nom à l'INSEE, et la durée légale HEBDOMADAIRE
#: qu'ils supposent — le titre la dit pour SM01, la note de l'INSEE pour SM02.
TABLEAUX = {
    "SM02": "Salaire minimum avant le passage aux 35 heures, 1951-2005",
    "SM01": "Salaire minimum pour 35 heures hebdomadaires, 2000-2012",
}

#: Les colonnes lues, dans l'ordre où l'INSEE les donne après l'année. Les
#: en-têtes sont RELUS : un tableau republié dans un autre ordre doit échouer
#: plutôt que d'échanger le mensuel et l'annuel.
COLONNES = {
    "duree_mensuelle": "Durée légale mensuelle (heures)",
    "horaire": "Salaire minimum brut (horaire)",
    "mensuel": "Salaire minimum brut (mensuel)",
    "annuel": "Salaire minimum brut (annuel)",
}


def lire(contenu: bytes) -> dict[str, dict[str, float]]:
    """Les lignes annuelles d'un tableau SM : ``{année: {colonne: valeur}}``."""
    (cellules,) = feuilles(contenu).values()
    entetes = {cellules.get((2, colonne)): colonne for colonne in range(1, 12)}
    rangs = {}
    for cle, titre in COLONNES.items():
        if titre not in entetes:
            raise ValueError(f"colonne « {titre} » absente du tableau")
        rangs[cle] = entetes[titre]
    annees = {}
    for ligne in range(3, 200):
        annee = cellules.get((ligne, 0))
        if not (isinstance(annee, str) and annee.isdigit()):
            continue
        annees[annee] = {cle: float(cellules[(ligne, rang)]) for cle, rang in rangs.items()}
    if not annees:
        raise ValueError("aucune ligne annuelle dans le tableau")
    return annees


def main() -> int:
    tableaux = {}
    for nom, titre in TABLEAUX.items():
        url = f"{BASE}/SLS2010_{nom}.xls"
        demande = urllib.request.Request(url, headers=ENTETES)
        try:
            with urllib.request.urlopen(demande, timeout=120) as reponse:
                contenu = reponse.read()
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"ÉCHEC   {nom} ({url}) : {erreur}", file=sys.stderr)
            return 1
        annees = lire(contenu)
        tableaux[nom] = {"titre": titre, "url": url, "annees": annees}
        print(f"OK      {nom}  {len(annees)} années {min(annees)}-{max(annees)}")
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    charge = {"source": BASE, "recupere_le": date.today().isoformat(), "tableaux": tableaux}
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(tableaux)} tableaux écrits dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
