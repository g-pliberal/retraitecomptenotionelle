"""La façade des tests : les entrées du moteur Python que les tests appellent,
servies par le portage sous leurs noms (action 161, note de décision 0007).

``tests/facade.py`` en est le client, ``pont.facade`` la demande, et
``pont.lu_strictement`` la lecture : ce que le portage rend revient sous les
types du Python, champ par champ, et rien ne s'y devine. Les valeurs attendues
ici sont celles de la source — le texte, que les tests du moteur citaient
déjà —, ou posées à la main ; ce que la façade rend ne s'y compare pas à ce
que le portage rend par une autre voie. La confrontation au jumeau Python,
tant qu'il vit, est à part (``tests/test_facade_jumeau.py``).
"""

from __future__ import annotations

import dataclasses
import inspect
import math
import re
from types import SimpleNamespace

import pytest

from retraite_notionnelle import carriere as carriere_python
from retraite_notionnelle import memoire, pont
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle import simulateur as simulateur_python
from retraite_notionnelle.carriere import LigneRelevee, Metier
from retraite_notionnelle.config import (RACINE_PROJET, ContributionEtat, Neutralisations,
                                         Parametres)
from retraite_notionnelle.donnees.chargement import DonneeInsuffisante, Fiabilite
from retraite_notionnelle.droit import commun as commun_python
from retraite_notionnelle.droit import completer as completer_python
from retraite_notionnelle.droit import foyer as foyer_python
from retraite_notionnelle.droit import liquidation as liquidation_python
from retraite_notionnelle.droit import liquider as liquider_python
from retraite_notionnelle.droit import ouvrir as ouvrir_python
from retraite_notionnelle.droit import reversion as reversion_python
from retraite_notionnelle import revalorisation as revalorisation_python
from retraite_notionnelle.droit.commun import PensionRegime
from retraite_notionnelle.droit.liquider import EligibleAgricole, EligibleMinimum
from retraite_notionnelle.journal import Journal
from retraite_notionnelle.remuneration import AnneeComparee, FicheDePaie, RemunerationActif
from retraite_notionnelle.scenarios.actuel import ResultatActuel
from retraite_notionnelle.scenarios.notionnel import ResultatNotionnel
from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Comparaison

import facade
from facade import (Carriere, NonTransmissible, Simulateur, commun, completer, foyer, liquider,
                    ouvrir, regles_de_la_reversion, reversion)
from facade import entrees_du_test  # noqa: F401 — la fixture d'un fichier basculé

HAUTE = Fiabilite.CERTIFIEE


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


# -- la lecture stricte ------------------------------------------------------------

#: Une pension de régime telle que le portage l'écrit quand rien d'autre ne
#: s'y applique : ses cinq champs, 1 200,0 écrit « 1200 » par node.
PENSION = {"regime": "regime_general", "montant": 1200, "type_calcul": "annuites",
           "detail": "50 % × 2 400", "fiabilite": HAUTE.value}


def test_un_champ_sans_objet_que_le_portage_n_ecrit_pas_prend_sa_valeur_par_defaut():
    """Le portage n'écrit pas la date d'effet d'une pension qui part avec les
    autres, ni son capital quand elle est une rente : le Python les tient à
    leur défaut. Et node écrit « 1200 » un flottant entier, qui revient
    flottant."""
    lue = pont.lu_strictement(PensionRegime, PENSION)
    assert lue == PensionRegime("regime_general", 1200.0, "annuites", "50 % × 2 400", HAUTE)
    assert type(lue.montant) is float
    assert lue.fiabilite is HAUTE
    assert lue.date_effet is None and lue.conjoint == () and lue.coefficient_du_maximum == 1.0


def test_la_lecture_refuse_un_champ_que_le_type_ne_porte_pas():
    with pytest.raises(ValueError, match="PensionRegime.*montant_brut"):
        pont.lu_strictement(PensionRegime, {**PENSION, "montant_brut": 1300})


def test_la_lecture_refuse_un_champ_qui_manque():
    """``detail`` s'applique toujours : sans lui, la lecture s'arrête."""
    sans_detail = {nom: valeur for nom, valeur in PENSION.items() if nom != "detail"}
    with pytest.raises(ValueError, match="PensionRegime.*detail"):
        pont.lu_strictement(PensionRegime, sans_detail)


@pytest.mark.parametrize("champ, valeur, motif", [
    ("regime", 12, "texte attendu"),
    ("montant", "1200", "nombre attendu"),
    ("montant", True, "nombre attendu"),
    ("montant", None, "nombre attendu"),
    ("fiabilite", 99, "Fiabilite"),
    ("sur_la_duree_maximum", 1, "booléen attendu"),
    ("conjoint", [["majoration", 100.0, "trop"]], "2 éléments attendus"),
    ("conjoint", {"majoration": 100.0}, "suite attendue"),
])
def test_la_lecture_refuse_une_valeur_qui_n_a_pas_le_type_du_champ(champ, valeur, motif):
    with pytest.raises((TypeError, ValueError), match=motif):
        pont.lu_strictement(PensionRegime, {**PENSION, champ: valeur})


def test_un_entier_doit_en_etre_un_et_un_nombre_non_fini_passe_par_son_nom():
    """JSON n'écrit ni l'infini ni « pas un nombre » : le portage les écrit par
    leur nom, et un champ flottant les relit."""
    assert pont.lu_strictement(int, 172) == 172
    with pytest.raises(TypeError, match="entier attendu"):
        pont.lu_strictement(int, 172.5)
    with pytest.raises(TypeError, match="entier attendu"):
        pont.lu_strictement(int, True)
    assert pont.lu_strictement(float, "Infinity") == math.inf
    assert pont.lu_strictement(float, "-Infinity") == -math.inf
    assert math.isnan(pont.lu_strictement(float, "NaN"))
    assert pont.lu_strictement(float | None, None) is None
    assert pont.lu_strictement(dict[int, float], {"2024": 3}) == {2024: 3.0}


def test_une_valeur_que_le_python_calcule_et_que_le_portage_tient_ne_se_relit_pas():
    """Le portage tient en champ la pension mensuelle, que le Python calcule
    de la pension annuelle : la lecture la laisse à son type, qui la refait."""
    lu = pont.lu_strictement(ResultatActuel, {
        "pension_annuelle": 12000, "pension_mensuelle": 1000,
        "pensions_par_regime": [PENSION], "avantages_appliques": [], "total_contributif": 12000,
        "pension_hors_repartition": 0, "trimestres_valides": 172, "trimestres_etrangers": 0,
        "trimestres_requis": 172, "taux_liquidation": 0.5, "minimum_applique": False,
        "age_ouverture_opposable": 62.75, "liquidation_ouverte": True,
        "motif_ouverture": "age_legal", "fiabilite": HAUTE.value, "departs": [],
        "demandes": [], "retraite_progressive": None, "cumul": None,
        "droits_apres_depart": None, "petites_pensions": [], "chef_d_exploitation": None,
        "exploitant_agricole": None})
    assert lu.pension_mensuelle == 1000.0
    assert lu.minimum_ecrete is None  # sans objet : le portage ne l'écrit pas
    assert lu.pensions_par_regime == [pont.lu_strictement(PensionRegime, PENSION)]
    assert type(lu.pensions_par_regime) is list and type(lu.departs) is tuple


def test_une_classe_que_le_portage_ecrit_en_casse_de_chameau_se_relit_sous_ses_noms():
    lu = pont.lu_strictement(EligibleAgricole, {
        "indice": 3, "tauxPlein": True, "dureeRequiseAtteinte": False, "surcote": 0,
        "duree": 150, "chef": 120, "enfants": 8, "reference": 160,
        "collaborateurRegularise": 4, "conjointAvant1999": 0, "horsForfait": 2,
        "anneesHorsForfait": 1})
    assert lu == EligibleAgricole(indice=3, taux_plein=True, duree_requise_atteinte=False,
                                  surcote=0.0, duree=150, chef=120, enfants=8, reference=160,
                                  collaborateur_regularise=4, conjoint_avant_1999=0,
                                  hors_forfait=2, annees_hors_forfait=1)
    with pytest.raises(ValueError, match="EligibleAgricole.*taux_plein"):
        pont.lu_strictement(EligibleAgricole, {"taux_plein": True})


# -- les bâtisseurs de carrière ----------------------------------------------------

#: Un salarié né en 1965, entré à 23 ans, parti à 64 ans.
SALARIE = dict(annee_naissance=1965, sexe="H", affiliation="salarie_prive_non_cadre",
               age_debut=23, age_liquidation=64)


def test_la_carriere_simple_revient_sous_le_type_du_python(simulateur):
    """La carrière que le portage bâtit est une ``Carriere`` du Python : née en
    1965, entrée à 23 ans, en 1988, partie à 64 ans, en 2029, salariée chaque
    année."""
    carriere = simulateur.carriere_simple(**SALARIE)
    assert type(carriere) is carriere_python.Carriere
    assert (carriere.annee_naissance, carriere.sexe, carriere.age_liquidation) == (1965, "H", 64.0)
    assert carriere.premiere_annee == 1988
    assert carriere.annee_liquidation == 2029
    assert {ligne.affiliation for ligne in carriere.lignes} == {"salarie_prive_non_cadre"}
    assert type(carriere.lignes[0].revenu) is float


def test_les_arguments_passent_par_leur_rang_comme_par_leur_nom(simulateur):
    par_nom = simulateur.carriere_simple(**SALARIE, nombre_enfants=2)
    par_rang = simulateur.carriere_simple(1965, "H", "salarie_prive_non_cadre", 23, 64,
                                          nombre_enfants=2)
    assert pont.carriere_en_donnees(par_rang) == pont.carriere_en_donnees(par_nom)
    assert par_nom.nombre_enfants == 2


def test_la_carriere_d_un_seul_metier_est_celle_du_profil_et_celle_du_parcours(simulateur):
    """``carriere_simple`` est ``Carriere.depuis_profil`` sur les séries du
    simulateur, et le cas à un métier de ``carriere_parcours`` : les trois
    bâtisseurs, et ``Carriere.depuis_parcours``, rendent la même carrière."""
    simple = pont.carriere_en_donnees(simulateur.carriere_simple(**SALARIE))
    commun = dict(annee_naissance=1965, sexe="H", age_liquidation=64)
    metiers = [Metier("salarie_prive_non_cadre", 23)]
    assert pont.carriere_en_donnees(
        Carriere.depuis_profil(**SALARIE, macro=simulateur.macro)) == simple
    assert pont.carriere_en_donnees(
        simulateur.carriere_parcours(metiers=metiers, **commun)) == simple
    assert pont.carriere_en_donnees(
        Carriere.depuis_parcours(metiers=metiers, macro=simulateur.macro, **commun)) == simple


