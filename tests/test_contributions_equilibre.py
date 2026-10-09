"""Les contributions d'équilibre de l'Agirc-Arrco : ce que la paie supporte sans points.

``retraite_notionnelle.contributions_equilibre`` lit leurs barèmes
(``legislation/contributions_equilibre_agirc_arrco.yaml``) et dit ce qu'une
carrière en a versé, année par année ; les indicateurs de cycle de vie
l'ajoutent à ce qu'elle verse (action 138, étape 9). Ce module tient les
barèmes aux textes qui les fixent, et la règle à ses bords : l'année qui change
de barème, la tranche des cadres, le seuil de la CET, les statuts que les
textes écartent, le forfait des cultes, le chômage et l'année du départ. Ce
qu'elles déplacent dans le rendement interne, et la preuve que le COR et
TRAJECTOiRE les comptent, est dans ``tests/test_cycle_de_vie_references.py``.
"""

from __future__ import annotations

import datetime as dt

import pytest

from retraite_notionnelle import contributions_equilibre as ce
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import RACINE_DONNEES, Parametres
from retraite_notionnelle.remuneration import _montant, charger_prelevements
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def regles() -> ce.ContributionsEquilibre:
    return ce.charger_contributions_equilibre(RACINE_DONNEES)


def _taux(contribution: ce.Contribution, jour: dt.date, cadre: bool = False
          ) -> list[tuple[float | None, float, float]]:
    return [(t.jusqu_en_plafonds, t.salarie, t.employeur)
            for t in contribution.bareme(jour).tranches(cadre)]


def _carriere(affiliation: str, revenus: dict[int, float],
              champs: dict[int, dict] | None = None) -> Carriere:
    """Une carrière aux revenus donnés, partie au 1er janvier qui suit ; une
    ligne prend en plus les ``champs`` de son année."""
    derniere = max(revenus)
    return Carriere(
        annee_naissance=derniere + 1 - 62, sexe="H", age_liquidation=62.0, jour_naissance=1,
        lignes=[AnneeCarriere(annee=annee, revenu=revenu, affiliation=affiliation,
                              **(champs or {}).get(annee, {}))
                for annee, revenu in sorted(revenus.items())])


# -- les barèmes ------------------------------------------------------------------


def test_les_baremes_sont_ceux_des_accords(regles):
    """Les taux que les accords écrivent, et leurs dates : l'AGFF au
    1er avril 2001 (accord du 10 février 2001, III.2), étendue à la tranche C
    des cadres en 2016 (accord du 30 octobre 2015, article 3) ; la CET de
    l'Agirc montée de 0,07 à 0,35 % de 1997 à 2001 (accord du 25 avril 1996,
    article 7) ; la CEG et la CET de 2019, partagées à 60 et 40 % (accord du
    17 novembre 2017, articles 37 et 38)."""
    agff = regles["agff"]
    assert _taux(agff, dt.date(2001, 4, 1), cadre=True) == [
        (1.0, 0.0080, 0.0120), (4.0, 0.0090, 0.0130)]
    assert _taux(agff, dt.date(2016, 1, 1), cadre=True) == [
        (1.0, 0.0080, 0.0120), (8.0, 0.0090, 0.0130)]
    assert _taux(agff, dt.date(2016, 1, 1), cadre=False) == [
        (1.0, 0.0080, 0.0120), (3.0, 0.0090, 0.0130)]
    totaux = {annee: sum(t.taux for t in regles["cet_agirc"].bareme(
        dt.date(annee, 1, 1)).tranches(True)) for annee in range(1997, 2019)}
    assert [round(totaux[annee], 6) for annee in range(1997, 2002)] == [
        0.0007, 0.0014, 0.0021, 0.0028, 0.0035]
    assert {round(totaux[annee], 6) for annee in range(2001, 2019)} == {0.0035}
    for code, attendus in (("ceg", [0.0215, 0.0270]), ("cet", [0.0035])):
        tranches = regles[code].bareme(dt.date(2019, 1, 1)).tranches(False)
        assert [round(t.taux, 6) for t in tranches] == attendus
        for tranche in tranches:
            assert tranche.employeur == pytest.approx(0.6 * tranche.taux)


