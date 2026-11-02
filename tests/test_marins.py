"""Le régime des marins, lu au droit.

Trois fiches de la carte, lues au droit le 2 novembre 2026 (action 130) dans
les rédactions du code des pensions de retraite des marins — le décret
n° 68-292 du 21 mars 1968 le crée en abrogeant la loi du 12 avril 1941, le
décret n° 79-791 du 13 septembre 1979 remplace son article R. 14, le décret
n° 85-1159 du 5 novembre 1985 son article R. 13, le décret n° 99-265 du
1er avril 1999 lui ajoute R. 31 — et dans les articles du code des transports
qui reprennent sa partie législative depuis le 1er décembre 2010 :
l'ouverture de la pension d'ancienneté à cinquante ans et le plafond de ses
annuités avant cinquante-cinq ans (`marins_ouverture_cinquante_ans`), la
bonification pour enfants (`marins_bonification_enfants`), le salaire de
référence (`marins_salaire_de_reference`).

Chaque paramètre d'une version porte le nom du champ de la période qui le
porterait. La fiche de régime `regimes/marins.yaml`, une seule période depuis
1930, en porte la valeur ; sinon, la fiche déclare l'écart, et le test qui
suit `ECARTS_DECLARES` le tient, cas par cas. Une période couvre des années
entières : une version qui commence en cours d'année se confronte aux années
qu'elle couvre en entier.
"""

from __future__ import annotations

import csv
from datetime import date

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte

LOT = ("marins_ouverture_cinquante_ans", "marins_bonification_enfants",
       "marins_salaire_de_reference")
REFERENCE = RACINE_DONNEES / "reference"
PERIODES = yaml.safe_load((REFERENCE / "regimes" / "marins.yaml")
                          .read_text(encoding="utf-8"))["periodes"]
#: La première année de la fiche de régime, et la dernière que les
#: confrontations parcourent.
DEBUT, HORIZON = 1930, 2050
#: Les versions du salaire de référence, qui lisent toutes la règle de R. 11
#: et de R. 12.
SALAIRE = ("loi_du_12_avril_1941", "code_de_1968", "contrats_simultanes")

#: Ce que le modèle fait autrement que le droit : la fiche, la version, le
#: champ que la version lit et que la période des marins porte autrement, ou
#: ne porte pas, et l'article que cite l'approximation qui le déclare.
#: Avant le 7 novembre 1985, R. 13 plafonne à vingt-cinq annuités toute
#: pension d'ancienneté liquidée avant cinquante-cinq ans, sans l'exception
#: des cinquante-deux ans et demi que le modèle sert dès 1930 ; la
#: bonification ne compte que l'enfant élevé neuf ans, condition que le
#: modèle n'oppose pas ; le salaire de référence est la catégorie des
#: trente-six derniers mois, ou de fonctions supérieures tenues cinq ans,
#: abattue au-delà de huit fois le traitement de l'indice 100, sur des
#: services décomptés au semestre, quand le modèle prend la catégorie de la
#: dernière année, rangée par le revenu, entière, et compte au trimestre.
ECARTS_DECLARES = [
    *[("marins_ouverture_cinquante_ans", version, champ, "R. 13")
      for version in ("loi_du_12_avril_1941", "code_de_1968")
      for champ in ("duree_maximum_levee_age", "duree_maximum_levee_trimestres")],
    ("marins_bonification_enfants", "neuf_ans_d_education", "annees_d_education", "R. 14"),
    ("marins_bonification_enfants", "neuf_ans_d_education", "age_de_fin_d_education", "R. 14"),
    *[("marins_salaire_de_reference", version, champ, article)
      for version in SALAIRE
      for champ, article in (("mois_de_reference", "R. 11"),
                             ("annees_de_fonctions_superieures", "R. 11"),
                             ("plafond_en_traitements_de_l_indice_100", "R. 11, 3°"),
                             ("part_au_dela_du_plafond", "R. 11, 3°"),
                             ("mois_du_decompte_des_services", "R. 12"))],
    ("marins_salaire_de_reference", "contrats_simultanes", "contrats_simultanes", "R. 31"),
]


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _bornes(version: dict) -> list:
    return version["bornes"]["liquidation.date_effet"]


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1930."""
    premiere = DEBUT if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT), HORIZON + 1 if fin is None else fin.year)


def _periode(annee: int) -> dict:
    return next(p for p in PERIODES
                if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"]))


def _valeur(valeur):
    """Une valeur comparable : un barème, liste dans le YAML, en tuple."""
    return tuple(valeur) if isinstance(valeur, list) else valeur


def _portes(version: dict, champ: str) -> set:
    """Les valeurs que la période des marins porte pour ce champ, sur les
    années que la version couvre en entier ; ``None`` si elle n'en porte pas."""
    return {_valeur(_periode(annee).get(champ)) for annee in _annees_entieres(*_bornes(version))}