def test_le_parcours_change_de_statut_a_l_age_dit(simulateur):
    """Salarié de 21 à 40 ans, artisan ensuite : né en janvier 1975, il change
    en 2015."""
    carriere = simulateur.carriere_parcours(
        annee_naissance=1975, sexe="H", age_liquidation=64,
        metiers=[Metier("salarie_prive_non_cadre", 21), Metier("artisan", 40)])
    statuts = {ligne.annee: ligne.affiliation for ligne in carriere.lignes}
    assert statuts[2014] == "salarie_prive_non_cadre"
    assert statuts[2016] == "artisan"


def test_la_carriere_du_releve_porte_les_revenus_de_ses_lignes(simulateur):
    releve = [LigneRelevee(1990, "salarie_prive_non_cadre", 15000.0),
              LigneRelevee(1991, "artisan", 18000.0, trimestres=3)]
    carriere = simulateur.carriere_releve(1965, "F", releve, 64)
    assert type(carriere) is carriere_python.Carriere
    lues = {ligne.annee: ligne for ligne in carriere.lignes}
    assert (lues[1990].affiliation, lues[1990].revenu) == ("salarie_prive_non_cadre", 15000.0)
    assert (lues[1991].affiliation, lues[1991].revenu, lues[1991].trimestres_valides) == (
        "artisan", 18000.0, 3)


@pytest.mark.parametrize("batisseur, signature_python", [
    ("depuisParcours", carriere_python.Carriere.depuis_parcours),
    ("depuisReleve", carriere_python.Carriere.depuis_releve),
])
def test_le_portage_connait_chaque_option_que_la_facade_lui_passe(batisseur, signature_python):
    """Le portage lit ses options par leur nom, et ignorerait sans rien dire
    celle qu'il ne connaît pas : chaque argument du bâtisseur Python a le
    sien dans le portage. ``depuis_profil`` passe par ``depuisParcours``."""
    source = (RACINE_PROJET / "moteur" / "js" / "carriere.js").read_text(encoding="utf-8")
    options = re.search(r"static %s\(\{(.*?)\}\) \{" % batisseur, source, re.DOTALL).group(1)
    connues = set(re.findall(r"^\s*([a-z_]+)(?: = [^\n]*)?,?$", options, re.MULTILINE))
    assert {"annee_naissance", "macro"} <= connues
    assert set(inspect.signature(signature_python).parameters) <= connues
    assert set(inspect.signature(carriere_python.Carriere.depuis_profil).parameters) <= (
        connues | {"affiliation", "age_debut", "niveau_salaire"}) or batisseur != "depuisParcours"


# -- le scénario 1 -----------------------------------------------------------------

def test_calculer_rend_le_resultat_entier_du_scenario_1(simulateur):
    """Un salarié né en 1965 n'a pas le droit de partir à 60 ans, sauf carrière
    longue : 62 ans et 9 mois depuis la suspension de la réforme (LFSS 2026).
    Entré à seize ans, il part à 60 ans. Ce que le pont ne rendait pas — l'âge
    d'ouverture opposable, le total contributif, la fiabilité — revient avec
    le reste, sous le type du Python."""
    tardif = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(**{**SALARIE, "age_liquidation": 60}))
    assert type(tardif) is ResultatActuel
    assert tardif.liquidation_ouverte is False
    assert tardif.motif_ouverture == "non_ouverte"
    assert tardif.age_ouverture_opposable == pytest.approx(62.75)
    assert type(tardif.trimestres_valides) is int
    assert type(tardif.fiabilite) is Fiabilite
    assert all(type(pension) is PensionRegime for pension in tardif.pensions_par_regime)
    assert tardif.total_contributif > 0.0

    precoce = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(**{**SALARIE, "age_debut": 16, "age_liquidation": 60}))
    assert precoce.liquidation_ouverte is True
    assert precoce.motif_ouverture == "carriere_longue"
    assert precoce.age_ouverture_opposable == pytest.approx(60.0)


def test_calculer_nomme_le_dispositif_de_chaque_avantage(simulateur):
    """Le libellé de l'avantage, que le pont ne rendait pas : la fonction
    publique ne sert pas une majoration de durée d'assurance, mais une
    bonification."""
    commun = dict(annee_naissance=1960, sexe="F", age_debut=30, age_liquidation=62,
                  nombre_enfants=3)

    def libelle(affiliation):
        resultat = simulateur.scenario_actuel.calculer(
            simulateur.carriere_simple(affiliation=affiliation, **commun))
        return next(avantage.libelle for avantage in resultat.avantages_appliques
                    if avantage.code == "majoration_duree_assurance")

    assert libelle("salarie_prive_non_cadre") == "Majoration de durée d'assurance"
    assert libelle("fonctionnaire_etat") == "Bonification pour enfants"


def test_les_drapeaux_de_calculer_passent_au_portage(simulateur):
    """Une carrière courte au SMIC, partie à 67 ans, relève du minimum
    contributif ; ``avantages_non_contributifs`` le commande, et sans eux le
    résultat n'en applique aucun."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=37, age_liquidation=67, niveau_salaire=0.4, profil_carriere="plat")
    assert simulateur.scenario_actuel.calculer(carriere).minimum_applique is True
    sans = simulateur.scenario_actuel.calculer(carriere, avantages_non_contributifs=False)
    assert sans.minimum_applique is False
    assert sans.avantages_appliques == []
    assert simulateur.scenario_actuel.calculer(carriere, False, False).minimum_applique is False
    with pytest.raises(TypeError):
        simulateur.scenario_actuel.calculer(carriere, sans_minimum=True)


# -- la comparaison ----------------------------------------------------------------

def test_simuler_rend_la_comparaison_entiere_sous_ses_types(simulateur):
    """Une carrière courte au SMIC, partie à 67 ans, relève du minimum
    contributif. La comparaison revient entière : la carrière, le scénario 1,
    les cinq scénarios de la proposition, les paramètres du simulateur, et les
    méthodes du type, qui lisent ce que le portage a écrit."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=37, age_liquidation=67, niveau_salaire=0.4, profil_carriere="plat")
    comparaison = simulateur.simuler(carriere)
    assert type(comparaison) is Comparaison
    assert type(comparaison.actuel) is ResultatActuel
    assert comparaison.actuel.minimum_applique is True
    for scenario, *_ in SCENARIOS_NOTIONNELS:
        assert type(getattr(comparaison, scenario)) is ResultatNotionnel, scenario
    assert comparaison.parametres == simulateur.parametres
    assert pont.carriere_en_donnees(comparaison.carriere) == pont.carriere_en_donnees(carriere)
    retroactif = comparaison.notionnel_retroactif
    assert type(retroactif.compte.annee_liquidation) is int
    assert retroactif.compte.annee_liquidation == 2032
    assert comparaison.variation("notionnel_retroactif") == (
        retroactif.pension_annuelle / comparaison.actuel.pension_annuelle - 1.0)
    # Partie après l'âge légal de la proposition, 65 ans, elle n'est pas reportée.
    assert comparaison.depart_reporte is False and comparaison.carriere_liberal is None


def test_le_depart_que_la_proposition_reporte_revient_avec_sa_carriere(simulateur):
    """Un départ à 64 ans, après la bascule : la proposition le reporte à son
    âge légal, 65 ans (``Parametres.age_legal_liberal``), et la comparaison
    porte la carrière prolongée."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(**SALARIE))
    assert simulateur.parametres.age_legal_liberal == 65.0
    assert comparaison.depart_reporte is True
    assert type(comparaison.carriere_liberal) is carriere_python.Carriere
    assert comparaison.carriere_liberal.age_liquidation == 65.0
    assert comparaison.carriere_liberal.annee_liquidation == 2030


def test_les_neutralisations_declarees_reviennent_avec_la_comparaison(simulateur):
    """Les neutralisations déclarent ce que les scénarios notionnels retirent,
    sans rien commander (``tests/test_simulateur.py``) : le portage sert les
    deux jeux de paramètres du même simulateur, et la comparaison porte ceux
    du simulateur de la façade."""
    sans = Simulateur(Parametres(neutralisations=Neutralisations(minimum_contributif=False)))
    reference = simulateur.simuler(simulateur.carriere_simple(**SALARIE))
    comparaison = sans.simuler(sans.carriere_simple(**SALARIE))
    assert comparaison.parametres == sans.parametres != simulateur.parametres
    assert comparaison.actuel.pension_annuelle == reference.actuel.pension_annuelle


def test_la_fiche_de_paie_d_un_actif_revient_sous_les_noms_du_python(simulateur):
    """Le portage écrit la rémunération en casse de chameau ; un salarié né en
    1990 cotise encore, et sa fiche se lit sous les champs du Python."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64))
    remuneration = comparaison.remuneration
    assert type(remuneration) is RemunerationActif
    assert remuneration.statut == "salarie_prive_non_cadre" and remuneration.cadre is False
    annee = remuneration.annees[0]
    assert type(annee) is AnneeComparee and type(annee.droit_en_vigueur) is FicheDePaie
    assert annee.annee == simulateur.parametres.annee_bascule
    assert annee.droit_en_vigueur.brut > annee.droit_en_vigueur.net > 0.0


def test_le_journal_de_la_comparaison_revient_entree_par_entree(simulateur):
    """Le scénario 1 passe par l'échéancier, qui inscrit le départ et sa
    liquidation, une seule : chaque entrée revient avec ce qui la date. Le
    contenu d'une liquidation, qui tient les tables du moteur, ne passe pas :
    le lire est refusé. Né le 15 janvier 1965, l'assuré a 64 ans le 15 janvier
    2029 : sa pension prend effet le premier jour du mois suivant."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(**SALARIE, jour_naissance=15))
    assert type(comparaison.journal) is Journal
    liquidations = [entree for entree in comparaison.journal if entree.sorte == "liquidation"]
    assert len(liquidations) == 1
    assert liquidations[0].debut == "2029-02-01" and liquidations[0].fin is None
    assert ("depart_assure", "evenement") in {(e.id, e.sorte) for e in comparaison.journal}
    assert comparaison.journal.entree("depart_assure").inscrite_le == "2029-02-01"
    with pytest.raises(NonTransmissible, match="liquidation"):
        liquidations[0].contenu.pensions


def test_la_reversion_du_deces_declare_revient_avec_la_comparaison(simulateur):
    """Le décès déclaré ouvre la réversion au conjoint : l'échéancier
    l'inscrit, et la comparaison la porte."""
    from retraite_notionnelle.droit.reversion import Reversion

    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1958, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=62, conjoint={"naissance": "1960", "sexe": "F"}, deces="2023-05"))
    assert type(comparaison.reversion) is Reversion
    assert {("deces_assure", "evenement"), ("reversion_conjoint", "evenement"),
            ("liquidation_reversion_conjoint", "reversion")} <= {
                (entree.id, entree.sorte) for entree in comparaison.journal}
    inscrite = comparaison.journal.entree("liquidation_reversion_conjoint").contenu
    assert type(inscrite) is Reversion and inscrite.deces == comparaison.reversion.deces


