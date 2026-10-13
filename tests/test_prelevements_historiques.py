"""L'histoire des prélèvements sur les pensions et sur les salaires.

``prelevements_historiques.yaml``, qu'écrit ``scripts/fetch/ipp_prelevements_sociaux.py``
depuis les barèmes de l'IPP, donne aux indicateurs de cycle de vie nets les taux
de chaque année (action 138, étape 9). Ce module tient trois choses : que la
dernière marche de chaque série est le barème de l'année courante que le site
applique (``prelevements_remuneration.yaml``), hors de la maladie des pensions
de la SNCF et des mines, qu'il ne prélève pas encore ; que les marches connues
y sont, suppressions comprises, et que celles que le récupérateur lit aux
textes s'y relisent ; que le salaire net de l'année courante est celui de la
fiche de paie, et qu'une année ancienne en change ce que l'histoire dit.

Et la CSG déductible (action 138, étape 5) : la part que l'article 154
quinquies du code général des impôts déduit du revenu imposable, à chaque date
où ses versions la disent, et le net imposable qu'elle donne aux salaires et
aux pensions de chaque année.
"""

from __future__ import annotations

import datetime as dt
import sqlite3
import sys

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.config import RACINE_DONNEES, RACINE_PROJET, Parametres
from retraite_notionnelle.donnees.chargement import charger_yaml
from retraite_notionnelle.donnees.prelevements_historiques import (
    CHEMIN,
    charger_prelevements_historiques,
)
from retraite_notionnelle.remuneration import charger_prelevements, fiche_depuis_brut
from retraite_notionnelle.simulateur import Simulateur

APRES = dt.date(2026, 6, 1)


@pytest.fixture(scope="module")
def historique():
    return charger_prelevements_historiques(RACINE_DONNEES)


@pytest.fixture(scope="module")
def courants():
    return charger_prelevements(RACINE_DONNEES)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def test_la_derniere_marche_des_pensions_est_le_bareme_du_site(historique, courants):
    """La CSG au taux plein, médian et réduit, la CRDS, la CASA et la maladie
    des complémentaires de l'année courante sont celles que le site prélève ;
    la maladie des pensions du régime général n'existe plus depuis 1998."""
    pensions = courants.pensions
    taux = {tranche.libelle: tranche.taux for tranche in pensions.bareme_csg}
    assert historique.taux_csg_pension(APRES, "plein") == pytest.approx(taux["taux plein"])
    assert historique.taux_csg_pension(APRES, "median") == pytest.approx(taux["taux médian"])
    assert historique.taux_csg_pension(APRES, "reduit") == pytest.approx(taux["taux réduit"])
    assert historique.pensions["crds"].valeur(APRES) == pytest.approx(pensions.crds)
    assert historique.pensions["casa"].valeur(APRES) == pytest.approx(pensions.casa)
    assert historique.pensions["maladie_complementaires"].valeur(APRES) == pytest.approx(
        pensions.maladie_complementaire)
    assert historique.pensions["maladie_regime_general"].valeur(APRES) == 0.0


def test_la_derniere_marche_des_salaires_est_la_fiche_du_site(historique, courants):
    """La CSG et la CRDS d'activité, et leur abattement jusqu'à quatre
    plafonds, sont celles de la fiche de paie ; la maladie, le veuvage, le
    chômage salariés et la solidarité des agents publics n'existent plus."""
    profil = courants.profil("salarie_prive")
    csg = historique.salaires["csg"].en_vigueur(APRES)
    assert csg["taux"] == pytest.approx(profil.csg)
    assert historique.salaires["crds"].valeur(APRES) == pytest.approx(profil.crds)
    abattement = profil.abattement_frais[0]
    assert (abattement.haut_en_plafonds, abattement.taux) == (
        4.0, pytest.approx(csg["abattement_jusqu_a_quatre_plafonds"]))
    for serie in ("maladie_prive", "veuvage_prive", "chomage_prive", "maladie_etat",
                  "maladie_collectivites", "solidarite_public"):
        assert not any(historique.salaires[serie].en_vigueur(APRES).values()), serie


