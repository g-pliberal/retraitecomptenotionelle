#!/usr/bin/env python3
"""La durée de retraite et le rendement interne publiés par le COR.

    python scripts/fetch/cor_cycle_de_vie.py
    python scripts/fetch/cor_cycle_de_vie.py --fichier Donnees_RA2026_P3_2.xlsx \
        --fichier-2025 Donnees_RA2025_P3.xlsx

POURQUOI CE TÉMOIN. Le dépôt calcule, depuis l'action 138 (étape 9), les
indicateurs de cycle de vie de ses carrières : la durée de retraite, le
rendement interne, le taux de récupération, le patrimoine retraite
(``src/retraite_notionnelle/cycle_de_vie.py``). Le Conseil d'orientation des
retraites en publie deux, chaque année, calculés par d'autres et avec leurs
conventions écrites : la durée de retraite par génération, avec l'espérance de
vie à 60 ans de chaque génération par sexe, et le rendement interne net du
cas type n° 2, le non-cadre du privé à carrière complète, génération par
génération, puis selon le revenu, le sexe et les enfants pour la génération
2000. ``tests/test_cycle_de_vie_references.py`` s'y confronte.

LA SOURCE. Le classeur de données de la partie 3 du rapport annuel de juin
2026, celui de la figure 3.14 que ``cor_pouvoir_achat_retraite.py`` lit
déjà : feuilles « Fig 3.6 » (durée de retraite et, en « données
complémentaires », espérance de vie à 60 ans), « Fig 3.7 » (rendement interne
du cas type n° 2) et « Fig. 3.A » (rendement interne de la génération 2000).
Les conventions sont celles du rapport (p. 138-141) et de son annexe
méthodologique en ligne (§ 2.3) : le décès à 60 ans plus l'espérance de vie
à 60 ans de la génération, les cotisations seules, les droits propres hors
droits familiaux, l'actualisation selon le salaire moyen par tête.

ET LA SÉRIE DE 2025. Le rendement du cas type n° 2 que le rapport de juin 2025
publiait (classeur de la partie 3, feuille « Fig 3.7 »), BRUT : le rapport de
2026 dit que le rendement « était évalué à partir des rémunérations brutes »
(note 140). Le dépôt la retrouve, quand celle de 2026 n'en est pas la
version nette (action 138, étape 9, note du 10 octobre 2026).

Le témoin est versionné : les tests le relisent sans réseau.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://www.cor-retraites.fr/sites/default/files/2026-06/"
       "Donn%C3%A9es_RA2026_P3_2.xlsx")
URL_2025 = ("https://www.cor-retraites.fr/sites/default/files/2025-10/"
            "Donn%C3%A9es_RA2025_P3.xlsx")
SORTIE = RACINE / "tests" / "temoins" / "cor_cycle_de_vie.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Les profils de la figure 3.A, par l'en-tête de leur colonne : le profil de
#: revenu seul, ou le nombre d'enfants suivi du sexe.
PROFILS = {
    "Cadre": "cadre",
    "non-cadre": "non_cadre",
    "SMIC (avec exonérations)": "smic_avec_exonerations",
    "SMIC (hors exonérations)": "smic_hors_exonerations",
    ("Sans enfant", "Homme"): "homme_sans_enfant",
    ("Sans enfant", "Femme"): "femme_sans_enfant",
    ("2 enfants", "Homme"): "homme_deux_enfants",
    ("2 enfants", "Femme"): "femme_deux_enfants",
    ("3 enfants", "Homme"): "homme_trois_enfants",
    ("3 enfants", "Femme"): "femme_trois_enfants",
}
#: Les lignes de la figure 3.A, et la part du rendement qu'elles portent.
PARTS = {"TRI net": "total", "dont CNAV": "cnav", "dont AA": "agirc_arrco"}


def _lignes(grille: dict) -> list[list]:
    """La grille en lignes, chacune la liste de ses cellules par colonne."""
    if not grille:
        return []
    hauteur = max(ligne for ligne, _ in grille) + 1
    largeur = max(colonne for _, colonne in grille) + 1
    return [[grille.get((ligne, colonne)) for colonne in range(largeur)]
            for ligne in range(hauteur)]


def _serie(entete: list, valeurs: list) -> dict[str, float]:
    """Les valeurs d'une ligne, par la génération que l'en-tête met au-dessus."""
    return {str(int(generation)): valeur
            for generation, valeur in zip(entete, valeurs)
            if isinstance(generation, float) and isinstance(valeur, float)}


def lire_duree(grille: dict) -> dict:
    """La figure 3.6 : la durée de retraite moyenne par génération, en années
    puis en part de la vie, et l'espérance de vie à 60 ans par sexe."""
    lignes = _lignes(grille)
    durees: list[dict[str, float]] = []
    esperances: dict[str, dict[str, float]] = {}
    entete: list = []
    for ligne in lignes:
        titre = ligne[1] if len(ligne) > 1 else None
        if not isinstance(titre, str):
            continue
        titre = titre.strip()
        if titre in ("Moyenne par génération", "Espérance de vie par génération"):
            entete = ligne
        elif titre == "Scénario central de mortalité":
            durees.append(_serie(entete, ligne))
        elif titre.startswith("Scénario central de mortalité,"):
            qui = titre.split(",", 1)[1].strip()
            esperances[qui] = _serie(entete, ligne)
    if len(durees) != 2:
        raise ValueError(f"figure 3.6 : {len(durees)} séries de durée, deux attendues")
    return {"annees": durees[0], "part_de_vie": durees[1], "esperance_60": esperances}


