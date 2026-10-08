"""Ce que les emplois classés de la fonction publique ajoutent à la pension.

Action 138, étape 17 : le dépôt ne servait aucune bonification de service, et
TRAJECTOiRE servait celle des policiers (registre, 138.17). La loi n° 57-444
du 8 avril 1957 accorde aux policiers des services actifs « une bonification
pour la liquidation de ladite pension, égale à un cinquième du temps qu'ils
ont effectivement passé en position d'activité dans des services actifs de
police », cinq annuités au plus ; la loi n° 96-452 la même aux surveillants
pénitentiaires. Fiche ``bonification_cinquieme_police_penitentiaire``.

Elle entre aux services liquidés, mais « dans la limite du taux maximal de
75 % » (service des retraites de l'État) ; à la durée d'assurance, qui
« totalise la durée des services et bonifications admissibles en
liquidation » (L. 14, I), et non à celle de la surcote (L. 14, III).

Et l'article 78 de la loi n° 2003-775 majore la durée d'assurance du
fonctionnaire hospitalier de catégorie active d'« un an par période de dix
années de services effectifs », pour la seule décote de la CNRACL : fiche
``majoration_duree_hospitaliers_actifs``, au statut ``fonctionnaire_hospitalier_actif``
qui naît avec elle. Et le sapeur-pompier professionnel, de catégorie active et
non super-active, a sa bonification du cinquième depuis 1986 : fiche
``bonification_cinquieme_sapeurs_pompiers``, au statut ``sapeur_pompier_professionnel``.

Et le militaire a la sienne, au i de L. 12, « dans la limite de cinq annuités à
tous les militaires à la condition qu'ils aient accompli au moins dix-sept ans
de services militaires effectifs » : fiche ``bonification_cinquieme_militaires``,
la seule de ces bonifications qui porte le taux au-delà de 75 %.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import releve
from retraite_notionnelle.simulateur import Simulateur

POLICIER = "fonctionnaire_etat_super_actif"
ETAT = ("fonction_publique_etat",)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, metiers: list[Metier], naissance: int,
              liquidation: float, avantages: bool = True):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="H", metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, mois_naissance=1,
        part_primes=0.15)
    durees = releve.construire(simulateur.scenario_actuel, carriere,
                               avantages_non_contributifs=avantages).durees
    resultat = simulateur.scenario_actuel.calculer(carriere)
    pensions = {p.regime: p for p in resultat.pensions_par_regime}
    return durees, resultat, pensions


def test_vingt_trimestres_au_policier_de_trente_trois_ans_de_services(simulateur):
    """Le policier du cas type 8 du COR, né en 1960 : trente-trois ans de
    services actifs, départ à cinquante-deux ans en janvier 2012. Un cinquième
    de trente-trois ans, six ans et sept mois, borné à cinq annuités : vingt
    trimestres, aux services liquidés — 152/162 de 75 % — et à la durée."""
    durees, resultat, pensions = _calculer(
        simulateur, [Metier(POLICIER, 19.0, 1.0)], naissance=1960, liquidation=52.0)
    (emploi,) = durees.emplois
    assert (emploi.fiche, emploi.version) == (
        "bonification_cinquieme_police_penitentiaire", "loi_du_9_novembre_2010")
    assert (emploi.services, emploi.duree, emploi.majoration) == (20, 20, 0)
    assert durees.services_des_emplois(ETAT) == 20
    assert resultat.trimestres_valides == 132 + 20
    assert "× 152/162" in pensions["fonction_publique_etat"].detail


def test_sans_la_duree_de_l_age_minore_pas_de_bonification(simulateur):
    """Vingt-deux ans de services actifs, quand la génération 1960 en demande
    vingt-sept pour l'âge minoré : ni l'un ni l'autre."""
    durees, _, _ = _calculer(
        simulateur, [Metier(POLICIER, 30.0, 1.0)], naissance=1960, liquidation=52.0)
    assert durees.emplois == ()


