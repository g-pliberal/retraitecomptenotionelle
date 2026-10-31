"""Ce que les trois pages qui agrègent lisent du modèle, figé sous la référence.

``data/derive/agregats.json`` est fabriqué par ``scripts/construire_donnees.py``
depuis le 11 octobre 2026 (action 150) : Coût, Carrières types et Droits non
cotisés ne montrent plus que la référence, et ne calculent plus chez le
lecteur. Ces tests disent que la table porte ce que le modèle calcule, lue par
son seul lecteur, ``moteur/js/agregats.js`` (note de décision 0005), et
qu'elle refuse ce qu'elle ne porte pas. Le portage rend ses tableaux en
listes, que les tests comparent aux n-uplets du modèle.
"""

from __future__ import annotations

import json

import pytest

from retraite_notionnelle.avantages import carriere_variante
from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS, calculer_cas_types
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.donnees import agregats
from retraite_notionnelle.web.site import ErreurSite, disponible, module

#: Les systèmes que le site compare au système actuel, ceux que la table porte.
COMPARES = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

pytestmark = pytest.mark.skipif(not disponible(), reason="node absent : le site ne se lit pas")


@pytest.fixture(scope="module")
def table():
    """La table figée, ``data/derive/agregats.json``, lue par le portage."""
    brut = json.loads((RACINE_DONNEES / "derive" / "agregats.json").read_text(encoding="utf-8"))
    return module("agregats").charger_agregats(brut)


@pytest.fixture(scope="module")
def contexte():
    return Contexte()


@pytest.fixture(scope="module")
def grille(contexte):
    return calculer_cas_types(contexte.simulateur())


# -- les carrières types -------------------------------------------------------


def _cle(code: str, generation: int) -> str:
    """La clé d'une case de la grille dans la table, « code|génération »."""
    return f"{code}|{generation}"


def test_la_grille_figee_est_celle_que_le_modele_calcule(table, grille):
    figee = table.cas_types
    assert tuple(figee.generations) == GENERATIONS
    resultats = figee.resultats
    assert set(resultats) == {_cle(*cle) for cle in grille.resultats}
    assert dict(figee.echecs) == {_cle(*cle): echec for cle, echec in grille.echecs.items()}
    for cle, comparaison in grille.resultats.items():
        case = resultats[_cle(*cle)]
        assert case.carriere.annee_liquidation == comparaison.carriere.annee_liquidation
        for scenario in COMPARES:
            assert case.variation_totale(scenario) == comparaison.variation_totale(scenario)
            assert (case.carriere_de(scenario).annee_liquidation
                    == comparaison.carriere_de(scenario).annee_liquidation), (cle, scenario)


def test_les_cas_figes_sont_ceux_du_modele(table, contexte):
    figee = table.cas_types
    assert [cas.code for cas in figee.cas] == [cas.code for cas in CAS_TYPES]
    simulateur = contexte.simulateur()
    for cas in CAS_TYPES:
        fige = figee.cas_type(cas.code)
        assert (fige.libelle, fige.commentaire, tuple(fige.caisses)) == (
            cas.libelle, cas.commentaire, tuple(cas.caisses))
        for generation in GENERATIONS:
            assert fige.age_liquidation(generation) == cas.age_liquidation_pour(
                simulateur, generation), (cas.code, generation)


def test_la_table_ne_rend_pas_ce_qu_elle_ne_porte_pas(table):
    """Un zéro à la place d'une lecture absente tromperait la page sans bruit."""
    case = next(iter(table.cas_types.resultats.values()))
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        case.variation_totale("notionnel_prospectif")
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        table.cas_types.cas_type("inconnu")


def test_le_site_lit_la_table_figee():
    """Le paquet que le site charge porte la table telle que la fabrique l'a
    écrite : les pages lisent ce que ces tests confrontent au modèle."""
    paquet = json.loads((RACINE_DONNEES.parent / "moteur" / "donnees.json").read_text(
        encoding="utf-8"))
    assert paquet["agregats"] == json.loads(
        (RACINE_DONNEES / "derive" / "agregats.json").read_text(encoding="utf-8"))


# -- les avantages non contributifs --------------------------------------------


