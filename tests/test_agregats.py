"""Ce que les trois pages qui agrègent lisent du modèle, figé sous la référence.

``data/derive/agregats.json`` est fabriqué par ``scripts/construire_donnees.py``
depuis le 11 octobre 2026 (action 150) : Coût, Carrières types et Droits non
cotisés ne montrent plus que la référence, et ne calculent plus chez le
lecteur. Ces tests disent que la table porte ce que le modèle calcule, que les
deux lecteurs — ``donnees/agregats.py`` et ``moteur/js/agregats.js`` — en
lisent la même chose, et qu'elle refuse ce qu'elle ne porte pas.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.avantages import carriere_variante
from retraite_notionnelle.castypes import CAS_TYPES, GENERATIONS, calculer_cas_types
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.donnees import agregats
from retraite_notionnelle.donnees.agregats import charger_agregats
from retraite_notionnelle.web.site import disponible, module, site

AGREGATS = charger_agregats(RACINE_DONNEES)

#: Les systèmes que le site compare au système actuel, ceux que la table porte.
COMPARES = ("notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal")

sans_node = pytest.mark.skipif(not disponible(), reason="node absent : le site ne se lit pas")


@pytest.fixture(scope="module")
def contexte():
    return Contexte()


@pytest.fixture(scope="module")
def grille(contexte):
    return calculer_cas_types(contexte.simulateur())


# -- les carrières types -------------------------------------------------------


def test_la_grille_figee_est_celle_que_le_modele_calcule(grille):
    figee = AGREGATS.cas_types
    assert figee.generations == GENERATIONS
    assert set(figee.resultats) == set(grille.resultats)
    assert figee.echecs == grille.echecs
    for cle, comparaison in grille.resultats.items():
        case = figee.resultats[cle]
        assert case.carriere.annee_liquidation == comparaison.carriere.annee_liquidation
        for scenario in COMPARES:
            assert case.variation_totale(scenario) == comparaison.variation_totale(scenario)
            assert (case.carriere_de(scenario).annee_liquidation
                    == comparaison.carriere_de(scenario).annee_liquidation), (cle, scenario)


def test_les_cas_figes_sont_ceux_du_modele(contexte):
    figee = AGREGATS.cas_types
    assert [cas.code for cas in figee.cas] == [cas.code for cas in CAS_TYPES]
    simulateur = contexte.simulateur()
    for cas in CAS_TYPES:
        fige = figee.cas_type(cas.code)
        assert (fige.libelle, fige.commentaire, fige.caisses) == (
            cas.libelle, cas.commentaire, cas.caisses)
        for generation in GENERATIONS:
            assert fige.age_liquidation(generation) == cas.age_liquidation_pour(
                simulateur, generation), (cas.code, generation)


def test_la_table_ne_rend_pas_ce_qu_elle_ne_porte_pas():
    """Un zéro à la place d'une lecture absente tromperait la page sans bruit."""
    case = next(iter(AGREGATS.cas_types.resultats.values()))
    with pytest.raises(KeyError, match="absent de la table figée"):
        case.variation_totale("notionnel_prospectif")
    with pytest.raises(KeyError, match="absent de la table figée"):
        AGREGATS.cas_types.cas_type("inconnu")


@sans_node
def test_les_deux_lecteurs_lisent_la_meme_grille():
    js = site().contexte.cas_types()
    figee = AGREGATS.cas_types
    assert tuple(js.generations) == figee.generations
    # Les tables du portage se lisent, d'ici, en dictionnaires.
    assert len(js.echecs) == len(figee.echecs)
    assert len(js.resultats) == len(figee.resultats)
    for (code, generation), case in figee.resultats.items():
        lue = js.resultats[f"{code}|{generation}"]
        assert lue.carriere.annee_liquidation == case.carriere.annee_liquidation
        for scenario in COMPARES:
            assert lue.variation_totale(scenario) == case.variation_totale(scenario)
            assert (lue.carriere_de(scenario).annee_liquidation
                    == case.carriere_de(scenario).annee_liquidation)
    for cas in figee.cas:
        lu = js.cas_type(cas.code)
        assert (lu.libelle, lu.commentaire) == (cas.libelle, cas.commentaire)
        assert [lu.age_liquidation(generation) for generation in figee.generations] == [
            cas.age_liquidation(generation) for generation in figee.generations]


# -- les avantages non contributifs --------------------------------------------


