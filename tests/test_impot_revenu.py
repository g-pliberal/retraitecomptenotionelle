"""L'impôt sur le revenu d'un foyer, à l'euro près (action 138, étape 5).

``retraite_notionnelle/impot_revenu.py`` calcule l'impôt d'une personne seule
ou d'un couple, avec ou sans enfants, sur ses salaires et ses pensions
imposables, des revenus de 1960 à ceux de 2025, puis sur un barème projeté.
Il se confronte, dans l'ordre de la preuve (``docs/architecture.md``, § 3.3) :

1. aux tableaux de la brochure pratique de la DGFiP, qui donnent l'impôt, au
   plafonnement et à la décote près, de milliers de couples revenu-parts des
   revenus de 2023 et de 2024 (``tests/temoins/brochure_impot_revenu.json``) ;
2. aux exemples chiffrés du BOFiP, de la brochure et du Bulletin officiel des
   impôts, de 2000 à 2025, en francs et en euros, avant et après 2006
   (``tests/temoins/exemples_impot_revenu.yaml``) ;
3. à OpenFisca-France, exécuté à part, de 2002 à 2025
   (``tests/temoins/impot_revenu_openfisca.json``) : une seconde
   implémentation, dont chaque désaccord est tranché par le texte, et déclaré
   ici.

Puis ce que la donnée doit tenir : chaque année de 1960 à la dernière loi de
finances se lit dans sa monnaie, la projection suit les prix ou le salaire
moyen, et les valeurs que le script a lues dans l'index LEGI y sont toujours.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.donnees.impot_revenu import (
    FRANC, arrondi_a_l_euro, charger_baremes_impot_revenu, croissance_macro, monnaie_de)
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.impot_revenu import (
    Declarant, Foyer, decote, impot_aux_parametres, impot_d_un_revenu_imposable, impot_du_foyer,
    nombre_de_parts)

RACINE = Path(__file__).resolve().parents[1]
DONNEES = RACINE / "data"
TEMOINS = RACINE / "tests" / "temoins"


@pytest.fixture(scope="module")
def baremes():
    return charger_baremes_impot_revenu(DONNEES)


def _foyer(description: dict) -> Foyer:
    declarants = tuple(Declarant(salaires=d.get("salaires", 0.0), pensions=d.get("pensions", 0.0),
                                 age=d.get("age"), invalide=d.get("invalide", False),
                                 benefices=d.get("benefices", 0.0),
                                 regime=d.get("regime", "reel_adherent"),
                                 categorie=d.get("categorie", "bic"))
                       for d in description["declarants"])
    return Foyer(declarants, enfants=description.get("enfants", 0),
                 enfants_invalides=description.get("enfants_invalides", 0),
                 veuf=description.get("veuf", False), vit_seul=description.get("vit_seul", True))


# -- 1. La brochure pratique -----------------------------------------------------

#: Les foyers qui donnent chaque colonne d'un tableau de la brochure : le
#: nombre d'enfants à charge qui fait ses parts. Les colonnes qu'aucun foyer du
#: module n'atteint (2,5 parts d'une personne seule : un invalide, que la
#: brochure ne compte pas) ne se rejouent pas.
ENFANTS_PAR_PARTS = {
    "personne_seule": {1.0: 0, 1.5: 1, 2.0: 2, 3.0: 3, 4.0: 4, 5.0: 5},
    "parent_isole": {2.0: 1, 2.5: 2, 3.5: 3, 4.5: 4},
    "veuf": {2.5: 1, 3.0: 2, 4.0: 3, 5.0: 4},
    "couple": {2.0: 0, 2.5: 1, 3.0: 2, 4.0: 3, 5.0: 4},
}


def _foyer_de_la_brochure(situation: str, enfants: int) -> Foyer:
    if situation == "couple":
        return Foyer((Declarant(), Declarant()), enfants=enfants)
    return Foyer((Declarant(),), enfants=enfants, veuf=situation == "veuf",
                 vit_seul=situation == "parent_isole")


def test_les_tableaux_de_la_brochure_pratique_sont_reproduits(baremes):
    """Chaque case des tableaux « impôt suivant le nombre de parts » de la
    brochure pratique — plafonnement du quotient familial et décote compris,
    hors réductions d'impôt —, pour les revenus de 2023 et de 2024. Le
    10 octobre 2026, à l'écriture du module, les 4 592 cases que pdftotext lit
    dans les deux brochures étaient toutes reproduites ; le témoin garde
    celles que le lecteur du dépôt lit."""
    temoin = json.loads((TEMOINS / "brochure_impot_revenu.json").read_text(encoding="utf-8"))
    ecarts, cases = [], 0
    for annee, brochure in temoin["brochures"].items():
        for situation, tableau in brochure["tableaux"].items():
            for revenu, impots in tableau["lignes"]:
                for parts, publie in zip(tableau["parts"], impots):
                    enfants = ENFANTS_PAR_PARTS[situation].get(parts)
                    if enfants is None:
                        continue
                    foyer = _foyer_de_la_brochure(situation, enfants)
                    calcul = impot_d_un_revenu_imposable(foyer, int(annee), revenu, baremes)
                    assert calcul.parts == parts
                    cases += 1
                    if calcul.impot_brut - calcul.decote != publie:
                        ecarts.append((annee, situation, parts, revenu, publie,
                                       calcul.impot_brut - calcul.decote))
    assert cases > 2500
    assert not ecarts, f"{len(ecarts)} cases sur {cases} : {ecarts[:10]}"


# -- 2. Les exemples chiffrés -----------------------------------------------------

def _exemples() -> list[dict]:
    return yaml.safe_load((TEMOINS / "exemples_impot_revenu.yaml")
                          .read_text(encoding="utf-8"))["exemples"]


def _calcul(exemple: dict, baremes):
    foyer = _foyer(exemple["foyer"])
    annee = exemple["annee"]
    if "decote_de" in exemple:
        parametres = baremes.parametres(annee)
        return {"decote": decote(foyer, parametres, exemple["decote_de"],
                                 nombre_de_parts(foyer, parametres))}
    if "revenu_net_imposable" in exemple:
        calcul = impot_d_un_revenu_imposable(foyer, annee, exemple["revenu_net_imposable"],
                                             baremes, unite="monnaie")
    else:
        calcul = impot_du_foyer(foyer, annee, baremes, unite="monnaie")
    return {cle: getattr(calcul, cle) for cle in calcul.__dataclass_fields__}


@pytest.mark.parametrize("exemple", _exemples(), ids=lambda e: e["id"])
def test_les_exemples_officiels_sont_reproduits(exemple, baremes):
    """Chaque grandeur publiée, à l'unité près de sa monnaie ; un écart connu
    garde la valeur que rend le module, pour qu'elle ne change pas en silence."""
    calcul = _calcul(exemple, baremes)
    for grandeur, publie in exemple["attendu"].items():
        assert calcul[grandeur] == pytest.approx(publie, abs=0.001), (
            f"{exemple['id']} : {grandeur} = {calcul[grandeur]}, publié {publie}")
    for grandeur, ecart in (exemple.get("ecart_connu") or {}).items():
        assert ecart["raison"].strip()
        assert calcul[grandeur] == pytest.approx(ecart["obtenu"], abs=0.001), (
            f"{exemple['id']} : l'écart connu sur {grandeur} a changé "
            f"({calcul[grandeur]} au lieu de {ecart['obtenu']})")


def test_les_exemples_couvrent_francs_et_euros_avant_et_apres_2006():
    """La demande du propriétaire : plusieurs années, en francs et en euros,
    avant et après la réforme du barème de 2006, qui a intégré l'abattement de
    20 %."""
    annees = {exemple["annee"] for exemple in _exemples()}
    assert any(annee <= 2000 for annee in annees), "aucun exemple en francs"
    assert any(2001 <= annee <= 2005 for annee in annees), "aucun exemple en euros avant 2006"
    assert len([annee for annee in annees if annee >= 2006]) >= 10


# -- 3. OpenFisca-France ---------------------------------------------------------

