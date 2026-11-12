"""Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node.

La note de décision 0003 veut que le coût, la fabrique et les études fassent
tourner le moteur JavaScript au lieu du moteur Python, sous six conditions
(action 161, étape 5). La première lecture qui passe le pont est la grille des
carrières types de la table des agrégats, avec les deux départs que compare
Droits non cotisés (``scripts/construire_donnees.py``) ; ``test_agregats.py``
exige, à l'égalité exacte, que la table soit ce que le moteur Python calcule.
Puis le bilan figé : la même grille, dont il tire les écarts médians, et les
carrières d'exemple de « Pourquoi changer », simulées comme le site simule une
saisie ; ``test_cout.py`` et le contrôle de ``test_affirmations.py`` exigent
de même la table du moteur Python. Puis la grille du coût, sous les
conventions de projection du COR, que le portage date, bâtit et simule : le
Python ne lui passe que ce que chaque cas type décrit (action 161, étape 6).
Ici : le pont rend au bit près ce que le moteur Python date, bâtit et simule,
chaque nombre sous le type que le Python lui donne ; et, sans node, il
s'arrête, sans repli sur le moteur Python.
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import fields, replace

import pytest

from retraite_notionnelle import Parametres, pont
from retraite_notionnelle.droit import liquidation
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.castypes import (
    CAS_TYPES, GENERATIONS, GRILLE_DU_COUT, carriere_de_la_grille, cases_de_la_grille)
from retraite_notionnelle.config import RACINE_DONNEES, RACINE_PROJET
from retraite_notionnelle.simulateur import Simulateur

from outils_pont import (TOLERANCE_DU_MOTEUR_PYTHON, Saisies, ecarts_d_ecriture,
                         empecher_les_jumeaux_du_cout)

SCENARIOS = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

#: Des cases de la grille où passe ce que le pont fait traverser : un profil au
#: SMIC, des interruptions, des primes, la catégorie active, un non-salarié, un
#: exploitant ; plusieurs s'écartaient au dernier bit avant que le portage
#: calcule ses exponentielles comme la libm de Linux.
CASES = (("smic_carriere_complete", 1970), ("carriere_interrompue", 1970),
         ("fonctionnaire_actif", 1960), ("fonctionnaire_sedentaire", 2000),
         ("profession_liberale", 1960), ("exploitant_agricole", 2000), ("cadre", 2000))

#: Des saisies comme celles que le bilan figé simule : la carrière d'exemple de
#: « Pourquoi changer » au SMIC, et un cadre à deux fois le salaire moyen.
SAISIES = (
    {"naissance": 1990, "statut": "salarie_prive_non_cadre", "debut": 22, "liquidation": 64,
     "salaire": 0.55, "unite_revenu": "moyen", "demandee": True},
    {"naissance": 1975, "statut": "salarie_prive_cadre", "debut": 24, "liquidation": 65,
     "salaire": 2.0, "unite_revenu": "moyen", "demandee": True},
)


def _aujourd_hui(aujourd_hui, scenarios=SCENARIOS) -> dict | None:
    """Ce que les écarts médians lisent de la pension d'aujourd'hui d'un
    retraité, ou rien pour qui n'est pas encore parti."""
    if aujourd_hui is None:
        return None
    return {
        "pension_annuelle": aujourd_hui.pension("actuel"),
        "pensions_totales": {scenario: aujourd_hui.pension_totale(scenario)
                             for scenario in scenarios},
        "rente_capitalisee_volontaire": aujourd_hui.rente_capitalisee_volontaire,
    }


def _carrieres_simulees(simulateur: Simulateur, scenarios=SCENARIOS,
                        ) -> tuple[list[dict], dict[str, dict]]:
    """Les cases de ``CASES``, demandées au pont, et ce que le moteur Python en
    simule de ``scenarios``, sous les univers et les paramètres de
    ``simulateur``."""
    demandes, attendus = [], {}
    for code, generation in CASES:
        cas = next(cas for cas in CAS_TYPES if cas.code == code)
        carriere = carriere_de_la_grille(simulateur, cas, generation)
        comparaison = simulateur.simuler(carriere)
        cle = f"{code}|{generation}"
        demandes.append({"cle": cle, "options": cas.options(generation, carriere.age_liquidation)})
        attendus[cle] = {
            "annee_liquidation": comparaison.carriere.annee_liquidation,
            "annees_liquidation": {scenario: comparaison.carriere_de(scenario).annee_liquidation
                                   for scenario in scenarios},
            "variations": {scenario: comparaison.variation_totale(scenario)
                           for scenario in scenarios},
            # L'écart hors du pilier, que les études lisent des cas types.
            "ecarts": {scenario: comparaison.variation(scenario) for scenario in scenarios},
            "pension_annuelle": comparaison.actuel.pension_annuelle,
            "trimestres_requis": comparaison.actuel.trimestres_requis,
            # Ce que les écarts médians du bilan lisent d'une case.
            "pensions_totales": {scenario: comparaison.pension_totale(scenario)
                                 for scenario in scenarios},
            "rentes_volontaires": {scenario: comparaison.rente_capitalisee_volontaire(scenario)
                                   for scenario in scenarios},
            # La pension de l'étalon et de chaque scénario, hors du pilier, en
            # euros constants : ce que ``scripts/stock_age_legal.py`` lit.
            "pensions_euros_constants": {
                scenario: comparaison.en_euros_constants(
                    getattr(comparaison, scenario).pension_annuelle, scenario)
                for scenario in ("actuel", *scenarios)},
            "aujourd_hui": _aujourd_hui(comparaison.aujourd_hui, scenarios),
        }
    return demandes, attendus


def test_le_pont_rend_au_bit_pres_ce_que_le_moteur_python_simule():
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    demandes, attendus = _carrieres_simulees(Simulateur(Parametres()))
    resultats, echecs = pont.carrieres(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    # Les deux sortes de cases : celles qui partiront, celles déjà parties.
    assert {lu["aujourd_hui"] is None for lu in resultats.values()} == {True, False}
    for lu in resultats.values():
        assert type(lu["annee_liquidation"]) is int
        assert type(lu["trimestres_requis"]) is int
        assert type(lu["pension_annuelle"]) is float
        for lecture in ("variations", "ecarts", "pensions_totales", "rentes_volontaires",
                        "pensions_euros_constants"):
            assert all(type(nombre) is float for nombre in lu[lecture].values()), lecture
        if lu["aujourd_hui"] is not None:
            assert type(lu["aujourd_hui"]["pension_annuelle"]) is float
            assert type(lu["aujourd_hui"]["rente_capitalisee_volontaire"]) is float
            assert all(type(nombre) is float
                       for nombre in lu["aujourd_hui"]["pensions_totales"].values())


def _variantes() -> dict:
    """La proposition prospective, à la place du scénario 6
    (``scripts/proposition_prospective.py``, action 161)."""
    from retraite_notionnelle.noyau import univers

    return {"notionnel_liberal":
            univers.charger(univers.VARIANTES)["notionnel_liberal_prospectif"]}


def test_une_variante_passe_au_portage_dans_la_demande_au_bit_pres_du_jumeau():
    """Un univers que le paquet ne porte pas — la proposition prospective, à
    la place du scénario 6 (action 161) — passe au portage dans la demande, son
    calcul tel que la fabrication le résout : le portage rend, de chaque case,
    ce que le jumeau Python simule de la même variante, au bit près, et autre
    chose que le scénario 6, sur les cases déjà parties comme sur celles qui
    partiront."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    simulateur = Simulateur(Parametres(), variantes=_variantes())
    demandes, attendus = _carrieres_simulees(simulateur)
    resultats, echecs = pont.carrieres(demandes, SCENARIOS,
                                       univers=simulateur.univers_de_la_demande)
    assert not echecs
    assert resultats == attendus
    sans, _ = pont.carrieres(demandes, SCENARIOS)
    for parties in (True, False):
        assert any(lu["ecarts"]["notionnel_liberal"] != sans[cle]["ecarts"]["notionnel_liberal"]
                   for cle, lu in resultats.items()
                   if (lu["aujourd_hui"] is not None) == parties), parties


PROSPECTIFS = ("notionnel_prospectif", "notionnel_prospectif_employeur")


def test_le_stock_a_l_age_legal_passe_au_portage_dans_la_demande_au_bit_pres_du_jumeau():
    """La règle du stock à l'âge légal (``Parametres.stock_age_legal``,
    action 161), qu'aucun réglage de référence ne porte, passe au portage dans
    les paramètres de la demande : sous chacune de ses trois variantes, le
    portage rend de chaque case ce que le jumeau Python simule sous la même
    règle, au bit près, et autre chose que sans elle — les cases déjà parties
    dans les scénarios rétroactifs, sous ``droit_commun`` et ``tout_droit`` ;
    celles qui partiront dans les prospectifs, sous ``acquis``."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.config import StockAgeLegal

    scenarios = SCENARIOS + PROSPECTIFS
    sans = None
    for regle, touches in ((StockAgeLegal.DROIT_COMMUN, SCENARIOS),
                           (StockAgeLegal.TOUT_DROIT, SCENARIOS),
                           (StockAgeLegal.ACQUIS, PROSPECTIFS)):
        simulateur = Simulateur(replace(Parametres(), stock_age_legal=regle))
        demandes, attendus = _carrieres_simulees(simulateur, scenarios)
        if sans is None:
            sans, _ = pont.carrieres(demandes, scenarios)
        resultats, echecs = pont.carrieres(demandes, scenarios, parametres=simulateur.parametres)
        assert not echecs
        assert resultats == attendus, regle
        assert any(lu["ecarts"][scenario] != sans[cle]["ecarts"][scenario]
                   for cle, lu in resultats.items() for scenario in touches), regle


#: Deux barèmes du régime unique (``Parametres.bareme_regime_unique``) : des
#: tranches de plafond comme celles du salarié du privé, et un taux déplafonné.
BAREMES = (((1.0, 0.2815, 0.1145), (8.0, 0.2215, 0.0904), (None, 0.0240, 0.0040)),
           ((None, 0.2290, 0.0950),))


def test_le_bareme_du_regime_unique_passe_au_portage_dans_la_demande_au_bit_pres_du_jumeau():
    """Le barème du régime unique (``Parametres.bareme_regime_unique``, action
    161), qu'aucun réglage de référence ne porte, passe au portage dans les
    paramètres de la demande, et en revient sous les types du Python : sous
    chaque barème, le portage rend de chaque case ce que le jumeau Python simule
    sous le même, au bit près, et autre chose que sans lui, dans les scénarios
    du régime unique. Un barème mal formé arrête le compte du jumeau, comme
    celui du portage."""
    sous_un_bareme = replace(Parametres(), bareme_regime_unique=BAREMES[0])
    assert pont.parametres_des_donnees(
        _comme_node(pont.parametres_en_donnees(sous_un_bareme))) == sous_un_bareme
    with pytest.raises(ValueError, match="bareme_regime_unique"):
        Simulateur(replace(Parametres(), bareme_regime_unique=(
            (2.0, 0.25, 0.125), (1.0, 0.125, 0.0625)))).constructeur
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    sans = None
    for bareme in BAREMES:
        simulateur = Simulateur(replace(Parametres(), bareme_regime_unique=bareme))
        demandes, attendus = _carrieres_simulees(simulateur)
        if sans is None:
            sans, _ = pont.carrieres(demandes, SCENARIOS)
        resultats, echecs = pont.carrieres(demandes, SCENARIOS, parametres=simulateur.parametres)
        assert not echecs
        assert resultats == attendus, bareme
        for scenario in ("notionnel_retroactif", "notionnel_retroactif_employeur"):
            assert any(lu["ecarts"][scenario] != sans[cle]["ecarts"][scenario]
                       for cle, lu in resultats.items()), (bareme, scenario)


def test_le_pont_simule_une_saisie_comme_le_site_au_bit_pres_du_moteur_python():
    """Les carrières d'exemple du bilan figé sont des saisies, que le portage
    simule comme le site (``Contexte.simuler``, ``contexte.js``) : de chacune,
    la fiche de paie de l'année de référence sous le droit en vigueur, le
    passage aux euros constants, et la pension de chaque système demandé, au
    bit près de ce que le moteur Python simule de la carrière que le portage
    bâtit de la même saisie — la saisie n'a que son exemplaire (action 161,
    étape 6)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    demandes = [{"cle": str(rang), "saisie": saisie} for rang, saisie in enumerate(SAISIES)]
    carrieres, refus = pont.carrieres_des_saisies(demandes)
    assert not refus
    attendus = {}
    for cle, (parametres, carriere) in carrieres.items():
        comparaison = Simulateur(parametres).simuler(carriere)
        fiche = comparaison.remuneration.reference.droit_en_vigueur
        attendus[cle] = {
            "fiche": {"annee": fiche.annee, "brut": fiche.brut, "net": fiche.net,
                      "retraite_totale": fiche.retraite_totale,
                      "retraite_employeur": fiche.retraite_employeur},
            "coefficient_euros_constants": comparaison.coefficient_euros_constants,
            "pension_annuelle": comparaison.actuel.pension_annuelle,
            "pensions": {scenario: getattr(comparaison, scenario).pension_annuelle
                         for scenario in SCENARIOS},
        }
    resultats, echecs = pont.saisies(demandes, SCENARIOS)
    assert not echecs
    assert resultats == attendus
    for lu in resultats.values():
        assert type(lu["fiche"]["annee"]) is int
        assert all(type(lu["fiche"][champ]) is float
                   for champ in ("brut", "net", "retraite_totale", "retraite_employeur"))
        assert type(lu["coefficient_euros_constants"]) is float
        assert type(lu["pension_annuelle"]) is float
        assert all(type(pension) is float for pension in lu["pensions"].values())


def test_chaque_case_passe_au_portage_partant_a_l_age_que_le_pilote_fixe():
    """Le Python fixe l'âge de chaque départ et écarte ce que le droit écarte
    (``carriere_de_la_grille``) ; le portage simule. Sous les conventions du
    COR, la carrière d'un cas type se déforme en Python : rien ne passe."""
    simulateur = Simulateur(Parametres())
    types = tuple(cas for cas in CAS_TYPES if cas.code in ("cadre", "carriere_interrompue"))
    options, echecs = cases_de_la_grille(simulateur, types, (1940, 2000))
    assert set(options) | set(echecs) == {(cas.code, generation)
                                         for cas in types for generation in (1940, 2000)}
    for cas in types:
        for generation in (1940, 2000):
            if (cas.code, generation) in options:
                carriere = carriere_de_la_grille(simulateur, cas, generation)
                assert options[(cas.code, generation)] == cas.options(
                    generation, carriere.age_liquidation)
    with pytest.raises(ValueError, match="COR"):
        cases_de_la_grille(simulateur.pour_la_projection(), types, (2000,))


#: Des cohortes de la grille du coût où passe chaque chemin du pilote : le point
#: fixe qui monte ; la règle de l'ouverture, celle des services ; l'inaptitude ;
#: les primes des fonctionnaires, que les conventions du COR projettent ; et la
#: descente d'un an en un an (``pilote.descendre``), que prennent l'agent de
#: conduite né en 1879, l'actif né en 1884, l'artisan né en 1911, l'exploitant
#: né en 1925 et le contractuel né en 1884.
DEPARTS_D_ESSAI = (("salaire_moyen", 1960), ("smic_carriere_complete~inapte", 1965),
                   ("agent_sncf_conduite", 1879), ("agent_ieg", 2000), ("militaire", 1980),
                   ("fonctionnaire_sedentaire", 1990), ("fonctionnaire_actif", 1884),
                   ("fonctionnaire_sedentaire~super_actif", 1970), ("artisan", 1911),
                   ("exploitant_agricole", 1925), ("contractuel_public", 1884))


def _ages_au_portage(simulateur, cohortes, variante: str = "droit"):
    """Les âges que le portage fixe aux ``cohortes``, ``(cas type, génération)``,
    sous les paramètres de ``simulateur`` (:func:`pont.ages_de_depart`)."""
    from retraite_notionnelle.castypes import primes_projetees_en_donnees

    ages, attendus, refus = pont.ages_de_depart(
        [{"cle": f"{cas.code}|{generation}", **cas.pour_le_portage(simulateur, generation)}
         for cas, generation in cohortes],
        simulateur.parametres, primes_projetees_en_donnees(simulateur), variante)
    # Aucun cas type du dépôt n'attend après l'âge que son pilote fixe.
    assert not attendus
    return ages, refus