def test_les_marches_connues_y_sont(historique):
    """Quelques marches, et les suppressions que l'IPP marque d'une ligne aux
    cellules vides."""
    pensions, salaires = historique.pensions, historique.salaires
    assert historique.taux_csg_pension(dt.date(2017, 6, 1), "plein") == pytest.approx(0.066)
    assert historique.taux_csg_pension(dt.date(2018, 6, 1), "plein") == pytest.approx(0.083)
    assert historique.taux_csg_pension(dt.date(1990, 6, 1), "plein") == 0.0
    assert historique.taux_csg_pension(dt.date(2018, 6, 1), "median") == 0.0
    assert pensions["maladie_regime_general"].valeur(dt.date(1997, 6, 1)) == pytest.approx(0.028)
    assert pensions["maladie_complementaires"].valeur(dt.date(1997, 6, 1)) == pytest.approx(0.038)
    assert pensions["maladie_complementaires"].valeur(dt.date(1998, 6, 1)) == pytest.approx(0.01)
    assert pensions["maladie_complementaires"].valeur(dt.date(1980, 6, 1)) == 0.0
    assert salaires["maladie_prive"].valeur(dt.date(1995, 6, 1), "tout_salaire") == pytest.approx(0.068)
    assert salaires["maladie_prive"].valeur(dt.date(2018, 6, 1), "tout_salaire") == 0.0
    assert salaires["chomage_prive"].valeur(dt.date(2018, 6, 1), "sous_plafond") == pytest.approx(0.0095)
    assert salaires["chomage_prive"].valeur(dt.date(2018, 11, 1), "sous_plafond") == 0.0
    assert salaires["veuvage_prive"].valeur(dt.date(2004, 6, 1), "tout_salaire") == pytest.approx(0.001)
    assert salaires["veuvage_prive"].valeur(dt.date(2004, 8, 1), "tout_salaire") == 0.0
    assert salaires["solidarite_public"].valeur(dt.date(2010, 6, 1)) == pytest.approx(0.01)


def test_la_maladie_d_avant_1967_tient_les_taux_de_1967(historique):
    """Les barèmes de l'IPP prennent la maladie en 1967 ; elle existait
    avant : ses premiers taux valent en deçà, et la donnée le dit. La CSG,
    née en 1991, ne prélève rien avant."""
    maladie = historique.salaires["maladie_prive"]
    assert maladie.en_vigueur(dt.date(1960, 1, 1)) == maladie.marches[0][1]
    assert historique.salaires["csg"].en_vigueur(dt.date(1960, 1, 1)) == {}


def test_une_annee_qui_change_de_taux_preleve_la_moyenne_de_ses_mois(historique):
    """La maladie des pensions naît le 1er juillet 1980 : 1 % sur le régime
    général, 2 % sur les complémentaires, la moitié de l'année."""
    parts = {"maladie_regime_general": 0.6, "maladie_complementaires": 0.4}
    assert historique.taux_pension_annuel(1980, parts) == pytest.approx(
        0.5 * (0.01 * 0.6 + 0.02 * 0.4))
    assert historique.taux_pension_annuel(1979, parts) == 0.0


def test_la_maladie_des_pensions_des_autres_regimes_de_base(historique, courants):
    """La fonction publique, de 2,25 % en 1976 à 2,80 % en 1997 ; les retraités
    indépendants sur leur pension de base, 3 % jusqu'au 1er juillet 1987, que
    l'IPP porte à tort à 3,1 % au 1er janvier 1986 ; les salariés agricoles au
    taux du régime général ; plus rien depuis 1998, comme le site."""
    pensions = historique.pensions
    fonction_publique = pensions["maladie_fonction_publique"]
    assert fonction_publique.valeur(dt.date(1976, 6, 1)) == 0.0
    assert fonction_publique.valeur(dt.date(1980, 6, 1)) == pytest.approx(0.0225)
    assert fonction_publique.valeur(dt.date(1990, 6, 1)) == pytest.approx(0.0265)
    assert fonction_publique.valeur(dt.date(1996, 6, 1)) == pytest.approx(0.0305)
    assert fonction_publique.valeur(dt.date(1997, 6, 1)) == pytest.approx(0.028)
    independants = pensions["maladie_independants"]
    assert independants.valeur(dt.date(1984, 6, 1)) == pytest.approx(0.05)
    assert independants.valeur(dt.date(1986, 6, 1)) == pytest.approx(0.03)
    assert independants.valeur(dt.date(1990, 6, 1)) == pytest.approx(0.034)
    assert independants.valeur(dt.date(1997, 6, 1)) == pytest.approx(0.024)
    for serie in ("maladie_fonction_publique", "maladie_independants"):
        assert pensions[serie].valeur(APRES) == 0.0, serie
    regimes = historique.regimes_des_pensions
    assert {"regime_general", "msa_salaries"} <= regimes["maladie_regime_general"]
    assert {"fonction_publique_etat", "cnracl"} <= regimes["maladie_fonction_publique"]
    assert {"cancava", "organic", "cnavpl", "cnbf"} == regimes["maladie_independants"]
    # Une pension n'est comptée que dans une cotisation.
    groupes = [*regimes.values(), courants.pensions.regimes_maladie]
    assert sum(len(g) for g in groupes) == len(frozenset().union(*groupes))


