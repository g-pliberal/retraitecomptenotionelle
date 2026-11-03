"""Le panorama de la DREES, édition 2026, confronté au modèle (action 178, étapes 4 et 5).

Treize fiches du suivi (``data/reference/drees_panorama_2026.yaml``) mesurent
ce que le modèle calcule ou suppose : la revalorisation des pensions servies,
le taux de remplacement, la pension des nouveaux retraités, les durées de
carrière, la polyaffiliation, les départs anticipés, les fins de carrière, le
recours au minimum vieillesse, la retraite supplémentaire. Ce module tient
deux choses :

* LE TÉMOIN, ``tests/temoins/drees_panorama_2026_confrontations.json`` :
  chaque valeur confrontée, recopiée de sa cellule dans le classeur de sa
  fiche, et les phrases du PDF que les tests citent ; recoupé aux classeurs et
  au PDF quand ``data/brut/`` les porte
  (``python scripts/fetch/source_locale.py --recuperer``) ;
* LES CONFRONTATIONS, fiche par fiche. Un écart ne se corrige pas ici : il se
  déclare dans le test qui le mesure, borné, pour qu'un écart qui bouge se
  voie. Ceux qui disent une erreur du modèle sont consignés pour l'étape 5
  (``docs/feuille_de_route/178/2026-11-03-etape-4-confrontations.md``).

L'étape 5 y ajoute LES RÈGLES : les tableaux de législation des fiches 14, 24
et 26, l'encadré 1 de la fiche 2 et la revalorisation de la fiche 4, confrontés
aux tables de ``data/reference/legislation/``, par leur propre témoin,
``tests/temoins/drees_panorama_2026_regles.json``
(``docs/feuille_de_route/178/2026-11-03-etape-5-regles.md``).
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle import controle_eacr
from retraite_notionnelle.castypes import GRILLE_DU_COUT
from retraite_notionnelle.config import RACINE_DONNEES, Parametres
from retraite_notionnelle.donnees.population import CarrieresIncompletes
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import cycle_de_vie  # noqa: E402
import lecture_xlsx  # noqa: E402
import source_locale  # noqa: E402

TEMOIN = RACINE / "tests" / "temoins" / "drees_panorama_2026_confrontations.json"
REGLES = RACINE / "tests" / "temoins" / "drees_panorama_2026_regles.json"
LEGISLATION = RACINE_DONNEES / "reference" / "legislation"
SUIVI = RACINE / "data" / "reference" / "drees_panorama_2026.yaml"
MACRO = RACINE_DONNEES / "reference" / "macro"

#: Les cas types 1 (cadre) et 2 (non-cadre) du COR, que la fiche 4 suit : la
#: part de chaque régime dans leur pension, celle que le dépôt confronte déjà
#: au COR (``tests/test_revalorisation.py``).
COMPOSITION = json.loads(
    (RACINE / "tests" / "temoins" / "cor_pouvoir_achat_retraite.json").read_text(encoding="utf-8")
)["conventions"]["composition"]


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


def _publie(temoin: dict, cle: str, *chemin: str):
    noeud = temoin["valeurs"][cle]
    for pas in chemin:
        noeud = noeud[pas]
    return noeud["valeur"]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def grille() -> list:
    """Les cohortes de la grille de la page Coût en 2024, telles que la
    confrontation à l'EACR les compte (``controle_eacr.controle``)."""
    return controle_eacr.controle()


@pytest.fixture(scope="module")
def etages(simulateur) -> dict:
    """La pension du départ des cas types, étage par étage, et leurs taux de
    remplacement, par le portage (``scripts/cycle_de_vie.py --etages``)."""
    return cycle_de_vie.etages(simulateur)


# --- Le témoin ---------------------------------------------------------------


def _depose(ident: str) -> Path | None:
    """Le document du manifeste dans ``data/brut/``, s'il y est et porte son empreinte."""
    jeu = next(j for j in source_locale.jeux_bloques() if j["id"] == ident)
    chemin = source_locale.ou_deposer(jeu)
    if chemin is None or not chemin.is_file():
        return None
    if jeu.get("sha256") and source_locale.empreinte(chemin.read_bytes()) != jeu["sha256"]:
        return None
    return chemin


def _cellules(noeud):
    if isinstance(noeud, dict) and "classeur" in noeud:
        yield noeud
    elif isinstance(noeud, dict):
        for valeur in noeud.values():
            yield from _cellules(valeur)


def _indices(reference: str) -> tuple[int, int]:
    lettres, ligne = re.fullmatch(r"([A-Z]+)(\d+)", reference).groups()
    colonne = 0
    for lettre in lettres:
        colonne = colonne * 26 + ord(lettre) - ord("A") + 1
    return int(ligne) - 1, colonne - 1


@pytest.mark.parametrize("fichier", [TEMOIN, REGLES], ids=["etape_4", "etape_5"])
def test_chaque_valeur_du_temoin_est_celle_de_sa_cellule(fichier):
    """Chaque valeur confrontée est celle que le classeur de sa fiche porte, à
    la cellule que le témoin nomme, au bit près."""
    archive = _depose("drees_panorama_retraites_2026_classeurs")
    if archive is None:
        pytest.skip("classeurs absents de data/brut/ : "
                    "python scripts/fetch/source_locale.py --recuperer")
    cellules = list(_cellules(json.loads(fichier.read_text(encoding="utf-8"))["valeurs"]))
    assert len(cellules) > 150
    grilles: dict = {}
    with zipfile.ZipFile(archive) as classeurs:
        for cellule in cellules:
            cle = (cellule["classeur"], cellule["feuille"])
            if cle not in grilles:
                grilles[cle] = lecture_xlsx.feuilles(
                    classeurs.read(cellule["classeur"]), (cellule["feuille"],))[cellule["feuille"]]
            assert grilles[cle].get(_indices(cellule["cellule"])) == cellule["valeur"], cellule


@pytest.mark.parametrize("fichier", [TEMOIN, REGLES], ids=["etape_4", "etape_5"])
def test_chaque_citation_du_temoin_est_dans_le_pdf(fichier):
    """Les phrases que les tests citent sont celles du PDF, lu dans l'ordre de
    lecture, césures et espaces mis à part."""
    temoin = json.loads(fichier.read_text(encoding="utf-8"))
    pdf = _depose("drees_panorama_retraites_2026")
    if pdf is None or shutil.which("pdftotext") is None:
        pytest.skip("PDF absent de data/brut/, ou pdftotext absent")
    texte = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, check=True,
                           text=True).stdout.replace("­", "")
    plat = " ".join(re.sub(r"-\n(?=\w)", "", texte).split())
    for cle, bloc in temoin["citations"].items():
        for phrase in bloc["textes"]:
            assert " ".join(phrase.split()) in plat, (cle, phrase)


def test_chaque_fiche_de_l_etape_4_nomme_ses_confrontations():
    """Au suivi, chaque fiche que l'étape 4 a confrontée nomme les tests de ce
    module qui la confrontent ; chacun existe. Les fiches 8 et 15, que l'étape
    2 lui a renvoyées le 3 novembre 2026, attendent leur confrontation ; la
    fiche 21, que l'étape 3 lui a renvoyée le même jour, est confrontée à la
    grille depuis."""
    suivi = yaml.safe_load(SUIVI.read_text(encoding="utf-8"))["fiches"]
    etape_4 = {numero: ligne for numero, ligne in suivi.items()
               if ligne.get("etape") == 4 and ligne["statut"] == "confronte"}
    assert sorted(etape_4) == ["04", "06", "07", "09", "11", "13", "18", "21", "28", "29",
                               "30", "31", "32"]
    attendent = sorted(numero for numero, ligne in suivi.items()
                       if ligne.get("etape") == 4 and ligne["statut"] != "confronte")
    assert attendent == ["08", "15"]
    assert {suivi[numero]["statut"] for numero in attendent} == {"a_confronter"}
    module = sys.modules[__name__]
    for numero, ligne in etape_4.items():
        assert len(" ".join(str(ligne["confrontation"]).split())) > 40, numero
        assert ligne["confronte_par"], numero
        for nom in ligne["confronte_par"]:
            assert nom.startswith("test_") and callable(getattr(module, nom, None)), (numero, nom)