def test_le_portage_date_les_cas_types_au_bit_pres_du_pilote_python():
    """Le coût fait dater ses cas types au portage (``ageDeDepart`` de
    ``moteur/js/pilote.js`` ; action 161, étape 6), sur la carrière d'un seul
    statut que leurs options décrivent, ses primes projetées sous les
    conventions du COR (``castypes.primes_projetees``) : chaque cohorte part à
    l'âge que le pilote Python lui fixe (``pilote.age_de_depart``), au bit
    près, sous les paramètres de référence comme sous ceux de la projection ;
    l'âge écrit sous la variante ``absolu``."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import pilote

    cohortes = [(next(cas for cas in GRILLE_DU_COUT if cas.code == code), generation)
                for code, generation in DEPARTS_D_ESSAI]
    for simulateur in (Simulateur(Parametres()), Simulateur(Parametres()).pour_la_projection()):
        ages, refus = _ages_au_portage(simulateur, cohortes)
        assert not refus
        attendus = {f"{cas.code}|{generation}": float(pilote.age_de_depart(simulateur, cas,
                                                                            generation))
                    for cas, generation in cohortes}
        assert ages == attendus
        assert all(type(age) is float for age in ages.values())
        # La descente : un an plus tôt que l'âge écrit, et plus.
        assert ages["artisan|1911"] == 62.0 and ages["contractuel_public|1884"] == 61.0
    absolus, _ = _ages_au_portage(simulateur, cohortes, "absolu")
    assert absolus == {f"{cas.code}|{generation}": float(cas.age_liquidation)
                       for cas, generation in cohortes}


def test_le_portage_fait_attendre_l_annulation_et_descendre_a_la_carriere_longue():
    """Les deux chemins du pilote que la grille ne prend pas, que
    ``tests/test_liquidation.py`` tire du texte, refaits au portage. Né en 1955,
    entré à vingt ans et sans activité après quarante et une années, un salarié
    a 164 trimestres des 166 de sa génération et les garde : sa règle le fait
    attendre le taux plein de l'âge d'annulation de la décote, 67 ans
    (L. 351-8, 1°). Né en 1966, entré à seize ans et sans activité depuis ses
    59 ans, il a ses 172 trimestres cotisés à la fin de 2024 : la carrière
    longue lui ouvre le départ à 60 ans (L. 351-1-1, D. 351-1-1), sous la règle
    du taux plein comme sous celle de l'ouverture."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    salarie = next(cas for cas in CAS_TYPES if cas.code == "salaire_moyen")
    inactif = replace(salarie, code="salaire_moyen~inactif", age_debut=20,
                      interruptions_relatives=tuple((decalage, "inactivite")
                                                    for decalage in range(41, 51)))
    longues = [replace(salarie, code=f"salaire_moyen~inactif_a_59_ans~{regle}", age_debut=16,
                       regle_liquidation=regle,
                       interruptions_relatives=tuple((decalage, "inactivite")
                                                     for decalage in range(43, 64)))
               for regle in ("taux_plein", "ouverture")]
    ages, refus = _ages_au_portage(Simulateur(Parametres()),
                                   [(inactif, 1955), *((longue, 1966) for longue in longues)])
    assert not refus
    assert ages == {"salaire_moyen~inactif|1955": 67.0,
                    "salaire_moyen~inactif_a_59_ans~taux_plein|1966": 60.0,
                    "salaire_moyen~inactif_a_59_ans~ouverture|1966": 60.0}


#: Des cohortes de la grille du coût où passe ce que le portage bâtit : deux
#: cases que le droit écarte, chacune sous son motif ; l'entrée tardive et les
#: primes projetées d'un fonctionnaire, sous les conventions du COR ; le
#: super-actif, entré dans son corps après des années de privé ; l'inaptitude ;
#: la règle des services ; la descente ; un départ que l'âge légal de la
#: proposition reporte, et un autre, à 67 ans, qu'il ne reporte pas.
CARRIERES_D_ESSAI = (("salaire_moyen", 1879), ("agent_ieg", 1886),
                     ("fonctionnaire_sedentaire", 1990),
                     ("fonctionnaire_sedentaire~super_actif", 1970),
                     ("smic_carriere_complete~inapte", 1965), ("militaire", 1980),
                     ("artisan", 1911), ("salaire_moyen", 1975), ("profession_liberale", 1980))


def test_le_portage_bat_les_carrieres_de_la_grille_comme_le_python():
    """Le coût fait bâtir au portage la carrière de chaque case de sa grille,
    partie à l'âge que le portage lui fixe (action 161, étape 6) : sous les
    conventions du COR, l'entrée tardive d'un fonctionnaire, que le Python
    décrit en métiers, et ses primes projetées ; les cases que le droit écarte,
    sous le motif du Python ; et les deux carrières que l'âge légal de la
    proposition en dérive, poursuivie jusqu'à lui ou attendue sans activité.
    Chacune revient sous les types du Python, égale à celle qu'il bâtit
    (``castypes.carriere_de_la_grille``, ``Carriere.prolongee``) ; d'une cohorte
    voisine, l'année et le mois de son départ seulement."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.castypes import primes_projetees_en_donnees

    simulateur = Simulateur(Parametres()).pour_la_projection()
    macro, age_legal = simulateur.macro, simulateur.parametres.age_legal_liberal
    cohortes = {f"{code}|{generation}": (next(cas for cas in GRILLE_DU_COUT if cas.code == code),
                                         generation)
                for code, generation in CARRIERES_D_ESSAI}
    lus, refus = pont.carrieres_de_la_grille(
        [{"cle": f"{cle}|{rendre}", **cas.pour_le_portage(simulateur, generation),
          "rendre": rendre}
         for cle, (cas, generation) in cohortes.items() for rendre in ("carriere", "depart")],
        simulateur.parametres, primes_projetees_en_donnees(simulateur), "droit")
    assert refus == {f"salaire_moyen|1879|{rendre}": "liquidation antérieure à la répartition"
                     for rendre in ("carriere", "depart")} | {
        f"agent_ieg|1886|{rendre}": "aucun régime actif sur la période"
        for rendre in ("carriere", "depart")}
    for cle, (cas, generation) in cohortes.items():
        if f"{cle}|carriere" in refus:
            with pytest.raises(ValueError, match=refus[f"{cle}|carriere"]):
                carriere_de_la_grille(simulateur, cas, generation)
            continue
        carriere = carriere_de_la_grille(simulateur, cas, generation)
        bati = lus[f"{cle}|carriere"]
        assert type(bati["carriere"]) is Carriere
        assert bati["carriere"] == carriere, cle
        assert bati["age"] == float(carriere.age_liquidation), cle
        reportee = carriere.prolongee(age_legal, macro)
        if reportee is carriere:
            assert (bati["reportee"], bati["attente"]) == (None, None), cle
        else:
            assert bati["reportee"] == reportee, cle
            assert bati["attente"] == carriere.prolongee(age_legal, macro,
                                                         attente_travaillee=False), cle
        assert lus[f"{cle}|depart"] == {"age": bati["age"], "annee": carriere.annee_liquidation,
                                        "mois": carriere.mois_liquidation}, cle
    # Ce que les cohortes font traverser : l'entrée tardive, un report et un
    # départ que l'âge légal ne reporte pas.
    batis = [lu for cle, lu in lus.items() if cle.endswith("|carriere")]
    assert any(len({ligne.affiliation for ligne in lu["carriere"].lignes}) > 1 for lu in batis)
    assert {lu["reportee"] is None for lu in batis} == {True, False}


#: Les jumeaux Python par lesquels une grille se datait et se bâtissait : le
#: pilote, l'ouverture du droit qu'il interroge, les constructeurs de
#: carrières, leurs prolongations, la projection des primes.
def _jumeaux_qui_datent_et_batissent():
    from retraite_notionnelle import castypes, pilote
    from retraite_notionnelle.droit import ouvrir

    return ((pilote, "age_de_depart"), (pilote, "point_fixe"), (pilote, "descendre"),
            (ouvrir, "age_ouverture_droit"), (ouvrir, "age_taux_plein_droit"),
            (ouvrir, "age_annulation_droit"), (Simulateur, "carriere_simple"),
            (Simulateur, "carriere_parcours"), (Carriere, "prolongee"),
            (castypes, "primes_projetees"))


def _interdire(monkeypatch, jumeaux) -> None:
    """Les jumeaux Python nommés, ``(objet, nom)``, qu'on empêche de calculer."""
    def interdit(*_, **__):
        raise AssertionError("un jumeau Python date ou bâtit ce que le portage doit rendre")

    for objet, nom in jumeaux:
        monkeypatch.setattr(objet, nom, interdit)


def test_la_grille_des_carrieres_types_se_date_au_portage_sans_les_jumeaux(memoire_isolee,
                                                                           monkeypatch):
    """La grille des carrières types de la table (``castypes.cases_de_la_grille``)
    et les âges qu'en écrit ``figer_cas_types`` (``castypes.ages_de_la_grille``)
    se datent au portage (action 161, étape 6) : le pilote Python, l'ouverture
    du droit et les constructeurs de carrières, qu'on empêche ici de calculer,
    n'y entrent pas. Chaque case et chaque motif sont ceux du Python, et chaque
    âge l'est sous son type : l'âge écrit, un entier, quand le droit ne le
    déplace pas — la table l'écrit sans décimale —, un flottant sinon."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.castypes import ages_de_la_grille

    simulateur = Simulateur(Parametres())
    # Les générations de la table, et deux que le droit écarte en partie.
    generations = (1880, 1885, *GENERATIONS)
    with pont.par_le_jumeau():
        en_python = cases_de_la_grille(simulateur, CAS_TYPES, generations)
        ages_en_python = ages_de_la_grille(simulateur)
    _interdire(monkeypatch, _jumeaux_qui_datent_et_batissent())
    assert cases_de_la_grille(simulateur, CAS_TYPES, generations) == en_python
    ages = ages_de_la_grille(simulateur)
    assert ages == ages_en_python
    assert _types(ages) == _types(ages_en_python)
    assert {type(age) for age in ages.values()} == {int, float}
    assert set(en_python[1].values()) == {"liquidation antérieure à la répartition",
                                          "aucun régime actif sur la période"}


def test_les_departs_des_facteurs_de_la_depense_se_datent_au_portage_sans_les_jumeaux(
        memoire_isolee, monkeypatch):
    """Les dates des départs que comptent les facteurs de la dépense
    (``facteurs_depense.dates_des_departs``) se datent au portage (action 161,
    étape 6), sous chacune de leurs formes : la grille, l'entrée dans l'emploi
    décalée comme celle de l'EIC, le départ dès l'ouverture du droit. Le pilote
    Python et les constructeurs de carrières, qu'on empêche ici de calculer,
    n'y entrent pas ; chaque date est celle du Python, cohorte par cohorte, et
    une case que le droit écarte n'en a aucune."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.facteurs_depense import dates_des_departs

    cas = tuple(cas for cas in GRILLE_DU_COUT if cas.code in (
        "salaire_moyen", "fonctionnaire_sedentaire", "militaire", "agent_ieg"))
    formes = ({}, {"entree_depuis": 1960}, {"a_l_ouverture": True})

    def dates():
        return [dates_des_departs(Parametres(), cas_types=cas, generations=(1880, 1965, 2000),
                                  **forme) for forme in formes]

    with pont.par_le_jumeau():
        en_python = dates()
    _interdire(monkeypatch, _jumeaux_qui_datent_et_batissent())
    au_portage = dates()
    assert au_portage == en_python
    # L'entrée décalée et le départ dès l'ouverture déplacent des dates ; la
    # grille écarte des cases de la génération 1880.
    assert au_portage[1] != au_portage[0] and au_portage[2] != au_portage[0]
    assert len(au_portage[0]) < len(cas) * 3 * 5


def _grille_des_avantages() -> tuple:
    """Une grille d'essai du coût des avantages, où passe ce que la
    décomposition mesure : les périodes non travaillées et le salaire de
    référence des parents (la carrière interrompue), le classement de l'emploi
    (l'agent actif), la jouissance militaire, que le garde-fou refuse, et la
    bonification du militaire, le départ anticipé pour carrière longue (le
    salarié au SMIC entré à dix-huit ans), un régime spécial ; l'artisan né en
    1910 descend sous l'âge écrit, l'agent des IEG né en 1885 est écarté. Et
    un policier, qu'aucun cas type de la grille n'est, pour la bonification
    des emplois classés."""
    grille = tuple(cas for cas in CAS_TYPES if cas.code in (
        "carriere_interrompue", "fonctionnaire_actif", "militaire", "smic_carriere_complete",
        "artisan", "agent_ieg"))
    actif = next(cas for cas in grille if cas.code == "fonctionnaire_actif")
    return (*grille, replace(actif, code="policier", libelle="Policier", affiliation="policier"))


def test_le_cout_des_avantages_liquide_sa_grille_au_portage_sans_les_jumeaux(memoire_isolee,
                                                                             monkeypatch):
    """Le coût des avantages non contributifs (``avantages.calculer_avantages``)
    date, bâtit et liquide sa grille au portage (action 161, étape 6) : chaque
    case et ses cinq cohortes, sa liquidation au scénario 1 et ses
    contrefactuelles, sous les scénarios neutralisés de ``pont.mjs``, et l'âge
    légal de chaque génération. Le pilote Python, l'ouverture du droit, les
    constructeurs de carrières, les scénarios neutralisés et le scénario 1 du
    moteur Python, qu'on empêche ici de calculer, n'y entrent pas. Couple pour
    couple, la décomposition est celle du Python, chaque nombre sous son type,
    chaque refus sous sa raison ; et le coût, année par année, est le même."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import avantages, cout
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.scenarios.actuel import ScenarioActuel

    monkeypatch.setattr(avantages, "CAS_TYPES", _grille_des_avantages())
    monkeypatch.setattr(avantages, "generations", lambda: (1885, 1910, 1955, 1965, 1975))
    depenses = DepensesRetraite(RACINE_DONNEES)
    population = Population(RACINE_DONNEES, Parametres().hypothese_esperance_vie)
    with pont.par_le_jumeau():
        en_python = avantages.decomposer(Simulateur(Parametres()))
        cout_en_python = avantages.calculer_avantages(Simulateur(Parametres()), depenses,
                                                      population)

    def interdit(*_, **__):
        raise AssertionError("un jumeau Python date, bâtit ou liquide le coût des avantages")

    _interdire(monkeypatch, (*_jumeaux_qui_datent_et_batissent(), (ScenarioActuel, "__init__"),
                             (ScenarioActuel, "calculer"), (avantages, "scenarios_neutralises"),
                             (cout, "_carrieres_voisines"), (avantages, "_carrieres_voisines")))
    monkeypatch.setattr(Simulateur, "scenario_actuel", property(interdit))
    au_portage = avantages.decomposer(Simulateur(Parametres()))
    assert au_portage == en_python
    assert _types([vars(p) for p in au_portage[0]]) == _types([vars(p) for p in en_python[0]])
    assert avantages.calculer_avantages(Simulateur(Parametres()), depenses,
                                        population) == cout_en_python
    pensionnes, refus = au_portage
    # L'artisan né en 1910 descend sous l'âge écrit ; l'agent des IEG né en 1885
    # est écarté.
    assert {(p.code, p.generation) for p in pensionnes} >= {("artisan", 1910)}
    assert ("agent_ieg", 1885) not in {(p.code, p.generation) for p in pensionnes}
    # Ce que la grille fait traverser : une mesure de chaque sorte, et le refus
    # de la jouissance militaire, rendu partout à la part contributive.
    mesurees = {ligne for p in pensionnes for ligne in p.parts}
    assert mesurees >= {"periodes_assimilees", "categorie_active", "salaire_de_reference_des_parents",
                        "bonification_cinquieme_militaires",
                        "bonification_cinquieme_services_actifs"}
    assert set(refus) == {"age_jouissance_militaire"} and "age_jouissance_militaire" not in mesurees
    assert {p.motif for p in pensionnes} >= {"carriere_longue", "classement", "regime_special"}


#: Une carrière où mord chaque levier de la mesure des avantages non
#: contributifs (``avantages.scenarios_neutralises``), aux options de
#: ``carriere_simple`` : l'agent classé et le militaire partis avant l'âge
#: légal, la mère de deux enfants partie après le 1er septembre 2026, le
#: salarié entré à seize ans parti à soixante, l'assuré handicapé depuis ses
#: vingt et un ans parti à cinquante-six, le policier.
CARRIERES_DES_LEVIERS = {
    code: {"sexe": "H", "niveau_salaire": 1.0, "profil_carriere": "plat",
           "part_primes": 0.0, **options}
    for code, options in {
        "categorie_active": {"annee_naissance": 1965, "age_debut": 22, "age_liquidation": 59,
                             "affiliation": "fonctionnaire_territorial_hospitalier_actif",
                             "part_primes": 0.2},
        "age_jouissance_militaire": {"annee_naissance": 1975, "affiliation": "militaire",
                                     "age_debut": 21, "age_liquidation": 48.5,
                                     "part_primes": 0.2},
        "salaire_de_reference_des_parents": {
            "annee_naissance": 1966, "sexe": "F", "affiliation": "salarie_prive_non_cadre",
            "age_debut": 21, "age_liquidation": 64, "nombre_enfants": 2},
        "carriere_longue": {"annee_naissance": 1964, "affiliation": "salarie_prive_non_cadre",
                            "age_debut": 16, "age_liquidation": 60, "profil_carriere": "smic"},
        "retraite_anticipee_handicap": {
            "annee_naissance": 1973, "affiliation": "salarie_prive_non_cadre", "age_debut": 22,
            "age_liquidation": 56, "invalidite": {"handicap": 21.0}},
        "bonification_cinquieme_services_actifs": {
            "annee_naissance": 1975, "affiliation": "policier", "age_debut": 22,
            "age_liquidation": 57, "part_primes": 0.25},
    }.items()
}


def test_les_leviers_de_la_mesure_des_avantages_neutralisent_au_portage_comme_le_python():
    """Chaque scénario que la mesure des avantages non contributifs neutralise
    (``avantages.scenarios_neutralises``) a son jumeau au portage
    (``scenariosNeutralises`` de ``pont.mjs``), bâti des leviers de
    ``moteur/js/regimes.js`` : les fiches datées et les invalidités privées
    d'une fiche (``sans``), le catalogue privé d'une déclaration
    (``sansDeclaration``), le barème de la carrière longue vidé, la règle du
    salaire de référence des parents repoussée hors de portée (action 161,
    étape 6). Chacun liquide au bit près ce que liquide son jumeau Python
    (``droit_et_refait``), et chacun mord : la carrière que son levier vise
    n'y liquide pas ce qu'elle liquide au scénario 1 — le montant, ou, pour
    la carrière longue, le motif de l'ouverture."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import droit_et_refait
    from test_avantages import _apprenti_puis_salarie

    carrieres = {code: pont.CarriereSimple(options)
                 for code, options in CARRIERES_DES_LEVIERS.items()}
    carrieres["bonification_cinquieme_militaires"] = carrieres["age_jouissance_militaire"]
    # L'apprenti de trente mois dont la carrière reste incomplète : la fiche
    # retirée lui ôte dix trimestres.
    carrieres["apprentissage"] = _apprenti_puis_salarie(Simulateur(Parametres()), 2048, 67.0)
    appels = {}
    for code, carriere in carrieres.items():
        appels[f"{code}|reelle"] = ("scenario_actuel.calculer", pont.MOTEUR, carriere)
        appels[f"{code}|sans"] = ("scenario_actuel.calculer", pont.MOTEUR.neutralisant(code),
                                  carriere)
    lus, refus = droit_et_refait(appels)
    assert not refus
    for code in carrieres:
        reelle, sans = lus[f"{code}|reelle"], lus[f"{code}|sans"]
        if code == "carriere_longue":
            assert (reelle["motif_ouverture"], sans["motif_ouverture"]) == (
                "carriere_longue", "non_ouverte")
        else:
            assert sans["pension_annuelle"] < reelle["pension_annuelle"], code