def test_la_pension_d_un_fonctionnaire_parti_avant_1998_paie_sa_maladie(simulateur):
    """Une fonctionnaire de la catégorie active, partie à 55 ans en 1995 : sa
    pension civile paie 2,65 % de maladie en 1995 et 2,80 % en 1997, en plus de
    la CSG, puis rien en 1998, quand la CSG monte de 2,8 points."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1940, sexe="F", affiliation="fonctionnaire_etat_actif", age_debut=22,
        age_liquidation=55, niveau_salaire=1.0))
    taux = cycle_de_vie.prelevements_par_annee(simulateur, comparaison)
    part = cycle_de_vie._parts_assujetties(simulateur, comparaison.actuel)[
        "maladie_fonction_publique"]
    assert part == pytest.approx(1.0)
    assert taux[1995] == pytest.approx(0.024 + 0.0265)
    assert taux[1997] == pytest.approx(0.034 + 0.005 + 0.028)
    assert taux[1998] == pytest.approx(0.062 + 0.005)


def test_la_maladie_des_pensions_des_exploitants_et_des_regimes_speciaux(historique):
    """Lues aux textes (action 138, étape 9, huitième partie) : les exploitants
    de 1990 à 1997, l'année 1993 tenue ; les régimes spéciaux placés sous le
    régime général et les clercs de notaires depuis le 31 juillet 1980, les IEG
    depuis le 22 novembre, leur relèvement de 1996 au 1er octobre ; la SNCF, la
    RATP et la Banque de France depuis le 1er juillet 1991, les mines depuis le
    1er juillet 1988 ; rien depuis 1998, sauf à la SNCF et aux mines. Une série
    ne prélève rien avant sa première marche."""
    pensions = historique.pensions

    def taux(serie, annee, mois=6):
        return pensions[serie].valeur(dt.date(annee, mois, 1))

    assert taux("maladie_exploitants", 1989) == 0.0
    for annee in (1990, 1993, 1996):
        assert taux("maladie_exploitants", annee) == pytest.approx(0.038), annee
    assert taux("maladie_exploitants", 1997) == pytest.approx(0.028)
    assert taux("maladie_regimes_speciaux", 1980, 7) == 0.0
    assert taux("maladie_regimes_speciaux", 1980, 8) == pytest.approx(0.015)
    assert taux("maladie_regimes_speciaux", 1987, 7) == pytest.approx(0.019)
    assert taux("maladie_regimes_speciaux", 1996, 8) == pytest.approx(0.0285)
    assert taux("maladie_ieg", 1980, 11) == 0.0
    assert taux("maladie_ieg", 1980, 12) == pytest.approx(0.015)
    assert taux("maladie_ieg", 1996, 9) == pytest.approx(0.019)
    assert taux("maladie_ieg", 1996, 10) == pytest.approx(0.0285)
    for serie in ("maladie_regimes_speciaux", "maladie_ieg", "maladie_ratp"):
        assert taux(serie, 1997, 3) == pytest.approx(0.0185), serie
        assert taux(serie, 1997, 9) == pytest.approx(0.028), serie
    assert taux("maladie_sncf", 1991, 6) == 0.0
    assert taux("maladie_sncf", 1991, 7) == pytest.approx(0.045)
    assert taux("maladie_sncf", 1997) == pytest.approx(0.035)
    assert taux("maladie_ratp", 1992) == pytest.approx(0.0165)
    assert taux("maladie_banque_de_france", 1996, 9) == pytest.approx(0.0305)
    assert taux("maladie_banque_de_france", 1997, 3) == pytest.approx(0.0205)
    assert taux("maladie_crpcen", 1985) == pytest.approx(0.015)
    assert taux("maladie_crpcen", 1986) == pytest.approx(0.0225)
    assert taux("maladie_crpcen", 1990) == pytest.approx(0.0265)
    assert taux("maladie_mines", 1988, 6) == 0.0
    assert taux("maladie_mines", 1990) == pytest.approx(0.034)
    assert taux("maladie_mines", 1997) == pytest.approx(0.033)
    for serie in ("maladie_exploitants", "maladie_regimes_speciaux", "maladie_ieg",
                  "maladie_ratp", "maladie_banque_de_france", "maladie_crpcen"):
        assert pensions[serie].valeur(APRES) == 0.0, serie
    assert pensions["maladie_sncf"].valeur(APRES) == pytest.approx(0.007)
    assert pensions["maladie_mines"].valeur(APRES) == pytest.approx(0.005)
    regimes = historique.regimes_des_pensions
    assert regimes["maladie_exploitants"] == {"msa_non_salaries"}
    assert regimes["maladie_regimes_speciaux"] == {
        "opera_de_paris", "comedie_francaise", "chemins_fer_secondaires"}
    for regime in ("ieg", "sncf", "ratp", "banque_de_france", "crpcen", "mines"):
        assert regimes[f"maladie_{regime}"] == {regime}


def test_la_pension_d_un_agent_sncf_paie_encore_sa_maladie(simulateur):
    """Un agent de la SNCF parti à 55 ans en 1990 : 4,50 % de sa pension en
    1992, en plus de la CSG ; 0,70 % depuis 1998, toujours, que la fiche de paie
    du site ne prélève pas encore (``taux_de_prelevement``) : un écart déclaré,
    que le test tient jusqu'à ce qu'elle le prélève."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1935, sexe="H", affiliation="agent_sncf", age_debut=20,
        age_liquidation=55, niveau_salaire=1.0))
    taux = cycle_de_vie.prelevements_par_annee(simulateur, comparaison)
    assert cycle_de_vie._parts_assujetties(simulateur, comparaison.actuel)[
        "maladie_sncf"] == pytest.approx(1.0)
    assert taux[1992] == pytest.approx(0.011 + 0.045)
    assert taux[1998] == pytest.approx(0.062 + 0.005 + 0.007)
    courant = cycle_de_vie.taux_de_prelevement(simulateur, comparaison.actuel)
    assert taux[2030] == pytest.approx(courant + 0.007)