# --- Fiche 4 : la revalorisation des pensions servies -----------------------


def _mois_du_point(annee: int) -> int:
    """Le mois où les complémentaires revalorisent leur point : avril jusqu'en
    2015, novembre depuis 2016."""
    return 4 if annee <= 2015 else 11


def _servie(simulateur, cas: str, depart: int, annee: int, mois: int) -> float:
    """La pension brute du cas type du COR parti en janvier de ``depart``, au
    mois ``mois`` de ``annee``, en part de sa pension de départ : chaque
    régime revalorisé sous son texte, comme ``tests/test_revalorisation.py``
    le fait pour le COR."""
    actuel = simulateur.scenario_actuel
    # Le non-cadre ne dépasse pas 2 000 € par mois en 2019, le cadre si.
    mensuel_2019 = 1500.0 if cas == "non_cadre" else 5000.0
    total = 0.0
    for part, poids in COMPOSITION[cas].items():
        if part == "cnav":
            facteur = simulateur.revalorisations.generale(
                date(depart, 1, 1), date(annee, mois, 1), False, mensuel_2019)[0]
        else:
            servie = annee if mois >= _mois_du_point(annee) else annee - 1
            facteur = (actuel.conversions_points.echelle(part, depart, annee)[0]
                       * liquider.valeur_du_point(actuel, part, servie)[0]
                       / liquider.valeur_du_point(actuel, part, depart - 1)[0])
        total += poids * facteur
    return total


def _erosion(simulateur, cas: str, generation: int, annees: int) -> float:
    """L'érosion relativement aux prix de la fiche 4 : la pension brute
    annuelle moyenne des ``annees`` premières années de retraite, déflatée des
    prix, rapportée à celle de la première, moins un."""
    depart = generation + 60

    def reelle(annee: int) -> float:
        brute = sum(_servie(simulateur, cas, depart, annee, mois) for mois in range(1, 13)) / 12
        return brute / simulateur.macro.coefficient_prix(depart, annee)

    return sum(reelle(depart + rang) for rang in range(annees)) / annees / reelle(depart) - 1


def test_l_erosion_des_pensions_par_generation_est_celle_de_trajectoire(simulateur, temoin):
    """Graphique 4 de la fiche 4 : l'érosion des pensions brutes relativement
    aux prix, au cours des 5, 10, 15 et 20 premières années de retraite, des
    cas types 1 et 2 du COR que TRAJECTOiRE calcule. Le dépôt la retrouve à
    trois dixièmes de point pour chaque génération partie à 60 ans, de 1940 à
    1950, par ses seules séries — coefficients du régime général, valeurs du
    point Arrco et Agirc, prix. 1939, partie en 1999, l'année où l'Arrco change
    d'échelle, n'est pas refaite : la pension de départ y mêle les deux
    échelles, que le cas type du COR ne dit pas comment répartir."""
    publie = temoin["valeurs"]["04_graphique_4"]
    refaits = 0
    for cas in ("non_cadre", "cadre"):
        for generation in range(1940, 1951):
            for annees, cellule in publie[cas][str(generation)].items():
                if generation + 60 + int(annees) - 1 > 2025:
                    continue
                refait = 100 * _erosion(simulateur, cas, generation, int(annees))
                assert refait == pytest.approx(cellule["valeur"], abs=0.3), (cas, generation, annees)
                refaits += 1
    assert refaits > 60


def test_le_pouvoir_d_achat_des_liquidants_de_2000_baisse_un_peu_plus_au_modele(simulateur, temoin):
    """Graphique 3 de la fiche 4 : le pouvoir d'achat de la pension brute des
    cas types partis à 60 ans en 2000, de décembre 2000 à décembre 2025 —
    −3,7 % pour le non-cadre, −5,3 % pour le cadre, comme le texte le dit (la
    lecture sous le graphique inverse le brut et le net : 4,4 % et 3,7 %).

    ÉCART DÉCLARÉ. Le dépôt y perd davantage, chaque cinquième année, de 0,2 à
    0,9 point pour le non-cadre et de 0,3 à 1,1 point pour le cadre : moins de
    cinq centièmes de point par an. Les prix de décembre, approchés
    par la moyenne de deux années, ne le referment pas ; la composition des
    cas types (celle du COR de 2026, quand la DREES suit ceux du rapport de
    2025) et le calendrier des revalorisations restent les causes probables.
    L'érosion par génération, calculée sur l'année comme TRAJECTOiRE la
    calcule, est retrouvée à trois dixièmes près : les séries sont justes."""
    for cas, perte in (("non_cadre", 3.7), ("cadre", 5.3)):
        publie = temoin["valeurs"]["04_graphique_3"][cas]
        assert publie["2000"]["valeur"] == 100.0
        assert round(100 - publie["2025"]["valeur"], 1) == perte
        depart = _servie(simulateur, cas, 2000, 2000, 12)
        for annee in range(2005, 2026, 5):
            refait = (100 * _servie(simulateur, cas, 2000, annee, 12) / depart
                      / simulateur.macro.coefficient_prix(2000, annee))
            assert -1.3 < refait - publie[str(annee)]["valeur"] < -0.1, (cas, annee)


# --- Fiche 6 : les écarts de pension entre générations ----------------------


def test_le_taux_de_remplacement_median_du_prive_est_celui_du_salarie_au_smic(etages, temoin):
    """Graphique 4 de la fiche 6 : le taux de remplacement net médian des
    anciens salariés à carrière complète, 78,8 % pour la génération 1940 et
    76,2 % pour 1950 dans le privé, 76,3 % et 72,1 % dans le public — la
    pension nette rapportée au salaire net des cinq années qui précèdent la
    dernière (encadré 1). Celui des cas types, au départ, rapporté au dernier
    revenu : le salarié au SMIC tient la médiane du privé à deux points près.

    ÉCART DÉCLARÉ. Le salarié au salaire moyen en est à 8 à 11 points en
    dessous, et le fonctionnaire sédentaire à 4 à 9 points sous celle du
    public : la médiane est celle de salaires plus bas que le salaire moyen,
    rapportés à des salaires de fin de carrière, et la part des primes du
    sédentaire, qui n'entrent pas dans sa pension, dépasse celle de l'agent
    médian."""
    for generation in (1940, 1950):
        prive = _publie(temoin, "06_graphique_4", str(generation), "prive")
        public = _publie(temoin, "06_graphique_4", str(generation), "public")

        def net(code: str) -> float:
            return 100 * etages[f"{code}|{generation}"]["actuel"]["remplacement_net"]

        assert abs(net("smic_carriere_complete") - prive) < 2.0, generation
        assert 8.0 < prive - net("salaire_moyen") < 11.0, generation
        assert 3.0 < public - net("fonctionnaire_sedentaire") < 9.0, generation


def test_l_ecart_entre_femmes_et_hommes_de_la_grille_est_bien_moindre(etages, temoin):
    """Graphique 3 de la fiche 6 : la pension des femmes est de 40 % sous celle
    des hommes dans la génération 1940, de 32 % dans la génération 1950.

    ÉCART DÉCLARÉ. La seule femme de la grille, la carrière interrompue, deux
    enfants, touche de 12 à 17 % de moins que l'homme au même salaire : le
    tiers puis la moitié de l'écart publié. La grille ne représente ni les
    salaires plus bas des femmes, ni leurs carrières plus courtes ailleurs que
    dans ce cas type."""
    for generation in (1940, 1950):
        femme = etages[f"carriere_interrompue|{generation}"]["actuel"]["brute"]
        homme = etages[f"salaire_moyen|{generation}"]["actuel"]["brute"]
        publie = _publie(temoin, "06_graphique_3", str(generation)) / 100
        assert 0.25 < (femme / homme - 1) / publie < 0.6, generation


# --- Fiche 7 : la pension des nouveaux retraités ----------------------------