def test_une_donnee_insuffisante_reste_une_donnee_insuffisante():
    """Sous une fiabilité exigée « certifiée », une carrière qui se projette
    n'a pas ses séries : le portage le refuse, et le Python lève son type."""
    exigeant = Simulateur(Parametres(fiabilite_minimale="certifiee"))
    with pytest.raises(DonneeInsuffisante, match="fiabilité"):
        exigeant.simuler(exigeant.carriere_simple(**SALARIE))


# -- la réversion ------------------------------------------------------------------

@pytest.mark.parametrize("deces, attendu", [
    ("1982-10-15", ("regime_general", 0.50, 2500.0, "servie", "avant_1982", "1982-11-01")),
    ("1982-11-10", ("regime_general", 0.52, 2600.0, "servie", "taux_52", "1982-12-01")),
])
def test_la_reversion_revient_sous_le_type_du_python(simulateur, deces, attendu):
    """Décret n° 82-1035 : 52 % pour les réversions prenant effet à compter du
    1er décembre 1982, 50 % avant (``tests/test_reversion.py``)."""
    from retraite_notionnelle.droit.reversion import Reversion

    carriere = Carriere.depuis_profil(
        1920, "H", "salarie_prive_non_cadre", 21.0, 60.0, simulateur.macro,
        conjoint={"naissance": "1925", "sexe": "F"}, deces=deces)
    resultat = reversion(simulateur.scenario_actuel, [("regime_general", 5000.0, HAUTE)],
                         carriere, 1982)
    assert type(resultat) is Reversion
    ligne, = resultat.regimes
    assert (ligne.regime, ligne.taux, round(ligne.montant, 2), ligne.motif, ligne.version,
            ligne.date_effet) == attendu


def test_sans_conjoint_il_n_y_a_pas_de_reversion(simulateur):
    carriere = simulateur.carriere_simple(**SALARIE)
    assert reversion(simulateur.scenario_actuel, [("regime_general", 5000.0, HAUTE)],
                     carriere, 2030, deces_suppose="2030-06-01") is None


# -- les erreurs -------------------------------------------------------------------

def test_un_refus_du_portage_leve_l_erreur_que_le_python_leve(simulateur):
    """Une affiliation inconnue est une ``KeyError`` ; un parcours sans métier,
    une ``ValueError`` — le motif est celui du portage."""
    with pytest.raises(KeyError, match="affiliation inconnue : boulanger_lunaire"):
        simulateur.carriere_simple(1970, "H", "boulanger_lunaire", 20, 64)
    with pytest.raises(KeyError, match="affiliation inconnue"):
        simulateur.carriere_parcours(
            annee_naissance=1975, sexe="H", age_liquidation=64,
            metiers=[Metier("salarie_prive_non_cadre", 21), Metier("boulanger_lunaire", 40)])
    with pytest.raises(ValueError, match="au moins un métier"):
        simulateur.carriere_parcours(annee_naissance=1975, sexe="H", age_liquidation=64,
                                     metiers=[])


def test_une_entree_que_la_facade_ne_sert_pas_est_refusee_avant_node():
    with pytest.raises(ValueError, match="liquider.abattement_points"):
        pont.facade("liquider.abattement_points", 1.0)


# -- ce que le client ne sait pas transmettre ---------------------------------------

def test_une_serie_qui_n_est_pas_celle_d_un_simulateur_de_la_facade_est_refusee(simulateur):
    """Le portage calcule sur ses séries, celles des paramètres du simulateur :
    une série passée en argument, que le test aurait faite ou retouchée, ne
    lui parviendrait pas."""
    with pytest.raises(NonTransmissible, match="série"):
        Carriere.depuis_profil(**SALARIE, macro=SimpleNamespace(coefficient_prix=lambda *_: 1.0))
    with pytest.raises(NonTransmissible, match="série"):
        Carriere.depuis_parcours(1965, "H", [Metier("artisan", 23)], 64,
                                 simulateur_python.Simulateur().macro)


def test_les_series_d_un_simulateur_portent_ses_parametres():
    """Sous une autre année courante, les séries du simulateur bâtissent la
    carrière de ce simulateur-là : un départ à venir se projette depuis elle."""
    sous = Simulateur(Parametres(annee_courante=2030))
    carriere = Carriere.depuis_profil(**SALARIE, macro=sous.macro)
    attendue = sous.carriere_simple(**SALARIE)
    assert pont.carriere_en_donnees(carriere) == pont.carriere_en_donnees(attendue)


def test_un_moteur_qui_n_est_pas_celui_de_la_facade_est_refuse(simulateur):
    carriere = simulateur.carriere_simple(**SALARIE)
    pensions = [("regime_general", 5000.0, HAUTE)]
    with pytest.raises(NonTransmissible, match="moteur"):
        reversion(simulateur_python.Simulateur().scenario_actuel, pensions, carriere, 2030)
    with pytest.raises(NonTransmissible, match="moteur"):
        reversion(object(), pensions, carriere, 2030)


def test_le_moteur_de_la_facade_ne_se_modifie_pas(simulateur, monkeypatch):
    """Ce qu'un test poserait sur le moteur, le portage ne le verrait pas."""
    moteur = simulateur.scenario_actuel
    assert simulateur.scenario_actuel is moteur
    with pytest.raises(NonTransmissible, match="modifi"):
        moteur.minimum_contributif = None
    with pytest.raises(NonTransmissible, match="modifi"):
        monkeypatch.setattr(moteur, "calculer", lambda carriere: None)
    with pytest.raises(NonTransmissible, match="modifi"):
        simulateur.parametres = Parametres(annee_courante=2030)


def test_sous_un_modele_modifie_la_facade_refuse(simulateur):
    """``monkeypatch`` et ``memoire.modele_modifie`` disent qu'une fonction du
    modèle est remplacée en Python : le portage ne le verrait pas, et rendrait
    le calcul du modèle intact."""
    with memoire.modele_modifie():
        with pytest.raises(NonTransmissible, match="modèle modifié"):
            simulateur.carriere_simple(**SALARIE)
    assert simulateur.carriere_simple(**SALARIE).annee_naissance == 1965


def test_sous_monkeypatch_la_facade_refuse(simulateur, monkeypatch):
    with pytest.raises(NonTransmissible, match="modèle modifié"):
        simulateur.scenario_actuel.calculer(None)


def test_ce_que_la_facade_ne_sert_pas_ne_se_lit_pas_sur_son_simulateur(simulateur):
    """Les règles du simulateur Python — le compte, la conversion,
    l'indexation — ne sont pas des entrées de la façade : les lire échoue, au
    lieu de faire tourner le moteur Python. Ses données, elles, se lisent."""
    with pytest.raises(NonTransmissible, match="convertisseur"):
        simulateur.convertisseur
    with pytest.raises(NonTransmissible, match="fiches_datees"):
        simulateur.scenario_actuel.fiches_datees
    assert simulateur.macro.plafond_securite_sociale(2024) == 46368.0
    assert "artisan" in simulateur.affiliations
    assert simulateur.scenario_actuel.macro is simulateur.macro
    assert simulateur.parametres == Parametres()


# -- les tables du moteur ------------------------------------------------------------

def test_une_table_du_moteur_se_lit_par_son_nom_et_sa_methode(simulateur):
    """Les montants que D. 353-1 et D. 353-4 écrivent, et ce que la Cnav sert :
    le minimum de la réversion, 3 983,29 € en 2025, rien avant sa série ; le
    plafond de la majoration, 2 421,60 € par trimestre depuis avril 2010. Ce
    que la méthode rend revient sous le type que son jumeau annonce."""
    table = simulateur.scenario_actuel.reversions
    minimum = table.minimum(2025)
    assert type(minimum) is tuple and minimum[0] == 3983.29
    assert type(minimum[1]) is Fiabilite
    assert table.minimum(1940) is None
    assert table.plafond_majoration(annee=2010)[0] == 2421.60
    # La loi du 20 janvier 2014 : 166 trimestres pour les générations 1955 à 1957.
    requis, fiabilite = simulateur.scenario_actuel.durees_requises.trimestres(1955)
    assert (requis, type(requis), type(fiabilite)) == (166, int, Fiabilite)


def test_les_arguments_d_une_methode_se_lient_comme_le_python_les_lie(simulateur):
    table = simulateur.scenario_actuel.reversions
    with pytest.raises(TypeError, match="annee"):
        table.minimum(millesime=2025)
    with pytest.raises(TypeError):
        table.minimum(2025, 2026)


def test_une_table_se_lit_sous_les_parametres_de_son_simulateur(simulateur):
    """Les conventions du COR ne valent que pour la page Coût
    (``Parametres.conventions_cor``) : le simulateur individuel n'en tient
    aucune pour la valeur de service du point ; sous elles, celle de
    l'Agirc-Arrco suit la convention."""
    assert simulateur.scenario_actuel.valeurs_point.regimes_convenus("valeur_service") == ()
    convenu = Simulateur(Parametres(conventions_cor=True)).scenario_actuel
    assert "agirc_arrco" in convenu.valeurs_point.regimes_convenus("valeur_service")


def test_la_version_d_une_reversion_se_lit_par_la_fiche_de_son_regime(simulateur):
    """« Le montant maximum de la pension principale de réversion [...] est égal
    à 54 % du maximum » (circulaire Cnav n° 3/95, § 13) : la version de la
    réversion du régime général, que la fiche de son régime donne, porte ce
    taux en 2026 ; un régime sans fiche n'en a pas."""
    table = simulateur.scenario_actuel.reversions
    fiche = table.fiche_du_regime("regime_general")
    version = table.version(fiche, "2026-01-01", "2026-01-01")
    assert float(version["parametres"]["taux"]) == 0.54
    assert table.fiche_du_regime("regime_lunaire") is None