def _lectures():
    """Ce que le récupérateur lit aux textes pour la maladie des pensions."""
    sys.path.insert(0, str(RACINE_PROJET / "scripts" / "fetch"))
    import maladie_des_pensions

    return maladie_des_pensions


def test_la_maladie_lue_aux_textes_est_la_donnee():
    """Chaque série que le récupérateur lit aux textes est dans la donnée,
    marche pour marche, et ses régimes aussi : la donnée a été refaite."""
    lectures = _lectures()
    contenu = charger_yaml(RACINE_DONNEES / CHEMIN)
    for nom, marches in lectures.PENSIONS_LUES_AUX_TEXTES.items():
        ecrites = contenu["pensions"][nom]
        assert [(str(m["depuis"]), float(m["taux"])) for m in ecrites] == [
            (m["depuis"], m["taux"]) for m in marches], nom
    assert {nom: tuple(regimes) for nom, regimes in contenu["regimes_des_pensions"].items()} == (
        lectures.REGIMES_DES_PENSIONS)


def test_la_maladie_lue_aux_textes_se_relit_dans_l_index():
    """Chaque marche lue aux textes cite les mots de l'article de LEGI, de
    l'article ou de la notice du JORF qui la fixent, quand les index sont là
    (``python scripts/fetch/dila_index.py legi --recuperer``, de même ``jorf``)."""
    bases = {}
    for nom in ("legi", "jorf"):
        chemin = RACINE_DONNEES / "brut" / "dila" / f"{nom}.sqlite"
        if chemin.exists():
            bases[nom] = sqlite3.connect(f"file:{chemin}?mode=ro", uri=True)
    if not bases:
        pytest.skip("les index LEGI et JORF ne sont pas là")
    relues = 0
    try:
        for nom, marches in _lectures().PENSIONS_LUES_AUX_TEXTES.items():
            for marche in marches:
                assert marche["lu"], (nom, marche["depuis"])
                for identifiant, mots in marche["lu"]:
                    base = bases.get("legi" if identifiant.startswith("LEGI") else "jorf")
                    if base is None:
                        continue
                    lu = base.execute("select texte from doc where id = ?",
                                      (identifiant,)).fetchone()
                    assert lu, (nom, marche["depuis"], identifiant)
                    texte = " ".join(lu[0].replace(" ", " ").replace("\xa0", " ").split())
                    assert " ".join(mots.split()) in texte, (nom, marche["depuis"], identifiant)
                    relues += 1
    finally:
        for base in bases.values():
            base.close()
    assert relues


def test_le_prive_de_1995_paie_maladie_veuvage_chomage_et_csg(historique, simulateur):
    """Sous le plafond, en 1995 : la CSG de 2,4 % sur tout le brut, que l'IPP
    n'abat pas avant 1998, la maladie de 6,8 %, le veuvage de 0,1 %, le
    chômage de 2,42 %."""
    plafond = simulateur.macro.plafond_securite_sociale(1995)
    brut = 0.8 * plafond
    assert historique.hors_retraite_annuel("prive", 1995, brut, plafond) == pytest.approx(
        brut * (0.024 + 0.068 + 0.001 + 0.0242))