def test_la_grille_sert_trop_a_ses_nouveaux_retraites_de_2024(grille, temoin):
    """Tableau 1 de la fiche 7 : 1 637 euros bruts par mois en moyenne pour les
    nouveaux retraités de 2024 résidant en France, et une pension des femmes
    de 29,4 % sous celle des hommes.

    ÉCART DÉCLARÉ. Les nouveaux retraités de la grille de la page Coût
    touchent 2 102 euros, 28 % de plus : ses cas types partent tous à carrière
    complète ou presque, et pas un ne porte de petite pension. Les femmes n'y
    font que 13,5 % des départs, par le seul cas type de la carrière
    interrompue, et leur pension n'est que de 8,5 % sous celle des hommes."""
    nouveaux = [c for c in grille if c.nouvelle]
    tetes = sum(c.tetes for c in nouveaux)
    moyenne = sum(c.tetes * c.pension for c in nouveaux) / tetes
    assert 1.2 < moyenne / _publie(temoin, "07_tableau_1", "montant") < 1.4
    femmes = {cas.code for cas in GRILLE_DU_COUT if cas.sexe == "F"}
    assert femmes == {"carriere_interrompue"}
    leurs = [c for c in nouveaux if c.code in femmes]
    leurs_tetes = sum(c.tetes for c in leurs)
    assert leurs_tetes / tetes < 0.2
    pension_f = sum(c.tetes * c.pension for c in leurs) / leurs_tetes
    pension_h = (moyenne * tetes - pension_f * leurs_tetes) / (tetes - leurs_tetes)
    assert abs(pension_f / pension_h - 1) < abs(_publie(temoin, "07_tableau_1",
                                                        "ecart_femmes_hommes")) / 100 / 2


# --- Fiche 9 : le patrimoine des retraités ----------------------------------


def test_le_patrimoine_des_retraites_que_lit_la_garantie_date_de_2018(temoin):
    """Encadré 3 de la fiche 9 : début 2024, les ménages de retraités ont un
    patrimoine brut moyen de 395 300 euros, net de 388 900 euros.

    ÉCART DÉCLARÉ. La reprise de la garantie sur succession lit, pour les
    retraités, les chiffres du COR de 2018 (``patrimoine_menages.csv``) :
    296 600 euros bruts en moyenne, un quart de moins, en euros de 2018. Les
    chiffres de 2024 la couvriraient mieux ; le panorama n'en donne que la
    moyenne, quand le calcul de la couverture lit aussi des déciles."""
    with (MACRO / "patrimoine_menages.csv").open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(l for l in flux if not l.startswith("#")))
    retraites = [l for l in lignes if l["population"] == "retraites"]
    assert {l["annee"] for l in retraites} == {"2018"}
    moyenne = next(float(l["valeur"]) for l in retraites if l["statistique"] == "moyenne")
    assert moyenne == 296600.0
    assert 1.25 < _publie(temoin, "09_encadre_3", "brut") / moyenne < 1.45
    assert _publie(temoin, "09_encadre_3", "net") < _publie(temoin, "09_encadre_3", "brut")


# --- Fiche 11 : les durées de carrière ---------------------------------------


def test_les_durees_validees_du_depot_sont_celles_du_panorama(temoin):
    """Graphique 3 de la fiche 11 : les durées validées par sexe et par
    génération, de l'EIR de 2020. Celles qui font la complétude de la grille,
    que le dépôt lit du COR (``duree_assurance_generations.csv``, figure 3.22
    du rapport de juin 2026), sont les mêmes, trimestre pour trimestre."""
    with (MACRO / "duree_assurance_generations.csv").open(encoding="utf-8") as flux:
        lues = {(l["generation"], l["sexe"]): float(l["trimestres"])
                for l in csv.DictReader(l for l in flux if not l.startswith("#"))}
    publiees = temoin["valeurs"]["11_graphique_3"]
    assert len(publiees) == 8
    for generation, sexes in publiees.items():
        for sexe, cellule in sexes.items():
            assert lues[(generation, sexe)] == cellule["valeur"], (generation, sexe)


def test_la_completude_de_la_grille_passe_le_coefficient_de_proratisation(temoin):
    """Tableau 1 de la fiche 11 : le coefficient de proratisation moyen de la
    génération 1953 résidant en France, tous régimes, est de 0,93 ; graphique
    2 : 63 % de ses retraités ont une carrière complète.

    ÉCART DÉCLARÉ, ERREUR DU MODÈLE (étape 5). La grille réduit la pension de
    chaque génération par sa complétude, la durée validée moyenne rapportée à
    la durée requise : 0,973 pour 1953. Le coefficient de chaque retraité ne
    passe pas 100 %, et la moyenne des durées compte les trimestres de ceux
    qui dépassent la durée requise : la complétude surestime de quatre points
    la pension des carrières incomplètes."""
    completude = CarrieresIncompletes(RACINE_DONNEES).completude(1953)
    assert 0.03 < completude - _publie(temoin, "11_tableau_1", "ensemble") < 0.06
    assert _publie(temoin, "11_graphique_2", "1953") < 70


# --- Fiche 13 : les régimes d'affiliation ------------------------------------


def test_la_grille_ne_compte_aucun_polyaffilie(temoin):
    """Tableau 1 de la fiche 13 : 54 % des affiliés de la génération 1957 ont
    cotisé à plusieurs régimes de base.

    ÉCART DÉCLARÉ. Chaque cas type de la grille n'a qu'un régime de base : la
    grille compte des têtes de caisse, qu'elle pèse par les effectifs de
    chaque caisse (limite n° 1 de ``cout.py``), et non des personnes ; un
    polypensionné y est un cas type par caisse, à carrière complète dans
    chacune."""
    assert all(len(cas.caisses) == 1 for cas in GRILLE_DU_COUT)
    assert _publie(temoin, "13_tableau_1", "polyaffilies") > 50


# --- Fiche 18 : les départs anticipés ----------------------------------------


def test_la_grille_fait_partir_trop_de_carrieres_longues_au_regime_general(grille, temoin):
    """Graphique 3 de la fiche 18 : 17,4 % des départs de 2024 au régime
    général sont des départs anticipés pour carrière longue.

    ÉCART DÉCLARÉ. Les nouveaux retraités de la Cnav de la grille partent à
    60 ans pour 21,8 % d'entre eux, tous du salarié au SMIC entré à 18 ans :
    un quart de plus. Le même écart se voit, tous régimes, à la table C de
    l'EACR (``test_controle_eacr.py``), qui dit déjà qu'un écart qui se
    referme dira que la population de l'étape 14 de l'action 138 a remplacé
    la grille."""
    cnav = {cas.code for cas in GRILLE_DU_COUT if cas.caisses == ("cnav",)}
    nouveaux = [c for c in grille if c.nouvelle and c.code in cnav]
    tetes = sum(c.tetes for c in nouveaux)
    anticipes = sum(c.tetes for c in nouveaux if c.age_liquidation < 62)
    assert {c.code for c in nouveaux if c.age_liquidation < 62} == {"smic_carriere_complete"}
    part = 100 * anticipes / tetes
    assert 1.15 < part / _publie(temoin, "18_graphique_3", "regime_general_2024") < 1.45


# --- Fiche 21 : la situation des assurés en fin de carrière ------------------


#: La situation de l'EIC où se range chaque interruption de la grille
#: (encadré 1 de la fiche 21) : le chômage, indemnisé ou non ; l'invalidité,
#: dont la pension valide des trimestres ; l'inactivité, qui n'en valide
#: aucun, et que l'EIC compte en absence.
SITUATIONS_DE_L_EIC = {"chomage_indemnise": "chomage", "chomage_solidarite": "chomage",
                       "chomage_non_indemnise": "chomage", "invalidite": "maladie_invalidite",
                       "inactivite": "absence"}