def test_les_avantages_figes_sont_ceux_que_le_modele_calcule(table, contexte):
    modele = contexte.avantages()
    fige = table.avantages
    assert (tuple(fige.lignes), tuple(fige.lignes_modele)) == (
        tuple(modele.lignes), tuple(modele.lignes_modele))
    assert (fige.refus, fige.ponderation) == (modele.refus, modele.ponderation)
    assert [annee.annee for annee in fige.annees] == [annee.annee for annee in modele.annees]
    for figee, calculee in zip(fige.annees, modele.annees):
        assert figee.observee == calculee.observee
        assert (figee.lignes, figee.modele, figee.anticipees) == (
            calculee.lignes, calculee.modele, calculee.anticipees), figee.annee
        assert (figee.gratuit, figee.gratuit_modele, figee.anticipee) == (
            calculee.gratuit, calculee.gratuit_modele, calculee.anticipee), figee.annee
    assert fige.derniere.annee == modele.derniere.annee


def test_la_nomenclature_figee_est_celle_du_modele(table):
    """Ce que la page Droits non cotisés lit de la nomenclature du modèle, et
    qu'elle tenait du portage du coût : les lignes publiées, les avantages
    mesurés par retrait, les motifs d'un départ anticipé, dans leur ordre."""
    from retraite_notionnelle.avantages import (
        LIBELLES_MOTIFS, LIGNES_LUES, MOTIFS, NEUTRALISATIONS,
    )

    fige = table.avantages
    assert tuple(fige.lignes_lues) == LIGNES_LUES
    assert tuple(fige.neutralisations) == tuple(n.code for n in NEUTRALISATIONS)
    assert tuple(fige.motifs) == MOTIFS
    assert fige.libelles_motifs == LIBELLES_MOTIFS


# -- le classement de l'emploi --------------------------------------------------


def test_les_departs_compares_sont_ceux_que_le_modele_simule(table, contexte):
    """Les deux départs que Droits non cotisés compare, tels que la page les
    choisit (``CLASSEMENT_COMPARE``)."""
    choisis = table.classement
    assert dict(module("pages").CLASSEMENT_COMPARE) == {
        "cas": choisis.cas, "age": choisis.age, "declassement": choisis.declassement,
        "generations": list(choisis.generations)}
    simulateur = contexte.simulateur()
    cas = next(cas for cas in CAS_TYPES if cas.code == choisis.cas)
    for generation in choisis.generations:
        for depart, affiliation in zip(choisis.departs(generation),
                                       (None, choisis.declassement)):
            actuel = simulateur.simuler(carriere_variante(
                simulateur, cas, generation, choisis.age, affiliation)).actuel
            assert (depart.pension_annuelle, depart.trimestres_requis) == (
                actuel.pension_annuelle, actuel.trimestres_requis), (generation, affiliation)


# -- le coût agrégé ------------------------------------------------------------


@pytest.fixture(scope="module")
def cout(contexte):
    return contexte.cout()


@pytest.fixture(scope="module")
def montres():
    return tuple(module("pages").SCENARIOS_MONTRES)


@pytest.fixture(scope="module")
def bilan():
    return tuple(module("pages").SYSTEMES_BILAN)


def _memes_champs(fige, calcule, champs, ou):
    for champ in champs:
        if hasattr(fige, champ):
            assert getattr(fige, champ) == getattr(calcule, champ), (ou, champ)


def test_le_solde_fige_est_celui_que_le_modele_calcule(table, cout, montres, bilan):
    fige = table.cout.solde
    solde = cout.solde
    assert [ligne.annee for ligne in fige.annees] == [ligne.annee for ligne in solde.annees]
    assert (fige.premiere_annee_projetee, fige.derniere_annee_observee) == (
        solde.premiere_annee_projetee, solde.derniere_annee_observee)
    for figee, calculee in zip(fige.annees, solde.annees):
        _memes_champs(figee, calculee, agregats.CHAMPS_SOLDE_ANNUEL, figee.annee)
        assert figee.recette_par_assiette == calculee.recette_par_assiette
        assert figee.ressources_meur() == calculee.ressources_meur()
        for accesseur, _, du_bilan in agregats.PAR_SYSTEME_SOLDE_ANNUEL:
            for scenario in (bilan if du_bilan else montres):
                assert getattr(figee, accesseur)(scenario) == getattr(calculee, accesseur)(
                    scenario), (figee.annee, accesseur, scenario)
    for scenario in montres:
        assert fige.premiere_annee_equilibree(scenario) == solde.premiere_annee_equilibree(
            scenario)
        for debut in (solde.premiere_annee, solde.premiere_annee_projetee, 2040):
            assert fige.solde_moyen(scenario, debut, solde.derniere_annee) == (
                solde.solde_moyen(scenario, debut, solde.derniere_annee))
    derive = table.cout.solde_derive
    for figee, calculee in zip(derive.annees, cout.solde_derive.annees, strict=True):
        assert figee.coefficient("notionnel_liberal") == calculee.coefficient(
            "notionnel_liberal")
    assert derive.solde_moyen("notionnel_liberal", 2026, 2070) == (
        cout.solde_derive.solde_moyen("notionnel_liberal", 2026, 2070))