def test_le_salaire_net_de_l_annee_courante_est_celui_de_la_fiche(simulateur):
    """L'année courante, l'histoire et la fiche de paie disent la même chose ;
    une année ancienne retire ce que ses taux retiraient de plus."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1970, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=67, niveau_salaire=1.0)
    nets = cycle_de_vie.revenus_nets(simulateur, carriere)
    bruts = cycle_de_vie.revenus_d_activite(carriere)
    courante = simulateur.parametres.annee_courante
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations,
                              "salarie_prive_non_cadre", courante, bruts[courante])
    assert nets[courante] == pytest.approx(fiche.net, rel=1e-12)
    assert nets[1995] / bruts[1995] < nets[courante] / bruts[courante]


#: Les postes de la fiche d'un indépendant que l'histoire refait.
REFAITS = ("maladie_maternite", "indemnites_journalieres", "famille", "csg_crds")


def test_l_annee_courante_d_un_independant_est_la_fiche_du_site(historique, courants,
                                                                 simulateur):
    """L'année courante, la maladie et l'indemnité journalière des artisans et
    commerçants, les allocations familiales, la CSG et la CRDS de l'histoire
    sont, au centime, celles de la fiche de paie, du taux réduit des petits
    revenus aux tranches des plus grands."""
    annee = courants.annee
    plafond = simulateur.macro.plafond_securite_sociale(annee)
    for niveau in (0.1, 0.3, 0.5, 0.8, 1.2, 1.6, 2.5, 3.5, 6.0):
        revenu = niveau * plafond
        fiche = fiche_depuis_brut(RACINE_DONNEES, simulateur.macro, simulateur.catalogue,
                                  simulateur.affiliations, "commercant", annee, revenu)
        refaits = sum(l.salarie for l in fiche.lignes if l.code in REFAITS)
        autres = sum(l.salarie for l in fiche.lignes if l.code not in REFAITS)
        assert historique.hors_retraite_annuel("commercant", annee, revenu, plafond, autres) == (
            pytest.approx(refaits, rel=1e-9)), niveau


def test_les_marches_des_independants_y_sont(historique):
    """Les tranches de l'IPP qui s'ajoutent, ses marches corrigées par les
    décrets, et les barèmes des textes depuis 2013 ; l'indemnité journalière des
    seuls artisans de 1995 à 2000, des libéraux depuis 2021, que l'avocat ne
    paie pas."""
    plafond = 40_000.0

    def taux(famille, jour, niveau):
        revenu = niveau * plafond
        return historique.maladie_independant(famille, jour, revenu, plafond) / revenu

    assert taux("commercant", dt.date(1985, 6, 1), 0.8) == pytest.approx(0.031 + 0.0845)
    assert taux("commercant", dt.date(1985, 6, 1), 2.0) == pytest.approx(
        (0.031 + 0.0845 * 2.0) / 2.0)
    # Le décret n° 91-745 vaut à l'échéance du 1er octobre 1991, et le décret
    # n° 92-295 porte 9,75 % à celle du 1er octobre 1992 : l'IPP les avance.
    assert taux("commercant", dt.date(1991, 9, 1), 0.8) == pytest.approx(0.031 + 0.0885)
    assert taux("commercant", dt.date(1991, 11, 1), 0.8) == pytest.approx(0.031 + 0.0915)
    assert taux("commercant", dt.date(1993, 6, 1), 0.8) == pytest.approx(0.031 + 0.0975)
    assert taux("liberal", dt.date(1984, 6, 1), 0.8) == pytest.approx(0.037 + 0.0795)
    assert taux("liberal", dt.date(1984, 11, 1), 0.8) == pytest.approx(0.031 + 0.0845)
    assert taux("artisan", dt.date(1996, 6, 1), 0.8) - taux("commercant", dt.date(1996, 6, 1),
                                                             0.8) == pytest.approx(0.005)
    assert taux("commercant", dt.date(2015, 6, 1), 0.8) == pytest.approx(0.065 + 0.007)
    # 2018 : le taux réduit sous 40 % du plafond, et 6,5 % sur tout le revenu
    # au-delà de cinq plafonds ; la fraction au-delà seulement depuis mai 2020.
    assert taux("commercant", dt.date(2018, 6, 1), 0.2) == pytest.approx(
        0.0085 + (0.022 + 0.05 / 1.1 * 0.4 - 0.0085) / 2.0)
    assert taux("commercant", dt.date(2018, 6, 1), 6.0) == pytest.approx(0.065)
    assert taux("commercant", dt.date(2021, 6, 1), 6.0) == pytest.approx(
        (0.072 * 5.0 + 0.065) / 6.0)
    assert taux("liberal", dt.date(2022, 6, 1), 0.3) == pytest.approx(0.003)
    assert taux("avocat", dt.date(2022, 6, 1), 0.3) == 0.0
    assert taux("commercant", dt.date(1969, 6, 1), 0.8) == 0.0

    def famille(jour, niveau):
        revenu = niveau * plafond
        return historique.famille_independant(jour, revenu, plafond) / revenu

    assert famille(dt.date(1990, 6, 1), 0.8) == pytest.approx(0.021 + 0.049)
    assert famille(dt.date(2010, 6, 1), 0.8) == pytest.approx(0.054)
    assert famille(dt.date(2016, 6, 1), 1.25) == pytest.approx(0.0215 + 0.031 / 2.0)
    assert famille(dt.date(2016, 6, 1), 0.8) == pytest.approx(0.0215)
    # Forfaitaire avant 1974, que l'IPP ne chiffre pas : ses taux de 1974 valent
    # en deçà.
    assert famille(dt.date(1970, 6, 1), 0.8) == famille(dt.date(1975, 6, 1), 0.8)


def test_la_csg_d_un_independant_porte_sur_ses_cotisations_jusqu_en_2024(historique):
    """Jusqu'en 2024, la CSG et la CRDS d'un indépendant portent sur son revenu
    augmenté de ses cotisations personnelles (L. 136-3) ; depuis l'assiette
    unique, sur son revenu."""
    plafond, revenu, autres = 46_000.0, 40_000.0, 9_000.0
    for annee, ajoutees in ((1995, True), (2024, True), (2025, False)):
        jour = dt.date(annee, 6, 1)
        cotisations = (historique.maladie_independant("commercant", jour, revenu, plafond)
                       + historique.famille_independant(jour, revenu, plafond))
        taux = historique.salaires["csg"].valeur(jour) + historique.salaires["crds"].valeur(jour)
        assiette = revenu + (autres + cotisations if ajoutees else 0.0)
        assert historique.hors_retraite("commercant", jour, revenu, plafond, autres) == (
            pytest.approx(cotisations + taux * assiette)), annee


def test_le_net_d_un_independant_suit_les_prelevements_de_son_annee(simulateur):
    """L'année courante, le net d'un commerçant est celui de sa fiche de paie ;
    en 1985, il perd 11,55 % de maladie et 9 % d'allocations familiales sous le
    plafond, et pas de CSG."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1950, sexe="H", affiliation="commercant", age_debut=21,
        age_liquidation=64, niveau_salaire=1.0)
    nets = cycle_de_vie.revenus_nets(simulateur, carriere)
    bruts = cycle_de_vie.revenus_d_activite(carriere)
    courante = simulateur.parametres.annee_courante
    jeune = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="commercant", age_debut=25,
        age_liquidation=64, niveau_salaire=1.0)
    revenu = cycle_de_vie.revenus_d_activite(jeune)[courante]
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations, "commercant",
                              courante, revenu)
    assert cycle_de_vie.revenus_nets(simulateur, jeune)[courante] == pytest.approx(
        fiche.net, rel=1e-12)
    ligne = next(l for l in carriere.lignes if l.annee == 1985)
    fiche_1985 = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                                   simulateur.catalogue, simulateur.affiliations,
                                   "commercant", 1985, ligne.revenu_annualise)
    refaits = sum(l.salarie for l in fiche_1985.lignes if l.code in REFAITS)
    plafond = simulateur.macro.plafond_securite_sociale(1985)
    assert ligne.revenu_annualise < plafond
    attendu = fiche_1985.net + refaits - ligne.revenu_annualise * (0.031 + 0.0845 + 0.09)
    assert nets[1985] == pytest.approx(attendu * ligne.fraction_annee, rel=1e-9)