def test_une_methode_que_la_facade_ne_sert_pas_est_refusee(simulateur):
    """Une méthode servie se déclare (``pont.TABLES_DE_LA_FACADE``) : une
    autre, une méthode privée, une table que le moteur ne tient pas sont
    refusées, au lieu que le type de ce qu'elles rendent se devine."""
    table = simulateur.scenario_actuel.reversions
    with pytest.raises(NonTransmissible, match="reversions.fiche "):
        table.fiche("reversion")
    with pytest.raises(NonTransmissible, match="carriere_longue._portes"):
        simulateur.scenario_actuel.carriere_longue._portes
    with pytest.raises(NonTransmissible, match="table_lunaire"):
        simulateur.scenario_actuel.table_lunaire
    with pytest.raises(ValueError, match="reversions.fiche "):
        pont.table_du_moteur("reversions", "fiche", dict, "reversion")
    assert facade.TABLES is pont.TABLES_DE_LA_FACADE


def test_une_table_de_la_facade_ne_se_modifie_pas(simulateur, monkeypatch):
    table = simulateur.scenario_actuel.reversions
    with pytest.raises(NonTransmissible, match="modifi"):
        table.minimum = lambda annee: (0.0, HAUTE)
    with pytest.raises(NonTransmissible, match="modèle modifié"):
        table.minimum(2025)


def test_une_regle_du_moteur_python_ne_lit_pas_une_table_de_la_facade(simulateur):
    """Une règle du moteur Python à qui un test passe le moteur de la façade
    tournerait en Python sur les tables du portage : le test verdirait sans
    éprouver le portage. Elle est refusée ; le test reste sur le moteur
    Python, ou demande la règle au pont."""
    from retraite_notionnelle.droit import ouvrir

    carriere = simulateur.carriere_simple(**SALARIE)
    periode = simulateur.catalogue["regime_general"].periode(2029)
    with pytest.raises(NonTransmissible, match="règle du moteur Python"):
        ouvrir.duree_requise(simulateur.scenario_actuel, periode, carriere)


# -- les règles du droit --------------------------------------------------------------

NE_EN_1955 = dict(annee_naissance=1955, sexe="H", affiliation="salarie_prive_non_cadre",
                  age_debut=23, age_liquidation=62)


def test_une_regle_du_droit_se_demande_par_son_module_et_son_nom(simulateur):
    """Né en 1955, au régime général : 166 trimestres requis (loi du 20 janvier
    2014, article 2), l'ouverture à soixante-deux ans (L. 161-17-2, loi du
    9 novembre 2010) et le taux plein à soixante-sept (L. 351-8). À
    l'Agirc-Arrco, partir à cinquante-sept ans sans la durée abat la pension au
    coefficient 0,43 de l'accord, et rien au taux plein. Ce que la règle rend
    revient sous le type que son jumeau annonce."""
    moteur = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(**NE_EN_1955)
    periode = simulateur.catalogue["regime_general"].periode(2017)
    requis, fiabilite = ouvrir.duree_requise(moteur, periode, carriere)
    assert (requis, type(requis), type(fiabilite)) == (166, int, Fiabilite)
    ouverture = ouvrir.age_ouverture(moteur, periode, carriere)
    assert (ouverture, type(ouverture)) == (62.0, float)
    assert ouvrir.age_taux_plein(moteur, periode, carriere) == 67.0

    parti_tot = simulateur.carriere_simple(**{**SALARIE, "age_debut": 25, "age_liquidation": 57})
    complementaire = simulateur.catalogue["agirc_arrco"].periode(2019)
    assert liquider.abattement_points(
        moteur, complementaire, parti_tot, 100, 172, 57.0, 2022) == pytest.approx(0.43)
    assert liquider.abattement_points(
        moteur, complementaire, parti_tot, 172, 172, 57.0, 2022) == 1.0


def test_les_arguments_d_une_regle_se_lient_comme_le_python_les_lie(simulateur):
    """Par leur rang comme par leur nom, les valeurs par défaut du jumeau
    comprises ; un argument inconnu ou en trop est une ``TypeError``, avant
    node."""
    moteur = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(**NE_EN_1955)
    periode = simulateur.catalogue["regime_general"].periode(2017)
    assert ouvrir.age_ouverture(moteur, carriere=carriere, periode=periode,
                                parents_compris=False) == 62.0
    with pytest.raises(TypeError, match="generation"):
        ouvrir.age_ouverture(moteur, periode, carriere, generation=1955)
    with pytest.raises(TypeError):
        ouvrir.age_taux_plein(moteur, periode, carriere, 2017)


def test_une_regle_sans_moteur_se_demande_de_meme():
    """R. 173-4-3, l'exemple de la circulaire Cnav n° 2004/29 : 21 années, 126
    trimestres sur 174, « 21 x 126 / 174 = 15,2 arrondi à 15 »."""
    retenues = liquider.annees_au_prorata(21, 126, 174)
    assert (retenues, type(retenues)) == (15, int)
    assert liquider.annees_au_prorata(total=20, duree=28, somme=135) == 4


def test_une_date_passe_a_la_regle_au_mois_pres(simulateur):
    """L'Agirc-Arrco revalorise au 1er novembre : le point vaut 1,3498 € en
    octobre 2023 et 1,4159 € en novembre ; une année se lit au 31 décembre."""
    moteur = simulateur.scenario_actuel
    assert liquider.valeur_du_point(moteur, "agirc_arrco", DateMois(2023, 10)) == (1.3498, HAUTE)
    assert liquider.valeur_du_point(moteur, "agirc_arrco", DateMois(2023, 11)) == (1.4159, HAUTE)
    assert liquider.valeur_du_point(moteur, "agirc_arrco", 2023) == (1.4159, HAUTE)
    assert liquider.valeur_du_point(moteur, "regime_general", 2023) is None


def test_une_regle_que_la_facade_ne_sert_pas_est_refusee(simulateur):
    """Une règle servie se déclare (``pont.REGLES_DE_LA_FACADE``) : une autre,
    une règle privée, une classe du module sont refusées, au lieu que le type
    de ce qu'elles rendent se devine. Ce que le jumeau ne porte pas manque,
    comme à un module."""
    with pytest.raises(NonTransmissible, match="liquider.liquider_chaque_regime"):
        liquider.liquider_chaque_regime
    with pytest.raises(NonTransmissible, match="liquider._coefficient_anticipation"):
        liquider._coefficient_anticipation
    with pytest.raises(NonTransmissible, match="liquider.EligibleMinimum"):
        liquider.EligibleMinimum
    with pytest.raises(AttributeError, match="ouvrir.regle_lunaire"):
        ouvrir.regle_lunaire
    with pytest.raises(ValueError, match="ouvrir.ouvrir"):
        pont.regle_du_droit("ouvrir", "ouvrir", float)
    assert facade.REGLES is pont.REGLES_DE_LA_FACADE
    assert set(facade.REGLES) == {"commun", "completer", "foyer", "liquider", "ouvrir",
                                  "reversion", "revalorisation"}


def test_une_regle_ne_recoit_que_ce_que_la_facade_sait_transmettre(simulateur):
    """Le moteur d'un simulateur de la façade, une période de son catalogue,
    une carrière, une date, des valeurs simples. Le moteur Python, une période
    que le test a retouchée, un objet du moteur — les durées d'un relevé —
    n'arriveraient pas au portage : la règle est refusée."""
    moteur = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(**NE_EN_1955)
    periode = simulateur.catalogue["regime_general"].periode(2017)
    with pytest.raises(NonTransmissible, match="moteur"):
        ouvrir.duree_requise(simulateur_python.Simulateur().scenario_actuel, periode, carriere)
    with pytest.raises(NonTransmissible, match="moteur"):
        ouvrir.duree_requise(None, periode, carriere)
    retouchee = dataclasses.replace(periode, age_taux_plein=65.0)
    with pytest.raises(NonTransmissible, match="catalogue"):
        ouvrir.age_taux_plein(moteur, retouchee, carriere)
    with pytest.raises(NonTransmissible, match="durees"):
        liquider.abattement_points(moteur, periode, carriere, 100, 166, 62.0, 2017,
                                   durees=SimpleNamespace(tous_regimes=100))
    with pytest.raises(NonTransmissible, match="duree .PeriodeRegime."):
        liquider.annees_au_prorata(21, periode, 174)


#: Un régime porteur du minimum : 140 trimestres, dont 40 cotisés, sur 152.
ELIGIBLE = EligibleMinimum(
    indice=0, prorata_assurance=140 / 152, prorata_cotise=40 / 152, taux_plein=True,
    duree_regime=140, cotisee_regime=40, proratisation=152, requis=160,
    duree_tous_regimes=140, cotisee_tous_regimes=40, porte_avpf=True,
    bornee_avec=("cancava_avant_1973",))


def test_une_regle_recoit_un_eligible_au_minimum_et_la_regle_de_sa_fiche(simulateur):
    """Un éligible au minimum passe au portage sous les noms qu'il y porte, et
    en revient sous son type ; la règle de la fiche, un dictionnaire de valeurs
    simples, passe telle quelle. De janvier 2004 à juin 2005, la durée cotisée
    vaut la durée d'assurance (lettre ministérielle du 25 mars 2004)."""
    sans_distinction = completer.selon_la_regle(ELIGIBLE, {"majoration": "sans_distinction"}, 0)
    assert type(sans_distinction) is EligibleMinimum
    assert sans_distinction == dataclasses.replace(
        ELIGIBLE, cotisee_regime=140, prorata_cotise=140 / 152, cotisee_tous_regimes=140)
    assert completer.plancher_du_regime(sans_distinction, 6511.06, 6706.39, True, True) == (
        pytest.approx(6706.39 * 140 / 152))
    seuil = {"majoration": "periodes_cotisees", "seuil_trimestres_cotises": 120}
    assert completer.majoration_ouverte(seuil, 120) is True
    assert completer.majoration_ouverte(seuil, 118) is False


def test_une_regle_ne_recoit_qu_un_dictionnaire_de_valeurs_simples(simulateur):
    """Un dictionnaire dont une valeur n'est pas simple, ou dont une clé n'est
    pas un texte, n'arriverait pas au portage sous son type : refusé."""
    with pytest.raises(NonTransmissible, match="regle"):
        completer.majoration_ouverte({"majoration": object()}, 120)
    with pytest.raises(NonTransmissible, match="regle"):
        completer.majoration_ouverte({2004: "sans_distinction"}, 120)