#: Les désaccords avec OpenFisca-France, chacun tranché par le texte : le foyer,
#: les années, les grandeurs qu'il touche, et pourquoi.
DESACCORDS_OPENFISCA = (
    ("veuf_un_enfant", range(2002, 2008), {"nbptr", "ir_plaf_qf", "ip_net", "iai"},
     "OpenFisca compte 1,5 part au veuf ayant un enfant à charge avant 2008 ; l'article 194 "
     "(LEGIARTI000006308280, revenus de 2003 et suivants) dit « Marié ou veuf ayant un "
     "enfant à charge = 2,5 ». L'IPP, qui partage ses paramètres, ne la fait naître qu'en "
     "2008."),
    ("couple_retraites", range(2002, 2006), {"rng", "rni", "rfr", "ir_plaf_qf", "ip_net", "iai"},
     "Jusqu'en 2005, OpenFisca applique l'abattement de 20 % aux pensions diminuées de leur "
     "abattement de 10 % AVANT son plafond par foyer ; l'article 158, 5, a "
     "(LEGIARTI000006307985) ne retient que 80 % des pensions « après application des "
     "dispositions des deuxième et troisième alinéas », plafond compris."),
    ("couple_retraites_aises", range(2002, 2006),
     {"rng", "rni", "rfr", "ir_plaf_qf", "ip_net", "iai"},
     "Le même abattement de 20 % (voir couple_retraites)."),
    ("celibataire_bas_salaire", range(2005, 2006), {"ppe"},
     "OpenFisca prend pour la prime pour l'emploi des revenus de 2005 les taux de 6,8 % et "
     "17 % ; l'article 200 sexies (LEGIARTI000006303356) donne « 6,0 % (2) » et « 15,0 % "
     "(2) », « (2) applicable aux revenus 2005 », les premiers étant ceux qu'il donnait aux "
     "revenus de 2006. L'IPP, qui partage ses paramètres, porte la même erreur."),
    ("couple_un_salaire", range(2005, 2006), {"ppe"},
     "Les mêmes taux de 2005 (voir celibataire_bas_salaire)."),
)


def _desaccord(code: str, annee: int, grandeur: str) -> bool:
    return any(code == c and annee in annees and grandeur in grandeurs
               for c, annees, grandeurs, _ in DESACCORDS_OPENFISCA)


def test_openfisca_france_confirme_le_calcul(baremes):
    """Quinze foyers, de 2002 à 2025. Concordent : les parts, le revenu net
    global et imposable, l'abattement des personnes âgées, le revenu fiscal de
    référence, l'impôt après plafonnement, la décote, l'impôt après décote et
    réductions, la prime pour l'emploi. Trois conventions d'OpenFisca, qui ne
    sont pas des désaccords sur le droit, se neutralisent :

    - il arrondit les corrections sur l'impôt brut non arrondi, quand le BOFiP
      arrondit chaque élément (BOI-IR-LIQ-20-20-40, § 50 : « Tout élément venant
      modifier [...] les cotisations (décotes [...]) est arrondi à l'euro le plus
      proche ») : un euro d'écart, au plus, sur l'impôt ; la brochure et le
      BOFiP donnent raison au module ;
    - sa décote n'est pas bornée par l'impôt : elle ne se compare que quand
      l'impôt reste positif ;
    - de 2010 à 2015, il diminue la prime pour l'emploi du RSA activité auquel
      le foyer a droit (art. 200 sexies), que le module ne calcule pas
      (``HORS_CHAMP``) : la prime ne se compare que jusqu'en 2009.
    """
    temoin = json.loads((TEMOINS / "impot_revenu_openfisca.json").read_text(encoding="utf-8"))
    grandeurs = temoin["grandeurs"]
    ecarts, comparees = [], 0
    for code, contenu in temoin["foyers"].items():
        description = contenu["foyer"]
        declarants = [{"salaires": d.get("salaire", 0), "pensions": d.get("pension", 0),
                       "age": d.get("age", 40), "invalide": d.get("invalide", False)}
                      for d in description["declarants"]]
        foyer = _foyer({"declarants": declarants, "enfants": description.get("enfants", 0),
                        "veuf": description.get("statut") == "veuf",
                        "vit_seul": bool(description.get("case_t"))})
        for annee, valeurs in contenu["annees"].items():
            annee = int(annee)
            eux = dict(zip(grandeurs, valeurs))
            nous = impot_du_foyer(foyer, annee, baremes)
            paires = {
                "nbptr": (nous.parts, 0.0),
                "rng": (nous.revenu_net_global, 0.5),
                "abat_spe": (nous.abattement_age_invalidite, 0.5),
                "rni": (nous.revenu_net_imposable, 0.5),
                "rfr": (nous.revenu_fiscal_de_reference, 0.5),
                "ir_plaf_qf": (nous.impot_brut, 0.5),
                "ip_net": (nous.impot_brut - nous.decote - nous.reduction_sous_condition_de_revenus,
                           1.0),
                "iai": (nous.impot_avant_credits, 1.0),
            }
            if eux["ip_net"]:
                paires["decote"] = (nous.decote, 1.0)
            if annee <= 2009:
                paires["ppe"] = (nous.prime_pour_l_emploi, 0.5)
            for grandeur, (valeur, tolerance) in paires.items():
                if eux[grandeur] is None or _desaccord(code, annee, grandeur):
                    continue
                comparees += 1
                if abs(valeur - eux[grandeur]) > tolerance + 1e-9:
                    ecarts.append((code, annee, grandeur, valeur, eux[grandeur]))
    assert comparees > 2500
    assert not ecarts, f"{len(ecarts)} désaccords non déclarés : {ecarts[:10]}"


def test_les_desaccords_avec_openfisca_sont_ceux_du_texte(baremes):
    """Ce que le module rend là où il désaccorde OpenFisca est ce que le texte
    dit : 2,5 parts au veuf qui a un enfant à charge en 2003 ; 80 % des pensions
    après leur abattement plafonné en 2002 ; la prime pour l'emploi de 2005 à
    6,0 % du revenu d'activité."""
    veuf = Foyer((Declarant(salaires=45000),), enfants=1, veuf=True)
    assert impot_du_foyer(veuf, 2003, baremes).parts == 2.5
    couple = Foyer((Declarant(pensions=60000, age=75), Declarant(pensions=30000, age=74)))
    calcul = impot_du_foyer(couple, 2002, baremes, unite="monnaie")
    # 10 % de 90 000 € plafonnés à 3 214 € par foyer, puis 80 % du reste.
    assert calcul.revenu_net_global == pytest.approx(round((90000 - 3214) * 0.8), abs=1)
    # 10 000 € de salaire, sous le seuil du taux plein de 11 899 € : 6,0 %.
    seul = Foyer((Declarant(salaires=10000),))
    assert impot_du_foyer(seul, 2005, baremes).prime_pour_l_emploi == 600


# -- Ce que la donnée doit tenir ---------------------------------------------------

def test_chaque_annee_de_1960_a_la_derniere_loi_se_lit_dans_sa_monnaie(baremes):
    """Chaque année de revenus de 1960 à la dernière loi de finances lue rend
    ses paramètres dans sa monnaie, francs jusqu'en 2000, euros ensuite, et
    l'impôt d'un salarié et d'un retraité s'y calcule."""
    assert baremes.premiere_annee == 1960
    assert baremes.derniere_annee >= 2025
    salarie = Foyer((Declarant(salaires=30000),))
    retraites = Foyer((Declarant(pensions=25000, age=70), Declarant(pensions=12000, age=68)))
    for annee in range(baremes.premiere_annee, baremes.derniere_annee + 1):
        parametres = baremes.lus(annee)
        assert parametres.monnaie == monnaie_de(annee)
        assert list(parametres.seuils) == sorted(parametres.seuils)
        assert len(parametres.seuils) == len(parametres.taux)
        for foyer in (salarie, retraites):
            calcul = impot_du_foyer(foyer, annee, baremes)
            assert calcul.impot_avant_credits >= 0
            assert calcul.revenu_fiscal_de_reference == calcul.revenu_net_imposable


def test_un_impot_en_francs_se_calcule_en_francs(baremes):
    """Les mêmes revenus, donnés en euros ou en francs : le même impôt, au
    franc près — le calcul d'une année en francs se fait en francs, arrondis
    compris."""
    for annee in (1975, 1990, 1999):
        foyer_francs = Foyer((Declarant(salaires=150000.0), Declarant(pensions=60000.0, age=66)),
                             enfants=2)
        foyer_euros = Foyer((Declarant(salaires=150000.0 / FRANC),
                             Declarant(pensions=60000.0 / FRANC, age=66)), enfants=2)
        en_francs = impot_du_foyer(foyer_francs, annee, baremes, unite="monnaie")
        en_euros = impot_du_foyer(foyer_euros, annee, baremes, unite="euro")
        assert en_euros.impot * FRANC == pytest.approx(en_francs.impot, abs=1.0)