def test_chaque_marche_dit_son_ancrage_au_journal_officiel():
    """Chaque marche porte le texte du Journal officiel qu'elle cite, tel que
    l'index JORF de la DILA le trouve à la date que l'IPP annonce (``jorf``), ou
    ce qui manque pour l'y trouver (``ancrage``) : la cotisation maladie des
    pensions de 1980 est le décret n° 80-298, publié le 26 avril 1980 ; la date
    de publication du décret n° 2012-853, que l'IPP met un an trop tard, se
    voit."""
    contenu = charger_yaml(RACINE_DONNEES / CHEMIN)
    for partie in ("pensions", "salaires", "independants"):
        for nom, marches in contenu[partie].items():
            for marche in marches:
                assert ("jorf" in marche) != ("ancrage" in marche), (partie, nom, marche["depuis"])
    assert contenu["pensions"]["maladie_regime_general"][0]["jorf"] == "JORFTEXT000000328902"
    solidarite = {m["depuis"]: m for m in contenu["salaires"]["solidarite_public"]}
    assert "2012-07-06" in solidarite["2012-07-01"]["ancrage"]
    fonction_publique = contenu["pensions"]["maladie_fonction_publique"]
    assert fonction_publique[1]["jorf"] == "JORFTEXT000000693584"


def test_une_pension_nette_suit_les_prelevements_de_chaque_annee(simulateur):
    """Partie en 2014 : sa pension perd 7,4 % et la maladie des
    complémentaires en 2015, 9,1 % et la même maladie depuis 2018, dernière
    marche tenue au-delà."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1950, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=64, niveau_salaire=1.0))
    taux = cycle_de_vie.prelevements_par_annee(simulateur, comparaison)
    courant = cycle_de_vie.taux_de_prelevement(simulateur, comparaison.actuel)
    maladie = courant - 0.091
    assert taux[2015] == pytest.approx(0.066 + 0.005 + 0.003 + maladie)
    assert taux[2040] == pytest.approx(courant)
    convention = cycle_de_vie.convention_nette(simulateur, comparaison)
    assert convention.nette
    assert convention.retenu(2015) == pytest.approx(1.0 - taux[2015])


# -- La CSG déductible et le net imposable (action 138, étape 5) ----------------

def _script():
    """Le récupérateur, qui dit ce que les textes déduisent."""
    sys.path.insert(0, str(RACINE_PROJET / "scripts" / "fetch"))
    import ipp_prelevements_sociaux

    return ipp_prelevements_sociaux


def test_la_csg_deductible_est_celle_des_textes(historique, courants):
    """La part de la CSG que le revenu imposable déduit (CGI, art. 154
    quinquies), à chaque date où les textes la disent : rien avant 1997, un
    point en 1997, puis la part de l'assurance maladie. Sa dernière marche,
    6,8 points d'un revenu d'activité, est celle de la fiche de paie du site."""
    for texte in _script().DEDUCTIBLE_AUX_TEXTES:
        jour = dt.date.fromisoformat(texte["depuis"])
        for cle, attendu in texte["taux"].items():
            partie, nom = cle.split(".")
            serie = getattr(historique, partie)[nom]
            assert serie.valeur(jour, "deductible") == pytest.approx(attendu), (cle, jour)
    avant = dt.date(1996, 12, 1)
    assert historique.salaires["csg"].valeur(avant, "deductible") == 0.0
    for taux in ("plein", "median", "reduit"):
        assert historique.csg_deductible_pension(avant, taux) == 0.0
    for profil in ("salarie_prive", "agent_seul", "independant"):
        assert historique.salaires["csg"].valeur(APRES, "deductible") == pytest.approx(
            courants.profil(profil).csg_deductible), profil


def test_les_parts_deductibles_se_lisent_dans_legi():
    """Les versions de l'article 154 quinquies, et de L. 136-8 pour 1998, que
    le récupérateur cite disent, mot pour mot, la part qu'il en tire, quand
    l'index LEGI est là (``python scripts/fetch/dila_index.py legi --recuperer``)."""
    base = RACINE_DONNEES / "brut" / "dila" / "legi.sqlite"
    if not base.exists():
        pytest.skip("l'index LEGI n'est pas là")
    connexion = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    try:
        for texte in _script().DEDUCTIBLE_AUX_TEXTES:
            lus = [connexion.execute("select texte from doc where id = ?", (identifiant,))
                   .fetchone() for identifiant in texte["legi"]]
            assert all(lus), texte["legi"]
            tout = " ".join(" ".join(lu[0].replace("\u202f", " ").replace("\xa0", " ").split())
                            for lu in lus)
            for mots in texte["lu"]:
                assert mots in tout, (texte["depuis"], mots)
    finally:
        connexion.close()