def test_le_releve_revient_avec_ses_durees_et_ses_points(simulateur):
    """Le relevé d'un salarié né en janvier 1955, entré à vingt-trois ans,
    parti à soixante-deux, le 1er février 2017 : quatre trimestres par année
    de 1978 à 2016 (R. 351-9), 156 au régime général, et aucun en 2017, dont
    la durée s'arrête au dernier trimestre civil qui précède l'effet
    (R. 351-1). La durée du régime aligné que R. 173-4-3 compare est la même.
    Ce que le relevé rend passe le pont en données ; ses durées repassent au
    portage par la carrière dont il vient."""
    carriere = simulateur.carriere_simple(**NE_EN_1955)
    releve = facade.releve.construire(simulateur.scenario_actuel, carriere)
    durees = releve.durees
    assert durees.par_annee["assurance"]["regime_general"][1978] == 4
    assert 2017 not in durees.par_annee["assurance"]["regime_general"]
    assert (durees.plafond("assurance", 2016), durees.plafond("assurance", 2017)) == (4, 0)
    assert durees.trimestres_par_regime["regime_general"] == 156
    assert durees.trimestres == 156
    aligne = liquider.duree_du_regime_aligne(carriere, durees, ("regime_general",))
    assert (aligne, type(aligne)) == (156, int)
    # Le non-cadre acquiert ses points à l'Arrco, avant la fusion de 2019.
    assert "arrco" in {code for code, annee, *_ in releve.droits.points if annee == 2016}


def test_le_releve_ne_sert_que_ce_qu_il_transmet(simulateur):
    """Un plafond de régimes nommés, des durées passées avec une autre
    carrière, ou celles d'un relevé construit sous un drapeau, que le portage
    refait du relevé de la carrière sous ses drapeaux par défaut,
    n'arriveraient pas au portage : refusés."""
    carriere = simulateur.carriere_simple(**NE_EN_1955)
    sans = facade.releve.construire(simulateur.scenario_actuel, carriere, points_gratuits=False)
    with pytest.raises(NonTransmissible, match="drapeaux"):
        liquider.duree_du_regime_aligne(carriere, sans.durees, ("regime_general",))
    with pytest.raises(NonTransmissible, match="moteur"):
        facade.releve.construire(simulateur_python.Simulateur().scenario_actuel, carriere)
    durees = facade.releve.construire(simulateur.scenario_actuel, carriere).durees
    with pytest.raises(NonTransmissible, match="membres"):
        durees.plafond("assurance", 2016, ("regime_general",))
    autre = simulateur.carriere_simple(**SALARIE)
    with pytest.raises(NonTransmissible, match="carrière"):
        liquider.duree_du_regime_aligne(autre, durees, ("regime_general",))
    with pytest.raises(NonTransmissible, match="modifi"):
        durees.trimestres = 0


# -- le relevé entier et ses étapes ------------------------------------------------------

#: Un artisan devenu salarié, né en 1960, parti à soixante-quatre ans, en 2024 :
#: la liquidation unique réunit ses régimes alignés (L. 173-1-2).
ARTISAN_PUIS_SALARIE = dict(annee_naissance=1960, sexe="H", age_liquidation=64,
                            metiers=[Metier("artisan", 20.0),
                                     Metier("salarie_prive_non_cadre", 40.0)])


def test_le_releve_rend_ses_lignes_ses_groupes_et_ses_etapes(simulateur):
    """Le relevé de l'artisan devenu salarié revient avec ses lignes (contrat
    C.5), le groupe de la liquidation unique, le liquidateur en tête, et ce
    que chaque étape a écrit : la coordination, une ligne de régimes par
    ligne de carrière ; les durées et les droits, en données, sous leur
    schéma ; les points acquis de chaque régime."""
    carriere = simulateur.carriere_parcours(**ARTISAN_PUIS_SALARIE)
    releve = facade.releve.construire(simulateur.scenario_actuel, carriere)
    donnees = releve.donnees()
    assert donnees["lignes"] == releve.lignes() and donnees["lignes"]
    assert releve.groupes and all(type(membres) is tuple and len(membres) >= 2
                                  for membres in releve.groupes.values())
    assert [g["regimes"] for g in donnees["groupes"]] == [
        list(membres) for membres in dict.fromkeys(releve.groupes.values())]
    coordination = releve.coordination
    assert len(coordination.regimes) == len(coordination.carriere.lignes)
    assert all(type(regimes) is tuple for regimes in coordination.regimes)
    assert coordination.donnees()["lignes"][0]["affiliation"] == "artisan"
    assert releve.durees.donnees()["trimestres"] == releve.durees.trimestres
    assert {point["regime"] for point in releve.droits.donnees()["points"]} == set(
        releve.droits.points_acquis)
    assert releve.durees.hors_annee["assurance"] == {}
    assert releve.durees.enfants is None


def test_le_releve_sert_ses_drapeaux(simulateur):
    """Les trois drapeaux de ``construire`` passent au portage : sans la
    liquidation unique, aucun groupe ; sans points gratuits, le chef
    d'exploitation installé en 1975 n'en a pas ; sans avantages non
    contributifs, la mère de trois enfants n'a pas ses vingt-quatre
    trimestres."""
    actuel = simulateur.scenario_actuel
    artisan = simulateur.carriere_parcours(**ARTISAN_PUIS_SALARIE)
    assert facade.releve.construire(actuel, artisan, liquider_successions=False).groupes == {}
    chef = simulateur.carriere_parcours(annee_naissance=1955, sexe="H", age_liquidation=64,
                                        metiers=[Metier("exploitant_agricole", 20.0)])
    assert facade.releve.construire(actuel, chef).droits.gratuits
    assert facade.releve.construire(actuel, chef, points_gratuits=False).droits.gratuits == {}
    mere = simulateur.carriere_parcours(annee_naissance=1970, sexe="F", age_liquidation=64,
                                        nombre_enfants=3,
                                        metiers=[Metier("salarie_prive_non_cadre", 22.0)])
    avec = facade.releve.construire(actuel, mere)
    sans = facade.releve.construire(actuel, mere, avantages_non_contributifs=False)
    assert (avec.durees.enfants.trimestres, avec.durees.enfants.regimes,
            avec.durees.enfants.dispositifs) == (24, ["regime_general"], ["mda"])
    assert sans.durees.enfants is None
    assert sans.durees.trimestres == avec.durees.trimestres - 24


def test_chaque_etape_se_sert_seule(simulateur):
    """``coordonner``, ``compter`` et ``acquerir``, servis par le portage, une
    étape après l'autre, rendent ce que le relevé rend ; une carrière que la
    coordination ne rétablit pas revient elle-même ; le cumul plafonné de
    plusieurs régimes se lit sur les durées."""
    actuel = simulateur.scenario_actuel
    carriere = simulateur.carriere_parcours(**ARTISAN_PUIS_SALARIE)
    coordination = facade.coordonner.coordonner(actuel, carriere)
    assert coordination.carriere is carriere and coordination.retablissements == ()
    durees = facade.compter.compter(actuel, coordination)
    droits = facade.acquerir.acquerir(actuel, coordination, durees)
    releve = facade.releve.construire(actuel, carriere)
    assert coordination.donnees() == releve.coordination.donnees()
    assert durees.donnees() == releve.durees.donnees()
    assert droits.donnees() == releve.droits.donnees()
    regimes = ("regime_general", "cancava")
    assert durees.cumul_plafonne("assurance", regimes) == sum(
        min(sum(durees.par_annee["assurance"].get(code, {}).get(annee, 0) for code in regimes),
            durees.plafond("assurance", annee))
        for annee in {annee for code in regimes
                      for annee in durees.par_annee["assurance"].get(code, {})})


def test_une_etape_ne_sert_que_ce_qu_elle_transmet(simulateur):
    """Une coordination, des durées qui ne viennent pas de la façade, ou des
    durées d'une autre coordination, un filtre d'années n'arriveraient pas au
    portage : refusés."""
    actuel = simulateur.scenario_actuel
    carriere = simulateur.carriere_parcours(**ARTISAN_PUIS_SALARIE)
    coordination = facade.coordonner.coordonner(actuel, carriere)
    with pytest.raises(NonTransmissible, match="coordination"):
        facade.compter.compter(actuel, object())
    autre = facade.coordonner.coordonner(actuel, simulateur.carriere_simple(**SALARIE))
    with pytest.raises(NonTransmissible, match="durées"):
        facade.acquerir.acquerir(actuel, coordination, facade.compter.compter(actuel, autre))
    durees = facade.compter.compter(actuel, coordination)
    with pytest.raises(NonTransmissible, match="annees"):
        durees.cumul_plafonne("assurance", ("regime_general",), lambda annee: annee > 2000)
    with pytest.raises(NonTransmissible, match="drapeaux"):
        liquider.duree_du_regime_aligne(carriere, durees, ("regime_general",))


# -- les cotisations du relevé et le constructeur du compte -----------------------------

#: Un chef d'exploitation né en 1925, de 1952 à 1972 à 100 € par an, sous le
#: plafond, parti à soixante-cinq ans, en 1990.
CHEF_DE_1952 = dict(annee_naissance=1925, mois_naissance=1, jour_naissance=15, sexe="H",
                    age_liquidation=65.0)


def _chef_de_1952():
    from retraite_notionnelle.carriere import AnneeCarriere

    return Carriere(**CHEF_DE_1952, lignes=[
        AnneeCarriere(annee=annee, revenu=100.0, affiliation="exploitant_agricole")
        for annee in range(1952, 1973)])


def test_le_releve_rend_ses_cotisations(simulateur):
    """« Pour l'exercice 1952, les cotisations professionnelles [...] sont
    égales à la moitié des cotisations annuelles » (décret n° 52-1166,
    article 45) : la cotisation de 1952 que le relevé revalorise, ramenée aux
    prix de son année, est la moitié des 8,5 % de 100 €, 4,25 € ; celle de
    1953, 8,50 €. Elles passent le pont en données, ``(code, annee, montant)``."""
    cotisations = facade.releve.construire(
        simulateur.scenario_actuel, _chef_de_1952()).droits.cotisations
    assert type(cotisations) is tuple
    code, annee, montant = cotisations[0]
    assert (type(code), type(annee), type(montant)) == (str, int, float)
    assert {annee: round(montant / simulateur.macro.coefficient_prix(annee, 1990), 2)
            for code, annee, montant in cotisations
            if code == "msa_non_salaries" and annee in (1952, 1953)} == {1952: 4.25, 1953: 8.50}


