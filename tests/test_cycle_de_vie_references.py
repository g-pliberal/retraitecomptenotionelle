"""Les indicateurs de cycle de vie confrontés au COR, à TRAJECTOiRE et à l'OCDE.

Le dépôt calcule depuis l'action 138 (étape 9) la durée de retraite, le taux de
récupération, le rendement interne et le patrimoine retraite de ses carrières
(``retraite_notionnelle.cycle_de_vie`` ; définitions dans
``tests/test_cycle_de_vie.py``). Trois références en publient, chacune sous ses
conventions, et ce module les refait sous les mêmes :

* LE COR, rapport annuel de juin 2026 (``tests/temoins/cor_cycle_de_vie.json``,
  ``scripts/fetch/cor_cycle_de_vie.py``) : l'espérance de vie à 60 ans de chaque
  génération, celle des projections de l'INSEE, et le rendement interne net du
  cas type n° 2, sur les carrières que TRAJECTOiRE a bâties pour lui ;
* TRAJECTOiRE, exécuté à part (``tests/temoins/trajectoire.json``) : sa durée de
  retraite rapportée à la carrière, son taux d'annuité, son taux de
  cotisation, sur les mêmes carrières ;
* L'OCDE, *Pensions at a Glance 2025* (``tests/temoins/ocde_pensions.json``,
  ``scripts/fetch/ocde_pensions.py``) : le taux de remplacement et le patrimoine
  retraite d'un salarié entré à 22 ans en 2024, sous ses hypothèses
  macroéconomiques (jeu ``ocde_2025``).

Chaque grandeur concorde à sa tolérance, ou son écart est DÉCLARÉ avec sa cause
et sa borne ; un écart déclaré qui rentrerait dans la tolérance fait échouer le
test, comme dans ``tests/test_trajectoire.py``.

Ce que la première confrontation a montré, le 7 octobre 2026 :

* **Concordent** — l'espérance de vie à 60 ans des générations 1960 à 2000,
  à 0,02 an près par sexe depuis l'étape 7, publiée le même soir : les tables
  du dépôt sont celles de l'INSEE ; la
  durée de retraite rapportée à la carrière de TRAJECTOiRE, exactement, sur
  ses cas types du COR, avec un âge de décès par génération ; le rendement
  interne net du cas type n° 2, à 0,3 point près, et son profil décroissant ;
  l'écart de rendement du cadre au non-cadre de la génération 2000 ; le
  coefficient de rente de l'OCDE des hommes.
* **Contre le dépôt** — la génération 1941, dont les quotients observés sont
  de 5 à 10 % sous ceux de ses voisines à chaque âge de 60 à 83 ans : son
  espérance de vie à 60 ans dépasse celle de l'INSEE de 0,3 an pour les
  hommes et de 0,2 pour les femmes, et son diviseur en hérite. À reprendre
  avec les données.
* **Des conventions** — le dépôt ne porte pas les contributions d'équilibre
  de l'Agirc-Arrco (AGFF, CEG, CET), que TRAJECTOiRE compte, et cotise à
  l'Arrco au taux minimal, TRAJECTOiRE au taux moyen des entreprises : son
  taux de cotisation du privé est inférieur de 10 à 12 %. Pour l'État, le dépôt
  compte la part de la contribution que la Cour des comptes rattache à la
  retraite de l'agent, TRAJECTOiRE et le COR la seule retenue. L'Agirc-Arrco
  que l'OCDE projette sert un quart de plus que celui du dépôt, sous la
  convention du COR. La mortalité de l'ONU fait vivre les femmes plus
  longtemps que celle de l'INSEE.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.castypes import CAS_TYPES, CasType
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
TEMOINS = RACINE / "tests" / "temoins"


def _temoin(nom: str) -> dict:
    return json.loads((TEMOINS / nom).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cor() -> dict:
    return _temoin("cor_cycle_de_vie.json")


@pytest.fixture(scope="module")
def trajectoire() -> dict:
    return _temoin("trajectoire.json")


@pytest.fixture(scope="module")
def ocde() -> dict:
    return _temoin("ocde_pensions.json")


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


@pytest.fixture(scope="module")
def simulateur(contexte) -> Simulateur:
    return contexte.simulateur()


# ---------------------------------------------------------------------------
# Le COR : l'espérance de vie à 60 ans, le rendement interne
# ---------------------------------------------------------------------------

#: Les générations dont l'espérance de vie à 60 ans s'écarte de celle de
#: l'INSEE, la cause, et la borne de l'écart (en années, par sexe).
ECARTS_ESPERANCE = {
    1941: ("les quotients observés de la génération 1941 sont de 5 à 10 % sous "
           "ceux de 1940 et de 1942 à chaque âge de 60 à 83 ans ; la table de "
           "génération de l'INSEE ne montre pas cette marche", 0.18, 0.40),
}


def test_l_esperance_de_vie_a_60_ans_des_generations_est_celle_de_l_insee(cor, simulateur):
    """Le COR publie, avec sa durée de retraite, l'espérance de vie à 60 ans de
    chaque génération de 1940 à 2000, par sexe, du scénario central des
    projections de l'INSEE (figure 3.6, données complémentaires). Le dépôt la
    retrouve sur ses tables de génération : à 0,05 an près dès la génération
    1960, dont il lit les quotients projetés de l'INSEE depuis l'étape 7 ; à
    0,15 an près avant, où ses quotients observés d'Eurostat ne sont pas
    exactement ceux que l'INSEE retient."""
    mortalite = simulateur.mortalite
    esperances = cor["duree_retraite"]["esperance_60"]
    for generation in range(1940, 2001):
        for sexe, qui in (("H", "hommes"), ("F", "femmes")):
            ecart = (mortalite.esperance_residuelle(60.0, generation + 60.0, sexe)
                     - esperances[qui][str(generation)])
            if generation in ECARTS_ESPERANCE:
                _, bas, haut = ECARTS_ESPERANCE[generation]
                assert bas <= ecart <= haut, (generation, sexe, ecart)
            else:
                tolerance = 0.05 if generation >= 1960 else 0.15
                assert abs(ecart) <= tolerance, (generation, sexe, ecart)