def test_la_table_porte_le_taux_effectif_et_la_depense_nette(table, cout, montres):
    """Chaque année du bilan figé porte le taux que les prélèvements sociaux
    prennent à la masse des pensions, l'année publiée qui le donne, et la
    dépense nette de chaque système montré : ce que la page Coût mettra à côté
    de la brute (action 138, étape 3)."""
    for figee, calculee in zip(table.cout.solde.annees, cout.solde.annees, strict=True):
        assert (figee.taux_effectif, figee.annee_taux_effectif) == (
            calculee.taux_effectif, calculee.annee_taux_effectif), figee.annee
        for scenario in montres:
            assert figee.depense_nette(scenario) == calculee.depense_nette(scenario), (
                figee.annee, scenario)
    assert table.cout.solde.annee(2070).annee_taux_effectif == 2022


def test_le_passe_et_l_avenir_figes_sont_ceux_que_le_modele_calcule(table, cout, montres):
    from retraite_notionnelle.cout import COMPOSANTE_GARANTIE, masse_du_scenario

    fige = table.cout
    avec_garantie = (*montres, COMPOSANTE_GARANTIE)
    assert (fige.premiere_annee, fige.annee_euros, tuple(fige.generations)) == (
        cout.premiere_annee, cout.annee_euros, tuple(cout.generations))
    # Par cas type de la page : l'agent sédentaire de la CNRACL compte avec
    # l'actif dont il porte le code.
    from retraite_notionnelle.donnees.agregats import _par_cas_type_affiche

    assert (fige.poids, fige.poids_cotisants) == (
        _par_cas_type_affiche(cout.poids), _par_cas_type_affiche(cout.poids_cotisants))
    assert set(fige.poids) == {cas.code for cas in CAS_TYPES}
    assert tuple(fige.confondus_avec_actuel()) == tuple(cout.confondus_avec_actuel())
    assert fige.cumul_observe() == cout.cumul_observe()
    for figee, calculee in zip(fige.annees, cout.annees, strict=True):
        _memes_champs(figee, calculee, agregats.CHAMPS_COUT_ANNUEL, figee.annee)
        assert (figee.garantie is None) == (calculee.garantie is None)
        if calculee.garantie is not None:
            assert figee.garantie.facteur == calculee.garantie.facteur
        for scenario in avec_garantie:
            assert figee.cout(scenario) == calculee.cout(scenario)
            assert figee.cout_constants(scenario) == calculee.cout_constants(scenario)
            assert figee.part_pib_de(scenario) == masse_du_scenario(
                calculee.part_pib_pensions, calculee.part_derives,
                calculee.rapports[scenario], scenario, calculee.reversion_servie,
                calculee.reforme_en_vigueur)
    for scenario in avec_garantie:
        assert fige.cumul(scenario) == cout.cumul(scenario)
        assert fige.avenir.cumul(scenario) == cout.avenir.cumul(scenario)
    avenir = cout.avenir
    assert fige.avenir.cumul_reprises() == avenir.cumul_reprises()
    for scenario in montres[1:]:
        assert fige.avenir.ecart_cumule(scenario) == avenir.ecart_cumule(scenario)
    depuis = avenir.premiere_annee_projetee
    assert {annee: tuple(valeurs) for annee, valeurs in fige.avenir.decomposition(
        depuis).items()} == {annee: tuple(valeurs) for annee, valeurs in avenir.decomposition(
            depuis).items()}
    for figee, calculee in zip(fige.avenir.annees, avenir.annees, strict=True):
        _memes_champs(figee, calculee, agregats.CHAMPS_AVENIR_ANNUEL, figee.annee)
        for scenario in avec_garantie:
            assert figee.cout_constants(scenario) == calculee.cout_constants(scenario)
            assert figee.part_pib(scenario) == calculee.part_pib(scenario)
        assert figee.part_pib_derive("notionnel_liberal") == calculee.part_pib_derive(
            "notionnel_liberal")
        assert (figee.reprises_constants(), figee.reprises(), figee.part_pib_reprises(),
                figee.garantie_nette_constants()) == (
            calculee.reprises_constants(), calculee.reprises(),
            calculee.part_pib_reprises(), calculee.garantie_nette_constants())
        if calculee.garantie is not None:
            _memes_champs(figee.garantie, calculee.garantie, agregats.CHAMPS_GARANTIE,
                          figee.annee)
        if calculee.pilier is not None:
            _memes_champs(figee.pilier, calculee.pilier, agregats.CHAMPS_PILIER, figee.annee)
            assert figee.pilier.niveaux(1234.5) == calculee.pilier.niveaux(1234.5)