def test_chaque_version_nait_du_texte_qui_la_coupe():
    """Chaque fiche du lot couvre toute date d'effet ; chaque version commence
    le jour où entre en vigueur le texte qui la fait naître (`nee_de`), qu'elle
    cite parmi ses textes."""
    for nom in LOT:
        versions = _versions(nom)
        assert _bornes(versions[0])[0] is None and _bornes(versions[-1])[1] is None, nom
        for avant, apres in zip(versions, versions[1:]):
            assert _bornes(avant)[1] == _bornes(apres)[0], (nom, apres["id"])
        for version in versions:
            if version.get("nee_de"):
                texte = next((t for t in version.get("textes") or []
                              if t.get("id") == version["nee_de"]), None)
                assert texte is not None, (nom, version["id"])
                assert texte["en_vigueur"] == _bornes(version)[0], (nom, version["id"])


def test_la_periode_des_marins_porte_ce_que_chaque_version_lit():
    """Sur chaque année que la version couvre en entier, la période des marins
    porte la valeur que la version lit, sous le même nom, ou l'écart est
    déclaré."""
    declares = {(nom, version, champ) for nom, version, champ, _ in ECARTS_DECLARES}
    for nom in LOT:
        for version in _versions(nom):
            for champ, lu in (version["contenu"].get("parametres") or {}).items():
                if (nom, version["id"], champ) not in declares:
                    assert _portes(version, champ) == {_valeur(lu)}, (nom, version["id"], champ)


@pytest.mark.parametrize("nom, version, champ, article", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(nom, version, champ, article):
    """La version lit une valeur — rien, quand le droit n'a pas encore ce que
    le modèle sert — que la période des marins ne porte sur aucune des années
    qu'elle couvre ; une approximation de la fiche touche cette version et
    cite l'article qui la fonde."""
    fiche = carte.fiches()[nom]
    lue = next(v for v in fiche["versions"] if v["id"] == version)
    valeur = _valeur(lue["contenu"]["parametres"][champ])
    assert valeur not in _portes(lue, champ), (nom, version, champ)
    assert any(version in (a.get("version") or []) and article in str(a.get("textes") or "")
               for a in fiche.get("approximations") or []), (nom, version, article)


def _lignes(relatif: str) -> list[dict]:
    with (REFERENCE / relatif).open(encoding="utf-8", newline="") as flux:
        return list(csv.DictReader(ligne for ligne in flux if not ligne.startswith("#")))


def test_l_abattement_de_r_11_toucherait_les_six_plus_hautes_categories_en_2026():
    """R. 11, 3° : « Lorsque le salaire ainsi défini excède huit fois le montant
    du traitement brut correspondant à l'indice 100 dans la fonction publique,
    la portion dépassant cette limite n'est comptée que pour moitié. » Lu au
    traitement annuel de l'indice 100 majoré, 5 907,34 € depuis le 1er juillet
    2023 (article 3 du décret n° 85-1148 ; cent fois la valeur du point,
    `legislation/point_indice_fonction_publique.csv`), le plafond vaut
    47 258,72 € en 2026 ; les forfaits des catégories 15 à 20 de l'arrêté de
    2026 (`regimes/salaires_forfaitaires.csv`) le dépassent, celui de la
    vingtième, 76 867,05 €, de 29 608,33 €, dont la moitié ne compte pas :
    19,3 % de son forfait, que le modèle liquide entier."""
    lus = _versions("marins_salaire_de_reference")[-1]["contenu"]["parametres"]
    point = next(float(l["valeur"]) for l in _lignes("legislation/point_indice_fonction_publique.csv")
                 if l["annee"] == "2026")
    grille = {int(l["categorie"]): float(l["montant_annuel"])
              for l in _lignes("regimes/salaires_forfaitaires.csv")
              if l["regime"] == "marins" and l["annee"] == "2026"}
    plafond = lus["plafond_en_traitements_de_l_indice_100"] * 100 * point
    assert round(plafond, 2) == 47258.72
    assert sorted(c for c, montant in grille.items() if montant > plafond) == list(range(15, 21))
    retenu = plafond + (grille[20] - plafond) * lus["part_au_dela_du_plafond"]
    assert round(1 - retenu / grille[20], 3) == 0.193