def test_le_salaire_imposable_de_l_annee_courante_est_celui_de_la_fiche(simulateur, courants):
    """L'année courante, le salaire imposable est le brut de la fiche de paie
    moins ses cotisations et sa CSG déductible, sur le brut abattu de 1,75 %."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1970, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=67, niveau_salaire=1.0)
    imposables = cycle_de_vie.revenus_imposables(simulateur, carriere)
    bruts = cycle_de_vie.revenus_d_activite(carriere)
    courante = simulateur.parametres.annee_courante
    fiche = fiche_depuis_brut(simulateur.parametres.racine_donnees, simulateur.macro,
                              simulateur.catalogue, simulateur.affiliations,
                              "salarie_prive_non_cadre", courante, bruts[courante])
    profil = courants.profil("salarie_prive")
    cotisations = sum(l.salarie for l in fiche.lignes if l.code != "csg_crds")
    assiette = fiche.brut * (1.0 - profil.abattement_frais[0].taux)
    assert imposables[courante] == pytest.approx(
        fiche.brut - cotisations - profil.csg_deductible * assiette, rel=1e-9)
    assert set(imposables) == set(cycle_de_vie.revenus_nets(simulateur, carriere))


def test_ce_qu_un_salaire_paie_sans_le_deduire_suit_les_textes(historique, simulateur):
    """Sous le plafond, ce que la paie retire sans que le revenu imposable le
    déduise : toute la CSG jusqu'en 1996, la CRDS depuis 1996 ; 2,4 points de
    CSG depuis 1997, sur le brut abattu de 5 % en 1998, de 3 % en 2005, de
    1,75 % depuis 2012. La contribution de solidarité d'un agent public se
    déduit (CGI, art. 83, 2° ter) ; la CSG d'un indépendant porte sur son
    revenu augmenté de ses cotisations."""
    for annee, part in ((1990, 0.0), (1995, 0.024), (1997, 0.029), (1998, 0.029 * 0.95),
                        (2005, 0.029 * 0.97), (2012, 0.029 * 0.9825), (2020, 0.029 * 0.9825)):
        plafond = simulateur.macro.plafond_securite_sociale(annee)
        for famille in ("prive", "contractuel", "agent"):
            assert historique.non_deductibles_annuel(famille, annee, 0.8 * plafond, plafond) == (
                pytest.approx(part * 0.8 * plafond)), (famille, annee)
    jour, plafond, revenu, autres = dt.date(2020, 6, 1), 41_136.0, 40_000.0, 9_000.0
    cotisations = (historique.maladie_independant("commercant", jour, revenu, plafond)
                   + historique.famille_independant(jour, revenu, plafond))
    assert historique.non_deductibles("commercant", jour, revenu, plafond, autres) == (
        pytest.approx(0.029 * (revenu + autres + cotisations)))


def test_la_pension_imposable_suit_la_csg_deductible_de_chaque_annee(simulateur):
    """Partie en 2014, la pension d'un salarié du privé est imposable moins
    4,2 % de CSG et la maladie de sa part complémentaire jusqu'en 2017, moins
    5,9 % depuis : la CRDS, la CASA et 2,4 points de CSG restent imposables.
    Celle d'une fonctionnaire partie en 1995 ne déduit que sa maladie jusqu'en
    1996, un point de CSG de plus en 1997, 3,8 points seuls depuis 1998."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1950, sexe="H", affiliation="salarie_prive_non_cadre", age_debut=21,
        age_liquidation=64, niveau_salaire=1.0))
    parts = cycle_de_vie.parts_imposables_par_annee(simulateur, comparaison)
    prelevements = cycle_de_vie.prelevements_par_annee(simulateur, comparaison)
    assert set(parts) == set(prelevements)
    maladie = prelevements[2015] - (0.066 + 0.005 + 0.003)
    assert maladie > 0.0
    assert parts[2015] == pytest.approx(1.0 - 0.042 - maladie)
    assert parts[2020] == pytest.approx(1.0 - 0.059 - maladie)
    assert prelevements[2020] - (1.0 - parts[2020]) == pytest.approx(0.024 + 0.005 + 0.003)
    fonctionnaire = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1940, sexe="F", affiliation="fonctionnaire_etat_actif", age_debut=22,
        age_liquidation=55, niveau_salaire=1.0))
    parts = cycle_de_vie.parts_imposables_par_annee(simulateur, fonctionnaire)
    assert parts[1995] == pytest.approx(1.0 - 0.0265)
    assert parts[1997] == pytest.approx(1.0 - 0.01 - 0.028)
    assert parts[1998] == pytest.approx(1.0 - 0.038)


def test_la_csg_que_rend_la_proposition_baisse_la_part_deductible(simulateur):
    """Après la bascule, le scénario 6 laisse un net plus fort du même brut ;
    son net imposable garde la part non déductible du droit en vigueur."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1985, sexe="H", affiliation="salarie_prive_cadre", age_debut=22,
        age_liquidation=64, niveau_salaire=1.0)
    nets = cycle_de_vie.revenus_nets(simulateur, carriere)
    imposables = cycle_de_vie.revenus_imposables(simulateur, carriere)
    nets_6 = cycle_de_vie.revenus_nets(simulateur, carriere, proposition=True)
    imposables_6 = cycle_de_vie.revenus_imposables(simulateur, carriere, proposition=True)
    apres = [annee for annee in nets if nets_6[annee] > nets[annee] + 1.0]
    assert apres
    for annee in apres:
        assert imposables_6[annee] - nets_6[annee] == pytest.approx(
            imposables[annee] - nets[annee]), annee