def test_le_constructeur_du_compte_rend_la_cotisation_d_une_annee(simulateur):
    """Le même chef : son compte reçoit pour 1952 la moitié de la cotisation
    annuelle, 4,25 €, sous le constructeur du scénario 2 comme sous celui des
    scénarios 4 et 5. Ce qu'il rend revient sous le type du Python."""
    from retraite_notionnelle.moteur.compte import CotisationAnnuelle

    for constructeur in (simulateur.constructeur, simulateur.constructeur_employeur):
        cotisation = constructeur.cotisation_annuelle(_chef_de_1952(), 1952)
        assert type(cotisation) is CotisationAnnuelle
        assert dict(cotisation.par_regime) == {"msa_non_salaries": 4.25}
        assert type(cotisation.fiabilite) is Fiabilite


def test_le_constructeur_du_compte_rend_le_taux_effectif_d_une_periode(simulateur):
    """44,1 % de la rémunération d'un agent civil de l'État en 2025 : la part du
    taux de l'État que la Cour des comptes rattache à sa retraite (tableau
    n° 15), que le compte des scénarios 4 et 5 reçoit par défaut. La période
    passe au portage par son rang dans le catalogue."""
    periode = next(iter(
        simulateur.catalogue["fonction_publique_etat"].periodes_actives(2025)))
    taux, employeur, origine, fiabilite = simulateur.constructeur_employeur.taux_effectif(
        "fonction_publique_etat", periode, 2025, militaire=False)
    assert (employeur, origine, fiabilite) == (pytest.approx(0.441), "retraite_seule",
                                               Fiabilite.HAUTE)
    assert type(taux) is float


def test_le_constructeur_du_compte_rend_un_compte_entier(simulateur):
    """Le compte du même chef, ouvert en 1952 et liquidé en 1990 : une
    cotisation par année, de 1952 à 1972, la première à 4,25 €, la moitié de la
    cotisation annuelle (décret n° 52-1166, article 45), la suivante à 8,50 €,
    les 8,5 % de 100 € ; un seul régime au capital. Il revient sous le type du
    Python, ses cotisations comprises."""
    from retraite_notionnelle.moteur.compte import CompteNotionnel, CotisationAnnuelle

    compte = simulateur.constructeur.construire(_chef_de_1952(), 1990, annee_debut=1952)
    assert type(compte) is CompteNotionnel
    assert all(type(cotisation) is CotisationAnnuelle for cotisation in compte.cotisations)
    assert [cotisation.annee for cotisation in compte.cotisations] == list(range(1952, 1973))
    assert [cotisation.cotisation for cotisation in compte.cotisations[:2]] == [4.25, 8.50]
    assert set(compte.capital_par_regime) == {"msa_non_salaries"}
    assert compte.capital == pytest.approx(compte.capital_par_regime["msa_non_salaries"])
    assert compte.annee_liquidation == 1990


def test_le_prelevement_porte_le_taux_entier_de_l_etat(simulateur):
    """Ce que le droit en vigueur prélève sur un civil de l'État en 2025 : le
    taux entier que l'État verse, 78,28 % (la série des taux appelés,
    ``contribution_employeur_public.csv``), quand son compte
    ne reçoit par défaut que 44,1 %. Sous le taux entier, le constructeur du
    prélèvement est celui des scénarios 4 et 5."""
    periode = next(iter(
        simulateur.catalogue["fonction_publique_etat"].periodes_actives(2025)))
    _, employeur, origine, _ = simulateur.constructeur_prelevement.taux_effectif(
        "fonction_publique_etat", periode, 2025, militaire=False)
    assert (employeur, origine) == (pytest.approx(0.7828), "appelee")
    entiere = facade.Simulateur(Parametres().avec(contribution_etat=ContributionEtat.ENTIERE))
    assert entiere.constructeur_prelevement is entiere.constructeur_employeur
    assert simulateur.constructeur_prelevement is not simulateur.constructeur_employeur
    assert simulateur.constructeur is simulateur.constructeur


def test_le_regime_unique_se_lit_sur_le_simulateur(simulateur):
    """Le régime unique d'après la bascule, que le portage fusionne de son
    catalogue : sous le type du Python, à l'année de bascule du modèle, sur
    une assiette déplafonnée (``fusion.py``, ``_taux_total``), la fonction
    publique de l'État parmi ce qu'il fusionne, et la part de l'assuré moindre
    que le taux entier. Le même à chaque lecture."""
    from retraite_notionnelle.moteur.fusion import RegimeFusionne

    fusionne = simulateur.regime_fusionne
    assert type(fusionne) is RegimeFusionne
    assert fusionne.annee_bascule == simulateur.parametres.annee_bascule == 2026
    assert fusionne.assiette == "deplafonnee"
    assert "fonction_publique_etat" in fusionne.regimes_fusionnes
    assert type(fusionne.regimes_fusionnes) is tuple
    assert type(fusionne.fiabilite) is Fiabilite
    assert 0 < fusionne.taux_cotisation_salarie < fusionne.taux_cotisation_retraite
    assert simulateur.regime_fusionne is fusionne


def test_le_compte_recoit_le_regime_unique_du_simulateur(simulateur):
    """Une fonctionnaire de l'État née en 1975, liquidée en 2039 : passé la
    bascule, son compte porte le taux entier du régime unique, plus la
    pension civile. Un autre régime unique — retouché par le test — ne
    parviendrait pas au portage : refusé."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64)
    fusionne = simulateur.regime_fusionne
    compte = simulateur.constructeur_employeur.construire(
        carriere, carriere.annee_liquidation, regime_fusionne=fusionne)
    par_annee = {cotisation.annee: cotisation for cotisation in compte.cotisations}
    assert par_annee[2030].taux_effectif == pytest.approx(fusionne.taux_cotisation_retraite)
    assert par_annee[2020].taux_effectif != pytest.approx(fusionne.taux_cotisation_retraite)
    with pytest.raises(NonTransmissible, match="régime unique"):
        simulateur.constructeur_employeur.construire(
            carriere, carriere.annee_liquidation,
            regime_fusionne=dataclasses.replace(fusionne, taux_cotisation_retraite=0.5))


def test_le_constructeur_ne_sert_que_ce_qu_il_transmet(simulateur):
    """Une méthode que la façade ne déclare pas, un constructeur qu'elle ne
    sert pas, une retouche : refusés, au lieu de tourner en Python."""
    with pytest.raises(NonTransmissible, match="constructeur.taux_unifie"):
        simulateur.constructeur.taux_unifie
    with pytest.raises(NonTransmissible, match="constructeur_liberal"):
        simulateur.constructeur_liberal
    with pytest.raises(NonTransmissible, match="modifi"):
        simulateur.constructeur.taux_effectif = None
    with pytest.raises(ValueError, match="constructeur.taux_unifie"):
        pont.constructeur_du_compte("constructeur", "taux_unifie", dict)
    assert facade.CONSTRUCTEURS is pont.CONSTRUCTEURS_DE_LA_FACADE


#: Une mère née en 1962, au salaire bas, entrée à vingt ans, partie à
#: soixante-quatre ans et demi, en 2027, qui a élevé ses enfants de 1985 à
#: 2002 sous l'AVPF.
MERE_SOUS_L_AVPF = dict(
    annee_naissance=1962, sexe="F", affiliation="salarie_prive_non_cadre", age_debut=20,
    age_liquidation=64.5, niveau_salaire=0.3, profil_carriere="plat",
    interruptions={annee: "education_enfant" for annee in range(1985, 2003)})


def test_une_regle_recoit_une_ligne_de_sa_carriere(simulateur):
    """Une ligne passe au portage par son rang dans la carrière que la règle
    reçoit. L'année 1984, d'emploi, compte parmi les trimestres cotisés ;
    l'année 1990, d'éducation d'un enfant, non : elle porte l'AVPF, dont la
    majoration du minimum retient, depuis septembre 2023, vingt-quatre
    trimestres au plus (L. 351-10, D. 351-2-2), et aucun avant (plafond nul)."""
    moteur = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(**MERE_SOUS_L_AVPF)
    par_annee = {ligne.annee: ligne for ligne in carriere.lignes}
    assert commun.ligne_cotisee(moteur, carriere, par_annee[1984]) is True
    assert commun.ligne_cotisee(moteur, carriere, par_annee[1990]) is False
    assert completer.avpf_retenue(moteur, carriere, 24) == 24
    assert completer.avpf_retenue(moteur, carriere, 0) == 0


def test_une_ligne_ne_passe_qu_avec_sa_carriere(simulateur):
    """Le portage relit la ligne dans la carrière qu'il reçoit : une ligne
    d'une autre carrière, une ligne retouchée n'arriveraient pas au portage
    sous leur valeur : refusées."""
    moteur = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(**MERE_SOUS_L_AVPF)
    autre = simulateur.carriere_simple(**NE_EN_1955)
    with pytest.raises(NonTransmissible, match="ligne"):
        commun.ligne_cotisee(moteur, carriere, autre.lignes[0])
    with pytest.raises(NonTransmissible, match="ligne"):
        commun.ligne_cotisee(moteur, carriere, dataclasses.replace(carriere.lignes[0]))


def test_une_regle_recoit_une_table_que_le_portage_lit_en_map():
    """Un dictionnaire que le portage lit en ``Map`` passe en table, ses clés
    sous leur type, et ce qu'il rend revient en dictionnaire. L'exemple de la
    MSA (« Réforme de la retraite des exploitants : 25 meilleures années »,
    section 3) : 40 trimestres alignés et 132 de non-salarié agricole font
    « 6 ans » et « 19 » (R. 173-3-2) ; 88 trimestres avant 2016 et 44 depuis,
    « 13 ans » et « 6 ans ». Sans minimums, la règle les tient pour nuls."""
    assert liquider.repartir_les_annees(
        25, {"alignes": 40, "msa_non_salaries": 132},
        minimums={"msa_non_salaries": 2}, priorite=("msa_non_salaries", "alignes"),
    ) == {"alignes": 6, "msa_non_salaries": 19}
    assert liquider.repartir_les_annees(
        19, {"avant": 88, "apres": 44}, priorite=("avant", "apres")) == {"avant": 13, "apres": 6}
    assert liquider.repartir_les_annees(25, {"a": 50, "b": 50, "c": 50}) \
        == {"a": 8, "b": 8, "c": 8}


def test_les_points_de_chef_passent_annee_par_annee():
    """Des points par année, une table aux clés entières, et des cotisations
    en couples : vingt points en 1960 et quinze en 1961, de chef, font une
    moyenne de 17,5 et 5 % (R. 732-67) : 21 points, et 15,75 arrondis à 16 ;
    1 000 € par an de 1960 à 1969, à 6 % de rendement et 3 € de service, vingt
    points, 6,57 % de 600 € (D. 732-77), 39,42 €."""
    majores, taux, moyenne = liquider.majorer_les_points_de_1952_a_1972(
        {1960: 20.0, 1961: 15.0}, [1960, 1961])
    assert majores == {1960: 21.0, 1961: 16.0}
    assert (taux, moyenne) == pytest.approx((0.05, 17.5), abs=1e-12)
    assert liquider.majoration_des_points_de_1952_a_1972_d_avant_2026(
        [(annee, 1000.0) for annee in range(1960, 1970)], list(range(1960, 1970)), 0.06, 3.0,
    ) == pytest.approx((39.42, 0.0657, 20.0), abs=1e-9)


def test_une_table_mal_formee_ne_passe_pas():
    """Une table dont une valeur n'est pas simple n'arriverait pas au portage
    sous son type : refusée."""
    with pytest.raises(NonTransmissible, match="durees"):
        liquider.repartir_les_annees(25, {"alignes": [40]})


def test_le_maximum_des_pensions_est_la_moitie_du_plafond(simulateur):
    """Le maximum des pensions du régime général, 50 % du plafond de la
    Sécurité sociale (R. 351-29) : 24 030 € en 2026, le plafond étant de
    48 060 € ; 54 % en font les 12 976,20 € du barème de la réversion de la
    Cnav. Un régime que la fiche ne borne pas n'a pas de maximum."""
    maximum, fiabilite = liquider.maximum_des_pensions(
        simulateur.scenario_actuel, "regime_general", "2026-01-01", 2026)
    assert maximum == pytest.approx(24_030.0) and type(fiabilite) is Fiabilite
    assert liquider.maximum_des_pensions(
        simulateur.scenario_actuel, "regime_lunaire", "2026-01-01", 2026) is None