def test_sans_node_le_pont_s_arrete_sans_repli(monkeypatch):
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.carrieres([{"cle": "cadre|2000", "options": {}}], SCENARIOS)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.saisies([{"cle": "0", "saisie": SAISIES[0]}], SCENARIOS)
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.grille_du_cout([], SCENARIOS, Parametres())
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.scenario_actuel([{"cle": "a", "requete": REQUETE}])
    with pytest.raises(pont.PontIndisponible, match="node"):
        pont.droit({"a": ("ouvrir.duree_requise", pont.MOTEUR, pont.Periode("regime_general", 2020),
                          _carriere_d_openfisca({"code": "a", "debut": 1980, "liquidation": 2020,
                                                 "naissance": 1958, "salaire": 20_000.0}))})


# -- sans paquet, le pont reste ouvert --------------------------------------------

#: Une requête du simulateur : un salarié du privé né en 1965.
REQUETE = {"naissance": "1965-03-15", "statut": "salarie_prive_non_cadre",
           "debut": "1987-09", "liquidation": "2029-04", "salaire": "2500",
           "unite_revenu": "euros_mois"}


def _lancements(monkeypatch) -> list:
    """Les node que le pont lance désormais, sur un pont refermé : chacun se
    compte, et le pont d'une seule demande est interdit."""
    pont.fermer()
    lances, reel = [], subprocess.Popen

    def lancer(commande, *arguments, **options):
        lances.append(commande)
        return reel(commande, *arguments, **options)

    def interdit(*_arguments, **_options):
        raise AssertionError("sans paquet, le pont ne se lance pas pour une seule demande")

    monkeypatch.setattr(subprocess, "Popen", lancer)
    monkeypatch.setattr(subprocess, "run", interdit)
    return lances


def test_sans_paquet_le_pont_reste_ouvert_d_une_demande_a_l_autre(monkeypatch):
    """Les tests demandent au pont une carrière à la fois (action 161,
    étape 6) : sur le paquet du dépôt, node ne se lance qu'une fois, et ne lit
    le paquet qu'une fois, au lieu de trois dixièmes de seconde par demande ;
    ce qu'il rend est ce que rend le pont lancé pour une seule demande."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    paquet = (RACINE_PROJET / "moteur" / "donnees.json").read_bytes()
    seul, _ = pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}], paquet)
    lances = _lancements(monkeypatch)
    premier, _ = pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}])
    autre, refus = pont.carrieres_des_saisies(
        [{"cle": "b", "requete": {**REQUETE, "salaire": "3000"}},
         {"cle": "c", "requete": {**REQUETE, "statut": "inconnu"}}])
    try:
        assert len(lances) == 1 and lances[0][-1] == "--servir"
        assert premier["a"][0] == seul["a"][0]
        assert (json.dumps(pont.carriere_en_donnees(premier["a"][1]))
                == json.dumps(pont.carriere_en_donnees(seul["a"][1])))
        assert list(autre) == ["b"] and "inconnu" in refus["c"]
    finally:
        pont.fermer()


def test_une_saisie_par_la_pension_passe_le_pont_par_la_carriere_que_l_inversion_trouve():
    """Sa carrière vient de la pension, que le contexte inverse en la
    simulant (``Contexte.simuler``, ``contexte.js``) : le pont rend celle que
    l'inversion trouve, que le site simule, et non une carrière au revenu de
    la saisie."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.web.site import module, site

    par_pension = {**REQUETE, "saisie_par": "pension", "pension": "1500"}
    lus, refus = pont.carrieres_des_saisies([{"cle": "pension", "requete": par_pension},
                                             {"cle": "revenu", "requete": REQUETE}])
    assert not refus
    (parametres, carriere), (_, au_revenu) = lus["pension"], lus["revenu"]
    saisie = module("saisie").Saisie.depuis_requete(
        par_pension, False, site().contexte.paquet.presomptions)
    assert (Simulateur(parametres).simuler(carriere).actuel.pension_annuelle
            == site().contexte.simuler(saisie).actuel.pension_annuelle)
    assert ([ligne.revenu for ligne in carriere.lignes]
            != [ligne.revenu for ligne in au_revenu.lignes])


# -- le scénario 1 des confrontations ----------------------------------------------

#: Un relevé que l'appelant prolonge à sa façon (``scripts/estimation_officielle.py``) :
#: une mère de trois enfants, salariée du privé de 2002 à 2025, qui part en juin 2033.
RELEVE_A_PROLONGER = {
    "naissance": "1966-05-12", "sexe": "F", "liquidation": "2033-06", "enfants": "3",
    "euros": "2026",
    "releve": ",".join(f"{annee}:salarie_prive_non_cadre:{18_300 + 600 * (annee - 2002)}"
                       for annee in range(2002, 2026)),
}


