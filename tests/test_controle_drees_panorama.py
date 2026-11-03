"""Le panorama de la DREES, édition 2026, confronté au modèle (action 178, étape 4).

Douze fiches du suivi (``data/reference/drees_panorama_2026.yaml``) mesurent
ce que le modèle calcule ou suppose : la revalorisation des pensions servies,
le taux de remplacement, la pension des nouveaux retraités, les durées de
carrière, la polyaffiliation, les départs anticipés, le recours au minimum
vieillesse, la retraite supplémentaire. Ce module tient deux choses :

* LE TÉMOIN, ``tests/temoins/drees_panorama_2026_confrontations.json`` :
  chaque valeur confrontée, recopiée de sa cellule dans le classeur de sa
  fiche, et les phrases du PDF que les tests citent ; recoupé aux classeurs et
  au PDF quand ``data/brut/`` les porte
  (``python scripts/fetch/source_locale.py --recuperer``) ;
* LES CONFRONTATIONS, fiche par fiche. Un écart ne se corrige pas ici : il se
  déclare dans le test qui le mesure, borné, pour qu'un écart qui bouge se
  voie. Ceux qui disent une erreur du modèle sont consignés pour l'étape 5
  (``docs/feuille_de_route/178/2026-11-03-etape-4-confrontations.md``).
"""

from __future__ import annotations

import csv
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


def test_chaque_valeur_du_temoin_est_celle_de_sa_cellule(temoin):
    """Chaque valeur confrontée est celle que le classeur de sa fiche porte, à
    la cellule que le témoin nomme, au bit près."""
    archive = _depose("drees_panorama_retraites_2026_classeurs")
    if archive is None:
        pytest.skip("classeurs absents de data/brut/ : "
                    "python scripts/fetch/source_locale.py --recuperer")
    cellules = list(_cellules(temoin["valeurs"]))
    assert len(cellules) > 150
    grilles: dict = {}
    with zipfile.ZipFile(archive) as classeurs:
        for cellule in cellules:
            cle = (cellule["classeur"], cellule["feuille"])
            if cle not in grilles:
                grilles[cle] = lecture_xlsx.feuilles(
                    classeurs.read(cellule["classeur"]), (cellule["feuille"],))[cellule["feuille"]]
            assert grilles[cle].get(_indices(cellule["cellule"])) == cellule["valeur"], cellule


def test_chaque_citation_du_temoin_est_dans_le_pdf(temoin):
    """Les phrases que les tests citent sont celles du PDF, lu dans l'ordre de
    lecture, césures et espaces mis à part."""
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
    """Au suivi, chaque fiche de l'étape 4 est confrontée, et nomme les tests
    de ce module qui la confrontent ; chacun existe."""
    suivi = yaml.safe_load(SUIVI.read_text(encoding="utf-8"))["fiches"]
    etape_4 = {numero: ligne for numero, ligne in suivi.items() if ligne.get("etape") == 4}
    assert sorted(etape_4) == ["04", "06", "07", "09", "11", "13", "18", "28", "29", "30",
                               "31", "32"]
    module = sys.modules[__name__]
    for numero, ligne in etape_4.items():
        assert ligne["statut"] == "confronte", numero
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