#: Les cas types n° 2 du COR que TRAJECTOiRE a bâtis pour le témoin.
GENERATIONS_CAS_TYPE_2 = (1955, 1960, 1963, 1964, 1970)


@pytest.fixture(scope="module")
def cas_type_2(trajectoire, contexte, simulateur) -> dict[int, object]:
    return {generation: contexte.simuler(Saisie.depuis_requete(
                dict(trajectoire["cas"][f"cor_2_{generation}"]["requete"])))
            for generation in GENERATIONS_CAS_TYPE_2}


def test_le_rendement_interne_du_cas_type_2_est_celui_du_cor(cor, cas_type_2, simulateur):
    """Le COR publie le rendement interne net de son cas type n° 2, flux
    actualisés selon le salaire moyen (figure 3.7). Sous ses conventions —
    les deux sexes réunis, le décès à 60 ans plus l'espérance de vie à 60 ans
    de la génération, la pension nette au taux plein, les cotisations seules
    — et sur les carrières que TRAJECTOiRE a bâties pour lui, le dépôt le
    retrouve à 0,3 point près, et décroissant comme lui de 1955 à 1970.

    Ce qui sépare encore les deux : le dépôt prélève toute la retraite aux
    taux de 2026, quand la CSG d'une pension était de 6,6 % jusqu'en 2017 —
    le rendement des générations 1955 et 1960 en est abaissé — ; il ne porte
    pas l'AGFF ni la CEG — le rendement en est relevé — ; et ses carrières
    sont celles de TRAJECTOiRE, non celles du secrétariat général du COR."""
    publie = cor["rendement_cas_type_2"]
    calcules = {}
    for generation, comparaison in cas_type_2.items():
        flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"]
        calcules[generation] = cycle_de_vie.indicateurs(
            flux, simulateur, cycle_de_vie.convention_cor(simulateur, comparaison)
        ).rendement_smpt
        assert abs(calcules[generation] - publie[str(generation)]) <= 0.0035, (
            generation, calcules[generation], publie[str(generation)])
    rangs = list(GENERATIONS_CAS_TYPE_2)
    assert all(calcules[a] > calcules[b] for a, b in zip(rangs, rangs[1:]))
    assert all(publie[str(a)] > publie[str(b)] for a, b in zip(rangs, rangs[1:]))