def test_les_parts_des_enfants_suivent_les_lois_de_1980_et_1986(baremes):
    """Une part entière pour le cinquième enfant sur les revenus de 1979 (loi de
    finances pour 1980, art. 4, I : « marié ou veuf ayant cinq enfants à
    charge 5 [...] et ainsi de suite, en augmentant d'une demi-part par enfant
    à charge ») ; sur ceux de 1980, une demi-part de plus à qui a au moins
    trois enfants, qui « se substitue » à celle du cinquième (loi de finances
    pour 1981, art. 3, I) ; une part pour chaque enfant à partir du troisième
    sur ceux de 1986 ; une demi-part chacun avant 1979."""
    def parts(annee, enfants):
        return impot_d_un_revenu_imposable(
            Foyer((Declarant(), Declarant()), enfants=enfants), annee, 100000, baremes,
            unite="monnaie").parts
    assert parts(1978, 5) == 4.5
    assert parts(1979, 5) == 5.0 and parts(1979, 6) == 5.5
    assert parts(1980, 3) == 4.0 and parts(1980, 4) == 4.5 and parts(1980, 5) == 5.0
    assert parts(1985, 6) == 5.5
    assert parts(1986, 4) == 5.0 and parts(2024, 5) == 6.0


def test_l_abattement_des_pensions_a_un_minimum_par_pensionne_et_un_maximum_par_foyer(baremes):
    """CGI, art. 158, 5, a, revenus de 2024 : 10 %, au moins 450 € par pensionné,
    au plus 4 399 € pour le foyer."""
    petite = impot_du_foyer(Foyer((Declarant(pensions=3000, age=70),)), 2024, baremes)
    assert petite.pensions_nettes == (3000 - 450,)
    grosses = impot_du_foyer(Foyer((Declarant(pensions=40000, age=70),
                                    Declarant(pensions=20000, age=70))), 2024, baremes)
    assert sum(grosses.pensions_nettes) == 60000 - 4399
    # Les exemples de l'administration, sans la pension de l'enfant à charge
    # qu'ils comptent aussi : DB 5 F 311 du 10 février 1999 (revenus de 1998),
    # « Abattement effectif global plafonné accordé : 20 000 F » ;
    # BOI-RSA-PENS-30-10-10-20121211, § 180 (revenus de 2011), « 3 660 € ».
    francs = impot_du_foyer(Foyer((Declarant(pensions=280000, age=70),
                                   Declarant(pensions=15000, age=70))), 1998, baremes,
                            unite="monnaie")
    assert sum(francs.pensions_nettes) == 295000 - 20000
    euros = impot_du_foyer(Foyer((Declarant(pensions=40000, age=70),
                                  Declarant(pensions=2000, age=70))), 2011, baremes)
    assert sum(euros.pensions_nettes) == 42000 - 3660


def test_l_abattement_des_personnes_agees_suit_le_revenu_net_global(baremes):
    """CGI, art. 157 bis, revenus de 2024 : 2 796 € jusqu'à 17 510 € de revenu net
    global, 1 398 € jusqu'à 28 170 €, rien au-delà ; doublé pour un couple dont
    les deux ont plus de 65 ans."""
    def abattement(pensions, ages):
        foyer = Foyer(tuple(Declarant(pensions=p, age=a) for p, a in zip(pensions, ages)))
        return impot_du_foyer(foyer, 2024, baremes).abattement_age_invalidite
    assert abattement([19000], [70]) == 2796        # revenu net global 17 100 €
    assert abattement([22000], [70]) == 1398        # 19 800 €
    assert abattement([32000], [70]) == 0           # 28 800 €
    assert abattement([10000, 9000], [70, 66]) == 2 * 2796
    assert abattement([10000, 9000], [70, 64]) == 2796


def test_le_seuil_de_mise_en_recouvrement(baremes):
    """Une cotisation sous le seuil n'est pas mise en recouvrement : 61 € depuis
    2001, 400 F de 1993 à 2000 (CGI, art. 1657, 1 bis)."""
    foyer = Foyer((Declarant(),))
    petit = impot_d_un_revenu_imposable(foyer, 2024, 17300, baremes)
    assert 0 < petit.impot_avant_credits < 61 and not petit.mis_en_recouvrement
    assert petit.impot == 0
    # 1996 : la décote efface l'impôt jusqu'à 1 630 F, en laisse 182 F à 42 000 F.
    for revenu, cotisation, recouvre in ((42000, 182, False), (60000, 4910, True)):
        calcul = impot_d_un_revenu_imposable(foyer, 1996, revenu, baremes, unite="monnaie")
        assert calcul.impot_avant_credits == cotisation
        assert calcul.mis_en_recouvrement is recouvre


def test_la_prime_pour_l_emploi_suit_l_article_200_sexies(baremes):
    """Revenus de 2007 (LEGIARTI000017888107) : 7,7 % du revenu d'activité
    jusqu'à 12 475 €, 19,3 % de ce qui le sépare de 17 451 € au-delà ; 83 € de
    plus au couple dont un seul travaille, 83 € forfaitaires de 17 451 € à
    24 950 € ; 36 € par enfant à charge."""
    def prime(salaires, enfants=0):
        foyer = Foyer(tuple(Declarant(salaires=s) for s in salaires), enfants=enfants)
        return impot_du_foyer(foyer, 2007, baremes).prime_pour_l_emploi
    assert prime([10000]) == round(0.077 * 10000)
    assert prime([15000]) == round(0.193 * (17451 - 15000))
    assert prime([10000, 0]) == round(0.077 * 10000 + 83)
    assert prime([20000, 0]) == 83
    assert prime([10000, 9000], enfants=2) == round(0.077 * 10000 + 0.077 * 9000 + 2 * 36)
    assert prime([40000]) == 0


def test_le_minimum_de_la_prime_est_un_plancher_puis_un_seuil(baremes):
    """« ne peut être inférieur à 25 euros » jusqu'aux revenus de 2004
    (LEGIARTI000006303353) ; « n'est pas due lorsque son montant avant
    imputation est inférieur à 30 Euros » depuis ceux de 2005
    (LEGIARTI000006303356)."""
    def prime(annee, salaire):
        return impot_du_foyer(Foyer((Declarant(salaires=salaire),)), annee,
                              baremes).prime_pour_l_emploi
    # (15 735 - 15 600) x 11,5 % = 16 €, porté à 25 €.
    assert prime(2003, 15600) == 25
    # (16 659 - 16 500) x 15 % = 24 €, qui n'est pas dû.
    assert prime(2005, 16500) == 0


def test_la_prime_pour_l_emploi_finit_avec_les_revenus_de_2014(baremes):
    """L'article 28 de la loi de finances rectificative pour 2014 (n° 2014-1655)
    abroge l'article 200 sexies, dont la dernière rédaction finit le 30 décembre
    2014 (LEGIARTI000029042107) : « Le dispositif de la PPE reste applicable en
    2015 pour l'imposition des revenus de 2014 », ses commentaires « ne trouvent
    plus à s'appliquer à compter de l'imposition des revenus de 2015 »
    (BOI-IR-RICI-310-10-30-20150515). La prime d'activité qui la remplace au 1er
    janvier 2016 n'est pas un crédit d'impôt."""
    def prime(annee):
        return impot_du_foyer(Foyer((Declarant(salaires=10000),)), annee,
                              baremes).prime_pour_l_emploi
    assert prime(2014) == round(0.077 * 10000)
    assert prime(2015) == 0


def test_le_foyer_qui_n_est_pas_imposable_recoit_toute_sa_prime(baremes):
    """Une cotisation sous le seuil de mise en recouvrement n'est pas due (art.
    1657, 1 bis) : la prime pour l'emploi est versée en entier (art. 200 sexies,
    IV : « Si l'impôt sur le revenu n'est pas dû [...] la différence est versée
    aux intéressés » ; BOI 5 B-12-01, n° 53)."""
    calcul = impot_du_foyer(Foyer((Declarant(salaires=11650),)), 2005, baremes)
    assert 0 < calcul.impot_avant_credits < 61 and not calcul.mis_en_recouvrement
    assert calcul.impot == -calcul.prime_pour_l_emploi