def lire_rendement(grille: dict) -> dict[str, float]:
    """La figure 3.7 : le rendement interne net du cas type n° 2."""
    lignes = _lignes(grille)
    entete = next(l for l in lignes if isinstance(l[1], str) and "cas n°2" in l[1])
    reference = next(l for l in lignes if isinstance(l[1], str) and l[1].strip() == "Sc. Réf")
    return _serie(entete, reference)


def lire_profils(grille: dict) -> dict[str, dict[str, float]]:
    """La figure 3.A : le rendement interne net de la génération 2000, par
    profil, et sa part au régime général et à l'Agirc-Arrco."""
    lignes = _lignes(grille)
    profils_ligne = next(l for l in lignes if "Cadre" in l)
    sexes_ligne = next(l for l in lignes if "Homme" in l)
    colonnes: dict[int, str] = {}
    enfants = None
    for colonne, tete in enumerate(profils_ligne):
        if isinstance(tete, str):
            if tete in PROFILS:
                colonnes[colonne] = PROFILS[tete]
                continue
            enfants = tete
        sexe = sexes_ligne[colonne] if colonne < len(sexes_ligne) else None
        if enfants and isinstance(sexe, str) and (enfants, sexe) in PROFILS:
            colonnes[colonne] = PROFILS[(enfants, sexe)]
    profils: dict[str, dict[str, float]] = {nom: {} for nom in colonnes.values()}
    for ligne in lignes:
        tete = ligne[1] if len(ligne) > 1 else None
        if isinstance(tete, str) and tete.strip() in PARTS:
            for colonne, nom in colonnes.items():
                if isinstance(ligne[colonne], float):
                    profils[nom][PARTS[tete.strip()]] = ligne[colonne]
    return profils


