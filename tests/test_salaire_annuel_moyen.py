"""Le salaire annuel moyen du régime général, et ce qui le nourrit, datés.

Action 138, étape 16 : les règles que le relevé des modèles publics a montrées
fausses au scénario 1, relues au texte et chez la caisse — R. 351-29 et ses
rédactions, le décret n° 72-1229, les circulaires Cnav 1/73, 95/94 et 2004/27,
R. 634-1-1 pour les artisans et les commerçants, R. 381-3 et le barème de la
Cnav pour l'assurance vieillesse des parents au foyer, les colonnes de
revalorisation de la caisse depuis 1946. Le jumeau JavaScript de chaque test est
dans ``tests/js/moteur.test.js``.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import date_d_effet
from retraite_notionnelle.donnees.axes import en_vigueur_au_jour
from retraite_notionnelle.types_du_pont.carriere import AnneeCarriere
from retraite_notionnelle.config import RACINE_PROJET

from facade import Carriere, liquider, Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


#: Quatre années à la main : une pleine, une moitié travaillée et moitié
#: assimilée, une pleine, une dont le salaire ne valide aucun trimestre.
VALEURS = [(1960, 1000.0), (1961, 4000.0), (1962, 3000.0), (1963, 500.0)]
TRIMESTRES = {1960: [4, 0], 1961: [2, 2], 1962: [4, 0], 1963: [0, 0]}
VALIDANTES = {1960, 1961, 1962}


def _regle(**parametres) -> dict:
    regle = {"selection": "meilleures", "avant_la_liquidation": False,
             "calcul": "annuel", "trimestres_comptes": "cotises_et_assimiles",
             "annees_assimilees_exclues": False, "annees_sans_trimestre": "retenues"}
    regle.update(parametres)
    return regle


#: La moyenne du portage, ``moyenneSelonLaRegle``, sur des années à la main :
#: les trimestres en ``Map``, les années validantes en ``Set``, comme le
#: droit les lui passe.
_MOYENNE_DU_PORTAGE = """
import { moyenneSelonLaRegle } from "./moteur/js/droit/liquider.js";
const [regle, valeurs, trimestres, validantes, nombre, soixante, avant] = JSON.parse(process.argv[1]);
process.stdout.write(JSON.stringify(moyenneSelonLaRegle(regle, valeurs,
  new Map(trimestres), new Set(validantes), nombre, soixante, avant)));
"""


def _moyenne_du_portage(regle: dict, valeurs, trimestres: dict, validantes: set,
                        nombre: int, annee_soixante_ans: int,
                        trimestres_avant_soixante_ans: int | None = None) -> float:
    import json
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se vérifie pas ici")
    entree = [regle, valeurs, sorted(trimestres.items()), sorted(validantes), nombre,
              annee_soixante_ans, trimestres_avant_soixante_ans]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _MOYENNE_DU_PORTAGE, json.dumps(entree)],
        cwd=RACINE_PROJET, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    return json.loads(execution.stdout)


def test_la_moyenne_suit_la_version_de_la_date_d_effet():
    """Chaque version de la fiche `salaire_annuel_moyen`, sur les mêmes quatre
    années.

    Depuis 2004, l'année qui ne valide aucun trimestre sort (R. 351-29,
    circulaire 2004/27) ; de juillet 1995 à 2003, elle compte, en moyenne
    annuelle (circulaire 95/94) ; de 1973 à juin 1995, la somme des salaires
    est rapportée aux trimestres, assimilés compris, puis multipliée par quatre
    (circulaire 1/73) ; avant 1973, les dix DERNIÈRES années, sans celles de
    deux trimestres assimilés, rapportées à leurs trimestres cotisés — avant
    soixante ans, ou avant l'effet depuis juillet 1948 si c'est mieux.
    """
    moyenne = _moyenne_du_portage
    depuis_2004 = _regle(annees_sans_trimestre="exclues")
    assert moyenne(depuis_2004, VALEURS, TRIMESTRES, VALIDANTES, 10, 9999) \
        == pytest.approx(8000.0 / 3)
    assert moyenne(_regle(), VALEURS, TRIMESTRES, VALIDANTES, 10, 9999) \
        == pytest.approx(8500.0 / 4)
    # Les meilleures d'abord : sur deux années, 1961 et 1962.
    assert moyenne(_regle(), VALEURS, TRIMESTRES, VALIDANTES, 2, 9999) == 3500.0
    trimestriel = _regle(calcul="trimestriel")
    assert moyenne(trimestriel, VALEURS, TRIMESTRES, VALIDANTES, 10, 9999) \
        == pytest.approx(8500.0 * 4 / 12)
    sans_les_assimilees = _regle(selection="dernieres", calcul="trimestriel",
                                 trimestres_comptes="cotises", annees_assimilees_exclues=True)
    # Les deux dernières années d'avant 1963, l'année des soixante ans, sans
    # 1961 et ses deux trimestres assimilés : 1960 et 1962.
    assert moyenne(sans_les_assimilees, VALEURS, TRIMESTRES, VALIDANTES, 2, 1963) \
        == pytest.approx(4000.0 * 4 / 8)
    # Depuis juillet 1948, les deux dernières d'avant l'effet, 1962 et 1963,
    # valent mieux : 3 500 € sur quatre trimestres.
    depuis_1948 = dict(sans_les_assimilees, avant_la_liquidation=True)
    assert moyenne(depuis_1948, VALEURS, TRIMESTRES, VALIDANTES, 2, 1963) \
        == pytest.approx(3500.0 * 4 / 4)


def _carriere(annee_naissance: int, age_liquidation: float, lignes) -> Carriere:
    return Carriere.depuis_lignes(
        annee_naissance, "H",
        [AnneeCarriere(annee=annee, revenu=revenu, affiliation="salarie_prive_non_cadre",
                       trimestres_valides=trimestres)
         for annee, revenu, trimestres in lignes],
        age_liquidation=age_liquidation)


def test_une_annee_sans_trimestre_ne_compte_plus_depuis_2004(simulateur):
    """Un salarié né en 1950, vingt années à 30 000 €, puis une année à
    100 €, qui ne valide aucun trimestre : liquidé en 2012, son salaire moyen
    est celui des vingt bonnes années ; liquidé en 2003, la petite année tirait
    sa moyenne vers le bas. C'est ce que trois modèles publics faisaient et que
    le dépôt ne faisait pas (OpenFisca-France-Pension, calcul_pension, CALIPER)."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    lignes = [(annee, 30_000.0, 4) for annee in range(1985, 2001)]
    lignes.append((2001, 100.0, 0))
    code = "regime_general"

    tardive = _carriere(1950, 62, lignes)
    periode = simulateur.catalogue[code].a_la_date(date_d_effet(tardive))
    revalorise = [min(30_000.0, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 2012, tardive.mois_liquidation)
                  for annee in range(1985, 2001)]
    sam = liquider.salaire_de_reference(actuel, code, tardive, periode, 2012, True, 1950)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) / len(revalorise))

    precoce = _carriere(1950, 53, lignes)
    periode = simulateur.catalogue[code].a_la_date(date_d_effet(precoce))
    revalorise = [min(revenu, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 2003, precoce.mois_liquidation)
                  for annee, revenu, _ in lignes]
    sam = liquider.salaire_de_reference(actuel, code, precoce, periode, 2003, True, 1950)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) / len(revalorise))


