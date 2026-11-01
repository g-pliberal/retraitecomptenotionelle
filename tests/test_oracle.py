"""Confrontation du scénario 1 à une SECONDE IMPLÉMENTATION, écrite par d'autres.

Le scénario « système actuel » est l'étalon du modèle : tous les écarts affichés
se mesurent par rapport à lui. Le vérifier en le relisant ne prouve rien — une
réimplémentation écrite par la même main hérite des mêmes hypothèses. Les
simulateurs anonymes des caisses répondent, eux, une saisie à la fois et dans un
budget (`docs/architecture.md`, § 3.5) : leurs réponses sont des exemples
officiels, rejoués plus bas. Mais « Mon estimation retraite », le seul qui
chiffre une pension entière, exige FranceConnect et le relevé de carrière réel.

Reste OpenFisca-France-Pension, le module « retraites » de l'écosystème
OpenFisca. Ce n'est pas une source officielle, c'est un autre modèle — mais il
est écrit par d'autres, à partir des mêmes textes, et c'est exactement ce qui
manquait. La première confrontation a produit deux désaccords, un de chaque
côté : la durée de proratisation, que nous confondions avec la durée requise
(corrigé), et sa table de durée requise, qui ignore la réforme du 14 avril 2023.

**Ce test n'installe pas OpenFisca.** Il rejoue les témoins versionnés que
`scripts/fetch/openfisca_regime_general.py`, `openfisca_fonction_publique.py`,
`openfisca_arrco.py`, `openfisca_agirc.py` et `openfisca_ircantec.py` ont figés,
ce qui le rend exécutable sur un dépôt fraîchement cloné, sans les quatre cents
mégaoctets de numpy, pandas et numba.

**Le moteur confronté est le portage**, celui qui fait foi (note de décision
0005) : chaque mesure des cinq familles et des régimes alignés le fait
calculer, une fonction du droit après l'autre (``pont.droit``), sur la
carrière que le test bâtit. Tant que le moteur Python garde ses jumeaux
(action 161), il refait chaque appel au bit près
(``outils_pont.droit_et_refait``), et chaque famille se mesure aussi sans lui.
Les exemples officiels, plus bas, y passent à leur tour : leurs carrières, leur
liquidation et leurs grandeurs de base ; le relevé, l'invalidité, la
réversion, le cumul et le reste appellent encore le moteur Python.

Cinq familles de régimes sont confrontées, et c'est tout ce qu'OpenFisca
expose : le régime général, la pension civile (État et CNRACL), l'Arrco d'avant
2019, l'Agirc des cadres et l'Ircantec des agents non titulaires. S'y ajoutent
les régimes ALIGNÉS — MSA des salariés agricoles, artisans, commerçants —, pour
lesquels il n'a aucun module et n'en a pas besoin : la loi les calcule comme le
régime général, et c'est à l'oracle du régime général qu'ils se confrontent.

Ce que chaque confrontation a trouvé, dans l'ordre où elles ont été écrites.

* **Régime général** — deux désaccords, un de chaque côté : la durée de
  proratisation, que nous confondions avec la durée requise (corrigé), et sa
  table de durée requise, qui ignore la réforme du 14 avril 2023.
* **Pension civile** — deux erreurs chez nous, le barème de décote lu à l'année
  de liquidation au lieu de l'année d'ouverture du droit et le traitement de
  l'année d'avant ramené au départ par les prix au lieu du point d'indice ; une
  chez lui, un 0,65 % transcrit pour 2010 là où la loi écrit 0,625 %.
* **Arrco** — rien à corriger, et c'est le résultat.
* **Agirc** — trois écarts, tous chez lui : son barème salarié ne suit pas le
  taux d'appel de 1989 ni le contractuel de 1994, sa tranche C est cotisée par
  le salarié dès 1948 faute d'un taux nul écrit là où le barème employeur en
  porte un, et son prix d'achat se lit au 1er janvier, soit un millésime de
  retard à partir de 2004.
* **Ircantec** — deux corrections chez nous, toutes deux lues dans les textes :
  l'assiette de la tranche B, que l'article 7 du décret n° 70-1277 limite à
  4,75 plafonds jusqu'en 2008, et le coefficient d'anticipation, que l'article
  16 de l'arrêté du 30 décembre 1970 écrit en escalier là où la fiche portait
  une pente moyenne. Chez lui, une assiette portée à huit plafonds seize ans
  trop tôt et une surcote dix fois trop forte.
* **Régimes alignés** — la MSA rend exactement la pension du régime général ;
  l'artisan et le commerçant, non, parce que le modèle coupe leur carrière à
  chaque changement de caisse et calcule deux salaires de référence là où la
  loi n'en veut qu'un.

Au-delà de ces carrières simples, la confrontation se poursuit une famille de
profils à la fois, chacune avec sa convention de traduction écrite :
``tests/test_oracle_familles.py`` (action 153).
"""

from __future__ import annotations

import functools
import json
import re
from pathlib import Path

import pytest

from outils_pont import droit_et_refait
from retraite_notionnelle import pont
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.donnees.chargement import Fiabilite, SerieAnnuelle
from retraite_notionnelle.droit import departs, invalidite, liquider, ouvrir
from retraite_notionnelle.droit.reversion import reversion
from retraite_notionnelle.echeancier import Echeancier
from retraite_notionnelle.scenarios.actuel import (
    AgesAnnulationDecote, MinimumGaranti, ScenarioActuel, ValeursPoint)

TEMOINS = Path(__file__).resolve().parent / "temoins"
TEMOIN = TEMOINS / "openfisca_regime_general.json"
TEMOIN_FONCTION_PUBLIQUE = TEMOINS / "openfisca_fonction_publique.json"
TEMOIN_ARRCO = TEMOINS / "openfisca_arrco.json"
TEMOIN_AGIRC = TEMOINS / "openfisca_agirc.json"
TEMOIN_IRCANTEC = TEMOINS / "openfisca_ircantec.json"

#: Tolérance sur la durée, la décote, le taux et la proratisation : ce sont des
#: comptages et des tables, ils doivent tomber juste à l'unité près.
TOLERANCE_EXACTE = 1e-4

#: Tolérance sur le salaire annuel moyen et sur la pension, qui en découle.
#:
#: Elle valait 8 % : le modèle approchait les coefficients de revalorisation des
#: salaires portés au compte par « les salaires jusqu'en 1986, les prix depuis »,
#: une approximation qui sur-revalorise les salaires anciens de 12 à 14 % sur
#: quarante ans.
#:
#: Le modèle lit désormais les coefficients dans la circulaire annuelle de la
#: Cnav, et **c'est OpenFisca qui s'en écarte** : il compose sa table d'une
#: série annuelle (``reval_s``), qui s'écarte des colonnes publiées de −9 à
#: +2 % selon l'année dès avant 2022, et de 3 à 5,5 % de plus au-delà, faute de
#: la revalorisation exceptionnelle de 4 % du 1er juillet 2022. La
#: confrontation vaut toujours, mais elle ne peut plus être une égalité sur ce
#: poste : le désaccord résiduel, de 0,12 % à 2,46 %, est celui d'OpenFisca avec
#: la source ; ``tests/test_oracle_salaire_annuel_moyen.py`` montre que, sous
#: les mêmes coefficients, les deux règles rendent le même salaire au centime. `tests/test_simulateur.py` vérifie, lui, que le modèle reproduit
#: la colonne que la caisse a publiée.
TOLERANCE_SALAIRE = 0.03


@pytest.fixture(scope="module")
def oracle() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _carriere_du_regime_general(profil: dict) -> Carriere:
    """La carrière exacte d'un profil du témoin : salarié du privé, quatre
    trimestres chaque année, du début au départ."""
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"],
            affiliation="salarie_prive_non_cadre", trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    return Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )


def _profils(temoin: dict) -> dict[str, dict]:
    """Chaque profil d'un témoin d'OpenFisca, sous son code."""
    return {code: entree["profil"] for code, entree in temoin["profils"].items()}


def _nos_calculs(profils: dict[str, dict], droit=droit_et_refait) -> dict[str, dict[str, float]]:
    """Le régime général du scénario 1, sur la carrière exacte de chaque
    profil, sous son code.

    Le portage le calcule, le moteur qui fait foi (note de décision 0005), une
    fonction du droit après l'autre (:func:`pont.droit`), en deux demandes : la
    seconde lit dans la première la durée requise, la durée validée et l'âge
    d'annulation de la décote. Par défaut, ``droit_et_refait`` y fait refaire
    chaque appel au jumeau Python, au bit près, tant qu'il reste (action 161).
    Les trimestres de décote se relisent sous le type que le pont déclare, un
    flottant, que le jumeau rend entier (``pont.relu_du_droit``, décision du
    propriétaire du 31 octobre 2026).
    """
    carrieres = {code: _carriere_du_regime_general(profil) for code, profil in profils.items()}
    periodes = {code: pont.Periode("regime_general", profil["liquidation"])
                for code, profil in profils.items()}
    premiers = {}
    for code, profil in profils.items():
        carriere, periode, depart = carrieres[code], periodes[code], profil["liquidation"]
        premiers |= {
            f"{code}|resultat": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
            f"{code}|requis": ("ouvrir.duree_requise", pont.MOTEUR, periode, carriere),
            f"{code}|decote": ("liquider.decote_opposable", pont.MOTEUR, periode, carriere,
                               depart),
            f"{code}|salaire": ("liquider.salaire_de_reference", pont.MOTEUR,
                                "regime_general", carriere, periode, depart, True,
                                profil["naissance"], True),
        }
    lus, refus = droit(premiers)
    assert refus == {}, refus
    seconds = {}
    for code, profil in profils.items():
        requis, _ = lus[f"{code}|requis"]
        _, age_annulation, _ = lus[f"{code}|decote"]
        seconds |= {
            f"{code}|proratisation": ("liquider.duree_proratisation", pont.MOTEUR,
                                      periodes[code], carrieres[code], requis),
            f"{code}|manquants": ("liquider.trimestres_de_decote", pont.MOTEUR, periodes[code],
                                  carrieres[code], lus[f"{code}|resultat"]["trimestres_valides"],
                                  requis, profil["liquidation"] - profil["naissance"],
                                  age_annulation),
        }
    suivants, refus = droit(seconds)
    assert refus == {}, refus
    calculs = {}
    for code in profils:
        resultat = lus[f"{code}|resultat"]
        trimestres = resultat["trimestres_valides"]
        proratisation, _ = suivants[f"{code}|proratisation"]
        base = next(p for p in resultat["pensions_par_regime"] if p["regime"] == "regime_general")
        calculs[code] = {
            "duree_assurance": float(trimestres),
            "salaire_de_reference": lus[f"{code}|salaire"],
            "coefficient_de_proratisation": min(trimestres, proratisation) / proratisation,
            "decote_trimestres": suivants[f"{code}|manquants"],
            "taux_de_liquidation": resultat["taux_liquidation"],
            "pension_brute": base["montant"],
        }
    return calculs


@pytest.fixture(scope="module")
def nos_calculs(oracle) -> dict[str, dict[str, float]]:
    """Le régime général du scénario 1 sur chaque profil du témoin, sous son code."""
    return _nos_calculs(_profils(oracle))


def test_le_temoin_couvre_le_perimetre_annonce(oracle):
    """Le témoin doit dire d'où il vient, et rester dans ce qu'OpenFisca sait faire.

    Ses barèmes s'arrêtent en 2024 — valeur du point Agirc-Arrco en novembre
    2024, revalorisations CNAV en 2023 — et son Arrco est cassé dans la version
    publiée. Un profil qui déborderait ces bornes produirait une comparaison
    sans valeur, ou pas de comparaison du tout.
    """
    assert oracle["source"] == "OpenFisca-France-Pension"
    assert oracle["version"]
    assert len(oracle["profils"]) >= 8
    for code, entree in oracle["profils"].items():
        assert entree["profil"]["liquidation"] < 2025, code
        # Le garde-fou du récupérateur : un oracle silencieusement nul
        # validerait n'importe quoi.
        assert entree["openfisca"]["duree_assurance"] > 0, code
        assert entree["openfisca"]["pension_brute"] > 0, code


def test_la_duree_dassurance_concorde(oracle, nos_calculs):
    """Trimestres validés : les deux modèles doivent compter pareil."""
    for code, entree in oracle["profils"].items():
        nous = nos_calculs[code]
        assert nous["duree_assurance"] == entree["openfisca"]["duree_assurance"], code


def test_la_decote_concorde_trimestre_par_trimestre(oracle, nos_calculs):
    """Le décompte des trimestres de décote, et le taux qui en découle.

    C'est le contrôle le plus exigeant du lot : il met en jeu la durée requise
    par génération, l'âge d'annulation de la décote par génération, la règle du
    minimum entre les deux décomptes, le plafond de vingt trimestres et
    l'arrondi à l'entier supérieur. Cinq tables et trois règles doivent tomber
    juste ensemble.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = nos_calculs[code], entree["openfisca"]
        assert nous["decote_trimestres"] == eux["decote_trimestres"], code
        assert nous["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE
        ), code


def test_la_proratisation_concorde(oracle, nos_calculs):
    """Le coefficient de proratisation, et son dénominateur.

    C'est ce contrôle qui a révélé que le modèle confondait la durée requise
    pour le taux plein et la durée maximale prise en compte par la
    proratisation, que l'article R. 351-6 fixe plus bas pour les générations
    d'avant 1949. Un assuré né en 1945 avec 156 trimestres y perdait 2,5 % de
    pension de base que le droit ne lui retire pas.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = nos_calculs[code], entree["openfisca"]
        assert nous["coefficient_de_proratisation"] == pytest.approx(
            eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE
        ), code


def test_le_salaire_de_reference_reste_proche(oracle, nos_calculs):
    """Le salaire annuel moyen : le seul poste où les deux modèles diffèrent.

    Il divergeait de 0,30 % à 7,55 % quand le modèle APPROCHAIT les coefficients
    de revalorisation. Il les lit maintenant dans la circulaire de la Cnav, et
    ce qui reste — de 0,12 % à 2,46 % sur ces départs de 2007 à 2018 — n'est
    plus notre écart mais celui d'OpenFisca avec la source : il compose ses
    coefficients d'une série annuelle, qui s'écarte des colonnes de la caisse.

    Le test garde donc une borne large, et ce n'est pas un relâchement : le
    contrôle serré de cette grandeur est ailleurs, dans
    `test_les_coefficients_de_revalorisation_reproduisent_la_circulaire`, qui
    oppose au modèle la colonne que la caisse a publiée, et dans
    `tests/test_oracle_salaire_annuel_moyen.py`, qui rejoue la règle
    d'OpenFisca sous les coefficients du dépôt.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = nos_calculs[code], entree["openfisca"]
        assert nous["salaire_de_reference"] == pytest.approx(
            eux["salaire_de_reference"], rel=TOLERANCE_SALAIRE
        ), code
        # Et toujours en dessous : l'écart a un sens, il n'est pas du bruit.
        assert nous["salaire_de_reference"] <= eux["salaire_de_reference"], code


def test_la_pension_de_base_concorde(oracle, nos_calculs):
    """Le bout de la chaîne : deux implémentations, une pension.

    C'est le contrôle qui donne son prix à la confrontation. Salaire de
    référence, taux, coefficient de proratisation : chacun a été vérifié
    séparément, et leur produit doit tomber juste — un écart qui n'apparaîtrait
    qu'ici signalerait une règle appliquée dans le mauvais ordre.
    """
    for code, entree in oracle["profils"].items():
        nous, eux = nos_calculs[code], entree["openfisca"]
        assert nous["pension_brute"] == pytest.approx(
            eux["pension_brute"], rel=TOLERANCE_SALAIRE
        ), code


def _sans_les_jumeaux(monkeypatch, *jumeaux) -> None:
    """Les jumeaux Python nommés, ``(objet, nom)``, qu'on empêche de
    calculer : une mesure qui y entrerait s'arrête."""
    def interdit(*_, **__):
        raise AssertionError("un jumeau Python calcule ce que le portage doit rendre")

    for objet, nom in jumeaux:
        monkeypatch.setattr(objet, nom, interdit)


def test_le_regime_general_se_mesure_au_portage_sans_les_jumeaux_python(
        oracle, nos_calculs, monkeypatch):
    """Le moteur qui fait foi est le JavaScript (note de décision 0005) :
    chaque profil du témoin se mesure au portage, une fonction du droit après
    l'autre (``pont.droit``), et les jumeaux Python, qu'on empêche ici de
    calculer, n'y entrent pas."""
    _sans_les_jumeaux(monkeypatch, (ScenarioActuel, "calculer"), (ouvrir, "duree_requise"),
                      (liquider, "duree_proratisation"), (liquider, "decote_opposable"),
                      (liquider, "salaire_de_reference"), (liquider, "trimestres_de_decote"))
    nos = _nos_calculs(_profils(oracle), pont.droit)
    assert set(nos) == set(oracle["profils"]) and nos == nos_calculs


# -- la pension civile : État et CNRACL ---------------------------------------

#: Ce que le témoin appelle chaque régime, et le statut d'affiliation qui y
#: conduit dans le modèle.
AFFILIATIONS_PUBLIQUES = {
    "fonction_publique_etat": "fonctionnaire_etat",
    "cnracl": "fonctionnaire_territorial_hospitalier",
}

#: Coefficient de décote que la loi du 21 août 2003 fixe pour un droit ouvert
#: en 2010 — le cinquième huitième de point —, et celui qu'OpenFisca a
#: transcrit. Le profil est gardé exprès : la confrontation vaut en
#: connaissance de cause, et le test dit de quel côté est l'écart.
COEFFICIENT_2010_LOI = 0.00625
COEFFICIENT_2010_OPENFISCA = 0.0065
TAUX_PLEIN_PENSION_CIVILE = 0.75

#: Marge laissée au minimum garanti : OpenFisca le calcule au point d'indice de
#: l'année de liquidation, quand l'article L. 17 fige la référence au 1er
#: janvier 2004 et la revalorise comme les pensions. L'écart est le sien, et
#: il va toujours dans le même sens — le point a fait moins que les prix
#: depuis 2004, gel de 2010-2016 compris : de 4,7 % en 2010 à 8,5 % en 2012.
TOLERANCE_MINIMUM_GARANTI = 0.10


@pytest.fixture(scope="module")
def oracle_fonction_publique() -> dict:
    return json.loads(TEMOIN_FONCTION_PUBLIQUE.read_text(encoding="utf-8"))


def _annee_ouverture_du_droit(profil: dict) -> int:
    """Année où un sédentaire de ce profil atteint l'âge d'ouverture."""
    return profil["naissance"] + (60 if profil["naissance"] < 1951 else 62)


def _carriere_de_la_fonction_publique(profil: dict) -> Carriere:
    """La carrière exacte d'un profil du témoin : fonctionnaire de son régime,
    quatre trimestres chaque année, du début au départ.

    OpenFisca date la naissance et le départ au 1er janvier : le témoin naît
    un 1er, et part le jour même où il a l'âge, comme lui.
    """
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["traitement"],
            affiliation=AFFILIATIONS_PUBLIQUES[profil["regime"]], trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    return Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"], jour_naissance=1,
    )