def test_les_services_au_dela_de_cinquante_sept_ans_la_reduisent_jusqu_en_2023(simulateur):
    """Né en janvier 1953, policier de vingt à soixante ans, départ en janvier
    2013 : les trois années servies depuis ses cinquante-sept ans, de janvier
    2010 à décembre 2012, retirent trois annuités — huit trimestres, et non
    vingt (« réduite à concurrence de la durée des services accomplis au-delà de
    cinquante-sept ans »). Comptées à l'année, l'année de l'anniversaire
    réputée servie avant lui, elles n'en retiraient que deux. Et sous le
    maximum : 150/150, non 168/150."""
    durees, _, pensions = _calculer(
        simulateur, [Metier(POLICIER, 20.0, 1.0)], naissance=1953, liquidation=60.0)
    assert [e.services for e in durees.emplois] == [8]
    assert "× 150/150" in pensions["fonction_publique_etat"].detail
    # Depuis le 1er septembre 2023, aucune réduction : vingt trimestres.
    durees, _, _ = _calculer(
        simulateur, [Metier(POLICIER, 20.0, 1.0)], naissance=1964, liquidation=62.0)
    assert [(e.version, e.services) for e in durees.emplois] == [("loi_du_14_avril_2023", 20)]


def test_rien_avant_la_loi_de_1957(simulateur):
    """La loi l'accorde « à compter du 1er janvier 1957 »."""
    durees, _, _ = _calculer(
        simulateur, [Metier(POLICIER, 20.0, 1.0)], naissance=1900, liquidation=54.0)
    assert durees.emplois == ()


def test_la_bonification_n_ouvre_pas_la_surcote(simulateur):
    """Né en 1964, policier de vingt-cinq à soixante-quatre ans : 156 trimestres
    de services, vingt de bonification. Sa durée efface la décote et sa
    pension atteint le maximum ; mais « les bonifications de durée de services
    […] ne sont pas prises en compte » pour la surcote (L. 14, III) : ses huit
    trimestres d'après soixante-deux ans n'en ouvrent aucune."""
    durees, resultat, pensions = _calculer(
        simulateur, [Metier(POLICIER, 25.0, 1.0)], naissance=1964, liquidation=64.0)
    assert durees.duree_hors_surcote == 20
    assert resultat.trimestres_valides >= resultat.trimestres_requis
    assert resultat.taux_liquidation == pytest.approx(0.75)
    assert f"× {resultat.trimestres_requis}/{resultat.trimestres_requis}" in (
        pensions["fonction_publique_etat"].detail)


def test_le_contributif_pur_ne_la_sert_pas(simulateur):
    """La valorisation des droits acquis ne mesure que le contributif : la
    bonification, que rien n'a cotisé, en sort avec les trimestres des
    enfants."""
    durees, _, _ = _calculer(simulateur, [Metier(POLICIER, 19.0, 1.0)],
                             naissance=1960, liquidation=52.0, avantages=False)
    assert durees.emplois == ()
    assert durees.trimestres == 132


# -- la majoration de durée des hospitaliers actifs ----------------------------

HOSPITALIER = "fonctionnaire_hospitalier_actif"
CNRACL = ("cnracl",)


def _durees_de(simulateur: Simulateur, metiers: list[Metier], naissance: int,
               liquidation: float):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="F", metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, mois_naissance=1,
        part_primes=0.15)
    durees = releve.construire(simulateur.scenario_actuel, carriere).durees
    return durees, simulateur.scenario_actuel.calculer(carriere)


def test_quinze_trimestres_a_l_aide_soignante_de_trente_huit_ans_de_services(simulateur):
    """L'aide-soignante du cas type 9 du COR, née en 1960, entrée à dix-huit ans
    et demi, partie à cinquante-sept ans en janvier 2017 : « un an par période de
    dix années de services effectifs », au prorata, soit quinze trimestres pour
    trente-huit ans et demi. Ils effacent sa décote, sans entrer ni aux services
    liquidés (154/166) ni à la durée tous régimes, qui reste de 154 trimestres :
    la majoration ne vaut que « pour l'application des dispositions du I de
    l'article L. 14 »."""
    durees, resultat = _durees_de(simulateur, [Metier(HOSPITALIER, 18.5, 1.0)],
                                  naissance=1960, liquidation=57.0)
    (emploi,) = durees.emplois
    assert (emploi.fiche, emploi.version) == (
        "majoration_duree_hospitaliers_actifs", "loi_du_9_novembre_2010")
    assert (emploi.services, emploi.duree, emploi.majoration) == (0, 0, 15)
    assert durees.majorations_des_emplois(CNRACL) == 15
    assert resultat.trimestres_valides == 154
    assert resultat.taux_liquidation == pytest.approx(0.75)
    # Le statut qui ne dit pas le versant n'a rien : sa décote demeure.
    durees, resultat = _durees_de(
        simulateur, [Metier("fonctionnaire_territorial_hospitalier_actif", 18.5, 1.0)],
        naissance=1960, liquidation=57.0)
    assert durees.emplois == ()
    assert resultat.taux_liquidation < 0.75


