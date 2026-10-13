"""Le scénario 1 confronté à Ines, le modèle de l'INSEE, de la DREES et de la Cnaf, exécuté à part.

Ines applique la législation sociale et fiscale d'une année aux ménages de
l'ERFS. Il ne calcule pas la pension, qui y est une donnée, mais ce qui
l'entoure : les prélèvements selon le revenu fiscal du foyer, et l'ASPA. Le
registre (`data/reference/referents.yaml`, `ines`) le tient hors de toute
famille. Son code est sous CeCILL 2.1 : il s'exécute À PART, dans R
(`scripts/fetch/ines.py` et `ines.R`), et seules ses sorties entrent au dépôt,
figées dans `tests/temoins/ines.json` avec leur origine, leur licence, le
commit, les paramètres qu'il a lus et les seuils de revenu fiscal que la
caisse publie pour chaque année.

**Ce test n'exécute pas Ines.** Il rejoue ses foyers dans le scénario 1 :

* l'ASPA, par l'étape « foyer et net » (`droit/foyer.py`), sur les mêmes
  pensions brutes et le même conjoint, de 2021 à 2025. La règle et le barème
  se confrontent à part : la règle du dépôt, nourrie du barème d'Ines, doit
  redonner Ines au centime ; les deux barèmes, année par année, ne diffèrent
  que de ce que `BAREME_DE_L_ASPA` déclare ;
* la tranche de CSG, par la règle du dépôt (`PrelevementsPension.tranche`)
  sous les seuils de la caisse de chaque année, que le dépôt, qui nette aux
  seuils de 2026, ne porte pas ; puis, à la tranche d'Ines, la CSG, sa part
  déductible, la CRDS, la CASA et la cotisation maladie des complémentaires,
  aux taux que le dépôt tient pour l'année (`prelevements_historiques`), sur
  la pension brute qu'Ines reconstitue.

Chaque quantité concorde au centime, ou son écart est DÉCLARÉ avec sa cause et
ce qui le tranche (`ECARTS`) : un écart inexpliqué fait échouer le test, et un
écart déclaré qui n'en est plus un aussi. Ce que la première exécution a
montré, le 13 octobre 2026 :

* **Concordent** — les taux de CSG, leur part déductible, la CRDS et la CASA,
  dans chaque tranche, de 2023 à 2025 ; la règle de l'ASPA d'une personne
  seule et d'un couple, d'un ou de deux allocataires ; le barème de l'ASPA du
  couple de 2023 à 2025 ; la tranche de tous les foyers éloignés des seuils.
* **Contre Ines** — l'inégalité stricte aux seuils d'exonération et du taux
  réduit ; ses seuils à deux parts, faits de quatre quarts de part arrondis
  plutôt que de deux demi-parts (2 € de trop là où la demi-part est impaire) ;
  la cotisation maladie sous le seuil d'exonération ; au taux réduit, une
  pension brute reconstituée d'une cotisation maladie qu'il ne prélève pas ;
  la CRDS ajoutée à la pension brute que lit l'ASPA ; l'allocataire de l'ASPA
  prélevé ; le plafond du couple de 2021, 0,20 € sous celui de la caisse.
* **Contre le dépôt** — une personne seule servie de douze fois le mensuel
  arrondi, de 0,03 à 0,08 € par an sous le montant annuel de la caisse ; en
  2022, une seule valeur pour l'année, celle de janvier pour une personne
  seule et celle de juillet pour un couple, où Ines prend la moyenne des douze
  mois ; les revenus d'activité, que le dépôt ne compte pas aux ressources.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from retraite_notionnelle.contexte import Montants
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.prelevements_historiques import (
    charger_prelevements_historiques,
)
from retraite_notionnelle.droit import foyer
from retraite_notionnelle.remuneration import charger_prelevements
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "ines.json"
SCRIPT = RACINE / "scripts" / "fetch" / "ines.py"

#: Les écarts, chacun avec sa cause et ce qui le tranche. Le test vérifie que
#: chacun se produit encore, et qu'aucun autre ne se produit.
ECARTS = {
    # ---- Contre Ines -------------------------------------------------------
    "seuil_strict": (
        "Au seuil d'exonération et au seuil du taux réduit, Ines passe à la tranche "
        "suivante (`rfr < seuil`, R/12_cotisations.R, impot_ind) : L. 136-1-2, II 1° "
        "exonère le revenu qui « n'excède pas » le premier seuil, L. 136-8, III prend "
        "le taux réduit jusqu'au second « inférieur ou égal » (fiche "
        "csg_des_pensions_selon_le_revenu), et le barème de la caisse dit « si le "
        "revenu fiscal de référence dépasse »."),
    "quarts_de_part": (
        "Ines majore chaque seuil de quatre quarts de part par part supplémentaire "
        "(`pm_..._pac * 4 * (npart - 1)`), le quart de part arrondi à l'euro "
        "au-dessus : 2 € de trop à deux parts quand la demi-part est impaire (en "
        "2023 au premier seuil, en 2024 aux trois, en 2025 au troisième). La caisse "
        "majore de deux demi-parts (barème de chaque année, colonne « par demi-part "
        "supplémentaire »), et L. 136-8, III majore chaque seuil par demi-part."),
    "maladie_exoneree": (
        "Ines prélève la cotisation maladie des complémentaires sous le seuil "
        "d'exonération (`exo_csg == 1 ~ coprmal`) : D. 242-9, 1° l'exonère sous le "
        "seuil du taux réduit. Au registre depuis le 1er octobre 2026."),
    "brute_au_taux_reduit": (
        "Au taux réduit, Ines reconstitue la pension brute d'un ancien salarié du "
        "privé en retirant la cotisation maladie de sa part complémentaire, qu'il ne "
        "prélève pas (`coprmal` nul quand `reduc_csg`) : la brute en sort trop haute "
        "de cette cotisation, 0,23 % pour une part complémentaire de 22,5 %. D. 242-9, "
        "1° : pas de cotisation au taux réduit, donc rien à retirer."),
    "crds_dans_les_ressources": (
        "La pension brute qu'Ines donne à l'ASPA (`zrstbrut = zrsti + coprmal + "
        "csgprd + crdspr`) ajoute la CRDS, que le revenu imposable ne déduit pas "
        "(CGI, art. 154 quinquies et 83) : 0,5 % de trop aux ressources dès le taux "
        "réduit. La caisse retient « le montant brut avant cotisations » (base "
        "législative de la Cnav, « Evaluation des ressources - Aspa »)."),
    "allocataire_preleve": (
        "Ines prélève la CSG et la CRDS de la pension d'un allocataire de l'ASPA, "
        "écart qu'il déclare lui-même (R/12_cotisations.R, « Écart à la législation ») : "
        "L. 136-1-2, II 1° et D. 242-9, 2° l'exonèrent, et le dépôt aussi "
        "(`Montants.du_foyer`). Au registre depuis le 1er octobre 2026."),
    "plafond_couple_2021": (
        "Ines porte pour 2021 un plafond du couple de 16 893,74 € par an, douze mois "
        "durant (param_presta_mensuel.xlsx, Minima, mv_plfc) ; la caisse, 16 893,94 € "
        "au 1er janvier 2021, 1 407,82 € par mois (barème aspa_montant_bar, circulaire "
        "Cnav 2022/3), que le dépôt sert."),
    # ---- Contre le dépôt ---------------------------------------------------
    "douze_fois_le_mensuel": (
        "Le dépôt sert à une personne seule douze fois le montant mensuel arrondi "
        "(minimum_vieillesse.csv : 10 881,72 € en 2021) où la caisse fixe le montant "
        "annuel (10 881,75 €), qu'Ines porte : de 0,03 à 0,08 € par an. Connu à "
        "l'étape 2 de l'action 138, « à décider » : le mensuel affiché changerait."),
    "bareme_de_2022": (
        "Le dépôt ne tient qu'une valeur par an : pour 2022, celle de janvier pour une "
        "personne seule (11 001,36 €), celle du 1er juillet pour un couple "
        "(17 762,96 €). Ines prend la moyenne des douze mois de son barème mensuel, "
        "celui de la caisse, revalorisé de 4 % au 1er juillet 2022 (loi n° 2022-1158, "
        "art. 9). Le barème daté est au registre, à reprendre (138.2)."),
    "revenus_d_activite": (
        "Le dépôt ne compte aux ressources de l'ASPA que des pensions ; Ines y ajoute "
        "les revenus d'activité, abattus de quatre fois l'abattement trimestriel de "
        "R. 815-29. Reste de l'étape 2 de l'action 138."),
}

#: Le barème de l'ASPA, dépôt moins Ines, par année : une personne seule, un
#: couple. Chaque différence a sa cause dans `ECARTS`.
BAREME_DE_L_ASPA = {
    2021: ((-0.03, "douze_fois_le_mensuel"), (0.20, "plafond_couple_2021")),
    2022: ((-220.105, "bareme_de_2022"), (341.595, "bareme_de_2022")),
    2023: ((-0.06, "douze_fois_le_mensuel"), (0.0, None)),
    2024: ((-0.03, "douze_fois_le_mensuel"), (0.0, None)),
    2025: ((-0.08, "douze_fois_le_mensuel"), (0.0, None)),
}

TRANCHES = ("exonéré", "taux réduit", "taux médian", "taux plein")
#: La tranche dans les séries du dépôt (`prelevements_historiques`).
TAUX = {"taux réduit": "reduit", "taux médian": "median", "taux plein": "plein"}


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


@pytest.fixture(scope="module")
def historiques():
    return charger_prelevements_historiques(RACINE / "data")


@pytest.fixture(scope="module")
def bareme_2026():
    return charger_prelevements(RACINE / "data").pensions


def _tranche_d_ines(sortie: dict) -> str:
    if sortie["exo_csg"]:
        return "exonéré"
    if sortie["reduc_csg"]:
        return "taux réduit"
    return "taux médian" if sortie["interm_csg"] else "taux plein"


def _bareme_de_la_caisse(bareme_2026, seuils: dict):
    """La règle du dépôt, sous les seuils de la caisse d'une autre année : la
    première part et la demi-part de chacune des trois bornes."""
    tranches = list(bareme_2026.bareme_csg)
    for rang in range(3):
        tranches[rang] = dataclasses.replace(
            tranches[rang], revenu_fiscal_maximum=float(seuils["premiere_part"][rang]),
            majoration_demi_part=float(seuils["demi_part"][rang]))
    return dataclasses.replace(bareme_2026, bareme_csg=tuple(tranches))


def _seuils_d_ines(parametres: dict, parts: float) -> list[float]:
    """Les seuils qu'Ines compare au revenu fiscal : la première part, et quatre
    quarts de part par part supplémentaire."""
    return [parametres[f"pm_{nom}"] + parametres[f"pm_{nom}_pac"] * 4 * max(0.0, parts - 1)
            for nom in ("exo_csg_remp", "plaf_csg_remp", "plaf2_csg_ret")]


def _foyers(temoin):
    for code, cas in temoin["prelevements"].items():
        for annee, sortie in sorted(cas["par_annee"].items()):
            yield code, cas, int(annee), sortie


# ---- Le témoin --------------------------------------------------------------------

def test_le_temoin_dit_son_origine_sa_licence_et_sa_legislation(temoin):
    """Des sorties d'un code sous CeCILL n'entrent au dépôt qu'avec leur origine et
    leur licence (docs/architecture.md, § 3.4) ; une législation sans sa date ne
    dirait pas ce qu'on confronte."""
    assert temoin["code"] == "https://gitlab.com/insee_drees_cnaf/ines-public"
    assert re.fullmatch(r"[0-9a-f]{40}", temoin["commit"])
    assert "CeCILL 2.1" in temoin["licence"] and "ODbL" in temoin["licence"]
    assert "n'entre pas au dépôt" in temoin["origine"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", temoin["execute_le"])
    assert temoin["version"] == "Ines 2024.1"
    assert temoin["legislation"]["prelevements"] == [2023, 2024, 2025]
    assert temoin["legislation"]["aspa"] == [2021, 2022, 2023, 2024, 2025]
    for annee, seuils in temoin["seuils_de_la_caisse"].items():
        assert seuils["circulaire"].startswith("Circulaire Cnav"), annee
        assert seuils["bareme"].startswith("https://legislation.lassuranceretraite.fr/"), annee


def test_les_scripts_appellent_ines_sans_le_recopier():
    """Le script R du dépôt charge les fonctions d'Ines depuis son dossier et
    n'en évalue que les instructions qu'il nomme : aucune ligne de calcul d'Ines
    n'y entre."""
    script_r = SCRIPT.with_suffix(".R").read_text(encoding="utf-8")
    for chemin, texte in ((SCRIPT, SCRIPT.read_text(encoding="utf-8")),
                          (SCRIPT.with_suffix(".R"), script_r)):
        for ligne_d_ines in ("partretrcompl = case_when", "nb_elig_aspa1 = case_when",
                             "rev_aspa_abat = if_else", "reduc_csg =  (rfr == 0"):
            assert ligne_d_ines not in texte, (chemin.name, ligne_d_ines)
    assert 'sys.source(file.path("R", fichier)' in script_r
    assert 'instruction(calcule_cotis, "retraites", 1L)' in script_r
    assert "modelise_aspa_asi(" in script_r


# ---- La tranche de CSG ------------------------------------------------------------

def test_ines_classe_les_foyers_par_ses_propres_seuils(temoin):
    """Les deux écarts de classement d'Ines tiennent à sa règle, que le témoin
    redonne entière : ses seuils, quatre quarts de part par part, et une
    inégalité stricte aux trois. Si Ines change, l'explication tombe ici."""
    for code, cas, annee, sortie in _foyers(temoin):
        seuils = _seuils_d_ines(temoin["parametres_ines"][str(annee)], cas["parts"])
        revenu = sortie["revenu_fiscal"]
        attendue = next((TRANCHES[rang] for rang, seuil in enumerate(seuils)
                         if revenu < seuil), "taux plein")
        assert _tranche_d_ines(sortie) == attendue, (annee, code)


def test_la_tranche_du_depot_est_celle_de_la_caisse_ou_l_ecart_d_ines_est_declare(
        temoin, bareme_2026):
    """Sous les seuils de la caisse de l'année, la règle du dépôt range chaque
    foyer ; Ines le range ailleurs aux seuls cas que ses deux écarts expliquent,
    et chacun se produit."""
    vus = set()
    for code, cas, annee, sortie in _foyers(temoin):
        caisse = temoin["seuils_de_la_caisse"][str(annee)]
        depot = _bareme_de_la_caisse(bareme_2026, caisse).tranche(
            sortie["revenu_fiscal"], cas["parts"]).libelle
        ines = _tranche_d_ines(sortie)
        if depot == ines:
            continue
        rang = min(TRANCHES.index(depot), TRANCHES.index(ines))
        seuil_caisse = caisse["premiere_part"][rang] + 2 * (cas["parts"] - 1) * caisse["demi_part"][rang]
        seuil_ines = _seuils_d_ines(temoin["parametres_ines"][str(annee)], cas["parts"])[rang]
        if seuil_ines != seuil_caisse:
            cause = "quarts_de_part"
            assert seuil_ines - seuil_caisse == 2 and seuil_caisse <= sortie["revenu_fiscal"] < seuil_ines, (annee, code)
        else:
            cause = "seuil_strict"
            assert sortie["revenu_fiscal"] == seuil_caisse and rang < 2, (annee, code)
        vus.add(cause)
    assert vus == {"quarts_de_part", "seuil_strict"}


def test_le_bareme_de_2026_du_depot_suit_la_meme_regle(bareme_2026):
    """Le dépôt nette aux seuils de 2026 : à une et à deux parts, ceux de la caisse
    (barème de 2026, circulaire Cnav 2025/35) — 26 472 € et 40 604 € au taux plein."""
    assert bareme_2026.tranche(26471.0, 1).libelle == "taux médian"
    assert bareme_2026.tranche(26472.0, 1).libelle == "taux plein"
    assert bareme_2026.tranche(40603.0, 2).libelle == "taux médian"
    assert bareme_2026.tranche(40604.0, 2).libelle == "taux plein"
    assert bareme_2026.tranche(13048.0, 1).libelle == "exonéré"
    assert bareme_2026.tranche(17057.0, 1).libelle == "taux réduit"


# ---- Les montants prélevés --------------------------------------------------------

def test_les_taux_du_depot_redonnent_les_prelevements_d_ines(temoin, historiques):
    """À la tranche d'Ines et sur sa pension brute, les taux que le dépôt tient
    pour l'année redonnent sa CSG, sa part déductible, sa CRDS, sa CASA et sa
    cotisation maladie, au centime ; la cotisation maladie sous le seuil
    d'exonération est son écart."""
    vus = set()
    for code, cas, annee, sortie in _foyers(temoin):
        jour = dt.date(annee, 7, 1)
        tranche = _tranche_d_ines(sortie)
        brute = sortie["zpenu"]
        part = sortie["partretrcompl"] or 0.0
        preleve = tranche != "exonéré"
        csg = historiques.taux_csg_pension(jour, TAUX[tranche]) * brute if preleve else 0.0
        deductible = (historiques.csg_deductible_pension(jour, TAUX[tranche]) * brute
                      if preleve else 0.0)
        crds = historiques.pensions["crds"].valeur(jour) * brute if preleve else 0.0
        seconde = tranche in ("taux médian", "taux plein")
        casa = historiques.pensions["casa"].valeur(jour) * brute if seconde else 0.0
        maladie = (historiques.pensions["maladie_complementaires"].valeur(jour) * part * brute
                   if seconde else 0.0)
        cle = (annee, code)
        assert sortie["csgprd"] + sortie["csgpri"] == pytest.approx(csg, abs=1e-6), cle
        assert sortie["csgprd"] == pytest.approx(deductible, abs=1e-6), cle
        assert sortie["crdspr"] == pytest.approx(crds, abs=1e-6), cle
        assert sortie["casapr"] == pytest.approx(casa, abs=1e-6), cle
        if tranche == "exonéré" and part > 0:
            assert sortie["coprmal"] == pytest.approx(0.01 * part * brute, abs=1e-6), cle
            vus.add("maladie_exoneree")
        else:
            assert sortie["coprmal"] == pytest.approx(maladie, abs=1e-6), cle
    assert vus == {"maladie_exoneree"}


def test_la_pension_imposable_et_la_brute_d_ines(temoin):
    """La pension déclarée est la brute moins la CSG déductible et la cotisation
    maladie (CGI, art. 83 et 154 quinquies) : Ines la redonne, sauf au taux
    réduit d'un ancien salarié du privé. La brute qu'il donne à l'ASPA porte la
    CRDS en plus."""
    vus = set()
    for code, cas, annee, sortie in _foyers(temoin):
        cle = (annee, code)
        brute = sortie["zpenu"]
        imposable = brute - sortie["csgprd"] - sortie["coprmal"]
        part = sortie["partretrcompl"] or 0.0
        if _tranche_d_ines(sortie) == "taux réduit" and part > 0:
            assert cas["pension_imposable"] == pytest.approx(
                imposable - 0.01 * part * brute, abs=1e-6), cle
            vus.add("brute_au_taux_reduit")
            surplus = sortie["crdspr"] - 0.01 * part * brute
        else:
            assert cas["pension_imposable"] == pytest.approx(imposable, abs=1e-6), cle
            surplus = sortie["crdspr"]
        assert sortie["zrstbrut"] - brute == pytest.approx(surplus, abs=1e-6), cle
        if sortie["crdspr"] > 0:
            vus.add("crds_dans_les_ressources")
    assert vus == {"brute_au_taux_reduit", "crds_dans_les_ressources"}


# ---- L'ASPA -----------------------------------------------------------------------

class _BaremeFixe:
    """Le barème d'une année, tel qu'un autre modèle le lit : une personne seule,
    un couple, sans les deux étages d'avant 2007."""

    def __init__(self, seule: float, couple: float):
        self.seule, self.couple = seule, couple

    def plafond(self, annee):
        return self.seule, Fiabilite.HAUTE

    def plafond_couple(self, annee):
        return self.couple, Fiabilite.HAUTE

    def deux_etages(self, annee):
        return None


def _aspa_du_depot(simulateur, annee: int, personnes: list[dict], bareme=None) -> float:
    """L'ASPA que l'étape « foyer et net » sert à la première personne : ses
    pensions, et le conjoint, ses ressources et son âge."""
    actuel = simulateur.scenario_actuel
    moteur = actuel if bareme is None else SimpleNamespace(
        minimum_vieillesse=bareme, parametres=actuel.parametres, macro=actuel.macro,
        carrieres_hors_de_france=actuel.carrieres_hors_de_france)
    assure = personnes[0]
    conjoint = None
    if len(personnes) == 2:
        conjoint = {"naissance": f"{annee - personnes[1]['age']:04d}-07-01", "sexe": "F",
                    "mariage": None, "ressources": personnes[1]["pension_brute"],
                    "invalidite": None}
    carriere = simulateur.carriere_simple(
        annee_naissance=annee - assure["age"], sexe="H", affiliation="salarie_prive_non_cadre",
        age_liquidation=66.0, age_debut=20.0, niveau_salaire=0.3, conjoint=conjoint)
    return foyer.foyer_et_net(moteur, carriere.personne, f"{annee}-12-31", annee,
                              assure["pension_brute"], True, carriere=carriere).minimum_vieillesse


def _bareme_d_ines(temoin, annee: int) -> _BaremeFixe:
    parametres = temoin["parametres_ines"][str(annee)]
    # Le montant d'une personne seule et son plafond sont égaux depuis 2009 :
    # Ines les porte à part, le dépôt en une valeur.
    assert parametres["pm_mv_mi"] == parametres["pm_mv_plfi"]
    return _BaremeFixe(parametres["pm_mv_plfi"], parametres["pm_mv_plfc"])


def test_la_regle_de_l_aspa_du_depot_redonne_ines(temoin, simulateur):
    """Nourrie du barème d'Ines, l'étape du dépôt redonne son allocation au
    centime : une personne seule, un couple d'un ou de deux allocataires, sous
    ou au-dessus du plafond. Seul s'en écarte qui travaille encore : le dépôt
    ne compte que ses pensions."""
    vus = set()
    for code, cas in temoin["aspa"].items():
        for annee, sorties in sorted(cas["par_annee"].items()):
            annee = int(annee)
            ines = sorties[0]["aspa_eli"] or 0.0
            depot = _aspa_du_depot(simulateur, annee, cas["personnes"],
                                   _bareme_d_ines(temoin, annee))
            salaire = cas["personnes"][0]["salaire_brut"]
            if salaire > 0:
                abattement = 4 * temoin["parametres_ines"][str(annee)]["pm_abat_aspa_celib"]
                assert depot - ines == pytest.approx(max(0.0, salaire - abattement),
                                                     abs=1e-6), (annee, code)
                vus.add("revenus_d_activite")
            else:
                assert depot == pytest.approx(ines, abs=1e-6), (annee, code)
            if len(sorties) == 2 and sorties[1]["nb_elig_aspa"] == 2:
                # Deux allocataires : chacun la moitié de ce qui manque.
                assert sorties[1]["aspa_eli"] == pytest.approx(ines, abs=1e-9)
    assert vus == {"revenus_d_activite"}


def test_le_bareme_de_l_aspa_du_depot_et_celui_d_ines(temoin, simulateur):
    """Les deux barèmes, année par année : ce que `BAREME_DE_L_ASPA` déclare, au
    centime, et rien d'autre."""
    actuel = simulateur.scenario_actuel
    for annee, ((seule, cause_seule), (couple, cause_couple)) in BAREME_DE_L_ASPA.items():
        ines = _bareme_d_ines(temoin, annee)
        ecart_seule = actuel.minimum_vieillesse.plafond(annee)[0] - ines.seule
        ecart_couple = actuel.minimum_vieillesse.plafond_couple(annee)[0] - ines.couple
        assert ecart_seule == pytest.approx(seule, abs=1e-6), (annee, cause_seule)
        assert ecart_couple == pytest.approx(couple, abs=1e-6), (annee, cause_couple)
        for ecart, cause in ((seule, cause_seule), (couple, cause_couple)):
            assert (cause is None) == (ecart == 0.0), (annee, cause)
            assert cause is None or cause in ECARTS
    # Le barème d'Ines est celui de la caisse au centime en 2022 : les montants
    # du 1er janvier et du 1er juillet (circulaires Cnav 2022/19 et 2023/3).
    mois = temoin["parametres_ines"]["2022"]
    assert {mois[f"pm_mv_plfi_mois_{m:02d}"] for m in range(1, 7)} == {11001.44}
    assert {mois[f"pm_mv_plfi_mois_{m:02d}"] for m in range(7, 13)} == {11441.49}
    assert {mois[f"pm_mv_plfc_mois_{m:02d}"] for m in range(1, 7)} == {17079.77}
    assert {mois[f"pm_mv_plfc_mois_{m:02d}"] for m in range(7, 13)} == {17762.96}


def test_l_aspa_lit_chez_ines_une_brute_qui_porte_la_crds(temoin, simulateur):
    """La chaîne d'Ines : sa section des retraités reconstitue la brute, son ASPA
    la lit. Exonéré, l'allocataire reçoit ce que le dépôt lui sert sous le
    barème d'Ines ; au taux réduit, la CRDS de moins, et Ines le prélève."""
    vus = set()
    for code, cas in temoin["chaine"].items():
        for annee, sortie in sorted(cas["par_annee"].items()):
            annee = int(annee)
            personne = {"age": cas["age"], "pension_brute": sortie["zpenu"], "salaire_brut": 0}
            depot = _aspa_du_depot(simulateur, annee, [personne], _bareme_d_ines(temoin, annee))
            assert sortie["aspa_eli"] > 0, (annee, code)
            assert depot - sortie["aspa_eli"] == pytest.approx(sortie["crdspr"], abs=1e-6), (
                annee, code)
            if sortie["crdspr"] > 0:
                vus.add("crds_dans_les_ressources")
            if sortie["csgprd"] + sortie["crdspr"] > 0:
                vus.add("allocataire_preleve")
    assert vus == {"crds_dans_les_ressources", "allocataire_preleve"}


def test_le_depot_n_preleve_pas_l_allocataire_qu_ines_preleve(temoin, bareme_2026):
    """Le même allocataire, au taux réduit par son revenu fiscal : Ines prélève
    4,3 % de sa pension, le dépôt rien, l'ASPA exonérant de tout (L. 136-1-2,
    II 1° ; D. 242-9, 2°). Sans l'ASPA, le dépôt le range au taux réduit aussi."""
    cas = temoin["chaine"]["seul_taux_reduit"]
    saisie = Saisie.depuis_requete({
        "naissance": "1955-01-01", "debut": "1975-01", "liquidation": "2020-01",
        "unite_revenu": "moyen", "salaire": "0.3", "montants": "net",
        "revenu_fiscal": str(cas["revenu_fiscal"])})
    for annee, sortie in sorted(cas["par_annee"].items()):
        brute = sortie["zpenu"]
        actuel = SimpleNamespace(
            pensions_par_regime=[SimpleNamespace(regime="fonction_publique_etat", montant=brute)],
            pension_annuelle=brute,
            avantages_appliques=[SimpleNamespace(code="minimum_vieillesse",
                                                 montant=sortie["aspa_eli"])])
        allocataire = Montants.du_foyer(saisie, bareme_2026, actuel)
        assert allocataire.aspa and allocataire.taux_pension == 0.0, annee
        ines = (sortie["csgprd"] + sortie["csgpri"] + sortie["crdspr"]) / brute
        assert ines == pytest.approx(0.043, abs=1e-12), annee
        sans_aspa = SimpleNamespace(pensions_par_regime=actuel.pensions_par_regime,
                                    pension_annuelle=brute, avantages_appliques=[])
        assert Montants.du_foyer(saisie, bareme_2026, sans_aspa).tranche == "taux réduit"


def test_ines_rejoue_le_temoin(temoin, tmp_path):
    """Le témoin est ce qu'Ines produit : rejoué si R et le code d'Ines sont là et
    que `INES` le demande — le dossier de son code, et `INES_WSL` la
    distribution de la WSL, « aucune » pour Rscript du système. Les sorties
    figées suffisent à la confrontation ; les seuils de la caisse se relisent
    dans son API."""
    code_ines = os.environ.get("INES")
    if not code_ines:
        pytest.skip("les sorties figées suffisent : Ines ne se rejoue que sur demande "
                    "(INES=<dossier de son code>), R installé")
    distribution = os.environ.get("INES_WSL", "aucune")
    if shutil.which("Rscript" if distribution == "aucune" else "wsl") is None:
        pytest.skip("R introuvable sur ce poste")
    sys.path.insert(0, str(SCRIPT.parent))
    import ines as script  # noqa: E402

    sortie = tmp_path / "ines.json"
    script.SORTIE = sortie
    assert script.main(["--ines", code_ines, "--wsl", distribution]) == 0
    rejoue = json.loads(sortie.read_text(encoding="utf-8"))
    sans_date = lambda document: {k: v for k, v in document.items() if k != "execute_le"}
    assert sans_date(rejoue) == sans_date(temoin)