def _nos_calculs_fonction_publique(profils: dict[str, dict], droit=droit_et_refait,
                                   ) -> dict[str, dict[str, float]]:
    """La pension civile du scénario 1, sur la carrière exacte de chaque
    profil, sous son code : le portage la calcule, une fonction du droit après
    l'autre, en deux demandes comme le régime général (:func:`_nos_calculs`),
    la seconde lisant aussi le minimum garanti de la durée validée. Par
    défaut, le jumeau Python refait chaque appel au bit près
    (``droit_et_refait``)."""
    carrieres = {code: _carriere_de_la_fonction_publique(profil)
                 for code, profil in profils.items()}
    periodes = {code: pont.Periode(profil["regime"], profil["liquidation"])
                for code, profil in profils.items()}
    premiers = {}
    for code, profil in profils.items():
        carriere, periode, depart = carrieres[code], periodes[code], profil["liquidation"]
        premiers |= {
            f"{code}|resultat": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
            f"{code}|requis": ("ouvrir.duree_requise", pont.MOTEUR, periode, carriere),
            f"{code}|decote": ("liquider.decote_opposable", pont.MOTEUR, periode, carriere,
                               depart),
            f"{code}|traitement": ("liquider.salaire_de_reference", pont.MOTEUR,
                                   profil["regime"], carriere, periode, depart, False,
                                   profil["naissance"], True),
        }
    lus, refus = droit(premiers)
    assert refus == {}, refus
    seconds = {}
    for code, profil in profils.items():
        requis, _ = lus[f"{code}|requis"]
        _, age_annulation, _ = lus[f"{code}|decote"]
        trimestres = lus[f"{code}|resultat"]["trimestres_valides"]
        seconds |= {
            f"{code}|proratisation": ("liquider.duree_proratisation", pont.MOTEUR,
                                      periodes[code], carrieres[code], requis),
            f"{code}|manquants": ("liquider.trimestres_de_decote", pont.MOTEUR, periodes[code],
                                  carrieres[code], trimestres, requis,
                                  profil["liquidation"] - profil["naissance"], age_annulation),
            f"{code}|plancher": ("scenario_actuel.minimum_garanti.montant", pont.MOTEUR,
                                 profil["liquidation"], trimestres),
        }
    suivants, refus = droit(seconds)
    assert refus == {}, refus
    calculs = {}
    for code, profil in profils.items():
        resultat = lus[f"{code}|resultat"]
        trimestres = resultat["trimestres_valides"]
        proratisation, _ = suivants[f"{code}|proratisation"]
        pension = next(p for p in resultat["pensions_par_regime"]
                       if p["regime"] == profil["regime"])
        # Le minimum garanti se SUBSTITUE à la pension quand il lui est
        # supérieur, et le complément est dit : la pension d'avant le plancher
        # se retrouve en le retirant.
        complement = sum(a["montant"] for a in resultat["avantages_appliques"]
                         if a["code"] == "minimum_garanti")
        plancher = suivants[f"{code}|plancher"]
        calculs[code] = {
            "duree_assurance": float(trimestres),
            "coefficient_de_proratisation": min(trimestres, proratisation) / proratisation,
            "decote_trimestres": suivants[f"{code}|manquants"],
            "taux_de_liquidation": resultat["taux_liquidation"],
            "traitement_de_reference": lus[f"{code}|traitement"],
            "pension_avant_minimum": pension["montant"] - complement,
            "minimum_garanti": plancher[0] if plancher else 0.0,
            "pension_brute": pension["montant"],
        }
    return calculs


@pytest.fixture(scope="module")
def nos_calculs_fonction_publique(oracle_fonction_publique) -> dict[str, dict[str, float]]:
    """La pension civile du scénario 1 sur chaque profil du témoin, sous son code."""
    return _nos_calculs_fonction_publique(_profils(oracle_fonction_publique))


def test_le_temoin_de_la_fonction_publique_couvre_le_perimetre_annonce(
        oracle_fonction_publique):
    """Deux régimes, liquidations de 2009 à 2020, aucun relevé nul."""
    assert oracle_fonction_publique["source"] == "OpenFisca-France-Pension"
    assert oracle_fonction_publique["version"]
    profils = oracle_fonction_publique["profils"]
    assert len(profils) >= 8
    assert {e["profil"]["regime"] for e in profils.values()} == set(AFFILIATIONS_PUBLIQUES)
    for code, entree in profils.items():
        assert 2009 <= entree["profil"]["liquidation"] <= 2020, code
        # Les générations d'avant 1949 liquidant après 2013 tombent sur une
        # table de durée de service qu'OpenFisca a mal transcrite.
        assert not (entree["profil"]["naissance"] < 1949
                    and entree["profil"]["liquidation"] > 2013), code
        assert entree["openfisca"]["duree_assurance"] > 0, code
        assert entree["openfisca"]["pension_brute"] > 0, code


def test_la_duree_de_service_de_la_pension_civile_concorde(
        oracle_fonction_publique, nos_calculs_fonction_publique):
    for code, entree in oracle_fonction_publique["profils"].items():
        nous = nos_calculs_fonction_publique[code]
        assert nous["duree_assurance"] == entree["openfisca"]["duree_assurance"], code


def test_la_decote_de_la_pension_civile_se_lit_a_l_annee_d_ouverture_du_droit(
        oracle_fonction_publique, nos_calculs_fonction_publique):
    """Le décompte des trimestres de décote, barème de l'article L. 14.

    C'est ce contrôle qui a révélé que le modèle lisait le barème à l'année de
    LIQUIDATION. Le III de l'article 66 de la loi du 21 août 2003 titre sa
    colonne « Année au cours de laquelle sont réunies les conditions
    mentionnées au I et au II de l'article L. 24 » : un sédentaire né en 1948
    réunit ces conditions en 2008, et garde 0,375 % et « limite d'âge moins
    douze trimestres » quelle que soit l'année de son départ. Parti en 2010 à
    soixante-deux ans, il n'a aucun trimestre de décote — le modèle lui en
    opposait deux, avec le barème de 2010.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        nous, eux = (nos_calculs_fonction_publique[code],
                     entree["openfisca"])
        assert nous["decote_trimestres"] == eux["decote_trimestres"], code


#: Profils où OpenFisca sert la surcote au taux de l'année du départ à tous
#: les trimestres, quand l'article L. 14 III donne à chacun le taux en vigueur
#: quand il a été accompli — 0,75 % jusqu'en 2008, 1,25 % depuis (LFSS 2009).
#: Né le 1er janvier 1948, à l'âge légal le 1er janvier 2008, parti le 1er
#: janvier 2011 : douze trimestres de durée depuis l'âge légal, quatre
#: accomplis en 2008 à 0,75 % et huit en 2009 et 2010 à 1,25 % ; OpenFisca en
#: compte douze aussi, tous à 1,25 %. Jusqu'au 28 septembre 2026, le modèle,
#: qui ne connaissait pas le jour, ouvrait la période au mois suivant et n'en
#: comptait que onze. Le test vérifie que chacun rend exactement ce que SA
#: règle commande.
SURCOTE_CIVILE_DATEE = {"surcote_1948": ((4, 0.0075), (8, 0.0125))}


def _coefficient_surcote_civile(code: str, eux: dict) -> tuple[float, float]:
    """(notre coefficient, celui d'OpenFisca) pour un profil surcoté."""
    leur = 1 + 0.0125 * eux["surcote_trimestres"]
    if code not in SURCOTE_CIVILE_DATEE:
        return leur, leur
    notre = 1 + sum(n * taux for n, taux in SURCOTE_CIVILE_DATEE[code])
    return notre, leur


def test_le_taux_de_la_pension_civile_concorde_sauf_la_transcription_de_2010(
        oracle_fonction_publique, nos_calculs_fonction_publique):
    """Décote et surcote ensemble : le taux de liquidation.

    Un seul écart, et il est chez OpenFisca : pour un droit ouvert en 2010, sa
    table porte 0,65 % par trimestre là où la loi écrit 0,625 %. Le profil est
    gardé, et le test vérifie que chacun des deux modèles rend exactement le
    taux que SON coefficient commande — c'est ainsi qu'on sait de quel côté
    est l'écart, et qu'il n'est que celui-là.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        profil, eux = entree["profil"], entree["openfisca"]
        nous = nos_calculs_fonction_publique[code]
        if _annee_ouverture_du_droit(profil) == 2010 and eux["decote_trimestres"]:
            manquants = eux["decote_trimestres"]
            assert nous["taux_de_liquidation"] == pytest.approx(
                TAUX_PLEIN_PENSION_CIVILE * (1 - COEFFICIENT_2010_LOI * manquants),
                abs=TOLERANCE_EXACTE), code
            assert eux["taux_de_liquidation"] == pytest.approx(
                TAUX_PLEIN_PENSION_CIVILE * (1 - COEFFICIENT_2010_OPENFISCA * manquants),
                abs=TOLERANCE_EXACTE), code
            continue
        if code in SURCOTE_CIVILE_DATEE:
            notre, leur = _coefficient_surcote_civile(code, eux)
            assert nous["taux_de_liquidation"] == pytest.approx(
                TAUX_PLEIN_PENSION_CIVILE * notre, abs=TOLERANCE_EXACTE), code
            assert eux["taux_de_liquidation"] == pytest.approx(
                TAUX_PLEIN_PENSION_CIVILE * leur, abs=TOLERANCE_EXACTE), code
            continue
        assert nous["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code


def test_la_surcote_de_la_pension_civile_concorde(oracle_fonction_publique, nos_calculs_fonction_publique):
    """Le témoin porte au moins un profil surcoté, et les deux la servent —
    OpenFisca au taux du départ pour tous les trimestres, nous au taux de
    chacun (voir ``SURCOTE_CIVILE_DATEE``)."""
    surcotes = [
        (code, entree) for code, entree in oracle_fonction_publique["profils"].items()
        if entree["openfisca"]["surcote_trimestres"] > 0
    ]
    assert surcotes
    for code, entree in surcotes:
        eux = entree["openfisca"]
        nous = nos_calculs_fonction_publique[code]
        notre, leur = _coefficient_surcote_civile(code, eux)
        assert eux["decote_trimestres"] == 0, code
        assert nous["taux_de_liquidation"] == pytest.approx(
            TAUX_PLEIN_PENSION_CIVILE * notre, abs=TOLERANCE_EXACTE), code
        assert eux["taux_de_liquidation"] == pytest.approx(
            TAUX_PLEIN_PENSION_CIVILE * leur, abs=TOLERANCE_EXACTE), code


def test_la_proratisation_de_la_pension_civile_concorde(
        oracle_fonction_publique, nos_calculs_fonction_publique):
    for code, entree in oracle_fonction_publique["profils"].items():
        nous, eux = (nos_calculs_fonction_publique[code],
                     entree["openfisca"])
        assert nous["coefficient_de_proratisation"] == pytest.approx(
            eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE), code


def test_le_traitement_de_reference_suit_le_point_d_indice(
        oracle_fonction_publique, nos_calculs_fonction_publique):
    """Le traitement de l'année d'avant, ramené à l'année du départ.

    Un fonctionnaire garde son indice : son traitement suit le point. Le
    modèle le ramenait au départ par les prix, et s'écartait d'OpenFisca de
    0,5 à 0,8 % — de tout ce que le point avait fait de moins que les prix,
    gel de 2010-2016 compris. Il suit maintenant le point, et les deux
    traitements tombent au centime.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        nous, eux = (nos_calculs_fonction_publique[code],
                     entree["openfisca"])
        assert nous["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=1e-6), code


def test_la_pension_civile_concorde_au_centime(oracle_fonction_publique, nos_calculs_fonction_publique):
    """Traitement × taux × proratisation : le bout de la chaîne.

    Au centime près, sauf pour le droit ouvert en 2010, où l'écart est celui
    de la transcription d'OpenFisca — et il se retrouve exactement en
    substituant son coefficient au nôtre.
    """
    for code, entree in oracle_fonction_publique["profils"].items():
        profil, eux = entree["profil"], entree["openfisca"]
        nous = nos_calculs_fonction_publique[code]
        notre_pension = nous["pension_avant_minimum"]
        if _annee_ouverture_du_droit(profil) == 2010 and eux["decote_trimestres"]:
            manquants = eux["decote_trimestres"]
            notre_pension *= ((1 - COEFFICIENT_2010_OPENFISCA * manquants)
                              / (1 - COEFFICIENT_2010_LOI * manquants))
        if code in SURCOTE_CIVILE_DATEE:
            notre, leur = _coefficient_surcote_civile(code, eux)
            notre_pension *= leur / notre
        assert notre_pension == pytest.approx(eux["pension_avant_minimum"], rel=1e-6), code


def test_le_minimum_garanti_reste_proche(oracle_fonction_publique, nos_calculs_fonction_publique):
    """Le plancher de l'article L. 17, sur un profil où il joue.

    OpenFisca le calcule au point d'indice de l'année de liquidation ; le
    modèle fige la référence au 1er janvier 2004 et la revalorise comme les
    pensions, ce que l'article écrit. L'écart est donc le sien, il va toujours
    dans le même sens — le point a fait moins que les prix — et il reste de
    quelques pour cent : le test le borne sans l'effacer.
    """
    joues = [
        (code, entree) for code, entree in oracle_fonction_publique["profils"].items()
        if entree["openfisca"]["minimum_garanti"] > entree["openfisca"]["pension_avant_minimum"]
    ]
    assert joues, "aucun profil où le minimum garanti se substitue à la pension"
    for code, entree in oracle_fonction_publique["profils"].items():
        eux = entree["openfisca"]
        if eux["minimum_garanti"] <= 0:
            continue
        nous = nos_calculs_fonction_publique[code]
        assert nous["minimum_garanti"] == pytest.approx(
            eux["minimum_garanti"], rel=TOLERANCE_MINIMUM_GARANTI), code
        assert nous["minimum_garanti"] >= eux["minimum_garanti"], code
    for code, entree in joues:
        nous = nos_calculs_fonction_publique[code]
        assert nous["pension_brute"] == pytest.approx(nous["minimum_garanti"], rel=1e-6), code
        assert entree["openfisca"]["pension_brute"] == pytest.approx(
            entree["openfisca"]["minimum_garanti"], rel=1e-6), code



def test_la_pension_civile_se_mesure_au_portage_sans_les_jumeaux_python(
        oracle_fonction_publique, nos_calculs_fonction_publique, monkeypatch):
    """Chaque profil du témoin de la pension civile se mesure au portage, le
    moteur qui fait foi, minimum garanti compris (``pont.droit``) : les
    jumeaux Python, qu'on empêche ici de calculer, n'y entrent pas."""
    _sans_les_jumeaux(monkeypatch, (ScenarioActuel, "calculer"), (ouvrir, "duree_requise"),
                      (liquider, "duree_proratisation"), (liquider, "decote_opposable"),
                      (liquider, "salaire_de_reference"), (liquider, "trimestres_de_decote"),
                      (MinimumGaranti, "montant"))
    nos = _nos_calculs_fonction_publique(_profils(oracle_fonction_publique), pont.droit)
    assert set(nos) == set(oracle_fonction_publique["profils"])
    assert nos == nos_calculs_fonction_publique

# -- l'Arrco d'avant 2019 ------------------------------------------------------

@pytest.fixture(scope="module")
def oracle_arrco() -> dict:
    return json.loads(TEMOIN_ARRCO.read_text(encoding="utf-8"))


_POINTS = re.compile(r"^([\d,]+\.\d+) points ×")


def _points_servis(resultat: dict, du_regime) -> tuple[float, float]:
    """Les points acquis, et le coefficient d'anticipation ou de majoration,
    que la formule servie écrit sous chaque pension des régimes que
    ``du_regime`` retient — « 1,543.91 points × valeur de service 1.2513 € »
    —, celle qu'on doit pouvoir refaire à la main, dans le résultat du
    scénario 1 que le portage rend."""
    points, coefficient = 0.0, 1.0
    for pension in resultat["pensions_par_regime"]:
        if not du_regime(pension["regime"]) or pension["montant"] <= 0:
            continue
        lecture = _POINTS.match(pension["detail"])
        assert lecture, pension["detail"]
        points += float(lecture.group(1).replace(",", ""))
        if ("coefficient d'anticipation" in pension["detail"]
                or "coefficient de majoration" in pension["detail"]):
            coefficient = float(pension["detail"].rsplit(" ", 1)[1])
    return points, coefficient


def _nos_points_arrco(profils: dict[str, dict], droit=droit_et_refait,
                      ) -> dict[str, dict[str, float]]:
    """L'Arrco du scénario 1, sur la carrière exacte de chaque profil, sous
    son code : points acquis, valeur servie, abattement.

    Les points se lisent dans la formule que le modèle écrit pour chaque
    pension (:func:`_points_servis`). La tranche 2 des non-cadres a sa propre
    ligne, et OpenFisca additionne les deux. Le portage calcule la pension et
    la valeur du point au jour du départ (:func:`pont.droit`) ; par défaut, le
    jumeau Python refait chaque appel au bit près (``droit_et_refait``).
    """
    appels = {}
    for code, profil in profils.items():
        appels |= {
            f"{code}|resultat": ("scenario_actuel.calculer", pont.MOTEUR,
                                 _carriere_du_regime_general(profil)),
            f"{code}|service": ("liquider.valeur_du_point", pont.MOTEUR, "arrco",
                                DateMois(profil["liquidation"], 1)),
        }
    lus, refus = droit(appels)
    assert refus == {}, refus
    mesures = {}
    for code in profils:
        points, coefficient = _points_servis(lus[f"{code}|resultat"],
                                             lambda regime: regime.startswith("arrco"))
        service = lus[f"{code}|service"]
        mesures[code] = {
            "points": points,
            "coefficient_de_minoration": coefficient,
            "valeur_du_point_au_1er_janvier": service[0] if service else 0.0,
        }
    return mesures


@pytest.fixture(scope="module")
def nos_points_arrco(oracle_arrco) -> dict[str, dict[str, float]]:
    """L'Arrco du scénario 1 sur chaque profil du témoin, sous son code."""
    return _nos_points_arrco(_profils(oracle_arrco))


def test_le_temoin_de_l_arrco_couvre_le_perimetre_annonce(oracle_arrco):
    """Carrières d'après l'unification de 1999, liquidées avant la fusion."""
    assert oracle_arrco["source"] == "OpenFisca-France-Pension"
    assert oracle_arrco["version"]
    assert len(oracle_arrco["profils"]) >= 6
    for code, entree in oracle_arrco["profils"].items():
        assert entree["profil"]["debut"] >= 1999, code
        assert entree["profil"]["liquidation"] <= 2018, code
        assert entree["openfisca"]["points"] > 0, code
        assert entree["openfisca"]["pension_brute"] > 0, code
        assert len(entree["openfisca"]["points_annuels"]) == (
            entree["profil"]["liquidation"] - entree["profil"]["debut"]), code


def test_les_points_arrco_concordent(oracle_arrco, nos_points_arrco):
    """Cotisation → points, vingt ans de barèmes rejoués par un autre moteur.

    Taux effectif par tranche, prix d'achat du point, taux d'appel : trois
    transcriptions séparées d'OpenFisca-France, que le modèle lit, contre le
    calcul complet d'OpenFisca-France-Pension. Au millième, tranche 2 comprise.
    """
    for code, entree in oracle_arrco["profils"].items():
        nous = nos_points_arrco[code]
        assert nous["points"] == pytest.approx(entree["openfisca"]["points"], rel=1e-4), code
    assert any(e["profil"]["salaire"] > 30000 for e in oracle_arrco["profils"].values()), (
        "aucun profil au-dessus du plafond : la tranche 2 n'est pas mise à l'épreuve"
    )


def test_la_valeur_de_service_arrco_concorde_au_jour(oracle_arrco, nos_points_arrco):
    """La même valeur du point, au même jour.

    OpenFisca lit la valeur du 1er janvier de la liquidation : une liquidation
    au 1er janvier 2012 se voit servir 1,2135 € chez lui, la valeur d'avril
    2011. Le dépôt, qui retenait celle du 31 décembre — 1,2414 € —, sert
    désormais celle du jour (`valeurs_service_datees.csv`, étape 138.20) :
    au 1er janvier, la même.
    """
    for code, entree in oracle_arrco["profils"].items():
        nous = nos_points_arrco[code]
        assert nous["valeur_du_point_au_1er_janvier"] == pytest.approx(
            entree["openfisca"]["valeur_du_point"], abs=1e-4), code


def test_la_decote_du_regime_general_qui_commande_l_arrco_concorde(
        oracle_arrco):
    """L'abattement Arrco se lit sur les trimestres de décote du régime général."""
    nos = _nos_calculs(_profils(oracle_arrco))
    for code, entree in oracle_arrco["profils"].items():
        nous = nos[code]
        assert nous["decote_trimestres"] == (
            entree["openfisca"]["decote_trimestres_regime_general"]), code


def test_le_coefficient_d_anticipation_arrco_concorde_sur_les_annees_pleines(
        oracle_arrco, nos_points_arrco):
    """Le barème d'anticipation, là où les deux lectures se recouvrent.

    OpenFisca ne lit son barème que par année ENTIÈRE d'anticipation, en
    tronquant les trimestres ; l'Arrco l'écrit par trimestre, et le modèle le
    lit ainsi. Les deux coïncident quand l'anticipation tombe sur des années
    pleines, et le modèle ne peut jamais servir plus qu'OpenFisca ailleurs.
    """
    pleines = 0
    for code, entree in oracle_arrco["profils"].items():
        eux = entree["openfisca"]
        nous = nos_points_arrco[code]
        if eux["decote_trimestres_regime_general"] % 4 == 0:
            pleines += 1
            assert nous["coefficient_de_minoration"] == pytest.approx(
                eux["coefficient_de_minoration"], abs=TOLERANCE_EXACTE), code
        else:
            assert nous["coefficient_de_minoration"] <= (
                eux["coefficient_de_minoration"] + TOLERANCE_EXACTE), code
    assert pleines >= 3



def test_l_arrco_se_mesure_au_portage_sans_les_jumeaux_python(
        oracle_arrco, nos_points_arrco, monkeypatch):
    """Les points, l'abattement et la valeur de service de chaque profil du
    témoin de l'Arrco se mesurent au portage (``pont.droit``) : les jumeaux
    Python, qu'on empêche ici de calculer, n'y entrent pas."""
    _sans_les_jumeaux(monkeypatch, (ScenarioActuel, "calculer"), (liquider, "valeur_du_point"))
    nos = _nos_points_arrco(_profils(oracle_arrco), pont.droit)
    assert set(nos) == set(oracle_arrco["profils"]) and nos == nos_points_arrco

# -- l'Agirc des cadres, 1947-2018 ---------------------------------------------

#: Taux EFFECTIFS que le barème d'OpenFisca sert sur la tranche B là où il
#: s'écarte du nôtre, et ils ne s'en écartent que deux fois. En 1989, le taux
#: d'appel de l'Agirc passe à 1,134 : son barème employeur suit — 6 % × 1,134 =
#: 6,804 % — et son barème salarié reste à 2,2 %, la valeur de 1987, au lieu de
#: 2,268 %. En 1994, son couple 8,43 / 3,63 donne 12,06 % quand le contractuel
#: de 10 % appelé à 1,21 en fait 12,10. Les profils sont gardés, et le test
#: vérifie que l'écart n'est que celui-là.
TAUX_AGIRC_OPENFISCA = {1989: 0.09004, 1994: 0.1206}

#: Même chose pour la part SALARIÉE, qui est celle qu'OpenFisca étend à tort à
#: la tranche C avant 1991 : 2,2 % en 1989 au lieu de 2,268 %.
TAUX_SALARIE_AGIRC_OPENFISCA = {1989: 0.022}

#: Année à partir de laquelle l'Agirc revalorise sa valeur de service au 1er
#: avril et non plus au 1er janvier — donc année à partir de laquelle le
#: paramètre lu au 1er janvier par OpenFisca porte le millésime précédent.
ANNEE_DU_1ER_AVRIL_SERVICE_AGIRC = 2001

#: Même bascule pour le prix d'achat, trois ans plus tard.
ANNEE_DU_1ER_AVRIL_ACHAT_AGIRC = 2004

#: Première année où l'Agirc appelle une cotisation sur la tranche C.
PREMIERE_ANNEE_TRANCHE_C = 1991

#: Tolérance des identités rejouées sur les relevés d'OpenFisca : il rend des
#: flottants simple précision, et le témoin les porte tels quels.
TOLERANCE_FLOTTANT_32 = 1e-4


@pytest.fixture(scope="module")
def oracle_agirc() -> dict:
    return json.loads(TEMOIN_AGIRC.read_text(encoding="utf-8"))


def _annees_du_temoin(temoin: dict) -> range:
    """Les années que les profils d'un témoin traversent, l'année d'avant le
    premier début comprise : celle du millésime qu'OpenFisca lit au 1er
    janvier."""
    profils = temoin["profils"].values()
    return range(min(e["profil"]["debut"] for e in profils) - 1,
                 max(e["profil"]["liquidation"] for e in profils) + 1)


def _bareme(code: str, annees, droit=droit_et_refait) -> dict:
    """Le barème d'un régime, que le portage lit, sur les ``annees`` que
    traversent les profils : ses périodes — leurs années, leur assiette, leur
    taux de cotisation et la part du salarié —, les bornes de chaque assiette
    en plafonds, le plafond de la Sécurité sociale de chaque année, le prix
    d'achat du point et le taux d'appel de chaque année (:func:`pont.droit`).
    Par défaut, le jumeau Python refait chaque lecture au bit près
    (``droit_et_refait``)."""
    annees = list(annees)
    lus, refus = droit({
        "periodes": ("scenario_actuel.catalogue.periodes", pont.MOTEUR, code),
        "bornes": ("regimes.BORNES_ASSIETTE",),
        **{f"plafond|{annee}": ("scenario_actuel.macro.plafond_securite_sociale", pont.MOTEUR,
                                annee) for annee in annees},
        **{f"achat|{annee}": ("scenario_actuel.valeurs_point.achat", pont.MOTEUR, code, annee)
           for annee in annees},
    })
    assert refus == {}, refus
    return {
        "periodes": lus["periodes"],
        "bornes": lus["bornes"],
        "plafonds": {annee: lus[f"plafond|{annee}"] for annee in annees},
        "achats": {annee: lus[f"achat|{annee}"] for annee in annees},
    }


def _assiette_et_cotisation(bareme: dict, annee: int, salaire: float) -> dict[str, float]:
    """L'assiette de chaque tranche du régime, et la cotisation qui en sort.

    Le moteur ne les publie pas séparément — il n'en publie que des points.
    Le test les recompose depuis la fiche du régime, parce que c'est là que
    porte la confrontation : ce sont les barèmes de cotisation des deux
    modèles qu'il s'agit d'opposer, avant qu'un prix d'achat ne les traduise.
    La fiche, le plafond et les bornes des tranches sont ceux du portage
    (:func:`_bareme`).
    """
    plafond = bareme["plafonds"][annee]
    tranches: dict[str, float] = {}
    parts: dict[str, float] = {}
    cotisation = 0.0
    for periode in bareme["periodes"]:
        if not (periode["debut"] <= annee <= (periode["fin"] or 9999)):
            continue
        bas, haut = bareme["bornes"][periode["assiette"]]
        assiette = max(
            0.0, min(salaire, (haut * plafond) if haut else salaire) - bas * plafond
        )
        tranches[periode["assiette"]] = assiette
        parts[periode["assiette"]] = periode["part_salariale"]
        cotisation += assiette * periode["taux_cotisation_retraite"]
    return {"tranches": tranches, "cotisation": cotisation,
            "parts_salariales": parts}


def _taux_de_la_tranche(bareme: dict, annee: int, assiette: str) -> float:
    for periode in bareme["periodes"]:
        if (periode["debut"] <= annee <= (periode["fin"] or 9999)
                and periode["assiette"] == assiette):
            return periode["taux_cotisation_retraite"]
    return 0.0


def _carriere_a_points(profil: dict, affiliation: str) -> Carriere:
    """La carrière exacte d'un profil du témoin, dans l'affiliation du régime
    à points, quatre trimestres chaque année, du début au départ.

    ``prive_des`` : l'année où le profil quitte le service public pour le privé
    (l'Ircantec `surcote_1945`, que sa limite d'âge arrête à soixante-cinq ans).
    """
    prive_des = profil.get("prive_des", profil["liquidation"])
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"], trimestres_valides=4,
            affiliation=affiliation if annee < prive_des else "salarie_prive_non_cadre",
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    return Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )


def _nos_points(profils: dict[str, dict], regime: str, affiliation: str,
                droit=droit_et_refait) -> dict[str, dict[str, float]]:
    """Points acquis et coefficient d'anticipation de chaque profil, sous son
    code, lus dans la formule servie (:func:`_points_servis`).

    Comme pour l'Arrco : la formule que le modèle écrit sous chaque pension est
    celle qu'on doit pouvoir refaire à la main, et c'est donc elle qu'on
    oppose à l'oracle. Le portage calcule la pension (:func:`pont.droit`) ;
    par défaut, le jumeau Python la refait au bit près (``droit_et_refait``).
    """
    lus, refus = droit({code: ("scenario_actuel.calculer", pont.MOTEUR,
                               _carriere_a_points(profil, affiliation))
                        for code, profil in profils.items()})
    assert refus == {}, refus
    mesures = {}
    for code in profils:
        points, coefficient = _points_servis(lus[code], lambda nom: nom == regime)
        mesures[code] = {"points": points, "coefficient_de_minoration": coefficient}
    return mesures


def _services_au_depart(profils: dict[str, dict], regime: str, droit=droit_et_refait,
                        ) -> dict[str, tuple | None]:
    """La valeur de service du point de ``regime`` au jour du départ de chaque
    profil, le 1er janvier de sa liquidation, sous son code, que le portage
    lit (:func:`pont.droit`) ; par défaut, le jumeau Python la refait au bit
    près (``droit_et_refait``)."""
    lus, refus = droit({code: ("liquider.valeur_du_point", pont.MOTEUR, regime,
                               DateMois(profil["liquidation"], 1))
                        for code, profil in profils.items()})
    assert refus == {}, refus
    return lus


@pytest.fixture(scope="module")
def bareme_agirc(oracle_agirc) -> dict:
    """Le barème de l'Agirc sur les années que traversent les profils."""
    return _bareme("agirc", _annees_du_temoin(oracle_agirc))


@pytest.fixture(scope="module")
def nos_points_agirc(oracle_agirc) -> dict[str, dict[str, float]]:
    """Les points Agirc du scénario 1 sur chaque profil du témoin, sous son code."""
    return _nos_points(_profils(oracle_agirc), "agirc", "salarie_prive_cadre")


@pytest.fixture(scope="module")
def services_agirc(oracle_agirc) -> dict[str, tuple]:
    """La valeur de service de l'Agirc au jour du départ de chaque profil."""
    return _services_au_depart(_profils(oracle_agirc), "agirc")


def test_le_temoin_de_l_agirc_couvre_le_perimetre_annonce(oracle_agirc):
    """Dix profils de cadres, aucun relevé nul, aucune liquidation hors barème."""
    assert oracle_agirc["source"] == "OpenFisca-France-Pension"
    assert oracle_agirc["version"]
    profils = oracle_agirc["profils"]
    assert len(profils) >= 10
    for code, entree in profils.items():
        profil, mesures = entree["profil"], entree["openfisca"]
        assert profil["liquidation"] < 2025, code
        assert profil["debut"] >= 1948, code
        assert mesures["points"] > 0, code
        assert mesures["pension_brute"] > 0, code
        assert len(mesures["points_annuels"]) == (
            profil["liquidation"] - profil["debut"]), code


def test_le_prix_d_achat_agirc_concorde_a_une_date_pres(oracle_agirc, bareme_agirc):
    """Prix d'achat et taux d'appel, année par année, sur les dix profils.

    OpenFisca achète ses points comme nous — cotisation ÷ (taux d'appel × prix
    d'achat) —, et rejouer cette division sur ses propres relevés dit si les
    deux séries sont la même. Elles le sont, à une date près : l'Agirc a
    déplacé la revalorisation de son salaire de référence du 1er janvier au
    1er avril en 2004, le dépôt retient le prix en vigueur au 31 décembre —
    celui qui vaut pour les salaires de l'année — et OpenFisca lit le
    paramètre au 1er janvier, donc le millésime précédent. Le test vérifie
    que l'écart n'est QUE ce décalage, et qu'il ne commence pas avant 2004.
    """
    decales = 0
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        for annee in range(profil["debut"], profil["liquidation"]):
            cotisation = mesures["cotisations_annuelles"][str(annee)]
            leurs = mesures["points_annuels"][str(annee)]
            millesime = (annee - 1 if annee >= ANNEE_DU_1ER_AVRIL_ACHAT_AGIRC
                         else annee)
            # Le prix d'achat est lu au millésime qu'OpenFisca sert, le taux
            # d'appel à l'année courante : c'est lui qui ne bouge pas.
            prix = bareme_agirc["achats"][millesime][0]
            appel = bareme_agirc["achats"][annee][1]
            assert cotisation / (appel * prix) == pytest.approx(
                leurs, rel=TOLERANCE_FLOTTANT_32), (code, annee)
            decales += millesime != annee
    assert decales, "aucun profil ne franchit 2004 : le décalage n'est pas mis à l'épreuve"


def test_la_cotisation_agirc_concorde_sauf_deux_taux(oracle_agirc, bareme_agirc):
    """Le barème de cotisation, opposé au sien année par année.

    Il tombe juste partout, sauf deux fois, et les deux sont chez lui : son
    barème salarié ne suit pas le taux d'appel de 1989 et son couple de 1994
    perd quatre centièmes de point. Le profil qui traverse la tranche C est
    traité à part, dans le test suivant.
    """
    vus = set()
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        if code.startswith("tranche_c"):
            continue
        for annee in range(profil["debut"], profil["liquidation"]):
            nous = _assiette_et_cotisation(bareme_agirc, annee, profil["salaire"])
            assert not nous["tranches"].get("tranche_c"), (code, annee)
            attendu = nous["cotisation"]
            if annee in TAUX_AGIRC_OPENFISCA:
                attendu = (nous["tranches"]["tranche_b"]
                           * TAUX_AGIRC_OPENFISCA[annee])
                vus.add(annee)
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                attendu, rel=TOLERANCE_FLOTTANT_32), (code, annee)
    assert vus == set(TAUX_AGIRC_OPENFISCA), (
        "les deux années où son barème retarde ne sont pas traversées"
    )