def test_la_dette_figee_est_celle_que_le_modele_calcule(table, contexte, cout, montres):
    from retraite_notionnelle.cout import calculer_dette

    fige = table.cout.dette
    dette = cout.dette
    assert [ligne.annee for ligne in fige.annees] == [ligne.annee for ligne in dette.annees]
    # La table écrit ses années en clés de texte, que le modèle tient en entiers.
    observee = {int(annee): valeur for annee, valeur in fige.dette_publique_observee.items()}
    assert (fige.annee_depart, fige.date_courbe, fige.derniere_annee_cotee,
            observee, fige.dette_publique_depart) == (
        dette.annee_depart, dette.date_courbe, dette.derniere_annee_cotee,
        dette.dette_publique_observee, dette.dette_publique_depart)
    for scenario in montres:
        assert fige.horizon(scenario) == dette.horizon(scenario)
        assert fige.cumul_soldes(scenario) == dette.cumul_soldes(scenario)
        assert table.cout.dette_derive.horizon(scenario) == cout.dette_derive.horizon(
            scenario)
        for ligne in dette.annees:
            assert fige.stock(scenario, ligne.annee) == dette.stock(scenario, ligne.annee)
            assert fige.dette_publique(scenario, ligne.annee) == dette.dette_publique(
                scenario, ligne.annee)
            assert fige.annee(ligne.annee).interet(scenario) == ligne.interet(scenario)
    ecart = module("pages").ECART_TAUX_DETTE
    for decalage in (-ecart, ecart):
        decalee = calculer_dette(cout.solde, cout.avenir,
                                 contexte.simulateur().courbe_taux, decalage)
        for scenario in montres:
            assert table.cout.dette_decalee(decalage).horizon(scenario) == (
                decalee.horizon(scenario))


def test_le_taux_de_tva_requis_est_celui_du_modele(table, contexte, cout):
    """Il ne s'écrit que si la TVA est réformée, ce que la référence ne fait
    pas : la table porte alors (0, 0), comme le modèle."""
    from retraite_notionnelle.cout import taux_tva_requis
    from retraite_notionnelle.donnees.tva import AssietteTva

    assert tuple(table.cout.taux_tva_requis()) == tuple(taux_tva_requis(
        cout.solde, contexte.base, AssietteTva(RACINE_DONNEES)))


def test_la_cle_de_la_garantie_est_celle_du_modele():
    from retraite_notionnelle.cout import COMPOSANTE_GARANTIE

    assert module("agregats").COMPOSANTE_GARANTIE == COMPOSANTE_GARANTIE


def test_le_cout_fige_refuse_ce_qu_il_ne_porte_pas(table):
    ligne = table.cout.solde.annee(2030)
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        ligne.postes_ressources("notionnel_retroactif")
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        table.cout.dette_decalee(0.02)
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        table.cout.avenir.decomposition(1990)


# -- le coût sous les variantes de population de l'INSEE ------------------------


def _sous_la_variante(contexte, composante, hypothese):
    """Le coût que le modèle calcule sous une hypothèse d'une composante."""
    from retraite_notionnelle import memoire

    if composante == "esperance_vie":
        return memoire.cout(contexte.base.avec(hypothese_esperance_vie=hypothese))
    if hypothese == "centrale":
        return memoire.cout(contexte.base)
    return memoire.cout(contexte.base, demographie=f"{composante}_{hypothese}")


