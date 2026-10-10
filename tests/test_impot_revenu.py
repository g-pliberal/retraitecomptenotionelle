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
    Declarant, Foyer, decote, impot_d_un_revenu_imposable, impot_du_foyer, nombre_de_parts)

RACINE = Path(__file__).resolve().parents[1]
DONNEES = RACINE / "data"
TEMOINS = RACINE / "tests" / "temoins"


@pytest.fixture(scope="module")
def baremes():
    return charger_baremes_impot_revenu(DONNEES)


def _foyer(description: dict) -> Foyer:
    declarants = tuple(Declarant(salaires=d.get("salaires", 0.0), pensions=d.get("pensions", 0.0),
                                 age=d.get("age"), invalide=d.get("invalide", False))
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
    """Une part entière pour le cinquième enfant sur les revenus de 1979, pour le
    troisième sur ceux de 1980, pour chaque enfant à partir du troisième sur
    ceux de 1986 ; une demi-part chacun avant."""
    def parts(annee, enfants):
        return impot_d_un_revenu_imposable(
            Foyer((Declarant(), Declarant()), enfants=enfants), annee, 100000, baremes,
            unite="monnaie").parts
    assert parts(1978, 5) == 4.5
    assert parts(1979, 5) == 5.0
    assert parts(1980, 3) == 4.0 and parts(1980, 4) == 4.5
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


def test_le_foyer_qui_n_est_pas_imposable_recoit_toute_sa_prime(baremes):
    """Une cotisation sous le seuil de mise en recouvrement n'est pas due (art.
    1657, 1 bis) : la prime pour l'emploi est versée en entier (art. 200 sexies,
    IV : « Si l'impôt sur le revenu n'est pas dû [...] la différence est versée
    aux intéressés » ; BOI 5 B-12-01, n° 53)."""
    calcul = impot_du_foyer(Foyer((Declarant(salaires=11650),)), 2005, baremes)
    assert 0 < calcul.impot_avant_credits < 61 and not calcul.mis_en_recouvrement
    assert calcul.impot == -calcul.prime_pour_l_emploi


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


# -- Ce que le script a lu dans l'index LEGI ----------------------------------------

def _texte_legi(identifiant: str) -> str | None:
    base = RACINE / "data" / "brut" / "dila" / "legi.sqlite"
    if not base.exists():
        return None
    with sqlite3.connect(base) as connexion:
        ligne = connexion.execute("select texte from doc where id = ?", (identifiant,)).fetchone()
    return ligne[0] if ligne else None


def _montant(valeur) -> str:
    return f"{int(valeur):,}".replace(",", " ")


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
                    assert _montant(nombre) in tout, f"{serie} {marche['annee']} : {nombre} absent"
                    verifiees += 1
    if not verifiees:
        pytest.skip("l'index LEGI n'est pas là")
