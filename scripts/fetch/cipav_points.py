#!/usr/bin/env python3
"""Le prix et la valeur du point de la complémentaire de la Cipav, saisis
depuis les textes et les fiches de la caisse.

    python scripts/fetch/cipav_points.py

Rien n'est téléchargé : aucune table de la caisse ne porte ces séries. Le
décret n° 79-262 dit que « le montant de la pension est égal au produit du
nombre de points acquis […] par la valeur de service du point » (article 5-2),
et son article 2 donne les points de chaque classe de cotisation. Le script en
tire ce qu'il faut au moteur pour compter ces points, au lieu du rendement de
l'année du départ qu'il appliquait jusqu'au 20 novembre 2026.

LE PRIX DU POINT (``salaire_reference``), en points d'aujourd'hui.

* De 1979 à 2012, la classe 1 « porte attribution de quatre points »
  (LEGIARTI000006767473), que la conversion du 1er janvier 2013 a multipliés
  par dix : le quarantième de sa cotisation, que le décret annuel fixe
  (`regimes/classes_cotisation_epoques.yaml`, d'où le script la lit).
* De 2013 à 2022, la classe A porte attribution de 36 points
  (LEGIARTI000026892951) : le trente-sixième de sa cotisation.
* Depuis 2023, le « coût d'acquisition du point » : 45,30 € en 2023 (statuts,
  arrêté du 20 mars 2023), 47,40 € en 2024 et 2025 (décrets n° 2024-1214 et
  n° 2025-1076), 47,40 € en 2026 (fiche pratique 2026 de la caisse, « Cotiser
  pour acquérir des droits à retraite » : « 3 600 € / 47,40 € »).

Une année dont le décret est lu vaut le niveau ``moyenne`` ; une année dont la
cotisation est ramenée d'une autre au rapport des plafonds, ``estimee``.

LA VALEUR DE SERVICE. 2,63 € de 2015 à 2022 (fiche pratique de 2018, « 2,63 €,
valeur du point du régime complémentaire au 1er janvier 2018 » ; fiche de 2022),
2,77 € en 2023, 2,89 € de 2024 à 2026 (fiches pratiques de 2024 et de 2026) :
``moyenne``. De 2011 à 2014 — 25,07 € et 25,47 € pour un point d'avant la
conversion, 2,60 € puis 2,63 € —, elle n'est lue que chez deux tiers qui citent
la caisse (Neovia, « La CIPAV réforme son régime de retraite complémentaire » ;
Toutsurmesfinances, tableau « Source : CIPAV »), comme le facteur dix de la
conversion, que le décret n° 2012-1522 ne chiffre pas (« sans impact pour les
points attribués au titre des périodes antérieures ») : ``estimee``. Rien
n'est connu avant 2011.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.donnees.regimes import ClassesCotisation  # noqa: E402

REGIME = "cipav_complementaire"
SORTIE = Path("data/brut/cipav_points.json")

#: Points d'aujourd'hui que porte la classe de référence : quatre points de
#: la classe 1, dix fois, jusqu'en 2012 ; 36 points de la classe A ensuite.
POINTS_DE_LA_CLASSE = ((1979, 2012, 40), (2013, 2022, 36))
#: Coût d'acquisition du point depuis 2023.
COUT_D_ACQUISITION = {2023: 45.30, 2024: 47.40, 2025: 47.40, 2026: 47.40}
#: Valeur de service lue dans les fiches de la caisse.
SERVICE_DE_LA_CAISSE = {**dict.fromkeys(range(2015, 2023), 2.63),
                        2023: 2.77, 2024: 2.89, 2025: 2.89, 2026: 2.89}
#: Valeur de service lue chez des tiers, en points d'aujourd'hui.
SERVICE_DES_TIERS = {2011: 2.507, 2012: 2.547, 2013: 2.60, 2014: 2.63}


def series() -> tuple[dict[str, float], dict[str, float]]:
    """Les valeurs saisies et les valeurs estimées, par clé de la table."""
    classes = ClassesCotisation(RACINE / "data")
    epoques = yaml.safe_load(
        (RACINE / "data/reference/regimes/classes_cotisation_epoques.yaml")
        .read_text(encoding="utf-8"))[REGIME]
    lues = set(epoques["montants"])
    saisies: dict[str, float] = {}
    estimees: dict[str, float] = {}
    for debut, fin, points in POINTS_DE_LA_CLASSE:
        for annee in range(debut, fin + 1):
            if classes.annee_grille(REGIME, annee) != annee:
                raise SystemExit(f"{annee} : pas de grille de classes pour cet exercice")
            prix = round(classes.grille(REGIME, annee)[0].cotisation / points, 6)
            cible = saisies if annee in lues else estimees
            cible[f"{REGIME}|{annee}|salaire_reference"] = prix
    for annee, cout in COUT_D_ACQUISITION.items():
        saisies[f"{REGIME}|{annee}|salaire_reference"] = cout
    for annee, valeur in SERVICE_DE_LA_CAISSE.items():
        saisies[f"{REGIME}|{annee}|valeur_service"] = valeur
    for annee, valeur in SERVICE_DES_TIERS.items():
        estimees[f"{REGIME}|{annee}|valeur_service"] = valeur
    return saisies, estimees


def main() -> int:
    saisies, estimees = series()
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": "décret n° 79-262, article 2 ; fiches pratiques de la Cipav",
            "saisi_le": date.today().isoformat(),
            "saisies": saisies,
            "estimees": estimees,
        }, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8",
    )
    print(f"{SORTIE} : {len(saisies)} valeurs saisies, {len(estimees)} estimées")
    return 0


if __name__ == "__main__":
    sys.exit(main())