def test_le_rendement_du_cadre_est_sous_celui_du_non_cadre_comme_au_cor(cor, simulateur):
    """Génération 2000 (figure 3.A) : le cadre rend 0,04 %, le non-cadre
    0,83 %, parce qu'une part de la rémunération du cadre cotise au-dessus du
    plafond sans ouvrir de droit au régime général. Sous les mêmes
    conventions, le cadre et le salarié au salaire moyen de la grille
    s'écartent d'autant, à 0,2 point près."""
    publie = cor["rendement_generation_2000"]
    ecart_publie = publie["cadre"]["total"] - publie["non_cadre"]["total"]
    rendements = {}
    for code in ("cadre", "salaire_moyen"):
        cas = next(c for c in CAS_TYPES if c.code == code)
        comparaison = simulateur.simuler(cas.construire(simulateur, 2000))
        flux = cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"]
        rendements[code] = cycle_de_vie.indicateurs(
            flux, simulateur, cycle_de_vie.convention_cor(simulateur, comparaison)
        ).rendement_smpt
    ecart = rendements["cadre"] - rendements["salaire_moyen"]
    assert ecart < 0.0 and ecart_publie < 0.0
    assert abs(ecart - ecart_publie) <= 0.002, (ecart, ecart_publie)


# ---------------------------------------------------------------------------
# TRAJECTOiRE : la durée, le flux des pensions, la cotisation
# ---------------------------------------------------------------------------

#: L'âge de décès des cas types du COR dans TRAJECTOiRE, par génération :
#: ``round(60 + e60)`` de la table du COR (``casTypesCOR.R``, l. 94), plus les
#: six mois que son calcul ajoute (``fonctionsCalculsPensions.R``, l. 4692).
AGES_DE_DECES_TRAJECTOIRE = {1955: 86.5, 1960: 87.5, 1963: 87.5, 1964: 87.5, 1970: 88.5}

#: Les cas dont TRAJECTOiRE compte d'autres années de carrière que le dépôt,
#: et la cause ; l'âge de décès qu'on en déduirait s'écarte alors du sien.
CARRIERES_COMPTEES_AUTREMENT = {
    "cor_3_1955": "une année de chômage, que TRAJECTOiRE compte comme une année "
                  "de carrière quand son script lui donne un revenu",
    "cor_4_1955": "des années d'AVPF, dont TRAJECTOiRE multiplie l'assiette par "
                  "douze et qu'il compte comme des années de carrière",
    "cor_4_1963": "des années d'AVPF, comptées par TRAJECTOiRE",
    "cor_4_1964": "des années d'AVPF, comptées par TRAJECTOiRE",
}


def _cas_du_cor(trajectoire: dict) -> list[tuple[str, int, dict]]:
    cas = []
    for cle, contenu in sorted(trajectoire["cas"].items()):
        if contenu.get("jeu") == "cas_types_cor" and contenu["trajectoire"].get("indicateurs"):
            cas.append((cle, int(contenu["generation"]), contenu))
    return cas


@pytest.fixture(scope="module")
def flux_trajectoire(trajectoire, contexte, simulateur) -> dict[str, tuple]:
    """Chaque carrière du témoin rejouée, et le flux du scénario 1."""
    rejoues = {}
    for cle, contenu in sorted(trajectoire["cas"].items()):
        if "requete" not in contenu or not contenu["trajectoire"].get("indicateurs"):
            continue
        comparaison = contexte.simuler(Saisie.depuis_requete(dict(contenu["requete"])))
        rejoues[cle] = (comparaison,
                        cycle_de_vie.flux_des_systemes(simulateur, comparaison)["actuel"])
    return rejoues