def test_la_grille_ne_finit_aucune_carriere_au_chomage(grille):
    """Tableau 1 de la fiche 21 : l'année qui précède leur liquidation, les
    liquidants de 67 ans ou avant de la génération 1954, la dernière que
    l'EIC de 2021 suit jusqu'à cet âge, sont en emploi pour 70,9 %, au
    chômage pour 10,4 %, en maladie ou en invalidité pour 7,5 %, absents
    pour 11,3 % (``fins_de_carriere.csv``, que l'étape 3 certifie au classeur
    de la fiche).

    ÉCART DÉCLARÉ. Les nouveaux retraités de 2024 de la grille de la page
    Coût, dans le même champ — partis à 67 ans ou avant, mais pas dès 50 —,
    sont en emploi l'année qui précède leur liquidation pour 88,7 % d'entre
    eux, 18 points de plus : seuls l'inapte, sans activité depuis ses
    quarante-neuf ans, et l'ex-invalide, en invalidité depuis ses
    quarante-six, ne travaillent pas, et aucun cas type ne finit au chômage.
    L'écart tient aux cas types de la grille, comme ceux des fiches 7 et 18 :
    qu'il se referme dira que la population de l'étape 14 de l'action 138,
    et ses carrières inactives, ont remplacé la grille."""
    with (MACRO / "fins_de_carriere.csv").open(encoding="utf-8") as flux:
        publie = {ligne["modalite"]: float(ligne["valeur"])
                  for ligne in csv.DictReader(l for l in flux if not l.startswith("#"))
                  if (ligne["generation"], ligne["champ"], ligne["groupe"], ligne["sexe"])
                  == ("1954", "situation_avant_liquidation", "ensemble", "ensemble")}
    cas_types = {cas.code: cas for cas in GRILLE_DU_COUT}
    parts: dict[str, float] = {}
    for cohorte in grille:
        if not cohorte.nouvelle or not 50 < cohorte.age_liquidation <= 67:
            continue
        cas = cas_types[cohorte.code]
        interruptions = {int(cas.age_debut + decalage): motif
                         for decalage, motif in cas.interruptions_relatives}
        motif = interruptions.get(cohorte.age_liquidation - 1)
        situation = "emploi" if motif is None else SITUATIONS_DE_L_EIC[motif]
        parts[situation] = parts.get(situation, 0.0) + cohorte.tetes
    total = sum(parts.values())
    parts = {situation: 100 * tetes / total for situation, tetes in parts.items()}
    assert sorted(parts) == ["absence", "emploi", "maladie_invalidite"]
    assert publie["chomage"] > 10
    assert 15 < parts["emploi"] - publie["emploi"] < 21
    assert 0.4 < parts["absence"] / publie["absence"] < 0.6
    assert 0.65 < parts["maladie_invalidite"] / publie["maladie_invalidite"] < 0.9


# --- Fiche 28 : le recours au minimum vieillesse -----------------------------


def test_le_recours_a_la_garantie_est_celui_des_tetes_et_non_des_euros(temoin):
    """Encadré 2 de la fiche 28 : en 2016, près de la moitié des personnes
    seules éligibles au minimum vieillesse n'y recourent pas ; elles
    toucheraient 205 euros par mois, quand les allocataires en touchent 337 ;
    le non-recours passe de 77 % sous 100 euros attendus à 22 % entre 500 et
    600 euros. La garantie de la proposition retient un recours de 50 %.

    ÉCART DÉCLARÉ, ERREUR DU MODÈLE (étape 5). Le coût multiplie la dépense des
    ayants droit par ce taux (``GarantieDistribution``) : il compte un euro
    sur deux. Mais le recours croît avec le montant : en euros, les
    allocataires portent 337 / (337 + 205) = 62 % de ce que toucheraient tous
    les ayants droit, et le coût de la garantie est sous-estimé d'un
    cinquième."""
    assert Parametres().taux_recours_garantie == 0.5
    encadre = temoin["citations"]["28_encadre_2"]
    assert any("près de la moitié" in phrase for phrase in encadre["textes"])
    en_euros = encadre["allocataires_euros"] / (encadre["allocataires_euros"]
                                                + encadre["non_recourants_euros"])
    assert en_euros == pytest.approx(0.62, abs=0.005)
    assert encadre["non_recours_moins_de_100_euros"] > 3 * encadre["non_recours_500_a_600_euros"]


# --- Fiches 29 à 32 : la retraite supplémentaire -----------------------------


def test_le_pilier_sert_en_rente_ce_que_le_per_laisse_sortir_en_capital(temoin):
    """Tableau 1 de la fiche 29 : le PER se sort en rente ou en capital pour
    ses compartiments 1 et 2, les versements volontaires et l'épargne
    salariale ; le compartiment 3, les versements obligatoires, en rente.

    ÉCART DÉCLARÉ. Le pilier de la proposition, « logé dans l'enveloppe du
    PER », sert tout en rente viagère : ses 5 % obligatoires comme le
    compartiment 3, ses 5 % volontaires plus étroitement que le compartiment
    1, qui laisse le choix du capital. Le régime fiscal des versements et des
    rentes (RVTG ou RVTO, versements déductibles ou non) n'est pas dit par la
    fiche du pilier."""
    sortie = _publie(temoin, "29_tableau_1", "sortie_per_individuel")
    assert "sortie en capital (compartiments 1 et 2)" in sortie
    assert _publie(temoin, "29_tableau_1", "compartiment_3").startswith(
        "Compartiment 3 – Versements obligatoires")
    fiche = yaml.safe_load((RACINE_DONNEES / "reference" / "regles" / "proposition"
                            / "capitalisation_obligatoire.yaml").read_text(encoding="utf-8"))
    intitule = " ".join(fiche["intitule"].split())
    assert "servis en rente viagère" in intitule
    assert "RVT" not in json.dumps(fiche, ensure_ascii=False, default=str)


def test_le_pilier_ferait_de_la_capitalisation_le_tiers_des_cotisations(temoin):
    """Graphique 5 de la fiche 30 : la retraite supplémentaire fait 5,4 % des
    cotisations de retraite en 2024, 2,2 % des prestations.

    COMPARAISON DÉCLARÉE. Sur l'assiette de la proposition, ses 5 points
    obligatoires et ses 5 points volontaires font 10 points sur 28, plus du
    tiers de ce qui est prélevé pour la retraite : six fois et demie la part
    d'aujourd'hui, à verser au PER."""
    parametres = Parametres()
    capitalise = parametres.taux_capitalisation_obligatoire + parametres.taux_capitalisation_volontaire
    part = capitalise / (parametres.taux_cotisation_liberal + capitalise)
    assert part == pytest.approx(10 / 28)
    assert 6 < 100 * part / _publie(temoin, "30_graphique_5", "cotisations_2024") < 7


def _smpt_2024() -> float:
    with (MACRO / "salaire_moyen_niveau.csv").open(encoding="utf-8") as flux:
        return next(float(l["salaire_moyen_annuel"])
                    for l in csv.DictReader(l for l in flux if not l.startswith("#"))
                    if l["annee"] == "2024")


def test_la_capitalisation_volontaire_vaut_les_deux_tiers_d_un_versement_au_per(temoin):
    """Graphique 6 de la fiche 31 : un contrat individuel de retraite
    supplémentaire qui reçoit une cotisation en reçoit 3 160 euros en 2024.

    COMPARAISON DÉCLARÉE. La capitalisation volontaire de la proposition, 5 %
    de l'assiette, vaut 2 045 euros au salaire moyen par tête de 2024
    (40 897 euros) : deux tiers d'un versement d'aujourd'hui, que la
    convention suppose versés par chaque salarié."""
    volontaire = Parametres().taux_capitalisation_volontaire * _smpt_2024()
    assert 0.55 < volontaire / _publie(temoin, "31_graphique_6", "cicd_2024") < 0.75


def test_la_rente_du_pilier_a_maturite_passe_trois_fois_celle_d_aujourd_hui(etages, temoin):
    """Graphique 2 de la fiche 32 : une rente viagère de contrat individuel
    vaut 1 820 euros par an en moyenne en 2024, 4,5 % du salaire moyen.

    COMPARAISON DÉCLARÉE. Le pilier de la proposition sert au salarié au
    salaire moyen de la génération 2000, qui y a cotisé toute sa carrière, une
    rente de 15,6 % de son dernier revenu : plus de trois fois la rente
    moyenne d'aujourd'hui, rapportée au salaire."""
    pilier = etages["salaire_moyen|2000"]["notionnel_liberal"]
    rente = pilier["etages"]["capitalise"] / pilier["dernier_revenu"]
    aujourd_hui = _publie(temoin, "32_graphique_2", "cicd_2024") / _smpt_2024()
    assert 3.0 < rente / aujourd_hui < 4.5