def controler(temoin: dict) -> list[str]:
    """La forme que les tests supposent."""
    erreurs = []
    attendues = [str(annee) for annee in range(1940, 2001)]
    for nom, serie in (("durée", temoin["duree_retraite"]["annees"]),
                       ("part de vie", temoin["duree_retraite"]["part_de_vie"]),
                       ("rendement", temoin["rendement_cas_type_2"]),
                       ("rendement brut de 2025", temoin["rendement_cas_type_2_brut_2025"])):
        if sorted(serie) != attendues:
            erreurs.append(f"{nom} : générations {sorted(serie)[:3]}…")
    for qui in ("ensemble", "femmes", "hommes"):
        if sorted(temoin["duree_retraite"]["esperance_60"].get(qui, {})) != attendues:
            erreurs.append(f"espérance de vie à 60 ans, {qui} : absente ou incomplète")
    profils = temoin["rendement_generation_2000"]
    if sorted(profils) != sorted(set(PROFILS.values())):
        erreurs.append(f"figure 3.A : profils {sorted(profils)}")
    elif any(sorted(parts) != sorted(PARTS.values()) for parts in profils.values()):
        erreurs.append("figure 3.A : un profil sans ses trois lignes")
    elif abs(profils["non_cadre"]["total"] - temoin["rendement_cas_type_2"]["2000"]) > 1e-12:
        erreurs.append("figure 3.A : le non-cadre n'est pas le cas type n° 2 de 2000")
    return erreurs


def _classeur(fichier: Path | None, url: str) -> bytes:
    """Le classeur déjà téléchargé, ou celui du réseau."""
    if fichier:
        return fichier.read_bytes()
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        return reponse.read()


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path,
                           help="classeur de 2026 déjà téléchargé, lu au lieu du réseau")
    analyseur.add_argument("--fichier-2025", type=Path,
                           help="classeur de 2025 déjà téléchargé, lu au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    grilles = feuilles(_classeur(arguments.fichier, URL))
    grilles_2025 = feuilles(_classeur(arguments.fichier_2025, URL_2025))
    temoin = {
        "source": {
            "editeur": "Conseil d'orientation des retraites",
            "reference": "Rapport annuel de juin 2026, figures 3.6, 3.7 et 3.A ; "
                         "conventions : p. 138-141 et annexe méthodologique en "
                         "ligne, § 2.3",
            "url": URL,
            "lu_le": "2026-10-07",
        },
        "conventions": {
            "duree_retraite": ("moyenne par génération : 60 + espérance de vie à "
                               "60 ans de la génération, moins son âge moyen de "
                               "départ ; scénario central de mortalité de l'Insee "
                               "(projections 2026-2070, prolongées au-delà)"),
            "esperance_60": "par génération, en années ; « ensemble » est la "
                            "moyenne des deux sexes",
            "rendement": ("taux de rendement interne net, flux actualisés selon le "
                          "salaire moyen par tête, scénario de référence ; cotisations "
                          "seules, sans les allègements ni les impôts affectés ; "
                          "droits propres hors droits familiaux ; décès à 60 ans "
                          "plus l'espérance de vie à 60 ans de la génération"),
            "cas_type_2": ("non-cadre du privé à carrière continue, au salaire moyen "
                           "du tiers inférieur de la distribution à chaque âge"),
            "rendement_brut_2025": ("celui du rapport de juin 2025 : les mêmes "
                                    "conventions, la pension brute, et la mortalité "
                                    "des projections de l'Insee de 2021"),
            "profils_2000": ("sans genre et sans enfant pour les profils de revenu : "
                             "cadre et non-cadre au taux plein de CSG, le SMIC au "
                             "taux réduit ; le cadre a l'espérance de vie la plus "
                             "élevée, le SMIC celle des ouvriers"),
        },
        "duree_retraite": lire_duree(grilles["Fig 3.6"]),
        "rendement_cas_type_2": lire_rendement(grilles["Fig 3.7"]),
        "rendement_generation_2000": lire_profils(grilles["Fig. 3.A"]),
        "source_2025": {
            "editeur": "Conseil d'orientation des retraites",
            "reference": "Rapport annuel de juin 2025, figure 3.7 ; le rapport de juin "
                         "2026, note 140 : le rendement « était évalué à partir des "
                         "rémunérations brutes »",
            "url": URL_2025,
            "lu_le": "2026-10-10",
        },
        "rendement_cas_type_2_brut_2025": lire_rendement(grilles_2025["Fig 3.7"]),
    }
    erreurs = controler(temoin)
    if erreurs:
        print("Figures refusées :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"Témoin écrit dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