def test_les_regles_de_la_reversion_se_demandent_sous_un_nom_a_elles():
    """``reversion`` est l'entrée de la réversion : les règles de son module se
    demandent sous ``regles_de_la_reversion``. La durée d'un mariage,
    « déterminée de date à date, est arrondie au nombre de mois inférieur »
    (R. 353-4) : du 15 juin 1990 au 10 mars 2000, 116 mois."""
    duree = regles_de_la_reversion.mois_de_mariage("1990-06-15", "2000-03-10")
    assert (duree, type(duree)) == (116, int)
    assert facade.JUMEAUX["regles_de_la_reversion"] is reversion_python


def test_une_regle_privee_du_jumeau_se_demande_a_la_fonction_du_portage():
    """``_cumuler``, privée au Python, est ``cumuler`` dans le portage, qui
    l'exporte pour la façade. Avant le 1er juillet 1974, la réversion ne se
    cumule pas : elle complète la retraite personnelle, divisée par le nombre
    des réversions de base (D. 171-1) — 3 000 € moins la moitié de 2 000 €.
    Depuis, la limite est de 52 % du total des retraites et de la pension
    principale (D. 355-1) : (50 000 + 65 973) × 52 % = 60 305,96, au-dessus de
    la réversion et des retraites, qui passent entières."""
    assert regles_de_la_reversion._cumuler({"cumul": "aucun"}, 3000.0, 2000.0, 0.0,
                                           None, 2) == (2000.0, 0.0)
    montant, limite = regles_de_la_reversion._cumuler(
        {"cumul": "limite", "cumul_taux": 0.52}, 1000.0, 50000.0, 65973.0, None, 1)
    assert montant == 1000.0 and limite == pytest.approx(60305.96)


def _foyer_du_couple(simulateur, conjoint: str, mariage: str | None = None):
    """Un salarié né en 1955, parti à 66 ans, marié à une conjointe née en
    ``conjoint`` qui déclare 4 000 € de ressources."""
    return simulateur.carriere_simple(
        annee_naissance=1955, sexe="H", affiliation="salarie_prive_non_cadre",
        age_liquidation=66.0, age_debut=20.0, niveau_salaire=0.3,
        conjoint={"naissance": conjoint, "sexe": "F", "mariage": mariage,
                  "ressources": 4000.0, "invalidite": None})


def test_le_plafond_du_couple_se_lit_dans_la_table_du_minimum_vieillesse(simulateur):
    """Le plafond de ressources d'un couple en 2026, que la Cnav publie :
    19 442,21 € par an. Il revient sous le type que son jumeau annonce."""
    table = simulateur.scenario_actuel.minimum_vieillesse
    couple, fiabilite = table.plafond_couple(2026)
    assert type(couple) is float and type(fiabilite) is Fiabilite
    assert couple == 19442.21


def test_le_foyer_se_demande_au_portage_et_revient_sous_son_type(simulateur):
    """« Foyer et net » sur une carrière qui déclare sa conjointe : le barème
    du couple, son plafond, les ressources de la conjointe ; ce que le portage
    rend revient sous le type ``Foyer`` du Python, dont les méthodes se lisent.
    Le mariage après la date rend le barème d'une personne seule."""
    actuel = simulateur.scenario_actuel
    lu = foyer.foyer_et_net(actuel, "assure", "2026-06-01", 2026, 6000.0, True,
                            carriere=_foyer_du_couple(simulateur, "1970"))
    assert type(lu) is foyer_python.Foyer and type(lu.fiabilite) is Fiabilite
    assert (lu.bareme, lu.ressources_conjoint) == ("couple", 4000.0)
    assert lu.plafond == actuel.minimum_vieillesse.plafond_couple(2026)[0]
    assert lu.servie_avec(6000.0) == pytest.approx(6000.0 + lu.minimum_vieillesse)
    avant = foyer.foyer_et_net(actuel, "assure", "2026-06-01", 2026, 6000.0, True,
                               carriere=_foyer_du_couple(simulateur, "1956", "2026-09"))
    assert (avant.bareme, avant.ressources_conjoint) == ("personne_seule", 0.0)
    assert facade.JUMEAUX["foyer"] is foyer_python


def test_le_foyer_ne_recoit_pas_le_contexte_d_une_liquidation(simulateur):
    """Le contexte d'une liquidation, objet du moteur Python, n'arriverait pas
    au portage : la règle est refusée."""
    contexte = liquidation_python.Contexte(simulateur.scenario_actuel, frozenset())
    with pytest.raises(NonTransmissible, match="contexte"):
        foyer.foyer_et_net(simulateur.scenario_actuel, "assure", "2026-06-01", 2026, 6000.0,
                           True, contexte)


def test_les_majorations_forfaitaires_se_demandent_sur_une_pension_de_regime(simulateur):
    """La pension du régime général prise en février 1973 sur la durée
    maximum reçoit 5,5 % au 1er décembre 1982 : « en 1973 à 47,82 % (45,33 %
    x 1,055) » (circulaire Cnav n° 79/82, B) ; sur une durée moindre, rien."""
    pension = PensionRegime(regime="regime_general", montant=1000.0, type_calcul="annuites",
                            detail="", fiabilite=HAUTE, sur_la_duree_maximum=True)
    assert facade.revalorisation.majorations_forfaitaires(
        simulateur.scenario_actuel, pension, "1973-02-01") == (("1982-12-01", 0.055),)
    assert facade.revalorisation.majorations_forfaitaires(
        simulateur.scenario_actuel, dataclasses.replace(pension, sur_la_duree_maximum=False),
        "1973-02-01") == ()
    assert facade.JUMEAUX["revalorisation"] is revalorisation_python


# -- la liquidation ---------------------------------------------------------------------

def _depart_a_taux_plein(simulateur):
    """Un salarié né en 1958, entré à 20 ans, parti à 62, l'âge légal : ses
    168 trimestres passent les 167 requis, sa pension est au taux plein, sans
    surcote."""
    carriere = simulateur.carriere_simple(1958, "H", "salarie_prive_non_cadre", 20, 62)
    return liquidation_python.demande_de_depart(carriere), carriere


def test_la_liquidation_se_demande_au_portage(simulateur):
    """La liquidation d'une demande, dans l'état d'une carrière, sous le
    contexte du moteur de la façade : le taux plein, 50 % (L. 351-1), et la
    pension de chaque régime, que la façade rend en données."""
    demande, carriere = _depart_a_taux_plein(simulateur)
    liquidee = facade.liquidation.liquider(
        demande, facade.liquidation.Etat(carriere),
        facade.liquidation.Contexte(simulateur.scenario_actuel))
    assert liquidee.pensions.taux == 0.5
    montants = {pension.regime: pension.montant for pension in liquidee.regimes}
    assert set(montants) >= {"regime_general", "agirc_arrco"}
    assert all(type(montant) is float and montant > 0 for montant in montants.values())
    assert facade.JUMEAUX["liquidation"] is liquidation_python


def test_la_liquidation_ne_recoit_que_ce_que_la_facade_sait_transmettre(simulateur):
    """L'état d'une carrière seule, le contexte du moteur de la façade sans
    rien de plus : le journal, les pensions déjà servies, une neutralisation,
    une date d'observation, le moteur Python n'arriveraient pas au portage."""
    demande, carriere = _depart_a_taux_plein(simulateur)
    Etat, Contexte = facade.liquidation.Etat, facade.liquidation.Contexte
    moteur = simulateur.scenario_actuel
    for etat, contexte, motif in [
            (Etat(carriere, servies=(object(),)), Contexte(moteur), "état"),
            (Etat(carriere, recalcul=False), Contexte(moteur), "état"),
            (Etat(carriere, journal=Journal()), Contexte(moteur), "état"),
            (Etat(carriere), Contexte(moteur, observation="2026-01-01"), "contexte"),
            (Etat(carriere), Contexte(simulateur_python.Simulateur().scenario_actuel),
             "moteur")]:
        with pytest.raises(NonTransmissible, match=motif):
            facade.liquidation.liquider(demande, etat, contexte)


def _mere_de_deux_enfants(simulateur):
    """Une salariée née en 1970, deux enfants, deux années d'éducation qui
    ouvrent l'AVPF, partie à 64 ans : la cascade mesure ses trimestres
    d'enfants (L. 351-4), puis l'AVPF."""
    return facade.Carriere.depuis_parcours(
        annee_naissance=1970, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 21.0)],
        age_liquidation=64, macro=simulateur.macro, nombre_enfants=2,
        interruptions={1998: "education_enfant", 1999: "education_enfant"})