# === Étape 5 : les règles ====================================================
#
# Les tableaux de législation du panorama, confrontés aux tables du scénario 1,
# mois de naissance par mois de naissance. Un écart que le texte tranche contre
# la DREES est déclaré ici, avec le texte ; un écart du dépôt, corrigé ou
# déclaré avec ce qui le tient ouvert.


@pytest.fixture(scope="module")
def regles() -> dict:
    return json.loads(REGLES.read_text(encoding="utf-8"))


def _fusions(classeur: bytes, feuille: str) -> set[str]:
    """Les plages fusionnées d'une feuille, lues dans le XML du classeur."""
    with zipfile.ZipFile(io.BytesIO(classeur)) as archive:
        relations = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"',
                                    archive.read("xl/_rels/workbook.xml.rels").decode("utf-8")))
        feuilles = dict(re.findall(r'<sheet name="([^"]+)"[^>]*r:id="(rId\d+)"',
                                   archive.read("xl/workbook.xml").decode("utf-8")))
        xml = archive.read("xl/" + relations[feuilles[feuille]].lstrip("/")).decode("utf-8")
    return set(re.findall(r'<mergeCell ref="([A-Z]+\d+:[A-Z]+\d+)"', xml))


def test_chaque_fusion_du_temoin_est_celle_du_classeur(regles):
    """Une cellule vide que couvre une fusion prend la valeur de sa première
    cellule : la fusion est dans le classeur, commence à la cellule nommée, et
    couvre la ligne de la génération qui la lit."""
    for cle, tableau in regles["valeurs"].items():
        for ligne in tableau.get("lignes", []) if isinstance(tableau, dict) else []:
            rang = _indices(ligne["generation"]["cellule"])[0]
            for noeud in ligne.values():
                if "fusion" in noeud:
                    debut, fin = noeud["fusion"].split(":")
                    assert debut == noeud["cellule"], (cle, noeud)
                    assert _indices(debut)[0] <= rang <= _indices(fin)[0], (cle, noeud)
    archive = _depose("drees_panorama_retraites_2026_classeurs")
    if archive is None:
        pytest.skip("classeurs absents de data/brut/ : "
                    "python scripts/fetch/source_locale.py --recuperer")
    lues: dict = {}
    with zipfile.ZipFile(archive) as classeurs:
        for noeud in _cellules(regles["valeurs"]):
            if "fusion" in noeud:
                cle = (noeud["classeur"], noeud["feuille"])
                if cle not in lues:
                    lues[cle] = _fusions(classeurs.read(cle[0]), cle[1])
                assert noeud["fusion"] in lues[cle], noeud


MOIS_DU_LIBELLE = {"avril": 4, "juillet": 7, "septembre": 9}


def _naissances(libelle) -> list[tuple[int, int]]:
    """Les mois de naissance (année, mois) qu'une ligne d'un tableau couvre ;
    « et suivantes » s'arrête cinq ans plus loin, « avant le » dix ans plus tôt."""
    texte = " ".join(str(libelle).split())
    def suite(debut, fin):
        return [(n // 12, n % 12 + 1) for n in range(debut[0] * 12 + debut[1] - 1,
                                                     fin[0] * 12 + fin[1])]
    if isinstance(libelle, float) or re.fullmatch(r"\d{4}", texte):
        annee = int(float(libelle))
        return suite((annee, 1), (annee, 12))
    if trouve := re.fullmatch(r"(\d{4})-(\d{4})", texte):
        return suite((int(trouve[1]), 1), (int(trouve[2]), 12))
    if trouve := re.fullmatch(r"Du 01/(\d\d)/(\d{4}) au \d\d/(\d\d)/(\d{4})", texte):
        return suite((int(trouve[2]), int(trouve[1])), (int(trouve[4]), int(trouve[3])))
    if trouve := re.fullmatch(r"Avant le 01/(\d\d)/(\d{4})", texte):
        annee, mois = int(trouve[2]), int(trouve[1])
        return suite((annee - 10, mois), (annee - (mois == 1), (mois - 2) % 12 + 1))
    if trouve := re.fullmatch(r"(\d{4}) et suivantes", texte):
        return suite((int(trouve[1]), 1), (int(trouve[1]) + 4, 12))
    if trouve := re.fullmatch(r"(\d{4}), avant le 1er (\w+)", texte):
        return suite((int(trouve[1]), 1), (int(trouve[1]), MOIS_DU_LIBELLE[trouve[2]] - 1))
    if trouve := re.fullmatch(r"(\d{4}), à partir du 1er (\w+)", texte):
        return suite((int(trouve[1]), MOIS_DU_LIBELLE[trouve[2]]), (int(trouve[1]), 12))
    raise ValueError(f"libellé de génération inconnu : {texte!r}")


def _en_mois(age) -> int | None:
    """« 62 ans et 9 mois » : 753 mois ; « - », « Inutile » : rien."""
    trouve = re.match(r"(\d+) ans(?: et (\d+) mois)?", " ".join(str(age).split()))
    return None if trouve is None else 12 * int(trouve[1]) + int(trouve[2] or 0)


def _csv(nom: str) -> list[dict]:
    with open(LEGISLATION / nom, encoding="utf-8") as fichier:
        return list(csv.DictReader(ligne for ligne in fichier if not ligne.startswith("#")))


def _escalier(nom: str, colonne: str, **filtre) -> list[tuple[float, float]]:
    """Une table par génération (année décimale, mois compris), en escalier."""
    return sorted((float(ligne["generation"]), float(ligne[colonne])) for ligne in _csv(nom)
                  if all(ligne[cle] == valeur for cle, valeur in filtre.items()))


def _a_la_naissance(table: list[tuple[float, float]], annee: int, mois: int) -> float:
    """La ligne qui couvre ce mois de naissance : la dernière qui commence avant
    lui (``1961.667`` est septembre 1961, arrondi au millième)."""
    naissance = annee + (mois - 1) / 12
    return [valeur for generation, valeur in table if generation <= naissance + 1e-3][-1]


def _confronter(regles: dict, cle: str, colonnes: dict, declares: dict | None = None) -> int:
    """Chaque mois de naissance de chaque ligne : la valeur du panorama, en mois
    ou en trimestres, contre celle que ``colonnes[nom](annee, mois)`` lit au
    dépôt ; ``declares`` porte les écarts connus, (colonne, année, mois) →
    (panorama, dépôt). Rend le nombre de mois confrontés."""
    declares = dict(declares or {})
    vus = 0
    for ligne in regles["valeurs"][cle]["lignes"]:
        for annee, mois in _naissances(ligne["generation"]["valeur"]):
            for nom, lire in colonnes.items():
                if nom not in ligne:
                    continue
                valeur = ligne[nom]["valeur"]
                publie = int(valeur) if isinstance(valeur, float) else _en_mois(valeur)
                if publie is None:
                    continue
                au_depot = lire(annee, mois)
                if (nom, annee, mois) in declares:
                    assert (publie, au_depot) == declares.pop((nom, annee, mois)), (nom, annee, mois)
                else:
                    assert publie == au_depot, (cle, nom, annee, mois, ligne[nom])
                vus += 1
    assert not declares, f"écarts déclarés qui n'ont pas paru : {declares}"
    return vus


# --- Fiche 14, tableaux 1 à 3, et encadré 1 de la fiche 2 : âges et durées ---


