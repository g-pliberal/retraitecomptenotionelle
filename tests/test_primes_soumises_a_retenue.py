"""Les primes que la loi assujettit à la retenue pour pension.

Action 138, étape 17, douzième partie. Trois primes de la fonction publique
entrent dans l'assiette de la retenue et dans la pension, quand toutes les
autres n'ouvrent de droits qu'au RAFP :

* l'indemnité de sujétions spéciales des policiers des services actifs, depuis
  1983, « un dixième par an » jusqu'en 1992 (loi n° 57-444, article 6 bis),
  avec ses retenues supplémentaires de 1 % et de 1,2 % ;
* l'indemnité de feu des sapeurs-pompiers professionnels, depuis 1991, deux
  quinzièmes puis un quinzième par an jusqu'en 2003 (loi n° 90-1067,
  article 17), proratisée sur les années de sapeur-pompier ;
* la prime spéciale de sujétion des aides-soignants de la fonction publique
  hospitalière, depuis 2004, dans la limite de 10 % du traitement, et le
  supplément de pension qu'elle ouvre (loi n° 2003-1199, article 37).

Leur table, année par année : ``legislation/primes_soumises_a_retenue.yaml`` ;
ce que la pension en fait, à sa date d'effet : les fiches
``indemnite_sujetions_speciales_police``, ``indemnite_de_feu_sapeurs_pompiers``
et ``prime_speciale_sujetion_aides_soignants``. La part de primes de la saisie
reste l'assiette du RAFP : la prime soumise est dans le reste, avec le
traitement. Le jumeau JavaScript se compare aux témoins de chaque statut
(``scripts/construire_temoins.py``, ``STATUTS``).
"""

from __future__ import annotations

import datetime as dt
import re

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.carriere import Affiliations, Carriere, LigneRelevee, Metier
from retraite_notionnelle.donnees.primes import charger_primes_soumises
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.remuneration import bloc_droit_en_vigueur
from retraite_notionnelle.simulateur import Simulateur

PARAMETRES = Parametres()
POLICIER = "policier"
AIDE_SOIGNANT = "aide_soignant"
POMPIER = "sapeur_pompier_professionnel"
#: Les agents de la CNRACL sans prime soumise : l'adjoint administratif des
#: exemples de la CNRACL, l'agent hospitalier de catégorie active.
SEDENTAIRE = "fonctionnaire_territorial_hospitalier"
HOSPITALIER_ACTIF = "fonctionnaire_hospitalier_actif"
#: Le traitement de l'indice brut 486 des exemples de la CNRACL, par an.
TRAITEMENT_486 = 2092.18 * 12
SR = re.compile(r"SR ([\d,]+\.\d\d) € \(([\d,]+\.\d\d) €")


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


@pytest.fixture(scope="module")
def table():
    return charger_primes_soumises(PARAMETRES.racine_donnees)


def _pension(simulateur: Simulateur, carriere: Carriere, regime: str):
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}[regime]


def _parcours(simulateur: Simulateur, metiers: list[Metier], naissance: int,
              liquidation: float, sexe: str = "H") -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, mois_naissance=1,
        part_primes=0.15)


def _sr_et_traitement(detail: str) -> tuple[float, float]:
    """Le salaire de référence, prime comprise, et le traitement seul."""
    sr, traitement = SR.search(detail).groups()
    return float(sr.replace(",", "")), float(traitement.replace(",", ""))


# -- la table ------------------------------------------------------------------


