"""Le chômage aux régimes complémentaires (action 141) : la borne de quatre
plafonds, le premier jour validé, la solidarité à 4 %, 8 % ou 12 %, et ce que
le compte notionnel porte d'une année chômée — le versement de l'Unédic ou de
l'État, la participation de l'allocataire aux scénarios 2 et 3. Les règles sont
dans `legislation/chomage_complementaires.yaml`, la fiche dans
`regles/chomage_retraite_complementaire.yaml` ; les témoins `chomage_*` et
`solidarite_*` confrontent les deux moteurs."""

from __future__ import annotations

import re

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.config import RACINE_DONNEES, PartCotisation
from retraite_notionnelle.donnees.chargement import charger_chomage_complementaires
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def regles():
    return charger_chomage_complementaires(RACINE_DONNEES)


def _carriere(simulateur, interruptions, niveau=2.0, naissance=1965):
    return simulateur.carriere_simple(
        annee_naissance=naissance, sexe="F", affiliation="salarie_prive_cadre",
        mois_naissance=1, age_debut=22, age_liquidation=64,
        niveau_salaire=niveau, profil_carriere="plat", interruptions=interruptions)


def _ligne(carriere, annee):
    (ligne,) = [l for l in carriere.lignes if l.annee == annee]
    return ligne


def _compte(simulateur, carriere, annee, part):
    constructeur = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, simulateur.parametres.avec(part_cotisation=part))
    return constructeur.cotisation_annuelle(carriere, annee)


def _points(simulateur, regime, interruptions, **carriere):
    resultat = simulateur.scenario_actuel.calculer(
        _carriere(simulateur, interruptions, **carriere))
    detail = {p.regime: p for p in resultat.pensions_par_regime}[regime].detail
    return float(re.search(r"([\d,]+\.\d+) points", detail).group(1).replace(",", ""))


def test_les_regles_du_chomage_se_lisent(regles):
    """Ce que le fichier dit, tel que les moteurs le lisent."""
    assert regles.nature("chomage_indemnise", 2010) == "assurance"
    assert regles.nature("chomage_solidarite", 2010) == "solidarite"
    # La solidarité naît le 1er avril 1984 : avant, le régime était unique.
    assert regles.nature("chomage_solidarite", 1983) == "assurance"
    assert regles.nature("maladie", 2010) is None
    # Rien avant le 1er octobre 1967, trois mois en 1967 ; l'Ircantec en 1977.
    assert [regles.part_validee("agirc", a) for a in (1966, 1967, 1968)] == [0.0, 0.25, 1.0]
    assert regles.part_validee("ircantec", 1977) == pytest.approx(5 / 12)
    assert regles.part_validee("agirc_arrco", 2020) == 1.0
    # L'Arrco valide aux taux obligatoires la solidarité des ruptures d'avant
    # juin 2000, que l'État finance pourtant à 4 %.
    assert regles.taux_solidarite("arrco", 1995, points=True) is None
    assert regles.taux_solidarite("arrco", 1995, points=False) == 0.04
    # La date de la rupture décide, non l'année de l'allocation.
    assert regles.taux_solidarite("arrco", 2003, points=True, rupture=1998) is None
    assert regles.taux_solidarite("arrco", 2003, points=True, rupture=2001) == 0.04
    assert regles.taux_solidarite("agirc", 1990, points=True) == 0.08
    assert regles.taux_solidarite("agirc_entreprises_nouvelles", 1990, points=True) == 0.12
    assert regles.taux_solidarite("agirc_arrco", 2021, points=True) == 0.04
    assert regles.taux_solidarite("ircantec", 2021, points=True) is None
    # La participation de l'allocataire : rien avant mars 1988, 3 % depuis 2003.
    assert regles.taux_participation(1987) == 0.0
    assert regles.taux_participation(1988) == pytest.approx(0.004 * 10 / 12)
    assert regles.taux_participation(2010) == 0.03