def test_le_pont_sert_le_scenario_actuel_au_bit_pres_du_moteur_python():
    """Les confrontations aux références extérieures — l'estimation officielle,
    Destinie 2 — lisent du scénario 1 ce qu'aucun témoin n'écrit : la part de
    chaque régime dans la majoration pour enfants, la durée validée, le taux.
    Le portage le sert (:func:`pont.scenario_actuel`), chaque nombre sous le
    type que le Python lui donne, et le moteur Python, qui garde ses jumeaux,
    le refait au bit près sous Linux x86_64 (:data:`TOLERANCE_DU_MOTEUR_PYTHON`).
    Un relevé que l'appelant a prolongé à sa façon s'en tient à ses années."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    destinie = json.loads((RACINE_PROJET / "tests" / "temoins" / "destinie_2.json")
                          .read_text(encoding="utf-8"))["cas"]
    cas = [{"cle": "veuf", "requete": destinie["reversion_trois_enfants"]["requete"]},
           {"cle": "metiers", "requete": REQUETE},
           {"cle": "prolonge", "requete": RELEVE_A_PROLONGER},
           {"cle": "tel_quel", "requete": RELEVE_A_PROLONGER, "prolonger": False}]
    servis, refus = pont.scenario_actuel(cas)
    assert refus == {}
    refaits, refus = Saisies().scenario_actuel(cas)
    assert refus == {}
    for cle, servi in servis.items():
        assert ecarts_d_ecriture(refaits[cle], servi,
                                 tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == [], cle
    veuf = servis["veuf"]
    (majoration,) = (avantage for avantage in veuf["actuel"]["avantages_appliques"]
                     if avantage["code"] == "majoration_enfants")
    assert "regime_general" in {regime for regime, _ in majoration["par_regime"]}
    assert veuf["reversion"]["regimes"] and servis["metiers"]["reversion"] is None
    # Tel quel, le relevé s'arrête en 2025 ; prolongé, il court jusqu'au départ.
    assert (servis["tel_quel"]["actuel"]["trimestres_valides"]
            < servis["prolonge"]["actuel"]["trimestres_valides"])
    assert (servis["tel_quel"]["annee_liquidation"],
            servis["tel_quel"]["mois_liquidation"]) == (2033, 6)
    for servi in servis.values():
        actuel = servi["actuel"]
        assert type(servi["annee_liquidation"]) is int and type(servi["mois_liquidation"]) is int
        assert type(actuel["trimestres_valides"]) is int
        assert all(type(nombre) is float for nombre in (
            servi["coefficient_euros_constants"], actuel["pension_annuelle"],
            actuel["pension_hors_repartition"], actuel["taux_liquidation"]))
        assert all(type(pension["montant"]) is float for pension in actuel["pensions_par_regime"])
        assert all(type(avantage["montant"]) is float and type(part) is float
                   for avantage in actuel["avantages_appliques"]
                   for _, part in avantage["par_regime"])


# -- le droit, fonction par fonction -------------------------------------------------

def _carriere_d_openfisca(profil: dict) -> Carriere:
    """La carrière exacte d'un profil d'OpenFisca au régime général, bâtie à
    la main comme ``tests/test_oracle.py`` la bâtit (``_notre_calcul``)."""
    lignes = [AnneeCarriere(annee=annee, revenu=profil["salaire"],
                            affiliation="salarie_prive_non_cadre", trimestres_valides=4)
              for annee in range(profil["debut"], profil["liquidation"])]
    return Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    identifiant=profil["code"])


def test_le_pont_fait_appeler_les_fonctions_du_droit_au_bit_pres_de_leur_jumeau():
    """Les exemples d'OpenFisca et des caisses (``tests/test_oracle.py``)
    éprouvent le droit fonction par fonction, sur des carrières bâties à la
    main : le pont les fait appeler au portage (:func:`pont.droit`), la carrière
    passée en données, le moteur du scénario 1 et la période d'un régime
    désignés, et rend ce que chacune rend sous le type de son jumeau Python
    (:data:`pont.LECTURES_DU_DROIT`) — au bit près de lui sous Linux x86_64,
    sur chaque profil d'OpenFisca au régime général. Une fonction que le pont
    ne sait pas relire est refusée avant node."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import actuel_en_donnees
    from retraite_notionnelle.donnees.chargement import Fiabilite
    from retraite_notionnelle.droit import liquider, ouvrir

    profils = json.loads((RACINE_PROJET / "tests" / "temoins" / "openfisca_regime_general.json")
                         .read_text(encoding="utf-8"))["profils"]
    simulateur = Simulateur(Parametres())
    scenario = simulateur.scenario_actuel
    for code, temoin in profils.items():
        profil = temoin["profil"]
        carriere, depart = _carriere_d_openfisca(profil), profil["liquidation"]
        age = float(depart - profil["naissance"])
        periode = simulateur.catalogue["regime_general"].periode(depart)
        requis, _ = ouvrir.duree_requise(scenario, periode, carriere)
        _, annulation, _ = liquider.decote_opposable(scenario, periode, carriere, depart)
        resultat = scenario.calculer(carriere)
        # Ce que rend chaque jumeau Python, relu sous le type que le pont
        # déclare : « 2 » que le jumeau rend pour des trimestres de décote,
        # flottants, s'y relit « 2.0 », comme le zéro d'une somme vide des témoins.
        attendus = {cle: pont.relu_du_droit(fonction, rendu) for cle, (fonction, rendu) in {
            "requis": ("ouvrir.duree_requise", ouvrir.duree_requise(scenario, periode, carriere)),
            "proratisation": ("liquider.duree_proratisation", liquider.duree_proratisation(
                scenario, periode, carriere, requis)),
            "decote": ("liquider.decote_opposable", liquider.decote_opposable(
                scenario, periode, carriere, depart)),
            "salaire": ("liquider.salaire_de_reference", liquider.salaire_de_reference(
                scenario, "regime_general", carriere, periode, depart, True,
                profil["naissance"], True)),
            "manquants": ("liquider.trimestres_de_decote", liquider.trimestres_de_decote(
                scenario, periode, carriere, resultat.trimestres_valides, requis, age,
                annulation)),
            "resultat": ("scenario_actuel.calculer", actuel_en_donnees(resultat)),
        }.items()}
        rg = pont.Periode("regime_general", depart)
        lus, echecs = pont.droit({
            "requis": ("ouvrir.duree_requise", pont.MOTEUR, rg, carriere),
            "proratisation": ("liquider.duree_proratisation", pont.MOTEUR, rg, carriere, requis),
            "decote": ("liquider.decote_opposable", pont.MOTEUR, rg, carriere, depart),
            "salaire": ("liquider.salaire_de_reference", pont.MOTEUR, "regime_general", carriere,
                        rg, depart, True, profil["naissance"], True),
            "manquants": ("liquider.trimestres_de_decote", pont.MOTEUR, rg, carriere,
                          resultat.trimestres_valides, requis, age, annulation),
            "resultat": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
        })
        assert echecs == {}, code
        for cle, attendu in attendus.items():
            assert ecarts_d_ecriture(lus[cle], attendu,
                                     tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == [], (code, cle)
        assert type(lus["requis"]) is tuple and type(lus["requis"][0]) is int
        assert lus["requis"][1] is None or type(lus["requis"][1]) is Fiabilite
        assert type(lus["decote"][1]) is float and type(lus["salaire"]) is float
        assert type(lus["manquants"]) is float
        assert lus["resultat"]["trimestres_valides"] == attendus["resultat"]["trimestres_valides"]
    with pytest.raises(ValueError, match="liquider.inconnue"):
        pont.droit({"a": ("liquider.inconnue", pont.MOTEUR)})


def test_le_controle_du_droit_voit_un_ulp_deplace_dans_le_jumeau_python(monkeypatch):
    """Les exemples d'OpenFisca et des caisses font appeler le droit au
    portage, et son jumeau Python le refait tant qu'il reste (action 161) :
    :func:`outils_pont.droit_et_refait` rend ce que le portage rend, chaque
    fonction refaite par son jumeau (``JUMEAUX_DU_DROIT``, un par fonction que
    le pont relit), et arrête la confrontation sur un ulp qu'on y déplace —
    au-delà de la tolérance hors de Linux x86_64."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    import math

    from outils_pont import JUMEAUX_DU_DROIT, droit_et_refait

    assert set(JUMEAUX_DU_DROIT) == set(pont.LECTURES_DU_DROIT)
    profil = {"code": "a", "debut": 1980, "liquidation": 2016, "naissance": 1954,
              "salaire": 31_000.0}
    carriere, rg = _carriere_d_openfisca(profil), pont.Periode("regime_general", 2016)
    appels = {
        "salaire": ("liquider.salaire_de_reference", pont.MOTEUR, "regime_general", carriere,
                    rg, 2016, True, 1954, True),
        "resultat": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
    }
    lus, refus = droit_et_refait(appels)
    assert refus == {} and lus == pont.droit(appels)[0]
    jumeau = JUMEAUX_DU_DROIT["liquider.salaire_de_reference"]

    def deplace(*arguments):
        rendu = jumeau(*arguments)
        return (math.nextafter(rendu, math.inf) if TOLERANCE_DU_MOTEUR_PYTHON == 0.0
                else rendu * (1 + 1e-9))

    monkeypatch.setitem(JUMEAUX_DU_DROIT, "liquider.salaire_de_reference", deplace)
    with pytest.raises(AssertionError, match="salaire"):
        droit_et_refait(appels)


def test_le_pont_rend_ce_que_chaque_ligne_du_releve_cite():
    """Le tableau de bord compte, sur les relevés des cas types, les lignes
    qui citent leur fiche et la version qu'elles appliquent (contrat C.5) : le
    pont rend, de chaque ligne du relevé que le portage construit, son
    identifiant, sa fiche et sa version (action 161, lot A). Une fonctionnaire
    de l'État née en 1970, entrée à vingt-deux ans et partie à soixante-quatre,
    a quarante-deux années de services, de 1992 à 2033 : chacune cite la fiche
    des services de la fonction publique, sans version, et aucune ligne de
    durée d'assurance, de points ni de cotisations ne cite de fiche. Une
    salariée du même âge, mère de deux enfants nés avant 2010, a une ligne de
    trimestres par enfant, qui cite la majoration de durée d'assurance et sa
    version d'avant 2010. Le jumeau Python le refait tant qu'il reste."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import droit_et_refait

    options = {"annee_naissance": 1970, "sexe": "F", "age_debut": 22, "age_liquidation": 64}
    lus, refus = droit_et_refait({
        "fonctionnaire": ("releve.construire.lignes.citations", pont.MOTEUR, pont.CarriereSimple(
            {**options, "affiliation": "fonctionnaire_etat"})),
        "mere": ("releve.construire.lignes.citations", pont.MOTEUR, pont.CarriereSimple(
            {**options, "affiliation": "salarie_prive_non_cadre", "nombre_enfants": 2})),
    })
    assert refus == {}
    assert type(lus["fonctionnaire"]) is tuple and type(lus["fonctionnaire"][0]) is tuple
    citations = {ligne: (fiche, version) for ligne, fiche, version in lus["fonctionnaire"]}
    assert len(citations) == len(lus["fonctionnaire"])
    assert {ligne: cite for ligne, cite in citations.items() if ligne.startswith("services_")} == {
        f"services_fonction_publique_etat_{annee}": ("services_et_duree_fonction_publique", None)
        for annee in range(1992, 2034)}
    assert {cite for ligne, cite in citations.items()
            if ligne.startswith(("assurance_", "cotises_", "points_", "cotisations_"))} == {
        (None, None)}
    assert {(ligne, fiche, version) for ligne, fiche, version in lus["mere"]
            if fiche is not None} == {
        (f"enfants_assurance_regime_general_{rang}", "majoration_duree_assurance_enfants",
         "mda_2010_nes_avant") for rang in (1, 2)}


def test_le_pont_bat_une_carriere_de_ses_options_sans_la_faire_passer():
    """Les exemples officiels cherchent la carrière qui rend leurs trimestres,
    un âge de début après l'autre : chaque essai se liquide sur la carrière
    que ``simulateur.carriere_simple`` bâtit de ses options
    (``pont.CarriereSimple``), que le portage bâtit lui-même, sans qu'elle
    passe le pont. Liquidée, elle rend ce que rend la même carrière bâtie,
    écrite en données et relue ; le jumeau Python la bâtit et la refait au bit
    près (``droit_et_refait``)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import droit_et_refait

    options = {"annee_naissance": 1962, "sexe": "F", "affiliation": "salarie_prive_non_cadre",
               "age_debut": 21.5, "age_liquidation": 64.25, "nombre_enfants": 2,
               "interruptions": {1990: "chomage_indemnise"}, "temps_partiel": {2000: 0.8}}
    lus, echecs = droit_et_refait({
        "carriere": ("simulateur.carriere_simple", pont.SIMULATEUR, options),
        "par_options": ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple(options)),
    })
    assert echecs == {}
    relue = pont.carriere_des_donnees(lus["carriere"])
    par_donnees, _ = pont.droit({"resultat": ("scenario_actuel.calculer", pont.MOTEUR, relue)})
    assert lus["par_options"] == par_donnees["resultat"]


def test_le_pont_prete_une_table_au_moteur_du_portage(monkeypatch):
    """Un test prête au moteur Python une de ses tables par une autre
    (``monkeypatch.setattr``) — celle des indépendants par celle du régime
    général, pour lire ce que la règle des artisans ajoute à leur pension : le
    pont prête la même au moteur du portage (``pont.MOTEUR.pretant``), sur
    une copie, au bit près du moteur Python sous le même prêt ; le moteur sans
    prêt n'en garde rien, et une table que le moteur ne porte pas arrête
    l'appel. L'artisan né en 1949 en est la mesure : vingt et une années
    retenues (R. 634-1-1), vingt-cinq au régime général."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from outils_pont import actuel_en_donnees

    carriere = Carriere(
        annee_naissance=1949, sexe="H", age_liquidation=62.0, identifiant="artisan_1949",
        lignes=[AnneeCarriere(annee=annee, revenu=12_000.0 + 900.0 * (annee - 1973),
                              affiliation="artisan", trimestres_valides=4)
                for annee in range(1973, 2011)])
    pretant = pont.MOTEUR.pretant("annees_revenu_independants", "annees_salaire_reference")
    lus, echecs = pont.droit({
        "sans": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
        "prete": ("scenario_actuel.calculer", pretant, carriere),
        "apres": ("scenario_actuel.calculer", pont.MOTEUR, carriere),
    })
    assert echecs == {}
    actuel = Simulateur(Parametres()).scenario_actuel
    sans = pont.relu_du_droit("scenario_actuel.calculer", actuel_en_donnees(actuel.calculer(carriere)))
    monkeypatch.setattr(actuel, "annees_revenu_independants", actuel.annees_salaire_reference)
    prete = pont.relu_du_droit("scenario_actuel.calculer",
                               actuel_en_donnees(actuel.calculer(carriere)))
    assert ecarts_d_ecriture(lus["prete"], prete, tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []
    assert ecarts_d_ecriture(lus["sans"], sans, tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == []
    assert lus["apres"] == lus["sans"]
    assert lus["prete"]["pension_annuelle"] < lus["sans"]["pension_annuelle"]
    _, echecs = pont.droit({"inconnue": (
        "scenario_actuel.calculer",
        pont.MOTEUR.pretant("table_inconnue", "annees_salaire_reference"), carriere)})
    assert "tableInconnue" in echecs["inconnue"]


def test_le_pont_ouvert_se_relance_quand_le_paquet_du_depot_change(monkeypatch):
    """Le paquet du dépôt se récrit à chaque fabrique : le pont ouvert sur
    l'ancien se referme, et le suivant lit le nouveau."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    lances = _lancements(monkeypatch)
    pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}])
    signature = pont._signature_du_paquet()
    monkeypatch.setattr(pont, "_signature_du_paquet", lambda: (*signature, "récrit"))
    try:
        pont.carrieres_des_saisies([{"cle": "a", "requete": REQUETE}])
        assert len(lances) == 2
    finally:
        pont.fermer()


#: Un appel au droit qui ne demande qu'une valeur présumée : le jour de
#: naissance que le droit retient quand on ne le connaît pas, le 15.
JOUR_DE_NAISSANCE = {"j": ("chronologie.valeur", "jour_de_naissance")}


def test_le_pont_ouvert_se_relance_quand_node_s_est_arrete(monkeypatch):
    """Node mort entre deux demandes, la suivante le relance, au lieu
    d'échouer, « node s'est arrêté », jusqu'à un ``pont.fermer()`` que seuls
    les tests appellent ; le pont mort est refermé (action 190, étape 3)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    lances = _lancements(monkeypatch)
    try:
        assert pont.droit(JOUR_DE_NAISSANCE) == ({"j": 15}, {})
        mort = pont._OUVERT._processus
        mort.kill()
        mort.wait()
        assert pont.droit(JOUR_DE_NAISSANCE) == ({"j": 15}, {})
        assert len(lances) == 2 and pont._OUVERT._processus is not mort
        assert mort.stdin.closed
    finally:
        pont.fermer()


def test_node_mort_en_pleine_demande_la_fait_echouer_avec_son_journal(monkeypatch, tmp_path):
    """Node qui s'arrête pendant une demande la fait échouer, avec ce qu'il a
    écrit sur sa sortie d'erreur ; la demande suivante le relance."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    tombe = tmp_path / "tombe.mjs"
    tombe.write_text('process.stdin.once("data", () => {\n'
                     '  console.error("tombé en pleine demande");\n'
                     "  process.exit(1);\n"
                     "});\n", encoding="utf-8")
    programme = pont.PROGRAMME
    lances = _lancements(monkeypatch)
    monkeypatch.setattr(pont, "PROGRAMME", tombe)
    try:
        with pytest.raises(RuntimeError, match="node s'est arrêté : tombé en pleine demande"):
            pont.droit(JOUR_DE_NAISSANCE)
        monkeypatch.setattr(pont, "PROGRAMME", programme)
        assert pont.droit(JOUR_DE_NAISSANCE) == ({"j": 15}, {})
        assert len(lances) == 2
    finally:
        pont.fermer()


def test_fermer_un_pont_mort_ferme_son_tuyau_d_entree():
    """Node mort, la demande qu'on lui écrit reste dans le tuyau : le pont
    refermé le ferme sans l'écrire, au lieu que Python le signale en le
    ramassant (« Exception ignored … BrokenPipeError »)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ouvert = pont._PontOuvert()
    try:
        ouvert._processus.kill()
        ouvert._processus.wait()
        with pytest.raises(RuntimeError, match="node s'est arrêté"):
            ouvert.demander({"droit": {}})
        ouvert.fermer()
        assert ouvert._processus.stdin.closed
    finally:
        ouvert.fermer()


def test_sous_la_garde_des_presomptions_le_portage_les_lit_decalees(monkeypatch):
    """La garde des présomptions (``PRESOMPTIONS_DECALEES``, ``tests/conftest.py`` ;
    action 135, levier 2) fait dire au vocabulaire du Python d'autres valeurs :
    le portage lit les mêmes dans son paquet, celui du dépôt comme celui d'une
    demande, pour qu'un test qui en écrit une en dur échoue d'un côté comme de
    l'autre. Le pont ouvert sans la garde se relance sous elle, et
    inversement."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from conftest import DECALAGES, PRESOMPTIONS_DECALEES

    paquet = (RACINE_PROJET / "moteur" / "donnees.json").read_bytes()
    du_paquet = {nom: json.loads(paquet)["presomptions"][nom]["valeur"] for nom in DECALAGES}
    assert du_paquet != DECALAGES
    appels = {nom: ("chronologie.valeur", nom) for nom in DECALAGES}
    pont.fermer()
    monkeypatch.delenv(PRESOMPTIONS_DECALEES, raising=False)
    try:
        assert pont.droit(appels) == (du_paquet, {})
        monkeypatch.setenv(PRESOMPTIONS_DECALEES, "1")
        assert pont.droit(appels) == (DECALAGES, {})
        assert pont.droit(appels, paquet=paquet) == (DECALAGES, {})
        monkeypatch.delenv(PRESOMPTIONS_DECALEES)
        assert pont.droit(appels) == (du_paquet, {})
    finally:
        pont.fermer()


# -- la grille du coût : ses carrières passent en données ------------------------

#: Des cases de la grille du coût où passe ce que les conventions de projection
#: du COR déforment en Python : l'entrée tardive dans le régime de l'État et
#: dans celui de la CNRACL, la part des primes que le décrochage du traitement
#: porte, l'inaptitude reconnue ; et, sans déformation, une carrière de mère de
#: deux enfants interrompue, déjà partie, et le salarié que l'âge légal de la
#: proposition reporte.
CASES_DU_COUT = (("fonctionnaire_sedentaire", 1990), ("fonctionnaire_actif", 1975),
                 ("militaire", 1980), ("smic_carriere_complete~inapte", 1960),
                 ("smic_carriere_complete~ex_invalide", 1965),
                 ("carriere_interrompue", 1950), ("salaire_moyen", 1970))


def _carriere_du_cout(simulateur, code: str, generation: int):
    return carriere_de_la_grille(
        simulateur, next(cas for cas in GRILLE_DU_COUT if cas.code == code), generation)


def _types(valeur):
    """La structure de ``valeur``, chaque nombre remplacé par son type : deux
    lectures égales dont un entier serait ici un flottant ne s'écrivent pas de
    même dans un fichier fabriqué."""
    if isinstance(valeur, dict):
        return {cle: _types(lu) for cle, lu in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return type(valeur)(_types(lu) for lu in valeur)
    return type(valeur).__name__


def test_une_carriere_passe_en_donnees_champ_par_champ():
    """La carrière d'un cas type, déformée sous les conventions du COR
    (``primes_projetees``, l'entrée tardive), passe au portage en données pour
    qu'il la simule (``pont.grille_du_cout``) : tous les champs de la carrière,
    chaque ligne entière et la chronologie dont elle est la vue, en JSON strict
    — un champ qui naîtrait sans passer le pont ferait échouer ce test."""
    simulateur = Simulateur(Parametres()).pour_la_projection()
    carriere = _carriere_du_cout(simulateur, "fonctionnaire_sedentaire", 1990)
    donnees = pont.carriere_en_donnees(carriere)
    assert set(donnees) == {champ.name for champ in fields(Carriere)}
    for ligne in donnees["lignes"]:
        assert set(ligne) == {champ.name for champ in fields(AnneeCarriere)}
    assert json.loads(json.dumps(donnees, allow_nan=False)) == donnees
    assert donnees["chronologie"] == carriere.chronologie
    # Déformée : entrée tard dans le régime de l'État, après des années de
    # contractuel, sa part des primes portée par le décrochage du traitement.
    assert {ligne["affiliation"] for ligne in donnees["lignes"]} == {
        "contractuel_public", "fonctionnaire_etat"}
    assert donnees["dates_entree"]["fonctionnaire_etat"] == [
        carriere.dates_entree["fonctionnaire_etat"].annee,
        carriere.dates_entree["fonctionnaire_etat"].mois]
    assert len({ligne["part_primes"] for ligne in donnees["lignes"]
                if ligne["affiliation"] == "fonctionnaire_etat"}) > 1


def _construire_temoins():
    """Le module de ``scripts/construire_temoins.py``."""
    import importlib.util

    chemin = RACINE_PROJET / "scripts" / "construire_temoins.py"
    specification = importlib.util.spec_from_file_location("construire_temoins", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _echantillon(temoins: dict) -> list[str]:
    """Des témoins de chaque forme : la base, un relevé, un conjoint, un décès,
    l'étranger, un emploi après le départ."""
    formes = ("releve", "conjoint", "deces", "etranger1_pays", "emploi_retraite")
    return ["base"] + [next(nom for nom, temoin in temoins.items() if forme in temoin["requete"])
                       for forme in formes]


def _au_moteur_python(requetes: dict[str, dict]) -> dict[str, dict]:
    """Chaque requête, sous le nom de son témoin, simulée au moteur Python comme
    ``scripts/construire_temoins.py`` la simulait jusqu'au 31 octobre 2026 : la
    carrière que le portage bâtit de sa saisie, la seule
    (:func:`pont.carrieres_des_saisies`), simulée par le jumeau Python, un
    simulateur par jeu de paramètres ; son résultat écrit sous la table des
    types (:func:`pont.resultat_des_donnees`), et ses appels de ``liquider``,
    liquidations d'essai comprises."""
    fini = _construire_temoins()._fini
    carrieres, refusees = pont.carrieres_des_saisies(
        [{"cle": nom, "requete": requete} for nom, requete in requetes.items()])
    assert refusees == {}
    simulateurs = {}
    refaits = {}
    for nom, requete in requetes.items():
        parametres, carriere = carrieres[nom]
        if parametres not in simulateurs:
            simulateurs[parametres] = Simulateur(parametres)
        avant = liquidation.appels()
        resultat = simulateurs[parametres].simuler(carriere).dictionnaire()
        refaits[nom] = {"requete": requete,
                        "resultat": pont.resultat_des_donnees(fini(resultat)),
                        "appels_liquider": liquidation.appels() - avant}
    return refaits


def test_les_temoins_se_simulent_par_le_portage_sans_le_moteur_python(monkeypatch):
    """``scripts/construire_temoins.py`` fait simuler ses témoins au portage
    (:func:`pont.simulations`), le moteur qui fait foi (note de décision
    0005) : le moteur Python, qu'on empêche ici de simuler, n'y entre pas, et
    des témoins de chaque forme reviennent tels que le fichier les porte, à
    l'octet."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    module = _construire_temoins()
    _, temoins = _temoins_de_simulations()
    noms = _echantillon(temoins)
    monkeypatch.setattr(module, "_cas", lambda: [{"nom": nom, "requete": temoins[nom]["requete"]}
                                                  for nom in noms])

    def interdit(*_, **__):
        raise AssertionError("le moteur Python simule un témoin")

    monkeypatch.setattr(Simulateur, "simuler", interdit)
    simulations = module._simulations()
    assert list(simulations) == noms
    for nom in noms:
        assert ecarts_d_ecriture(simulations[nom], temoins[nom]) == [], nom


def test_le_moteur_python_refait_des_temoins_de_chaque_forme():
    """Le moteur Python garde ses jumeaux jusqu'à leur retrait (action 161), et
    les témoins, que le portage calcule, le confrontent : sur des témoins de
    chaque forme, la carrière que le portage bâtit, simulée au moteur Python
    et écrite sous la table des types, redonne ce que porte le fichier, appels
    de ``liquider`` compris (:data:`TOLERANCE_DU_MOTEUR_PYTHON`)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    _, temoins = _temoins_de_simulations()
    noms = _echantillon(temoins)
    refaits = _au_moteur_python({nom: temoins[nom]["requete"] for nom in noms})
    for nom in noms:
        assert ecarts_d_ecriture(refaits[nom], temoins[nom],
                                 tolerance=TOLERANCE_DU_MOTEUR_PYTHON) == [], nom


def _comme_node(valeur):
    """Une valeur telle que node l'écrit en JSON : un flottant entier sans sa
    décimale, « 2 » pour 2.0."""
    if isinstance(valeur, float) and valeur.is_integer():
        return int(valeur)
    if isinstance(valeur, dict):
        return {cle: _comme_node(element) for cle, element in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_comme_node(element) for element in valeur]
    return valeur


def _temoins_de_simulations() -> tuple[str, dict]:
    """Le texte de ``tests/temoins/simulations.json``, et ce qu'il porte."""
    texte = (RACINE_PROJET / "tests" / "temoins" / "simulations.json").read_text(encoding="utf-8")
    return texte, json.loads(texte)


def test_la_table_des_types_relit_chaque_temoin_ecrit_comme_node_l_ecrirait():
    """Node n'écrit qu'un type de nombre, « 2 » pour 2.0 : le pont relit le
    résultat d'une simulation que le portage a écrit sous la table des types
    qu'il déclare champ par champ (:func:`pont.resultat_des_donnees`). Les
    témoins s'écrivent sous la même table : le zéro d'un champ flottant
    « 0.0 », même quand le moteur Python le rend entier, d'une somme vide
    (décision du propriétaire, 31 octobre 2026). Chaque témoin, écrit comme
    node l'écrirait, en revient donc à l'octet. Un champ numérique qui naît
    dans le résultat sans son type déclaré fait échouer ce test, et la
    relecture avec lui."""
    _, temoins = _temoins_de_simulations()
    ecarts = [f"{nom}, {ecart}" for nom, temoin in temoins.items()
              for ecart in ecarts_d_ecriture(
                  pont.resultat_des_donnees(_comme_node(temoin["resultat"])),
                  temoin["resultat"])]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"


def test_la_table_des_types_refuse_le_nombre_qu_elle_ne_declare_pas():
    """Un nombre sous un champ que la table ne déclare pas arrête la relecture,
    au lieu d'en deviner le type, et un entier qui n'en est pas un aussi. Un
    nombre non fini, que node écrit « null » comme ``_fini`` l'écrit, reste
    ``None`` ; un texte et un booléen restent ce qu'ils sont. Les clés d'un
    dictionnaire déclaré — les régimes du capital, les origines des années
    d'une part employeur — sont libres. Le zéro d'un champ flottant s'écrit
    « 0.0 », quel que soit le chemin du calcul qui l'a rendu."""
    with pytest.raises(ValueError, match="assure.nouveau"):
        pont.resultat_des_donnees({"assure": {"nouveau": 1}})
    with pytest.raises(TypeError, match="entier"):
        pont.resultat_des_donnees({"assure": {"annee_naissance": 1970.5}})
    relu = pont.resultat_des_donnees({
        "assure": {"annee_naissance": 1970, "age_liquidation": 64, "sexe": "F",
                   "affiliations": ["salarie_prive_non_cadre"]},
        "scenarios": {
            "actuel": {"pension_annuelle": 12000, "pension_hors_repartition": 0,
                       "taux_remplacement": None, "liquidation_ouverte": True,
                       "droits_apres_depart": {"montant": 0, "pensions": [
                           {"montant": 0, "trimestres": 4}]}},
            "notionnel_liberal": {
                "capital_par_regime": {"un_regime_de_plus": 3},
                "annees_part_employeur": {"appelee": 2},
                "capitalisation": {"interets": 0, "versements": 0, "annees_cotisees": 0}},
            "notionnel_retroactif": {"capitalisation": {"interets": 12}}},
        "aujourd_hui": {"actuel": {"majoration_enfants": 0, "pension_hors_repartition": 0}},
    })
    assert json.dumps(relu, sort_keys=True) == json.dumps({
        "assure": {"annee_naissance": 1970, "age_liquidation": 64.0, "sexe": "F",
                   "affiliations": ["salarie_prive_non_cadre"]},
        "scenarios": {
            "actuel": {"pension_annuelle": 12000.0, "pension_hors_repartition": 0.0,
                       "taux_remplacement": None, "liquidation_ouverte": True,
                       "droits_apres_depart": {"montant": 0.0, "pensions": [
                           {"montant": 0.0, "trimestres": 4}]}},
            "notionnel_liberal": {
                "capital_par_regime": {"un_regime_de_plus": 3.0},
                "annees_part_employeur": {"appelee": 2},
                "capitalisation": {"interets": 0.0, "versements": 0.0, "annees_cotisees": 0}},
            "notionnel_retroactif": {"capitalisation": {"interets": 12.0}}},
        "aujourd_hui": {"actuel": {"majoration_enfants": 0.0, "pension_hors_repartition": 0.0}},
    }, sort_keys=True)


def test_le_pont_simule_des_temoins_comme_le_portage_les_simule():
    """Les témoins simulés par le portage (:func:`pont.simulations`), comme
    ``tests/js/moteur.test.js`` les simule : sur des témoins de chaque forme —
    un relevé, un conjoint, un décès, l'étranger, un emploi après le départ —,
    les appels de ``liquider`` que porte le fichier, et son résultat, relu par
    la table des types, à l'octet."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    _, temoins = _temoins_de_simulations()
    noms = _echantillon(temoins)
    resultats, echecs = pont.simulations([{"cle": nom, "requete": temoins[nom]["requete"]}
                                          for nom in noms])
    assert (list(resultats), echecs) == (noms, {})
    for nom in noms:
        assert set(resultats[nom]) == {"resultat", "appels_liquider"}, nom
        assert resultats[nom]["appels_liquider"] == temoins[nom]["appels_liquider"], nom
        assert ecarts_d_ecriture(resultats[nom]["resultat"], temoins[nom]["resultat"]) == [], nom


def test_le_portage_relu_par_la_table_redonne_les_temoins_a_l_octet():
    """Tous les témoins de simulations, simulés par le portage
    (:func:`pont.simulations`), relus par la table des types et écrits comme
    ``scripts/construire_temoins.py`` les écrit : le fichier revient à l'octet,
    appels de ``liquider`` compris. C'est la preuve que les témoins peuvent se
    simuler par le portage sans qu'un octet change (action 161, étape 6)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    texte, temoins = _temoins_de_simulations()
    resultats, echecs = pont.simulations([{"cle": nom, "requete": temoin["requete"]}
                                          for nom, temoin in temoins.items()])
    assert echecs == {}
    relus = {nom: {"requete": temoin["requete"], **resultats[nom]}
             for nom, temoin in temoins.items()}
    ecarts = [f"{nom}, {ecart}" for nom, temoin in temoins.items()
              for ecart in ecarts_d_ecriture(relus[nom], temoin)]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"
    assert json.dumps(relus, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == texte


def test_le_moteur_python_refait_chaque_temoin():
    """Tous les témoins, simulés au moteur Python sur la carrière que le portage
    bâtit, écrits sous la table des types : le fichier, que le portage calcule,
    revient à l'octet sous Linux x86_64, appels de ``liquider`` compris
    (:data:`TOLERANCE_DU_MOTEUR_PYTHON`). C'est la concordance des deux
    moteurs, que ``tests/js/moteur.test.js`` tenait quand les témoins se
    simulaient au Python : une règle portée d'un seul côté, ou dans un autre
    ordre d'addition, la rougit (note de décision 0005)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    texte, temoins = _temoins_de_simulations()
    refaits = _au_moteur_python({nom: temoin["requete"] for nom, temoin in temoins.items()})
    ecarts = [f"{nom}, {ecart}" for nom, temoin in temoins.items()
              for ecart in ecarts_d_ecriture(refaits[nom], temoin,
                                             tolerance=TOLERANCE_DU_MOTEUR_PYTHON)]
    assert not ecarts, f"{len(ecarts)} écart(s), dont : {ecarts[:5]}"
    if not TOLERANCE_DU_MOTEUR_PYTHON:
        assert json.dumps(refaits, ensure_ascii=False, sort_keys=True, indent=1) + "\n" == texte


def test_le_python_relit_une_carriere_ecrite_par_node_sous_ses_types():
    """Ce que node écrit, le Python le relit sous ses types : un flottant entier
    redevient flottant, dans les champs comme dans les nombres libres de la
    chronologie qu'il écrit en flottants, quand les trimestres d'un relevé
    gardent le type que JSON leur rend. Un champ qu'il ne connaît pas, ou un
    entier qui n'en est pas un, arrête la relecture au lieu de se perdre."""
    simulateur = Simulateur(Parametres())
    carriere = simulateur.carriere_simple(annee_naissance=1970, sexe="F",
                                          affiliation="salarie_prive_non_cadre",
                                          age_debut=22.0, age_liquidation=64.0)
    ecrite = pont.carriere_en_donnees(carriere)
    relue = pont.carriere_des_donnees(_comme_node(ecrite))
    assert json.dumps(pont.carriere_en_donnees(relue)) == json.dumps(ecrite)
    with pytest.raises(ValueError, match="champs"):
        pont.carriere_des_donnees({**_comme_node(ecrite), "nouveau": 1})
    premiere, *suivantes = _comme_node(ecrite)["lignes"]
    with pytest.raises(ValueError, match="AnneeCarriere"):
        pont.carriere_des_donnees({**_comme_node(ecrite),
                                   "lignes": [{**premiere, "nouveau": 1}, *suivantes]})
    with pytest.raises(TypeError, match="entier"):
        pont.carriere_des_donnees({**_comme_node(ecrite), "annee_naissance": 1970.5})
    parametres = pont.parametres_des_donnees(_comme_node(pont.parametres_en_donnees(Parametres())))
    assert (json.dumps(pont.parametres_en_donnees(parametres))
            == json.dumps(pont.parametres_en_donnees(Parametres())))
    chronologie = pont.carriere_des_donnees({**_comme_node(ecrite), "chronologie": {
        "schema_version": 1, "liens": [], "faits": [
            {"attributs": {"age": 64, "trimestres": 4, "taux": 50}, "montant": {"mensuel": 100}},
            {"attributs": {"trimestres": 2.5, "revenu": 1500}}]}}).chronologie
    assert [json.dumps(fait) for fait in chronologie["faits"]] == [
        '{"attributs": {"age": 64.0, "trimestres": 4, "taux": 50}, "montant": {"mensuel": 100.0}}',
        '{"attributs": {"trimestres": 2.5, "revenu": 1500.0}}']


def test_les_parametres_passent_en_donnees_sous_les_noms_du_portage():
    """Tous les paramètres du Python, sauf la racine des données, dont le
    paquet tient lieu ; ceux de référence sont, valeur pour valeur, ceux du
    portage (``PARAMETRES_DEFAUT`` de ``moteur/js/config.js``)."""
    donnees = pont.parametres_en_donnees(Parametres())
    assert set(donnees) == {champ.name for champ in fields(Parametres)} - {"racine_donnees"}
    assert json.loads(json.dumps(donnees, allow_nan=False)) == donnees
    projection = pont.parametres_en_donnees(Simulateur(Parametres()).pour_la_projection().parametres)
    assert (projection["conventions_cor"],
            projection["minimum_vieillesse_dans_le_scenario_actuel"]) == (True, False)
    if shutil.which("node") is None:
        pytest.skip("node absent : les paramètres du portage ne se lisent pas ici")
    lus = subprocess.run(
        ["node", "--input-type=module", "-e",
         'const m = await import("./moteur/js/config.js");'
         "process.stdout.write(JSON.stringify(m.PARAMETRES_DEFAUT));"],
        cwd=RACINE_PROJET, capture_output=True, check=True).stdout
    assert donnees == json.loads(lus)


def test_la_grille_du_cout_passe_le_pont_au_bit_pres_du_moteur_python():
    """Ce que le coût lit de chaque case de sa grille — la pension de chaque
    système en euros constants ; la proposition sur la carrière où elle se
    calcule, sa garantie, son compte et son pilier ; le report de l'âge légal ;
    ce que le droit en vigueur prélève, année par année ; la part de chaque
    régime ; la population de sa mortalité — et la proposition seule sur les
    carrières qu'il en dérive : le portage le rend, sur des carrières passées
    en données et sous les paramètres de la projection, au bit près de ce que
    le moteur Python calcule (``cout._simulations_en_python``), chaque nombre
    sous son type."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    simulateur = Simulateur(Parametres()).pour_la_projection()
    macro = simulateur.macro
    age_legal = simulateur.parametres.age_legal_liberal
    cas = []
    for code, generation in CASES_DU_COUT:
        carriere = _carriere_du_cout(simulateur, code, generation)
        cas.append({"cle": f"{code}|{generation}", "carriere": carriere, "propositions": {
            "sans_report": carriere,
            "reportee": carriere.prolongee(age_legal, macro),
            "attente": carriere.prolongee(age_legal, macro, attente_travaillee=False)}})
    scenarios = [cle for cle, _ in cout.SCENARIOS]
    attendus, refus = cout._simulations_en_python(simulateur, cas, scenarios)
    assert not refus
    resultats, echecs = pont.grille_du_cout(cas, scenarios, simulateur.parametres,
                                            pont.paquet_des_donnees())
    assert not echecs
    assert _types(resultats) == _types(attendus)
    assert resultats == attendus
    # Ce que les cases font traverser : un report, un départ déjà pris, un
    # pilier, une population de mortalité, une pension de deux régimes.
    lus = resultats.values()
    assert {lu["depart_reporte"] for lu in lus} == {True, False}
    assert any(lu["liberal"]["pilier"] is not None for lu in lus)
    assert any(lu["liberal"]["pilier"] is None for lu in lus)
    assert any(lu["population"] is not None for lu in lus)
    assert any(len(lu["pensions_par_regime"]) > 1 for lu in lus)


def test_les_parametres_du_cout_passent_le_pont():
    """Une variante de la projection — la bascule en 2030 — se simule sous ses
    paramètres, non sous ceux de référence : le pilier ne s'ouvre qu'à elle."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    variante = replace(Parametres(), annee_bascule=2030)
    scenarios = ["actuel", "notionnel_liberal"]
    lus = {}
    for parametres in (Parametres(), variante):
        simulateur = Simulateur(parametres).pour_la_projection()
        carriere = _carriere_du_cout(simulateur, "salaire_moyen", 1975)
        cas = [{"cle": "salaire_moyen|1975", "carriere": carriere, "propositions": {}}]
        attendus, _ = cout._simulations_en_python(simulateur, cas, scenarios)
        resultats, _ = pont.grille_du_cout(cas, scenarios, simulateur.parametres,
                                           pont.paquet_des_donnees())
        assert resultats == attendus
        lus[parametres.annee_bascule] = resultats["salaire_moyen|1975"]
    assert min(lus[2026]["liberal"]["pilier"]["annees"]) == 2026
    assert min(lus[2030]["liberal"]["pilier"]["annees"]) == 2030
    assert lus[2030]["pensions"]["notionnel_liberal"] != lus[2026]["pensions"]["notionnel_liberal"]


def test_les_lignes_du_compte_d_un_scenario_passent_le_pont_sous_un_bareme():
    """Les scénarios que la demande nomme (``comptes``), la grille du coût rend
    de plus, de chaque case, les lignes de leur compte — ce qu'il porte, année
    par année, et sur quels revenus —, ce que ``scripts/solde_fusion.py`` lit
    du scénario 4 sous le barème d'un régime unique (action 161) : au bit près
    du jumeau (``cout._simulations_en_python``), sous le modèle comme sous un
    barème, qui ne change que ce que le compte porte après la bascule. Sans
    ``comptes``, aucune ligne."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    scenarios = [cle for cle, _ in cout.SCENARIOS]
    comptes = ("notionnel_retroactif", "notionnel_retroactif_employeur")
    lus = {}
    for bareme in (None, BAREMES[0]):
        simulateur = Simulateur(replace(Parametres(), bareme_regime_unique=bareme)
                                ).pour_la_projection()
        cas = [{"cle": f"{code}|{generation}", "propositions": {},
                "carriere": _carriere_du_cout(simulateur, code, generation)}
               for code, generation in CASES_DU_COUT]
        attendus, refus = cout._simulations_en_python(simulateur, cas, scenarios, comptes)
        resultats, echecs = pont.grille_du_cout(cas, scenarios, simulateur.parametres,
                                                pont.paquet_des_donnees(), comptes=comptes)
        assert not refus and not echecs
        assert _types(resultats) == _types(attendus)
        assert resultats == attendus, bareme
        assert all(set(lu["comptes"]) == set(comptes) for lu in resultats.values())
        lus[bareme] = resultats
    sans = pont.grille_du_cout(cas[:1], scenarios, simulateur.parametres,
                               pont.paquet_des_donnees())[0]
    assert all(lu["comptes"] == {} for lu in sans.values())
    bascule = Parametres().annee_bascule
    touches = 0
    for cle, lu in lus[BAREMES[0]].items():
        for scenario in comptes:
            avec, modele = lu["comptes"][scenario], lus[None][cle]["comptes"][scenario]
            assert avec["revenus"] == modele["revenus"], (cle, scenario)
            assert ({annee: c for annee, c in avec["cotisations"].items() if annee < bascule}
                    == {annee: c for annee, c in modele["cotisations"].items()
                        if annee < bascule}), (cle, scenario)
            touches += avec["cotisations"] != modele["cotisations"]
    assert touches > 0


# -- le coût branché sur le pont --------------------------------------------------

#: Une grille d'essai où passe ce que le coût lit en profondeur : l'entrée
#: tardive et les primes projetées, l'inaptitude, le report de l'âge légal, la
#: bascule qui passe entre les cohortes d'une génération.
GRILLE_D_ESSAI = tuple(cas for cas in GRILLE_DU_COUT if cas.code in (
    "fonctionnaire_sedentaire", "salaire_moyen", "smic_carriere_complete~inapte"))


def test_le_cout_simule_sa_grille_par_le_portage_sans_repli(memoire_isolee, monkeypatch):
    """Le modèle intact, sur les données du dépôt, la grille du coût se simule
    par le portage (action 161, étape 5) : sans node, elle s'arrête, sans
    repli sur le moteur Python."""
    from retraite_notionnelle import cout

    monkeypatch.setattr(cout, "generations", lambda: (1970,))
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        cout._pensionnes(Simulateur(Parametres()), GRILLE_D_ESSAI, "droit")


def test_le_cout_date_et_bat_sa_grille_par_le_portage_sans_les_jumeaux(memoire_isolee,
                                                                        monkeypatch):
    """Le modèle intact, sur les données du dépôt, le coût fait dater et bâtir
    sa grille au portage, comme il la fait simuler (action 161, étape 6) : le
    pilote Python, l'ouverture du droit qu'il interroge, les constructeurs de
    carrières, la projection des primes et le moteur Python, qu'on empêche ici
    de calculer, n'y entrent pas — ni dans ses cohortes nées toute l'année.
    Couple pour couple, la grille est celle que le Python date, bâtit et simule
    sous ``pont.par_le_jumeau()``."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    monkeypatch.setattr(cout, "generations", lambda: (1965, 2000))
    simulateur = Simulateur(Parametres())
    with pont.par_le_jumeau():
        en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
        nees_en_python = cout._nees_toute_l_annee(simulateur, GRILLE_D_ESSAI, en_python[0],
                                                  "droit")
    empecher_les_jumeaux_du_cout(monkeypatch)
    par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    assert par_le_portage == en_python
    assert _types([vars(p) for p in par_le_portage[0]]) == _types([vars(p) for p in en_python[0]])
    assert cout._nees_toute_l_annee(simulateur, GRILLE_D_ESSAI, par_le_portage[0],
                                    "droit") == nees_en_python
    # Ce que la grille d'essai fait traverser : un report de l'âge légal, la
    # bascule entre les cohortes d'une génération.
    assert any(p.propre.annee_liquidation > p.annee_liquidation for p in par_le_portage[0])
    assert any(p.autre is not None for p in par_le_portage[0])


def test_sous_le_jumeau_le_cout_simule_sa_grille_en_python(memoire_isolee, monkeypatch):
    """Une confrontation qui fait refaire au jumeau ce que le portage calcule
    s'ouvre sous ``pont.par_le_jumeau()`` : la grille s'y simule par le moteur
    Python, sans rien faire dater, bâtir ni simuler au portage, et rend ce
    que le portage rend, couple pour couple, chaque nombre au bit près. Une
    seule demande part encore : les séries de la revalorisation servie, que
    le portage seul calcule et que le jumeau lit comme le coût (note de
    décision 0007)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    monkeypatch.setattr(cout, "generations", lambda: (1950, 1965, 1975, 2000))
    simulateur = Simulateur(Parametres())
    par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    demandes = []
    demander = pont._demander

    def espion(demande, paquet):
        demandes.extend(demande)
        return demander(demande, paquet)

    monkeypatch.setattr(pont, "_demander", espion)
    with pont.par_le_jumeau():
        en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    assert demandes == ["revalorisation_servie"]
    assert en_python == par_le_portage
    assert _types([vars(p) for p in en_python[0]]) == _types([vars(p) for p in par_le_portage[0]])
    pensionnes = par_le_portage[0]
    assert len(pensionnes) == len(GRILLE_D_ESSAI) * 4
    assert any(p.autre is not None for p in pensionnes)
    assert any(p.propre.annee_liquidation > p.annee_liquidation for p in pensionnes)


def test_le_cout_d_une_variante_simule_sa_grille_par_le_portage(memoire_isolee, monkeypatch):
    """Le coût sous une variante d'une étude — la proposition prospective,
    ``scripts/proposition_prospective.py`` — simule sa grille par le portage,
    la variante dans la demande (action 161) : couple pour couple, chaque
    nombre sous son type, ce que le jumeau calcule de la même variante sous
    ``pont.par_le_jumeau()`` ; et autre chose que le coût du scénario 6, sur
    une génération partie avant la bascule comme sur une autre, après."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    monkeypatch.setattr(cout, "generations", lambda: (1950, 2000))
    simulateur = Simulateur(Parametres(), variantes=_variantes())
    with pont.par_le_jumeau():
        en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    assert par_le_portage == en_python
    assert _types([vars(p) for p in par_le_portage[0]]) == _types([vars(p) for p in en_python[0]])
    du_scenario_6 = cout._pensionnes(Simulateur(Parametres()), GRILLE_D_ESSAI, "droit")[0]
    for generation in (1950, 2000):
        assert any(p.propre != q.propre for p, q in zip(par_le_portage[0], du_scenario_6)
                   if p.generation == generation), generation


def test_le_cout_sous_la_regle_du_stock_simule_sa_grille_par_le_portage(memoire_isolee,
                                                                         monkeypatch):
    """Le coût sous la règle du stock à l'âge légal
    (``Parametres.stock_age_legal``, ``scripts/stock_age_legal.py``) simule sa
    grille par le portage, la règle dans les paramètres de la demande
    (action 161) : couple pour couple, chaque nombre sous son type, ce que le
    jumeau calcule sous la même règle et ``pont.par_le_jumeau()`` ; et autre
    chose que sans elle, sur la génération que la règle touche — partie avant
    la bascule sous ``droit_commun``, après sous ``acquis``."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout
    from retraite_notionnelle.config import StockAgeLegal

    monkeypatch.setattr(cout, "generations", lambda: (1950, 2000))
    sans = cout._pensionnes(Simulateur(Parametres()), GRILLE_D_ESSAI, "droit")[0]
    for regle, touchee in ((StockAgeLegal.DROIT_COMMUN, 1950), (StockAgeLegal.ACQUIS, 2000)):
        simulateur = Simulateur(replace(Parametres(), stock_age_legal=regle))
        with pont.par_le_jumeau():
            en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
        par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
        assert par_le_portage == en_python, regle
        assert (_types([vars(p) for p in par_le_portage[0]])
                == _types([vars(p) for p in en_python[0]])), regle
        # La pension de chaque scénario : ``acquis`` ne touche que les
        # prospectifs, que le volet de la proposition ne porte pas.
        assert any(p.pensions != q.pensions for p, q in zip(par_le_portage[0], sans)
                   if p.generation == touchee), regle


def test_sous_monkeypatch_le_cout_simule_sa_grille_par_le_portage(monkeypatch):
    """``monkeypatch`` fait taire la mémoire des calculs (``tests/conftest.py``),
    sans renvoyer au jumeau Python : ce qu'un test remplace du coût ou d'une
    étude, le Python le lit, et le portage simule la grille. Sans node, elle
    s'arrête donc, sans repli sur le moteur Python."""
    from retraite_notionnelle import cout, memoire

    assert not memoire._active()
    monkeypatch.setattr(cout, "generations", lambda: (1970,))
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        cout._pensionnes(Simulateur(Parametres()), GRILLE_D_ESSAI, "droit")


def test_sur_des_donnees_d_ailleurs_le_cout_calcule_par_le_portage(tmp_path):
    """Des données d'ailleurs — une copie que l'on a retouchée
    (``scripts/facteurs_depense.py --sans-suspension``) — se calculent par le
    portage, sur leur paquet (``pont.paquet_des_donnees``), comme celles du
    dépôt : seul ``pont.par_le_jumeau()`` renvoie au moteur Python. Un
    contexte qui ne fait que taire la mémoire des calculs
    (``memoire.modele_modifie``) laisse calculer le portage."""
    from retraite_notionnelle import memoire

    ailleurs = replace(Parametres(), racine_donnees=tmp_path)
    assert pont.par_le_portage(Parametres())
    assert pont.par_le_portage(ailleurs)
    with memoire.modele_modifie():
        assert pont.par_le_portage(Parametres())
    with pont.par_le_jumeau():
        assert not pont.par_le_portage(Parametres())
        assert not pont.par_le_portage(ailleurs)
        assert not memoire._active()
    assert pont.par_le_portage(Parametres())


#: Le levier qui fait calculer le jumeau Python (``pont.par_le_jumeau``).
LEVIER = "par_le_jumeau"

#: Les confrontations qui font refaire au jumeau Python ce que le portage
#: calcule, par fichier : avec les tests du levier (:data:`TESTS_DU_LEVIER`),
#: seules à ouvrir ``pont.par_le_jumeau()`` (action 161, le coût sous un modèle
#: modifié, sous-étape 6). Aucune étude ni aucun script ne l'ouvre : une
#: variante qui remplacerait une fonction du moteur, que le portage ne voit
#: pas, s'écrit en données, une couche ou un paramètre de la demande au pont
#: (note de décision 0006). Une confrontation part avec la paire qu'elle
#: confronte, et le levier avec la dernière.
CONFRONTATIONS_DU_JUMEAU = {
    "tests/test_cout.py": ("test_le_portage_bat_toute_la_grille_du_cout_comme_le_python",),
    "tests/test_grille_large.py": (
        "test_la_grille_large_se_date_et_se_bat_au_portage_sans_les_jumeaux",
        "test_les_mesures_de_la_grille_large_passent_par_le_portage_sans_les_jumeaux"),
    "tests/test_pont.py": (
        "test_la_grille_des_carrieres_types_se_date_au_portage_sans_les_jumeaux",
        "test_les_departs_des_facteurs_de_la_depense_se_datent_au_portage_sans_les_jumeaux",
        "test_le_cout_des_avantages_liquide_sa_grille_au_portage_sans_les_jumeaux",
        "test_le_cout_date_et_bat_sa_grille_par_le_portage_sans_les_jumeaux",
        "test_le_cout_d_une_variante_simule_sa_grille_par_le_portage",
        "test_le_cout_sous_la_regle_du_stock_simule_sa_grille_par_le_portage",
        "test_sur_des_donnees_d_ailleurs_le_cout_date_bat_et_simule_sa_grille_par_le_portage"),
    "tests/test_solde_fusion.py": (
        "test_la_grille_se_simule_par_le_portage_au_bit_pres_du_jumeau",),
    "tests/test_stock_age_legal.py": (
        "test_les_cas_types_passent_par_le_portage_au_bit_pres_du_jumeau",),
}

#: Les tests du levier lui-même — ce qu'il aiguille, le moteur Python qui
#: calcule sous lui —, qui partent avec lui.
TESTS_DU_LEVIER = {"tests/test_pont.py": (
    "test_sous_le_jumeau_le_cout_simule_sa_grille_en_python",
    "test_sur_des_donnees_d_ailleurs_le_cout_calcule_par_le_portage")}


def _ouvertures_du_levier(source: str) -> set[str]:
    """Les définitions de premier niveau d'un module, fonctions et classes —
    « » pour ce qui est hors d'elles —, qui ouvrent le levier ou touchent son
    compteur (``pont._JUMEAU``) : qui les nomment dans leur code, hors des
    chaînes, ou importent le levier."""
    def nomme(noeud) -> bool:
        if isinstance(noeud, ast.Name):
            return noeud.id == LEVIER
        if isinstance(noeud, ast.Attribute):
            return noeud.attr in (LEVIER, "_JUMEAU")
        return isinstance(noeud, ast.alias) and noeud.name.rpartition(".")[2] == LEVIER

    definitions = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    return {haut.name if isinstance(haut, definitions) else ""
            for haut in ast.parse(source).body if any(map(nomme, ast.walk(haut)))}


def test_seules_les_confrontations_ouvrent_le_jumeau():
    """Le levier qui fait calculer le jumeau Python, ``pont.par_le_jumeau()``,
    ne s'ouvre que dans les confrontations, qui font refaire au jumeau ce que
    le portage calcule, et dans les tests du levier, déclarés un à un
    (:data:`CONFRONTATIONS_DU_JUMEAU`, :data:`TESTS_DU_LEVIER`) : aucune
    étude, aucun script, aucun module du modèle ne l'ouvre ni ne touche son
    compteur (action 161, le coût sous un modèle modifié, sous-étape 6). Plus
    aucune confrontation, le levier part. Chaque fichier Python du dépôt, suivi
    ou nouveau, se lit dans son arbre syntaxique, où se voient l'attribut,
    l'import et le compteur, et non une mention dans une chaîne."""
    assert _ouvertures_du_levier(textwrap.dedent('''\
        from retraite_notionnelle import pont
        from retraite_notionnelle.pont import par_le_jumeau as levier

        def etude():
            with pont.par_le_jumeau():
                pass

        class Variante:
            def __enter__(self):
                pont._JUMEAU += 1

        def mention():
            """``pont.par_le_jumeau()``, nommé dans une chaîne, ne s'ouvre pas."""
        ''')) == {"", "etude", "Variante"}
    sortie = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.py"],
        cwd=RACINE_PROJET, capture_output=True, check=True).stdout.decode("utf-8")
    trouvees = set()
    for chemin in sorted(c for c in sortie.split("\0") if c and (RACINE_PROJET / c).is_file()):
        texte = (RACINE_PROJET / chemin).read_text(encoding="utf-8")
        if LEVIER in texte or "_JUMEAU" in texte:
            trouvees |= {(chemin, nom) for nom in _ouvertures_du_levier(texte)}
    hors_des_tests = sorted(ouverture for ouverture in trouvees
                            if not ouverture[0].startswith("tests/"))
    assert hors_des_tests == [], (
        "une étude n'ouvre pas pont.par_le_jumeau() : sa variante s'écrit en données, une "
        "couche ou un paramètre de la demande au pont (note de décision 0006), et le portage "
        "la calcule")
    declarees = {(chemin, nom) for registre in (CONFRONTATIONS_DU_JUMEAU, TESTS_DU_LEVIER)
                 for chemin, noms in registre.items() for nom in noms}
    assert sorted(trouvees - declarees) == [], (
        "ouvrent pont.par_le_jumeau() sans être déclarées : une confrontation se déclare "
        "dans CONFRONTATIONS_DU_JUMEAU, et une variante s'écrit en données")
    assert sorted(declarees - trouvees) == [], (
        "déclarées, elles n'ouvrent plus pont.par_le_jumeau() : leur déclaration part")
    if not any(CONFRONTATIONS_DU_JUMEAU.values()):
        assert not hasattr(pont, LEVIER), (
            "plus aucune confrontation n'ouvre pont.par_le_jumeau() : le levier part, avec "
            "TESTS_DU_LEVIER et l'aiguillage de pont.par_le_portage")


@pytest.fixture
def donnees_d_ailleurs(tmp_path):
    """Des données d'ailleurs : une copie de celles du dépôt que l'on a
    retouchée, comme ``scripts/facteurs_depense.py --sans-suspension`` récrit
    la sienne. La génération 1968 y ouvre son droit à soixante-six ans, et non
    à soixante-trois ans et neuf mois."""
    copie = tmp_path / "data"
    shutil.copytree(RACINE_DONNEES, copie)
    _recrire_l_age_legal(copie, "63.75", "66.00")
    return copie


def _recrire_l_age_legal(copie, avant: str, apres: str) -> None:
    """L'âge légal de la génération 1968 de la copie, récrit."""
    table = copie / "reference" / "legislation" / "age_ouverture_requis.csv"
    texte = table.read_text(encoding="utf-8")
    assert texte.count(f"\n1968,{avant},") == 1
    table.write_text(texte.replace(f"\n1968,{avant},", f"\n1968,{apres},"), encoding="utf-8")


def test_des_donnees_d_ailleurs_ont_leur_paquet(donnees_d_ailleurs):
    """Le paquet de données d'ailleurs se bâtit depuis elles, par la fabrique
    (``pont.paquet_des_donnees``) : l'âge légal que la copie retouche y est, et
    rien d'autre n'y change ; le paquet du dépôt n'en sait rien. Il se bâtit
    une fois par état de leurs fichiers : retouchées encore, il se rebâtit."""
    leur = pont.paquet_des_donnees(donnees_d_ailleurs)
    du_depot = json.loads(pont.paquet_des_donnees())
    lu = json.loads(leur)
    assert lu["ages_ouverture"]["1968"] == [66.0, 3]
    assert du_depot["ages_ouverture"]["1968"] == [63.75, 3]
    assert lu.keys() == du_depot.keys()
    assert {cle for cle in lu if lu[cle] != du_depot[cle]} == {"ages_ouverture"}
    assert pont.paquet_des_donnees(donnees_d_ailleurs) is leur
    _recrire_l_age_legal(donnees_d_ailleurs, "66.00", "66.250")
    assert json.loads(pont.paquet_des_donnees(donnees_d_ailleurs))["ages_ouverture"]["1968"] == [
        66.25, 3]


def test_le_paquet_de_donnees_d_ailleurs_ne_lit_rien_de_celles_du_depot(monkeypatch, tmp_path):
    """Bâti depuis des données d'ailleurs, le paquet ne lit rien de celles du
    dépôt : la fabrique y lit ce que sa racine désigne (``DONNEES``), et une
    lecture qui irait aux données du dépôt par un autre chemin mêlerait les
    deux sans bruit. Le pont l'arrête."""
    fabrique = tmp_path / "fabrique.py"
    fabrique.write_text(textwrap.dedent(f"""\
        from pathlib import Path
        DONNEES = Path({str(RACINE_DONNEES)!r})
        def construire(bilan, agregats):
            ici = (DONNEES / "sources.yaml").read_bytes()
            return ici + Path({str(RACINE_DONNEES / "sources.yaml")!r}).read_bytes()[:1]
        """), encoding="utf-8")
    copie = tmp_path / "data"
    copie.mkdir()
    (copie / "sources.yaml").write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(pont, "FABRIQUE", fabrique)
    with pytest.raises(RuntimeError, match=re.escape(str(RACINE_DONNEES / "sources.yaml"))):
        pont.paquet_des_donnees(copie)


def test_des_donnees_d_ailleurs_se_calculent_sur_leur_paquet(donnees_d_ailleurs):
    """Une demande au pont sous des paramètres qui lisent des données d'ailleurs
    se calcule sur leur paquet : sans paquet, le pont le prend ; celui du
    dépôt, il le refuse, qui la ferait calculer sur d'autres données que les
    siennes."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    ailleurs = replace(Parametres(), racine_donnees=donnees_d_ailleurs)
    appel = {"1968": ("scenario_actuel.ages_ouverture.age", pont.MOTEUR, 1968)}
    assert pont.droit(appel, Parametres())[0]["1968"][0] == 63.75
    assert pont.droit(appel, ailleurs)[0]["1968"][0] == 66.0
    assert pont.droit(appel, ailleurs, pont.paquet_des_donnees(donnees_d_ailleurs))[0][
        "1968"][0] == 66.0
    with pytest.raises(ValueError, match="leur paquet"):
        pont.droit(appel, ailleurs, pont.paquet_des_donnees())


def test_sur_des_donnees_d_ailleurs_le_cout_date_bat_et_simule_sa_grille_par_le_portage(
        memoire_isolee, monkeypatch, donnees_d_ailleurs):
    """Des données d'ailleurs, le coût date, bâtit et simule sa grille au
    portage, sur leur paquet, comme celle du dépôt : les jumeaux Python, qu'on
    empêche ici de calculer, n'y entrent pas, et la grille est celle que le
    Python date, bâtit et simule sur la copie sous ``pont.par_le_jumeau()``,
    couple pour couple, au bit près. Ce n'est pas celle du dépôt : le salarié
    au salaire moyen né en 1968, qui a sa durée à 64 ans, y attend l'âge légal
    de la copie, et part en 2034 et non en 2032 ; l'inapte, qui part à 62 ans,
    ne bouge pas."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle import cout

    monkeypatch.setattr(cout, "generations", lambda: (1968,))
    simulateur = Simulateur(replace(Parametres(), racine_donnees=donnees_d_ailleurs))
    with pont.par_le_jumeau():
        en_python = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    du_depot = cout._pensionnes(Simulateur(Parametres()), GRILLE_D_ESSAI, "droit")
    empecher_les_jumeaux_du_cout(monkeypatch)
    par_le_portage = cout._pensionnes(simulateur, GRILLE_D_ESSAI, "droit")
    assert par_le_portage == en_python
    assert _types([vars(p) for p in par_le_portage[0]]) == _types([vars(p) for p in en_python[0]])

    def departs(pensionnes) -> dict[str, int]:
        return {p.code: p.annee_liquidation for p in pensionnes[0]}

    assert departs(du_depot) == {"salaire_moyen": 2032, "fonctionnaire_sedentaire": 2033,
                                 "smic_carriere_complete~inapte": 2030}
    assert departs(par_le_portage) == {**departs(du_depot), "salaire_moyen": 2034,
                                       "fonctionnaire_sedentaire": 2034}


def test_le_paquet_du_jour_suit_les_sources(monkeypatch, tmp_path):
    """Le paquet du jour se bâtit une fois par état des sources de la mémoire
    des calculs, et non une fois par processus : une donnée retouchée pendant
    qu'un processus calcule entre dans le paquet de son calcul suivant, et la
    mémoire ne garde pas, sous l'empreinte des données nouvelles, une grille
    simulée sur le paquet des anciennes."""
    from retraite_notionnelle import memoire

    depot = tmp_path / "depot"
    (depot / "data").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(depot)], check=True)
    donnee = depot / "data" / "taux.csv"
    donnee.write_text("annee,taux\n2026,1\n", encoding="utf-8")
    monkeypatch.setattr(memoire, "RACINE_PROJET", depot)
    reel, batis = subprocess.run, []

    def batir(commande, *arguments, **options):
        if commande[0] != sys.executable:
            return reel(commande, *arguments, **options)
        batis.append(commande)
        return subprocess.CompletedProcess(commande, 0, f"paquet {len(batis)}".encode(), b"")

    monkeypatch.setattr(subprocess, "run", batir)
    assert pont.paquet_des_donnees() == b"paquet 1"
    assert pont.paquet_des_donnees() == b"paquet 1"
    donnee.write_text("annee,taux\n2026,1.5\n", encoding="utf-8")
    assert pont.paquet_des_donnees() == b"paquet 2"


# -- la garantie d'une population (action 161, note de décision 0007) ---------


def _distribution_d_essai(*tranches):
    """Une distribution de tranches posées à la main, sans passer par le
    fichier de l'enquête."""
    from retraite_notionnelle.donnees.distribution import DistributionPensions, Tranche

    distribution = object.__new__(DistributionPensions)
    distribution.tranches = [Tranche(*tranche) for tranche in tranches]
    return distribution


def test_le_pont_chiffre_la_garantie_d_une_population():
    """La garantie d'une population ne s'écrit qu'en JavaScript
    (``moteur/js/garantie.js``, note de décision 0007) : le coût la demande au
    pont, par lot (:func:`pont.garantie`), ses distributions passées en
    données, et relit ce que chaque fonction rend sous le type du Python.

    Posé à la main. Un million de retraités, la moitié répartie de 0 à
    1 000 €, l'autre en masse ponctuelle à 1 000 €, sous un plancher
    différentiel de 1 500 € : la première moitié reçoit en moyenne 1 500 −
    500 = 1 000 €, la seconde 500 ; tous sont servis, de 750 € en moyenne,
    soit 750 × 12 = 9 000 M€ par an. Leur pension moyenne : 0,5 × 500 + 0,5 ×
    1 000 = 750 €. Si les femmes, la moitié, vivent toutes seules sous un
    plancher de 2 000 €, elles reçoivent en moyenne (1 500 + 1 000) / 2 =
    1 250 €, les hommes 750 : 1 000 € en moyenne, 12 000 M€. Et des pensions
    moyennes de 1 000 et 2 000 €, à parts égales, sous un rapport d'un demi :
    1 500 / (250 + 1 000) = 1,2 pour les hommes, 0,6 pour les femmes."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.cout import CoutGarantie

    distribution = _distribution_d_essai((0.0, 1000.0, 0.5), (1000.0, None, 0.5))
    cout, moyenne, manque, facteurs, par_sexe = pont.garantie([
        ("cout_garantie", distribution, 1e6, 1500.0, 1.0, 1.0, 1.0),
        ("pension_moyenne", distribution),
        ("manque_moyen", 0.0, 1000.0, 1500.0, 1.0, 1.0),
        ("facteurs_par_sexe", 1000.0, 2000.0, 0.5, 1.0, 0.5),
        ("cout_garantie_par_sexe", distribution, distribution, 0.5, 1e6, 1500.0, 1.0, 1.0,
         2000.0, {"F": 1.0, "H": 0.0}, 1.0, 1.0),
    ])
    assert cout == CoutGarantie(
        plancher_mensuel=1500.0, facteur=1.0, part_beneficiaires=1.0, beneficiaires=1e6,
        complement_moyen_mensuel=750.0, cout_annuel_meur=9000.0)
    assert moyenne == 750.0 and manque == (1.0, 1000.0) and facteurs == (0.6, 1.2)
    assert par_sexe == CoutGarantie(
        plancher_mensuel=1500.0, facteur=1.0, part_beneficiaires=1.0, beneficiaires=1e6,
        complement_moyen_mensuel=1000.0, cout_annuel_meur=12000.0)
    # Node n'écrit qu'un type de nombre : chacun revient flottant.
    for chiffre in (cout, par_sexe):
        assert all(type(valeur) is float for valeur in vars(chiffre).values())
    assert type(moyenne) is float and type(manque) is tuple
    assert all(type(valeur) is float for valeur in (*manque, *facteurs))
    # La masse ponctuelle au-dessus du plancher n'est pas servie : sa part
    # revient « 0 », relue flottante.
    assert pont.garantie([("manque_moyen", 1000.0, None, 800.0, 1.0, 1.0)]) == [(0.0, 0.0)]
    assert pont.garantie([]) == []


#: Ce que le barème refuse, et son motif : un facteur nul ou négatif, une
#: forme qui n'est pas un barème dégressif — un pivot hors du plancher, un
#: retrait nul, qui ne s'éteindrait jamais, ou de plus d'un euro par euro —,
#: un rapport ou des pensions moyennes qui ne sont pas positifs. Les messages
#: sont ceux que le jumeau Python opposait, relevés avant son retrait.
REFUS_DE_LA_GARANTIE = (
    (("cout_garantie", 1e6, 800.0, 0.0, 0.5, 0.5),
     "le facteur de déplacement doit être strictement positif"),
    (("cout_garantie", 1e6, 800.0, -1.0, 0.5, 0.5),
     "le facteur de déplacement doit être strictement positif"),
    (("cout_garantie", 1e6, 800.0, 1.0, -0.1, 0.5),
     "la part du plancher jusqu'où la pension est retirée en entier est entre zéro et un"),
    (("cout_garantie", 1e6, 800.0, 1.0, 1.1, 0.5),
     "la part du plancher jusqu'où la pension est retirée en entier est entre zéro et un"),
    (("cout_garantie", 1e6, 800.0, 1.0, 0.5, 0.0),
     "le taux de retrait est une part, entre zéro exclu et un"),
    (("cout_garantie", 1e6, 800.0, 1.0, 0.5, 1.5),
     "le taux de retrait est une part, entre zéro exclu et un"),
    (("facteurs_par_sexe", 1200.0, 1900.0, 0.53, 0.8, 0.0),
     "le rapport des deux facteurs doit être strictement positif"),
    (("facteurs_par_sexe", 0.0, 0.0, 0.53, 0.8, 1.0),
     "les pensions moyennes doivent être strictement positives"),
    (("cout_garantie_par_sexe", 0.5, 1e6, 800.0, 1.0, -0.5, None, None, 1.0, 1.0),
     "le rapport des deux facteurs doit être strictement positif"),
)


def test_le_pont_rend_les_refus_du_bareme_de_la_garantie():
    """Un appel que le barème refuse arrête le lot, de son motif, celui du
    portage, sous ``ValueError`` ; une fonction que le pont ne relit pas est
    refusée avant node."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    distribution = _distribution_d_essai((0.0, 1000.0, 0.5), (1000.0, None, 0.5))
    for (fonction, *arguments), motif in REFUS_DE_LA_GARANTIE:
        distributions = {"cout_garantie": (distribution,), "facteurs_par_sexe": (),
                         "cout_garantie_par_sexe": (distribution, distribution)}[fonction]
        with pytest.raises(ValueError) as refus:
            pont.garantie([("pension_moyenne", distribution),
                           (fonction, *distributions, *arguments)])
        assert str(refus.value) == motif, (fonction, arguments)
    with pytest.raises(ValueError, match="garantie_inconnue"):
        pont.garantie([("garantie_inconnue", distribution)])


def test_la_garantie_demandee_au_pont_se_passe_du_paquet(monkeypatch):
    """Le barème ne lit que ses arguments : la demande passe par le pont gardé
    ouvert, sans paquet, et ne relance pas node d'un chiffrage à l'autre —
    le coût en fait plusieurs centaines."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    distribution = _distribution_d_essai((0.0, 1000.0, 0.5), (1000.0, None, 0.5))
    pont.garantie([("pension_moyenne", distribution)])
    monkeypatch.setattr(pont.subprocess, "run", None)
    monkeypatch.setattr(pont.subprocess, "Popen", None)
    assert pont.garantie([("pension_moyenne", distribution)]) == [750.0]


def test_le_cout_chiffre_sa_garantie_par_le_portage_sans_repli(monkeypatch):
    """Le coût demande au portage le barème de sa garantie, chaque année, et
    les deux facteurs sous lesquels il déplace chaque sexe (action 161, note
    de décision 0007) : mêmes valeurs posées à la main que
    :func:`test_le_pont_chiffre_la_garantie_d_une_population` ; sans node, il
    s'arrête, sans repli sur un barème écrit en Python."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    from retraite_notionnelle.cout import CoutGarantie, GarantieDistribution

    distribution = _distribution_d_essai((0.0, 1000.0, 0.5), (1000.0, None, 0.5))
    calage = GarantieDistribution(distribution, 1500.0, 1000.0, 1.0, 1.0)
    neuf_milliards = CoutGarantie(
        plancher_mensuel=1500.0, facteur=1.0, part_beneficiaires=1.0, beneficiaires=1e6,
        complement_moyen_mensuel=750.0, cout_annuel_meur=9000.0)
    assert calage.chiffrer_distribution(1e6, 1.0) == neuf_milliards
    # Deux masses ponctuelles, à 1 000 € pour les femmes et 2 000 € pour les
    # hommes, à parts égales, sous un rapport d'un demi : 0,6 et 1,2.
    sexes = {"F": _distribution_d_essai((1000.0, None, 1.0)),
             "H": _distribution_d_essai((2000.0, None, 1.0))}
    par_sexe = GarantieDistribution(distribution, 1500.0, 1000.0, 1.0, 1.0,
                                    distributions_sexe=sexes, part_femmes=0.5,
                                    rapport_deplacement=0.5)
    assert par_sexe.facteurs_des_sexes(1.0) == (0.6, 1.2)
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        calage.chiffrer_distribution(1e6, 1.0)
    with pytest.raises(pont.PontIndisponible, match="node"):
        par_sexe.facteurs_des_sexes(1.0)


# -- l'impôt sur le revenu (action 161, note de décision 0007) ----------------


def _retraites(*pensions: float) -> dict:
    """Un foyer de retraités de 70 ans, en données : une pension chacun."""
    return {"declarants": [{"pensions": pension, "age": 70} for pension in pensions]}


def test_le_pont_calcule_l_impot_de_chaque_foyer():
    """L'impôt sur le revenu ne s'écrit qu'en JavaScript
    (``moteur/js/impot-revenu.js``, note de décision 0007) : l'effet retour le
    demande au pont, par lot (:func:`pont.impot`), ses foyers passés en
    données. Les valeurs sont posées à la main sur le barème des revenus de
    2024 (CGI, art. 197, I, art. 158, 5, a, et art. 157 bis, dans leur
    rédaction de la loi n° 2025-127 du 14 février 2025, art. 2).

    Un retraité seul de 70 ans, 30 000 € de pension : l'abattement de 10 %,
    3 000 €, laisse 27 000 € ; celui des personnes âgées, 1 398 € entre
    17 510 € et 28 170 €, laisse 25 602 € ; au barème,
    (25 602 − 11 497) × 11 % = 1 551,55 € ; la décote,
    889 − 45,25 % × 1 551,55 = 186,92 € ; l'impôt, 1 364,63 €, arrondi à
    1 365 €. Avec 15 000 € : 13 500 €, moins 2 796 € sous 17 510 €, soit
    10 704 €, sous la première tranche : aucun impôt, rien en recouvrement.
    Un couple de 40 000 € et 20 000 € : l'abattement de 10 %, 6 000 €, est
    plafonné à 4 399 € pour le foyer, soit 55 601 €, au-delà de 28 170 € ;
    par part, (27 800,50 − 11 497) × 11 % = 1 793,385 €, soit 3 586,77 €
    pour deux, sans décote (1 470 − 45,25 % × 3 586,77 < 0) : 3 587 €."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    seul, modeste, couple, avant_les_baremes = pont.impot([
        (2024, _retraites(30000.0)), (2024, _retraites(15000.0)),
        (2024, _retraites(40000.0, 20000.0)), (1950, _retraites(30000.0))])
    assert seul == pont.ImpotDemande(impot=1365.0, mis_en_recouvrement=True)
    assert modeste == pont.ImpotDemande(impot=0.0, mis_en_recouvrement=False)
    assert couple == pont.ImpotDemande(impot=3587.0, mis_en_recouvrement=True)
    assert [type(seul.impot), type(modeste.impot), type(seul.mis_en_recouvrement)] == [
        float, float, bool]
    # Avant le premier barème lu, 1960, et après la dernière année demandée :
    # aucun barème, aucun impôt à rendre.
    assert avant_les_baremes is None
    assert pont.impot([(2041, _retraites(30000.0))], derniere=2040) == [None]
    assert pont.impot([]) == []


def test_le_bareme_projete_suit_l_indexation_demandee():
    """Au-delà de la dernière loi de finances lue, le barème se projette sur
    les prix, ou sur le salaire moyen, qui croît plus vite : la même pension
    de 2060, en euros de 2060, paie alors moins d'impôt. Sous les paramètres
    du simulateur, ceux de référence sans eux."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    foyer = _retraites(100000.0)
    [prix] = pont.impot([(2060, foyer)], Parametres())
    [salaires] = pont.impot([(2060, foyer)], indexation="salaire_moyen")
    assert pont.impot([(2060, foyer)]) == [prix]
    assert 0.0 < salaires.impot < prix.impot and prix.mis_en_recouvrement


def test_le_pont_rend_les_refus_de_l_impot():
    """Un foyer que l'impôt refuse arrête le lot, du message du portage."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")
    with pytest.raises(ValueError, match="un foyer a un déclarant, ou deux"):
        pont.impot([(2024, _retraites(30000.0)),
                    (2024, _retraites(10000.0, 10000.0, 10000.0))])


# -- la revalorisation servie et l'indexation (action 161, note de décision 0007) --


def _sans_node():
    if shutil.which("node") is None:
        pytest.skip("node absent : le pont ne se vérifie pas ici")


#: Le simulateur de la page Coût (``Simulateur.pour_la_projection``) : sous
#: les conventions du COR, la valeur de service de l'Agirc-Arrco est convenue.
SOUS_LE_COR = dict(conventions_cor=True, minimum_vieillesse_dans_le_scenario_actuel=False)


def _regles(**reglages) -> Parametres:
    """Les paramètres d'un jeu de réglages, la règle d'indexation et celle du
    stock écrites par leur valeur."""
    from retraite_notionnelle.config import ModeIndexation, RevalorisationStock

    types_ = {"mode_indexation": ModeIndexation, "revalorisation_stock": RevalorisationStock}
    return Parametres(**{nom: types_.get(nom, lambda valeur: valeur)(valeur)
                         for nom, valeur in reglages.items()})


def test_le_pont_rend_les_series_de_la_revalorisation_servie():
    """Le cœur de la revalorisation servie ne s'écrit qu'en JavaScript
    (``RevalorisationServie`` de ``moteur/js/revalorisation.js``, note de
    décision 0007) : le coût en demande les séries au pont, une demande par
    jeu de paramètres (:func:`pont.series_servies`), et sa classe Python ne
    fait plus que les lire. Les valeurs sont posées à la main.

    L'index du compte, en euros constants, vaut un la première année, et
    gagne chaque année le taux d'indexation déflaté des prix. En 2023, sous
    la masse salariale, +5,625 % (``data/reference/macro/masse_salariale.csv``)
    contre +4,875 % de prix (``ipc_annuel.csv``) : 1,05625 / 1,04875. Un
    diviseur actualisé à 1,6 % a servi d'avance ce rendement : la pension
    servie le rend chaque année, soit 1,016 puissance dix de moins en dix
    ans, la règle suédoise.

    La valeur de service de l'Agirc-Arrco, sous les conventions du COR
    (``conventions_points`` de ``hypotheses_projection.yaml``) : le salaire
    moyen moins 1,16 point de 2027 à 2037, moins 0,86 ensuite, quand le
    scénario de référence porte le salaire à 2,45 % et les prix à 1,75 %.
    De 2026 à 2040, en euros constants : (1,0129 / 1,0175) puissance onze,
    fois (1,0159 / 1,0175) puissance trois, soit 0,9469. Elle sert, au bout
    de leurs fusions, les points de l'Arrco et de l'Agirc ; le régime général
    n'a pas de valeur de service."""
    _sans_node()
    series = pont.series_servies(Parametres(), 2020, 2030)
    assert (series.premiere_annee, series.derniere_annee) == (2020, 2030)
    assert list(series.index) == list(range(2020, 2031))
    assert series.index[2020] == 1.0
    assert {type(annee) for annee in series.index} == {int}
    assert {type(valeur) for valeur in series.index.values()} == {float}
    assert series.index[2023] / series.index[2022] == pytest.approx(
        1.05625 / 1.04875, rel=1e-12)
    # Sans les conventions du COR, aucune valeur de service n'est convenue.
    assert series.points == {}
    assert series.convenus["arrco"] is None and series.convenus["regime_general"] is None

    prefinancee = pont.series_servies(Parametres(taux_anticipe_conversion=0.016), 2020, 2030)
    assert prefinancee.index[2030] / series.index[2030] == pytest.approx(
        1.016 ** -10, rel=1e-12)

    cor = pont.series_servies(Parametres(**SOUS_LE_COR), 2026, 2040)
    assert list(cor.points) == ["agirc_arrco"]
    valeur = cor.points["agirc_arrco"]
    assert list(valeur) == list(range(2026, 2041)) and valeur[2026] == 1.0
    assert valeur[2040] == pytest.approx(
        (1.0129 / 1.0175) ** 11 * (1.0159 / 1.0175) ** 3, rel=1e-6)
    assert (cor.convenus["arrco"], cor.convenus["agirc"], cor.convenus["agirc_arrco"],
            cor.convenus["regime_general"]) == ("agirc_arrco", "agirc_arrco", "agirc_arrco", None)
    # Une dernière année d'avant la première : la première seule.
    assert pont.series_servies(Parametres(), 2030, 2020).index == {2030: 1.0}


def test_le_pont_fait_lire_la_revalorisation_servie_au_portage():
    """Les quatre lectures que la classe Python garde — le coefficient, la
    règle du stock à la bascule, la valeur de service, le régime convenu —
    se demandent aussi au portage lui-même (:func:`pont.revalorisation_servie`),
    pour les confronter. Les valeurs sont posées à la main : le coefficient
    de 2022 à 2023, 1,05625 / 1,04875 ; un, exactement, tant que la pension
    n'est pas servie.

    La règle du stock (``revalorisation_stock``), pour une pension liquidée
    en 2012, lue en 2030, la bascule en 2026. Le stock aux prix : une réforme
    prospective ne lui donne rien, un ; une rétroactive le gèle à ce qu'il
    valait à la bascule, le coefficient de 2012 à 2026. Le stock réindexé :
    la prospective le prend à sa règle le jour de la bascule, le coefficient
    de 2026 à 2030 ; la rétroactive l'a toujours revalorisé, de 2012 à 2030.
    Une pension liquidée après la bascule suit la règle du compte dans tous
    les cas."""
    _sans_node()
    lire = lambda appels, **reglages: pont.revalorisation_servie(  # noqa: E731
        appels, _regles(**reglages), 1941, 2070)
    an, avant, de_2012_a_2026, de_2012_a_2030, de_2026_a_2030, de_2028_a_2030 = lire([
        ("coefficient", 2022, 2023), ("coefficient", 2023, 2022), ("coefficient", 2012, 2026),
        ("coefficient", 2012, 2030), ("coefficient", 2026, 2030), ("coefficient", 2028, 2030)])
    assert an == pytest.approx(1.05625 / 1.04875, rel=1e-12)
    assert avant == 1.0 and type(avant) is float
    stock = [("coefficient_stock", 2012, 2030, True), ("coefficient_stock", 2012, 2030, False),
             ("coefficient_stock", 2028, 2030, True), ("coefficient_stock", 2028, 2030, False)]
    assert lire(stock) == [1.0, de_2012_a_2026, de_2028_a_2030, de_2028_a_2030]
    assert lire(stock, revalorisation_stock="reindexe") == [
        de_2026_a_2030, de_2012_a_2030, de_2028_a_2030, de_2028_a_2030]
    assert de_2012_a_2026 != de_2012_a_2030 != de_2026_a_2030
    # La valeur de service convenue, et le régime qui la sert.
    points, sans_convention, arrco, general = lire([
        ("coefficient_points", "agirc_arrco", 2026, 2040),
        ("coefficient_points", "regime_general", 2026, 2040),
        ("regime_convenu", "arrco"), ("regime_convenu", "regime_general")], **SOUS_LE_COR)
    assert points == pytest.approx((1.0129 / 1.0175) ** 11 * (1.0159 / 1.0175) ** 3, rel=1e-6)
    assert (sans_convention, arrco, general) == (1.0, "agirc_arrco", None)
    assert pont.revalorisation_servie([], Parametres(), 1941, 2070) == []
    with pytest.raises(ValueError, match="coefficient_nominal"):
        lire([("coefficient_nominal", 2020, 2030)])


def test_le_pont_rend_les_taux_de_l_indexation():
    """L'indexation ne s'écrit qu'en JavaScript (``moteur/js/indexation.js``,
    note de décision 0007) : le coût, qui en lit le rendement d'une
    cotisation sous une variante démographique, le demande au pont, par lot
    (:func:`pont.indexation`). Les valeurs sont posées à la main sur 2023 :
    la masse salariale, +5,625 %, les prix, +4,875 %, le salaire moyen,
    +4,662 %, la productivité réelle, +1,099 % (``masse_salariale.csv``,
    ``ipc_annuel.csv``, ``salaire_moyen.csv`` et ``productivite.csv`` de
    ``data/reference/macro/``), et, en 2022, la masse salariale à +7,838 %.

    Une cotisation de 2021 arrêtée en 2023 a reçu les taux de 2022 et de
    2023, non celui de l'année de son versement : 1,07838 × 1,05625. Le
    triple verrou inversé retient le plus petit des trois taux, la
    productivité ; son plancher, s'il passe au-dessus, le remplace."""
    _sans_node()
    from retraite_notionnelle.donnees.chargement import Fiabilite
    from retraite_notionnelle.moteur.indexation import TauxIndexation

    taux, deux_ans, meme_annee, a_rebours = pont.indexation([
        ("taux", 2023), ("coefficient", 2021, 2023), ("coefficient", 2023, 2023),
        ("coefficient", 2023, 2021)])
    assert taux == TauxIndexation(
        annee=2023, taux=0.05625, terme_retenu="masse_salariale", inflation=0.04875,
        salaire_moyen=0.04662, productivite=0.01099, fiabilite=Fiabilite.CERTIFIEE)
    assert [type(taux.annee), type(taux.taux), type(taux.fiabilite)] == [int, float, Fiabilite]
    assert deux_ans == (1 + 0.07838) * (1 + 0.05625)
    assert (meme_annee, a_rebours) == (1.0, 1.0) and type(meme_annee) is float
    [verrou] = pont.indexation([("taux", 2023)], _regles(mode_indexation="triple_lock_inverse"))
    assert (verrou.taux, verrou.terme_retenu) == (0.01099, "productivite_reelle")
    [plancher] = pont.indexation([("taux", 2023)], _regles(
        mode_indexation="triple_lock_inverse", plancher_indexation=0.02))
    assert (plancher.taux, plancher.terme_retenu) == (0.02, "plancher")
    assert pont.indexation([]) == []
    with pytest.raises(ValueError, match="historique"):
        pont.indexation([("historique", 2020, 2023)])


#: Les jeux de paramètres de la confrontation : chaque réglage que
#: l'indexation et la revalorisation servie lisent — la règle, son lissage,
#: son plancher, le préfinancement, la règle du stock et la bascule, le
#: scénario de projection, la trajectoire de l'emploi —, et le simulateur de
#: la page Coût.
JEUX_DE_L_INDEXATION = (
    {},
    *({"mode_indexation": mode} for mode in (
        "triple_lock_inverse", "triple_lock_inverse_nominal", "mediane_trois_taux",
        "moyenne_trois_taux", "pib_nominal", "revalorisation_portee_au_compte", "prix",
        "salaires")),
    {"lissage_indexation": 3}, {"lissage_indexation": 5},
    {"mode_indexation": "triple_lock_inverse", "lissage_indexation": 5},
    {"mode_indexation": "triple_lock_inverse", "plancher_indexation": 0.0},
    {"mode_indexation": "prix", "plancher_indexation": 0.02, "lissage_indexation": 3},
    {"taux_anticipe_conversion": 0.016},
    {"revalorisation_stock": "reindexe"}, {"annee_bascule": 2035},
    {"revalorisation_stock": "reindexe", "annee_bascule": 2019},
    {"scenario_projection": "cor_productivite_basse"},
    {"scenario_projection": "cor_productivite_haute"}, {"trajectoire_emploi": "constant"},
    SOUS_LE_COR,
    {**SOUS_LE_COR, "revalorisation_stock": "reindexe", "taux_anticipe_conversion": 0.016},
    {**SOUS_LE_COR, "scenario_projection": "cor_productivite_basse"},
)


def test_l_indexation_du_portage_est_celle_du_jumeau_au_bit():
    """La confrontation qui tient lieu de relecture de l'indexation (note de
    décision 0007) : le taux de chaque année de 1941 à 2070 — le taux, le
    terme retenu, les trois séries, la fiabilité —, et le rendement cumulé
    d'une grille de cotisations, les mêmes au bit dans les deux exemplaires,
    sous chaque jeu de :data:`JEUX_DE_L_INDEXATION`. Elle ne dit pas que la
    règle est juste — :func:`test_le_pont_rend_les_taux_de_l_indexation` et
    ``tests/test_moteur.py`` le disent —, mais que le jumeau Python, que le
    moteur d'une carrière lit jusqu'à son retrait, fait le même calcul."""
    _sans_node()
    annees = range(1941, 2071)
    paires = [(depart, arrivee) for depart in range(1938, 2074, 4)
              for arrivee in range(1940, 2076, 5)]
    appels = [*(("taux", annee) for annee in annees),
              *(("coefficient", *paire) for paire in paires)]
    compares = 0
    for jeu in JEUX_DE_L_INDEXATION:
        parametres = _regles(**jeu)
        jumeau = Simulateur(parametres).indexation
        lus = pont.indexation(appels, parametres)
        attendus = [*(jumeau.taux(annee) for annee in annees),
                    *(jumeau.coefficient(*paire) for paire in paires)]
        ecarts = [(appel, repr(lu), repr(attendu))
                  for appel, lu, attendu in zip(appels, lus, attendus, strict=True)
                  if lu != attendu or type(lu) is not type(attendu)]
        assert ecarts == [], f"sous {jeu} : {ecarts[:3]}"
        compares += len(appels)
    assert compares == len(JEUX_DE_L_INDEXATION) * (130 + len(paires))


def test_les_lectures_python_de_la_revalorisation_servie_sont_celles_du_portage():
    """La confrontation qui tient lieu de relecture de la revalorisation
    servie (note de décision 0007). Avant que la classe Python cesse de
    calculer, elle a tenu au bit, sous chaque jeu de
    :data:`JEUX_DE_L_INDEXATION`, l'index du compte et la valeur de service
    que le pont rend contre ceux que le jumeau bâtissait, de 1941 à 2070 ;
    le calcul parti, elle tient ce qui reste des deux côtés : les quatre
    lectures que la classe Python garde — le coefficient, la règle du stock
    à la bascule, la valeur de service, le régime convenu —, sur les séries
    qu'elle a relues, contre celles du portage lui-même, demandées par le
    pont sur une grille de liquidations et d'années qui déborde la série des
    deux côtés, et sur chaque régime du catalogue."""
    _sans_node()
    from retraite_notionnelle.revalorisation import RevalorisationServie

    grille = [(liquidation, annee) for liquidation in range(1935, 2076, 7)
              for annee in range(1938, 2079, 5)]
    compares = 0
    for jeu in JEUX_DE_L_INDEXATION:
        parametres = _regles(**jeu)
        simulateur = Simulateur(parametres)
        lectrice = RevalorisationServie(simulateur, 1941, 2070)
        codes = [*simulateur.scenario_actuel.catalogue.codes, "regime_inconnu"]
        regimes = [*lectrice._points, "regime_general"]
        appels = [
            *(("coefficient", *case) for case in grille),
            *(("coefficient_stock", *case, prospectif)
              for case in grille for prospectif in (True, False)),
            *(("coefficient_points", regime, *case) for regime in regimes for case in grille),
            *(("regime_convenu", code) for code in codes)]
        lus = pont.revalorisation_servie(appels, parametres, 1941, 2070)
        attendus = [getattr(lectrice, methode)(*arguments) for methode, *arguments in appels]
        ecarts = [(appel, repr(lu), repr(attendu))
                  for appel, lu, attendu in zip(appels, lus, attendus, strict=True)
                  if lu != attendu or type(lu) is not type(attendu)]
        assert ecarts == [], f"sous {jeu} : {ecarts[:3]}"
        compares += len(appels)
    # La valeur de service n'est convenue que sous les conventions du COR :
    # trois jeux l'éprouvent.
    assert compares > 60000


def test_la_classe_python_lit_les_series_du_portage_sans_repli(monkeypatch):
    """``RevalorisationServie`` ne calcule plus en Python (note de décision
    0007) : elle demande ses séries au pont, une fois, sous les paramètres de
    son simulateur, et ses lectures ne sont plus que des rapports de deux
    valeurs. Sans node, elle s'arrête, sans repli. Les séries sont posées à
    la main : un index de 1, 2 et 3 de 2020 à 2022, une valeur de service de
    1, un demi et un quart.

    Le coefficient est le rapport de l'index à ses deux dates, un tant que la
    pension n'est pas servie, et l'index se lit à ses bornes au-delà. La
    bascule en 2021, le stock aux prix : la pension de 2020 ne reçoit rien
    d'une réforme prospective, et garde d'une rétroactive ce qu'elle valait à
    la bascule, 2."""
    _sans_node()
    from retraite_notionnelle.moteur.indexation import Indexation
    from retraite_notionnelle.revalorisation import RevalorisationServie

    simulateur = Simulateur(Parametres(annee_bascule=2021, **SOUS_LE_COR))
    with monkeypatch.context() as sans_node:
        sans_node.setattr(pont.shutil, "which", lambda nom: None)
        with pytest.raises(pont.PontIndisponible, match="node"):
            RevalorisationServie(simulateur, 2020, 2022)

    demandes = []

    def series(parametres, premiere_annee, derniere_annee):
        demandes.append((parametres, premiere_annee, derniere_annee))
        return pont.SeriesServies(
            premiere_annee=2020, derniere_annee=2022, index={2020: 1.0, 2021: 2.0, 2022: 3.0},
            points={"agirc_arrco": {2020: 1.0, 2021: 0.5, 2022: 0.25}},
            convenus={"arrco": "agirc_arrco", "agirc_arrco": "agirc_arrco",
                      "regime_general": None})

    def calcule(self, annee):
        raise AssertionError("la classe Python ne calcule plus l'index du compte")

    monkeypatch.setattr(pont, "series_servies", series)
    monkeypatch.setattr(Indexation, "taux", calcule)
    servie = RevalorisationServie(simulateur, 2020, 2022)
    assert demandes == [(simulateur.parametres, 2020, 2022)]
    assert (servie.premiere_annee, servie.derniere_annee) == (2020, 2022)
    assert [servie.coefficient(2020, 2022), servie.coefficient(2021, 2022),
            servie.coefficient(2022, 2021), servie.coefficient(2010, 2030)] == [
                3.0, 1.5, 1.0, 3.0]
    assert [servie.coefficient_points("agirc_arrco", 2020, 2022),
            servie.coefficient_points("agirc_arrco", 2021, 2022),
            servie.coefficient_points("regime_general", 2020, 2022)] == [0.25, 0.5, 1.0]
    assert [servie.regime_convenu("arrco"), servie.regime_convenu("regime_general"),
            servie.regime_convenu("regime_inconnu")] == ["agirc_arrco", None, None]
    assert [servie.coefficient_stock(2020, 2022, True),
            servie.coefficient_stock(2020, 2022, False),
            servie.coefficient_stock(2021, 2022, True)] == [1.0, 2.0, 1.5]
    assert demandes == [(simulateur.parametres, 2020, 2022)]


def test_le_cout_demande_au_portage_le_rendement_des_cotisations(monkeypatch):
    """Sous une variante démographique, le coût porte le compte de la
    proposition à la masse salariale de la variante, cotisation par
    cotisation, chacune pesant ce que l'indexation lui a rendu jusqu'à la
    liquidation (``cout._sous_la_demographie``). Ce rendement, il le demande
    au portage, d'un seul lot pour toute sa grille, chaque couple (année de
    la cotisation, année de la liquidation) une fois (note de décision 0007).

    Valeurs posées à la main, sous la masse salariale, +7,838 % en 2022 et
    +5,625 % en 2023 (``data/reference/macro/masse_salariale.csv``) : une
    cotisation de 2021 liquidée en 2023 a reçu les deux taux, celle de 2022
    le second seul ; celle de 2024, versée après le départ, ne se demande
    pas. Sans node, le coût s'arrête, sans repli sur l'indexation du Python."""
    _sans_node()
    from retraite_notionnelle import cout

    volet = cout.VoletLiberal(annee_liquidation=2023, annee_ouverture_garantie=2023,
                              pension=1.0, ressources_garantie=1.0,
                              cotisations={2021: 100.0, 2022: 100.0, 2024: 50.0, 2020: 0.0})
    pensionne = cout.Pensionne(code="x", generation=1960, annee_liquidation=2023,
                               pensions={cle: 1.0 for cle in cout.CLES_CAS_TYPES},
                               propre=volet)
    simulateur = Simulateur(Parametres())
    demandes = []
    demander = pont._demander

    def espion(demande, paquet):
        demandes.append(demande)
        return demander(demande, paquet)

    monkeypatch.setattr(pont, "_demander", espion)
    rendements = cout._rendements_des_cotisations(simulateur, [pensionne, pensionne])
    assert rendements == {(2021, 2023): (1 + 0.07838) * (1 + 0.05625),
                          (2022, 2023): 1 + 0.05625}
    assert [list(demande) for demande in demandes] == [["indexation"]]
    assert len(demandes[0]["indexation"]["appels"]) == 2
    # Le compte gagne la moyenne de f(L) / f(a), pondérée par ces rendements.
    lourd, leger = rendements[2021, 2023] * 100.0, rendements[2022, 2023] * 100.0
    capitaux = cout._capitaux_sous_la_variante(
        pensionne, lambda annee: 1.0 if annee < 2022 else 1.1,
        lambda annee, liquidation: rendements[annee, liquidation])
    assert capitaux[2] == pytest.approx((lourd * 1.1 + leger) / (lourd + leger), rel=1e-12)
    monkeypatch.setattr(pont.shutil, "which", lambda nom: None)
    with pytest.raises(pont.PontIndisponible, match="node"):
        cout._rendements_des_cotisations(simulateur, [pensionne])