def test_avant_juillet_1995_la_moyenne_se_rapporte_aux_trimestres(simulateur):
    """Une année d'entrée qui ne valide que deux trimestres compte pour deux
    trimestres, non pour une année : avant le 1er juillet 1995, la somme des
    salaires retenus est rapportée à leurs trimestres et multipliée par quatre
    (circulaire Cnav 1/73 ; circulaire 95/94)."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    lignes = [(1975, 4_000.0, 2)] + [(annee, 20_000.0, 4) for annee in range(1976, 1985)]
    carriere = _carriere(1925, 65, lignes)
    periode = simulateur.catalogue["regime_general"].a_la_date(date_d_effet(carriere))
    revalorise = [min(revenu, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 1990, carriere.mois_liquidation)
                  for annee, revenu, _ in lignes]
    sam = liquider.salaire_de_reference(actuel, "regime_general", carriere, periode, 1990,
                                        True, 1925)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) * 4 / 38)


def test_les_artisans_et_commercants_ont_leur_table(simulateur):
    """R. 634-1-1 : vingt années pour un commerçant né en 1948, quinze pour
    1943, vingt-quatre pour 1952, quand les salariés en ont vingt-cinq dès
    1948 ; depuis 2026, la règle commune de R. 173-3-2."""
    actuel = simulateur.scenario_actuel
    periode = simulateur.catalogue["rsi"].a_la_date("2010-01-01")
    for naissance, attendu in ((1943, 15), (1948, 20), (1952, 24), (1953, 25)):
        carriere = _carriere(naissance, 2010.5 - naissance, [(2000, 30_000.0, 4)])
        assert liquider.nombre_d_annees_retenues(
            actuel, periode, carriere, naissance) == attendu, naissance
    salarie = simulateur.catalogue["regime_general"].a_la_date("2010-01-01")
    carriere = _carriere(1948, 62, [(2000, 30_000.0, 4)])
    assert liquider.nombre_d_annees_retenues(actuel, salarie, carriere, 1948) == 25


def test_l_assiette_de_l_avpf_est_celle_de_la_cnav(simulateur):
    """R. 381-3 : 169 heures par mois du SMIC du 1er juillet précédent, que la
    Cnav publie depuis la naissance de l'AVPF, le 1er juillet 1972 — 1 715,35 €
    par mois en 2021, 2 031,38 € en 2026 (circulaire 2025/33). Au-delà, le texte,
    sur le SMIC du 1er juillet 2026 (12,31 €)."""
    macro = simulateur.macro
    assert macro.revenu_avpf(1971) == 0.0
    assert macro.revenu_avpf(1972) == pytest.approx(6 * 667.32 / 6.55957)
    assert macro.revenu_avpf(2021) == pytest.approx(12 * 1_715.35)
    assert macro.revenu_avpf(2026) == pytest.approx(12 * 2_031.38)
    assert macro.revenu_avpf(2027) == pytest.approx(2_028 * 12.31)


def test_l_avpf_compte_avant_avril_1983(simulateur):
    """L'assurance vieillesse des mères au foyer porte un salaire au compte du
    régime général depuis le 1er juillet 1972 (loi n° 72-8 ; décret n° 73-88,
    article 3) : une pension de janvier 1983, liquidée sous les règles d'avant
    l'ordonnance de 1982, le compte dans son salaire annuel moyen. Les périodes
    de 1972 à 1982 l'omettaient jusqu'au 14 octobre 2026 (action 131)."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1918, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=50, age_liquidation=65, niveau_salaire=0.4,
        profil_carriere="plat", nombre_enfants=2, jour_naissance=1,
        interruptions={a: "education_enfant" for a in range(1972, 1978)})
    assert en_vigueur_au_jour(simulateur.catalogue["regime_general"].liquidation,
                              "1982-01-01")["au"] == "1983-04-01"
    resultat = simulateur.scenario_actuel.calculer(carriere)
    applique = {a.code: a.montant for a in resultat.avantages_appliques}
    assert applique["avpf"] == pytest.approx(7.0812, abs=1e-3)