def test_chacune_s_arrete_quand_la_suivante_commence(regles):
    """L'AGFF « se substitue » à l'ASF au 1er avril 2001 ; l'accord de 2017
    acte le terme de l'AGFF au 31 décembre 2018, la CET de l'Agirc disparaît
    avec elle, et la CEG et la CET les remplacent au 1er janvier 2019."""
    assert regles["asf"].bareme(dt.date(2001, 3, 1)) is not None
    assert regles["asf"].bareme(dt.date(2001, 4, 1)) is None
    assert regles["agff"].bareme(dt.date(2001, 3, 1)) is None
    for code in ("agff", "cet_agirc"):
        assert regles[code].bareme(dt.date(2018, 12, 1)) is not None
        assert regles[code].bareme(dt.date(2019, 1, 1)) is None
    for code in ("ceg", "cet"):
        assert regles[code].bareme(dt.date(2018, 12, 1)) is None
        assert regles[code].bareme(dt.date(2060, 1, 1)) is not None
    assert regles["asf"].bareme(dt.date(1983, 12, 1)) is None


def test_la_fiche_de_paie_porte_le_dernier_bareme_de_la_ceg_et_de_la_cet(regles):
    """La fiche de paie de l'année courante lit la CEG et la CET dans
    ``prelevements_remuneration.yaml`` : les deux fichiers disent la même
    chose, du premier euro à neuf plafonds, sous le plafond comme au-delà."""
    prelevements = charger_prelevements(RACINE_DONNEES)
    postes = {poste.code: poste for poste in prelevements.profils["salarie_prive"].postes}
    plafond = 48_060.0
    for code, poste in (("ceg", postes["equilibre_general"]),
                        ("cet", postes["equilibre_technique"])):
        for multiple in (0.5, 1.0, 1.2, 3.0, 8.0, 9.0):
            brut = multiple * plafond
            fiche = ((_montant(poste.salarie, brut, plafond)
                      + _montant(poste.employeur, brut, plafond))
                     if poste.du(brut, plafond, cadre=False) else 0.0)
            assert regles[code].montant(prelevements.annee, brut, plafond, cadre=False) == (
                pytest.approx(fiche)), (code, multiple)


# -- une carrière -----------------------------------------------------------------


def test_une_annee_qui_change_de_bareme_preleve_ses_mois(simulateur):
    """En 2001, l'ASF prélève 1,96 % sous le plafond de janvier à mars,
    l'AGFF 2,00 % d'avril à décembre : l'année en prélève la moyenne."""
    plafond = simulateur.macro.plafond_securite_sociale(2001)
    revenu = 0.8 * plafond
    verse = ce.contributions_d_une_carriere(
        simulateur, _carriere("salarie_prive_non_cadre", {2000: revenu, 2001: revenu}))
    assert verse[2001] == pytest.approx(revenu * (3 * 0.0196 + 9 * 0.0200) / 12)
    assert verse[2000] == pytest.approx(revenu * 0.0196)


def test_le_cadre_verse_la_cet_de_l_agirc_sur_toute_sa_remuneration(simulateur):
    """En 2010, le cadre payé deux plafonds verse l'AGFF sur ses tranches A
    et B, et la CET de l'Agirc, 0,35 %, sur toute sa rémunération ; le
    non-cadre au même salaire, l'AGFF seule."""
    plafond = simulateur.macro.plafond_securite_sociale(2010)
    revenu = 2.0 * plafond
    agff = plafond * 0.0200 + plafond * 0.0220
    cadre = ce.contributions_d_une_carriere(
        simulateur, _carriere("salarie_prive_cadre", {2010: revenu}))
    non_cadre = ce.contributions_d_une_carriere(
        simulateur, _carriere("salarie_prive_non_cadre", {2010: revenu}))
    assert cadre[2010] == pytest.approx(agff + revenu * 0.0035)
    assert non_cadre[2010] == pytest.approx(agff)