def test_les_ages_legaux_du_panorama_sont_ceux_du_depot(regles):
    """Tableau 1 et son complément : l'âge légal du privé, des actifs et des
    super-actifs, avant et après la loi de financement pour 2026, mois de
    naissance par mois de naissance. Le dépôt ne porte, pour les actifs et les
    super-actifs, que le calendrier de 2026 : là où celui de 2023 s'en écarte
    (nés de 1969 à 1973, et de 1974 à 1978), l'âge de 2026 se trouve atteint après
    le 1er septembre 2026, si bien qu'aucune pension n'a pu prendre effet sous
    l'ancien — l'argument de ``age_ouverture_requis.csv`` pour le privé."""
    legal = _escalier("age_ouverture_requis.csv", "age")
    suspendu = _escalier("age_ouverture_avant_suspension.csv", "age")
    actifs = _escalier("categorie_active.csv", "age_ouverture", classement="active")
    super_actifs = _escalier("categorie_active.csv", "age_ouverture", classement="super_active")

    def mois(table):
        return lambda annee, m: round(12 * _a_la_naissance(table, annee, m))

    def avant_la_suspension(annee, m):
        """Le calendrier de 2023, que le dépôt porte pour les nés de 1964 à 1968."""
        table = suspendu if 1964 <= annee <= 1968 else legal
        return round(12 * _a_la_naissance(table, annee, m))

    vus = _confronter(regles, "14_tableau_1", {
        "prive_apres": mois(legal), "prive_avant": avant_la_suspension,
        "actifs_apres": mois(actifs)})
    vus += _confronter(regles, "14_tableau_1_comp", {"super_actifs_apres": mois(super_actifs)})
    assert vus > 1000
    # Le calendrier de 2023 des actifs et des super-actifs : là où il diffère,
    # le dépôt n'a que celui de 2026, atteint plus tôt, et après septembre 2026.
    for cle, nom, table, nes in (("14_tableau_1", "actifs_avant", actifs, range(1969, 1974)),
                                 ("14_tableau_1_comp", "super_actifs_avant", super_actifs,
                                  range(1974, 1979))):
        for ligne in regles["valeurs"][cle]["lignes"]:
            for annee, m in _naissances(ligne["generation"]["valeur"]):
                publie = _en_mois(ligne.get(nom, {}).get("valeur"))
                if publie is None or annee < 1950:
                    continue
                au_depot = round(12 * _a_la_naissance(table, annee, m))
                if annee in nes:
                    assert publie > au_depot, (nom, annee, m)
                    atteint = annee * 12 + m - 1 + au_depot + 1
                    assert atteint >= 2026 * 12 + 8, (nom, annee, m)
                else:
                    assert publie == au_depot, (nom, annee, m)


def test_les_durees_requises_du_panorama_sont_celles_du_depot(regles):
    """Tableau 2 : la durée requise du privé, avant et après la loi de
    financement pour 2026, et celle des sédentaires de la fonction publique,
    qui suit, de 1944 à 1948, l'année où le droit s'ouvre, à soixante ans
    (``duree_requise_fonction_publique.csv`` ; 150 trimestres avant 2004, que la
    fiche du régime porte), puis celle du privé."""
    requise = _escalier("duree_assurance_requise.csv", "trimestres")
    suspendue = _escalier("duree_requise_avant_suspension.csv", "trimestres")
    publique = {int(ligne["annee_ouverture"]): int(ligne["trimestres"])
                for ligne in _csv("duree_requise_fonction_publique.csv")}

    def trimestres(annee, m):
        return int(_a_la_naissance(requise, annee, m))

    def avant_la_suspension(annee, m):
        """Le calendrier de 2023, que le dépôt porte pour les nés de 1964 et 1965."""
        return int(_a_la_naissance(suspendue if annee in (1964, 1965) else requise, annee, m))

    def sedentaires(annee, m):
        if annee <= 1948:
            return publique.get(annee + 60, 150 if annee + 60 < 2004 else None)
        return int(_a_la_naissance(requise, annee, m))

    vus = _confronter(regles, "14_tableau_2", {
        "prive_apres": trimestres, "prive_avant": avant_la_suspension,
        "sedentaires_apres": sedentaires, "sedentaires_avant": lambda a, m: (
            sedentaires(a, m) if a <= 1963 else avant_la_suspension(a, m))})
    assert vus > 300


def _annulation_fonction_publique(limite: float, ouverture: float, annee: int, mois: int,
                                  minorations: dict[int, int]) -> int | None:
    """L'âge d'annulation de la décote d'un fonctionnaire, en mois : sa limite
    d'âge, moins les trimestres que la loi de 2003 retranche l'année où son droit
    s'ouvre (``decote_fonction_publique.csv``) ; rien avant 2006, où la décote
    n'existe pas."""
    ouvert_en = (annee * 12 + mois - 1 + round(12 * ouverture)) // 12
    if ouvert_en < min(minorations):
        return None
    retranche = minorations[min(ouvert_en, max(minorations))]
    return round(12 * limite) - 3 * retranche


def test_les_ages_d_annulation_de_la_decote_sont_ceux_du_depot(regles):
    """Tableau 3 : l'âge d'annulation de la décote du privé, et celui des
    fonctionnaires, sédentaires et actifs, que le dépôt tire de leur limite
    d'âge et de l'année où leur droit s'ouvre ; le « - » du panorama est
    l'absence de décote, avant 2006."""
    prive = _escalier("age_annulation_decote.csv", "age")
    legal = _escalier("age_ouverture_requis.csv", "age")
    actifs = {nom: _escalier("categorie_active.csv", nom, classement="active")
              for nom in ("age_ouverture", "age_annulation")}
    minorations = {int(ligne["annee"]): int(ligne["trimestres_avant_limite"])
                   for ligne in _csv("decote_fonction_publique.csv")}
    tirets = 0
    for ligne in regles["valeurs"]["14_tableau_3"]["lignes"]:
        for annee, m in _naissances(ligne["generation"]["valeur"]):
            calcules = {
                "prive": round(12 * _a_la_naissance(prive, annee, m)),
                "sedentaires": _annulation_fonction_publique(
                    _a_la_naissance(prive, annee, m), _a_la_naissance(legal, annee, m),
                    annee, m, minorations),
                "actifs": _annulation_fonction_publique(
                    _a_la_naissance(actifs["age_annulation"], annee, m),
                    _a_la_naissance(actifs["age_ouverture"], annee, m), annee, m, minorations)}
            for nom, calcule in calcules.items():
                if nom not in ligne:
                    continue
                publie = _en_mois(ligne[nom]["valeur"])
                tirets += publie is None
                assert publie == calcule, (nom, annee, m, ligne[nom])
    assert tirets == 12 * 7