def test_l_avpf_du_pere_ne_court_que_depuis_1985(simulateur):
    """La caisse affilie les femmes à l'AVPF « depuis le 01/07/1972 », les hommes
    « depuis le 01/07/1979 », et de 1979 à 1984 « uniquement s'ils assumaient la
    charge d'un enfant ou d'un adulte handicapé » ; « Depuis le 01/01/1985, la
    condition d'affiliation était identique à celle des femmes » (exposé
    « Parent au foyer - AVPF » de la Cnav, 24 octobre 2025 ; circulaire Cnav
    25/79 ; décret n° 73-88, article 1er, de 1978 à août 1985 : « les mères de
    famille et les femmes », « les femmes isolées »). La saisie ne dit pas le
    handicap : le père n'a l'AVPF que depuis 1985. Douze fois l'assiette
    mensuelle de la Cnav (assiette_avpf.csv) : 253,141593 € en 1978, 286,700195
    en 1979, 563,971419 en 1984, 614,210992 en 1985, 770,597768 en 1990."""
    annees = (1978, 1979, 1984, 1985, 1990)

    def avpf(sexe: str) -> list[float]:
        carriere = simulateur.carriere_simple(
            annee_naissance=1950, sexe=sexe, affiliation="salarie_prive_non_cadre",
            age_debut=20, age_liquidation=65, niveau_salaire=1.0,
            profil_carriere="plat", nombre_enfants=2, jour_naissance=1,
            interruptions={a: "education_enfant" for a in annees})
        return [next(l for l in carriere.lignes if l.annee == a).revenu_avpf
                for a in annees]

    assert avpf("F") == pytest.approx(
        [3_037.699116, 3_440.40234, 6_767.657028, 7_370.531904, 9_247.173216], abs=1e-6)
    assert avpf("H") == pytest.approx([0, 0, 0, 7_370.531904, 9_247.173216], abs=1e-6)


def test_la_colonne_de_revalorisation_est_celle_de_la_date_d_effet(simulateur):
    """Trois coefficients recopiés à la main de la page de la Cnav des
    coefficients d'avant 2013 et du barème d'avril 2013, qu'un défaut du
    récupérateur ne pourrait pas reproduire : le salaire de 1970 d'un départ de
    janvier 1990, celui de 1947 d'un départ de juin 1949, celui de 1990 d'un
    départ de mai 2013."""
    lu = simulateur.macro.coefficient_revalorisation_portee_au_compte
    assert lu(1970, 1990, 1) == pytest.approx(5.629)
    assert lu(1947, 1949, 6) == pytest.approx(1.6)
    assert lu(1990, 2013, 5) == pytest.approx(1.431)


def test_avant_1972_le_trimestre_se_valide_au_trimestre_de_l_avts(simulateur):
    """R. 351-9 (action 138, étape 6) : de 1949 à 1971, autant de trimestres que
    le salaire annuel représente de fois « le montant trimestriel de
    l'allocation aux vieux travailleurs salariés au 1er janvier », celui des
    villes de plus de 5 000 habitants jusqu'en 1962 ; de 1946 à 1948, autant de
    fois 18 F. Le modèle validait quatre trimestres à toute année travaillée
    avant 1972 ; avant 1946, la règle se lit sur la retenue (test suivant).
    Les montants viennent du barème de la Cnav : 34 000 anciens francs au
    1er octobre 1948, 72 380 au 1er janvier 1956, 800 F au 1er avril 1962 — qui
    ne compte qu'en 1963 —, 1 750 F au 1er octobre 1970 (décret n° 70-879)."""
    valides = simulateur.macro.trimestres_valides

    def francs(montant: float) -> float:
        return montant / 6.55957

    assert [valides(francs(f), 1946) for f in (17.99, 18.0, 71.99, 72.0)] == [0, 1, 3, 4]
    assert [valides(francs(f), 1949) for f in (84.99, 85.0, 170.0)] == [0, 1, 2]
    assert [valides(francs(f), 1962) for f in (180.95, 723.79, 723.80)] == [1, 3, 4]
    assert [valides(francs(f), 1963) for f in (199.99, 200.0)] == [0, 1]
    assert [valides(francs(f), 1971) for f in (437.49, 437.50, 1_749.0, 1_750.0)] == [
        0, 1, 3, 4]
    # 1972 : 200 heures du SMIC de janvier, 3,94 F, la règle d'avant inchangée.
    assert [valides(francs(f), 1972) for f in (787.0, 788.0)] == [0, 1]


def test_avant_1946_le_trimestre_se_lit_sur_la_retenue(simulateur):
    """R. 351-9, rédactions de 1985 à 2025, et l'article 71 du décret
    n° 45-0179 (action 138, étape 6) : les périodes d'assurance comptent « du
    1er juillet 1930 » ; de 1936 à 1941, un trimestre « au cours [duquel]
    l'assuré a subi sur son salaire une retenue au moins égale à 15 anciens
    francs » ; de 1942 à 1945, autant de trimestres que la retenue annuelle
    « représente de fois 15 F (anciens) », quatre au plus. La retenue est la
    moitié de la double contribution (loi du 30 avril 1930, article 2) : 4 % de
    8 % jusqu'en 1944, puis la moitié de 9, 11, 12 et 12 % aux quatre trimestres
    de 1945, 5,5 % sur l'année. Au-delà du plafond d'assujettissement (loi du
    30 avril 1930, article 1er), aucune retenue : 15 000 anciens francs, 21 000
    en 1937, 30 000 au 1er juillet 1938, 42 000 en 1942, 48 000 en 1944, 60 000
    au 1er septembre 1944, 120 000 au 1er avril 1945 et jusqu'à la fin de 1946
    (barème de la Cnav), au prorata des mois de chaque montant. De 1930 à 1935,
    le texte compte des cotisations journalières, soixante par trimestre, que le
    salaire ne dit pas : le modèle en compte un par trimestre civil travaillé."""
    valides = simulateur.macro.trimestres_valides

    def francs(montant: float) -> float:
        return montant / 6.55957

    # Rien avant le 1er juillet 1930 ; deux trimestres en 1930, un pour qui
    # commence en octobre.
    assert valides(francs(100.0), 1929) == 0
    assert valides(francs(100.0), 1930) == 2
    assert valides(francs(25.0), 1930, fraction=0.25) == 1
    # De 1931 à 1935, quatre, jusqu'au plafond d'assujettissement de 150 F.
    assert [valides(francs(f), 1933) for f in (1.0, 150.0, 150.01)] == [4, 4, 0]
    # 1937 : 4 % de retenue, 3,75 F de salaire par trimestre ; plafond de 210 F.
    assert [valides(francs(f), 1937) for f in (3.74, 3.75, 14.99, 15.0)] == [0, 1, 3, 4]
    assert [valides(francs(f), 1937) for f in (210.0, 210.01)] == [4, 0]
    # 1938 : 210 F six mois, 300 F six mois, 255 F sur l'année, 127,50 F sur la
    # moitié d'une année.
    assert [valides(francs(f), 1938) for f in (255.0, 255.01)] == [4, 0]
    assert [valides(francs(f), 1938, fraction=0.5) for f in (127.5, 127.51)] == [4, 0]
    # 1943 : la retenue annuelle, autant de fois 0,15 F ; plafond de 420 F.
    assert [valides(francs(f), 1943) for f in (7.49, 7.5, 420.0, 420.01)] == [1, 2, 4, 0]
    # 1944 : 480 F huit mois, 600 F quatre mois, 520 F sur l'année.
    assert [valides(francs(f), 1944) for f in (520.0, 520.01)] == [4, 0]
    # 1945 : 5,5 % de retenue, 2,7272… F par trimestre ; 600 F trois mois,
    # 1 200 F neuf mois, 1 050 F sur l'année.
    assert [valides(francs(f), 1945) for f in (2.72, 2.73, 10.90, 10.91)] == [0, 1, 3, 4]
    assert [valides(francs(f), 1945) for f in (1_050.0, 1_050.01)] == [4, 0]
    # 1946 : le salaire de R. 351-9, 18 F, sous le plafond d'assujettissement
    # de 1 200 F, que la Cnav date jusqu'au 31 décembre 1946.
    assert [valides(francs(f), 1946) for f in (18.0, 1_200.0, 1_200.01)] == [1, 4, 0]
    # Un statut que les assurances sociales ne couvraient pas garde ses quatre.
    assert valides(francs(1_000.0), 1940, assure_social=False) == 4
    assert valides(francs(1.0), 1925, assure_social=False) == 4