def test_la_prime_pour_l_emploi_retient_le_benefice_majore_de_11_11(baremes):
    """Art. 200 sexies, I, B, 3° : le revenu d'activité de la prime comprend les
    bénéfices industriels et commerciaux, agricoles et non commerciaux, et III :
    « majorés de 11,11 % » dans la première rédaction (LEGIARTI000006303351,
    revenus de 2000), « majorés, ou diminués en cas de déficits, de 11,11 % »
    dès la suivante (LEGIARTI000006303352, revenus de 2001). Le déficit de qui
    a aussi un salaire s'en déduit (BOI 5 B-12-01, n° 15 : « il est fait masse
    ») ; le bénéfice est pris avant l'abattement des adhérents (n° 17) et
    avant la majoration de qui n'adhère pas (BOI-IR-RICI-310-10-30, n° 90).
    Qui n'a qu'un déficit n'est pas actif : son conjoint travaille seul."""
    def calcul(annee, *declarants):
        return impot_du_foyer(Foyer(declarants), annee, baremes, unite="monnaie")
    # 2000 : le déficit de 10 000 F se déduit du salaire tel quel.
    assert calcul(2000, Declarant(salaires=90000, benefices=-10000)).revenus_d_activite == (80000,)
    # 2001 : minoré de 11,11 % (222 €), il retranche 1 778 € ; 4,4 % de 10 222 €.
    mixte = calcul(2001, Declarant(salaires=12000, benefices=-2000))
    assert mixte.revenus_d_activite == (10222,)
    assert mixte.prime_pour_l_emploi == round(0.044 * 10222)
    # 2005 : 9 000 € et 1 000 € de majoration, sans l'abattement de 20 % ; 6 %.
    adherent = calcul(2005, Declarant(benefices=9000))
    assert adherent.abattement_adherents == 1800
    assert adherent.revenus_d_activite == (10000,) and adherent.prime_pour_l_emploi == 600
    # 2012 : sans la majoration de 25 % du non-adhérent ; 7,7 %.
    non_adherent = calcul(2012, Declarant(benefices=9000, regime="reel_non_adherent"))
    assert non_adherent.benefices_retenus == (11250,)
    assert non_adherent.revenus_d_activite == (10000,)
    assert non_adherent.prime_pour_l_emploi == 770
    # 2007 : deux actifs, puis un salarié dont le conjoint n'a qu'un déficit,
    # minoré de 556 € : 83 € de plus pour le couple dont un seul travaille.
    deux_actifs = calcul(2007, Declarant(salaires=10000), Declarant(benefices=9000))
    assert deux_actifs.revenus_d_activite == (10000, 10000)
    assert deux_actifs.prime_pour_l_emploi == 2 * 770
    un_actif = calcul(2007, Declarant(salaires=10000), Declarant(benefices=-5000))
    assert un_actif.revenus_d_activite == (10000, -4444)
    assert un_actif.prime_pour_l_emploi == 770 + 83
    # Hors des années de la prime, rien.
    for annee in (1999, 2016):
        assert calcul(annee, Declarant(salaires=10000, benefices=5000)).revenus_d_activite == ()


def test_les_mesures_des_revenus_de_2001_et_de_2008(baremes):
    """Les 5 % retranchés de l'impôt après la décote, aux revenus de 2001 (loi
    n° 2002-1050, art. 1) ; le crédit d'impôt exceptionnel des revenus de 2008,
    refusé à partir de 12 475 € de revenu par part (loi n° 2009-431, art. 1)."""
    seul = Foyer((Declarant(),))
    calcul = impot_d_un_revenu_imposable(seul, 2001, 20000, baremes)
    # 3 370 € au barème, sans décote ; 5 % font 168,50 €, arrondis à 169 €.
    assert (calcul.impot_brut, calcul.reduction_proportionnelle,
            calcul.impot_avant_credits) == (3370, 169, 3201)
    assert impot_d_un_revenu_imposable(seul, 2002, 20000, baremes).reduction_proportionnelle == 0
    # Une part : 33 € au premier seuil, x (12 475 - 12 000) / 802 = 19,55 €.
    assert impot_d_un_revenu_imposable(seul, 2008, 12000, baremes).credit_exceptionnel == 20
    assert impot_d_un_revenu_imposable(seul, 2008, 12475, baremes).credit_exceptionnel == 0
    assert impot_d_un_revenu_imposable(seul, 2009, 11000, baremes).credit_exceptionnel == 0


def test_la_projection_suit_les_prix_par_defaut_et_le_salaire_moyen_en_variante(baremes):
    """Au-delà de la dernière loi de finances, chaque montant est relevé de la
    croissance de l'année et arrondi à l'euro ; les taux et le seuil de mise en
    recouvrement ne bougent pas ; une année projetée est estimée."""
    macro = DonneesMacro(DONNEES)
    derniere = baremes.derniere_annee
    lue = baremes.lus(derniere)
    for indexation in ("prix", "salaire_moyen"):
        croissance = croissance_macro(macro, indexation)
        projetee = baremes.parametres(derniere + 1, indexation, croissance)
        facteur = 1 + croissance(derniere + 1)
        assert projetee.seuils == tuple(arrondi_a_l_euro(s * facteur) for s in lue.seuils)
        assert projetee.taux == lue.taux
        assert projetee["decote"]["seuil_couple"] == arrondi_a_l_euro(
            lue["decote"]["seuil_couple"] * facteur)
        assert projetee["recouvrement"] == lue["recouvrement"]
        assert projetee.projete and str(projetee.fiabilite) == "estimee"
        calcul = impot_du_foyer(Foyer((Declarant(salaires=40000),)), derniere + 10, baremes,
                                indexation=indexation, croissance=croissance)
        assert calcul.impot > 0 and calcul.remarques
    with pytest.raises(ValueError):
        baremes.parametres(derniere + 1)


def test_la_chronique_du_bareme_est_celle_de_chaque_annee(baremes):
    """Les indicateurs de cycle de vie prennent les paramètres d'un siècle en
    une passe (``chronique``), chaque année projetée partant de la précédente :
    ce sont ceux que ``parametres`` rend un à un, et l'impôt qu'ils donnent est
    celui d'``impot_du_foyer``."""
    macro = DonneesMacro(DONNEES)
    foyer = Foyer((Declarant(salaires=30000, pensions=12000, age=66),))
    for indexation in ("prix", "salaire_moyen"):
        croissance = croissance_macro(macro, indexation)
        chronique = baremes.chronique(2100, indexation, croissance)
        assert list(chronique) == list(range(baremes.premiere_annee, 2101))
        for annee in (1960, 2000, baremes.derniere_annee, baremes.derniere_annee + 1, 2100):
            assert chronique[annee] == baremes.parametres(annee, indexation, croissance), annee
            assert impot_aux_parametres(foyer, chronique[annee]) == impot_du_foyer(
                foyer, annee, baremes, indexation=indexation, croissance=croissance), annee
    assert list(baremes.chronique(1999)) == list(range(baremes.premiere_annee, 2000))
    with pytest.raises(ValueError):
        baremes.chronique(baremes.derniere_annee + 1)


# -- Ce que le script a lu dans l'index LEGI ----------------------------------------

def _texte_legi(identifiant: str) -> str | None:
    base = RACINE / "data" / "brut" / "dila" / "legi.sqlite"
    if not base.exists():
        return None
    with sqlite3.connect(base) as connexion:
        ligne = connexion.execute("select texte from doc where id = ?", (identifiant,)).fetchone()
    return ligne[0] if ligne else None


def _montants(valeur) -> tuple[str, str]:
    """Un montant tel qu'une rédaction l'écrit : ses milliers séparés d'une
    espace, ou d'un point avant les années 1990 (« 16.800 F »)."""
    chiffres = f"{int(valeur):,}"
    return chiffres.replace(",", " "), chiffres.replace(",", ".")


# -- Le bénéfice d'un indépendant ---------------------------------------------------


def _benefice(baremes, annee, benefice, unite="euro", **declarant):
    return impot_du_foyer(Foyer((Declarant(benefices=benefice, age=45, **declarant),)), annee,
                          baremes, unite=unite)


def test_le_benefice_de_qui_n_adhere_pas_est_majore_comme_le_bofip_l_illustre(baremes):
    """BOI-IR-BASE-10-10-20-20210512, n° 90 : le bénéfice de 50 000 € des
    revenus de 2019 d'un non-adhérent est retenu pour 62 500 € ; le déficit de
    10 000 € reste de 10 000 €. Le revenu fiscal de référence porte la
    majoration (n° 100). Puis 1,20, 1,15 et 1,10 de 2020 à 2022 (n° 55), rien
    avant 2006 ni depuis 2023."""
    majore = _benefice(baremes, 2019, 50000, regime="reel_non_adherent")
    assert majore.benefices_retenus == (62500,) and majore.majoration_des_benefices == 12500
    assert majore.revenu_fiscal_de_reference == 62500
    deficit = impot_du_foyer(Foyer((Declarant(salaires=40000, benefices=-10000,
                                              regime="reel_non_adherent"),)), 2019, baremes)
    assert deficit.benefices_retenus == (-10000,)
    assert deficit.revenu_net_global == 36000 - 10000
    for annee, retenu in ((2005, 50000), (2006, 62500), (2020, 60000), (2021, 57500),
                          (2022, 55000), (2023, 50000), (2025, 50000)):
        assert _benefice(baremes, annee, 50000,
                         regime="reel_non_adherent").benefices_retenus == (retenu,), annee
    adherent = _benefice(baremes, 2019, 50000)
    assert adherent.benefices_retenus == (50000,) and adherent.impot < majore.impot
    assert _benefice(baremes, 2019, 50000, regime="micro").benefices_retenus == (50000,)


