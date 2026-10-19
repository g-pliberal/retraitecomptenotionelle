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

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.simulateur import Simulateur


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
    moyenne = liquider.moyenne_selon_la_regle
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
    avant_1948 = _regle(selection="dernieres", calcul="trimestriel",
                        trimestres_comptes="cotises", annees_assimilees_exclues=True)
    # Les deux dernières années d'avant 1963, l'année des soixante ans, sans
    # 1961 et ses deux trimestres assimilés : 1960 et 1962.
    assert moyenne(avant_1948, VALEURS, TRIMESTRES, VALIDANTES, 2, 1963) \
        == pytest.approx(4000.0 * 4 / 8)
    # Depuis juillet 1948, les deux dernières d'avant l'effet, 1962 et 1963,
    # valent mieux : 3 500 € sur quatre trimestres.
    depuis_1948 = dict(avant_1948, avant_la_liquidation=True)
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
    periode = simulateur.catalogue[code].periode(2012)
    revalorise = [min(30_000.0, macro.plafond_securite_sociale(annee))
                  * macro.coefficient_revalorisation_portee_au_compte(
                      annee, 2012, tardive.mois_liquidation)
                  for annee in range(1985, 2001)]
    sam = liquider.salaire_de_reference(actuel, code, tardive, periode, 2012, True, 1950)
    assert sam == pytest.approx(sum(sorted(revalorise, reverse=True)) / len(revalorise))

    precoce = _carriere(1950, 53, lignes)
    periode = simulateur.catalogue[code].periode(2003)
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
    periode = simulateur.catalogue["regime_general"].periode(1990)
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
    periode = simulateur.catalogue["rsi"].periode(2010)
    for naissance, attendu in ((1943, 15), (1948, 20), (1952, 24), (1953, 25)):
        carriere = _carriere(naissance, 2010.5 - naissance, [(2000, 30_000.0, 4)])
        assert liquider.nombre_d_annees_retenues(
            actuel, periode, carriere, naissance) == attendu, naissance
    salarie = simulateur.catalogue["regime_general"].periode(2010)
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
    assert simulateur.catalogue["regime_general"].periode(1982).date_effet[1] == "1983-04-01"
    resultat = simulateur.scenario_actuel.calculer(carriere)
    applique = {a.code: a.montant for a in resultat.avantages_appliques}
    assert applique["avpf"] == pytest.approx(7.0812, abs=1e-3)


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


def test_avant_1946_la_retenue_ne_lit_que_les_assures_sociaux(simulateur):
    """Le statut de l'année dit si la retenue compte : un cadre payé 400 F en
    1940, au-delà du plafond d'assujettissement de 300 F, ne cotisait pas aux
    assurances sociales et ne valide rien ; le même traitement d'un
    fonctionnaire de l'État, dont la pension civile compte les services, en
    valide quatre ; 2 F de salaire, 0,08 F de retenue, aucun."""
    from retraite_notionnelle.carriere import LigneRelevee

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
    periode = simulateur.catalogue[code].periode(1980)

    def sam(lignes_de_la_carriere: list[AnneeCarriere]) -> float:
        carriere = Carriere.depuis_lignes(1915, "H", lignes_de_la_carriere,
                                          age_liquidation=65)
        return liquider.salaire_de_reference(actuel, code, carriere, periode, 1980, True,
                                             1915)

    assert sam(anciennes + lignes) == pytest.approx(sam(lignes))


#: Le jumeau JavaScript du test précédent : les mêmes relevés, lus par le
#: portage.
_JUMEAU_RETENUE = """
import { readFileSync } from "node:fs";
import { Simulateur } from "./moteur/js/simulateur.js";
const releves = JSON.parse(process.argv[1]);
const simulateur = new Simulateur(JSON.parse(readFileSync("./moteur/donnees.json", "utf8")));
process.stdout.write(JSON.stringify(releves.map((releve) => simulateur.carriereReleve({
  annee_naissance: 1915, sexe: "H", releve, age_liquidation: 60,
}).lignes.map((l) => [l.annee, l.trimestres_valides]))));
"""


def test_le_portage_javascript_lit_la_retenue_comme_le_modele(simulateur):
    import json
    import shutil
    import subprocess
    from pathlib import Path

    from retraite_notionnelle.carriere import LigneRelevee

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    releves = [[{"annee": annee, "affiliation": statut, "revenu": francs / 6.55957}
                for annee in (1929, 1930, 1938, 1946)]
               for statut, francs in (("salarie_prive_cadre", 400.0),
                                      ("salarie_prive_non_cadre", 200.0),
                                      ("salarie_prive_non_cadre", 2.0),
                                      ("fonctionnaire_etat", 400.0))]
    attendus = [[[l.annee, l.trimestres_valides] for l in simulateur.carriere_releve(
                    1915, "H", [LigneRelevee(**ligne) for ligne in releve], 60.0).lignes]
                for releve in releves]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU_RETENUE, json.dumps(releves)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    assert json.loads(execution.stdout) == attendus
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