def test_le_salaire_de_reference_du_chomage_s_arrete_a_quatre_plafonds(simulateur):
    """Le salaire journalier de référence se calcule sur l'assiette des
    contributions, bornée à quatre plafonds (règlement de 2019, art. 11 et
    49) ; la maladie, elle, garde le salaire d'avant."""
    carriere = _carriere(simulateur, {2021: "chomage_indemnise", 2022: "maladie"},
                         niveau=8.0, naissance=1970)
    plafond = simulateur.macro.plafond_securite_sociale(2021)
    assert _ligne(carriere, 2021).revenu_reference == pytest.approx(4 * plafond)
    assert _ligne(carriere, 2022).revenu_reference > 4 * simulateur.macro.plafond_securite_sociale(2022)


def test_rien_n_est_valide_avant_1967(simulateur):
    """Les complémentaires ne valident le chômage que depuis le 1er octobre
    1967 : une année chômée de 1966 ne vaut rien au compte, quand celle de 1968
    vaut ce que l'Unédic versait."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="salarie_prive_non_cadre",
        mois_naissance=1, age_debut=19, age_liquidation=60, niveau_salaire=1.0,
        profil_carriere="plat", interruptions={1966: "chomage_indemnise",
                                               1968: "chomage_indemnise"})
    assert _compte(simulateur, carriere, 1966, PartCotisation.TOTALE).cotisation == 0.0
    assert _compte(simulateur, carriere, 1968, PartCotisation.TOTALE).cotisation > 0.0


def test_le_compte_porte_le_versement_de_l_unedic(simulateur):
    """Une année d'assurance porte 60 % de ce qu'une année travaillée porterait
    à chaque régime, et 0,8 % de son assiette ; les scénarios 2 et 3, la
    participation de l'allocataire, 3 % du salaire de référence en 2010."""
    chomee = _carriere(simulateur, {2010: "chomage_indemnise"})
    revenu = _ligne(chomee, 2010).revenu_reference
    plafond = simulateur.macro.plafond_securite_sociale(2010)
    assert revenu > plafond
    travaillee = dict(_compte(simulateur, _carriere(simulateur, {}), 2010,
                              PartCotisation.TOTALE).par_regime)
    verse = dict(_compte(simulateur, chomee, 2010, PartCotisation.TOTALE).par_regime)
    assert verse["arrco"] == pytest.approx(0.6 * travaillee["arrco"] + 0.008 * plafond)
    assert verse["agirc"] == pytest.approx(
        0.6 * travaillee["agirc"] + 0.008 * (revenu - plafond))
    salariale = _compte(simulateur, chomee, 2010, PartCotisation.SALARIALE)
    assert salariale.cotisation == pytest.approx(0.03 * revenu)
    assert salariale.part_employeur == 0.0


def test_le_compte_porte_le_versement_de_l_etat_pour_la_solidarite(simulateur):
    """Une année de solidarité porte 70 % de la cotisation au taux que l'État
    finance — 4 % à l'Arrco, 8 % sur la tranche B de l'Agirc —, taux d'appel
    compris ; l'allocataire ne paie rien, et les scénarios 2 et 3 n'en portent
    rien."""
    chomee = _carriere(simulateur, {2010: "chomage_solidarite"})
    revenu = _ligne(chomee, 2010).revenu_reference
    plafond = simulateur.macro.plafond_securite_sociale(2010)
    valeurs = simulateur.scenario_actuel.valeurs_point
    verse = dict(_compte(simulateur, chomee, 2010, PartCotisation.TOTALE).par_regime)
    assert verse["arrco"] == pytest.approx(
        0.7 * plafond * 0.04 * valeurs.achat("arrco", 2010)[1])
    assert verse["agirc"] == pytest.approx(
        0.7 * (revenu - plafond) * 0.08 * valeurs.achat("agirc", 2010)[1])
    assert _compte(simulateur, chomee, 2010, PartCotisation.SALARIALE).cotisation == 0.0


def test_la_solidarite_vaut_des_points_a_son_taux(simulateur):
    """Au scénario 1, une année d'assurance vaut les points d'une année
    travaillée ; une année de solidarité, ceux de 4 % à l'Arrco et de 8 % sur la
    tranche B de l'Agirc, au lieu des taux contractuels de l'année."""
    for regime, taux in (("arrco", 0.04), ("agirc", 0.08)):
        sans = _points(simulateur, regime, {2010: "sans_activite"})
        travaillee = _points(simulateur, regime, {})
        assurance = _points(simulateur, regime, {2010: "chomage_indemnise"})
        solidarite = _points(simulateur, regime, {2010: "chomage_solidarite"})
        assert assurance == pytest.approx(travaillee, abs=0.01)
        (periode,) = [p for p in simulateur.catalogue[regime].periodes_actives(2010)
                      if p.assiette in ("tranche_1", "tranche_a", "tranche_b")]
        appel = simulateur.scenario_actuel.valeurs_point.achat(regime, 2010)[1]
        contractuel = periode.taux_cotisation_retraite / appel
        assert (solidarite - sans) / (travaillee - sans) == pytest.approx(
            taux / contractuel, abs=0.001)