def test_l_adherent_a_son_abattement_jusqu_en_2005(baremes):
    """Art. 158, 4 bis : 20 % du bénéfice de l'adhérent de 1978 à 2005, sans
    les 10 % de frais professionnels d'un salaire ; jusqu'en 1995, 10 % sur la
    fraction qui excède le seuil de l'année — 150 000 F en 1980 —, rien
    au-delà de la limite de l'abattement des salaires."""
    en_2005 = _benefice(baremes, 2005, 50000)
    assert en_2005.abattement_adherents == 10000 and en_2005.revenu_net_global == 40000
    en_1980 = _benefice(baremes, 1980, 300000, unite="monnaie")
    assert en_1980.abattement_adherents == pytest.approx(0.2 * 150000 + 0.1 * 150000)
    assert any("fraction à 10 %" in r for r in en_1980.remarques)
    plafond = _benefice(baremes, 1980, 1000000, unite="monnaie")
    assert plafond.abattement_adherents == pytest.approx(0.2 * 150000 + 0.1 * (410000 - 150000))
    en_1997 = _benefice(baremes, 1997, 300000, unite="monnaie")
    assert en_1997.abattement_adherents == 60000
    assert _benefice(baremes, 1984, 100000, unite="monnaie",
                     categorie="bnc").abattement_adherents == 20000
    with pytest.raises(ValueError, match="régime"):
        Declarant(benefices=1.0, regime="forfait")


def test_l_adherent_d_avant_1978(baremes):
    """La loi de finances rectificative pour 1974 (n° 74-1114, art. 1er, III,
    texte définitif adopté par le Sénat le 20 décembre 1974) : « un abattement
    de 10 % sur leur bénéfice imposable », sans seuil ni limite, que le décret
    n° 75-911 du 6 octobre 1975 (art. 17) n'accorde qu'à l'adhérent de tout
    l'exercice : rien en 1975. La loi de finances pour 1978 (n° 77-1467, texte
    définitif du 16 décembre 1977) le porte à 20 % dès les revenus de 1977
    (art. 7, II, et 1er, III), 10 % au-delà des 150 000 F de son article 6,
    rien au-delà d'une fois et demie la limite de la dernière tranche du barème
    de son article 2 (238 200 F, pour deux parts). Les bénéfices non
    commerciaux, par les associations agréées que le décret n° 77-1519 du
    31 décembre 1977 fait naître : 20 % dès 1978 (art. 158, 4 ter, rédaction du
    1er juillet 1979, « pour l'imposition des revenus de 1978 et de 1979 »),
    jusqu'à leur entrée au 4 bis."""
    assert _benefice(baremes, 1975, 100000, unite="monnaie").abattement_adherents == 0
    assert _benefice(baremes, 1976, 100000, unite="monnaie").abattement_adherents == 10000
    assert _benefice(baremes, 1976, 1000000, unite="monnaie").abattement_adherents == 100000
    assert _benefice(baremes, 1976, 100000, unite="monnaie",
                     categorie="ba").abattement_adherents == 10000
    en_1977 = _benefice(baremes, 1977, 300000, unite="monnaie")
    assert en_1977.abattement_adherents == pytest.approx(0.2 * 150000 + 0.1 * 150000)
    plafond = _benefice(baremes, 1977, 1000000, unite="monnaie")
    assert plafond.abattement_adherents == pytest.approx(0.2 * 150000 + 0.1 * (357300 - 150000))
    for annee, abattement in ((1976, 0), (1977, 0), (1978, 20000), (1983, 20000)):
        assert _benefice(baremes, annee, 100000, unite="monnaie",
                         categorie="bnc").abattement_adherents == abattement, annee
    assert not any("avant 1978" in r
                   for r in _benefice(baremes, 1975, 50000, unite="monnaie").remarques)


def test_les_valeurs_lues_dans_legi_y_sont():
    """Chaque montant que ``scripts/fetch/ipp_impot_revenu.py`` dit avoir lu dans
    une rédaction du code — ce qu'il ajoute à l'IPP, ce qu'il y corrige — s'y
    lit encore, quand l'index LEGI est là
    (``python scripts/fetch/dila_index.py legi --recuperer``)."""
    sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
    import ipp_impot_revenu as script

    verifiees = 0
    corrections = [(serie, [{"annee": annee, "texte": texte, **valeurs}])
                   for (serie, annee), (valeurs, texte, _) in script.CORRECTIONS.items()]
    for serie, marches in [*script.COMPLEMENTS.items(), *corrections]:
        for marche in marches:
            identifiants = [mot.strip(",;()") for mot in marche["texte"].split()
                            if mot.startswith("LEGIARTI")]
            textes = [t for t in map(_texte_legi, identifiants) if t]
            if not textes:
                continue
            tout = " ".join(textes).replace(" ", " ").replace("\xa0", " ")
            montants = [v for cle, v in marche.items() if cle not in ("annee", "monnaie", "texte",
                                                                          "origine", "taux")]
            for valeur in montants:
                for nombre in (valeur if isinstance(valeur, list) else [valeur]):
                    if isinstance(nombre, float) and nombre < 1:
                        continue
                    if nombre == 0:
                        continue
                    assert any(forme in tout for forme in _montants(nombre)), \
                        f"{serie} {marche['annee']} : {nombre} absent"
                    verifiees += 1
    if not verifiees:
        pytest.skip("l'index LEGI n'est pas là")


# -- Les lois de finances pour 1974 à 1981 -----------------------------------------
#
# Les règles des revenus de 1973 à 1980, lues au texte définitif de chaque loi de
# finances que le Sénat publie (senat.fr/leg/<session>/ta<session>_<numéro>.pdf),
# et, pour la limite d'exonération, à l'article 5, 2° bis du code, que l'index
# LEGI conserve depuis sa rédaction du 1er juillet 1979.

#: Les barèmes des revenus de 1973 à 1980, que l'article 2 des lois de finances
#: pour 1974 à 1979 et pour 1981, et l'article 3 de celle pour 1980, écrivent
#: « (deux parts) » : la limite basse de chaque tranche imposée, et son taux en
#: pour cent.
TAUX_DEPUIS_1974 = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60)
BAREMES_DES_LOIS_DE_FINANCES = {
    1973: ((9900, 10400, 12500, 19800, 29800, 44000, 92650, 184250),
           (5, 10, 15, 20, 30, 40, 50, 60)),
    1974: ((11100, 11650, 14000, 22200, 30100, 38000, 45900, 52950, 91650, 129800, 168000,
            206300), TAUX_DEPUIS_1974),
    1975: ((12250, 12850, 15400, 24450, 33150, 41800, 50500, 58250, 100800, 142750, 184800,
            226900), TAUX_DEPUIS_1974),
    1976: ((13450, 14100, 16900, 26800, 35150, 44300, 53550, 61750, 106850, 147050, 190350,
            226900), TAUX_DEPUIS_1974),
    1977: ((14500, 15200, 18200, 28800, 37800, 47600, 57550, 66400, 114850, 158050, 201800,
            238200), TAUX_DEPUIS_1974),
    1978: ((15850, 16600, 19850, 31400, 41250, 51850, 62700, 72350, 125200, 172250, 211900,
            250100), TAUX_DEPUIS_1974),
    1979: ((17450, 18250, 21650, 34250, 44550, 56000, 67750, 78150, 130250, 179150, 211900,
            250100), TAUX_DEPUIS_1974),
    1980: ((19780, 20680, 24540, 38820, 49900, 62720, 75880, 87540, 145880, 200640, 237320,
            270000), TAUX_DEPUIS_1974),
}