def test_la_duree_de_retraite_rapportee_a_la_carriere_est_celle_de_trajectoire(
        trajectoire, flux_trajectoire):
    """TRAJECTOiRE rapporte la durée de retraite au nombre d'années de
    carrière (``dureeRetraiteRelativeDureeCotisation``). Le dépôt compte les
    mêmes années et liquide à la même date : sur chaque cas type du COR,
    l'âge de décès que son rapport implique est celui de la génération, au
    mois près, sauf où l'un compte des années que l'autre ne compte pas."""
    for cle, generation, contenu in _cas_du_cor(trajectoire):
        _, flux = flux_trajectoire[cle]
        rapport = contenu["trajectoire"]["indicateurs"]["dureeRetraiteRelativeDureeCotisation"]
        implicite = flux.age + rapport * flux.duree_carriere
        attendu = AGES_DE_DECES_TRAJECTOIRE[generation]
        if cle in CARRIERES_COMPTEES_AUTREMENT:
            assert abs(implicite - attendu) > 1.0 / 12.0, cle
        else:
            assert implicite == pytest.approx(attendu, abs=1.0 / 24.0), cle


#: Les carrières d'un seul statut à la fois : TRAJECTOiRE compte jusqu'à seize
#: fois le revenu d'une année partagée entre deux états (``test_trajectoire``),
#: ce qui fausse son taux d'annuité ailleurs ; ses âges et durées des emplois
#: actifs et super-actifs sont les siens.
UN_SEUL_STATUT = ("cor_2_", "cor_2bis_", "cor_5_", "cor_6_", "cor_7_", "cor_10_",
                  "cor_11_", "rg_", "fp_", "loi_2023_")


def _pension_de_trajectoire(contenu: dict) -> float:
    """La pension annuelle au départ, hors RAFP, que le dépôt sert à part."""
    return 12.0 * sum(caisse["pension_mensuelle"]
                      for nom, caisse in contenu["trajectoire"]["caisses"].items()
                      if nom != "Rafp")


def _convention_trajectoire(contenu: dict, flux) -> cycle_de_vie.Convention:
    """Le décès que le rapport de TRAJECTOiRE implique, les deux sexes réunis."""
    rapport = contenu["trajectoire"]["indicateurs"]["dureeRetraiteRelativeDureeCotisation"]
    return cycle_de_vie.Convention(age_deces=flux.age + rapport * flux.duree_carriere,
                                   unisexe=True)


def test_le_flux_des_pensions_a_l_allure_de_celui_de_trajectoire(trajectoire, flux_trajectoire,
                                                                  simulateur):
    """Le taux d'annuité de TRAJECTOiRE (``txAnnuite``) rapporte la somme des
    pensions de la retraite à celle des revenus de la carrière, en salaire
    moyen. La pension de départ des deux modèles est confrontée ailleurs
    (``test_trajectoire``) ; recalée sur celle de TRAJECTOiRE, celle du dépôt
    en garde l'allure : 0,88 à 1,05 fois son taux d'annuité.

    Ce qui reste : TRAJECTOiRE projette le salaire moyen à 1 % de croissance
    réelle, le dépôt à 0,7 % ; il projette ses paramètres depuis 2024, et
    revalorise la pension au mois, le dépôt à l'année, au niveau du 31
    décembre ; il sert la RAFP, que le dépôt sert à part."""
    for cle, (comparaison, flux) in flux_trajectoire.items():
        if not cle.startswith(UN_SEUL_STATUT):
            continue
        contenu = trajectoire["cas"][cle]
        rapport = _pension_de_trajectoire(contenu) / flux.niveaux[flux.annee_liquidation]
        recale = replace(flux, niveaux={annee: niveau * rapport
                                        for annee, niveau in flux.niveaux.items()})
        annuite = cycle_de_vie.indicateurs(
            recale, simulateur, _convention_trajectoire(contenu, flux)).taux_annuite
        ratio = annuite / contenu["trajectoire"]["indicateurs"]["txAnnuite"]
        assert 0.88 <= ratio <= 1.05, (cle, ratio)