def test_rien_avant_2008(simulateur):
    """Les droits « s'ouvrent à compter du 1er janvier 2008 au plus tôt »."""
    durees, _ = _durees_de(simulateur, [Metier(HOSPITALIER, 20.0, 1.0)],
                           naissance=1950, liquidation=55.0)
    assert durees.emplois == ()


def test_jusqu_en_2023_il_faut_etre_dans_l_emploi_a_la_radiation(simulateur):
    """Vingt ans d'emploi hospitalier actif, puis un emploi sédentaire. Jusqu'en
    août 2023, l'agent doit être « titulaire d'un emploi classé en catégorie
    active au moment de la radiation des cadres » ; depuis, il suffit d'avoir eu
    « la qualité de fonctionnaire hospitalier » et dix-sept ans de services
    actifs : seize trimestres pour quarante et un ans de services."""
    metiers = [Metier(HOSPITALIER, 22.0, 1.0),
               Metier("fonctionnaire_territorial_hospitalier", 42.0, 1.0)]
    durees, _ = _durees_de(simulateur, metiers, naissance=1955, liquidation=60.0)
    assert durees.emplois == ()
    durees, _ = _durees_de(simulateur, metiers, naissance=1962, liquidation=63.0)
    assert [(e.version, e.majoration) for e in durees.emplois] == [
        ("loi_du_14_avril_2023", 16)]


def test_bonification_et_majoration_dans_la_limite_de_vingt_trimestres(simulateur):
    """Policier vingt-huit ans, puis aide-soignant : sa bonification du cinquième,
    vingt trimestres, épuise la limite que l'article 21 du décret n° 2003-1306
    pose depuis septembre 2023 ; la majoration ne s'y ajoute pas."""
    durees, _ = _durees_de(
        simulateur, [Metier(POLICIER, 20.0, 1.0), Metier(HOSPITALIER, 48.0, 1.0)],
        naissance=1970, liquidation=60.0)
    assert [(e.fiche, e.services, e.duree, e.majoration) for e in durees.emplois] == [
        ("bonification_cinquieme_police_penitentiaire", 20, 20, 0)]


# -- la bonification du cinquième des sapeurs-pompiers professionnels ----------

POMPIER = "sapeur_pompier_professionnel"


def test_vingt_trimestres_au_sapeur_pompier_sous_le_maximum(simulateur):
    """Né en 1960, sapeur-pompier de vingt à cinquante-sept ans, départ en
    janvier 2017 : trente-sept ans de services, dont autant en cette qualité,
    l'âge anticipé de sa génération atteint ; vingt trimestres, qui « ne
    peuvent avoir pour effet de porter le nombre des trimestres liquidables
    dans la pension au-delà du maximum » : 166/166, non 168/166."""
    durees, resultat, pensions = _calculer(
        simulateur, [Metier(POMPIER, 20.0, 1.0)], naissance=1960, liquidation=57.0)
    assert [(e.fiche, e.version, e.services) for e in durees.emplois] == [
        ("bonification_cinquieme_sapeurs_pompiers", "decret_du_30_decembre_2010", 20)]
    assert resultat.trimestres_valides == 148 + 20
    assert "× 166/166" in pensions["cnracl"].detail
    # Le statut est de catégorie active, non super-active : l'âge anticipé.
    assert resultat.age_ouverture_opposable == pytest.approx(57.0)