COMPOSANTES = ("esperance_vie", "fecondite", "migrations")


@pytest.mark.parametrize("composante", COMPOSANTES)
def test_le_cout_sous_chaque_variante_est_celui_du_modele(table, contexte, montres, composante):
    """La table porte, sous chacune des trois hypothèses de l'INSEE d'une
    composante (action 138, étape 7), ce que le modèle calcule sous elle : la
    dépense du bilan aux années que la page cite, le solde à l'horizon, le
    solde moyen projeté. Le système actuel paie plus quand la longévité monte,
    quand la fécondité ou les migrations baissent ; la proposition ne bouge
    presque pas à l'horizon : son diviseur absorbe la longévité, et ses comptes
    et ses pensions, indexés sur la masse salariale de la variante, suivent le
    PIB sous la fécondité et les migrations. Ce qui en reste, moins d'un
    dixième de point, est le stock liquidé avant la bascule, qui garde les
    prix."""
    figee = getattr(table, composante)
    assert tuple(figee.hypotheses) == ("basse", "centrale", "haute")
    assert tuple(figee.annees) == tuple(module("pages").ANNEES_ESPERANCE_VIE)
    for hypothese in figee.hypotheses:
        solde = _sous_la_variante(contexte, composante, hypothese).solde
        assert (figee.premiere_annee, figee.derniere_annee) == (
            solde.premiere_annee_projetee, solde.derniere_annee)
        for scenario in montres:
            for annee in figee.annees:
                assert figee.part_pib(hypothese, scenario, annee) == solde.annee(
                    annee).depense(scenario), (hypothese, scenario, annee)
            assert figee.solde(hypothese, scenario) == solde.annee(
                solde.derniere_annee).solde(scenario)
            assert figee.solde_moyen(hypothese, scenario) == solde.solde_moyen(
                scenario, solde.premiere_annee_projetee, solde.derniere_annee)
    horizon = figee.derniere_annee
    actuel = [figee.part_pib(h, "actuel", horizon) for h in figee.hypotheses]
    liberal = [figee.part_pib(h, "notionnel_liberal", horizon) for h in figee.hypotheses]
    if composante == "esperance_vie":
        assert actuel == sorted(actuel)
    else:
        assert actuel == sorted(actuel, reverse=True)
        assert liberal == sorted(liberal, reverse=True)
    assert max(liberal) - min(liberal) < 0.001
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        figee.solde("tres_haute", "actuel")
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        figee.part_pib("haute", "actuel", 2051)


# -- le bilan du compte, à la manière suédoise -----------------------------------


@pytest.fixture(scope="module")
def bilans(table, contexte, montres):
    from retraite_notionnelle.bilan_compte import bilans_gardes

    return bilans_gardes(contexte, table.bilan_compte.annee, montres)


def test_le_bilan_du_compte_fige_est_celui_que_le_modele_calcule(table, bilans, montres):
    """La table porte le bilan du compte de chaque système (action 138, étape
    19) à la dernière année dont le COR publie les réserves, et leur rendement
    comptable cette année-là : chaque champ de ``BilanCompte`` et chaque
    indicateur qu'il en tire, tels que ``bilan_compte`` les calcule. Le lecteur
    n'en refait aucune opération, la durée de rotation, l'actif, le ratio et
    les taux d'équilibre compris : il les rend."""
    from dataclasses import fields

    from retraite_notionnelle.bilan_compte import BilanCompte, Reserves

    assert {champ.name for champ in fields(BilanCompte)} - {"annee", "scenario"} <= set(
        agregats.CHAMPS_BILAN_COMPTE)
    fige = table.bilan_compte
    reserves = Reserves.charger(RACINE_DONNEES)
    assert fige.annee == reserves.derniere_annee()
    assert fige.rendement == reserves.rendement(fige.annee)
    assert set(bilans) == set(montres)
    for scenario in montres:
        systeme = fige.systeme(scenario)
        for champ in agregats.CHAMPS_BILAN_COMPTE:
            assert getattr(systeme, champ) == getattr(bilans[scenario], champ), (
                scenario, champ)
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        fige.systeme("notionnel_bascule")


# -- les leviers de l'équilibre, à la manière du COR ------------------------------