def test_les_annees_des_assurances_sociales_comptent_a_la_duree_du_regime(simulateur):
    """Les trimestres de 1930 à 1944 sont des trimestres du régime général :
    R. 351-9, rédaction de 1985 à 2014 (LEGIARTI000006749353), compte « les
    périodes d'assurance accomplies du 1er juillet 1930 au 31 décembre 1935 »,
    puis celles de 1936 à 1941 et de 1942 à 1945, avec celles d'après, parmi
    les « trimestres d'assurance valables pour le calcul de la pension »
    (article 71 du décret n° 45-0179, LEGIARTI000006760608, de 1983 à 1985) ;
    aux salariés agricoles, « entre le 1er juillet 1930 et le 31 décembre
    1945, il est décompté un trimestre pour tout versement correspondant à
    cinquante jours de travail » (décret n° 50-1225, article 58, de 1983 à
    1988). La pension se proratise donc sur les deux durées réunies.

    Posé à la main : né en 1912, salarié de 1932 à 1976, parti à 65 ans en
    1977, treize années aux assurances sociales, 52 trimestres, et 128 au
    régime général : 180, bornés aux 150 de la pension entière. Née en 1924,
    salariée de 1938 à 1950, partie à 65 ans en 1989 : sept années avant 1945,
    28 trimestres, et six après, 24 : 52 sur 150."""
    from retraite_notionnelle.types_du_pont.carriere import LigneRelevee

    def francs(montant: float) -> float:
        return montant / 6.55957

    def detail(carriere, regime: str) -> str:
        resultat = simulateur.scenario_actuel.calculer(carriere)
        return next(p.detail for p in resultat.pensions_par_regime if p.regime == regime)

    for statut, regime in (("salarie_prive_non_cadre", "regime_general"),
                           ("salarie_agricole", "msa_salaries")):
        carriere = simulateur.carriere_simple(
            annee_naissance=1912, sexe="H", affiliation=statut, age_debut=20,
            age_liquidation=65, niveau_salaire=1.0, profil_carriere="plat",
            jour_naissance=1)
        par_annee = {l.annee: l.trimestres_valides for l in carriere.lignes}
        assert sum(n for a, n in par_annee.items() if a < 1945) == 52
        assert sum(n for a, n in par_annee.items() if a >= 1945) >= 128
        assert "× 150/150" in detail(carriere, regime), statut

    lignes = ([LigneRelevee(a, "salarie_prive_non_cadre", francs(200.0))
               for a in range(1938, 1945)]
              + [LigneRelevee(a, "salarie_prive_non_cadre", francs(500.0))
                 for a in range(1945, 1949)]
              + [LigneRelevee(a, "salarie_prive_non_cadre", francs(2_000.0))
                 for a in (1949, 1950)])
    carriere = simulateur.carriere_releve(1924, "F", lignes, 65.0)
    par_annee = {l.annee: l.trimestres_valides for l in carriere.lignes}
    assert sum(n for a, n in par_annee.items() if a < 1945) == 28
    assert sum(n for a, n in par_annee.items() if a >= 1945) == 24
    assert "× 52/150" in detail(carriere, "regime_general")


def test_avant_1946_la_retenue_ne_lit_que_les_assures_sociaux(simulateur):
    """Le statut de l'année dit si la retenue compte : un cadre payé 400 F en
    1940, au-delà du plafond d'assujettissement de 300 F, ne cotisait pas aux
    assurances sociales et ne valide rien ; le même traitement d'un
    fonctionnaire de l'État, dont la pension civile compte les services, en
    valide quatre ; 2 F de salaire, 0,08 F de retenue, aucun."""
    from retraite_notionnelle.types_du_pont.carriere import LigneRelevee

    def francs(montant: float) -> float:
        return montant / 6.55957

    def trimestres(statut: str, montant: float) -> int:
        carriere = simulateur.carriere_releve(
            1915, "H", [LigneRelevee(1940, statut, francs(montant))], 60.0)
        return {ligne.annee: ligne.trimestres_valides for ligne in carriere.lignes}[1940]

    assert trimestres("salarie_prive_cadre", 400.0) == 0
    assert trimestres("salarie_prive_non_cadre", 200.0) == 4
    assert trimestres("salarie_prive_non_cadre", 2.0) == 0
    assert trimestres("fonctionnaire_etat", 400.0) == 4