def test_la_tranche_c_de_l_agirc_est_cotisee_chez_lui_des_1948(
        oracle_agirc, bareme_agirc):
    """Ce qu'un cadre payé plus de quatre plafonds paie, chez lui et chez nous.

    L'Agirc n'appelle de cotisation sur la tranche C qu'à compter de 1991.
    Le barème EMPLOYEUR d'OpenFisca l'écrit — taux nul de 1948 à 1990 — mais
    son barème SALARIÉ laisse la case vide, et OpenFisca lit une case vide
    comme une tranche absente : le taux de la tranche B s'étend alors jusqu'à
    huit plafonds. Le test reconstitue exactement cette cotisation
    fantôme — part salariale de la tranche B appliquée à la tranche C — et
    vérifie qu'elle explique tout l'écart, année par année.
    """
    entrees = [(c, e) for c, e in oracle_agirc["profils"].items()
               if c.startswith("tranche_c")]
    assert entrees, "aucun profil au-dessus de quatre plafonds"
    for code, entree in entrees:
        profil, mesures = entree["profil"], entree["openfisca"]
        avant_1991 = 0
        for annee in range(profil["debut"], profil["liquidation"]):
            nous = _assiette_et_cotisation(bareme_agirc, annee, profil["salaire"])
            tranche_b = nous["tranches"]["tranche_b"]
            tranche_c = nous["tranches"].get("tranche_c", 0.0)
            taux_b = TAUX_AGIRC_OPENFISCA.get(
                annee, _taux_de_la_tranche(bareme_agirc, annee, "tranche_b")
            )
            if annee >= PREMIERE_ANNEE_TRANCHE_C:
                attendu = tranche_b * taux_b + tranche_c * _taux_de_la_tranche(
                    bareme_agirc, annee, "tranche_c"
                )
            else:
                # Sa tranche B s'étend à huit plafonds : au-delà de quatre, il
                # ne prélève que la part salariale, l'employeur ayant un taux
                # nul écrit.
                plafond = bareme_agirc["plafonds"][annee]
                fantome = max(0.0, min(profil["salaire"], 8 * plafond) - 4 * plafond)
                taux_salarie = TAUX_SALARIE_AGIRC_OPENFISCA.get(
                    annee, taux_b * nous["parts_salariales"]["tranche_b"]
                )
                attendu = tranche_b * taux_b + fantome * taux_salarie
                avant_1991 += fantome > 0
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                attendu, rel=TOLERANCE_FLOTTANT_32), (code, annee)
        assert avant_1991 >= 5, code


def test_les_points_agirc_concordent(oracle_agirc, nos_points_agirc):
    """Le bout de la chaîne, sur les profils que rien ne sépare.

    Trois profils ne traversent ni 1989, ni 1994, ni la tranche C, ni le
    changement de date de 2004 : sur eux, les deux moteurs doivent rendre le
    même nombre de points, au millième. Les sept autres portent chacun un des
    trois écarts, et le test vérifie que le SENS de chacun est le bon — les
    deux taux en retard font servir MOINS de points à OpenFisca, et de peu ;
    la tranche C fantôme et le prix d'achat d'un millésime en arrière lui en
    font servir davantage.
    """
    exacts = 0
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        nous = nos_points_agirc[code]
        annees = set(range(profil["debut"], profil["liquidation"]))
        sert_plus = (code.startswith("tranche_c")
                     or profil["liquidation"] > ANNEE_DU_1ER_AVRIL_ACHAT_AGIRC)
        if not sert_plus and not annees & set(TAUX_AGIRC_OPENFISCA):
            exacts += 1
            assert nous["points"] == pytest.approx(
                mesures["points"], rel=1e-4), code
        elif sert_plus:
            assert mesures["points"] > nous["points"] > 0, code
        else:
            assert 0 < mesures["points"] < nous["points"], code
            assert nous["points"] / mesures["points"] - 1 < 1e-3, code
    assert exacts >= 3