def test_la_demande_de_depart_se_demande_au_portage(simulateur):
    """La demande qu'un départ appelle : la date d'effet de la carrière, le
    premier du mois qui suit ses 62 ans pour un salarié né en janvier 1958
    parti à l'âge légal (L. 351-1, R. 351-37), sous la nature demandée."""
    carriere = simulateur.carriere_simple(1958, "H", "salarie_prive_non_cadre", 20, 62)
    demande = facade.liquidation.demande_de_depart(carriere)
    assert type(demande) is liquidation_python.Demande
    assert (demande.personne, demande.date_effet, demande.date_evenement, demande.nature) == (
        carriere.personne, f"{carriere.date_liquidation.annee:04d}-"
        f"{carriere.date_liquidation.mois:02d}-01", demande.date_effet, "definitive")
    assert facade.liquidation.demande_de_depart(carriere, nature="fictive").nature == "fictive"


def test_la_liquidation_rend_son_contrat_ses_mesures_et_ses_appels(simulateur):
    """La liquidation entière, telle que le contrat C.6 la décrit, sous une
    neutralisation du contexte : ses composantes, les lignes du relevé qu'elle
    a lues, ses totaux, et la cascade — les trimestres des enfants mesurés par
    une liquidation d'essai, l'AVPF par une autre qui ne trouve rien, trois
    appels de ``liquider`` que la façade compte (§ 7.8). Les constantes du
    module se lisent."""
    carriere = _mere_de_deux_enfants(simulateur)
    Etat, Contexte = facade.liquidation.Etat, facade.liquidation.Contexte
    demande = facade.liquidation.demande_de_depart(carriere)
    avant = facade.liquidation.appels()
    liquidee = facade.liquidation.liquider(demande, Etat(carriere),
                                           Contexte(simulateur.scenario_actuel))
    assert facade.liquidation.appels() - avant == 3
    donnees = liquidee.donnees()
    assert donnees["demande"] == demande.donnees()
    assert donnees["contexte"]["neutralisations"] == []
    assert {c["id"] for c in donnees["composantes"]} >= {
        "pension_regime_general", "pension_agirc_arrco"}
    assert set(donnees["lignes_consommees"]) == {ligne["id"] for ligne in liquidee.releve.lignes()}
    assert [(m.code, m.neutralisation) for m in liquidee.mesures] == [
        ("majoration_duree_assurance", "avantages_non_contributifs")]
    assert type(liquidee.mesures[0]) is liquidation_python.Mesure
    montants = {a.code: a.montant for a in liquidee.avantages}
    assert liquidee.mesures[0].montant == montants["majoration_duree_assurance"] > 0
    assert type(liquidee.total) is float and liquidee.total >= liquidee.total_contributif > 0
    assert liquidee.hors_repartition == 0.0
    assert liquidee.contexte.donnees()["neutralisations"] == []
    sans = facade.liquidation.liquider(
        demande, Etat(carriere), Contexte(simulateur.scenario_actuel,
                                          frozenset({"avantages_non_contributifs"})))
    assert sans.donnees()["contexte"]["neutralisations"] == ["avantages_non_contributifs"]
    # Le total contributif ne compte pas les trimestres des enfants : le même.
    assert sans.mesures == () and sans.total_contributif == liquidee.total_contributif
    assert sans.total < liquidee.total
    assert facade.liquidation.APPELS_DECLARES == liquidation_python.APPELS_DECLARES
    assert facade.liquidation.NEUTRALISATIONS == liquidation_python.NEUTRALISATIONS


def test_une_regle_se_demande_sous_les_parametres_de_son_moteur(simulateur):
    """Les conventions du COR ne valent que pour la page Coût : sous elles, la
    valeur de service de l'Agirc-Arrco de 2045 suit la convention, moins que
    les prix, qui la portent sans elles."""
    convenu = Simulateur(Parametres(conventions_cor=True)).scenario_actuel
    sans, _ = liquider.valeur_du_point(simulateur.scenario_actuel, "agirc_arrco", 2045)
    avec, _ = liquider.valeur_du_point(convenu, "agirc_arrco", 2045)
    assert avec < sans


def test_une_regle_n_est_pas_servie_sous_un_modele_modifie(simulateur, monkeypatch):
    with pytest.raises(NonTransmissible, match="modèle modifié"):
        liquider.annees_au_prorata(21, 126, 174)
    with pytest.raises(NonTransmissible, match="modifi"):
        liquider.annees_au_prorata = lambda *valeurs: 0


def _parametres_du_portage(module: str, regle: str) -> list[tuple[str, str | None]]:
    """Les paramètres de la règle dans le portage, et la valeur par défaut que
    chacun y prend, telle qu'elle est écrite."""
    dossier = RACINE_PROJET / "moteur" / "js"
    source = (dossier / f"{module}.js" if module == "revalorisation"
              else dossier / "droit" / f"{module}.js").read_text(encoding="utf-8")
    # Une règle privée au Python s'exporte sans son tiret bas.
    nom = re.sub(r"_([a-z0-9])", lambda lettre: lettre.group(1).upper(), regle.lstrip("_"))
    ecrits = re.search(r"^export function %s\(((?:[^()]|\(\))*)\)" % nom, source,
                       re.MULTILINE).group(1)
    return [(parametre.split("=")[0].strip(),
             parametre.split("=")[1].strip() if "=" in parametre else None)
            for parametre in ecrits.split(",") if parametre.strip()]


#: La valeur par défaut d'un paramètre, comme le portage l'écrit.
DEFAUTS_DU_PORTAGE = {"null": None, "true": True, "false": False, "[]": ()}


@pytest.mark.parametrize("module, regle", [
    (module, regle) for module, regles in sorted(pont.REGLES_DE_LA_FACADE.items())
    for regle in regles])
def test_chaque_regle_servie_a_les_arguments_de_son_jumeau_dans_leur_ordre(module, regle):
    """La façade passe les arguments par leur rang, ceux que le test tait à
    leur valeur par défaut du Python : le portage en attend autant, sous la
    même valeur par défaut — une table vide pour le ``None`` d'une table
    (``pont.TABLES_DES_REGLES``). Deux noms seulement diffèrent d'un côté à
    l'autre."""
    jumelle = getattr({"commun": commun_python, "completer": completer_python,
                       "foyer": foyer_python, "liquider": liquider_python, "ouvrir": ouvrir_python,
                       "reversion": reversion_python,
                       "revalorisation": revalorisation_python}[module], regle)
    attendus = [(nom, None if parametre.default is inspect.Parameter.empty else parametre.default)
                for nom, parametre in inspect.signature(jumelle).parameters.items()]
    autres_noms = {"annees": "anneesRetenues", "carriere": "carriereSaisie",
                   "periode": "periodeLiquidation"}
    portes = _parametres_du_portage(module, regle)
    assert len(portes) == len(attendus)
    for (nom, defaut), (porte, ecrit) in zip(attendus, portes):
        en_chameau = re.sub(r"_([a-z0-9])", lambda lettre: lettre.group(1).upper(), nom)
        assert porte in (en_chameau, autres_noms.get(nom)), (regle, nom, porte)
        lu = None if ecrit is None else DEFAUTS_DU_PORTAGE.get(ecrit, ecrit)
        if ecrit == "new Map()" and nom in pont.TABLES_DES_REGLES.get(f"{module}.{regle}", ()):
            # La table vide, que la façade passe pour le ``None`` du Python.
            lu = None
        assert (lu if type(lu) is not str else float(lu)) == defaut, (regle, nom, ecrit)
        assert type(lu) is not str or type(defaut) in (int, float), (regle, nom, ecrit)


# -- un test resté sur le moteur Python ------------------------------------------------

def test_un_test_sans_marque_passe_par_la_facade(request):
    """Dans un fichier basculé, les entrées sont celles de la façade, et le
    simulateur du test est le sien, le même d'un test à l'autre."""
    assert Simulateur is facade.Simulateur and reversion is facade.reversion
    assert liquider is facade.liquider and ouvrir is facade.ouvrir
    simulateur = facade.simulateur_du_test(request, Parametres())
    assert type(simulateur) is facade.Simulateur
    assert facade.simulateur_du_test(request, Parametres()) is simulateur
    assert facade.simulateur_du_test(request) is simulateur
    autre = facade.simulateur_du_test(request, Parametres(annee_courante=2030))
    assert autre is not simulateur and autre.parametres.annee_courante == 2030


@pytest.mark.sur_le_moteur_python("essai de la marque")
def test_un_test_marque_reste_sur_le_moteur_python(request):
    """Un test que la façade ne sait pas encore servir garde le moteur Python,
    tel qu'il était : sous sa marque, les entrées de son fichier sont celles
    du Python, et son simulateur aussi."""
    assert Simulateur is simulateur_python.Simulateur
    assert Carriere is carriere_python.Carriere
    assert reversion.__module__ == "retraite_notionnelle.droit.reversion"
    assert liquider is liquider_python and ouvrir is ouvrir_python
    simulateur = facade.simulateur_du_test(request, Parametres())
    assert type(simulateur) is simulateur_python.Simulateur
    assert facade.simulateur_du_test(request, Parametres()) is simulateur


def test_apres_un_test_marque_les_entrees_sont_de_nouveau_celles_de_la_facade():
    assert Simulateur is facade.Simulateur and Carriere is facade.Carriere
    assert reversion is facade.reversion
    assert liquider is facade.liquider and ouvrir is facade.ouvrir


def test_des_variantes_d_univers_sont_refusees():
    with pytest.raises(NonTransmissible, match="variantes"):
        Simulateur(variantes={"notionnel_liberal": object()})


def test_un_refus_de_la_facade_ne_passe_pas_pour_une_erreur_attendue(simulateur):
    """Un test qui attend une erreur du moteur ne verdit pas d'un refus de la
    façade : ``pytest.raises(Exception)`` ne le prend pas."""
    assert not issubclass(NonTransmissible, Exception)
    assert facade.ENTREES == ("simulateur.simuler", "scenario_actuel.calculer",
                              "reversion.reversion", "simulateur.carriere_simple",
                              "simulateur.carriere_parcours", "simulateur.carriere_releve",
                              "carriere.depuis_profil", "carriere.depuis_parcours",
                              "releve.construire", "simulateur.regime_fusionne",
                              "liquidation.liquider", "liquidation.demande_de_depart",
                              "coordonner.coordonner", "compter.compter",
                              "acquerir.acquerir", "compter.cumul_plafonne")
    assert set(facade.ENTREES) == set(pont.LECTURES_DE_LA_FACADE)