def test_le_sapeur_pompier_de_quatorze_ans_n_a_rien(simulateur):
    """Vingt-trois ans d'emploi territorial sédentaire, puis quatorze de
    sapeur-pompier : moins des dix-sept années en cette qualité."""
    durees, _, _ = _calculer(
        simulateur, [Metier("fonctionnaire_territorial_hospitalier", 20.0, 1.0),
                     Metier(POMPIER, 43.0, 1.0)], naissance=1960, liquidation=57.0)
    assert durees.emplois == ()


def test_rien_avant_le_decret_de_1986_puis_trente_ans_de_services(simulateur):
    """Le décret n° 86-169 l'applique aux sapeurs-pompiers admis à la retraite
    après le 7 février 1986 ; de 2004 à 2011, cent vingt trimestres de
    services, dont soixante de sapeur-pompier, et cinquante-cinq ans."""
    durees, _, _ = _calculer(simulateur, [Metier(POMPIER, 25.0, 1.0)],
                             naissance=1928, liquidation=55.0)
    assert durees.emplois == ()
    durees, _, pensions = _calculer(simulateur, [Metier(POMPIER, 25.0, 1.0)],
                                    naissance=1950, liquidation=55.0)
    assert [(e.version, e.services) for e in durees.emplois] == [("decret_de_2003", 20)]
    assert "× 140/154" in pensions["cnracl"].detail


# -- la bonification du cinquième des militaires -------------------------------

MILITAIRE = "militaire"
OFFICIER = "militaire_officier"
MILITAIRES = "bonification_cinquieme_militaires"


def test_vingt_trimestres_au_sous_officier_de_la_grille(simulateur):
    """Le cas type militaire de la grille : engagé à dix-neuf ans, radié à
    quarante-quatre, en 2024. Un cinquième de vingt-cinq ans, cinq annuités :
    vingt trimestres, aux services liquidés et à la durée — 120 trimestres
    liquidés, non 100."""
    durees, resultat, pensions = _calculer(
        simulateur, [Metier(MILITAIRE, 19.0, 1.0)], naissance=1980, liquidation=44.0)
    (emploi,) = durees.emplois
    assert (emploi.fiche, emploi.version) == (MILITAIRES, "loi_du_14_avril_2023")
    assert (emploi.services, emploi.duree, emploi.majoration) == (20, 20, 0)
    assert emploi.au_dela_du_maximum
    assert resultat.trimestres_valides == 100 + 20
    assert f"× 120/{resultat.trimestres_requis}" in pensions["fonction_publique_etat"].detail


def test_elle_porte_le_taux_au_dela_de_75_pour_cent(simulateur):
    """L'officier né en 1960, de vingt-deux à soixante-deux ans, parti en
    janvier 2022 : cent soixante trimestres de services, plus que les 156
    requis, et deux ans de bonification, après trois années servies depuis ses
    cinquante-neuf ans. « Le pourcentage maximum fixé à l'article L 13
    peut-être augmenté de cinq points du chef des bonifications » : 164/156 de
    75 %, quand le policier, de bonification égale, reste au maximum."""
    durees, _, pensions = _calculer(
        simulateur, [Metier(OFFICIER, 22.0, 1.0)], naissance=1960, liquidation=62.0)
    assert [(e.version, e.services) for e in durees.emplois] == [("loi_du_9_novembre_2010", 8)]
    assert "× 164/156" in pensions["fonction_publique_etat"].detail


def test_une_annuite_de_moins_par_annee_entiere_puis_rien_apres_l_age_legal(simulateur):
    """« Le maximum de bonifications est donné aux militaires qui quittent le
    service à cinquante-neuf ans ; la bonification est diminuée d'une annuité
    pour chaque année supplémentaire de service jusqu'à l'âge mentionné à
    l'article L. 161-17-2 » : l'officier né en janvier 1952, parti à soixante
    ans et demi en juillet 2012, a servi un an et demi au-delà, et perd une
    annuité — seize trimestres. Parti six mois plus tard, après l'âge légal de
    sa génération, soixante ans et neuf mois, il n'en a aucune : « Aucune
    bonification du 1/5ème n'est accordée au delà de 62 ans » (service des
    retraites de l'État, pour la génération de soixante-deux ans)."""
    durees, _, _ = _calculer(simulateur, [Metier(OFFICIER, 22.0, 1.0)],
                             naissance=1952, liquidation=60.5)
    assert [e.services for e in durees.emplois] == [16]
    durees, _, _ = _calculer(simulateur, [Metier(OFFICIER, 22.0, 1.0)],
                             naissance=1952, liquidation=61.0)
    assert durees.emplois == ()