def test_les_avantages_figes_sont_ceux_que_le_modele_calcule(contexte):
    modele = contexte.avantages()
    fige = AGREGATS.avantages
    assert (fige.lignes, fige.lignes_modele) == (modele.lignes, modele.lignes_modele)
    assert (fige.refus, fige.ponderation) == (modele.refus, modele.ponderation)
    assert [annee.annee for annee in fige.annees] == [annee.annee for annee in modele.annees]
    for figee, calculee in zip(fige.annees, modele.annees):
        assert figee.observee == calculee.observee
        assert (figee.lignes, figee.modele, figee.anticipees) == (
            calculee.lignes, calculee.modele, calculee.anticipees), figee.annee
        assert (figee.gratuit, figee.gratuit_modele, figee.anticipee) == (
            calculee.gratuit, calculee.gratuit_modele, calculee.anticipee), figee.annee
    assert fige.derniere.annee == modele.derniere.annee


def test_la_nomenclature_figee_est_celle_du_modele():
    """Ce que la page Droits non cotisés lit de la nomenclature du modèle, et
    qu'elle tenait du portage du coût : les lignes publiées, les avantages
    mesurés par retrait, les motifs d'un départ anticipé, dans leur ordre."""
    from retraite_notionnelle.avantages import (
        LIBELLES_MOTIFS, LIGNES_LUES, MOTIFS, NEUTRALISATIONS,
    )

    fige = AGREGATS.avantages
    assert fige.lignes_lues == LIGNES_LUES
    assert fige.neutralisations == tuple(n.code for n in NEUTRALISATIONS)
    assert fige.motifs == MOTIFS
    assert fige.libelles_motifs == LIBELLES_MOTIFS


@sans_node
def test_les_deux_lecteurs_lisent_les_memes_avantages():
    js = site().contexte.avantages()
    fige = AGREGATS.avantages
    assert (tuple(js.lignes), tuple(js.lignes_modele)) == (fige.lignes, fige.lignes_modele)
    assert dict(js.refus) == fige.refus
    assert [annee.annee for annee in js.annees] == [annee.annee for annee in fige.annees]
    derniere = js.derniere
    assert dict(derniere.lignes) == fige.derniere.lignes
    assert (derniere.gratuit, derniere.gratuit_modele, derniere.anticipee) == (
        fige.derniere.gratuit, fige.derniere.gratuit_modele, fige.derniere.anticipee)


# -- le classement de l'emploi --------------------------------------------------


def test_les_departs_compares_sont_ceux_que_le_modele_simule(contexte):
    """Les deux départs que Droits non cotisés compare, tels que la page les
    choisit (``CLASSEMENT_COMPARE``)."""
    choisis = AGREGATS.classement
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


@sans_node
def test_les_deux_lecteurs_lisent_les_memes_departs():
    js = site().contexte.agregats().classement
    fige = AGREGATS.classement
    assert list(js.generations) == list(fige.generations)
    for generation in fige.generations:
        assert [(d.pension_annuelle, d.trimestres_requis) for d in js.departs(generation)] == [
            (d.pension_annuelle, d.trimestres_requis) for d in fige.departs(generation)]


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


def test_le_solde_fige_est_celui_que_le_modele_calcule(cout, montres, bilan):
    fige = AGREGATS.cout.solde
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
    derive = AGREGATS.cout.solde_derive
    for figee, calculee in zip(derive.annees, cout.solde_derive.annees, strict=True):
        assert figee.coefficient("notionnel_liberal") == calculee.coefficient(
            "notionnel_liberal")
    assert derive.solde_moyen("notionnel_liberal", 2026, 2070) == (
        cout.solde_derive.solde_moyen("notionnel_liberal", 2026, 2070))


def test_la_table_porte_le_taux_effectif_et_la_depense_nette(cout, montres):
    """Chaque année du bilan figé porte le taux que les prélèvements sociaux
    prennent à la masse des pensions, l'année publiée qui le donne, et la
    dépense nette de chaque système montré : ce que la page Coût mettra à côté
    de la brute (action 138, étape 3)."""
    for figee, calculee in zip(AGREGATS.cout.solde.annees, cout.solde.annees, strict=True):
        assert (figee.taux_effectif, figee.annee_taux_effectif) == (
            calculee.taux_effectif, calculee.annee_taux_effectif), figee.annee
        for scenario in montres:
            assert figee.depense_nette(scenario) == calculee.depense_nette(scenario), (
                figee.annee, scenario)
    assert AGREGATS.cout.solde.annee(2070).annee_taux_effectif == 2022