def test_les_baremes_de_1973_a_1980_sont_ceux_des_lois_de_finances(baremes):
    """Le barème d'une part est la moitié de celui que la loi écrit pour deux.
    L'IPP en diffère trois fois : 5 500 F et 24 450 F au lieu de 5 550 F et
    22 950 F en 1974 (loi n° 74-1129, art. 2, I : « 11 100 F à 11 650 F », « 45 900
    F à 52 950 F ») ; 37 970 F au lieu de 37 940 F en 1980 (loi n° 80-1094, art.
    2, I : « De 62 720 F à 75 880 F », lu à l'image du texte), que confirme le
    relèvement uniforme des tranches, de 12 % sur 1979 et de 13,5 % en 1981."""
    for annee, (seuils, taux) in BAREMES_DES_LOIS_DE_FINANCES.items():
        parametres = baremes.lus(annee)
        assert [2 * s for s in parametres.seuils] == [0, *seuils], annee
        assert list(parametres.taux) == pytest.approx([0.0, *(t / 100 for t in taux)]), annee


def test_la_limite_d_exoneration_des_revenus_de_1973_a_2013(baremes):
    """« Les contribuables dont le revenu, net de frais professionnels, n'excède
    pas 15 200 F, ou 16 600 F s'ils sont âgés de plus de soixante-cinq ans, sont
    exonérés de l'impôt sur le revenu » (loi de finances pour 1978, art. 2, II),
    devenu l'article 5, 2° bis du code, jusqu'aux revenus de 2013 (8 680 € ou
    9 490 €, LEGIARTI000029042469) ; de 1973 à 1976, une limite pour qui vit
    « principalement de traitements, salaires et pensions », une autre pour
    les autres (lois de finances pour 1974 à 1977). Le revenu s'apprécie par
    foyer : les salaires après leurs frais professionnels, mais avant
    l'abattement de 20 % ; les pensions après leur abattement de 10 % ; les
    bénéfices avant celui des adhérents ; la limite des plus de 65 ans vaut si
    l'un des époux l'est (DB 5 B 132 du 1er septembre 1999, n° 6 et 7)."""
    def foyer(annee, *declarants, unite="monnaie"):
        return impot_du_foyer(Foyer(tuple(Declarant(**d) for d in declarants)), annee, baremes,
                              unite=unite)
    # 1977 : 16 880 F de salaire, 15 192 F nets de 10 % de frais, est exonéré ;
    # 17 000 F, 15 300 F, paie le barème sur 12 240 F, après 20 % : 5 % de
    # 350 F, 10 % de 1 500 F et 15 % de 3 140 F.
    exonere = foyer(1977, {"salaires": 16880, "age": 40})
    assert exonere.exonere and exonere.impot == 0 and exonere.impot_avant_credits == 0
    impose = foyer(1977, {"salaires": 17000, "age": 40})
    assert not impose.exonere and impose.impot == pytest.approx(17.5 + 150 + 471)
    # 1977 : 18 400 F de pension, 16 560 F après ses 10 % : sous la limite des
    # plus de 65 ans, au-dessus de l'autre.
    assert foyer(1977, {"pensions": 18400, "age": 70}).exonere
    assert not foyer(1977, {"pensions": 18400, "age": 60}).exonere
    # Un couple dont l'un a 66 ans : 6 500 F de salaire, net du minimum de
    # 1 500 F de frais, et 9 900 F de pension, 16 400 F en tout.
    assert foyer(1977, {"salaires": 8000, "age": 60}, {"pensions": 11000, "age": 66}).exonere
    assert not foyer(1977, {"salaires": 8000, "age": 60}, {"pensions": 11000, "age": 64}).exonere
    # 1974 : 11 400 F pour qui vit de salaires ou de pensions, 10 000 F pour les
    # autres (loi n° 74-1129, art. 2, II) ; le bénéfice de 10 500 F d'un artisan
    # paie le barème de la loi : 5 % de 275 F, 10 % de 1 175 F et 15 % de
    # 3 500 F, 656,25 F, à la dizaine de centimes.
    salarie = foyer(1974, {"salaires": 11600, "age": 40})
    assert salarie.exonere and salarie.impot == 0
    artisan = foyer(1974, {"benefices": 10500, "age": 40})
    assert not artisan.exonere and artisan.impot == pytest.approx(656.3)
    # 1973 : 10 000 F et 8 000 F (loi n° 73-1150, art. 4).
    assert foyer(1973, {"salaires": 11000, "age": 40}).exonere
    assert not foyer(1973, {"benefices": 9000, "age": 40}).exonere
    # 1980 : 21 100 F ou 23 000 F (loi n° 80-1094, art. 2, III, 1) ; 25 500 F de
    # pension, 22 950 F après ses 10 %.
    assert foyer(1980, {"pensions": 25500, "age": 70}).exonere
    assert not foyer(1980, {"pensions": 25500, "age": 64}).exonere
    # 2013 : 10 500 € de pension, 9 450 € après ses 10 % ; le 2° bis ne vaut plus
    # pour les revenus de 2014.
    assert foyer(2013, {"pensions": 10500, "age": 70}, unite="euro").exonere
    assert not foyer(2014, {"pensions": 10500, "age": 70}, unite="euro").exonere


def test_les_pensions_n_ont_d_abattement_de_10_qu_a_partir_de_1977(baremes):
    """L'abattement de 10 % des pensions est « institué par l'article 3-1 de la
    loi n° 77-1467 du 30 décembre 1977 » (loi de finances pour 1979, art. 4) :
    rien avant les revenus de 1977 ; 10 %, jusqu'à 5 000 F, ensuite ; au moins
    1 800 F dès 1978 (même loi, art. 5, II). Les pensions ont les 20 % « dont
    bénéficient les salariés et pensionnés » (loi n° 73-1150, art. 5)."""
    def calcul(annee, pension):
        return impot_du_foyer(Foyer((Declarant(pensions=pension, age=70),)), annee, baremes,
                              unite="monnaie")
    avant = calcul(1976, 30000)
    assert avant.pensions_nettes == (30000,) and avant.abattement_vingt_pour_cent == 6000
    assert calcul(1965, 10000).pensions_nettes == (10000,)
    assert calcul(1977, 30000).pensions_nettes == (27000,)
    assert calcul(1978, 10000).pensions_nettes == (8200,)


def test_l_abattement_de_20_de_1973_a_1976(baremes):
    """L'abattement de 20 % des salaires et des pensions ne porte, depuis les
    revenus de 1973, que sur ce qui n'excède pas « une fois et demie la limite
    de la dernière tranche du barème correspondant à deux parts, ce chiffre
    étant arrondi à la dizaine de milliers de francs supérieure » (loi n°
    73-1150, art. 5), avec 10 % au-delà jusqu'à ce que la loi de finances pour
    1976 le supprime (art. 14). Pour 1975 et 1976, 1,5 fois 226 900 F, 340 350 F :
    350 000 F, et non les 340 000 F de l'IPP."""
    def vingt(annee, salaire):
        return impot_du_foyer(Foyer((Declarant(salaires=salaire, age=40),)), annee, baremes,
                              unite="monnaie").abattement_vingt_pour_cent
    # 400 000 F de salaire, 360 000 F après 10 % de frais.
    assert vingt(1974, 400000) == pytest.approx(0.2 * 310000 + 0.1 * 50000)
    assert vingt(1975, 400000) == pytest.approx(0.2 * 350000)
    assert vingt(1976, 400000) == pytest.approx(0.2 * 350000)


def test_l_abattement_des_personnes_agees_de_1973_a_1976(baremes):
    """La déduction des plus de 65 ans, « de 500 F », est portée à 2 000 F sous
    12 000 F de revenu net global et à 1 000 F sous 20 000 F pour les revenus de
    1973 (loi n° 73-1150, art. 3) ; puis à 2 300 F et 1 150 F sous 14 000 F et
    23 000 F (loi n° 74-1129, art. 6), 2 800 F et 1 400 F sous 17 000 F et
    28 000 F (loi n° 75-1278, art. 2, III), 3 100 F et 1 550 F sous 19 000 F et
    31 000 F (loi n° 76-1232, art. 2, III). Une pension, qui n'a pas ses 10 %
    avant 1977, y entre pour 80 %."""
    def abattement(annee, pension):
        return impot_du_foyer(Foyer((Declarant(pensions=pension, age=70),)), annee, baremes,
                              unite="monnaie").abattement_age_invalidite
    assert [abattement(1973, p) for p in (15000, 25000, 26000)] == [2000, 1000, 0]
    assert [abattement(1974, p) for p in (17500, 28750, 30000)] == [2300, 1150, 0]
    assert [abattement(1975, p) for p in (21250, 35000, 36000)] == [2800, 1400, 0]
    assert [abattement(1976, p) for p in (23750, 38750, 40000)] == [3100, 1550, 0]