def test_jusqu_en_2023_l_ancien_militaire_n_en_a_pas(simulateur):
    """Vingt-deux ans de services militaires, puis fonctionnaire civil de l'État
    jusqu'à la liquidation. « À tous les militaires » jusqu'en août 2023 :
    l'ancien militaire n'a rien. Depuis, « à tous les militaires et anciens
    militaires » : un cinquième de vingt-deux ans, dix-huit trimestres."""
    metiers = [Metier(MILITAIRE, 18.0, 1.0), Metier("fonctionnaire_etat", 40.0, 1.0)]
    durees, _, _ = _calculer(simulateur, metiers, naissance=1958, liquidation=62.0)
    assert durees.emplois == ()
    durees, _, _ = _calculer(simulateur, metiers, naissance=1962, liquidation=63.0)
    assert [(e.version, e.services) for e in durees.emplois] == [("loi_du_14_avril_2023", 18)]


def test_dix_sept_ans_de_services_depuis_2011_quinze_avant(simulateur):
    """Seize ans de services militaires : rien en 2026, où il en faut dix-sept ;
    en 1996, où il en fallait quinze, un cinquième de seize ans, treize
    trimestres."""
    durees, _, _ = _calculer(simulateur, [Metier(MILITAIRE, 20.0, 1.0)],
                             naissance=1990, liquidation=36.0)
    assert durees.emplois == ()
    durees, _, _ = _calculer(simulateur, [Metier(MILITAIRE, 20.0, 1.0)],
                             naissance=1960, liquidation=36.0)
    assert [(e.version, e.services) for e in durees.emplois] == [
        ("redaction_du_14_juillet_1982", 13)]


def test_trois_annuites_de_1972_a_1975_et_rien_avant(simulateur):
    """La loi de finances pour 1972 accorde aux militaires rayés des cadres
    depuis le 1er janvier 1972 un cinquième du temps accompli, « dans la limite
    de trois annuités », à vingt-cinq ans de services, hors de L. 12 : sous le
    maximum. La loi du 30 octobre 1975 la rend permanente, cinq annuités."""
    durees, _, _ = _calculer(simulateur, [Metier(MILITAIRE, 18.0, 1.0)],
                             naissance=1925, liquidation=46.0)
    assert durees.emplois == ()
    durees, _, _ = _calculer(simulateur, [Metier(MILITAIRE, 18.0, 1.0)],
                             naissance=1927, liquidation=46.0)
    assert [(e.version, e.services, e.au_dela_du_maximum) for e in durees.emplois] == [
        ("loi_de_finances_pour_1972", 12, False)]
    durees, _, _ = _calculer(simulateur, [Metier(MILITAIRE, 18.0, 1.0)],
                             naissance=1930, liquidation=46.0)
    assert [(e.version, e.services) for e in durees.emplois] == [("loi_du_30_octobre_1975", 20)]


def test_avec_celle_du_policier_dans_la_limite_de_vingt_trimestres(simulateur):
    """Militaire dix-sept ans, puis policier vingt-neuf : depuis septembre 2023,
    la bonification du policier, vingt trimestres, et celle du militaire « peuvent
    se cumuler, dans la limite de vingt trimestres » (L. 12) ; la seconde ne
    s'ajoute pas."""
    metiers = [Metier(MILITAIRE, 18.0, 1.0), Metier(POLICIER, 35.0, 1.0)]
    durees, _, _ = _calculer(simulateur, metiers, naissance=1965, liquidation=64.0)
    assert [(e.fiche, e.services) for e in durees.emplois] == [
        ("bonification_cinquieme_police_penitentiaire", 20)]