def test_le_salaire_d_un_non_assujetti_n_entre_pas_au_salaire_annuel_moyen(simulateur):
    """Le cadre payé 1 500 F en 1945 et 2 000 F en 1946, au-delà du plafond
    d'assujettissement de 1 050 F et de 1 200 F, ne cotisait pas : la caisse n'a
    pas son salaire, et R. 351-9 ne connaît que « le salaire annuel
    correspondant aux retenues subies ». Ses deux années, que le routage porte
    au régime général, n'entrent pas dans le salaire annuel moyen d'une pension
    de 1980, qui se calcule au trimestre jusqu'en 1995 (circulaire Cnav 1/73) :
    avec un salaire et sans trimestre, elles le gonfleraient."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    code = "regime_general"
    lignes = [AnneeCarriere(annee=annee, revenu=macro.plafond_securite_sociale(annee) / 2,
                            affiliation="salarie_prive_non_cadre", trimestres_valides=4)
              for annee in range(1950, 1976)]
    anciennes = [AnneeCarriere(annee=1945, revenu=1_500.0 / 6.55957,
                               affiliation="salarie_prive_cadre", trimestres_valides=0),
                 AnneeCarriere(annee=1946, revenu=2_000.0 / 6.55957,
                               affiliation="salarie_prive_cadre", trimestres_valides=0)]
    periode = simulateur.catalogue[code].a_la_date("1980-01-01")

    def sam(lignes_de_la_carriere: list[AnneeCarriere]) -> float:
        carriere = Carriere.depuis_lignes(1915, "H", lignes_de_la_carriere,
                                          age_liquidation=65)
        return liquider.salaire_de_reference(actuel, code, carriere, periode, 1980, True,
                                             1915)

    assert sam(anciennes + lignes) == pytest.approx(sam(lignes))


def test_la_retenue_se_lit_selon_le_statut_et_l_annee(simulateur):
    from retraite_notionnelle.types_du_pont.carriere import LigneRelevee

    releves = [[{"annee": annee, "affiliation": statut, "revenu": francs / 6.55957}
                for annee in (1929, 1930, 1938, 1946)]
               for statut, francs in (("salarie_prive_cadre", 400.0),
                                      ("salarie_prive_non_cadre", 200.0),
                                      ("salarie_prive_non_cadre", 2.0),
                                      ("fonctionnaire_etat", 400.0))]
    attendus = [[[l.annee, l.trimestres_valides] for l in simulateur.carriere_releve(
                    1915, "H", [LigneRelevee(**ligne) for ligne in releve], 60.0).lignes]
                for releve in releves]
    # 1929, 1930, 1938, 1946 : le cadre à 400 F n'est assujetti qu'en 1946 ; le
    # non-cadre à 200 F dès que le plafond le dépasse ; 2 F de salaire valent
    # les deux trimestres de 1930, puis trop peu de retenue ; le fonctionnaire
    # garde les siens.
    assert [[t for _, t in lignes] for lignes in attendus] == [
        [0, 0, 0, 4], [0, 0, 4, 4], [0, 2, 0, 0], [4, 4, 4, 4]]


def test_outre_mer_le_trimestre_se_valide_au_seuil_du_departement(simulateur):
    """R. 753-21 et R. 351-9 (action 138, étape 6) : en Guadeloupe, en Guyane,
    en Martinique et à La Réunion, les cotisations comptent « depuis le
    1er janvier 1948 » ; en 1948, autant de trimestres que le salaire représente
    de fois « 1.800 F métropolitains », ou « 900 F. C. F. A. » à La Réunion ;
    depuis 1949, le trimestre de l'allocation aux vieux travailleurs salariés au
    1er janvier « dans les départements mentionnés à l'article L. 751-1 », que
    R. 351-39 ne garde qu'avant 1952 — 3 750, 5 625 et 8 000 anciens francs de
    1949 à 1951 au barème de la Cnav, le seul qui les écrive ; de 1972 à 2013,
    200 heures du SMIC « en vigueur dans ledit département au 1er janvier ».
    Les SMIC viennent du Journal officiel : la semaine de 40 heures à 220,74 F
    aux Antilles et en Guyane au 1er décembre 1974 (arrêté du 29 novembre 1974),
    à 593,36 F et 553,64 F au 1er janvier 1982 (arrêté du 30 décembre 1981) ; la
    semaine de 39 heures à 1 048,92 F et 1 012,07 F au 1er janvier 1991 (décret
    n° 90-1153), à 1 094,37 F dans les quatre départements en 1992 (décret
    n° 92-17) ; 36,98 F de l'heure, celui de la métropole, au 1er janvier 1996
    (décret n° 95-1312)."""
    valides = simulateur.macro.trimestres_valides

    def francs(montant: float) -> float:
        return montant / 6.55957

    # Avant 1948, aucune cotisation d'assurances sociales outre-mer.
    assert valides(francs(1_000.0), 1947, "martinique") == 0
    assert valides(francs(1_000.0), 1940, "reunion") == 0
    assert [valides(francs(f), 1948, "guadeloupe") for f in (17.99, 18.0)] == [0, 1]
    assert [valides(francs(f), 1948, "reunion") for f in (17.99, 18.0, 72.0)] == [0, 1, 4]
    # De 1949 à 1951, l'allocation des départements d'outre-mer, plus basse.
    assert [valides(francs(f), 1949, "guyane") for f in (37.49, 37.50, 150.0)] == [0, 1, 4]
    assert valides(francs(37.50), 1949) == 0
    assert [valides(francs(f), 1950, "martinique") for f in (56.24, 56.25)] == [0, 1]
    assert [valides(francs(f), 1951, "reunion") for f in (79.99, 80.0)] == [0, 1]
    # En 1952, celle de la métropole.
    assert [valides(francs(f), 1952, "martinique") for f in (149.49, 149.50)] == [0, 1]
    # De 1972 à 1995, le SMIC du département, plus bas à La Réunion.
    assert [valides(francs(f), 1975, "guadeloupe") for f in (1_103.69, 1_103.70)] == [0, 1]
    assert [valides(francs(f), 1982, "martinique") for f in (2_966.79, 2_966.80)] == [0, 1]
    assert [valides(francs(f), 1982, "reunion") for f in (2_768.19, 2_768.20)] == [0, 1]
    assert valides(francs(2_966.80), 1982) == 0
    assert [valides(francs(f), 1991, "guyane") for f in (5_379.06, 5_379.08)] == [0, 1]
    assert [valides(francs(f), 1991, "reunion") for f in (5_190.09, 5_190.11)] == [0, 1]
    assert [valides(francs(f), 1992, "reunion") for f in (5_612.14, 5_612.16)] == [0, 1]
    # Depuis 1996, le SMIC de la métropole : 6 484 F, le seuil de 1995, ne
    # valident plus rien.
    assert [valides(francs(f), 1996, "reunion") for f in (6_484.0, 7_396.01)] == [0, 1]


def test_le_seuil_d_un_trimestre_est_celui_qu_un_releve_se_lit_contre(simulateur):
    """Le revenu qui valide un trimestre, année par année (R. 351-9), que le
    contrôle d'un relevé montre en regard de chaque année (action 138,
    étape 10) : 200 heures du SMIC du 1er janvier de 1972 à 2013 — 8,71 € de
    l'heure en 2009, 1 742 € ; 9,43 € en 2013, 1 886 € —, 150 heures depuis
    2014 — 9,53 €, 1 429,50 € ; 9,61 € en 2015, 1 441,50 € ; de 1946 à 1971, le
    salaire que R. 351-9 fixe, 18 F en 1946, 437,5 F en 1971. Outre-mer, celui
    du département (R. 753-21), 3 750 anciens francs en Guyane en 1949, rien
    avant 1948 : un seuil infini ; le SMIC de la métropole depuis 1996. Avant
    1946, aucun montant : la retenue des assurances sociales les fait."""
    seuil = simulateur.macro.seuil_d_un_trimestre

    def francs(montant: float) -> float:
        return montant / 6.55957

    assert seuil(2009) == pytest.approx(1_742.0)
    assert seuil(2013) == pytest.approx(1_886.0)
    assert seuil(2014) == pytest.approx(1_429.50)
    assert seuil(2015) == pytest.approx(1_441.50)
    assert seuil(1946) == pytest.approx(francs(18.0))
    assert seuil(1971) == pytest.approx(francs(437.5))
    assert seuil(1945) is None
    assert seuil(1947, "martinique") == float("inf")
    assert seuil(1949, "guyane") == pytest.approx(francs(37.50))
    assert seuil(1949) == pytest.approx(francs(85.0))
    assert seuil(1996, "reunion") == seuil(1996)
    # Le seuil est celui que les trimestres valident : un revenu qui l'atteint
    # en valide un, un centime de moins aucun.
    for annee, departement in ((1950, ""), (1975, "guadeloupe"), (2009, ""), (2026, "")):
        montant = seuil(annee, departement)
        valides = simulateur.macro.trimestres_valides
        assert valides(montant, annee, departement) == 1
        assert valides(montant - 0.01, annee, departement) == 0


def test_les_annees_d_avant_1948_ne_sont_prises_qu_a_defaut():
    """R. 351-29, de 1985 à 2025 : les années « accomplies postérieurement au
    31 décembre 1947 » ; « lorsque l'assuré ne justifie pas de [dix, puis
    vingt-cinq] années civiles d'assurance postérieurement au 31 décembre 1947,
    les années antérieures sont prises en considération en remontant à partir
    de cette date jusqu'à concurrence de [ce nombre] ». La rédaction du 1er
    janvier 2026 (LEGIARTI000053335651) n'a plus cette phrase, mais R. 351-39
    (décret n° 2025-1409, article 2, 32°) la garde à qui a été assuré « au
    titre de périodes antérieures de plus de soixante ans » : toute année
    d'avant 1948.

    Posé à la main : 1946 et 1947 valent plus que toutes les autres."""
    valeurs = [(1946, 9000.0), (1947, 8000.0), (1948, 1000.0), (1949, 2000.0), (1950, 3000.0)]
    trimestres = {annee: [4, 0] for annee, _ in valeurs}
    validantes = {annee for annee, _ in valeurs}
    a_defaut = _regle(annees_sans_trimestre="exclues", derniere_annee_a_defaut=1947)
    # Une règle qui ne nomme pas cette année classe toutes les années ensemble :
    # celle des artisans et des commerçants, dont le régime naît en 1949.
    assert _moyenne_du_portage(_regle(), valeurs, trimestres, validantes, 2, 1990) \
        == pytest.approx((9000.0 + 8000.0) / 2)
    # Trois années après 1947 pour trois retenues : aucune d'avant 1948.
    assert _moyenne_du_portage(a_defaut, valeurs, trimestres, validantes, 3, 1990) \
        == pytest.approx((1000.0 + 2000.0 + 3000.0) / 3)
    # Deux retenues : les deux meilleures d'après 1947.
    assert _moyenne_du_portage(a_defaut, valeurs, trimestres, validantes, 2, 1990) \
        == pytest.approx((2000.0 + 3000.0) / 2)
    # Quatre retenues, trois après 1947 : on remonte d'une année, 1947, et non
    # à la meilleure, 1946.
    assert _moyenne_du_portage(a_defaut, valeurs, trimestres, validantes, 4, 1990) \
        == pytest.approx((1000.0 + 2000.0 + 3000.0 + 8000.0) / 4)


#: La version des liquidations d'avant le 1er juillet 1948, telle que la fiche
#: la porte depuis la lecture du décret n° 45-0179 (lot 1 des fac-similés).
AVANT_JUILLET_1948 = _regle(selection="dernieres", calcul="trimestriel",
                            trimestres_comptes="cotises", annees_assimilees_exclues=False,
                            apres_soixante_ans_a_defaut=True)


def test_avant_juillet_1948_les_trimestres_d_apres_soixante_ans_completent_les_dix_annees():
    """Décret n° 45-0179 du 29 décembre 1945, article 74, § 4, rédaction
    d'origine (JO du 30 décembre 1945, p. 8713) : « A défaut de justification
    de quarante trimestres d'assurance avant l'âge de soixante ans, seront pris
    en considération, pour le calcul du salaire annuel moyen, jusqu'à
    concurrence de ce nombre et dans leur ordre chronologique, les trimestres
    d'assurance accomplis postérieurement au soixantième anniversaire » ; la
    circulaire n° 151 du 5 août 1946 le reprend. Le modèle compte en années
    civiles : l'année des soixante ans est la première d'après.

    Posé à la main, cinq années retenues, soixante ans en 1940 : avant, 1937
    et 1938 ; il en manque trois, prises dans l'ordre chronologique, 1940,
    1941 et 1942, et non 1943, la meilleure et la dernière. 2 000 + 3 000 +
    1 000 + 4 000 + 5 000 = 15 000 € sur vingt trimestres : 3 000 € l'an."""
    valeurs = [(1937, 2000.0), (1938, 3000.0), (1940, 1000.0), (1941, 4000.0),
               (1942, 5000.0), (1943, 9000.0)]
    trimestres = {annee: [4, 0] for annee, _ in valeurs}
    validantes = {annee for annee, _ in valeurs}
    assert _moyenne_du_portage(AVANT_JUILLET_1948, valeurs, trimestres, validantes, 5, 1940) \
        == pytest.approx(15000.0 * 4 / 20)
    # Avec assez d'années avant soixante ans, aucune d'après n'entre : les deux
    # dernières d'avant 1940, 1937 et 1938.
    assert _moyenne_du_portage(AVANT_JUILLET_1948, valeurs, trimestres, validantes, 2, 1940) \
        == pytest.approx(5000.0 * 4 / 8)