def test_la_solidarite_n_a_pas_de_garantie_minimale(simulateur):
    """Le guide réglementaire assortit de la garantie minimale de points les
    taux de l'allocation spéciale du FNE, « depuis 1989 », et valide l'ASS
    « seulement sur la base du taux de 8 % ou de 12 % » (titre VII.3.1.6.2) :
    une cadre payée sous le plafond garde au chômage d'assurance les points de
    la garantie, et n'a rien à l'Agirc pour une année d'ASS."""
    carriere = {"niveau": 0.8, "naissance": 1975}
    sans = _points(simulateur, "agirc", {2005: "sans_activite"}, **carriere)
    assurance = _points(simulateur, "agirc", {2005: "chomage_indemnise"}, **carriere)
    solidarite = _points(simulateur, "agirc", {2005: "chomage_solidarite"}, **carriere)
    assert assurance - sans == pytest.approx(120, abs=1)
    assert solidarite == pytest.approx(sans, abs=0.01)


def test_les_regles_de_la_preretraite_et_des_agricoles_se_lisent(regles):
    """La préretraite du FNE a les taux de la solidarité et deux plafonds
    depuis 1998 ; le salarié agricole n'a rien avant le 1er avril 1974 ;
    trente jours au moins jusqu'en 1973 ; l'indemnisation cesse au taux plein
    depuis 1984."""
    assert regles.nature("preretraite_fne", 1990) == "fne"
    assert regles.nature("preretraite_fne", 1983) == "assurance"
    # La convention décide, non l'année : une préretraite commencée en 1982
    # garde les taux de l'assurance après 1984.
    assert regles.nature("preretraite_fne", 1986, debut=1982) == "assurance"
    assert regles.nature("preretraite_fne", 1986, debut=1985) == "fne"
    assert regles.plafond_preretraite(1997) is None
    assert regles.plafond_preretraite(1998) == 2
    assert [regles.part_validee("arrco", a, "salarie_agricole")
            for a in (1973, 1974, 1975)] == [0.0, 0.75, 1.0]
    assert regles.part_validee("arrco", 1973, "salarie_prive_non_cadre") == 1.0
    assert not regles.assez_long(1970, 29 / 365)
    assert regles.assez_long(1970, 1 / 12)
    assert regles.assez_long(1974, 1 / 365)
    assert regles.fin_indemnisation_duree_depuis == (1983, 4)


def test_la_preretraite_du_fne_a_deux_plafonds_et_sa_garantie(simulateur):
    """L'allocation spéciale du FNE : un salaire de référence borné à deux
    plafonds pour une convention conclue depuis le 5 mai 1997, que le modèle
    date du premier millésime de la préretraite, les points de 8 % sur la
    tranche B de l'Agirc, et la garantie minimale de points à la même
    proportion — 60 points en 2005 quand le forfait en achète 120 à 16 %
    (guide réglementaire, VII.3.1.6.2)."""
    def agirc(motif):
        return _points(simulateur, "agirc", {1998: motif}, niveau=3.0, naissance=1940)

    carriere = _carriere(simulateur, {1998: "preretraite_fne"}, niveau=3.0, naissance=1940)
    plafond = simulateur.macro.plafond_securite_sociale(1998)
    revenu = _ligne(carriere, 1998).revenu_reference
    assert revenu > 2.5 * plafond
    # Sur la tranche B, l'ASS vaut 8 % de ce qui dépasse le plafond, la
    # préretraite de 1998 8 % d'un seul plafond.
    sans = agirc("sans_activite")
    assert (agirc("preretraite_fne") - sans) / (agirc("chomage_solidarite") - sans) == (
        pytest.approx(plafond / (revenu - plafond), abs=1e-4))
    # Entrée en préretraite en 1997, la convention est d'avant le 5 mai 1997 :
    # quatre plafonds, comme l'ASS.
    entree_1997 = _points(simulateur, "agirc", {1997: "preretraite_fne", 1998: "preretraite_fne"},
                          niveau=3.0, naissance=1940)
    ass_1997 = _points(simulateur, "agirc", {1997: "preretraite_fne", 1998: "chomage_solidarite"},
                       niveau=3.0, naissance=1940)
    assert entree_1997 == pytest.approx(ass_1997, abs=0.02)
    garantie = {"niveau": 0.8, "naissance": 1975}
    sans = _points(simulateur, "agirc", {2005: "sans_activite"}, **garantie)
    assurance = _points(simulateur, "agirc", {2005: "chomage_indemnise"}, **garantie)
    fne = _points(simulateur, "agirc", {2005: "preretraite_fne"}, **garantie)
    assert fne - sans == pytest.approx((assurance - sans) / 2, abs=0.01)