#: Les carrières du privé, non cadres, d'un seul statut.
PRIVE_NON_CADRE = ("cor_2_", "cor_2bis_", "rg_salaire_moyen", "rg_bas_salaire",
                   "rg_pere_trois_enfants", "rg_ne_en_octobre", "loi_2023_salaire_moyen")


def _taux_de_cotisation(indicateurs) -> float:
    """Cotisations sur revenus, en salaire moyen : le taux d'annuité divisé
    par le taux de récupération."""
    return indicateurs.taux_annuite / indicateurs.taux_recuperation


def _taux_moyens_arrco(trajectoire: dict) -> dict[int, float]:
    """Le rapport du taux contractuel moyen de l'Arrco au taux minimal, par
    année, sous le plafond : les paramètres que le témoin garde."""
    rapports = {}
    for ligne in trajectoire["parametres_trajectoire"]["annuels"]:
        valeurs = dict(re.findall(r"(\w+)=([\d.]+)", ligne))
        if "txCotMIN_ARRCOsalempl_t1" in valeurs:
            rapports[int(ligne.split()[0])] = (float(valeurs["txCotARRCOsalempl_t1"])
                                               / float(valeurs["txCotMIN_ARRCOsalempl_t1"]))
    return rapports


def test_le_taux_de_cotisation_du_prive_est_celui_de_trajectoire_aux_conventions_pres(
        trajectoire, flux_trajectoire, simulateur):
    """TRAJECTOiRE cotise davantage, pour deux raisons que le dépôt connaît :
    il prend à l'Arrco le taux contractuel moyen des entreprises — 5,42 % de
    1960 à 1998, contre 4 % au minimum —, et il compte les contributions
    d'équilibre, l'AGFF de 2001 à 2018 et la CEG depuis 2019, que le compte
    notionnel ne porte pas, par un choix que les limites déclarent. Le taux
    de cotisation du dépôt est de 9 à 14 % sous le sien ; aux taux moyens de
    TRAJECTOiRE, l'écart se réduit de 2 à 5 points — d'autant plus que la
    carrière a d'années d'avant 1999 —, et ce qui en reste, 7 à 8 %, est celui
    des contributions d'équilibre."""
    moyens = _taux_moyens_arrco(trajectoire)
    for cle, (comparaison, flux) in flux_trajectoire.items():
        if not cle.startswith(PRIVE_NON_CADRE):
            continue
        contenu = trajectoire["cas"][cle]
        convention = _convention_trajectoire(contenu, flux)
        publie = (contenu["trajectoire"]["indicateurs"]["txAnnuite"]
                  / contenu["trajectoire"]["indicateurs"]["txRecuperation"])
        rapport = _taux_de_cotisation(cycle_de_vie.indicateurs(flux, simulateur, convention)) / publie
        assert 0.86 <= rapport <= 0.91, (cle, rapport)
        carriere = comparaison.carriere
        compte = simulateur.constructeur_employeur.construire(
            carriere, annee_liquidation=carriere.annee_liquidation,
            annee_debut=carriere.premiere_annee)
        aux_taux_moyens: dict[int, float] = {}
        for ligne in compte.cotisations:
            for regime, montant in ligne.par_regime:
                if regime in ("arrco", "agirc_arrco"):
                    montant *= moyens.get(ligne.annee, 1.0)
                aux_taux_moyens[ligne.annee] = aux_taux_moyens.get(ligne.annee, 0.0) + montant
        refait = _taux_de_cotisation(cycle_de_vie.indicateurs(
            replace(flux, cotisations=aux_taux_moyens), simulateur, convention)) / publie
        assert refait - rapport >= 0.02, (cle, rapport, refait)
        assert 0.91 <= refait <= 0.95, (cle, refait)


#: Les fonctionnaires de l'État des cas types du COR et du témoin de Destinie.
ETAT = ("cor_5_", "cor_6_", "cor_7_", "fp_", "loi_2023_fp_etat")
REGIMES_ETAT = {"fonction_publique_etat", "fonction_publique_etat_civile",
                "fonction_publique_etat_militaire"}