def test_la_valeur_de_service_agirc_suit_la_date_de_revalorisation(
        oracle_agirc, services_agirc):
    """La même valeur, au même jour.

    OpenFisca lit la valeur du 1er janvier de la liquidation. Tant que l'Agirc
    revalorise au 1er janvier — jusqu'en 2000 —, c'est celle de l'année ; à
    partir de 2001, où elle passe au 1er avril, celle de l'année précédente.
    Le dépôt, qui retenait celle du 31 décembre, sert désormais celle du jour
    (`valeurs_service_datees.csv`, étape 138.20) : au 1er janvier, la même, et
    le témoin la met à l'épreuve des deux côtés de la bascule.
    """
    des_deux_cotes = set()
    for code, entree in oracle_agirc["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        liquidation = profil["liquidation"]
        service = services_agirc[code]
        assert service is not None, code
        assert service[0] == pytest.approx(
            mesures["valeur_du_point"], abs=1e-4), code
        des_deux_cotes.add(liquidation >= ANNEE_DU_1ER_AVRIL_SERVICE_AGIRC)
    assert des_deux_cotes == {True, False}, (
        "les profils ne couvrent pas les deux conventions de date"
    )


def test_la_decote_du_regime_general_qui_commande_l_agirc_concorde(
        oracle_agirc):
    """L'abattement Agirc se lit sur les trimestres de décote du régime général."""
    nos = _nos_calculs(_profils(oracle_agirc))
    for code, entree in oracle_agirc["profils"].items():
        nous = nos[code]
        assert nous["decote_trimestres"] == (
            entree["openfisca"]["decote_trimestres_regime_general"]), code


def test_le_coefficient_d_anticipation_agirc_concorde(oracle_agirc, nos_points_agirc):
    """Le barème d'anticipation de l'Agirc, celui de l'Arrco à l'identique.

    Il se lit par année entière chez lui, par trimestre chez nous : les dix
    profils tombent sur des années pleines, et les deux coefficients doivent
    alors coïncider exactement.
    """
    for code, entree in oracle_agirc["profils"].items():
        eux = entree["openfisca"]
        assert eux["decote_trimestres_regime_general"] % 4 == 0, code
        nous = nos_points_agirc[code]
        assert nous["coefficient_de_minoration"] == pytest.approx(
            eux["coefficient_de_minoration"], abs=TOLERANCE_EXACTE), code



def test_l_agirc_se_mesure_au_portage_sans_les_jumeaux_python(
        oracle_agirc, bareme_agirc, nos_points_agirc, services_agirc, monkeypatch):
    """Le barème de l'Agirc — sa fiche, le plafond de chaque année, les bornes
    des tranches, le prix d'achat et le taux d'appel —, les points et la valeur
    de service de chaque profil du témoin se lisent au portage
    (``pont.droit``) : les jumeaux Python, qu'on empêche ici de calculer ou de
    lire, n'y entrent pas."""
    _sans_les_jumeaux(monkeypatch, (ScenarioActuel, "calculer"), (liquider, "valeur_du_point"),
                      (ValeursPoint, "achat"), (CatalogueRegimes, "__getitem__"),
                      (SerieAnnuelle, "__call__"))
    profils = _profils(oracle_agirc)
    assert _bareme("agirc", _annees_du_temoin(oracle_agirc), pont.droit) == bareme_agirc
    assert _nos_points(profils, "agirc", "salarie_prive_cadre", pont.droit) == nos_points_agirc
    assert _services_au_depart(profils, "agirc", pont.droit) == services_agirc

# -- l'Ircantec des agents non titulaires --------------------------------------

#: Seule année où le barème d'OpenFisca RETARDE : il prolonge en 1991 les taux
#: de 1989, quand la Caisse des dépôts — qui gère le régime — donne 5,28 % sur
#: la tranche A et 16,42 % sur la tranche B. C'est aussi l'année de son seul
#: désaccord de taux d'appel, 1,09 contre 1,173, que
#: `scripts/fetch/cdc_ircantec.py` avait déjà relevé.
ANNEE_DU_BAREME_EN_RETARD = 1991
TAUX_IRCANTEC_1989 = (0.04905, 0.1526)

#: Ailleurs, les deux barèmes ne diffèrent que par un ARRONDI, et il est du
#: côté du producteur : la Caisse des dépôts publie le taux appelé arrondi au
#: dix-millième — 5,63 % de 1992 à 2010 —, OpenFisca sert le produit exact du
#: contractuel par le taux d'appel, 4,5 % × 1,25 = 5,625 %. L'écart vaut cinq
#: cent-millièmes de taux, soit un millième et demi de la cotisation au pire —
#: la tranche A de 1989, dont le taux est le plus bas des trois concernés.
ECART_D_ARRONDI_IRCANTEC = 1.5e-3

#: Année du seul désaccord de taux d'appel entre la Caisse des dépôts (1,173)
#: et OpenFisca (1,09), déjà relevé par `scripts/fetch/cdc_ircantec.py`.
ANNEE_DU_TAUX_D_APPEL_CONTESTE = 1991

#: Année à partir de laquelle l'Ircantec revalorise sa valeur de service au 1er
#: avril et non plus au 1er janvier : le paramètre lu au 1er janvier porte
#: alors le millésime précédent.
ANNEE_DU_1ER_AVRIL_IRCANTEC = 2009

#: Année où OpenFisca porte l'assiette de la tranche B de 4,75 à huit plafonds.
#: Le décret n° 2008-996 du 23 septembre 2008 l'y porte seize ans plus tard.
ANNEE_DES_HUIT_PLAFONDS_OPENFISCA = 1992

#: Première année où le décret applique les huit plafonds, au 1er janvier
#: suivant la publication.
ANNEE_DES_HUIT_PLAFONDS_DECRET = 2009

#: Majoration par trimestre de surcote que sert OpenFisca, et celle que
#: l'arrêté écrit : « le nombre total de points est majoré de 0,75 % par
#: trimestre entier » (article 16, paragraphe 4). Son paramètre porte dix fois
#: cela, et c'est le seul poste où il sert plus que le droit.
SURCOTE_IRCANTEC_OPENFISCA = 0.075
SURCOTE_IRCANTEC_ARRETE = 0.0075


def _cotisation_ircantec(bareme: dict, salaire: float, annee: int,
                         plafonds: float) -> float:
    """La cotisation Ircantec d'une année, l'assiette bornée à ``plafonds``.

    La borne est le paramètre du test : le décret en écrit 4,75 jusqu'en 2008,
    OpenFisca huit à partir de 1992. Tout le reste — les deux taux, le
    découpage des tranches — est lu dans la fiche du régime, celle du portage
    (:func:`_bareme`), si bien que le seul écart que la comparaison peut faire
    apparaître est celui-là.
    """
    plafond = bareme["plafonds"][annee]
    cotisation = 0.0
    for periode in bareme["periodes"]:
        if not (periode["debut"] <= annee <= (periode["fin"] or 9999)):
            continue
        bas, _ = bareme["bornes"][periode["assiette"]]
        haut = 1.0 if periode["assiette"] == "tranche_1" else plafonds
        taux = periode["taux_cotisation_retraite"]
        if annee == ANNEE_DU_BAREME_EN_RETARD:
            taux = TAUX_IRCANTEC_1989[0 if periode["assiette"] == "tranche_1" else 1]
        cotisation += max(
            0.0, min(salaire, haut * plafond) - bas * plafond
        ) * taux
    return cotisation


@pytest.fixture(scope="module")
def oracle_ircantec() -> dict:
    return json.loads(TEMOIN_IRCANTEC.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def bareme_ircantec(oracle_ircantec) -> dict:
    """Le barème de l'Ircantec sur les années que traversent les profils."""
    return _bareme("ircantec", _annees_du_temoin(oracle_ircantec))


@pytest.fixture(scope="module")
def nos_points_ircantec(oracle_ircantec) -> dict[str, dict[str, float]]:
    """Les points Ircantec du scénario 1 sur chaque profil du témoin, sous son code."""
    return _nos_points(_profils(oracle_ircantec), "ircantec", "contractuel_public")


def _millesimes_ircantec(temoin: dict) -> dict[str, int]:
    """Le millésime de la valeur de service qu'OpenFisca lit pour chaque
    profil, au 1er janvier de la liquidation : celui de l'année tant que
    l'Ircantec revalorise au 1er janvier, celui d'avant depuis qu'elle
    revalorise au 1er avril."""
    return {code: (entree["profil"]["liquidation"] - 1
                   if entree["profil"]["liquidation"] >= ANNEE_DU_1ER_AVRIL_IRCANTEC
                   else entree["profil"]["liquidation"])
            for code, entree in temoin["profils"].items()}


def _services_du_millesime(regime: str, millesimes: dict[str, int], droit=droit_et_refait,
                           ) -> dict[str, tuple | None]:
    """La valeur de service du point de ``regime`` à chaque millésime, sous le
    code du profil, que le portage lit (:func:`pont.droit`) ; par défaut, le
    jumeau Python la refait au bit près (``droit_et_refait``)."""
    lus, refus = droit({code: ("scenario_actuel.valeurs_point.service", pont.MOTEUR, regime,
                               millesime) for code, millesime in millesimes.items()})
    assert refus == {}, refus
    return lus


def _ages_du_taux_plein(generations: dict[str, int], droit=droit_et_refait,
                        ) -> dict[str, tuple | None]:
    """L'âge d'annulation de la décote de chaque génération, sous le code du
    profil, que le portage lit (:func:`pont.droit`) ; par défaut, le jumeau
    Python le refait au bit près (``droit_et_refait``)."""
    lus, refus = droit({code: ("scenario_actuel.ages_annulation_decote.age", pont.MOTEUR,
                               generation) for code, generation in generations.items()})
    assert refus == {}, refus
    return lus


@pytest.fixture(scope="module")
def services_ircantec(oracle_ircantec) -> dict[str, tuple | None]:
    """La valeur de service de l'Ircantec, au millésime qu'OpenFisca lit pour
    chaque profil du témoin."""
    return _services_du_millesime("ircantec", _millesimes_ircantec(oracle_ircantec))


@pytest.fixture(scope="module")
def ages_du_taux_plein_ircantec(oracle_ircantec) -> dict[str, tuple | None]:
    """L'âge du taux plein de la génération de chaque profil du témoin."""
    return _ages_du_taux_plein({code: entree["profil"]["naissance"]
                                for code, entree in oracle_ircantec["profils"].items()})


def test_le_temoin_de_l_ircantec_couvre_le_perimetre_annonce(oracle_ircantec):
    """Onze profils d'agents non titulaires, tous postérieurs à 1971.

    Avant 1971, le dépôt a deux régimes — l'IPACTE au-dessus du plafond,
    l'IGRANTE en dessous — quand OpenFisca n'en a qu'un : la comparaison n'y
    porterait sur rien de commun.
    """
    assert oracle_ircantec["source"] == "OpenFisca-France-Pension"
    assert oracle_ircantec["version"]
    profils = oracle_ircantec["profils"]
    assert len(profils) >= 10
    for code, entree in profils.items():
        profil, mesures = entree["profil"], entree["openfisca"]
        assert profil["debut"] >= 1971, code
        assert profil["liquidation"] < 2025, code
        assert mesures["points"] > 0, code
        assert mesures["pension_brute"] > 0, code
        assert len(mesures["points_annuels"]) == (
            profil["liquidation"] - profil["debut"]), code


def test_le_prix_du_point_ircantec_concorde_sauf_le_taux_d_appel_de_1991(
        oracle_ircantec, bareme_ircantec):
    """Salaire de référence et taux d'appel, année par année, sur onze profils.

    L'Ircantec achète ses points comme nous — cotisation ÷ (taux d'appel ×
    salaire de référence) —, et rejouer cette division sur ses propres relevés
    dit si les deux séries sont la même. Elles le sont sur toute la période,
    sauf une année : 1991, où la Caisse des dépôts publie un taux d'appel de
    1,173 et OpenFisca 1,09. Le dépôt suit le producteur ; ce test constate
    que c'est bien là, et seulement là, que les deux séries divergent.
    """
    contestees = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        for annee in range(profil["debut"], profil.get("prive_des", profil["liquidation"])):
            reference, appel, _ = bareme_ircantec["achats"][annee]
            cotisation = mesures["cotisations_annuelles"][str(annee)]
            leurs = mesures["points_annuels"][str(annee)]
            if annee == ANNEE_DU_TAUX_D_APPEL_CONTESTE:
                contestees += 1
                assert leurs > cotisation / (appel * reference), (code, annee)
                continue
            assert cotisation / (appel * reference) == pytest.approx(
                leurs, rel=TOLERANCE_FLOTTANT_32), (code, annee)
    assert contestees, "aucun profil ne traverse 1991"


def test_la_cotisation_ircantec_concorde_sauf_un_arrondi(
        oracle_ircantec, bareme_ircantec):
    """Le barème des deux tranches, opposé au sien année par année.

    Les deux barèmes tombent d'accord à l'arrondi du producteur près — un
    millième de la cotisation — sur toute la période, sauf une année : 1991,
    où sa table prolonge les taux de 1989. Là, l'accord redevient exact dès
    qu'on lui substitue ce barème-là. Le profil qui dépasse 4,75 plafonds est
    traité à part, dans le test suivant.
    """
    retards = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        if code.startswith("tranche_b_1992"):
            continue
        for annee in range(profil["debut"], profil.get("prive_des", profil["liquidation"])):
            plafonds = bareme_ircantec["bornes"][
                "tranche_2_ircantec" if annee < ANNEE_DES_HUIT_PLAFONDS_DECRET
                else "tranche_2"][1]
            attendu = _cotisation_ircantec(bareme_ircantec, profil["salaire"], annee,
                                           plafonds)
            tolerance = (TOLERANCE_FLOTTANT_32 if annee == ANNEE_DU_BAREME_EN_RETARD
                         else ECART_D_ARRONDI_IRCANTEC)
            retards += annee == ANNEE_DU_BAREME_EN_RETARD
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                attendu, rel=tolerance), (code, annee)
    assert retards, "aucun profil ne traverse 1991"


def test_le_taux_appele_ircantec_est_celui_du_producteur_arrondi(
        oracle_ircantec, bareme_ircantec):
    """Là où l'assiette tient dans la tranche A, le taux se lit directement.

    Un salaire sous le plafond ne cotise que sur la tranche A : la cotisation
    divisée par le salaire EST le taux appelé, et on peut donc opposer les
    deux chiffres sans passer par une somme de tranches. Le sien, arrondi au
    dix-millième, est exactement celui que publie la Caisse des dépôts — ce
    qui établit que l'écart du test précédent est bien un arrondi, et non deux
    séries différentes.
    """
    lus = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        for annee in range(profil["debut"], profil.get("prive_des", profil["liquidation"])):
            if annee == ANNEE_DU_BAREME_EN_RETARD:
                continue
            plafond = bareme_ircantec["plafonds"][annee]
            if profil["salaire"] > plafond:
                continue
            implique = mesures["cotisations_annuelles"][str(annee)] / profil["salaire"]
            publie = _taux_de_la_tranche(bareme_ircantec, annee, "tranche_1")
            # « Arrondi au dix-millième » : la moitié d'un dix-millième sépare
            # au plus les deux lectures. On l'écrit ainsi plutôt qu'avec
            # `round`, qui tranche les demis à sa façon.
            assert abs(implique - publie) <= 5e-5 + TOLERANCE_EXACTE * 1e-3, (
                code, annee, implique, publie)
            lus += 1
    assert lus >= 20


def test_l_assiette_ircantec_s_arrete_a_4_75_plafonds_jusqu_en_2008(
        oracle_ircantec, bareme_ircantec):
    """Ce qu'un contractuel payé plus de 4,75 plafonds cotise, chez lui et chez nous.

    L'article 7 du décret n° 70-1277 limite l'assiette à « 4,75 fois le
    plafond fixé pour les cotisations de retraite du régime général » ; le
    décret n° 2008-996 du 23 septembre 2008 la porte à huit. OpenFisca l'y
    porte en 1992, seize ans trop tôt. Le test reconstitue exactement la
    tranche qu'il cotise en trop — de 4,75 à huit plafonds, au taux de la
    tranche B — et vérifie qu'avant 1992 et depuis 2009 les deux barèmes
    tombent d'accord au centime.
    """
    entrees = [(c, e) for c, e in oracle_ircantec["profils"].items()
               if c.startswith("tranche_b_1992")]
    assert entrees, "aucun profil au-dessus de 4,75 plafonds"
    for code, entree in entrees:
        profil, mesures = entree["profil"], entree["openfisca"]
        accords, ecarts = 0, 0
        for annee in range(profil["debut"], profil["liquidation"]):
            leur_borne = (8.0 if annee >= ANNEE_DES_HUIT_PLAFONDS_OPENFISCA
                          else bareme_ircantec["bornes"]["tranche_2_ircantec"][1])
            notre_borne = bareme_ircantec["bornes"][
                "tranche_2_ircantec" if annee < ANNEE_DES_HUIT_PLAFONDS_DECRET
                else "tranche_2"][1]
            tolerance = (TOLERANCE_FLOTTANT_32 if annee == ANNEE_DU_BAREME_EN_RETARD
                         else ECART_D_ARRONDI_IRCANTEC)
            assert mesures["cotisations_annuelles"][str(annee)] == pytest.approx(
                _cotisation_ircantec(bareme_ircantec, profil["salaire"], annee,
                                     leur_borne),
                rel=tolerance), (code, annee)
            if leur_borne == notre_borne:
                accords += 1
            else:
                # Le salaire dépasse les deux bornes : l'écart est tout entier
                # la tranche que le décret n'ouvre pas encore.
                assert mesures["cotisations_annuelles"][str(annee)] > (
                    _cotisation_ircantec(bareme_ircantec, profil["salaire"], annee,
                                         notre_borne) * 1.3), (code, annee)
                ecarts += 1
        assert accords >= 10, code
        assert ecarts >= 10, code


def test_les_points_ircantec_concordent(oracle_ircantec, nos_points_ircantec):
    """Le bout de la chaîne : dix profils, deux tranches, quarante ans de barèmes.

    Une seule chose sépare les deux totaux sur les profils qui restent sous
    4,75 plafonds : le taux d'appel contesté de 1991 et l'arrondi de la
    tranche A en 1989-1990, qui pèsent ensemble moins d'un pour mille. Le
    profil qui dépasse l'assiette du décret est exclu — le test précédent dit
    ce qu'il vaut, et de combien.
    """
    compares = 0
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        nous = nos_points_ircantec[code]
        if code.startswith("tranche_b_1992"):
            assert mesures["points"] > nous["points"] * 1.3, code
            continue
        compares += 1
        assert nous["points"] == pytest.approx(mesures["points"], rel=1e-3), code
    assert compares >= 9


def test_le_coefficient_d_anticipation_ircantec_suit_l_arrete_de_1970(
        oracle_ircantec, nos_points_ircantec):
    """Le barème de l'article 16, et c'est ce test qui a corrigé le modèle.

    Le modèle abattait 1,1 % par trimestre d'anticipation. L'arrêté du
    30 décembre 1970 écrit un escalier : 0,01 par trimestre sur les trois
    années les plus proches de l'âge normal, 0,012 5 sur les deux suivantes,
    0,017 5 au-delà — les paliers mêmes de l'Agirc-Arrco. Le taux moyen
    tombait juste à zéro et à cinq ans d'anticipation, et nulle part entre les
    deux : à treize trimestres il retirait 14,3 % là où l'arrêté en retire
    13,25.
    """
    intermediaires = 0
    for code, entree in oracle_ircantec["profils"].items():
        eux = entree["openfisca"]
        if eux["surcote_trimestres_regime_general"] > 0:
            continue
        nous = nos_points_ircantec[code]
        assert nous["coefficient_de_minoration"] == pytest.approx(
            eux["coefficient_de_minoration"], abs=TOLERANCE_EXACTE), code
        if 0 < eux["decote_trimestres_regime_general"] % 4:
            intermediaires += 1
    assert intermediaires >= 2, (
        "aucun profil ne tombe entre deux marches : l'escalier n'est pas "
        "distingué de la pente moyenne"
    )


def test_la_surcote_ircantec_est_dix_fois_trop_forte_chez_lui(
        oracle_ircantec, nos_points_ircantec, ages_du_taux_plein_ircantec):
    """Le seul poste où OpenFisca sert plus que le droit, et de loin.

    Le paragraphe 4 de l'article 16 majore le total des points « de 0,75 %
    par trimestre entier écoulé entre le soixante-cinquième anniversaire de
    l'assuré et la date d'entrée en jouissance » ; son paramètre porte 0,075.
    Une année de surcote y vaut +30 % de pension.

    **Ce que le modèle sert désormais, c'est l'arrêté.** Il n'en servait rien,
    et c'est ce test qui figeait les deux lectures ; il oppose maintenant la
    troisième, qui est le droit. La majoration ne se compte pas sur les mêmes
    trimestres des deux côtés : OpenFisca reprend ceux de la surcote du régime
    général — cotisés, au-delà de la durée requise —, l'arrêté compte au 1° le
    TEMPS ÉCOULÉ depuis l'âge du taux plein, sans condition de cotisation, et
    ne réserve la seconde assiette qu'à son 2°, moins bien payé.
    """
    surcotes = [
        (code, entree) for code, entree in oracle_ircantec["profils"].items()
        if entree["openfisca"]["surcote_trimestres_regime_general"] > 0
    ]
    assert surcotes, "aucun profil surcoté"
    for code, entree in surcotes:
        profil, eux = entree["profil"], entree["openfisca"]
        trimestres = eux["surcote_trimestres_regime_general"]
        assert eux["decote_trimestres_regime_general"] == 0, code
        assert eux["coefficient_de_minoration"] == pytest.approx(
            1 + SURCOTE_IRCANTEC_OPENFISCA * trimestres, abs=TOLERANCE_EXACTE), code
        nous = nos_points_ircantec[code]
        # Le 1° de l'arrêté, trimestre par trimestre : l'âge du taux plein de
        # la génération, et l'âge de la liquidation. Le 2° ne joue pas ici —
        # les trimestres au-delà de la durée requise sont postérieurs à
        # soixante-cinq ans, et le texte interdit de les payer deux fois.
        age_taux_plein = ages_du_taux_plein_ircantec[code][0]
        ecoules = round(
            (profil["liquidation"] - profil["naissance"] - age_taux_plein) * 4)
        assert ecoules > 0, code
        assert nous["coefficient_de_minoration"] == pytest.approx(
            1 + SURCOTE_IRCANTEC_ARRETE * ecoules, abs=TOLERANCE_EXACTE), code
        # Et il reste, comme avant, très en deçà de ce que lui sert.
        assert nous["coefficient_de_minoration"] < eux["coefficient_de_minoration"], code


def test_la_valeur_de_service_ircantec_suit_la_date_de_revalorisation(
        oracle_ircantec, services_ircantec):
    """La même chaîne de valeurs, lue à deux dates.

    Le dépôt retient la valeur en vigueur au 31 décembre, OpenFisca celle du
    1er janvier de la liquidation. Tant que l'Ircantec revalorise au 1er
    janvier — jusqu'en 2008 —, les deux lectures donnent le même millésime ;
    depuis 2009, où elle passe au 1er avril, la sienne est celle de l'année
    précédente.
    """
    des_deux_cotes = set()
    millesimes = _millesimes_ircantec(oracle_ircantec)
    for code, entree in oracle_ircantec["profils"].items():
        profil, mesures = entree["profil"], entree["openfisca"]
        liquidation, millesime = profil["liquidation"], millesimes[code]
        service = services_ircantec[code]
        assert service is not None, code
        assert service[0] == pytest.approx(
            mesures["valeur_du_point"], abs=1e-5), code
        des_deux_cotes.add(millesime == liquidation)
    assert des_deux_cotes == {True, False}


def test_la_decote_du_regime_general_qui_commande_l_ircantec_concorde(
        oracle_ircantec):
    """L'abattement Ircantec se lit sur les trimestres de décote du régime général."""
    nos = _nos_calculs(_profils(oracle_ircantec))
    for code, entree in oracle_ircantec["profils"].items():
        nous = nos[code]
        assert nous["decote_trimestres"] == (
            entree["openfisca"]["decote_trimestres_regime_general"]), code



def test_l_ircantec_se_mesure_au_portage_sans_les_jumeaux_python(
        oracle_ircantec, bareme_ircantec, nos_points_ircantec, services_ircantec,
        ages_du_taux_plein_ircantec, monkeypatch):
    """Le barème de l'Ircantec, les points de chaque profil du témoin, l'âge du
    taux plein de sa génération et la valeur de service qu'OpenFisca lit se
    lisent au portage (``pont.droit``) : les jumeaux Python, qu'on empêche ici
    de calculer ou de lire, n'y entrent pas."""
    _sans_les_jumeaux(monkeypatch, (ScenarioActuel, "calculer"), (ValeursPoint, "achat"),
                      (ValeursPoint, "service"), (AgesAnnulationDecote, "age"),
                      (CatalogueRegimes, "__getitem__"), (SerieAnnuelle, "__call__"))
    profils = _profils(oracle_ircantec)
    assert (_bareme("ircantec", _annees_du_temoin(oracle_ircantec), pont.droit)
            == bareme_ircantec)
    assert (_nos_points(profils, "ircantec", "contractuel_public", pont.droit)
            == nos_points_ircantec)
    assert (_services_du_millesime("ircantec", _millesimes_ircantec(oracle_ircantec),
                                   pont.droit) == services_ircantec)
    assert (_ages_du_taux_plein({code: profil["naissance"] for code, profil in profils.items()},
                                pont.droit) == ages_du_taux_plein_ircantec)

# -- les régimes alignés : MSA des salariés, artisans, commerçants --------------

#: Statuts dont le régime de base est ALIGNÉ sur le régime général par la loi,
#: et les régimes que le modèle leur donne. « Aligné » n'est pas une image,
#: c'est un renvoi d'article à article : L. 742-3 du code rural rend au régime
#: des assurances sociales agricoles le titre V du livre III du code de la
#: sécurité sociale, qui est l'assurance vieillesse du régime général, et
#: L. 634-2 du code de la sécurité sociale calcule les pensions des artisans et
#: des commerçants « dans les conditions définies […] du premier au quatrième
#: alinéas de l'article L. 351-1 ». Leur pension se confronte donc à l'oracle
#: du régime général, sur la même carrière, sans qu'aucun module supplémentaire
#: d'OpenFisca soit nécessaire — il n'en a d'ailleurs aucun.
AFFILIATIONS_ALIGNEES = {
    "salarie_agricole": ("msa_salaries",),
    "artisan": ("cancava", "rsi", "regime_general"),
    "commercant": ("organic", "rsi", "regime_general"),
}


def _carriere_alignee(profil: dict, affiliation: str) -> Carriere:
    """La carrière exacte d'un profil du témoin, dans un statut aligné, quatre
    trimestres chaque année, du début au départ."""
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["salaire"], affiliation=affiliation,
            trimestres_valides=4,
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    return Carriere(
        annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"],
    )


def _pension_alignee(resultat: dict, affiliation: str) -> dict[str, float]:
    """La pension de base d'un statut aligné, tous régimes de base confondus,
    dans le résultat du scénario 1 que le portage rend."""
    codes = set(AFFILIATIONS_ALIGNEES[affiliation])
    parts = [p for p in resultat["pensions_par_regime"]
             if p["regime"] in codes and p["montant"] > 0]
    return {
        "montant": sum(p["montant"] for p in parts),
        "morceaux": len(parts),
        "trimestres": float(resultat["trimestres_valides"]),
        "taux_de_liquidation": resultat["taux_liquidation"],
    }


#: Les statuts indépendants des régimes alignés : l'artisan et le commerçant.
INDEPENDANTS = ("artisan", "commercant")

#: Les drapeaux de ``ScenarioActuel.calculer`` d'avant ``liquider_successions``,
#: à leur valeur par défaut, dans l'ordre du jumeau, que le pont suit
#: (:func:`pont.droit`) : ``ignorer_penalite_age``,
#: ``avantages_non_contributifs``, ``avpf``.
DRAPEAUX_AVANT_LES_SUCCESSIONS = (False, True, True)

#: Les variantes du scénario 1 que mesurent les tests des indépendants : le
#: moteur, et les drapeaux de ``calculer`` après la carrière. ``"droit"``
#: liquide comme la caisse ; ``"table_du_regime_general"`` prête aux
#: indépendants la table du régime général, ce que R. 634-1-1 écarte ;
#: ``"cesure"`` liquide chaque nom de caisse sur ses seules années
#: (``liquider_successions=False``).
VARIANTES_DES_INDEPENDANTS = {
    "droit": (pont.MOTEUR, ()),
    "table_du_regime_general": (
        pont.MOTEUR.pretant("annees_revenu_independants", "annees_salaire_reference"), ()),
    "cesure": (pont.MOTEUR, (*DRAPEAUX_AVANT_LES_SUCCESSIONS, False)),
}


def _nos_pensions_alignees(profils: dict[str, dict], droit=droit_et_refait) -> dict:
    """Ce que les tests des régimes alignés mesurent du scénario 1 sur la
    carrière exacte de chaque profil, sous ``(statut, variante)``, puis son
    code : la pension de base de chaque statut aligné (:func:`_pension_alignee`)
    telle que la caisse la liquide (``"droit"``), et, pour l'artisan et le
    commerçant, sous chacune des :data:`VARIANTES_DES_INDEPENDANTS` ; sous
    ``"regimes"``, ce que sert chaque régime à leur carrière sans identifiant.
    Le portage la calcule (:func:`pont.droit`) ; par défaut, le jumeau Python
    la refait au bit près (``droit_et_refait``)."""
    appels = {}
    for affiliation in AFFILIATIONS_ALIGNEES:
        variantes = (VARIANTES_DES_INDEPENDANTS if affiliation in INDEPENDANTS
                     else {"droit": VARIANTES_DES_INDEPENDANTS["droit"]})
        for code, profil in profils.items():
            carriere = _carriere_alignee(profil, affiliation)
            for variante, (moteur, drapeaux) in variantes.items():
                appels[f"{affiliation}|{variante}|{code}"] = (
                    "scenario_actuel.calculer", moteur, carriere, *drapeaux)
            if affiliation in INDEPENDANTS:
                appels[f"{affiliation}|regimes|{code}"] = ("scenario_actuel.calculer", pont.MOTEUR, Carriere(
                    annee_naissance=profil["naissance"], sexe="H",
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    lignes=[AnneeCarriere(annee=annee, revenu=profil["salaire"],
                                          affiliation=affiliation, trimestres_valides=4)
                            for annee in range(profil["debut"], profil["liquidation"])]))
    lus, refus = droit(appels)
    assert refus == {}, refus
    mesures: dict = {}
    for cle, resultat in lus.items():
        affiliation, variante, code = cle.split("|")
        mesures.setdefault((affiliation, variante), {})[code] = (
            {p["regime"]: p["montant"] for p in resultat["pensions_par_regime"]}
            if variante == "regimes" else _pension_alignee(resultat, affiliation))
    return mesures


@pytest.fixture(scope="module")
def nos_pensions_alignees(oracle) -> dict:
    """Ce que les tests des régimes alignés mesurent du scénario 1 sur chaque
    profil du témoin du régime général, sous ``(statut, variante)``, puis son
    code."""
    return _nos_pensions_alignees(_profils(oracle))


def test_la_msa_des_salaries_agricoles_reproduit_le_regime_general(
        oracle, nos_calculs, nos_pensions_alignees):
    """Le régime des salariés agricoles, opposé à l'oracle du régime général.

    « Les prestations sont calculées comme au régime général » : l'alignement
    est dans la loi, mais rien ne vérifiait qu'il était dans le modèle. Il
    aurait pu ne pas l'être — l'action 3 de la feuille de route a montré que
    les TAUX DE COTISATION agricoles, eux, n'ont été alignés qu'en 2014, alors
    que le dépôt les croyait alignés depuis toujours.

    Sur les dix profils de l'oracle, la MSA rend exactement la pension du
    régime général : même salaire de référence, même taux, même coefficient de
    proratisation. Sa confrontation à OpenFisca est donc celle du régime
    général, à la virgule près — 1 678 770 retraités de droit direct (série
    certifiée du dépôt, 2024) entrent ainsi dans le périmètre contrôlé, sans
    qu'OpenFisca ait de module pour eux.
    """
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        nous = nos_pensions_alignees[("salarie_agricole", "droit")][code]
        reference = nos_calculs[code]
        assert nous["morceaux"] == 1, code
        assert nous["montant"] == pytest.approx(
            reference["pension_brute"], rel=1e-9), code
        assert nous["trimestres"] == reference["duree_assurance"], code
        assert nous["taux_de_liquidation"] == pytest.approx(
            entree["openfisca"]["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code
        assert nous["montant"] == pytest.approx(
            entree["openfisca"]["pension_brute"], rel=TOLERANCE_SALAIRE), code
        assert nous["montant"] <= entree["openfisca"]["pension_brute"], code


def test_les_regimes_alignes_des_independants_liquident_avec_leur_successeur(
        oracle, nos_calculs, nos_pensions_alignees):
    """L'artisan et le commerçant rendent la pension du régime général.

    Ils relèvent d'un régime aligné, eux aussi : leur pension doit donc, à
    carrière identique, être celle du régime général. Elle ne l'était pas, et
    la cause n'était pas le barème — le taux de liquidation et le décompte des
    trimestres tombaient juste — mais la SUCCESSION des caisses. La CANCAVA
    devient le RSI en 2006, le RSI est absorbé par le régime général en 2018 :
    le modèle liquidait ces trois régimes séparément, chacun sur ses seules
    années, et calculait donc DEUX salaires de référence là où la caisse n'en
    calcule qu'un.

    Le moteur liquide maintenant ensemble un régime d'annuités et celui qui
    lui succède, sous les règles de la caisse qui aurait le dossier : un seul
    salaire de référence, une seule proratisation, une seule ligne.

    Un seul écart reste, et il est dans la loi : le revenu annuel moyen des
    artisans et des commerçants nés de 1935 à 1952, pour les pensions prenant
    effet avant 2026, porte sur moins d'années que le salaire annuel moyen
    (R. 634-1-1 : vingt et une pour la génération 1949, au lieu de
    vingt-cinq), donc sur de meilleures. Leur prête-t-on celle du régime
    général, l'artisan et le commerçant rendent exactement la pension du
    salarié, comme la MSA — et donc, à la tolérance près, celle d'OpenFisca.

    L'ALIGNEMENT NE VAUT QUE DEPUIS 1973. Les années d'artisan ou de commerçant
    d'avant ont leurs points (L. 634-3 ; action 138, étape 18), hors de la
    pension alignée : l'égalité ne se lit que sur les cinq profils entrés depuis,
    et aucun ne part plus haut — leurs générations, 1952 à 1956, ne comptent pas
    plus d'années que la table n'en retient. Les cinq autres, entrés de 1968 à
    1972, gardent leur durée et leur taux ; leurs années d'avant 1973 sortent de
    la proratisation et rendent des points (test suivant).
    """
    plus_hauts = set()
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        if profil["debut"] < 1973:
            continue
        reference = nos_calculs[code]
        for affiliation in ("artisan", "commercant"):
            nous = nos_pensions_alignees[(affiliation, "droit")][code]
            assert nous["morceaux"] == 1, (code, affiliation)
            assert nous["montant"] >= reference["pension_brute"] * (1 - 1e-9), (
                code, affiliation)
            if nous["montant"] > reference["pension_brute"] * (1 + 1e-9):
                plus_hauts.add(code)
            assert nous["trimestres"] == reference["duree_assurance"], (code, affiliation)
            assert nous["taux_de_liquidation"] == pytest.approx(
                entree["openfisca"]["taux_de_liquidation"],
                abs=TOLERANCE_EXACTE), (code, affiliation)
    assert plus_hauts == set()

    # La table des indépendants prêtée par celle du régime général.
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        if profil["debut"] < 1973:
            continue
        reference = nos_calculs[code]
        for affiliation in ("artisan", "commercant"):
            nous = nos_pensions_alignees[(affiliation, "table_du_regime_general")][code]
            assert nous["montant"] == pytest.approx(
                reference["pension_brute"], rel=1e-9), (code, affiliation)
            assert nous["montant"] == pytest.approx(
                entree["openfisca"]["pension_brute"], rel=TOLERANCE_SALAIRE
            ), (code, affiliation)


def test_avant_1973_des_points_hors_de_la_pension_alignee(
        oracle, nos_calculs, nos_pensions_alignees):
    """Les cinq profils de l'oracle entrés avant 1973 (L. 634-3).

    Leurs années d'avant 1973 comptent dans la durée tous régimes — le taux de
    liquidation reste celui d'OpenFisca —, mais plus dans la pension alignée :
    elles rendent des points, au régime des droits d'avant 1973.
    """
    avant = {"artisan": "cancava_avant_1973", "commercant": "organic_avant_1973"}
    entres_avant = 0
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        if profil["debut"] >= 1973:
            continue
        entres_avant += 1
        reference = nos_calculs[code]
        for affiliation, regime in avant.items():
            nous = nos_pensions_alignees[(affiliation, "droit")][code]
            assert nous["trimestres"] == reference["duree_assurance"], (code, affiliation)
            assert nous["taux_de_liquidation"] == pytest.approx(
                entree["openfisca"]["taux_de_liquidation"],
                abs=TOLERANCE_EXACTE), (code, affiliation)
            points = nos_pensions_alignees[(affiliation, "regimes")][code][regime]
            assert points > 0, (code, affiliation)
    assert entres_avant == 5


def test_la_cesure_a_la_succession_reste_mesurable(oracle, nos_pensions_alignees):
    """Ce que la correction a déplacé, gardé comme variante pour le mesurer.

    À ``liquider_successions=False``, chaque nom de caisse est liquidé sur ses
    seules années, comme avant. La césure joue dans les deux sens — les
    meilleures années de chaque morceau peuvent être meilleures que celles de
    la carrière entière — et l'écart va de −7,1 % à +9,4 % contre OpenFisca.
    Le haut de la fourchette vient du barème DATÉ de la surcote : coupé, le
    morceau CANCAVA d'un artisan parti tard servait la surcote au taux plat
    de sa fiche de 2006 (0,75 %) à des trimestres accomplis de 2011 à 2015,
    qui valent 1,25 % — la césure cumulait deux erreurs, et l'une compensait
    l'autre. Il venait aussi de la table des indépendants (R. 634-1-1), que le
    morceau aligné d'un assuré né en 1949 appliquait à ses seules années.
    Depuis que les années d'avant 1973 ont leurs points (action 138, étape
    18), la mesure ne porte plus que sur les cinq profils entrés depuis : de
    −7,1 % à −0,2 %.
    """
    coupes, ecarts = 0, []
    for code, entree in oracle["profils"].items():
        profil = entree["profil"]
        if profil["debut"] < 1973:
            continue
        for affiliation in ("artisan", "commercant"):
            nous = nos_pensions_alignees[(affiliation, "cesure")][code]
            assert nous["morceaux"] == 2, (code, affiliation)
            coupes += 1
            ecarts.append(nous["montant"] / entree["openfisca"]["pension_brute"])
    assert coupes == 10
    assert 0.925 < min(ecarts) < 0.930, min(ecarts)
    assert 0.995 < max(ecarts) < 1.000, max(ecarts)


def test_les_regimes_alignes_se_mesurent_au_portage_sans_les_jumeaux_python(
        oracle, nos_pensions_alignees, monkeypatch):
    """La pension de base de chaque statut aligné, sur chaque profil du
    témoin — telle que la caisse la liquide, la table des indépendants prêtée
    par celle du régime général, chaque caisse sur ses seules années —, se
    mesure au portage (``pont.droit``) : le jumeau Python, qu'on empêche ici de
    calculer, n'y entre pas."""
    _sans_les_jumeaux(monkeypatch, (ScenarioActuel, "calculer"))
    assert _nos_pensions_alignees(_profils(oracle), pont.droit) == nos_pensions_alignees


# ---------------------------------------------------------------------------
# Les exemples chiffrés publiés par les caisses et par service-public.gouv.fr
# ---------------------------------------------------------------------------

EXEMPLES_OFFICIELS = TEMOIN.parent / "exemples_officiels.yaml"


def _charger_exemples() -> list[dict]:
    import yaml

    return yaml.safe_load(EXEMPLES_OFFICIELS.read_text(encoding="utf-8"))["exemples"]


def _mois(texte: str):
    from retraite_notionnelle.calendrier import DateMois

    annee, mois = texte.split("-")
    return DateMois(int(annee), int(mois))


def _naissance(texte: str):
    """Le mois de naissance d'un témoin, et son jour s'il le dit : « 1964-05-16 »
    le déclare, « 1964-05 » le laisse à la présomption ``jour_de_naissance``."""
    return _mois(texte[:7]), (int(texte[8:10]) if len(texte) > 7 else None)


def _quotites(texte: str) -> dict[int, float]:
    """Le temps partiel d'un exemple, écrit comme le formulaire l'écrit —
    « 2000:2009:80 » —, en quotité de chaque année."""
    quotites = {}
    for morceau in filter(None, (morceau.strip() for morceau in texte.split(","))):
        debut, fin, quotite = (int(partie) for partie in morceau.split(":"))
        quotites.update(dict.fromkeys(range(debut, fin + 1), quotite / 100.0))
    return quotites


#: Les âges de début qu'un exemple essaie à la fois, quand il cherche celui
#: qui rend son nombre de trimestres : une demande au pont par paquet, où
#: chaque essai se liquide sur la carrière que le portage bâtit de ses options
#: (``pont.CarriereSimple``), sans qu'elle passe le pont.
PAQUET_DE_DEBUTS = 8


def _rendu(droit, *appel):
    """Ce que rend un appel du droit (``pont.droit``), que le portage ne doit
    pas refuser."""
    lus, refus = droit({"rendu": appel})
    assert refus == {}, refus
    return lus["rendu"]


def _carriere_exemple(exemple: dict, decalage_mois: int = 0, sans_enfants: bool = False,
                      droit=droit_et_refait):
    """La carrière que l'exemple décrit, liquidée au mois voulu.

    Une seule affiliation, un salaire constant ou un profil, et — quand
    l'exemple ne donne que son nombre de trimestres — l'âge d'entrée qui rend
    exactement ce nombre à la liquidation, cherché au mois près.

    ``sans_enfants`` rejoue LA MÊME carrière sans aucun enfant. C'est ce qui
    rend la majoration de durée d'assurance mesurable sans la recalculer dans
    le test : la caisse publie le nombre de trimestres qu'elle ajoute, et
    l'écart entre les deux parcours doit valoir ce nombre. Un témoin qui
    l'emploie fixe son ``age_debut`` — sans quoi les deux parcours ne
    partiraient pas du même point.

    Le portage, qui fait foi, dit le mois d'où les âges se comptent, bâtit la
    carrière (``simulateur.carriere_simple``) et la liquide
    (``scenario_actuel.calculer``), par le pont : par défaut, le jumeau Python
    refait chaque appel au bit près (``droit_et_refait``). La carrière revient
    en Python (``pont.carriere_des_donnees``), où des grandeurs la lisent
    encore ; le résultat est celui du pont (``pont.actuel_des_donnees``).
    """
    c = exemple["carriere"]
    naissance, jour = _naissance(c["naissance"])
    liquidation = _mois(c["liquidation"]).plus_mois(decalage_mois)
    # L'âge au départ se compte depuis le mois d'où les âges se comptent, que
    # le jour déclaré ou présumé désigne : c'est la date d'effet qui est
    # publiée, et la carrière doit y retomber.
    origine = _rendu(droit, "calendrier.origine_des_ages", naissance,
                     jour if jour is not None
                     else _rendu(droit, "chronologie.valeur", "jour_de_naissance"))
    age = (liquidation.rang - origine.rang) / 12.0
    communs = dict(
        annee_naissance=naissance.annee, sexe=c.get("sexe", "H"),
        affiliation=c["affiliation"], age_liquidation=age,
        mois_naissance=naissance.mois, jour_naissance=jour,
        niveau_salaire=float(c.get("niveau_salaire", 1.0)),
        profil_carriere=c.get("profil_carriere", "ascendant"),
        nombre_enfants=0 if sans_enfants else int(c.get("nombre_enfants", 0)),
        naissances_enfants=() if sans_enfants else tuple(
            str(jour) for jour in c.get("naissances_enfants") or ()),
        interruptions={int(k): v for k, v in (c.get("interruptions") or {}).items()},
        # Le temps partiel, comme le formulaire l'écrit : « 2000:2009:80 ».
        temps_partiel=_quotites(str(c.get("temps_partiel") or "")),
    )
    if "conjoint" in c:
        # Le conjoint et le décès, comme la saisie les déclare : le sexe du
        # conjoint est l'autre que celui de l'assuré s'il n'est pas dit.
        communs["conjoint"] = {
            "naissance": str(c["conjoint"]),
            "sexe": c.get("conjoint_sexe") or ("H" if communs["sexe"] == "F" else "F"),
            "mariage": None if c.get("mariage") is None else str(c["mariage"]),
            "ressources": c.get("ressources_conjoint"),
            "invalidite": (None if c.get("conjoint_invalidite") is None
                           else str(c["conjoint_invalidite"])),
            "revenus_d_activite": c.get("activite_conjoint"),
            "fin_d_activite": (None if c.get("activite_conjoint_fin") is None
                               else str(c["activite_conjoint_fin"])),
            # Les variations, comme les interruptions, en table : date → montant.
            "variations_d_activite": [
                (str(jour), float(montant))
                for jour, montant in (c.get("activite_conjoint_variations") or {}).items()],
            "nouvelle_union": c.get("nouvelle_union"),
            "ressources_du_nouveau_conjoint": c.get("ressources_nouveau_conjoint"),
            "nouvelle_union_depuis": (None if c.get("nouvelle_union_depuis") is None
                                      else str(c["nouvelle_union_depuis"])),
            "nouvelle_union_fin": (None if c.get("nouvelle_union_fin") is None
                                   else str(c["nouvelle_union_fin"])),
            "variations_du_nouveau_conjoint": [
                (str(jour), float(montant)) for jour, montant
                in (c.get("ressources_nouveau_conjoint_variations") or {}).items()],
            "retraite": (None if c.get("conjoint_retraite") is None
                         else str(c["conjoint_retraite"])),
        }
        communs["deces"] = None if c.get("deces") is None else str(c["deces"])
    if "emploi_retraite" in c:
        # L'activité après le départ, dite par ses mois comme la liquidation :
        # ses âges se comptent du même mois d'origine.
        emploi = c["emploi_retraite"]
        communs["emploi_retraite"] = {
            "age": (_mois(emploi["debut"]).rang - origine.rang) / 12.0,
            "fin": (_mois(emploi["fin"]).rang - origine.rang) / 12.0,
            "affiliation": emploi.get("affiliation", c["affiliation"]),
            "niveau_salaire": float(emploi.get("niveau_salaire",
                                               c.get("niveau_salaire", 1.0))),
            "employeur": emploi.get("employeur", "autre"),
        }
    def age_du_mois(texte: str) -> float:
        """L'âge d'un mois, compté comme un début d'activité : depuis le
        mois de naissance."""
        return (_mois(texte).rang - naissance.rang) / 12.0

    if "etranger" in c:
        # La carrière hors de France, comme la saisie la déclare : chaque
        # période datée comme un début d'activité, salariée quand l'exemple
        # ne dit pas son activité.
        communs["etranger"] = {
            "periodes": [{"pays": periode["pays"], "debut": age_du_mois(periode["debut"]),
                          "fin": age_du_mois(periode["fin"]),
                          "activite": periode.get("activite", "salariee")}
                         for periode in c["etranger"]],
            "pensions": [], "residence": c.get("residence")}
    if any(cle in c for cle in ("inaptitude", "pension_d_invalidite", "radiation_invalidite",
                                "handicap")):
        # L'invalidité, l'inaptitude et l'incapacité permanente, comme la
        # saisie les déclare : la pension d'invalidité, la radiation et
        # l'incapacité datées comme un début d'activité, depuis le mois de
        # naissance.
        communs["invalidite"] = {
            "pension": (age_du_mois(c["pension_d_invalidite"])
                        if "pension_d_invalidite" in c else None),
            "inaptitude": bool(c.get("inaptitude")),
            "radiation": None if "radiation_invalidite" not in c else {
                "age": age_du_mois(c["radiation_invalidite"]),
                "imputable": bool(c.get("invalidite_imputable")),
                "taux": c.get("taux_invalidite")},
            "handicap": age_du_mois(c["handicap"]) if "handicap" in c else None,
        }
    if "age_debut" in c or "debut" in c:
        # Le début de la carrière en France, à un âge ou à un mois : celui
        # d'une carrière qui commence hors de France se date.
        debut = (float(c["age_debut"]) if "age_debut" in c else age_du_mois(c["debut"]))
        options = dict(communs, age_debut=debut)
        lus, refus = droit({
            "carriere": ("simulateur.carriere_simple", pont.SIMULATEUR, options),
            "resultat": ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple(options)),
        })
        assert refus == {}, refus
        return pont.carriere_des_donnees(lus["carriere"]), lus["resultat"]
    cible = int(c["trimestres_valides"])
    base = age - cible / 4.0
    debuts = [debut for debut in (round(base + k / 12.0, 6) for k in range(-16, 17))
              if debut >= 14]
    # Les essais dans l'ordre, par paquets : le premier qui rend les trimestres
    # de l'exemple est la carrière, comme un essai après l'autre.
    for rang in range(0, len(debuts), PAQUET_DE_DEBUTS):
        essais = debuts[rang:rang + PAQUET_DE_DEBUTS]
        liquidees, refus = droit({str(debut): (
            "scenario_actuel.calculer", pont.MOTEUR,
            pont.CarriereSimple(dict(communs, age_debut=debut))) for debut in essais})
        assert refus == {}, refus
        for debut in essais:
            if liquidees[str(debut)]["trimestres_valides"] == cible:
                return pont.carriere_des_donnees(_rendu(
                    droit, "simulateur.carriere_simple", pont.SIMULATEUR,
                    dict(communs, age_debut=debut))), liquidees[str(debut)]
    raise AssertionError(f"{exemple['id']} : aucune carrière ne donne {cible} trimestres")


def _mesurer(simulateur: Simulateur, exemple: dict, carriere, resultat, cle: str,
             droit=droit_et_refait):
    """Ce que le scénario 1 rend pour une grandeur du témoin, écrit comme le
    témoin l'écrit : c'est ce qui se compare à la valeur publiée, et, pour un
    écart connu, à la valeur que le modèle rendait quand on l'a déclaré. Les
    grandeurs passées au pont s'y mesurent (``droit``) ; par défaut, le jumeau
    Python refait chaque appel au bit près (``droit_et_refait``)."""
    actuel = simulateur.scenario_actuel
    if cle in ("trimestres_requis", "trimestres_valides", "taux_liquidation",
               "motif_ouverture", "liquidation_ouverte"):
        return resultat[cle]
    if cle == "age_ouverture":
        return _rendu(droit, "ouvrir.age_ouverture_droit", pont.MOTEUR, carriere)
    if cle == "date_age_legal":
        atteint = carriere.date_naissance.plus_mois(_rendu(
            droit, "calendrier.en_mois",
            _rendu(droit, "ouvrir.age_ouverture_droit", pont.MOTEUR, carriere)))
        return f"{atteint.annee}-{atteint.mois:02d}"
    if cle == "date_effet_au_plus_tot":
        # Le premier jour d'un mois où l'âge légal est atteint : celui qui
        # suit l'anniversaire, ou celui-ci pour qui est né un 1er (R. 351-37).
        effet = _rendu(droit, "carriere.date_de_l_age", carriere,
                       _rendu(droit, "ouvrir.age_ouverture_droit", pont.MOTEUR, carriere))
        return f"{effet.annee}-{effet.mois:02d}"
    if cle == "bonifications_des_emplois":
        # Les trimestres que chaque fiche des bonifications de service ajoute
        # aux services liquidés, telles que l'étape des durées les écrit.
        return dict(_rendu(droit, "releve.construire.durees.emplois", pont.MOTEUR, carriere))
    if cle == "services_liquidables":
        # Les trimestres de services que chaque régime nommé liquide, au
        # décompte final (R. 26), tels que l'étape des durées les écrit.
        return {regime: _rendu(droit, "releve.construire.durees.services_liquidables",
                               pont.MOTEUR, carriere, (regime,))
                for regime in exemple["attendu"][cle]}
    if cle == "trimestres_de_majoration_enfants":
        # La caisse publie le nombre de trimestres qu'elle ajoute par
        # enfant ; le test le mesure en rejouant la MÊME carrière sans
        # enfant. C'est un écart, pas un total : il ne dépend ni de l'âge
        # d'entrée ni de la durée requise de la génération.
        _, sans = _carriere_exemple(exemple, sans_enfants=True)
        return resultat["trimestres_valides"] - sans["trimestres_valides"]
    if cle == "trimestres_de_surcote_parentale":
        # Ceux que la surcote parentale compte dans l'année qui précède l'âge
        # légal, comme son avantage les dit ; zéro sans elle.
        parentale = next((a for a in resultat["avantages_appliques"]
                          if a["code"] == "surcote_parentale"), None)
        return 0 if parentale is None else int(
            re.search(r"pour (\d+) trimestre", parentale["detail"]).group(1))
    if cle == "majoration_enfants_sur_pensions":
        # L'assiette de la majoration pour enfants, mesurée sur ce que le
        # modèle sert : la circulaire dit qu'elle porte sur la retraite
        # TELLE QUE CALCULÉE, surcote comprise. Appliquer les 10 % à la
        # pension d'avant la surcote rendrait ici moins que le taux publié.
        #
        # Et sur la pension du RÉGIME DE BASE, dont la caisse publie
        # l'exemple, non sur le total : le témoin divisait la majoration de
        # tous les régimes par toutes les pensions, et ne valait 10 % que
        # parce que le modèle servait aussi 10 % à tous les points de
        # l'Agirc-Arrco — ce que l'accord ne fait pas (5 % aux points Arrco
        # de 1999 à 2011).
        majoration = next(
            (a for a in resultat["avantages_appliques"]
             if a["code"] == "majoration_enfants"), None)
        if majoration is None:
            return "aucune majoration pour enfants servie"
        base = {p["regime"]: p["montant"] for p in resultat["pensions_par_regime"]
                if p["type_calcul"] == "annuites"}
        part = sum(montant for regime, montant in majoration["par_regime"]
                   if regime in base)
        return part / sum(base.values())
    if cle == "majorations_enfants_des_regimes":
        # La majoration que chaque régime sert, rapportée à SA pension : le
        # barème propre d'une complémentaire, que la caisse publie en
        # pourcentage de ses points (l'Ircantec, article 15 de son arrêté).
        majoration = next(
            (a for a in resultat["avantages_appliques"]
             if a["code"] == "majoration_enfants"), None)
        if majoration is None:
            return "aucune majoration pour enfants servie"
        pensions = {p["regime"]: p["montant"] for p in resultat["pensions_par_regime"]}
        return {regime: montant / pensions[regime]
                for regime, montant in majoration["par_regime"] if pensions.get(regime)}
    if cle == "non_ouverte_un_trimestre_plus_tot":
        _, plus_tot = _carriere_exemple(exemple, decalage_mois=-3)
        return plus_tot["motif_ouverture"] == "non_ouverte"
    if cle in ("trimestres_handicap_requis", "trimestres_valides_handicap_requis"):
        # La durée cotisée — et validée, quand la version l'exige — que le
        # départ anticipé des assurés handicapés demande à cette génération,
        # pour cet âge, à cette date d'effet : ce que le simulateur annonce.
        exigences = _rendu(droit, "invalidite.exigences_du_handicap", pont.MOTEUR, carriere,
                           resultat["trimestres_requis"])
        if exigences is None:
            return "aucune exigence à cette date ni à cet âge"
        return exigences[1] if cle == "trimestres_handicap_requis" else exigences[2]
    if cle in ("coefficient_majoration_handicap", "majoration_handicap_ecretee"):
        # La majoration du départ des assurés handicapés au régime général,
        # telle que la formule affichée l'écrit : son coefficient, et si la
        # pension entière l'écrête.
        detail = next(p["detail"] for p in resultat["pensions_par_regime"]
                      if p["regime"] == "regime_general")
        lu = re.search(r"majoration des assurés handicapés ([0-9.]+)( écrêtée)?", detail)
        if cle == "coefficient_majoration_handicap":
            return float(lu.group(1)) if lu else "aucune majoration servie"
        return bool(lu and lu.group(2))
    if cle == "annees_du_salaire_annuel_moyen":
        # Le nombre des meilleures années que le salaire annuel moyen du
        # régime général retient, celui de la pension proratisée compris :
        # celui que son détail écrit quand une répartition l'a réduit.
        detail = next(p["detail"] for p in resultat["pensions_par_regime"]
                      if p["regime"] == "regime_general")
        reduit = re.search(r"(\d+) années au plus au salaire annuel moyen", detail)
        if reduit:
            return int(reduit.group(1))
        return _rendu(droit, "liquider.nombre_d_annees_retenues", pont.MOTEUR,
                      pont.Periode("regime_general", carriere.annee_liquidation), carriere,
                      carriere.annee_naissance)
    if cle == "pension_base_sur_sam":
        sam = _rendu(droit, "liquider.salaire_de_reference", pont.MOTEUR, "regime_general",
                     carriere, pont.Periode("regime_general", carriere.annee_liquidation),
                     carriere.annee_liquidation, True, carriere.annee_naissance)
        base = next(p["montant"] for p in resultat["pensions_par_regime"]
                    if p["regime"] == "regime_general")
        return base / sam
    if cle == "pension_base_sur_plafond":
        # La pension du régime général rapportée au plafond de l'année : celle
        # que le maximum ramène, à sa part du plafond (fiche
        # ``pension_maximale_regime_general``).
        base = next(p["montant"] for p in resultat["pensions_par_regime"]
                    if p["regime"] == "regime_general")
        return base / _rendu(droit, "scenario_actuel.macro.plafond_securite_sociale",
                             pont.MOTEUR, carriere.annee_liquidation)
    if cle == "coefficients_des_regimes":
        # Le coefficient d'anticipation ou de majoration qu'une section
        # applique à sa complémentaire, tel que la formule affichée
        # l'écrit ; aucun coefficient écrit vaut 1.
        coefficients = {}
        for p in resultat["pensions_par_regime"]:
            lu = re.search(r"coefficient (?:d'anticipation|de majoration) ([0-9.]+)",
                           p["detail"])
            coefficients[p["regime"]] = float(lu.group(1)) if lu else 1.0
        return coefficients
    if cle == "pension_regime_general_mensuelle":
        base = next(p["montant"] for p in resultat["pensions_par_regime"]
                    if p["regime"] == "regime_general")
        return base / 12
    if cle == "pensions_annuelles_des_regimes":
        # La pension annuelle brute d'un régime nommé : ce que publie un
        # régime dont la pension ne tient ni à un taux ni à un salaire.
        return {p["regime"]: p["montant"] for p in resultat["pensions_par_regime"]}
    if cle == "valeurs_de_service_au_jour":
        # La valeur de service qu'une pension prenant effet au départ de
        # l'exemple reçoit, régime par régime, fusions comprises : celle du
        # jour, non celle du 31 décembre (circulaire Agirc-Arrco 2020-02-DRJ).
        return {regime: _rendu(droit, "liquider.valeur_du_point", pont.MOTEUR, regime,
                               carriere.date_liquidation)[0]
                for regime in exemple["attendu"][cle]}
    if cle == "points_de_l_annee":
        # Les points qu'un salaire de l'année acquiert, tels que la fédération
        # les calcule dans ses guides : l'exemple donne le salaire de l'année
        # (`releve`, année : salaire), la grandeur les points de chaque régime,
        # une valeur par période qui en crédite — la tranche 1, puis la 2. Le
        # portage bâtit la carrière du relevé, qui revient en Python.
        from retraite_notionnelle.carriere import LigneRelevee

        c = exemple["carriere"]
        annee = int(exemple["attendu"][cle]["annee"])
        naissance, _ = _naissance(c["naissance"])
        depart = _mois(c["liquidation"])
        lignes = [LigneRelevee(int(a), c["affiliation"], float(revenu))
                  for a, revenu in c["releve"].items()]
        construite = pont.carriere_des_donnees(_rendu(
            droit, "simulateur.carriere_releve", pont.SIMULATEUR, dict(
                annee_naissance=naissance.annee, sexe=c.get("sexe", "H"), releve=lignes,
                age_liquidation=(depart.annee - naissance.annee
                                 + (depart.mois - naissance.mois) / 12),
                mois_naissance=naissance.mois)))
        mesure: dict = {"annee": annee}
        for code, a, points, _ in _rendu(droit, "releve.construire.droits.points", pont.MOTEUR,
                                         construite):
            if a == annee and points > 0:
                mesure.setdefault(code, []).append(points)
        return mesure
    if cle == "cotisation_agirc_de_l_annee":
        # La cotisation Agirc d'une année, part de l'assuré et cotisation
        # entière : ce que le droit de l'année prélevait, tel que le compte
        # notionnel le reçoit sous ses deux conventions. Le scénario 1 n'a pas
        # de cotisation en euros ; il n'en tire que des points.
        from retraite_notionnelle.config import PartCotisation
        from retraite_notionnelle.moteur.compte import ConstructeurCompte

        annee = int(exemple["attendu"][cle]["annee"])
        mesure = {"annee": annee}
        for nom, part in (("salariale", PartCotisation.SALARIALE),
                          ("totale", PartCotisation.TOTALE)):
            constructeur = ConstructeurCompte(
                simulateur.macro, simulateur.catalogue, simulateur.affiliations,
                simulateur.indexation, simulateur.parametres.avec(part_cotisation=part))
            versees = dict(constructeur.cotisation_annuelle(carriere, annee).par_regime)
            mesure[nom] = versees.get("agirc", 0.0)
        return mesure
    if cle == "cotisations_de_la_fiche_de_paie":
        # Les lignes de retraite de la fiche de paie du site, sur le revenu et
        # l'année de l'exemple, part de l'assuré : ce que la caisse appelle.
        from retraite_notionnelle.remuneration import fiche_depuis_brut

        valeur = exemple["attendu"][cle]
        annee, revenu = int(valeur["annee"]), float(valeur["revenu"])
        fiche = fiche_depuis_brut(
            simulateur.parametres.racine_donnees, simulateur.macro, simulateur.catalogue,
            simulateur.affiliations, exemple["carriere"]["affiliation"], annee, revenu)
        mesure = {"annee": annee, "revenu": revenu}
        for ligne in () if fiche is None else fiche.lignes:
            if ligne.retraite:
                mesure[ligne.code] = ligne.salarie
        return mesure
    if cle == "departs":
        # Les départs que l'échéancier inscrit quand les régimes ne liquident
        # pas tous au départ déclaré, chacun « AAAA-MM-JJ motif » ; aucun
        # pour un départ unique.
        return [f"{d['date_effet']} {d['motif']}" for d in resultat["departs"]]
    if cle == "dates_d_effet_de_la_reversion":
        # La réversion telle que l'échéancier la liquide au décès de l'assuré :
        # la date d'effet de chaque régime du défunt.
        echeancier = Echeancier(simulateur)
        echeancier.parcourir(carriere)
        if echeancier.reversion is None:
            return "aucune réversion liquidée"
        return {r.regime: r.date_effet for r in echeancier.reversion.regimes}
    if cle in ("dates_de_revision_de_la_reversion",
               "dates_de_premiere_revision_de_la_reversion",
               "dates_de_derniere_revision_de_la_reversion"):
        # La même réversion, revue quand la retraite du survivant suit sa date
        # d'effet, ou que ses ressources varient : le jour de sa dernière
        # révision, ou de la première, et celui d'où rien ne la revoit plus
        # (R. 353-1-1).
        echeancier = Echeancier(simulateur)
        echeancier.parcourir(carriere)
        if echeancier.reversion is None:
            return "aucune réversion liquidée"
        if cle == "dates_de_premiere_revision_de_la_reversion":
            return {r.regime: r.revisions[0][0] if r.revisions else None
                    for r in echeancier.reversion.regimes}
        champ = ("revision_effet" if cle == "dates_de_revision_de_la_reversion"
                 else "derniere_revision")
        return {r.regime: getattr(r, champ) for r in echeancier.reversion.regimes}
    if cle == "reversions_ecretees_mensuelles":
        # L'exemple donne la réversion d'avant le plafond, pas la carrière du
        # défunt : le test prête à chaque régime nommé la pension qui la rend,
        # au taux de la version que le modèle choisit, et le modèle l'écrête.
        avant = exemple["carriere"]["reversions_avant_plafond_mensuelles"]
        annee = int(str(exemple["carriere"]["deces"])[:4])
        sonde = reversion(actuel, [(regime, 1.0, Fiabilite.HAUTE) for regime in avant],
                          carriere, annee)
        taux = {r.regime: r.taux for r in sonde.regimes}
        servie = reversion(actuel, [(regime, 12 * montant / taux[regime], Fiabilite.HAUTE)
                                    for regime, montant in avant.items()], carriere, annee)
        return {r.regime: r.montant / 12 for r in servie.regimes}
    if cle == "ressources_retenues_mensuelles":
        # L'exemple donne les ressources que la caisse retient à côté de la
        # réversion, par mois : celles que le modèle retient sous le plafond de
        # chaque régime, à la date d'effet qu'ouvre le décès de l'exemple.
        pensions = exemple["carriere"]["pensions_du_defunt_mensuelles"]
        annee = int(str(exemple["carriere"]["deces"])[:4])
        servie = reversion(actuel, [(regime, 12 * montant, Fiabilite.HAUTE)
                                    for regime, montant in pensions.items()], carriere, annee)
        return {r.regime: r.ressources_retenues / 12 for r in servie.regimes}
    if cle == "ressources_retenues_mensuelles_aux_revisions":
        # Les mêmes, à chacune des révisions de la réversion de chaque régime,
        # par mois.
        pensions = exemple["carriere"]["pensions_du_defunt_mensuelles"]
        annee = int(str(exemple["carriere"]["deces"])[:4])
        servie = reversion(actuel, [(regime, 12 * montant, Fiabilite.HAUTE)
                                    for regime, montant in pensions.items()], carriere, annee)
        return {r.regime: {jour: ressources / 12 for jour, ressources in r.ressources_des_revisions}
                for r in servie.regimes}
    if cle == "reversions_mensuelles":
        # L'exemple donne les pensions du défunt, comme le simulateur les
        # demande, et la réversion qu'il en tire : le test les prête au défunt,
        # et le modèle y applique ses taux, ses conditions et son plafond.
        pensions = exemple["carriere"]["pensions_du_defunt_mensuelles"]
        annee = int(str(exemple["carriere"]["deces"])[:4])
        servie = reversion(actuel, [(regime, 12 * montant, Fiabilite.HAUTE)
                                    for regime, montant in pensions.items()], carriere, annee)
        return {r.regime: r.montant / 12 for r in servie.regimes}
    if cle == "reversions_au_maximum_mensuelles":
        # L'exemple donne la pension du défunt, ramenée au maximum des
        # pensions, surcote en sus, et ce qu'elle était avant lui : le test les
        # lui prête, et le modèle reverse la pension d'avant le maximum, sous
        # son propre maximum de l'année, la surcote en sus.
        pensions = exemple["carriere"]["pensions_du_defunt_mensuelles"]
        avant = exemple["carriere"]["pensions_avant_maximum_mensuelles"]
        surcotes = exemple["carriere"].get("surcotes_mensuelles") or {}
        annee = int(str(exemple["carriere"]["deces"])[:4])
        maxima = {regime: (12 * (avant[regime] - pensions[regime]
                                 + surcotes.get(regime, 0.0)),
                           12 * surcotes.get(regime, 0.0), 1.0)
                  for regime in avant}
        servie = reversion(actuel, [(regime, 12 * montant, Fiabilite.HAUTE)
                                    for regime, montant in pensions.items()], carriere, annee,
                           maxima=maxima)
        return {r.regime: r.montant / 12 for r in servie.regimes}
    if cle == "majoration_exceptionnelle_mensuelle":
        # La majoration exceptionnelle des petites pensions, servie le mois où
        # elle est due : « faire vivre » la calcule à l'échéance de 2023, où
        # rien ne l'a encore revalorisée.
        from retraite_notionnelle.revalorisation import faire_vivre

        # Le résultat Python de la même carrière, que « faire vivre » lit,
        # tant qu'il ne passe pas le pont (lot B).
        majorations = faire_vivre(simulateur, carriere, actuel.calculer(carriere),
                                  2023).majorations
        if not majorations:
            return "aucune majoration exceptionnelle"
        return sum(m.servie for m in majorations)
    if cle == "minimum_vieillesse_mensuel":
        # L'exemple donne les revenus du couple, pas les carrières : le test
        # prête à l'assuré la pension de l'exemple — le conjoint a déjà ses
        # ressources —, et lit l'allocation du foyer à la date de l'exemple.
        from retraite_notionnelle.droit.foyer import foyer_et_net

        jour = str(exemple["carriere"]["date_du_foyer"])
        pension = 12 * float(exemple["carriere"]["pensions_au_foyer_mensuelles"])
        foyer = foyer_et_net(actuel, carriere.personne, jour, int(jour[:4]), pension, True,
                             carriere=carriere)
        return foyer.minimum_vieillesse / 12
    if cle == "plafonds_des_nouvelles_pensions":
        echeancier = Echeancier(simulateur)
        echeancier.parcourir(carriere)
        droits = echeancier.au_depart.droits_apres_depart
        if droits is None:
            return "aucune activité après le départ"
        return {p.regime: p.plafond for p in droits.pensions if p.plafond is not None}
    if cle == "pension_et_rente_d_invalidite_sur_traitement":
        # L'exemple donne le traitement et le taux de la pension, non la
        # carrière : le test les prête au calcul de la retraite pour
        # invalidité de la fonction publique de l'État, sous la version que
        # la radiation choisit, et lit la rente dans ce que le détail en dit.
        # Le portage enchaîne la version et la pension : la version, une fiche
        # du paquet, ne passe pas le pont.
        c = exemple["carriere"]
        traitement = 12.0 * float(c["traitement_mensuel"])
        radiation = carriere.radiation_pour_invalidite
        servie = _rendu(
            droit, "invalidite.retraite_pour_invalidite.pension_du_fonctionnaire_invalide",
            pont.MOTEUR, "fonction_publique_etat", carriere,
            float(c["taux_de_la_pension"]) * traitement, traitement,
            None if radiation is None else radiation.date.annee)
        if servie is None:
            return "aucune retraite pour invalidité"
        total, detail = servie
        lu = re.search(r"rente viagère d'invalidité de ([0-9,.]+) €", detail)
        rente = float(lu.group(1).replace(",", "")) if lu else 0.0
        return {"pension": (total - rente) / traitement, "rente": rente / traitement,
                "total": total / traitement}
    if cle == "prestation_rafp":
        # L'ERAFP publie des points et une date d'effet, son simulateur les
        # prend : le test prête ces points au RAFP, et la valeur de service
        # publiée. Le modèle dit l'âge légal qui ouvre le droit, puis, s'il est
        # atteint, le coefficient de majoration, la forme de la prestation —
        # rente, capital en une fois ou en deux — et ses montants. La
        # retraite de base est le départ, sauf quand l'exemple la date
        # (`retraite_de_base`) : le fractionnement en compte les mois.
        c = exemple["carriere"]
        points, valeur = float(c["points_rafp"]), float(c["valeur_de_service_rafp"])
        legal = _rendu(droit, "departs.age_legal", pont.MOTEUR, carriere)
        effet = carriere.date_liquidation
        if effet < _rendu(droit, "carriere.date_de_l_age", carriere, legal):
            return {"forme": "non_ouverte", "age_legal": legal}
        age = carriere.age_liquidation
        coefficient = _rendu(droit, "liquider.majoration_rafp", age, effet)
        rente = points * coefficient * valeur
        seuil = _rendu(droit, "periode.capital_seuil_points", pont.Periode("rafp", effet.annee))
        ecart = (effet.rang - _mois(str(c["retraite_de_base"])).rang
                 if c.get("retraite_de_base")
                 else _rendu(droit, "liquider.mois_apres_le_depart", carriere, age))
        versee = _rendu(droit, "liquider.prestation_rafp", rente, points, seuil, age, effet,
                        ecart)
        mesure = {"forme": versee["forme"], "age_legal": legal, "coefficient": coefficient,
                  "rente_annuelle": rente, "rente_mensuelle": rente / 12}
        if versee["forme"] != "rente":
            mesure.update(conversion=versee["conversion"], capital=versee["capital"])
        if versee["forme"] == "capital_fractionne":
            mesure["premiere_fraction"] = versee["premiere_fraction"]
        return mesure
    if cle in ("deductions_annuelles_du_cumul", "mois_sans_pension_du_cumul",
               "plafond_mensuel_du_cumul", "cumul_integral_depuis"):
        resultat_cumul = _cumul_exemple(simulateur, exemple, carriere)
        if resultat_cumul is None:
            return "aucune activité après le départ"
        if cle == "cumul_integral_depuis":
            depuis = resultat_cumul.integral_depuis
            return ("jamais pendant l'activité" if depuis is None
                    else f"{depuis.annee}-{depuis.mois:02d}")
        if cle == "deductions_annuelles_du_cumul":
            annee = min(int(a) for a in exemple["carriere"]["revenus_apres_depart"])
            return {regime: sum(p.reduction * t.mois for t in resultat_cumul.tranches
                                if t.debut.annee == annee
                                for p in t.par_regime if p.regime == regime)
                    for regime in exemple["attendu"][cle]}
        if cle == "mois_sans_pension_du_cumul":
            bases = {"base", "integre"}
            return [f"{mois.annee}-{mois.mois:02d}"
                    for t in resultat_cumul.tranches
                    if all(p.statut == "non_due" for p in t.par_regime
                           if simulateur.catalogue[p.regime].etage in bases)
                    for mois in (t.debut.plus_mois(k) for k in range(t.mois))]
        premiere = resultat_cumul.tranches[0]
        base = next((p for p in premiere.par_regime if p.regime == "regime_general"), None)
        return base.plafond if base is not None and base.plafond is not None else (
            "aucun plafond au premier mois")
    raise AssertionError(f"grandeur inconnue dans le témoin : {cle}")


def _cumul_exemple(simulateur: Simulateur, exemple: dict, carriere):
    """Le cumul emploi-retraite de l'exemple. Quand il donne la pension et le
    revenu, non la carrière, le test prête à chaque régime nommé sa pension, et à
    chaque année son revenu brut ; sinon, l'échéancier le calcule."""
    from dataclasses import replace

    from retraite_notionnelle.droit import cumul

    c = exemple["carriere"]
    liquidee = carriere
    revenus = {int(a): float(m) for a, m in (c.get("revenus_apres_depart") or {}).items()}
    if revenus:
        carriere = replace(carriere, lignes_apres_depart=tuple(
            replace(ligne, revenu=revenus.get(ligne.annee, ligne.revenu))
            for ligne in carriere.lignes_apres_depart))
    pensions = c.get("pensions_annuelles_en_cumul")
    if pensions is None:
        echeancier = Echeancier(simulateur)
        echeancier.parcourir(carriere)
        return echeancier.au_depart.cumul
    pretees = {regime: float(montant) for regime, montant in pensions.items()}
    # Le résultat Python de la carrière liquidée, que le cumul lit, tant qu'il
    # ne passe pas le pont (lot B).
    return cumul.cumuler(simulateur.scenario_actuel, carriere,
                         simulateur.scenario_actuel.calculer(liquidee),
                         lambda annee: (dict(pretees), 0.0),
                         simulateur.parametres.annee_courante)



def _exemples_de_chaque_forme() -> list[dict]:
    """Un exemple de chaque forme de carrière que :func:`_carriere_exemple`
    bâtit : un âge de début, un début daté, un nombre de trimestres à
    retrouver, un conjoint et un décès, un emploi après le départ, une
    carrière hors de France, une invalidité, du temps partiel, des
    interruptions, des enfants."""
    formes = (
        lambda c: "age_debut" in c,
        lambda c: "debut" in c,
        lambda c: "age_debut" not in c and "debut" not in c,
        lambda c: "conjoint" in c,
        lambda c: "emploi_retraite" in c,
        lambda c: "etranger" in c,
        lambda c: any(cle in c for cle in ("inaptitude", "pension_d_invalidite",
                                           "radiation_invalidite", "handicap")),
        lambda c: bool(c.get("temps_partiel")),
        lambda c: bool(c.get("interruptions")),
        lambda c: bool(c.get("nombre_enfants")),
    )
    exemples = _charger_exemples()
    return [next(e for e in exemples if forme(e["carriere"])) for forme in formes]


def test_les_carrieres_des_exemples_se_batissent_au_portage_sans_les_jumeaux_python(
        monkeypatch):
    """La carrière de chaque exemple, de chaque forme, se bâtit au portage
    (``simulateur.carriere_simple``), depuis le mois d'où ses âges se comptent,
    et s'y liquide (``scenario_actuel.calculer``) : les jumeaux Python, qu'on
    empêche ici de calculer, n'y entrent pas."""
    from retraite_notionnelle import calendrier, chronologie

    exemples = _exemples_de_chaque_forme()
    attendus = {exemple["id"]: _carriere_exemple(exemple) for exemple in exemples}
    _sans_les_jumeaux(monkeypatch, (Simulateur, "carriere_simple"),
                      (ScenarioActuel, "calculer"), (calendrier, "origine_des_ages"),
                      (chronologie, "valeur"))
    for exemple in exemples:
        carriere, resultat = _carriere_exemple(exemple, droit=pont.droit)
        attendue, attendu = attendus[exemple["id"]]
        assert pont.carriere_en_donnees(carriere) == pont.carriere_en_donnees(attendue)
        assert resultat == attendu, exemple["id"]


def _mesures_sans_les_jumeaux(simulateur, monkeypatch, cles: tuple[str, ...], *jumeaux,
                              choisis: tuple[str, ...] = ()):
    """Sur le premier exemple qui publie chacune des grandeurs ``cles`` — ou sur
    chacun des exemples ``choisis``, qui les publient —, ce que ``_mesurer`` en
    rend par le pont seul (``pont.droit``), les jumeaux Python nommés empêchés
    de calculer, et ce qu'il en rend sous leur contrôle (``droit_et_refait``) :
    les deux doivent être les mêmes."""
    exemples = _charger_exemples()
    paires = ([(e, cle) for e in exemples if e["id"] in choisis for cle in cles
               if cle in e["attendu"]] if choisis
              else [(next(e for e in exemples if cle in e["attendu"]), cle) for cle in cles])
    mesures = []
    for exemple, cle in paires:
        carriere, resultat = _carriere_exemple(exemple)
        mesures.append((exemple, carriere, resultat, cle,
                        _mesurer(simulateur, exemple, carriere, resultat, cle)))
    _sans_les_jumeaux(monkeypatch, *jumeaux)
    return [((exemple["id"], cle), _mesurer(simulateur, exemple, carriere, resultat, cle,
                                             droit=pont.droit), attendue)
            for exemple, carriere, resultat, cle, attendue in mesures]


def test_l_ouverture_des_exemples_se_mesure_au_portage_sans_les_jumeaux_python(
        simulateur, monkeypatch):
    """L'âge d'ouverture du droit, le mois où il est atteint et la date d'effet
    au plus tôt se mesurent au portage (``ouvrir.age_ouverture_droit``,
    ``calendrier.en_mois``, ``carriere.date_de_l_age``) : les jumeaux Python,
    qu'on empêche ici de calculer, n'y entrent pas."""
    from retraite_notionnelle import calendrier

    for cas, lue, attendue in _mesures_sans_les_jumeaux(
            simulateur, monkeypatch, ("age_ouverture", "date_age_legal", "date_effet_au_plus_tot"),
            (ouvrir, "age_ouverture_droit"), (calendrier, "en_mois"),
            (Carriere, "date_de_l_age")):
        assert lue == attendue, cas


def test_la_liquidation_des_exemples_se_mesure_au_portage_sans_les_jumeaux_python(
        simulateur, monkeypatch):
    """Les années que retient le salaire annuel moyen, la pension rapportée à
    lui et au plafond, la valeur de service au jour du départ se mesurent au
    portage (``liquider``, la période du régime, le plafond) : les jumeaux
    Python, qu'on empêche ici de calculer ou de lire, n'y entrent pas."""
    for cas, lue, attendue in _mesures_sans_les_jumeaux(
            simulateur, monkeypatch,
            ("annees_du_salaire_annuel_moyen", "pension_base_sur_sam",
             "pension_base_sur_plafond", "valeurs_de_service_au_jour"),
            (liquider, "nombre_d_annees_retenues"), (liquider, "salaire_de_reference"),
            (liquider, "valeur_du_point"), (CatalogueRegimes, "__getitem__"),
            (SerieAnnuelle, "__call__")):
        assert lue == attendue, cas


def test_la_prestation_du_rafp_se_mesure_au_portage_sans_les_jumeaux_python(
        simulateur, monkeypatch):
    """L'âge légal qui ouvre le RAFP, son coefficient de majoration, son seuil
    en points, les mois qui séparent la prestation de la retraite de base et sa
    forme — rente, capital en une fois ou en deux — se mesurent au portage :
    les jumeaux Python, qu'on empêche ici de calculer ou de lire, n'y entrent
    pas."""
    choisis = ("erafp_1964_effet_2027_04_6000_points", "erafp_1966_effet_2029_04_3000_points",
               "erafp_1966_effet_2031_01_3000_points", "erafp_1963_effet_2026_11_5000_points",
               "erafp_ra2022_alain_capital_apres_la_base")
    mesures = _mesures_sans_les_jumeaux(
        simulateur, monkeypatch, ("prestation_rafp",),
        (departs, "age_legal"), (liquider, "majoration_rafp"),
        (liquider, "mois_apres_le_depart"), (liquider, "prestation_rafp"),
        (Carriere, "date_de_l_age"), (CatalogueRegimes, "__getitem__"), choisis=choisis)
    assert {lue["forme"] for _, lue, _ in mesures} == {
        "rente", "non_ouverte", "capital", "capital_fractionne"}
    for cas, lue, attendue in mesures:
        assert lue == attendue, cas


def test_le_releve_des_exemples_se_mesure_au_portage_sans_les_jumeaux_python(
        simulateur, monkeypatch):
    """La carrière lue sur un relevé (``simulateur.carriere_releve``), les points
    que chaque régime y acquiert, de l'Ircantec et de l'Agirc-Arrco, sur une
    tranche ou deux, les services que chaque fiche des bonifications ajoute et
    les services liquidables d'un régime se mesurent au portage
    (``releve.construire``) : les jumeaux Python, qu'on empêche ici de
    calculer, n'y entrent pas."""
    from retraite_notionnelle.droit import releve

    choisis = ("ircantec_points_2024_deux_tranches", "ircantec_points_2019_base_documentaire",
               "aa_livret3_points_2023", "aa_livret3_points_2024_deux_tranches",
               "sre_militaire_radie_le_lendemain_de_ses_62_ans", "sre_temps_partiel_pierre")
    mesures = _mesures_sans_les_jumeaux(
        simulateur, monkeypatch,
        ("points_de_l_annee", "bonifications_des_emplois", "services_liquidables"),
        (releve, "construire"), (Carriere, "depuis_releve"), (Simulateur, "carriere_releve"),
        choisis=choisis)
    assert len(mesures) == len(choisis)
    for cas, lue, attendue in mesures:
        assert lue == attendue, cas


def test_l_invalidite_des_exemples_se_mesure_au_portage_sans_les_jumeaux_python(
        simulateur, monkeypatch):
    """Les durées que le départ des assurés handicapés exige, cotisée et
    validée, au régime général et dans la fonction publique, et la pension du
    fonctionnaire radié pour invalidité, portée au plancher ou servie avec sa
    rente, sous la version que la radiation choisit, se mesurent au portage :
    les jumeaux Python, qu'on empêche ici de calculer, n'y entrent pas."""
    choisis = ("ur_handicap_1961_59", "ur_handicap_1961_59_fonctionnaire",
               "sre_plancher_monsieur_g_65", "sre_plancher_monsieur_g_55",
               "sre_rente_viagere_monsieur_h")
    mesures = _mesures_sans_les_jumeaux(
        simulateur, monkeypatch,
        ("trimestres_handicap_requis", "trimestres_valides_handicap_requis",
         "pension_et_rente_d_invalidite_sur_traitement"),
        (invalidite, "exigences_du_handicap"), (invalidite, "retraite_pour_invalidite"),
        (invalidite, "pension_du_fonctionnaire_invalide"), choisis=choisis)
    assert len(mesures) == 6
    for cas, lue, attendue in mesures:
        assert lue == attendue, cas

#: Les grandeurs qui se comparent à une tolérance près ; les autres, à
#: l'égalité. ``age_ouverture`` prend la tolérance relative de pytest.
TOLERANCES = {
    "taux_liquidation": {"abs": 1e-6},
    "age_ouverture": {},
    "majoration_enfants_sur_pensions": {"abs": 1e-9},
    "majorations_enfants_des_regimes": {"abs": 1e-9},
    "pension_base_sur_sam": {"abs": 1e-9},
    "pension_base_sur_plafond": {"abs": 1e-9},
    "coefficients_des_regimes": {"abs": 1e-9},
    "pension_regime_general_mensuelle": {"abs": 0.05},
    # Tronquée au centime, comme la caisse la calcule.
    "majoration_exceptionnelle_mensuelle": {"abs": 1e-9},
    "pensions_annuelles_des_regimes": {"abs": 0.5},
    # Au dix-millième d'euro, que la fédération écrit.
    "valeurs_de_service_au_jour": {"abs": 5e-5},
    # Annuelle, quand la caisse publie douze mensualités arrondies au centime
    # (six centimes au plus) et que la fiche arrondit le partage entre salarié
    # et employeur au dix-millième : 0,3796 pour 6,24 % sur 16,44 %.
    "cotisation_agirc_de_l_annee": {"abs": 0.10},
    "reversions_ecretees_mensuelles": {"abs": 0.01},
    "ressources_retenues_mensuelles": {"abs": 0.01},
    "ressources_retenues_mensuelles_aux_revisions": {"abs": 0.01},
    "reversions_mensuelles": {"abs": 0.5},
    # La circulaire arrondit chaque part au centime, le modèle le total.
    "reversions_au_maximum_mensuelles": {"abs": 0.01},
    "deductions_annuelles_du_cumul": {"abs": 0.01},
    "plafond_mensuel_du_cumul": {"abs": 0.01},
    "plafonds_des_nouvelles_pensions": {"abs": 0.01},
    "pension_et_rente_d_invalidite_sur_traitement": {"abs": 1e-6},
    "coefficient_majoration_handicap": {"abs": 1e-9},
    # La fiche publie des mensuels au centime, que l'annuel divisé par douze
    # dépasse de moins d'un demi-centime : 19 442,21 / 12 = 1 620,184.
    "minimum_vieillesse_mensuel": {"abs": 0.005},
}


def _concorde(cle: str, mesure, valeur) -> bool:
    """La mesure du modèle vaut-elle la valeur écrite au témoin ?"""
    if cle in ("liquidation_ouverte", "non_ouverte_un_trimestre_plus_tot"):
        return mesure is bool(valeur)
    if cle in ("date_age_legal", "date_effet_au_plus_tot", "cumul_integral_depuis"):
        return mesure == f"{_mois(valeur).annee}-{_mois(valeur).mois:02d}"
    if isinstance(mesure, str) and cle in TOLERANCES:
        return False  # la mesure dit pourquoi elle n'en est pas une
    if cle == "majorations_enfants_des_regimes":
        # Un régime nommé que le modèle ne majore pas n'a pas de taux.
        return all(regime in mesure and mesure[regime] == pytest.approx(taux, abs=1e-9)
                   for regime, taux in valeur.items())
    if cle == "coefficients_des_regimes":
        # Un régime nommé que le modèle ne sert pas n'a pas de coefficient.
        return all(regime in mesure and mesure[regime] == pytest.approx(c, abs=1e-9)
                   for regime, c in valeur.items())
    if cle == "pensions_annuelles_des_regimes":
        # Un régime nommé que le modèle ne sert pas lui verse zéro.
        return all(mesure.get(regime, 0.0) == pytest.approx(montant, abs=0.5)
                   for regime, montant in valeur.items())
    if cle == "valeurs_de_service_au_jour":
        return all(mesure[regime] == pytest.approx(v, **TOLERANCES[cle])
                   for regime, v in valeur.items())
    if cle == "departs":
        return mesure == [str(depart) for depart in valeur]
    if cle in ("dates_d_effet_de_la_reversion", "dates_de_revision_de_la_reversion",
               "dates_de_premiere_revision_de_la_reversion",
               "dates_de_derniere_revision_de_la_reversion"):
        # Un régime nommé que la réversion ne liquide pas n'a pas de date.
        return not isinstance(mesure, str) and all(
            mesure.get(regime) == str(date) for regime, date in valeur.items())
    if cle in ("reversions_ecretees_mensuelles", "deductions_annuelles_du_cumul",
               "plafonds_des_nouvelles_pensions", "reversions_au_maximum_mensuelles",
               "ressources_retenues_mensuelles"):
        return all(mesure.get(regime, 0.0) == pytest.approx(montant, abs=0.01)
                   for regime, montant in valeur.items())
    if cle == "ressources_retenues_mensuelles_aux_revisions":
        # Seules se comparent les révisions que l'exemple date.
        return all(jour in mesure.get(regime, {})
                   and mesure[regime][jour] == pytest.approx(montant, abs=0.01)
                   for regime, revisions in valeur.items()
                   for jour, montant in revisions.items())
    if cle == "reversions_mensuelles":
        # Les simulateurs arrondissent à l'euro.
        return all(mesure.get(regime, 0.0) == pytest.approx(montant, abs=0.5)
                   for regime, montant in valeur.items())
    if cle == "pension_et_rente_d_invalidite_sur_traitement":
        # Seules se comparent les parts que l'exemple publie.
        return all(mesure[part] == pytest.approx(valeur[part], abs=1e-6) for part in valeur)
    if cle == "mois_sans_pension_du_cumul":
        return mesure == [str(mois) for mois in valeur]
    if cle == "prestation_rafp":
        # Seules se comparent les grandeurs que l'ERAFP publie ou que son
        # simulateur affiche : la forme à l'égalité, les coefficients et l'âge
        # au millionième, les montants au centime, qu'il arrondit.
        return mesure["forme"] == valeur["forme"] and all(
            grandeur in mesure and mesure[grandeur] == pytest.approx(
                attendue, abs=1e-6 if grandeur in ("coefficient", "conversion", "age_legal")
                else 0.0051)
            for grandeur, attendue in valeur.items() if grandeur != "forme")
    if cle == "points_de_l_annee":
        # Au centième, que les guides arrondissent ; chaque période dans
        # l'ordre où le régime la crédite. Au demi-point quand la source
        # arrondit au point (`arrondi: point`, l'Ircantec) ; un nombre seul est
        # le total des périodes, quand elle ne publie que lui.
        ecart = 0.5 if valeur.get("arrondi") == "point" else 0.0051
        return mesure["annee"] == int(valeur["annee"]) and all(
            sum(mesure.get(code, [])) == pytest.approx(points, abs=ecart)
            if isinstance(points, (int, float)) else
            len(mesure.get(code, [])) == len(points) and all(
                m == pytest.approx(p, abs=ecart) for m, p in zip(mesure[code], points))
            for code, points in valeur.items() if code not in ("annee", "arrondi"))
    if cle == "cotisation_agirc_de_l_annee":
        return mesure["annee"] == int(valeur["annee"]) and all(
            mesure[part] == pytest.approx(valeur[part], **TOLERANCES[cle])
            for part in ("salariale", "totale") if part in valeur)
    if cle == "cotisations_de_la_fiche_de_paie":
        # À l'euro, que la caisse arrondit : chaque ligne de retraite de la
        # fiche, et elles seules.
        return set(mesure) == set(valeur) and all(
            mesure[code] == pytest.approx(montant, abs=0.5)
            for code, montant in valeur.items())
    if cle in TOLERANCES:
        return mesure == pytest.approx(valeur, **TOLERANCES[cle])
    return mesure == valeur


def _confronter(simulateur: Simulateur, exemple: dict) -> list[tuple]:
    """Ce qui sépare le modèle du témoin : rien, s'il concorde.

    Une grandeur que l'exemple déclare en écart connu (``ecart_connu``) doit
    rendre la valeur déclarée pour le modèle : si elle rend la valeur publiée,
    l'écart est corrigé et sa déclaration se retire ; si elle rend autre
    chose, le résultat a changé, et c'est le diff du témoin qui l'accepte.
    """
    carriere, resultat = _carriere_exemple(exemple)
    declares = (exemple.get("ecart_connu") or {}).get("modele") or {}
    problemes = []
    for cle, valeur in exemple["attendu"].items():
        mesure = _mesurer(simulateur, exemple, carriere, resultat, cle)
        if cle not in declares:
            if not _concorde(cle, mesure, valeur):
                problemes.append((cle, mesure, "au lieu de la valeur publiée", valeur))
        elif _concorde(cle, mesure, valeur):
            problemes.append((cle, mesure, "est la valeur publiée : l'écart connu est "
                              "corrigé, sa déclaration se retire du témoin"))
        elif not _concorde(cle, mesure, declares[cle]):
            problemes.append((cle, mesure, "au lieu de la valeur que l'écart connu "
                              "déclare", declares[cle]))
    return problemes


@pytest.mark.parametrize("exemple", _charger_exemples(), ids=lambda e: e["id"])
def test_les_exemples_publies_par_les_caisses_sont_reproduits(simulateur, exemple):
    """Chaque exemple est une carrière minuscule dont la réponse est écrite
    par l'organisme qui applique la règle : service-public.gouv.fr, la Cnav
    dans ses circulaires. C'est la seule confrontation qui ne soit ni une
    relecture du même code ni un autre modèle. Le témoin dit d'où vient chaque
    exemple et ce qu'il attend ; `docs/limites.md` dit ce que la confrontation
    a trouvé.

    Un exemple que le modèle ne reproduit pas entre quand même, en écart
    connu (`docs/architecture.md`, § 9.2) : ce qu'on apprend n'est jamais
    bloqué. Le test tient alors la valeur que le modèle rend, pour qu'aucun
    résultat ne change sans le diff du témoin.
    """
    problemes = _confronter(simulateur, exemple)
    assert not problemes, problemes


def test_un_ecart_connu_entre_et_ne_change_pas_en_silence(simulateur):
    """Le mécanisme de l'écart connu, sur un exemple réel qu'on fausse.

    Le modèle reproduit la décote de la fiche F19666. On prête à l'exemple une
    autre valeur publiée : sans déclaration, il est refusé ; déclaré en écart
    connu, il passe ; déclaré avec une autre valeur du modèle, il est refusé,
    puisque le résultat aurait changé sans le diff du témoin. Et l'exemple
    vrai, déclaré en écart, est refusé aussi : l'écart est corrigé, sa
    déclaration doit se retirer.
    """
    import copy

    vrai = next(e for e in _charger_exemples() if e["id"] == "sp_f19666_decote")
    modele = vrai["attendu"]["taux_liquidation"]

    faux = copy.deepcopy(vrai)
    faux["attendu"]["taux_liquidation"] = modele + 0.01
    assert _confronter(simulateur, faux)
    faux["ecart_connu"] = {"modele": {"taux_liquidation": modele}}
    assert not _confronter(simulateur, faux)
    faux["ecart_connu"]["modele"]["taux_liquidation"] = modele + 0.005
    assert _confronter(simulateur, faux)

    corrige = copy.deepcopy(vrai)
    corrige["ecart_connu"] = {"modele": {"taux_liquidation": modele}}
    ((cle, _, pourquoi),) = _confronter(simulateur, corrige)
    assert cle == "taux_liquidation" and "corrigé" in pourquoi


def test_le_temoin_des_exemples_officiels_est_source():
    """Chaque exemple dit qui l'a publié, où, et quand il a été vérifié.

    Un écart connu dit en plus la valeur que rend le modèle, pourquoi, depuis
    quand, et la fiche de la carte qui le déclare : une règle qui n'est ni
    `conforme` ni `transcrite`, et qui compte l'exemple parmi ses exemples. Ce
    qu'un exemple révèle est déclaré là où il va (§ 9.2), et un écart ne
    s'admet pas sans que sa règle le dise.

    Un exemple tiré d'un simulateur nomme sa ligne au registre des sources et
    ce qu'on y a saisi : c'est ce que le budget de ce simulateur compte (§ 3.5).
    """
    import yaml

    from retraite_notionnelle.noyau import carte

    fiches = carte.fiches()
    registre = yaml.safe_load((Path(__file__).resolve().parents[1] / "data"
                               / "sources_a_explorer.yaml").read_text(encoding="utf-8"))
    simulateurs = {s["id"] for s in registre["sources"] if s["nature"] == "simulateur"}
    for exemple in _charger_exemples():
        source = exemple["source"]
        if source["reference"].startswith("simulateur") or "simulateur" in source:
            assert source.get("simulateur") in simulateurs, exemple["id"]
            assert len(str(source.get("saisie", "")).split()) >= 1, exemple["id"]
        assert source["editeur"] in (
            "service-public.gouv.fr", "Cnav", "ENIM", "CARCDSF", "CARMF",
            "CAVAMAC", "Cour des comptes", "SRE", "COR", "CNRACL", "CNIEG",
            "Agirc-Arrco", "CRPCEN", "CLEISS", "Direction de la sécurité sociale",
            "Union Retraite", "Audiens", "Ircantec", "ERAFP", "Cipav", "RSI",
        ), exemple["id"]
        assert len(source["reference"].split()) >= 4, exemple["id"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["verifie_le"]), exemple["id"]
        assert len(exemple["enonce"].split()) >= 12, exemple["id"]
        assert exemple["attendu"], exemple["id"]
        ecart = exemple.get("ecart_connu")
        if ecart is None:
            continue
        assert set(ecart) == {"modele", "explication", "fiche", "depuis"}, exemple["id"]
        assert ecart["modele"], exemple["id"]
        assert set(ecart["modele"]) <= set(exemple["attendu"]), exemple["id"]
        assert len(str(ecart["explication"]).split()) >= 12, exemple["id"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ecart["depuis"])), exemple["id"]
        regle = fiches.get(ecart["fiche"])
        assert regle is not None, (exemple["id"], ecart["fiche"])
        assert regle["etat"] not in ("conforme", "transcrite"), (exemple["id"], regle["etat"])
        assert exemple["id"] in carte.exemples_de(regle), (exemple["id"], regle["id"])