def test_le_minimum_des_frais_professionnels_de_1975_a_1978(baremes):
    """« Le montant minimal de la déduction forfaitaire pour frais
    professionnels accordée aux salariés est porté de 1 200 F à 1 500 F » pour
    les revenus de 1976 (loi n° 76-1232, art. 2, IV), puis « de 1 500 F à
    1 800 F » pour ceux de 1978 (loi n° 78-1239, art. 5, I)."""
    def nets(annee):
        return impot_du_foyer(Foyer((Declarant(salaires=8000, age=40),)), annee, baremes,
                              unite="monnaie").salaires_nets
    assert [nets(annee) for annee in (1975, 1976, 1977, 1978)] == [
        (6800,), (6500,), (6500,), (6200,)]


def test_la_majoration_de_1980_n_est_pas_due_sous_200_f(baremes):
    """« La partie supérieure à 100.000 F de l'impôt sur le revenu, dû au titre
    de l'année 1980 [...] est majorée de 25 % [...]. La majoration n'est pas
    due si elle est inférieure à 200 F » (loi de finances rectificative pour
    1981, art. 1er, aux deux lectures du Sénat, des 24 et 30 juillet 1981). Le
    barème d'une part de la loi n° 80-1094 donne 50 157,50 F d'impôt à 135 000 F
    de revenu, 60 % au-delà : 100 402 F à 218 740 F, dont la majoration de
    100,50 F n'est pas due ; 102 364 F à 222 010 F, majorés de 591 F."""
    def majoration(revenu):
        return impot_d_un_revenu_imposable(Foyer((Declarant(),)), 1980, revenu, baremes,
                                           unite="monnaie").majoration_exceptionnelle
    assert majoration(218740) == 0
    assert majoration(222010) == 591


# -- Les lois de finances pour 1970 à 1973 -----------------------------------------
#
# Les règles des revenus de 1969 à 1972, lues au texte définitif des lois de
# finances pour 1970, 1971 et 1973 que le Sénat publie (senat.fr/leg/), et, pour
# celle de 1972, qu'il a rejetée et que l'Assemblée nationale a adoptée en
# lecture définitive, au texte que celle-ci a voté, que reproduit le rapport
# général de la commission des finances du Sénat (n° 27, 1971-1972, tome II) et
# que confirme celui sur la loi de finances pour 1973 (n° 66, 1972-1973, tome II).

#: Les barèmes des revenus de 1969 à 1972, pour deux parts : la limite basse de
#: chaque tranche après la première, et le taux de chaque tranche, en pour cent.
#: Jusqu'en 1971, le barème porte des points de plus, que la réduction des
#: salaires et des pensions leur rend.
BAREMES_DE_1969_A_1972 = {
    1969: ((5400, 9600, 16200, 24000, 38200, 76400, 152800), (5, 15, 20, 25, 35, 45, 55, 65)),
    1970: ((5800, 10200, 17000, 25200, 40100, 80200, 160400), (3, 13, 18, 23, 33, 43, 53, 63)),
    1971: ((6200, 10800, 17900, 26500, 42100, 84200, 168400), (3, 13, 18, 23, 33, 43, 53, 63)),
    1972: ((6600, 11500, 19000, 28100, 44000, 87000, 173000), (0, 10, 15, 20, 30, 40, 50, 60)),
}


def _seul(annee, baremes, **declarant):
    return impot_du_foyer(Foyer((Declarant(**declarant),)), annee, baremes, unite="monnaie")


def test_les_baremes_de_1969_a_1972_sont_ceux_des_lois_de_finances(baremes):
    """« Il est fait application du taux de : 5 % à la fraction du revenu qui
    n'excède pas 5.400 F [...] 65 % à la fraction du revenu supérieure à
    152.800 F » (loi n° 69-1161, art. 3, I) ; de 3 % à 63 % pour les revenus de
    1970 (loi n° 70-1199, art. 2, II) et de 1971 (loi n° 71-1061, art. 2, I) ;
    « Comprise entre 19.000 F et 28.100 F : 20 » pour ceux de 1972 (loi n°
    72-1121, art. 2), lu à l'image du texte. L'IPP porte à cette tranche 25 %, de
    1960 à 1972, et, jusqu'en 1971, les taux du barème diminués des points que
    la réduction rend aux seuls salaires et pensions."""
    for annee, (limites, taux) in BAREMES_DE_1969_A_1972.items():
        parametres = baremes.lus(annee)
        assert [2 * s for s in parametres.seuils] == [0, *limites], annee
        assert list(parametres.taux) == pytest.approx([t / 100 for t in taux]), annee


def test_la_reduction_des_salaires_et_des_pensions_jusqu_en_1971(baremes):
    """« Tous les contribuables percevant des salaires ou des pensions
    bénéficient d'une réduction d'impôt égale à 5 % du montant net imposable de
    ces salaires ou pensions » (rapport général du Sénat n° 56, 1969-1970, tome
    III, p. 14), « ce qui aboutit par conséquent à diminuer de 5 points le jeu du
    barème » (n° 54, 1970-1971, tome II, p. 77) ; 3 % pour les revenus de 1970
    (loi n° 70-1199, art. 2, III, 1) et de 1971, où elle « est maintenue et
    étendue aux revenus autres que les traitements, salaires, pensions et rentes
    viagères lorsqu'ils n'excèdent pas 15.000 F par contribuable » (loi n°
    71-1061, art. 2, II, 1°) ; « totalement intégrée au barème » en 1972 (n° 66,
    1972-1973, tome II, p. 8). Les minorations vont par paliers de la
    cotisation : 15 % jusqu'à 1 000 F, 12 % jusqu'à 1 500 F, 10 %, 8 %, 6 %,
    4 % de 500 F en 500 F, 2 % de 3 501 à 5 000 F (n° 56, tome III, p. 11)."""
    # 1969 : 20 000 F de salaire, 18 000 F après 10 % de frais, 14 400 F après
    # 20 % : 5 % de 2 700 F, 15 % de 2 100 F, 20 % de 3 300 F, 25 % de 3 900 F,
    # 35 % de 2 400 F, 2 925 F ; moins 5 % de 14 400 F, 2 205 F ; moins 8 %,
    # 176,40 F : 2 028,60 F.
    salarie = _seul(1969, baremes, salaires=20000, age=40)
    assert salarie.impot_brut == pytest.approx(2925)
    assert salarie.reduction_des_salaires == pytest.approx(720)
    assert salarie.minoration_exceptionnelle == pytest.approx(176.4)
    assert salarie.impot == pytest.approx(2028.6)
    assert not any("notes de l'IPP" in r for r in salarie.remarques)
    # 1971 : le bénéfice de 12 000 F d'un artisan : 3 % de 3 100 F, 13 % de
    # 2 300 F, 18 % de 3 550 F, 23 % de 3 050 F, 1 732,50 F ; moins 3 % de
    # 12 000 F, 1 372,50 F ; moins 12 %, 164,70 F : 1 207,80 F. À 16 000 F, rien
    # ne lui est rendu : 2 927,50 F, moins 6 %, 175,70 F : 2 751,80 F.
    artisan = _seul(1971, baremes, benefices=12000, age=40)
    assert artisan.reduction_des_salaires == pytest.approx(360)
    assert artisan.impot == pytest.approx(1207.8)
    au_dela = _seul(1971, baremes, benefices=16000, age=40)
    assert au_dela.reduction_des_salaires == 0 and au_dela.impot == pytest.approx(2751.8)
    # 1972 : 30 000 F de salaire, 21 600 F imposables : 10 % de 2 450 F, 15 % de
    # 3 750 F, 20 % de 4 550 F, 30 % de 7 550 F, 3 982,50 F ; moins 2 %,
    # 79,70 F : 3 902,80 F.
    en_1972 = _seul(1972, baremes, salaires=30000, age=40)
    assert en_1972.reduction_des_salaires == 0 and en_1972.impot == pytest.approx(3902.8)