def test_avant_juillet_1948_le_complement_se_mesure_aux_trimestres_d_avant_soixante_ans():
    """Le § 4 ne joue qu'« à défaut de justification de quarante trimestres
    d'assurance avant l'âge de soixante ans », et ne prend que des
    « trimestres d'assurance accomplis » : il se mesure aux trimestres, ceux
    des assurances sociales de 1930 à 1944 compris, que le salaire moyen du
    modèle ne voit pas, et une année sans trimestre ne complète rien.

    Posé à la main, dix années retenues, soixante ans en 1940 : avec quarante
    trimestres avant soixante ans, aucune année d'après n'entre, même si une
    seule de ces années est au compte (1938) ; avec trente-deux, il en manque
    huit : 1940, dont le salaire ne valide aucun trimestre, est sautée, puis
    1941 et 1942, quatre chacune, et non 1943."""
    valeurs = [(1938, 3000.0), (1940, 500.0), (1941, 4000.0), (1942, 5000.0),
               (1943, 9000.0)]
    trimestres = {1938: [4, 0], 1940: [0, 0], 1941: [4, 0], 1942: [4, 0], 1943: [4, 0]}
    validantes = {1938, 1941, 1942, 1943}
    assert _moyenne_du_portage(AVANT_JUILLET_1948, valeurs, trimestres, validantes, 10, 1940,
                               40) == pytest.approx(3000.0)
    assert _moyenne_du_portage(AVANT_JUILLET_1948, valeurs, trimestres, validantes, 10, 1940,
                               32) == pytest.approx(12000.0 * 4 / 12)
    # Dix années de deux trimestres avant soixante ans : vingt trimestres, il
    # en manque vingt, que 1941, 1942 et 1943 ne suffisent pas à donner.
    moities = [(annee, 1000.0) for annee in range(1930, 1940)]
    deux = {annee: [2, 0] for annee, _ in moities}
    assert _moyenne_du_portage(AVANT_JUILLET_1948, moities + valeurs[2:], {
        **deux, 1941: [4, 0], 1942: [4, 0], 1943: [4, 0]}, set(deux) | {1941, 1942, 1943}, 10,
        1940) == pytest.approx((10_000.0 + 18_000.0) * 4 / 32)