@pytest.fixture(scope="module")
def leviers(contexte, montres):
    from retraite_notionnelle.leviers import leviers_du_modele

    pages = module("pages")
    return {scenario: leviers_du_modele(contexte.base, scenario,
                                        soldes_vises=tuple(pages.SOLDES_VISES),
                                        annees_visees=tuple(pages.ANNEES_LEVIERS))
            for scenario in montres}


def test_les_leviers_figes_sont_ceux_que_le_modele_calcule(table, leviers, montres):
    """La table porte les trois leviers qui équilibreraient chaque système
    (action 138, étape 3) — la pension, le taux de prélèvement, l'âge —,
    chaque année de 2025 à 2070, et ses écarts sur les horizons du COR, le
    pension gap et le tax gap, tels que ``leviers.leviers_du_modele`` les
    calcule. Un âge que nul recul des bornes cherchées ne donne reste
    ``None`` : le système 2, qui encaisse plus qu'il ne sert. Puis le
    solveur inverse (action 138, étape 10) : pour chaque solde que la page
    Coût propose de viser (``SOLDES_VISES``), les leviers qui y portent chaque
    système aux années qu'elle montre (``ANNEES_LEVIERS``) ; viser l'équilibre
    redonne ses leviers. Le lecteur n'en refait aucune opération."""
    from dataclasses import fields

    from retraite_notionnelle.leviers import (
        DEBUT_AJUSTEMENT, HORIZONS_COR, RECUL_MAXIMAL, RECUL_MINIMAL, EcartsSurHorizon,
        Leviers,
    )

    assert {champ.name for champ in fields(Leviers)} - {"annee"} == set(
        agregats.CHAMPS_LEVIERS)
    assert {champ.name for champ in fields(EcartsSurHorizon)} - {"debut", "fin"} == set(
        agregats.CHAMPS_ECARTS_HORIZON)
    fige = table.leviers
    annees, annees_visees = tuple(fige.annees), tuple(fige.annees_visees)
    soldes_vises = tuple(fige.soldes_vises)
    assert fige.debut == DEBUT_AJUSTEMENT
    assert tuple(fige.horizons) == HORIZONS_COR
    assert tuple(fige.recul) == (RECUL_MINIMAL, RECUL_MAXIMAL)
    assert set(leviers) == set(montres)
    for scenario in montres:
        assert annees == tuple(sorted(leviers[scenario].annuels)), scenario
        for annee, ligne in leviers[scenario].annuels.items():
            lu = fige.annee(scenario, annee)
            for champ in agregats.CHAMPS_LEVIERS:
                assert getattr(lu, champ) == getattr(ligne, champ), (scenario, annee, champ)
        for fin, ecart in leviers[scenario].horizons.items():
            lu = fige.horizon(scenario, fin)
            for champ in agregats.CHAMPS_ECARTS_HORIZON:
                assert getattr(lu, champ) == getattr(ecart, champ), (scenario, fin, champ)
        assert tuple(leviers[scenario].vises) == soldes_vises, scenario
        for solde, annuels in leviers[scenario].vises.items():
            assert tuple(sorted(annuels)) == annees_visees, (scenario, solde)
            for annee, ligne in annuels.items():
                lu = fige.vise(scenario, solde, annee)
                for champ in agregats.CHAMPS_LEVIERS:
                    assert getattr(lu, champ) == getattr(ligne, champ), (
                        scenario, solde, annee, champ)
        for annee in annees_visees:
            equilibre, vise = fige.annee(scenario, annee), fige.vise(scenario, 0.0, annee)
            for champ in agregats.CHAMPS_LEVIERS:
                assert getattr(vise, champ) == getattr(equilibre, champ), (scenario, annee, champ)
    pages = module("pages")
    assert soldes_vises == tuple(pages.SOLDES_VISES)
    assert annees_visees == tuple(pages.ANNEES_LEVIERS)
    assert fige.annee("notionnel_retroactif", annees[-1]).age is None
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        fige.annee("notionnel_bascule", annees[-1])
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        fige.annee("actuel", annees[-1] + 1)
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        fige.horizon("actuel", 2040)
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        fige.vise("actuel", 0.0025, annees_visees[-1])
    with pytest.raises(ErreurSite, match="absent de la table figée"):
        fige.vise("actuel", 0.0, annees_visees[-1] + 1)