def test_les_contribuables_ages_de_1969_a_1972(baremes):
    """Les plus de 75 ans ont, en 1969, « dans la limite de 270 F, [...] une
    réduction d'impôt égale à 5 % de leurs revenus effectivement soumis à
    l'impôt », qui « ne se cumule pas avec la réduction d'impôt visée à
    l'article 198 [...], la réduction dont le montant est le plus élevé étant
    seule retenue » (loi n° 69-1161, art. 4, II) ; 3 % dans la limite de 170 F,
    dès 70 ans, en 1970 (loi n° 70-1199, art. 2, III et VII), et de 180 F en
    1971 (loi n° 71-1061, art. 2, II, 2°). En 1972, qui a plus de 65 ans, ou est
    invalide, déduit « une somme de 500 F » d'un revenu net global « inférieur à
    12.000 F », et autant pour son conjoint (loi n° 72-1121, art. 3)."""
    # 1969 : le bénéfice de 9 000 F d'un commerçant de 76 ans : 5 % de 2 700 F,
    # 15 % de 2 100 F, 20 % de 3 300 F, 25 % de 900 F, 1 335 F ; moins 270 F,
    # 1 065 F, au-dessus de la décote de ses 70 ans (900 F) ; moins 12 %,
    # 127,80 F : 937,20 F. À 74 ans, rien ne lui est rendu : 1 335 F, moins
    # 160,20 F.
    assert _seul(1969, baremes, benefices=9000, age=76).impot == pytest.approx(937.2)
    assert _seul(1969, baremes, benefices=9000, age=74).impot == pytest.approx(1174.8)
    # Une pension de 10 000 F, 8 000 F imposables, et un bénéfice de 3 000 F :
    # 5 % de 8 000 F, 400 F, plutôt que 270 F, et non leur somme.
    mixte = _seul(1969, baremes, pensions=10000, benefices=3000, age=76)
    assert mixte.reduction_des_salaires == pytest.approx(400)
    # 1970 : 10 000 F de bénéfice à 71 ans : 3 % de 2 900 F, 13 % de 2 200 F,
    # 18 % de 3 400 F, 23 % de 1 500 F, 1 330 F ; moins 170 F, et non 3 % de
    # 10 000 F, 1 160 F ; moins 12 %, 139,20 F : 1 020,80 F.
    assert _seul(1970, baremes, benefices=10000, age=71).impot == pytest.approx(1020.8)
    # 1971 : 16 000 F de bénéfice à 72 ans : 2 927,50 F, moins 180 F,
    # 2 747,50 F ; moins 6 %, 164,90 F : 2 582,60 F.
    assert _seul(1971, baremes, benefices=16000, age=72).impot == pytest.approx(2582.6)
    # 1972 : 14 900 F de pension, 11 920 F de revenu net global, 500 F déduits ;
    # 15 000 F de pension, 12 000 F, rien.
    assert _seul(1972, baremes, pensions=14900, age=70).abattement_age_invalidite == 500
    assert _seul(1972, baremes, pensions=15000, age=70).abattement_age_invalidite == 0
    couple = impot_du_foyer(Foyer((Declarant(pensions=6000, age=70),
                                   Declarant(pensions=4000, age=66))), 1972, baremes,
                            unite="monnaie")
    assert couple.abattement_age_invalidite == 1000


def test_l_exoneration_et_la_decote_de_1969_a_1972(baremes):
    """« Les limites respectives d'application de l'exonération et de la décote
    prévues à l'article 198 ter [...] sont fixées comme suit : 230 F et 690 F
    pour les contribuables qui ont droit à une part, à une part et demie ou à
    deux parts [...] ; 100 F et 300 F par part pour les autres contribuables »,
    300 F et 900 F, ou 180 F et 540 F par part, au-delà de 70 ans (loi n°
    69-1161, art. 4, I) ; « 380 F et 1.140 F » pour une part ou une part et
    demie, « 230 F et 690 F par part » pour les autres, au-delà de 65 ans et
    pour les invalides, dès 1970 (loi n° 70-1199, art. 2, V et VI). L'impôt qui
    n'excède pas la première limite n'est pas dû."""
    # 1969 : un couple et deux enfants, trois parts, 15 000 F de salaire,
    # 10 800 F imposables : 5 % de 2 700 F et 15 % de 900 F par part, 810 F ;
    # moins 540 F, 270 F, sous les 300 F de ses trois parts.
    famille = impot_du_foyer(Foyer((Declarant(salaires=15000, age=40), Declarant(age=40)),
                                   enfants=2), 1969, baremes, unite="monnaie")
    assert famille.parts == 3 and famille.impot == 0
    assert famille.decote == pytest.approx(270)
    # 1969 : un couple de retraités de 72 ans, 10 875 F de pensions, 8 700 F
    # imposables : 5 % de 2 700 F et 15 % de 1 650 F par part, 765 F ; moins
    # 435 F, 330 F, sous les 360 F de leurs deux parts ; à 60 ans, au-dessus
    # des 230 F de tous.
    def retraites(age):
        return impot_du_foyer(Foyer((Declarant(pensions=6000, age=age),
                                     Declarant(pensions=4875, age=age))), 1969, baremes,
                              unite="monnaie")
    assert retraites(72).impot == 0 and retraites(72).decote == pytest.approx(330)
    assert retraites(60).impot > 0
    # 1970 : un invalide seul, une part et demie, 10 200 F de salaire, 9 000 F
    # après le minimum de 1 200 F de frais, 7 200 F imposables : 3 % de 2 900 F
    # et 13 % de 1 900 F par part, 501 F ; moins 216 F, 285 F, sous ses 380 F.
    invalide = _seul(1970, baremes, salaires=10200, age=40, invalide=True)
    assert invalide.parts == 1.5 and invalide.impot == 0


def test_les_majorations_de_1969_vont_par_paliers(baremes):
    """« Pour l'imposition des revenus de l'année 1969, les majorations [...]
    sont maintenues en vigueur. Toutefois leurs taux sont réduits de moitié et
    aucune majoration n'est applicable aux cotisations comprises entre 6.001 F
    et 7.000 F » (loi n° 69-1161, art. 3, V) : 2 % de 7 001 à 8 000 F, 3 %,
    4 %, 5 % de 10 001 à 10 500 F, 6 % de 10 501 à 12 000 F, 7 % jusqu'à
    14 000 F, 7,5 % au-delà (rapport général du Sénat n° 56, 1969-1970, tome
    III, p. 11)."""
    def majoration(revenu):
        return impot_d_un_revenu_imposable(Foyer((Declarant(),)), 1969, revenu, baremes,
                                           unite="monnaie").majoration_exceptionnelle
    # 32 940 F d'un revenu qui n'est ni salaire ni pension : 4 570 F jusqu'à
    # 19 100 F, 45 % de 13 840 F, 10 798 F, majorés de 6 %, 647,90 F.
    assert majoration(32940) == pytest.approx(647.9)


def test_le_minimum_des_frais_professionnels_nait_en_1970(baremes):
    """« Le montant de la ou des déductions forfaitaires pour frais
    professionnels ne peut être inférieur à 1.200 F, sans pouvoir excéder le
    montant brut de ces traitements et salaires » (loi n° 70-1199, art. 4),
    jusqu'à ce que la loi de finances pour 1977 le porte « de 1 200 F à
    1 500 F » (art. 2, IV) : 8 000 F de salaire, 7 200 F nets en 1969, 6 800 F
    de 1970 à 1975."""
    assert [_seul(annee, baremes, salaires=8000, age=40).salaires_nets
            for annee in (1969, 1970, 1972, 1973, 1974)] == [
        (7200,), (6800,), (6800,), (6800,), (6800,)]


def test_l_exoneration_des_salaries_de_1972(baremes):
    """« Les personnes physiques qui bénéficient principalement de traitements
    et salaires sont exonérées de l'impôt sur le revenu lorsque leur revenu
    brut n'excède pas 9.500 F » (loi n° 72-1121, art. 4) ; principalement,
    quand « les salaires atteignent (après déduction des frais professionnels)
    au moins la moitié du revenu net » (rapport général du Sénat n° 66,
    1972-1973, tome II, p. 11). Le retraité ne l'a pas : il relève de
    l'exonération de l'article 5, 2°, qui n'est pas calculée."""
    def foyer(*declarants):
        return impot_du_foyer(Foyer(tuple(Declarant(**d) for d in declarants)), 1972, baremes,
                              unite="monnaie")
    assert foyer({"salaires": 9500, "age": 30}).exonere
    assert not foyer({"salaires": 9510, "age": 30}).exonere
    assert not foyer({"pensions": 9000, "age": 70}).exonere
    # 7 000 F de salaire, 5 800 F nets de frais, et 2 000 F de pension : surtout
    # des salaires, 9 000 F bruts ; 2 600 F de pension, 9 600 F.
    assert foyer({"salaires": 7000, "age": 40}, {"pensions": 2000, "age": 66}).exonere
    assert not foyer({"salaires": 7000, "age": 40}, {"pensions": 2600, "age": 66}).exonere
    # 3 000 F de salaire, 1 800 F nets, et 6 000 F de pension : surtout une pension.
    assert not foyer({"salaires": 3000, "age": 40}, {"pensions": 6000, "age": 66}).exonere