def test_avant_juillet_1948_les_annees_de_periodes_assimilees_entrent_en_compte():
    """Décret n° 45-0179, article 74, § 3, rédaction d'origine : « Pour la
    détermination du salaire annuel moyen [...], les périodes visées à
    l'article 70 de ladite ordonnance entrent en compte. » L'exclusion des
    années de deux trimestres assimilés ou plus est le § 7 de la rédaction du
    décret n° 49-328 du 7 mars 1949 (JO du 12 mars 1949), que la circulaire
    n° 143 SS du 29 juin 1949 applique aux pensions dont l'entrée en
    jouissance est fixée « au 1er juillet 1948 ou à une date postérieure ».
    Avant, la circulaire n° 246 du 25 août 1947 calcule la pension « sur la
    base des salaires réels », les périodes sans cotisation « neutralisées » :
    l'année compte son salaire réel sur ses trimestres cotisés.

    Sur les quatre années à la main, deux retenues, soixante ans en 1963 :
    avant juillet 1948, 1961, deux trimestres cotisés et deux assimilés, et
    1962 ; 7 000 € sur six trimestres cotisés. Depuis juillet 1948, 1961 sort,
    et ce sont 1960 et 1962 : 4 000 € sur huit trimestres."""
    assert _moyenne_du_portage(AVANT_JUILLET_1948, VALEURS, TRIMESTRES, VALIDANTES, 2, 1963) \
        == pytest.approx(7000.0 * 4 / 6)
    depuis_juillet_1948 = dict(AVANT_JUILLET_1948, annees_assimilees_exclues=True,
                               apres_soixante_ans_a_defaut=False)
    assert _moyenne_du_portage(depuis_juillet_1948, VALEURS, TRIMESTRES, VALIDANTES, 2,
                               1963) == pytest.approx(4000.0 * 4 / 8)


def test_la_fiche_d_avant_juillet_1948_suit_l_article_74_d_origine():
    """La version `dix_dernieres_annees_avant_soixante_ans` porte les deux
    règles du décret n° 45-0179 d'origine ; celle de juillet 1948 garde
    l'exclusion des années assimilées, que le décret n° 49-328 a écrite."""
    import yaml

    fiche = yaml.safe_load((RACINE_PROJET / "data/reference/regles/salaire_annuel_moyen.yaml")
                           .read_text(encoding="utf-8"))
    versions = {version["id"]: version["contenu"]["parametres"]
                for version in fiche["versions"]}
    avant = versions["dix_dernieres_annees_avant_soixante_ans"]
    assert avant["annees_assimilees_exclues"] is False
    assert avant["apres_soixante_ans_a_defaut"] is True
    assert versions["dix_dernieres_annees_1948"]["annees_assimilees_exclues"] is True