def test_pour_l_etat_trajectoire_ne_compte_que_la_retenue_de_l_agent(
        trajectoire, flux_trajectoire, simulateur):
    """TRAJECTOiRE ne compte, pour l'État, aucune contribution d'employeur
    (``fonctionsCalculsDivers.R``, l. 403-407), comme le COR, pour qui elle
    « ne reflète que le montant de la contribution qui permet de garantir en
    dernier ressort l'équilibre du régime ». Le dépôt en compte la part que
    la Cour des comptes rattache à la retraite de l'agent : son taux de
    cotisation est trois à six fois celui de TRAJECTOiRE. Réduit à la seule
    retenue les années à l'État, il est le sien à la RAFP près, que
    TRAJECTOiRE compte et que le dépôt sert à part."""
    salariale = simulateur.constructeur_de(simulateur.calculs["notionnel_retroactif"])
    for cle, (comparaison, flux) in flux_trajectoire.items():
        if not cle.startswith(ETAT):
            continue
        contenu = trajectoire["cas"][cle]
        convention = _convention_trajectoire(contenu, flux)
        publie = (contenu["trajectoire"]["indicateurs"]["txAnnuite"]
                  / contenu["trajectoire"]["indicateurs"]["txRecuperation"])
        rapport = _taux_de_cotisation(cycle_de_vie.indicateurs(flux, simulateur, convention)) / publie
        assert 3.0 <= rapport <= 6.0, (cle, rapport)
        carriere = comparaison.carriere
        bornes = dict(annee_liquidation=carriere.annee_liquidation,
                      annee_debut=carriere.premiere_annee)
        retenues = salariale.construire(carriere, **bornes).cotisations
        entieres = simulateur.constructeur_employeur.construire(carriere, **bornes).cotisations
        refaites: dict[int, float] = {}
        for retenue, entiere in zip(retenues, entieres):
            assert retenue.annee == entiere.annee
            etat = any(regime in REGIMES_ETAT for regime in entiere.regimes)
            refaites[entiere.annee] = (refaites.get(entiere.annee, 0.0)
                                       + (retenue.cotisation if etat else entiere.cotisation))
        refait = _taux_de_cotisation(cycle_de_vie.indicateurs(
            replace(flux, cotisations=refaites), simulateur, convention)) / publie
        assert 0.74 <= refait <= 0.97, (cle, refait)


# ---------------------------------------------------------------------------
# L'OCDE : le taux de remplacement et le patrimoine retraite
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def simulateur_ocde() -> Simulateur:
    return Simulateur(Parametres(scenario_projection="ocde_2025"))


@pytest.fixture(scope="module")
def carrieres_ocde(ocde, simulateur_ocde) -> dict[tuple[str, str], object]:
    """Le salarié de l'OCDE : né en 2002, entré à 22 ans, toute sa carrière
    au même multiple du salaire moyen de l'OCDE, parti à l'âge qu'elle lui
    donne, et non cadre — l'Agirc-Arrco ne distingue plus depuis 2019."""
    macro = simulateur_ocde.macro
    age = ocde["age_de_depart"]["futur"]["hommes"]
    salaire_moyen = ocde["salaire_moyen"] / macro.salaire_moyen_niveau(2024)
    carrieres = {}
    for sexe in ("H", "F"):
        for multiple in ("0.5", "1", "2"):
            carriere = simulateur_ocde.carriere_simple(
                annee_naissance=2002, sexe=sexe, affiliation="salarie_prive_non_cadre",
                age_debut=22, age_liquidation=age,
                niveau_salaire=float(multiple) * salaire_moyen, profil_carriere="plat")
            carrieres[(sexe, multiple)] = simulateur_ocde.simuler(carriere)
    return carrieres


