#!/usr/bin/env python3
"""Le patrimoine des personnes décédées en 2018, par décile, lu dans les données
du rapport de la Cour des comptes sur les droits de succession.

    python scripts/fetch/cdc_droits_succession.py
    python scripts/fetch/cdc_droits_succession.py --fichier ~/Téléchargements/donnees.zip

La Cour publie avec « Les droits de succession » (rapport public thématique,
septembre 2024) un zip de dix-huit CSV, les données de ses graphiques et de
ses tableaux. `ccomptes.fr` ferme la connexion aux sessions du cloud : le zip
est lu dans ``data/brut/``, sinon sur la release ``documents-apportes`` qui en
est le miroir (jeu ``cdc_successions_2024_donnees`` du manifeste, son
empreinte vérifiée), sinon sur le site.

CE QUE LE DÉPÔT EN REPREND
--------------------------
Le seul graphique qui décrive ce que les successions portent : le n° 18,
« patrimoine moyen des personnes décédées par décile en 2018 », en milliers
d'euros (``G18.csv``), que la Cour reprend de la direction générale du Trésor
(document de travail n° 2021/5, microsimulation sur l'enquête Patrimoine
2014-2015 de l'INSEE). Le texte de la page 65 en écrit trois valeurs — nul
pour le premier décile, 7 000 € pour le deuxième, 1,35 M€ pour le dernier —,
que le lecteur confronte au fichier avant d'écrire.

CE QUE LE RAPPORT NE DONNE PAS
------------------------------
La distribution des successions DÉCLARÉES par tranche d'actif net, que le
manifeste lui prêtait avant qu'on le lise : l'application où la DGFiP les
enregistre est un outil de gestion, « et non de contrôle ou de production de
statistiques » (p. 78). Les tableaux 9, 10 et 14
portent le contrôle fiscal (relances, contrôles, transactions), pas les
patrimoines. Le tableau 7 donne les déclarations de 2022 — 354 443, dont
47 % payantes, pour 673 637 décès —, cité dans la note de l'action 47 sans
entrer au dépôt.

À QUOI ÇA SERT
--------------
Au recoupement de la reprise sur succession de la garantie vieillesse
(action 47) : ``donnees/patrimoine.py`` tire la couverture d'une avance du
patrimoine des MÉNAGES de retraités ; celui-ci est celui des PERSONNES
décédées. Aucun calcul ne lit le fichier (``memoire.HORS_DU_MODELE``).
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
import urllib.error
import zipfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_locale import jeux_bloques, lire_ou_telecharger, option_fichier, telecharger  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "macro" / "patrimoine_defunts.csv"
JEU = "cdc_successions_2024_donnees"
GRAPHIQUE = "G18.csv"

#: Ce que le texte du rapport écrit (p. 65) : décile -> patrimoine moyen, en euros.
TEXTE_PAGE_65 = {1: 0, 2: 7_000, 10: 1_350_000}

ENTETE = """\
# Patrimoine moyen des personnes décédées en 2018, par décile de leur patrimoine
# source_id: cdc_successions_2024_donnees (Cour des comptes, « Les droits de
#            succession », septembre 2024, graphique n° 18, d'après la
#            direction générale du Trésor, document de travail n° 2021/5)
# unite: euros courants de 2018, par PERSONNE décédée : la moyenne du décile
# decile: 1 (le dixième des défunts au patrimoine le plus faible) … 10
# fiabilite:
#   haute : valeur publiée, lue telle quelle dans le G18.csv des données que
#           la Cour publie avec son rapport (en milliers d'euros, écrite ici
#           en euros) par scripts/fetch/cdc_droits_succession.py. Le texte de
#           la page 65 en écrit trois — nul, 7 000 € et 1,35 M€ —, que le
#           lecteur confronte ; aucune certification ne recontrôle les autres.
#
# CE QUE LA SÉRIE MESURE
# ----------------------
# Les personnes décédées en 2018, classées par décile de leur patrimoine, et
# la moyenne de chaque dixième : une microsimulation de la DG Trésor sur
# l'enquête Patrimoine 2014-2015 de l'INSEE, que la Cour reproduit. Le
# document de travail n'a pas été lu ; le rapport parle du « patrimoine moyen
# transmis lors d'une succession », sans dire s'il est brut ou net. Un
# défunt sur dix ne laisse rien.
#
# À QUOI ELLE SERT
# ----------------
# Au recoupement de la reprise sur succession de la garantie vieillesse
# (action 47) : `donnees/patrimoine.py` tire la couverture d'une avance du
# patrimoine des MÉNAGES de retraités (COR, 2018), et celle-ci est celle des
# PERSONNES décédées, toutes pensions confondues. Aucun calcul ne la lit
# (`memoire.HORS_DU_MODELE`).
#
# Ne pas modifier à la main : le script réécrit le fichier en entier.
"""


def jeu_du_manifeste() -> dict:
    for jeu in jeux_bloques():
        if jeu["id"] == JEU:
            return jeu
    raise LookupError(f"le manifeste ne déclare pas le jeu {JEU}")


def extraire(archive: bytes) -> dict[int, int]:
    """Décile -> patrimoine moyen en euros, lu dans ``G18.csv``."""
    with zipfile.ZipFile(io.BytesIO(archive)) as zip_:
        texte = zip_.read(GRAPHIQUE).decode("cp1252")
    moyennes = {}
    for ligne in csv.reader(io.StringIO(texte)):
        if not ligne:
            continue
        decile, milliers = int(ligne[0]), float(ligne[1])
        moyennes[decile] = int(round(milliers * 1000))
    if sorted(moyennes) != list(range(1, 11)):
        raise ValueError(f"{GRAPHIQUE} : dix déciles attendus, lus {sorted(moyennes)}")
    suite = [moyennes[d] for d in range(1, 11)]
    if any(b < a for a, b in zip(suite, suite[1:])):
        raise ValueError(f"{GRAPHIQUE} : moyennes non croissantes {suite}")
    for decile, valeur in TEXTE_PAGE_65.items():
        if moyennes[decile] != valeur:
            raise ValueError(f"{GRAPHIQUE} : décile {decile} à {moyennes[decile]} €, "
                             f"le texte de la page 65 écrit {valeur} €")
    return moyennes


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    options = analyseur.parse_args(argv)
    jeu = jeu_du_manifeste()
    print(f"Source    {jeu['document']}")
    try:
        archive = lire_ou_telecharger(jeu["document"], telecharger, options.fichier,
                                      nom_local=jeu["fichier_local"], miroir=jeu["miroir"],
                                      sha256=jeu["sha256"])
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
        print(f"ÉCHEC   téléchargement : {erreur}", file=sys.stderr)
        return 1
    try:
        moyennes = extraire(archive)
    except (KeyError, ValueError, zipfile.BadZipFile) as erreur:
        print(f"ÉCHEC   lecture du zip : {erreur}", file=sys.stderr)
        return 1
    with SORTIE.open("w", encoding="utf-8", newline="\n") as flux:
        flux.write(ENTETE)
        flux.write(f"# recupere_le: {date.today().isoformat()}\n")
        flux.write("annee,decile,patrimoine_moyen,source_id,fiabilite\n")
        for decile in range(1, 11):
            flux.write(f"2018,{decile},{moyennes[decile]},{JEU},haute\n")
    print(f"\n10 déciles écrits dans {SORTIE.relative_to(RACINE)} : de {moyennes[1]:,} € "
          f"à {moyennes[10]:,} €, moyenne {sum(moyennes.values()) / 10:,.0f} €")
    return 0


if __name__ == "__main__":
    sys.exit(main())