def test_le_passe_et_l_avenir_figes_sont_ceux_que_le_modele_calcule(cout, montres):
    from retraite_notionnelle.cout import COMPOSANTE_GARANTIE, masse_du_scenario

    fige = AGREGATS.cout
    avec_garantie = (*montres, COMPOSANTE_GARANTIE)
    assert (fige.premiere_annee, fige.annee_euros, fige.generations) == (
        cout.premiere_annee, cout.annee_euros, cout.generations)
    # Par cas type de la page : l'agent sédentaire de la CNRACL compte avec
    # l'actif dont il porte le code.
    from retraite_notionnelle.donnees.agregats import _par_cas_type_affiche

    assert (fige.poids, fige.poids_cotisants) == (
        _par_cas_type_affiche(cout.poids), _par_cas_type_affiche(cout.poids_cotisants))
    assert set(fige.poids) == {cas.code for cas in CAS_TYPES}
    assert fige.confondus_avec_actuel() == cout.confondus_avec_actuel()
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
    assert fige.avenir.decomposition(depuis) == avenir.decomposition(depuis)
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


def test_la_dette_figee_est_celle_que_le_modele_calcule(contexte, cout, montres):
    from retraite_notionnelle.cout import calculer_dette

    fige = AGREGATS.cout.dette
    dette = cout.dette
    assert [ligne.annee for ligne in fige.annees] == [ligne.annee for ligne in dette.annees]
    assert (fige.annee_depart, fige.date_courbe, fige.derniere_annee_cotee,
            fige.dette_publique_observee, fige.dette_publique_depart) == (
        dette.annee_depart, dette.date_courbe, dette.derniere_annee_cotee,
        dette.dette_publique_observee, dette.dette_publique_depart)
    for scenario in montres:
        assert fige.horizon(scenario) == dette.horizon(scenario)
        assert fige.cumul_soldes(scenario) == dette.cumul_soldes(scenario)
        assert AGREGATS.cout.dette_derive.horizon(scenario) == cout.dette_derive.horizon(
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
            assert AGREGATS.cout.dette_decalee(decalage).horizon(scenario) == (
                decalee.horizon(scenario))


def test_le_taux_de_tva_requis_est_celui_du_modele(contexte, cout):
    """Il ne s'écrit que si la TVA est réformée, ce que la référence ne fait
    pas : la table porte alors (0, 0), comme le modèle."""
    from retraite_notionnelle.cout import taux_tva_requis
    from retraite_notionnelle.donnees.tva import AssietteTva

    assert AGREGATS.cout.taux_tva_requis() == taux_tva_requis(
        cout.solde, contexte.base, AssietteTva(RACINE_DONNEES))


@sans_node
def test_la_cle_de_la_garantie_est_celle_du_modele():
    from retraite_notionnelle.cout import COMPOSANTE_GARANTIE

    assert module("agregats").COMPOSANTE_GARANTIE == COMPOSANTE_GARANTIE


def test_le_cout_fige_refuse_ce_qu_il_ne_porte_pas():
    ligne = AGREGATS.cout.solde.annee(2030)
    with pytest.raises(KeyError, match="absent de la table figée"):
        ligne.postes_ressources("notionnel_retroactif")
    with pytest.raises(KeyError, match="absent de la table figée"):
        AGREGATS.cout.dette_decalee(0.02)
    with pytest.raises(KeyError, match="absent de la table figée"):
        AGREGATS.cout.avenir.decomposition(1990)


@sans_node
def test_les_deux_lecteurs_lisent_le_meme_cout(montres, bilan):
    """Le lecteur du site rend, sous les noms du portage, ce que rend celui du
    Python : chaque accesseur d'une année sur dix, chaque système."""
    js = site().contexte.cout()
    fige = AGREGATS.cout
    assert list(js.generations) == list(fige.generations)
    assert js.anneeEuros == fige.annee_euros
    for scenario in montres:
        assert js.cumul(scenario) == fige.cumul(scenario)
        assert js.dette.horizon(scenario) == fige.dette.horizon(scenario)
        assert js.solde.soldeMoyen(scenario, 2026, 2070) == fige.solde.solde_moyen(
            scenario, 2026, 2070)
    for annee in range(fige.solde.premiere_annee, fige.solde.derniere_annee + 1, 10):
        lue, figee = js.solde.annee(annee), fige.solde.annee(annee)
        for scenario in montres:
            assert (lue.coefficient(scenario), lue.depense(scenario), lue.solde(scenario),
                    lue.ressources_de(scenario), lue.depense_nette(scenario)) == (
                figee.coefficient(scenario), figee.depense(scenario),
                figee.solde(scenario), figee.ressources_de(scenario),
                figee.depense_nette(scenario))
        for scenario in bilan:
            assert dict(lue.postes_ressources(scenario)) == figee.postes_ressources(scenario)
        assert lue.facteur_assiette == figee.facteur_assiette
        assert (lue.taux_effectif, lue.annee_taux_effectif) == (
            figee.taux_effectif, figee.annee_taux_effectif)
    for annee in range(fige.avenir.premiere_annee, fige.avenir.derniere_annee + 1, 10):
        lue, figee = js.avenir.annee(annee), fige.avenir.annee(annee)
        for scenario in montres:
            assert lue.part_pib(scenario) == figee.part_pib(scenario)
        assert lue.reprises_constants() == figee.reprises_constants()
        if figee.pilier is not None:
            assert dict(lue.pilier.niveaux(1000.0)) == figee.pilier.niveaux(1000.0)


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
def test_le_cout_sous_chaque_variante_est_celui_du_modele(contexte, montres, composante):
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
    figee = getattr(AGREGATS, composante)
    assert figee.hypotheses == ("basse", "centrale", "haute")
    assert figee.annees == tuple(module("pages").ANNEES_ESPERANCE_VIE)
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
    with pytest.raises(KeyError, match="absent de la table figée"):
        figee.solde("tres_haute", "actuel")
    with pytest.raises(KeyError, match="absent de la table figée"):
        figee.part_pib("haute", "actuel", 2051)


@sans_node
@pytest.mark.parametrize("composante", COMPOSANTES)
def test_les_deux_lecteurs_lisent_les_memes_variantes(montres, composante):
    js = getattr(site().contexte.agregats(),
                 {"esperance_vie": "esperanceVie"}.get(composante, composante))
    figee = getattr(AGREGATS, composante)
    assert tuple(js.hypotheses) == figee.hypotheses
    assert tuple(js.annees) == figee.annees
    assert (js.premiereAnnee, js.derniereAnnee) == (figee.premiere_annee,
                                                    figee.derniere_annee)
    for hypothese in figee.hypotheses:
        for scenario in montres:
            assert js.solde(hypothese, scenario) == figee.solde(hypothese, scenario)
            assert js.soldeMoyen(hypothese, scenario) == figee.solde_moyen(
                hypothese, scenario)
            for annee in figee.annees:
                assert js.partPib(hypothese, scenario, annee) == figee.part_pib(
                    hypothese, scenario, annee)


# -- le bilan du compte, à la manière suédoise -----------------------------------


@pytest.fixture(scope="module")
def bilans(contexte, montres):
    from retraite_notionnelle.bilan_compte import bilans_gardes

    return bilans_gardes(contexte, AGREGATS.bilan_compte.annee, montres)


def test_le_bilan_du_compte_fige_est_celui_que_le_modele_calcule(bilans, montres):
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
    fige = AGREGATS.bilan_compte
    reserves = Reserves.charger(RACINE_DONNEES)
    assert fige.annee == reserves.derniere_annee()
    assert fige.rendement == reserves.rendement(fige.annee)
    assert set(bilans) == set(montres)
    for scenario in montres:
        systeme = fige.systeme(scenario)
        for champ in agregats.CHAMPS_BILAN_COMPTE:
            assert getattr(systeme, champ) == getattr(bilans[scenario], champ), (
                scenario, champ)
    with pytest.raises(KeyError, match="absent de la table figée"):
        fige.systeme("notionnel_bascule")


@sans_node
def test_les_deux_lecteurs_lisent_le_meme_bilan_du_compte(montres):
    js = site().contexte.agregats().bilanCompte
    fige = AGREGATS.bilan_compte
    assert (js.annee, js.rendement) == (fige.annee, fige.rendement)
    for scenario in montres:
        lu, systeme = js.systeme(scenario), fige.systeme(scenario)
        for champ in agregats.CHAMPS_BILAN_COMPTE:
            assert getattr(lu, champ) == getattr(systeme, champ), (scenario, champ)


# -- les leviers de l'équilibre, à la manière du COR ------------------------------


@pytest.fixture(scope="module")
def leviers(contexte, montres):
    from retraite_notionnelle.leviers import leviers_du_modele

    pages = module("pages")
    return {scenario: leviers_du_modele(contexte.base, scenario,
                                        soldes_vises=tuple(pages.SOLDES_VISES),
                                        annees_visees=tuple(pages.ANNEES_LEVIERS))
            for scenario in montres}


def test_les_leviers_figes_sont_ceux_que_le_modele_calcule(leviers, montres):
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
    fige = AGREGATS.leviers
    assert fige.debut == DEBUT_AJUSTEMENT
    assert fige.horizons == HORIZONS_COR
    assert fige.recul == (RECUL_MINIMAL, RECUL_MAXIMAL)
    assert set(leviers) == set(montres)
    for scenario in montres:
        assert fige.annees == tuple(sorted(leviers[scenario].annuels)), scenario
        for annee, ligne in leviers[scenario].annuels.items():
            lu = fige.annee(scenario, annee)
            for champ in agregats.CHAMPS_LEVIERS:
                assert getattr(lu, champ) == getattr(ligne, champ), (scenario, annee, champ)
        for fin, ecart in leviers[scenario].horizons.items():
            lu = fige.horizon(scenario, fin)
            for champ in agregats.CHAMPS_ECARTS_HORIZON:
                assert getattr(lu, champ) == getattr(ecart, champ), (scenario, fin, champ)
        assert tuple(leviers[scenario].vises) == fige.soldes_vises, scenario
        for solde, annuels in leviers[scenario].vises.items():
            assert tuple(sorted(annuels)) == fige.annees_visees, (scenario, solde)
            for annee, ligne in annuels.items():
                lu = fige.vise(scenario, solde, annee)
                for champ in agregats.CHAMPS_LEVIERS:
                    assert getattr(lu, champ) == getattr(ligne, champ), (
                        scenario, solde, annee, champ)
        for annee in fige.annees_visees:
            equilibre, vise = fige.annee(scenario, annee), fige.vise(scenario, 0.0, annee)
            for champ in agregats.CHAMPS_LEVIERS:
                assert getattr(vise, champ) == getattr(equilibre, champ), (scenario, annee, champ)
    pages = module("pages")
    assert fige.soldes_vises == tuple(pages.SOLDES_VISES)
    assert fige.annees_visees == tuple(pages.ANNEES_LEVIERS)
    assert fige.annee("notionnel_retroactif", fige.annees[-1]).age is None
    with pytest.raises(KeyError, match="absent de la table figée"):
        fige.annee("notionnel_bascule", fige.annees[-1])
    with pytest.raises(KeyError, match="absent de la table figée"):
        fige.annee("actuel", fige.annees[-1] + 1)
    with pytest.raises(KeyError, match="absent de la table figée"):
        fige.horizon("actuel", 2040)
    with pytest.raises(KeyError, match="absent de la table figée"):
        fige.vise("actuel", 0.0025, fige.annees_visees[-1])
    with pytest.raises(KeyError, match="absent de la table figée"):
        fige.vise("actuel", 0.0, fige.annees_visees[-1] + 1)


@sans_node
def test_les_deux_lecteurs_lisent_les_memes_leviers(montres):
    js = site().contexte.agregats().leviers
    fige = AGREGATS.leviers
    assert (js.debut, tuple(js.annees), tuple(js.horizons), tuple(js.recul)) == (
        fige.debut, fige.annees, fige.horizons, fige.recul)
    assert (tuple(js.soldesVises), tuple(js.anneesVisees)) == (
        fige.soldes_vises, fige.annees_visees)
    for scenario in montres:
        for annee in fige.annees:
            lu, ligne = js.annee(scenario, annee), fige.annee(scenario, annee)
            for champ in agregats.CHAMPS_LEVIERS:
                assert getattr(lu, champ) == getattr(ligne, champ), (scenario, annee, champ)
        for fin in fige.horizons:
            lu, ecart = js.horizon(scenario, fin), fige.horizon(scenario, fin)
            for champ in agregats.CHAMPS_ECARTS_HORIZON:
                assert getattr(lu, champ) == getattr(ecart, champ), (scenario, fin, champ)
        for solde in fige.soldes_vises:
            for annee in fige.annees_visees:
                lu, ligne = js.vise(scenario, solde, annee), fige.vise(scenario, solde, annee)
                for champ in agregats.CHAMPS_LEVIERS:
                    assert getattr(lu, champ) == getattr(ligne, champ), (
                        scenario, solde, annee, champ)