def test_les_mois_de_depart_de_l_encadre_de_la_fiche_2_sont_ceux_de_l_age_legal(regles):
    """Encadré 1 de la fiche 2 : combien de mois de naissance de chaque
    génération atteignent l'âge légal chaque année, la pension prenant effet au
    premier jour du mois qui suit l'anniversaire ; l'âge de chaque ligne, et
    l'ensemble, sur ``age_ouverture_requis.csv``."""
    legal = _escalier("age_ouverture_requis.csv", "age")
    ensemble: dict[str, int] = {}
    for ligne in regles["valeurs"]["02_encadre_1"]["lignes"]:
        comptes: dict[str, int] = {}
        for annee, m in _naissances(ligne["generation"]["valeur"]):
            age = round(12 * _a_la_naissance(legal, annee, m))
            assert age == _en_mois(ligne["age"]["valeur"]), (annee, m)
            depart = str((annee * 12 + m - 1 + age + 1) // 12)
            comptes[depart] = comptes.get(depart, 0) + 1
            ensemble[depart] = ensemble.get(depart, 0) + 1
        dans_le_tableau = {annee: n for annee, n in comptes.items() if "2022" <= annee <= "2034"}
        assert dans_le_tableau == {annee: int(n["valeur"]) for annee, n in ligne["mois"].items()}, ligne
    publie = regles["valeurs"]["02_encadre_1"]["ensemble"]
    assert {annee: n for annee, n in ensemble.items() if annee in publie} == {
        annee: int(n["valeur"]) for annee, n in publie.items()}


# --- Fiche 14, tableau 4 : la carrière longue ---------------------------------


def _carriere_longue(annee: int, mois: int, debut: int, jusqu_a: float = 2100.0) -> int | None:
    """L'âge de départ, en mois, de la porte des débuts avant ``debut`` ans pour
    un assuré né ce mois-là : celui de la rédaction en vigueur au mois où il
    l'atteint (``carriere_longue.csv``, par ``date_effet``) — le premier jour
    du mois qui suit son anniversaire tombe dans la période de cette
    rédaction ; ``jusqu_a`` écarte les rédactions postérieures."""
    naissance = annee + (mois - 1) / 12
    lignes = [ligne for ligne in _csv("carriere_longue.csv")
              if int(ligne["age_debut_maximum"]) == debut
              and float(ligne["generation"]) - 1e-3 <= naissance < float(ligne["generation_fin"]) - 1e-3]
    effets = sorted({float(l["date_effet"]) for l in _csv("carriere_longue.csv")
                     if float(l["date_effet"]) < jusqu_a})
    for rang, effet in enumerate(effets):
        suivante = effets[rang + 1] if rang + 1 < len(effets) else 9999.0
        couvrantes = [ligne for ligne in lignes if float(ligne["date_effet"]) == effet]
        if not couvrantes:
            continue
        age = round(12 * float(max(couvrantes, key=lambda l: float(l["generation"]))["age_depart"]))
        if effet - 1e-3 <= (annee * 12 + mois - 1 + age + 1) / 12 < suivante - 1e-3:
            return age
    return None


def test_la_carriere_longue_du_panorama_est_celle_du_depot(regles):
    """Tableau 4 : la porte des débuts avant vingt ans, avant et après la loi
    de financement pour 2026 — « les âges de départ en vigueur au moment où
    ces générations les ont atteints » (note 1) —, et celles des débuts avant
    seize, dix-huit et vingt et un ans, là où le panorama les dit utiles.

    Un écart, que le texte tranche contre la DREES : le II de D. 351-1-1, dans
    sa rédaction du 1er septembre 2026 (décret n° 2026-345,
    LEGIARTI000054059621), 4° : « pour les assurés nés entre le 1er décembre
    et le 31 décembre 1965 inclus », « soixante ans et huit mois ». Le panorama
    fond décembre dans les 60 ans et 9 mois du reste de 1965."""
    vus = _confronter(regles, "14_tableau_4", {
        "avant_20_avant": lambda a, m: _carriere_longue(a, m, 20, jusqu_a=2026.667),
        "avant_20_apres": lambda a, m: _carriere_longue(a, m, 20),
        "avant_16": lambda a, m: _carriere_longue(a, m, 16),
        "avant_18": lambda a, m: _carriere_longue(a, m, 18),
        "avant_21": lambda a, m: _carriere_longue(a, m, 21)},
        declares={("avant_20_apres", 1965, 12): (729, 728)})
    assert vus > 400


def test_la_decote_et_la_surcote_du_panorama_sont_celles_du_depot(regles):
    """Encadrés 1 et 2 de la fiche 14 : le coefficient de minoration du régime
    général, la décote de la fonction publique, ses trimestres au plus, et les
    taux de la surcote.

    Un écart de rédaction : « 2,5 % pour la génération 1944 » ; R. 351-27, dans
    sa rédaction de 2004 (LEGIARTI000006749436), donne 2,5 % « pour l'assuré né
    avant le 1er janvier 1944 » et 2,375 % à celui né en 1944 — la marche de
    0,125 point par génération, qui mène aux 1,375 % de 1952 que le panorama dit
    aussi."""
    assert regles["citations"]["14_encadre_1"]["textes"][1].startswith(
        "Il passe de 2,5 % pour la génération 1944")
    minoration = {int(float(l["generation"])): float(l["coefficient"])
                  for l in _csv("coefficient_minoration.csv")}
    assert minoration[1943] == 0.025 and minoration[1944] == 0.02375
    assert minoration[1952] == 0.01375
    assert {taux for generation, taux in minoration.items() if generation >= 1953} == {0.0125}
    # Au plus vingt trimestres de décote avant 1961, douze à compter de 1969 :
    # l'âge d'annulation moins l'âge légal.
    annulation = _escalier("age_annulation_decote.csv", "age")
    legal = _escalier("age_ouverture_requis.csv", "age")
    ecart = {g: round(4 * (_a_la_naissance(annulation, g, 1) - _a_la_naissance(legal, g, 1)))
             for g in (1955, 1960, 1969, 1975)}
    assert ecart == {1955: 20, 1960: 20, 1969: 12, 1975: 12}
    publique = {int(l["annee"]): float(l["coefficient"]) for l in _csv("decote_fonction_publique.csv")}
    assert min(publique) == 2006 and publique[2006] == 0.00125 and publique[2015] == 0.0125
    surcote = [l for l in _csv("surcote_baremes.csv") if l["bareme"] == "regime_general"]
    taux = {(l["debut"], l["rang_minimum"], l["apres_65_ans"]): float(l["taux"]) for l in surcote}
    assert taux == {("2004", "1", "0"): 0.0075, ("2007", "1", "0"): 0.0075,
                    ("2007", "5", "0"): 0.01, ("2007", "1", "1"): 0.0125,
                    ("2009", "1", "0"): 0.0125}
    parentale = _csv("surcote_parentale.csv")[0]
    assert float(parentale["age_ouverture"]) == 63
    assert float(parentale["taux_par_trimestre"]) * int(parentale["trimestres_maximum"]) == 0.05


# --- Fiche 4, tableau 1 : la revalorisation, régime par régime ----------------


def _au_31_decembre(dates: dict[str, float], annee: int) -> float:
    return dates[max(date for date in dates if date <= f"{annee}-12-31")]


def _indices_des_regimes() -> dict[str, dict[str, float]]:
    """Pour chaque ligne du tableau, l'indice de la pension servie, daté, tel que
    le dépôt le lit : les coefficients des régimes de base (la ligne de 2020
    des pensions sous 2 000 €), les valeurs de service datées de l'Agirc et de
    l'Arrco, puis de l'Agirc-Arrco, et les valeurs annuelles de l'Ircantec, du
    RAFP et des complémentaires des indépendants (au 1er janvier)."""
    base, indice = {}, 1.0
    for ligne in _csv("revalorisation_pensions.csv"):
        if not ligne["mensuel_superieur_a"]:
            indice *= float(ligne["coefficient"])
            base[ligne["date_effet"]] = indice
    with open(RACINE_DONNEES / "reference" / "regimes" / "valeurs_service_datees.csv",
              encoding="utf-8") as fichier:
        datees = list(csv.DictReader(l for l in fichier if not l.startswith("#")))
    with open(RACINE_DONNEES / "reference" / "regimes" / "valeurs_point.csv",
              encoding="utf-8") as fichier:
        points = list(csv.DictReader(l for l in fichier if not l.startswith("#")))

    def annuelle(regime):
        return {f"{l['annee']}-01-01": float(l["valeur"]) for l in points
                if l["regime"] == regime and l["mesure"] == "valeur_service"}

    fusion = {l["date_effet"]: float(l["valeur"]) for l in datees if l["regime"] == "agirc_arrco"}
    indices = {"base": base, "ircantec": annuelle("ircantec"), "rafp": annuelle("rafp")}
    for regime in ("agirc", "arrco"):
        propre = {l["date_effet"]: float(l["valeur"]) for l in datees if l["regime"] == regime}
        dernier = propre[max(propre)]
        indices[regime] = {**propre, **{date: dernier * valeur / fusion["2019-01-01"]
                                        for date, valeur in fusion.items() if date > "2019-01-01"}}
    rci = annuelle("rci")
    for ligne, avant_2013 in (("rsi_commercants", "nric"), ("rsi_artisans", "rco_artisans")):
        propre = annuelle(avant_2013)
        indices[ligne] = {**propre, **{date: propre["2012-01-01"] * valeur / rci["2013-01-01"]
                                       for date, valeur in rci.items()}}
    return indices


#: Les écarts du tableau complémentaire, (ligne, année) → (panorama, dépôt), en %.
ECARTS_DE_REVALORISATION = {
    # La DREES écrit 1,8 % ; les arrêtés et la circulaire font 1,1 % au
    # 1er janvier 2008 et 0,8 % au 1er septembre, 1,9 %, comme l'indice du
    # graphique 1 de sa fiche 26 (116,13 / 113,97).
    ("base", 2008): (1.8, 1.9),
    # 2020 : 1 % sous 2 000 € par mois, 0,3 % au-dessus ; la DREES prend la
    # moyenne, 0,7 % (note 1), le dépôt porte le barème par tranche.
    ("base", 2020): (0.7, 1.0),
    # Le point de l'Ircantec passe de 0,47887 à 0,48031 € au 1er janvier 2019,
    # 0,3 % comme les pensions de base ; la DREES écrit 1,0 %.
    ("ircantec", 2019): (1.0, 0.3),
    # 2013 : les deux complémentaires du RSI fusionnent dans la RCI ; aucune
    # série du dépôt ne les enjambe.
    ("rsi_commercants", 2013): (1.3, 0.0), ("rsi_artisans", 2013): (1.3, 0.0),
    # La valeur de 2022 de la RCI, au dépôt, est celle de janvier, la hausse
    # de 4 % du 1er juillet 2022 ne paraissant qu'en 2023 ; puis la DREES
    # prête à la RCI la revalorisation des régimes de base, quand le barème de
    # la Cnav (circulaires 2023/33 et 2024/36) lui donne 3,7 et 0,6 %. Les
    # règles des indépendants sont à la file D cette nuit : à elle de trancher.
    ("rsi_commercants", 2022): (5.1, 1.1), ("rsi_artisans", 2022): (5.1, 1.1),
    ("rsi_commercants", 2023): (0.8, 4.8), ("rsi_artisans", 2023): (0.8, 4.8),
    ("rsi_commercants", 2024): (5.3, 3.7), ("rsi_artisans", 2024): (5.3, 3.7),
    ("rsi_commercants", 2025): (2.2, 0.6), ("rsi_artisans", 2025): (2.2, 0.6),
    # La RCO des artisans : 0,29331 puis 0,29770 €, 1,5 % ; la DREES, 1,7 %.
    ("rsi_artisans", 2008): (1.7, 1.5),
}


def test_les_revalorisations_du_panorama_sont_celles_du_depot(regles):
    """Tableau 1 complémentaire de la fiche 4 : la revalorisation de chaque
    régime, d'une fin d'année à la suivante, de 2008 à 2025, au dixième de point,
    hors les écarts déclarés, chacun borné."""
    indices = _indices_des_regimes()
    restants = dict(ECARTS_DE_REVALORISATION)
    for ligne, annees in regles["valeurs"]["04_tableau_1_comp"].items():
        for annee, noeud in annees.items():
            annee = int(annee)
            au_depot = round(100 * (_au_31_decembre(indices[ligne], annee)
                                    / _au_31_decembre(indices[ligne], annee - 1) - 1), 1)
            if (ligne, annee) in restants:
                assert (noeud["valeur"], au_depot) == restants.pop((ligne, annee)), (ligne, annee)
            else:
                assert au_depot == noeud["valeur"], (ligne, annee)
    assert not restants


# --- Fiche 24 : la pension d'invalidité ---------------------------------------


def test_les_bornes_de_la_pension_d_invalidite_sont_celles_du_depot(regles):
    """Tableau 1 de la fiche 24, au 1er janvier 2026 : 30 et 50 % du salaire
    annuel moyen des dix meilleures années, au moins l'allocation aux vieux
    travailleurs salariés, au plus ces taux du plafond de la sécurité sociale.
    La majoration pour tierce personne, que le modèle ne sert pas, reste au
    panorama."""
    tableau = regles["valeurs"]["24_tableau_1"]
    fiche = yaml.safe_load((RACINE_DONNEES / "reference" / "regles"
                            / "pension_d_invalidite_substituee.yaml").read_text(encoding="utf-8"))
    parametres = fiche["versions"][-1]["contenu"]["parametres"]
    assert parametres["annees_du_salaire_moyen"] == 10
    avts = {l["date"]: float(l["valeur"]) for l in _csv("pension_minimum_avant_1983.csv")}
    with open(MACRO / "plafond_securite_sociale.csv", encoding="utf-8") as fichier:
        plafond = {int(l["annee"]): float(l["pass_eur"])
                   for l in csv.DictReader(x for x in fichier if not x.startswith("#"))}
    for categorie, taux in enumerate(parametres["taux_des_categories"], start=1):
        ligne = tableau[f"categorie_{categorie}"]
        assert ligne["taux"]["valeur"] == 100 * taux
        assert ligne["minimum"]["valeur"] == round(avts["2026-01-01"] / 12, 2)
        assert ligne["maximum"]["valeur"] == round(taux * plafond[2026] / 12, 2)
    assert tableau["tierce_personne"]["minimum"]["valeur"] == 1288.13


# --- Fiche 26 : le minimum vieillesse -----------------------------------------


#: Le montant mensuel d'une personne seule que le modèle sert, là où il
#: s'écarte de celui que le panorama publie au 31 décembre : (panorama, modèle).
ECARTS_DE_L_ASPA = {
    # Douze fois le mensuel arrondi, où la caisse fixe l'annuel : 7 455,24 €
    # contre 7 455,30 € en 2007, 11 532,96 contre 11 533,02 en 2023, 12 411,36
    # contre 12 411,44 en 2025 ; inscrit, « à décider » (test_ines.py,
    # douze_fois_le_mensuel).
    2007: (621.28, 621.27), 2023: (961.09, 961.08), 2025: (1034.29, 1034.28),
    # 2022 : la valeur de janvier, quand le couple et le panorama prennent celle
    # du 1er juillet ; inscrit, « à reprendre (138.2) » (test_ines.py,
    # bareme_de_2022).
    2022: (953.46, 916.78),
}


def test_le_minimum_vieillesse_du_panorama_est_celui_que_le_modele_sert(simulateur, regles):
    """Graphique 2 de la fiche 26 : le minimum vieillesse au 31 décembre de
    chaque année, depuis 2006, d'une personne seule et d'un couple
    d'allocataires, contre le montant annuel que le modèle sert, au centime,
    les années que la table ne porte pas comprises. L'allocation
    supplémentaire d'invalidité, que le modèle ne sert pas, reste au panorama.

    La lecture du graphique dit « fin 2025 […] 1 620 euros » pour un couple :
    c'est le montant de 2026 ; sa cellule de 2025 porte 1 605,73 €."""
    minimum = simulateur.scenario_actuel.minimum_vieillesse

    def au_centime(annuel: float, publie: float) -> bool:
        """Le mensuel du panorama est l'annuel divisé par douze, arrondi."""
        return abs(annuel / 12 - publie) <= 0.005 + 1e-9

    restants = dict(ECARTS_DE_L_ASPA)
    for annee, ligne in regles["valeurs"]["26_graphique_2"].items():
        annee = int(annee)
        seule = minimum.plafond(annee)[0]
        if annee in restants:
            assert not au_centime(seule, ligne["seule"]["valeur"]), annee
            assert (ligne["seule"]["valeur"], round(seule / 12, 2)) == restants.pop(annee), annee
        else:
            assert au_centime(seule, ligne["seule"]["valeur"]), (annee, seule)
        assert au_centime(minimum.plafond_couple(annee)[0], ligne["couple"]["valeur"]), annee
    assert not restants
    lecture = " ".join(regles["valeurs"]["26_graphique_2_lecture"]["valeur"].split())
    assert "Fin 2025, pour un couple, le montant du minimum vieillesse est de 1 620 euros" in lecture
    assert round(minimum.plafond_couple(2026)[0] / 12, 2) == 1620.18


def test_chaque_fiche_de_l_etape_5_nomme_ses_confrontations():
    """Au suivi, chaque fiche de l'étape 5 est confrontée, et nomme les tests
    de ce module qui la confrontent ; chacun existe."""
    suivi = yaml.safe_load(SUIVI.read_text(encoding="utf-8"))["fiches"]
    etape_5 = {numero: ligne for numero, ligne in suivi.items() if ligne.get("etape") == 5}
    assert sorted(etape_5) == ["02", "14", "24", "26"]
    module = sys.modules[__name__]
    for numero, ligne in etape_5.items():
        assert ligne["statut"] == "confronte", numero
        assert len(" ".join(str(ligne["confrontation"]).split())) > 40, numero
        for nom in ligne["confronte_par"]:
            assert nom.startswith("test_") and callable(getattr(module, nom, None)), (numero, nom)