def test_l_etat_verse_la_garantie_de_la_preretraite(simulateur):
    """Le compte porte 70 % de la cotisation que l'État finance pour la
    préretraite du FNE, garantie minimale comprise : sur l'assiette qu'elle
    fait cotiser, et non sur un salaire qui ne dépasse pas le plafond."""
    chomee = _carriere(simulateur, {2005: "preretraite_fne"}, niveau=0.8, naissance=1975)
    verse = dict(_compte(simulateur, chomee, 2005, PartCotisation.TOTALE).par_regime)
    travaillee = _carriere(simulateur, {}, niveau=0.8, naissance=1975)
    agirc = _compte(simulateur, travaillee, 2005, PartCotisation.TOTALE)
    (periode,) = [p for p in simulateur.catalogue["agirc"].periodes_actives(2005)
                  if p.assiette == "tranche_b"]
    appel = simulateur.scenario_actuel.valeurs_point.achat("agirc", 2005)[1]
    assiette = dict(agirc.par_regime)["agirc"] / periode.taux_cotisation_retraite
    assert verse["agirc"] == pytest.approx(0.7 * assiette * 0.08 * appel)
    assert _compte(simulateur, chomee, 2005, PartCotisation.SALARIALE).cotisation == 0.0


def test_le_salarie_agricole_n_a_rien_avant_1974(simulateur):
    """« Pour les salariés de l'agriculture ayant bénéficié d'un régime
    d'assurance chômage à compter du 1er avril 1974, seules les périodes
    indemnisées, à compter de cette date, sont validables » (guide,
    VII.3.1.3.1) : une année chômée de 1973 ne vaut rien, ni point ni
    versement, celle de 1974 vaut ses neuf derniers mois."""
    def carriere(interruptions):
        return simulateur.carriere_simple(
            annee_naissance=1940, sexe="H", affiliation="salarie_agricole",
            mois_naissance=1, age_debut=20, age_liquidation=60, niveau_salaire=1.0,
            profil_carriere="plat", interruptions=interruptions)

    def points(interruptions):
        resultat = simulateur.scenario_actuel.calculer(carriere(interruptions))
        detail = {p.regime: p for p in resultat.pensions_par_regime}["arrco"].detail
        return float(re.search(r"([\d,]+\.\d+) points", detail).group(1).replace(",", ""))

    assert points({1973: "chomage_indemnise"}) == pytest.approx(
        points({1973: "sans_activite"}), abs=0.01)
    assert _compte(simulateur, carriere({1973: "chomage_indemnise"}), 1973,
                   PartCotisation.TOTALE).cotisation == 0.0
    sans, chomee, pleine = (points({1974: "sans_activite"}), points({1974: "chomage_indemnise"}),
                            points({1974: "emploi"}))
    assert (chomee - sans) / (pleine - sans) == pytest.approx(0.75, abs=0.01)


