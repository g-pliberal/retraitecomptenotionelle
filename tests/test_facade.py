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

import inspect
import math
import re
from types import SimpleNamespace

import pytest

from retraite_notionnelle import carriere as carriere_python
from retraite_notionnelle import memoire, pont
from retraite_notionnelle import simulateur as simulateur_python
from retraite_notionnelle.carriere import LigneRelevee, Metier
from retraite_notionnelle.config import RACINE_PROJET, Neutralisations, Parametres
from retraite_notionnelle.donnees.chargement import DonneeInsuffisante, Fiabilite
from retraite_notionnelle.droit.commun import PensionRegime
from retraite_notionnelle.droit.liquider import EligibleAgricole
from retraite_notionnelle.journal import Journal
from retraite_notionnelle.remuneration import AnneeComparee, FicheDePaie, RemunerationActif
from retraite_notionnelle.scenarios.actuel import ResultatActuel
from retraite_notionnelle.scenarios.notionnel import ResultatNotionnel
from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Comparaison

import facade
from facade import Carriere, NonTransmissible, Simulateur, reversion
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


def test_une_methode_que_la_facade_ne_sert_pas_est_refusee(simulateur):
    """Une méthode servie se déclare (``pont.TABLES_DE_LA_FACADE``) : une
    autre, une méthode privée, une table que le moteur ne tient pas sont
    refusées, au lieu que le type de ce qu'elles rendent se devine."""
    table = simulateur.scenario_actuel.reversions
    with pytest.raises(NonTransmissible, match="reversions.fiche_du_regime"):
        table.fiche_du_regime("regime_general")
    with pytest.raises(NonTransmissible, match="carriere_longue._portes"):
        simulateur.scenario_actuel.carriere_longue._portes
    with pytest.raises(NonTransmissible, match="table_lunaire"):
        simulateur.scenario_actuel.table_lunaire
    with pytest.raises(ValueError, match="reversions.fiche_du_regime"):
        pont.table_du_moteur("reversions", "fiche_du_regime", dict, "regime_general")
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


# -- un test resté sur le moteur Python ------------------------------------------------

def test_un_test_sans_marque_passe_par_la_facade(request):
    """Dans un fichier basculé, les entrées sont celles de la façade, et le
    simulateur du test est le sien, le même d'un test à l'autre."""
    assert Simulateur is facade.Simulateur and reversion is facade.reversion
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
    simulateur = facade.simulateur_du_test(request, Parametres())
    assert type(simulateur) is simulateur_python.Simulateur
    assert facade.simulateur_du_test(request, Parametres()) is simulateur


def test_apres_un_test_marque_les_entrees_sont_de_nouveau_celles_de_la_facade():
    assert Simulateur is facade.Simulateur and Carriere is facade.Carriere
    assert reversion is facade.reversion


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
                              "carriere.depuis_profil", "carriere.depuis_parcours")
    assert set(facade.ENTREES) == set(pont.LECTURES_DE_LA_FACADE)