def test_une_pension_du_debut_de_1948_complete_ses_annees_par_celles_d_apres_soixante_ans(
        simulateur):
    """Un assuré né en 1886, soixante ans en 1946, liquidé à soixante-deux ans
    au début de 1948 : une année au régime général avant soixante ans, 1945,
    puis 1946 et 1947 ; dix années retenues, il n'en a que trois, et toutes
    entrent dans son salaire annuel moyen (article 74, § 4, du décret
    n° 45-0179) ; le modèle n'en prenait qu'une, 1945. Chaque salaire, sous le
    plafond d'assujettissement, valide quatre trimestres."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    code = "regime_general"
    lignes = [(1945, 600.0 / 6.55957, 4), (1946, 900.0 / 6.55957, 4),
              (1947, 1_200.0 / 6.55957, 4)]
    carriere = _carriere(1886, 62, lignes)
    assert carriere.mois_liquidation < 7
    periode = simulateur.catalogue[code].a_la_date(date_d_effet(carriere))
    revalorise = [min(revenu, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 1948, carriere.mois_liquidation)
                  for annee, revenu, _ in lignes]
    sam = liquider.salaire_de_reference(actuel, code, carriere, periode, 1948, True, 1886)
    assert sam == pytest.approx(sum(revalorise) * 4 / 12)


def test_les_salaires_des_assurances_sociales_entrent_au_salaire_annuel_moyen(simulateur):
    """Un assuré né en 1886, soixante ans en 1946, liquidé à soixante-deux ans
    au début de 1948 : neuf années aux assurances sociales, 1936 à 1944, et
    1945 au régime général, quarante trimestres avant soixante ans ; 1946 et
    1947 n'entrent pas (article 74, § 4, du décret n° 45-0179). Les dix années
    entrent au salaire annuel moyen, celles de 1936 à 1944 revalorisées « pour
    la période du 1er juillet 1930 au 31 décembre 1944 » par les coefficients
    de la circulaire ministérielle n° 151 du 5 août 1946 : « 3 pour la période
    antérieure au 31 décembre 1941 ; 2 pour les années 1942 et 1943 ; 1 pour
    l'année 1944 ». Posé à la main : 100 F par an de 1936 à 1944, sous le
    plafond d'assujettissement, 6 × 300 + 2 × 200 + 100 = 2 300 F, et 600 F
    en 1945 ; moyenne des dix années, 290 F."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    code = "regime_general"
    lignes = ([(annee, 100.0 / 6.55957, 4) for annee in range(1936, 1945)]
              + [(1945, 600.0 / 6.55957, 4), (1946, 900.0 / 6.55957, 4),
                 (1947, 1_200.0 / 6.55957, 4)])
    carriere = _carriere(1886, 62, lignes)
    periode = simulateur.catalogue[code].a_la_date(date_d_effet(carriere))
    revalorise_1945 = 600.0 / 6.55957 * macro.coefficient_revalorisation_portee_au_compte(
        1945, 1948, carriere.mois_liquidation)
    attendu = (2_300.0 / 6.55957 + revalorise_1945) / 10
    sam = liquider.salaire_de_reference(actuel, code, carriere, periode, 1948, True, 1886)
    assert sam == pytest.approx(attendu)


def test_apres_1948_les_cotisations_d_avant_1945_suivent_la_colonne_de_la_cnav(simulateur):
    """La Cnav publie, à chaque date d'effet, un coefficient des COTISATIONS de
    1930 à 1946, qui les convertit en salaire et les revalorise d'un même
    geste : la colonne « Avant le 01/01/1949 », de l'arrêté du 14 mai 1946,
    porte 37,500 pour 1938 à 1941, 25,000 pour 1942 et 1943, 18,750 pour 1944,
    soit les coefficients 3, 2 et 1 de la circulaire n° 151 sur les
    cotisations d'un salaire, à 8 % puis à 5,33 % ; celle de l'arrêté du
    19 avril 1950 porte 263,750 (1938), 242,500 (1939 et 1940), 161,250
    (1941), 103,750 (1942 et 1943) et 83,750 (1944). Le salaire d'une année
    est donc revalorisé du rapport des deux colonnes, par le coefficient de la
    circulaire. Recopiés à la main de la page de la Cnav.

    Né en 1888, soixante ans en 1948, liquidé à soixante-deux ans au début de
    1950 : 100 F par an aux assurances sociales de 1938 à 1944, puis au régime
    général de 1945 à 1949 ; les dix dernières années avant soixante ans, 1938
    à 1947."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    code = "regime_general"
    lignes = [(annee, 100.0 / 6.55957, 4) for annee in range(1938, 1950)]
    carriere = _carriere(1888, 62, lignes)
    assert carriere.annee_liquidation == 1950
    periode = simulateur.catalogue[code].a_la_date(date_d_effet(carriere))
    coefficients = {1938: 263.75 * 3 / 37.5, 1939: 242.5 * 3 / 37.5,
                    1940: 242.5 * 3 / 37.5, 1941: 161.25 * 3 / 37.5,
                    1942: 103.75 * 2 / 25.0, 1943: 103.75 * 2 / 25.0,
                    1944: 83.75 * 1 / 18.75}
    assert coefficients[1938] == pytest.approx(21.1)
    avant_1945 = sum(coefficients.values()) * 100.0 / 6.55957
    apres = sum(100.0 / 6.55957 * macro.coefficient_revalorisation_portee_au_compte(
        annee, 1950, carriere.mois_liquidation) for annee in (1945, 1946, 1947))
    sam = liquider.salaire_de_reference(actuel, code, carriere, periode, 1950, True, 1888)
    assert sam == pytest.approx((avant_1945 + apres) / 10)