def test_le_salarie_de_l_ocde_part_au_taux_plein_a_l_age_qu_elle_lui_donne(ocde, simulateur_ocde):
    """Entré à 22 ans en 2024, il atteint les 172 trimestres à 65 ans : l'âge
    que l'OCDE écrit (``FRPLF22``), et celui où le pilote du dépôt le fait
    partir au taux plein."""
    cas = CasType(code="ocde", libelle="Salarié de l'OCDE", affiliation="salarie_prive_non_cadre",
                  age_debut=22, age_liquidation=64, niveau_salaire=1.0, profil_carriere="plat")
    assert cas.age_liquidation_pour(simulateur_ocde, 2002) == ocde["age_de_depart"]["futur"]["hommes"]


def _part_complementaire(comparaison) -> float:
    return sum(p.montant for p in comparaison.actuel.pensions_par_regime
               if p.regime.startswith(("agirc", "arrco"))) / comparaison.dernier_revenu_annualise


def test_le_taux_de_remplacement_brut_de_l_ocde_se_retrouve_a_l_agirc_arrco_pres(
        ocde, carrieres_ocde):
    """Au salaire moyen, le régime général du dépôt sert 42,7 % du dernier
    salaire : la moitié d'un salaire annuel moyen revalorisé sur les prix,
    quand les salaires réels montent de 1,25 % par an. L'écart à l'OCDE —
    2,7 points au salaire moyen, 4,9 à deux fois — est celui de
    l'Agirc-Arrco : il est, aux deux niveaux, le même quart de la pension
    complémentaire du dépôt, dont la valeur de service suit la convention du
    COR — le salaire moyen moins 1,16 point jusqu'en 2037, moins 0,86 ensuite
    — sous la valeur d'achat. À la moitié du salaire moyen, le minimum
    contributif, indexé sur le SMIC depuis 2023, relève le dépôt d'un point
    au-dessus de l'OCDE, dont le taux est celui du salaire moyen."""
    publies = ocde["taux_remplacement_brut"]["hommes"]
    facteurs = {}
    for multiple in ("0.5", "1", "2"):
        comparaison = carrieres_ocde[("H", multiple)]
        taux = 100.0 * comparaison.taux_remplacement_actuel
        assert abs(taux - publies[multiple]) <= 5.5, (multiple, taux, publies[multiple])
        if multiple != "0.5":
            facteurs[multiple] = ((publies[multiple] - taux) / 100.0
                                  / _part_complementaire(comparaison))
    assert 0.15 <= facteurs["1"] <= 0.35
    assert facteurs["2"] == pytest.approx(facteurs["1"], abs=0.05)
    assert 100.0 * carrieres_ocde[("H", "0.5")].taux_remplacement_actuel > publies["0.5"]


def test_le_patrimoine_retraite_de_l_ocde_se_retrouve_a_la_mortalite_pres(
        ocde, carrieres_ocde, simulateur_ocde):
    """Le patrimoine retraite est le taux de remplacement multiplié par la
    valeur d'un euro de rente : celle-ci, à 1,5 % réel sur la survie de
    génération, est celle de l'OCDE à 3 % près pour les hommes. Pour les
    femmes, la mortalité de l'ONU que l'OCDE retient les fait vivre plus
    longtemps que celle de l'INSEE que le dépôt suit : leur rente vaut 3 à
    8 % de moins au dépôt."""
    for sexe, qui, bas, haut in (("H", "hommes", -0.03, 0.03),
                                 ("F", "femmes", -0.08, -0.03)):
        for multiple in ("0.5", "1"):
            comparaison = carrieres_ocde[(sexe, multiple)]
            flux = cycle_de_vie.flux_des_systemes(simulateur_ocde, comparaison)["actuel"]
            patrimoine = cycle_de_vie.indicateurs(flux, simulateur_ocde).patrimoine
            rente = patrimoine / comparaison.taux_remplacement_actuel
            rente_publiee = (ocde["patrimoine_brut"][qui][multiple]
                             / (ocde["taux_remplacement_brut"][qui][multiple] / 100.0))
            ecart = rente / rente_publiee - 1.0
            assert bas <= ecart <= haut, (sexe, multiple, ecart)