def test_moins_de_trente_jours_avant_1974_ne_valent_rien(simulateur):
    """De 1967 à 1973, une période indemnisée de moins de trente jours ne se
    valide pas ; le modèle compte en mois, et la règle ne mord que sur une
    ligne plus courte."""
    from dataclasses import replace

    def courte(annee, fraction):
        carriere = simulateur.carriere_simple(
            annee_naissance=1945, sexe="H", affiliation="salarie_prive_non_cadre",
            mois_naissance=1, age_debut=19, age_liquidation=60, niveau_salaire=1.0,
            profil_carriere="plat", interruptions={annee: "chomage_indemnise"})
        return carriere.avec_lignes([
            replace(ligne, fraction_annee=fraction,
                    revenu_reference=ligne.revenu_reference * fraction)
            if ligne.annee == annee else ligne for ligne in carriere.lignes])

    assert _compte(simulateur, courte(1970, 20 / 365), 1970,
                   PartCotisation.TOTALE).cotisation == 0.0
    assert _compte(simulateur, courte(1970, 1 / 12), 1970,
                   PartCotisation.TOTALE).cotisation > 0.0
    assert _compte(simulateur, courte(1975, 20 / 365), 1975,
                   PartCotisation.TOTALE).cotisation > 0.0


def test_l_indemnisation_cesse_au_taux_plein(simulateur):
    """« Le revenu de remplacement cesse d'être versé » à qui a l'âge légal et
    la durée requise, et à qui atteint l'âge d'annulation de la décote
    (L. 5421-4 du code du travail) : les années de chômage qui commencent après
    ne valent ni trimestre ni point, et le scénario 1 sert ce que servirait la
    même carrière sans activité ces années-là."""
    from retraite_notionnelle.droit.ouvrir import fin_indemnisation, indemnisation_bornee

    def carriere(interruptions, naissance=1958, debut=20, depart=66):
        return simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H", affiliation="salarie_prive_cadre",
            mois_naissance=1, age_debut=debut, age_liquidation=depart,
            niveau_salaire=1.5, profil_carriere="plat", interruptions=interruptions)

    moteur = simulateur.scenario_actuel
    chomee = carriere({a: "chomage_indemnise" for a in range(2016, 2025)})
    coupure = fin_indemnisation(moteur, chomee)
    # La durée est là depuis longtemps : la coupure est l'âge légal, 62 ans.
    assert chomee.age_au(coupure) == 62
    bornee = indemnisation_bornee(moteur, chomee)
    assert {l.annee: l.type_periode for l in bornee.lignes if l.annee >= 2020} == {
        2020: "chomage_indemnise", 2021: "sans_activite", 2022: "sans_activite",
        2023: "sans_activite", 2024: "sans_activite"}
    # L'année de la coupure, entière, s'arrête au mois qui la précède.
    (coupee,) = [l for l in bornee.lignes if l.annee == coupure.annee]
    assert round(coupee.fraction_annee * 12) == coupure.mois - 1
    sans = carriere({**{a: "chomage_indemnise" for a in range(2016, 2021)},
                     **{a: "sans_activite" for a in range(2021, 2025)}})
    assert moteur.calculer(chomee).pension_annuelle == pytest.approx(
        moteur.calculer(sans).pension_annuelle)
    # Sans la durée, la coupure est l'âge d'annulation : 65 ans pour 1950.
    tardive = carriere({a: "chomage_indemnise" for a in range(2008, 2018)},
                       naissance=1950, debut=30, depart=67)
    assert tardive.age_au(fin_indemnisation(moteur, tardive)) == 65
    # Une carrière sans chômage au-delà reste la même.
    jeune = carriere({2000: "chomage_indemnise"})
    assert indemnisation_bornee(moteur, jeune) is jeune


def test_la_coupure_d_avant_1984(simulateur):
    """Avant le 1er avril 1983, l'indemnisation cessait à soixante-cinq ans :
    l'aide publique excluait « les personnes âgées de plus de soixante-cinq
    ans » (code du travail, R. 351-3, 1973). Depuis, à soixante ans pour qui a
    cent cinquante trimestres : l'Unédic les interrompt « à partir du
    01-04-1983 » (arrêté du 29 avril 1983), le décret n° 84-344 applique
    L. 351-19 « à compter du 01-04-1983 »."""
    from retraite_notionnelle.calendrier import DateMois
    from retraite_notionnelle.droit.ouvrir import fin_indemnisation

    def carriere(naissance, annees, depart):
        return simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H", affiliation="salarie_prive_non_cadre",
            mois_naissance=1, age_debut=18, age_liquidation=depart, niveau_salaire=1.0,
            profil_carriere="plat",
            interruptions={a: "chomage_indemnise" for a in annees})

    moteur = simulateur.scenario_actuel
    ancien = carriere(1912, range(1974, 1980), 67)
    assert ancien.age_au(fin_indemnisation(moteur, ancien)) == 65
    # Soixante ans en 1981 et la durée : la coupure attend le 1er avril 1983.
    assert fin_indemnisation(moteur, carriere(1921, range(1980, 1987), 65)) == DateMois(1983, 4)