def test_la_table_suit_les_textes(table):
    """Les taux à la date qui les fixe, les parts que l'intégration compte."""
    police = table.prime(POLICIER)
    assert police.taux_au(dt.date(2018, 6, 1)) == 0.27
    assert [police.part_comptee(a) for a in (1982, 1983, 1987, 1992, 2030)] == [
        0.0, 0.1, 0.5, 1.0, 1.0]
    feu = table.prime(POMPIER)
    assert (feu.taux_au(dt.date(2020, 7, 25)), feu.taux_au(dt.date(2020, 7, 26))) == (
        0.19, 0.25)
    # Le taux d'une année est la moyenne de ses mois : 19 % jusqu'au
    # 1er juillet 2020, 25 % depuis le 1er août.
    assert feu.taux_annuel(2020) == pytest.approx((7 * 0.19 + 5 * 0.25) / 12)
    assert feu.part_comptee(1990) == 0.0
    assert feu.part_comptee(1992) == pytest.approx(4 / 15, abs=1e-6)
    assert feu.part_comptee(2003) == 1.0
    soignant = table.prime(AIDE_SOIGNANT)
    assert soignant.taux_au(dt.date(2003, 12, 31)) == 0.0
    assert [soignant.part_comptee(a) for a in range(2003, 2009)] == [
        0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    # Le surveillant pénitentiaire, l'agent hospitalier de service : aucune.
    assert table.prime("fonctionnaire_etat_super_actif") is None
    assert table.prime(HOSPITALIER_ACTIF) is None


def test_la_part_de_primes_reste_l_assiette_du_rafp(table):
    """La saisie dit la part des primes que le RAFP prend ; le reste est le
    traitement et la part soumise de la prime, au taux de l'année."""
    parts = table.parts(POLICIER, 2018, 0.2)
    assert parts.traitement == pytest.approx(0.8 / 1.27)
    assert parts.prime == parts.soumise == pytest.approx(0.27 * 0.8 / 1.27)
    assert parts.traitement + parts.soumise == pytest.approx(0.8)
    # En 2005, l'aide-soignant ne compte que 40 % de sa prime : le reste est
    # avec les primes que la pension ne compte pas.
    parts = table.parts(AIDE_SOIGNANT, 2005, 0.2)
    assert parts.traitement == pytest.approx(0.8 / 1.04)
    assert parts.prime == pytest.approx(0.1 * parts.traitement)
    assert parts.soumise == pytest.approx(0.04 * parts.traitement)
    assert parts.traitement + parts.soumise == pytest.approx(0.8)
    # Avant la loi, et sans prime soumise, le reste est le traitement.
    assert table.parts(POMPIER, 1990, 0.2).traitement == pytest.approx(0.8)
    assert table.parts(HOSPITALIER_ACTIF, 2018, 0.2).traitement == pytest.approx(0.8)


def test_le_rafp_plafonne_les_primes_au_cinquieme_du_seul_traitement(simulateur, table):
    """Les primes n'entrent au RAFP que jusqu'à 20 % du « traitement
    indiciaire brut total perçu au cours de l'année » (décret n° 2004-569,
    article 2) : l'indemnité du policier n'en est pas."""
    periode = simulateur.catalogue["rafp"].periode(2018)
    soumise = table.parts(POLICIER, 2018, 0.3).soumise
    assert periode.part_du_revenu(1000.0, 0.3, soumise) == pytest.approx(
        0.2 * 1000.0 * 0.7 / 1.27)
    assert periode.part_du_revenu(1000.0, 0.3) == pytest.approx(0.2 * 1000.0 * 0.7)


# -- la retenue ----------------------------------------------------------------


def _taux_salarie(statut: str, annee: int, part_primes: float = 0.0) -> float:
    """Ce que le droit en vigueur retient au salarié pour sa retraite, en part
    de sa rémunération entière, hors de la RAFP, que la fiche prélève à part
    sur les autres primes."""
    bloc = bloc_droit_en_vigueur(CatalogueRegimes(PARAMETRES.racine_donnees),
                                 Affiliations(PARAMETRES.racine_donnees), statut, annee,
                                 part_primes)
    return sum(segment.taux for composante in bloc.composantes
               if not composante.hors_repartition
               for segment in composante.salarie)


def test_la_retenue_du_policier_fait_12_76_pour_cent_en_2018():
    """« 12,76 % » : le « taux normal de retenue pour pension (10,56 %) »,
    l'article 3 « (1 point) » et l'article 6 bis « (1,2 point) », sur
    « l'ensemble de la rémunération, hors NBI, soumise à retenue pour
    pension » (annexe au projet de loi de finances) : le traitement et
    l'indemnité."""
    assert _taux_salarie(POLICIER, 2018) == pytest.approx(0.1276)
    # Ses autres primes n'y sont pas.
    assert _taux_salarie(POLICIER, 2018, 0.2) == pytest.approx(0.1276 * 0.8)
    # Le surveillant pénitentiaire : la retenue ordinaire.
    assert _taux_salarie("fonctionnaire_etat_super_actif", 2018) == pytest.approx(0.1056)


def test_la_retenue_du_sapeur_pompier_compte_sa_bonification_et_l_integration():
    """En 2010, 7,85 % de retenue ordinaire, 2 % de la bonification du
    cinquième et 1,8 % de l'intégration de l'indemnité, sur le traitement et
    l'indemnité ; depuis 2022, l'intégration ne coûte plus rien à l'agent."""
    assert _taux_salarie(POMPIER, 2010) == pytest.approx(0.0785 + 0.02 + 0.018)
    assert _taux_salarie(POMPIER, 2022) == pytest.approx(0.1110 + 0.02)


def test_la_retenue_de_l_aide_soignant_prend_1_5_pour_cent_de_sa_prime():
    """La retenue ordinaire sur le traitement et la prime, 1,5 % de plus sur
    la prime, de 10 % du traitement."""
    assert _taux_salarie(AIDE_SOIGNANT, 2010) == pytest.approx(
        0.0785 + 0.015 * 0.1 / 1.1)
    assert _taux_salarie(HOSPITALIER_ACTIF, 2010) == pytest.approx(0.0785)


# -- la pension du policier ------------------------------------------------------


def test_le_policier_liquide_son_traitement_majore_de_l_indemnite(simulateur):
    """Le policier du cas type 8 du COR, parti à cinquante-deux ans en janvier
    2012 : son traitement de référence porte l'indemnité, au taux de 26 % de
    la veille, entière depuis 1992."""
    carriere = _parcours(simulateur, [Metier(POLICIER, 19.0, 1.0)], 1960, 52.0)
    _, pension = _pension(simulateur, carriere, "fonction_publique_etat")
    assert "+ prime de 26.00%)" in pension.detail
    sr, traitement = _sr_et_traitement(pension.detail)
    assert sr == pytest.approx(traitement * 1.26, abs=0.01)


def test_un_dixieme_par_an_de_1983_a_1992(simulateur):
    """Parti en janvier 1987, il compte la moitié de son indemnité ; parti en
    1980, rien."""
    carriere = _parcours(simulateur, [Metier(POLICIER, 20.0, 1.0)], 1932, 55.0)
    _, pension = _pension(simulateur, carriere, "fonction_publique_etat")
    assert "+ prime de 20.00% × 0.5000)" in pension.detail
    carriere = _parcours(simulateur, [Metier(POLICIER, 20.0, 1.0)], 1925, 55.0)
    _, pension = _pension(simulateur, carriere, "fonction_publique_etat")
    assert "prime" not in pension.detail


# -- la pension du sapeur-pompier : les exemples de la CNRACL ----------------------


def _releve_du_pompier(plages: list[tuple[str, int, int]], derniere: int,
                       trimestres: int) -> list[LigneRelevee]:
    """Le relevé d'un agent à l'indice brut 486 : le sapeur-pompier perçoit
    l'indemnité de feu de 25 % en plus de son traitement ; l'année du départ
    n'a que ses premiers trimestres."""
    lignes = []
    for statut, debut, fin in plages:
        brut = TRAITEMENT_486 * (1.25 if statut == POMPIER else 1.0)
        for annee in range(debut, fin + 1):
            quart = trimestres if annee == derniere else 4
            lignes.append(LigneRelevee(annee, statut, brut * quart / 4, quart))
    return lignes


def _pompier(simulateur: Simulateur, plages, naissance: int, liquidation: float,
             derniere: int, trimestres: int):
    carriere = Carriere.depuis_releve(
        annee_naissance=naissance, sexe="H",
        releve=_releve_du_pompier(plages, derniere, trimestres),
        age_liquidation=liquidation, macro=simulateur.macro, mois_naissance=1,
        jour_naissance=1)
    return _pension(simulateur, carriere, "cnracl")


def test_exemple_1_de_la_cnracl_sans_proratisation(simulateur):
    """« Un SPP né le 01/01/1968 [...] perçoit une indemnité de feu au taux de
    25 % [...]. Il est RDC au 01/10/2025 (soit à 57 ans et 9 mois). Il a fait
    toute sa carrière en qualité de SPP » : « (2092.18 + 523,04) x 0.75 =
    1961,41 € » par mois (CNRACL, « Majoration de pension Prime de feu »)."""
    resultat, pension = _pompier(simulateur, [(POMPIER, 1988, 2025)], 1968, 57.75,
                                 2025, 3)
    assert resultat.taux_liquidation == pytest.approx(0.75)
    assert "(25,106.16 € + prime de 25.00%)" in pension.detail
    assert pension.montant / 12 == pytest.approx(1961.41, abs=0.01)


def test_exemple_2_de_la_cnracl_au_prorata_des_jours_de_sapeur_pompier(simulateur):
    """L'exemple 2 : un adjoint administratif devenu sapeur-pompier, qui n'a
    pas la durée requise ; la majoration se proratise, « services accomplis en
    qualité de SPP (exprimés en jours) / Totalité des services retenus pour la
    liquidation ». Sa carrière tient ici en années entières : sept ans
    d'adjoint, vingt-neuf ans et neuf mois de sapeur-pompier, 119 trimestres
    sur 147 (120 sur 148 à la CNRACL), et la bonification du cinquième en
    plus, 167 trimestres pour 170 requis."""
    resultat, pension = _pompier(
        simulateur, [(SEDENTAIRE, 1989, 1995), (POMPIER, 1996, 2025)], 1968, 57.75,
        2025, 3)
    assert "+ prime de 25.00% × 0.8095)" in pension.detail
    sr, traitement = _sr_et_traitement(pension.detail)
    assert traitement == pytest.approx(TRAITEMENT_486, abs=0.01)
    assert sr == pytest.approx(TRAITEMENT_486 * (1 + 0.25 * 119 / 147), abs=0.01)
    # La décote de trois trimestres, puis le pourcentage de 167/170.
    assert resultat.taux_liquidation == pytest.approx(0.75 * (1 - 3 * 0.0125))
    assert pension.montant == pytest.approx(sr * 0.75 * (1 - 3 * 0.0125) * 167 / 170)


def test_exemple_4_de_la_cnracl_le_maximum_sans_autres_services(simulateur):
    """L'exemple 4 : huit trimestres d'adjoint administratif, 150 de
    sapeur-pompier et vingt de bonification, départ au 1er juillet 2027. Les
    services du sapeur-pompier et sa bonification atteignent seuls les 170
    trimestres du pourcentage maximum : « la majoration n'est pas
    proratisée » (décret n° 2003-1306, article 18, depuis le 2 janvier 2025),
    et la pension est celle de l'exemple 1."""
    resultat, pension = _pompier(
        simulateur, [(SEDENTAIRE, 1988, 1989), (POMPIER, 1990, 2027)], 1968, 59.5,
        2027, 2)
    assert resultat.trimestres_valides == 178
    assert "(25,106.16 € + prime de 25.00%)" in pension.detail
    assert pension.montant / 12 == pytest.approx(1961.41, abs=0.01)


def test_avant_2025_la_meme_carriere_se_proratisait(simulateur):
    """Né en 1965 et parti en juillet 2024, le même sapeur-pompier proratise :
    150 trimestres sur 158 ; parti un an plus tard, il ne proratise plus."""
    plages = [(SEDENTAIRE, 1985, 1986), (POMPIER, 1987, 2024)]
    _, pension = _pompier(simulateur, plages, 1965, 59.5, 2024, 2)
    assert "+ prime de 25.00% × 0.9494)" in pension.detail
    plages = [(SEDENTAIRE, 1986, 1987), (POMPIER, 1988, 2025)]
    _, pension = _pompier(simulateur, plages, 1966, 59.5, 2025, 2)
    assert "+ prime de 25.00%)" in pension.detail


def test_dix_sept_ans_de_sapeur_pompier_depuis_2011_quinze_avant(simulateur):
    """Seize ans de sapeur-pompier ne suffisent pas depuis le 1er juillet
    2011 ; ils suffisaient avant, au prorata : né à la mi-janvier 1950, parti
    en février 2010, seize ans et un mois sur trente-huit ans et un mois."""
    metiers = [Metier(SEDENTAIRE, 22.0, 1.0), Metier(POMPIER, 48.0, 1.0)]
    _, pension = _pension(simulateur, _parcours(simulateur, metiers, 1960, 64.0), "cnracl")
    assert "prime" not in pension.detail
    metiers = [Metier(SEDENTAIRE, 22.0, 1.0), Metier(POMPIER, 44.0, 1.0)]
    _, pension = _pension(simulateur, _parcours(simulateur, metiers, 1950, 60.0), "cnracl")
    assert f"+ prime de 19.00% × {(16 + 1 / 12) / (38 + 1 / 12):.4f})" in pension.detail


def test_les_droits_acquis_a_la_bascule_gardent_la_majoration(simulateur):
    """La loi diffère la jouissance de la majoration jusqu'à l'âge de la
    catégorie active ; elle ne la retire pas. Le sapeur-pompier né en 1975,
    entré à vingt et un ans, a trente ans de services à la bascule de 2026 :
    la liquidation fictive qui valorise ses droits, à cinquante et un ans,
    les compte avec l'indemnité sur laquelle il a cotisé."""
    carriere = _parcours(simulateur, [Metier(POMPIER, 21.0, 1.0)], 1975, 64.0)
    tronquee = Carriere(
        annee_naissance=1975, sexe="H",
        lignes=[ligne for ligne in carriere.lignes if ligne.annee < 2026],
        age_liquidation=51.0, jour_naissance=1, nombre_enfants=0)
    resultat = simulateur.scenario_actuel.calculer(tronquee, nature="fictive")
    (pension,) = [p for p in resultat.pensions_par_regime if p.regime == "cnracl"]
    assert "+ prime de 25.00%)" in pension.detail


def test_l_indemnite_de_feu_entre_par_quinziemes_de_1991_a_2003(simulateur):
    """Parti en janvier 1995, il compte sept quinzièmes de l'indemnité ;
    parti en 1990, rien."""
    _, pension = _pension(simulateur, _parcours(
        simulateur, [Metier(POMPIER, 20.0, 1.0)], 1935, 60.0), "cnracl")
    assert "+ prime de 19.00% × 0.4667)" in pension.detail
    _, pension = _pension(simulateur, _parcours(
        simulateur, [Metier(POMPIER, 20.0, 1.0)], 1930, 60.0), "cnracl")
    assert "prime" not in pension.detail


# -- le supplément de l'aide-soignant ----------------------------------------------

SUPPLEMENT = re.compile(r"supplément de 10\.00% du traitement([^,]*), ([\d,]+\.\d\d) €")


def _supplement(detail: str) -> tuple[str, float]:
    """Les facteurs du supplément, et son montant."""
    facteurs, montant = SUPPLEMENT.search(detail).groups()
    return facteurs, float(montant.replace(",", ""))


def test_l_aide_soignante_du_cas_type_9_a_dix_pour_cent_de_son_traitement(simulateur):
    """L'aide-soignante du cas type 9 du COR, entrée à dix-huit ans et demi,
    partie à cinquante-sept ans en janvier 2017 : la prime de ses six
    derniers mois, 10 % de son traitement, entière, sans prorata — elle était
    du corps avant 2004 —, ajoutée à la pension après la décote."""
    carriere = _parcours(simulateur, [Metier(AIDE_SOIGNANT, 18.5, 1.0)], 1960, 57.0, "F")
    _, pension = _pension(simulateur, carriere, "cnracl")
    facteurs, montant = _supplement(pension.detail)
    assert facteurs == ""
    # Le traitement de référence ne la porte pas : « SR 30,866.45 € × taux ».
    traitement = float(re.search(r"SR ([\d,]+\.\d\d) € ×", pension.detail)
                       .group(1).replace(",", ""))
    assert montant == pytest.approx(0.1 * traitement, abs=0.01)


def test_quarante_pour_cent_du_supplement_en_2005(simulateur):
    """« pour 20 % de son montant en 2004, 40 % en 2005 » ; rien avant 2004."""
    carriere = _parcours(simulateur, [Metier(AIDE_SOIGNANT, 20.0, 1.0)], 1945, 60.0, "F")
    _, pension = _pension(simulateur, carriere, "cnracl")
    assert _supplement(pension.detail)[0] == " × 0.4000"
    carriere = _parcours(simulateur, [Metier(AIDE_SOIGNANT, 20.0, 1.0)], 1940, 60.0, "F")
    _, pension = _pension(simulateur, carriere, "cnracl")
    assert "supplément" not in pension.detail


def test_entree_dans_le_corps_depuis_2004_au_prorata(simulateur):
    """Agent hospitalier de 1995 à 2010, aide-soignante ensuite jusqu'en
    2037 : le supplément « calculé à due proportion des années de services
    accomplis dans le corps des aides-soignants », vingt-sept ans et un mois
    sur quarante-deux ans et un mois, née à la mi-janvier 1975 et partie en
    février 2037."""
    metiers = [Metier(HOSPITALIER_ACTIF, 20.0, 1.0), Metier(AIDE_SOIGNANT, 35.0, 1.0)]
    _, pension = _pension(simulateur, _parcours(simulateur, metiers, 1975, 62.0, "F"),
                          "cnracl")
    assert _supplement(pension.detail)[0] == f" × {(27 + 1 / 12) / (42 + 1 / 12):.4f}"