def test_la_cet_n_est_due_qu_au_dela_du_plafond(simulateur):
    """Depuis 2019, la CET n'est due que si la rémunération dépasse le
    plafond, mais l'est alors dès le premier euro."""
    plafond = simulateur.macro.plafond_securite_sociale(2023)
    sous, dessus = 0.99 * plafond, 1.01 * plafond
    verse = {revenu: ce.contributions_d_une_carriere(
        simulateur, _carriere("salarie_prive_non_cadre", {2023: revenu}))[2023]
        for revenu in (sous, dessus)}
    assert verse[sous] == pytest.approx(sous * 0.0215)
    assert verse[dessus] == pytest.approx(plafond * 0.0215 + (dessus - plafond) * 0.0270
                                          + dessus * 0.0035)


@pytest.mark.parametrize("affiliation", ["fonctionnaire_etat", "contractuel_public", "artisan"])
def test_qui_n_est_pas_a_l_agirc_arrco_n_en_verse_aucune(simulateur, affiliation):
    """Le fonctionnaire, le contractuel public, à l'Ircantec, et l'artisan
    n'en versent aucune."""
    revenus = {annee: 30_000.0 for annee in (1990, 2010, 2020)}
    assert ce.contributions_d_une_carriere(simulateur, _carriere(affiliation, revenus)) == {}


def test_les_statuts_que_l_asf_ecarte_n_en_versent_pas(simulateur):
    """L'assurance chômage recouvrait l'ASF, sauf à Saint-Pierre-et-Miquelon
    (convention du 1er janvier 1994, art. 7, § 2) ; la Nouvelle-Calédonie a
    la CAFAT. Les deux versent l'AGFF, en salariés de l'Arrco."""
    for affiliation in ("salarie_saint_pierre_et_miquelon", "salarie_nouvelle_caledonie"):
        verse = ce.contributions_d_une_carriere(
            simulateur, _carriere(affiliation, {1998: 20_000.0, 2005: 20_000.0}))
        assert 1998 not in verse, affiliation
        assert verse[2005] == pytest.approx(20_000.0 * 0.0200), affiliation


def test_le_ministre_du_culte_verse_la_ceg_sur_son_forfait_depuis_2019(simulateur):
    """La CAVIMAC appelle depuis 2019 un « taux de base » de 10,02 % sur le
    forfait de la cotisation, le SMIC, dont les 2,15 % de la CEG ; le revenu
    déclaré n'y entre pas. Aucun texte lu ne lui fait verser l'AGFF."""
    verse = ce.contributions_d_une_carriere(
        simulateur, _carriere("ministre_du_culte", {2015: 5_000.0, 2022: 5_000.0}))
    forfait = 1820 * simulateur.macro.smic_horaire(2022)
    assert 2015 not in verse
    assert verse[2022] == pytest.approx(forfait * 0.0215)


def test_une_annee_de_chomage_n_en_verse_aucune(simulateur):
    """L'assurance chômage paie à l'Agirc-Arrco des cotisations, que le
    compte porte ; aucune paie ne supporte de contribution."""
    verse = ce.contributions_d_une_carriere(simulateur, _carriere(
        "salarie_prive_non_cadre", {2009: 25_000.0, 2010: 25_000.0},
        {2010: {"type_periode": "chomage_indemnise", "cotisations_versees": False}}))
    assert 2010 not in verse and verse[2009] > 0.0


def test_l_annee_du_depart_ne_porte_que_ses_mois(simulateur):
    """Comme au compte : qui part au 1er juillet ne verse que sur les six mois
    qui précèdent, sous un demi-plafond."""
    plafond = simulateur.macro.plafond_securite_sociale(2024)
    lignes = [AnneeCarriere(annee=annee, revenu=2.0 * plafond,
                            affiliation="salarie_prive_non_cadre")
              for annee in (2023, 2024)]
    carriere = Carriere(annee_naissance=1962, sexe="H", lignes=lignes,
                        age_liquidation=62.5, jour_naissance=1)
    assert carriere.part_retenue(2024) == pytest.approx(0.5)
    verse = ce.contributions_d_une_carriere(simulateur, carriere)
    demi = 0.5 * plafond
    assert verse[2024] == pytest.approx(demi * 0.0215 + demi * 0.0270 + plafond * 0.0035)