def test_l_arrco_suit_la_date_de_la_rupture(simulateur):
    """L'Arrco valide aux taux obligatoires l'ASS qui suit une rupture d'avant
    le 1er juin 2000, quelle que soit l'année de l'allocation, et à 4 % celle
    qui suit une rupture d'après (guide, VII.3.1.6.2, 2, a) : le modèle prend
    la rupture au premier millésime du chômage qui précède l'ASS sans
    emploi."""
    def arrco(interruptions):
        return _points(simulateur, "arrco", interruptions, naissance=1950)

    rupture_1998 = {1998: "chomage_indemnise", 1999: "chomage_indemnise",
                    **{a: "chomage_solidarite" for a in range(2000, 2005)}}
    assurance = {a: "chomage_indemnise" for a in range(1998, 2005)}
    assert arrco(rupture_1998) == pytest.approx(arrco(assurance), abs=0.02)
    rupture_2001 = {2001: "chomage_indemnise", 2002: "chomage_indemnise",
                    2003: "chomage_solidarite", 2004: "chomage_solidarite"}
    assurance_2001 = {a: "chomage_indemnise" for a in range(2001, 2005)}
    assert arrco(rupture_2001) < arrco(assurance_2001) - 1


def test_la_preretraite_d_avant_1984_garde_les_regles_de_l_assurance(simulateur, regles):
    """Une convention du FNE conclue avant le 1er avril 1984 vaut des points
    « dans les mêmes conditions que les allocataires du régime d'assurance
    chômage » (guide, VII.3.1.6.2, 2, a), même pour les années d'après 1984 :
    le compte en porte ce que l'assurance versait. Une convention de 1984, ce
    que l'État verse, à ses taux. Le taux minimal de l'Agirc, de 8 % jusqu'en
    1994, rend les points égaux : c'est le versement qui les sépare."""
    avant = _carriere(simulateur, {a: "preretraite_fne" for a in range(1982, 1986)},
                      naissance=1926)
    debut = regles.debuts(avant.lignes)[(1985, "preretraite_fne")]
    assert debut == 1982
    assert regles.nature("preretraite_fne", 1985, debut) == "assurance"
    assurance = _carriere(simulateur, {a: "chomage_indemnise" for a in range(1982, 1986)},
                          naissance=1926)
    apres = _carriere(simulateur, {a: "preretraite_fne" for a in range(1984, 1986)},
                      naissance=1926)

    def verse(carriere):
        return _compte(simulateur, carriere, 1985, PartCotisation.TOTALE).cotisation

    assert verse(avant) == pytest.approx(verse(assurance))
    assert verse(apres) < verse(assurance) - 1


def test_la_coupure_respecte_le_releve(simulateur):
    """Un relevé de carrière qui porte des trimestres de chômage après le
    taux plein fait foi : la caisse les a validés, l'indemnisation a donc
    couru, et le modèle n'y retouche pas."""
    from retraite_notionnelle.carriere import Carriere, LigneRelevee
    from retraite_notionnelle.droit.ouvrir import indemnisation_bornee

    releve = ([LigneRelevee(a, "salarie_prive_cadre", 40000.0, 4) for a in range(1978, 2016)]
              + [LigneRelevee(a, "salarie_prive_cadre", 40000.0, 4, "chomage_indemnise")
                 for a in range(2016, 2024)])
    carriere = Carriere.depuis_releve(
        annee_naissance=1958, sexe="H", releve=releve, age_liquidation=66,
        macro=simulateur.macro)
    assert carriere.annees_declarees >= set(range(2016, 2024))
    assert indemnisation_bornee(simulateur.scenario_actuel, carriere) is carriere
