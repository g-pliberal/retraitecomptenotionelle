"""Les exposés de la base de législation de la Cnav (action 175, étape 4) :
les tableaux qu'ils portent, confrontés aux séries du modèle.

Un exposé dit la règle telle que la caisse l'applique. Quand il la donne en
tableau — l'âge légal, la durée requise, le nombre d'années du revenu annuel
moyen —, ce tableau est recopié ici, à la version que le registre date
(`data/reference/legislation/cnav/exposes.csv`, colonne `modifie_le`), et
confronté à la série que le modèle lit ; le registre dit l'exposé `recoupe` par
le test. Les valeurs ont été lues le 3 novembre 2026 : quand la base sert une
autre version, la veille le dit (étape 5), et la session qui la relit récrit
la table du test. Un écart se corrige, ou se déclare ici avec sa raison.

Les générations coupées en cours d'année se lisent comme les séries les
écrivent : l'année plus la part écoulée avant le premier du mois, arrondie au
millième (le 1er septembre 1961 est `1961.667`), et la série se lit en
escalier, sa dernière ligne qui n'est pas postérieure à la génération.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
LEGISLATION = RACINE / "data" / "reference" / "legislation"


def _csv(nom: str) -> list[dict]:
    chemin = LEGISLATION / f"{nom}.csv"
    return list(csv.DictReader(
        ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
        if not ligne.startswith("#")))


def _generation(naissance: str) -> float:
    """La génération d'un assuré né ce jour-là (AAAA-MM-JJ), le premier du
    mois, telle que les séries l'écrivent."""
    annee, mois, _ = (int(morceau) for morceau in naissance.split("-"))
    return round(annee + (mois - 1) / 12, 3)


def _en_escalier(serie: str, colonne: str, generation: float) -> float:
    lignes = [ligne for ligne in _csv(serie) if float(ligne["generation"]) <= generation]
    return float(lignes[-1][colonne])


def _mois(annees: int, mois: int = 0) -> int:
    return 12 * annees + mois


# -- l'âge légal -----------------------------------------------------------------

#: « Âge de départ en retraite personnelle »
#: (`retraite_personnelle_age_retraite_ex.aspx`, version du 15 septembre 2026),
#: pour les retraites attribuées à partir du 1er septembre 2026 : le premier
#: jour de naissance de chaque ligne, et l'âge en années et mois. La suspension
#: de la loi n° 2025-1403 (article 105) ramène les générations de 1964 à 1968
#: d'un trimestre.
AGE_LEGAL = (
    ("1900-01-01", 60, 0),   # « avant le 01/07/1951 »
    ("1951-07-01", 60, 4),
    ("1952-01-01", 60, 9),
    ("1953-01-01", 61, 2),
    ("1954-01-01", 61, 7),
    ("1955-01-01", 62, 0),   # « de 1955 au 31/08/1961 »
    ("1961-09-01", 62, 3),
    ("1962-01-01", 62, 6),
    ("1963-01-01", 62, 9),
    ("1964-01-01", 62, 9),
    ("1965-01-01", 62, 9),   # « du 01/01/1965 au 31/03/1965 »
    ("1965-04-01", 63, 0),
    ("1966-01-01", 63, 3),
    ("1967-01-01", 63, 6),
    ("1968-01-01", 63, 9),
    ("1969-01-01", 64, 0),   # « à partir de 1969 »
)

#: Le même exposé, « Jusqu'au 01/08/2026 » : les retraites prenant effet du
#: 1er septembre 2023 au 1er août 2026, que la suspension ne touche pas
#: (`age_ouverture_avant_suspension.csv`).
AGE_LEGAL_AVANT_SUSPENSION = (
    ("1964-01-01", 63, 0),
    ("1965-01-01", 63, 3),
    ("1966-01-01", 63, 6),
    ("1967-01-01", 63, 9),
    ("1968-01-01", 64, 0),   # « à partir de 1968 »
)


@pytest.mark.parametrize("naissance, annees, mois", AGE_LEGAL)
def test_l_age_legal_de_la_caisse_est_celui_de_la_serie(naissance, annees, mois):
    age = _en_escalier("age_ouverture_requis", "age", _generation(naissance))
    assert round(age * 12) == _mois(annees, mois), naissance


@pytest.mark.parametrize("naissance, annees, mois", AGE_LEGAL_AVANT_SUSPENSION)
def test_l_age_legal_d_avant_la_suspension_est_celui_de_la_serie(naissance, annees, mois):
    age = _en_escalier("age_ouverture_avant_suspension", "age", _generation(naissance))
    assert round(age * 12) == _mois(annees, mois), naissance


# -- l'âge du taux plein ---------------------------------------------------------

#: « Taux de la retraite personnelle »
#: (`retraite_personnelle_taux_taux_retraite_ex.aspx`, version du 29 juillet
#: 2026) : l'âge d'obtention du taux plein, l'âge légal augmenté de cinq ans,
#: 67 ans pour les assurés nés à partir du 1er septembre 1961 comme pour ceux
#: de 1955 (« Anciennes dispositions, avant le 01/09/2023 »).
AGE_DU_TAUX_PLEIN = (
    ("1930-01-01", 65, 0),   # « avant le 01/07/1951 »
    ("1951-07-01", 65, 4),
    ("1952-01-01", 65, 9),
    ("1953-01-01", 66, 2),
    ("1954-01-01", 66, 7),
    ("1955-01-01", 67, 0),
    ("1961-09-01", 67, 0),
    ("1970-01-01", 67, 0),
)


@pytest.mark.parametrize("naissance, annees, mois", AGE_DU_TAUX_PLEIN)
def test_l_age_du_taux_plein_de_la_caisse_est_celui_de_la_serie(naissance, annees, mois):
    age = _en_escalier("age_annulation_decote", "age", _generation(naissance))
    assert round(age * 12) == _mois(annees, mois), naissance


# -- la durée requise pour le taux plein -----------------------------------------

#: « Durée d'assurance pour le taux plein »
#: (`retraite_personnelle_taux_duree_assurance_pour_taux_plein_ex.aspx`, version
#: du 15 septembre 2026), pour les retraites attribuées à compter du
#: 1er septembre 2026 ; avant 1943, le tableau de ses « Anciennes dispositions,
#: avant le 01/01/2003 », que la loi du 22 juillet 1993 a fait monter de 150 à
#: 159 trimestres.
DUREE_REQUISE = (
    ("1900-01-01", 150),   # « avant 1934 »
    ("1934-01-01", 151),
    ("1935-01-01", 152),
    ("1936-01-01", 153),
    ("1937-01-01", 154),
    ("1938-01-01", 155),
    ("1939-01-01", 156),
    ("1940-01-01", 157),
    ("1941-01-01", 158),
    ("1942-01-01", 159),
    ("1943-01-01", 160),   # « 1943 - 1944 - 1945 - 1946 - 1947 - 1948 »
    ("1948-01-01", 160),
    ("1949-01-01", 161),
    ("1950-01-01", 162),
    ("1951-01-01", 163),
    ("1952-01-01", 164),
    ("1953-01-01", 165),
    ("1955-01-01", 166),
    ("1958-01-01", 167),
    ("1961-01-01", 168),   # « 1961 (du 01/01 au 31/08) »
    ("1961-09-01", 169),
    ("1962-01-01", 169),
    ("1963-01-01", 170),
    ("1964-01-01", 170),
    ("1965-01-01", 170),   # « Du 01/01/1965 au 31/03/1965 »
    ("1965-04-01", 171),
    ("1966-01-01", 172),   # « À partir de 1966 »
    ("1975-01-01", 172),
)

#: Le même exposé, « Jusqu'au 01/08/2026 » : les retraites prenant effet du
#: 1er septembre 2023 au 1er août 2026 (`duree_requise_avant_suspension.csv`).
DUREE_REQUISE_AVANT_SUSPENSION = (("1964-01-01", 171), ("1965-01-01", 172))

#: Le même exposé, « Anciennes dispositions, avant le 01/09/2023 » : le
#: calendrier de la loi du 20 janvier 2014, d'un trimestre tous les trois ans
#: (`duree_requise_avant_reforme_2023.csv`, depuis la génération que la loi du
#: 14 avril 2023 a touchée la première).
DUREE_REQUISE_AVANT_2023 = (
    ("1961-09-01", 168),   # « 1961 - 1962 - 1963 »
    ("1963-01-01", 168),
    ("1964-01-01", 169),
    ("1967-01-01", 170),
    ("1970-01-01", 171),
    ("1973-01-01", 172),   # « A partir de 1973 »
)


#: Le même exposé, « Anciennes dispositions, avant le 01/01/2009 » : « Le
#: nombre de trimestres était fixé à 160 trimestres pour les retraites
#: attribuées à partir de 2003. L'assuré né en décembre 1942, qui totalisait
#: 159 trimestres bénéficiait du taux plein si le point de départ de sa
#: retraite était fixé le 01/01/2003. » C'est R. 351-45 dans ses deux
#: rédactions de 1993 et de 1995 (LEGIARTI000006749449, LEGIARTI000006749450) :
#: « I. - La durée [...] de 160 trimestres [...] est applicable aux pensions
#: prenant effet postérieurement au 31 décembre 2002, quelle que soit la date
#: de naissance de l'assuré. II. - En ce qui concerne les pensions prenant
#: effet avant le 1er janvier 2003 [...] 151 trimestres pour l'assuré né en
#: 1934 [...] 159 trimestres pour l'assuré né en 1942. III. - Par dérogation
#: au I ci-dessus, la durée [...] demeure fixée à 159 trimestres pour les
#: assurés nés en décembre 1942 et dont la pension prend effet au 1er janvier
#: 2003 » ; puis R. 351-27 depuis 2009 (LEGIARTI000020082993) : « Pour les
#: assurés nés avant le 1er janvier 1949, cette limite est fixée à 160
#: trimestres ». L'escalier de la série ne vaut donc qu'avant 2003. Un assuré
#: part à l'âge dit, compté du mois qui suit sa naissance : l'année et le mois
#: de naissance, l'âge, l'année et le mois où la pension prend effet, la durée.
DUREE_REQUISE_SELON_LA_DATE_D_EFFET = (
    (1942, 12, 60.0, 2003, 1, 159),            # le III
    (1942, 11, 60.0, 2002, 12, 159),           # le II
    (1942, 11, 60 + 1 / 12, 2003, 1, 160),     # le I : le III ne vise que décembre
    (1940, 6, 62.0, 2002, 7, 157),
    (1940, 6, 63.0, 2003, 7, 160),
    (1934, 1, 60.0, 1994, 2, 151),
    (1938, 3, 72.0, 2010, 4, 160),             # R. 351-27, nés avant 1949
    (1949, 1, 60.0, 2009, 2, 161),
)


def test_la_duree_requise_des_nes_avant_1943_est_de_160_trimestres_depuis_2003():
    from outils_pont import droit_et_refait

    from retraite_notionnelle import pont
    from retraite_notionnelle.carriere import AnneeCarriere, Carriere

    appels, attendus = {}, {}
    for annee, mois, age, effet, mois_effet, trimestres in DUREE_REQUISE_SELON_LA_DATE_D_EFFET:
        carriere = Carriere(
            annee_naissance=annee, mois_naissance=mois, sexe="H", age_liquidation=age,
            identifiant=f"né en {mois}/{annee}",
            lignes=[AnneeCarriere(annee=an, revenu=20_000.0, trimestres_valides=4,
                                  affiliation="salarie_prive_non_cadre")
                    for an in range(annee + 20, effet)])
        assert (carriere.annee_liquidation, carriere.mois_liquidation) == (effet, mois_effet)
        cle = f"{mois}/{annee}, effet {mois_effet}/{effet}"
        appels[cle] = ("ouvrir.duree_requise", pont.MOTEUR,
                       pont.Periode("regime_general", effet), carriere)
        attendus[cle] = trimestres
    lus, refus = droit_et_refait(appels)
    assert refus == {}, refus
    assert {cle: lu[0] for cle, lu in lus.items()} == attendus


@pytest.mark.parametrize("naissance, trimestres", DUREE_REQUISE)
def test_la_duree_requise_de_la_caisse_est_celle_de_la_serie(naissance, trimestres):
    serie = _en_escalier("duree_assurance_requise", "trimestres", _generation(naissance))
    assert serie == trimestres, naissance


@pytest.mark.parametrize("serie, table", [
    ("duree_requise_avant_suspension", DUREE_REQUISE_AVANT_SUSPENSION),
    ("duree_requise_avant_reforme_2023", DUREE_REQUISE_AVANT_2023),
])
def test_les_durees_requises_d_avant_sont_celles_de_la_caisse(serie, table):
    for naissance, trimestres in table:
        assert _en_escalier(serie, "trimestres", _generation(naissance)) == trimestres, (
            serie, naissance)


# -- la durée de proratisation ---------------------------------------------------

#: « Montant de la retraite personnelle »
#: (`retraite_personnelle_montant_montant_ex.aspx`, version du 6 mars 2026),
#: « Anciennes dispositions, avant le 01/09/2023 » : le nombre maximum de
#: trimestres retenus. Il ne suit la durée requise qu'à partir de 1948 : de 1944
#: à 1947, deux trimestres par génération (R. 351-6, `duree_proratisation.csv`),
#: puis la durée requise (`duree_assurance_requise.csv`), que le tableau de
#: l'exposé « à partir du 01/09/2026 » porte aussi, suspension comprise.
DUREE_DE_PRORATISATION = (
    ("1943-01-01", 150),   # « Avant 1944 »
    ("1944-01-01", 152),
    ("1945-01-01", 154),
    ("1946-01-01", 156),
    ("1947-01-01", 158),
    ("1948-01-01", 160),
    ("1949-01-01", 161),
    ("1950-01-01", 162),
    ("1951-01-01", 163),
    ("1952-01-01", 164),
    ("1953-01-01", 165),
    ("1955-01-01", 166),
    ("1958-01-01", 167),
    ("1961-01-01", 168),   # « 1961 (du 01/01 au 31/08) », à partir du 01/09/2026
    ("1961-09-01", 169),
    ("1963-01-01", 170),   # « 1963 au 31/03/1965 »
    ("1965-04-01", 171),
    ("1966-01-01", 172),
)


@pytest.mark.parametrize("naissance, trimestres", DUREE_DE_PRORATISATION)
def test_la_duree_de_proratisation_de_la_caisse_est_celle_de_la_serie(naissance, trimestres):
    generation = _generation(naissance)
    derniere = max(float(ligne["generation"]) for ligne in _csv("duree_proratisation"))
    serie = ("duree_proratisation" if generation < derniere + 1
             else "duree_assurance_requise")
    assert _en_escalier(serie, "trimestres", generation) == trimestres, naissance


# -- le nombre d'années du revenu annuel moyen -----------------------------------

#: « Nombre d'années retenues »
#: (`retraite_personnelle_salaire_annuel_moyen_nombre_annee_retenue_ex.aspx`,
#: version du 13 mai 2026) : les salariés, d'une année par génération de 1934 à
#: 1948 (R. 351-29) ; les travailleurs indépendants, d'une année toutes les deux
#: générations jusqu'en 1944, puis d'une par génération jusqu'en 1953
#: (R. 173-4-3).
ANNEES_DES_SALARIES = {1933: 10, 1934: 11, 1935: 12, 1936: 13, 1937: 14, 1938: 15,
                       1939: 16, 1940: 17, 1941: 18, 1942: 19, 1943: 20, 1944: 21,
                       1945: 22, 1946: 23, 1947: 24, 1948: 25, 1960: 25}
ANNEES_DES_INDEPENDANTS = {1933: 10, 1934: 11, 1935: 11, 1936: 12, 1937: 12, 1938: 13,
                           1939: 13, 1940: 14, 1941: 14, 1942: 15, 1943: 15, 1944: 16,
                           1945: 17, 1946: 18, 1947: 19, 1948: 20, 1949: 21, 1950: 22,
                           1951: 23, 1952: 24, 1953: 25, 1960: 25}


@pytest.mark.parametrize("serie, table", [
    ("annees_salaire_reference", ANNEES_DES_SALARIES),
    ("annees_revenu_annuel_moyen_independants", ANNEES_DES_INDEPENDANTS),
])
def test_le_nombre_d_annees_du_revenu_annuel_moyen_est_celui_de_la_caisse(serie, table):
    for annee, annees in table.items():
        assert _en_escalier(serie, "annees", float(annee)) == annees, (serie, annee)


# -- la carrière longue ----------------------------------------------------------

#: « Conditions d'attribution de la retraite anticipée carrière longue »
#: (`retraite_personnelle_retraite_anticipee_longue_carriere_condition_attribution_ex.aspx`,
#: version du 4 septembre 2026) : l'âge de départ de qui a commencé avant
#: vingt ans, par génération — le premier jour de naissance, le premier jour qui
#: n'en est plus —, et, pour les générations entières, les trois autres bornes
#: (seize, dix-huit et vingt et un ans). Deux régimes : les retraites qui
#: prennent effet à partir du 1er septembre 2026, sous la suspension, et celles
#: du 1er septembre 2023 au 31 août 2026 (`carriere_longue.csv`, date d'effet
#: `2026.667` et `2023.667`).
CARRIERE_LONGUE = {
    2026.667: (
        ("1961-09-01", "1963-09-01", 20, 60, 0),
        ("1963-09-01", "1964-01-01", 20, 60, 3),
        ("1964-01-01", "1965-01-01", 20, 60, 6),
        ("1965-01-01", "1965-12-01", 20, 60, 9),
        ("1965-12-01", "1966-01-01", 20, 60, 8),   # « du 01/12/1965 au 31/12/1965 »
        ("1966-01-01", "1967-01-01", 20, 60, 9),   # deux ans et demi avant l'âge légal
        ("1967-01-01", "1968-01-01", 20, 61, 0),
        ("1968-01-01", "1969-01-01", 20, 61, 3),
        ("1969-01-01", "1970-01-01", 20, 61, 6),
        ("1970-01-01", "1971-01-01", 20, 61, 9),
        ("1971-01-01", "2000-01-01", 20, 62, 0),
        ("1971-01-01", "2000-01-01", 16, 58, 0),
        ("1971-01-01", "2000-01-01", 18, 60, 0),
        ("1971-01-01", "2000-01-01", 21, 63, 0),
    ),
    2023.667: (
        ("1961-09-01", "1963-09-01", 20, 60, 0),
        ("1963-09-01", "1964-01-01", 20, 60, 3),
        ("1964-01-01", "1965-01-01", 20, 60, 6),
        ("1965-01-01", "1966-01-01", 20, 60, 9),
        ("1966-01-01", "1967-01-01", 20, 61, 0),
        ("1967-01-01", "1968-01-01", 20, 61, 3),
        ("1968-01-01", "1969-01-01", 20, 61, 6),
        ("1969-01-01", "1970-01-01", 20, 61, 9),
        ("1970-01-01", "2000-01-01", 20, 62, 0),
        ("1970-01-01", "2000-01-01", 16, 58, 0),
        ("1970-01-01", "2000-01-01", 18, 60, 0),
        ("1970-01-01", "2000-01-01", 21, 63, 0),
    ),
}


@pytest.mark.parametrize("date_effet", sorted(CARRIERE_LONGUE))
def test_les_ages_de_la_carriere_longue_sont_ceux_de_la_caisse(date_effet):
    """Une génération peut relever de plusieurs lignes de la série — la borne de
    toutes les générations et celle que la loi nomme pour la sienne — : la
    plus favorable ouvre le départ, et c'est elle que l'exposé donne."""
    lignes = [ligne for ligne in _csv("carriere_longue")
              if abs(float(ligne["date_effet"]) - date_effet) < 1e-9]
    for debut, fin, age_debut, annees, mois in CARRIERE_LONGUE[date_effet]:
        de, a = _generation(debut), _generation(fin)
        ages = [float(ligne["age_depart"]) for ligne in lignes
                if int(ligne["age_debut_maximum"]) == age_debut
                and float(ligne["generation"]) <= de and a <= float(ligne["generation_fin"])]
        assert ages, (date_effet, debut, age_debut)
        assert round(min(ages) * 12) == _mois(annees, mois), (date_effet, debut, age_debut)


# -- le salaire qui valide un trimestre -----------------------------------------------

#: « Validation des périodes de cotisations »
#: (`cotisation_salaire_validation_periode_cotisation_validation_periode_cotisation_ex.aspx`,
#: version du 13 novembre 2025) : ce qui valide un trimestre au salarié, chaque règle
#: sous l'année de son premier jour. L'année 1946 compte « autant de trimestres que le
#: salaire correspondant aux retenues [...] représente de fois 1.800 AF », comme 1947 et
#: 1948 ; le Smic et l'allocation aux vieux travailleurs salariés sont ceux du 1er
#: janvier de l'année.
SALAIRE_VALIDANT_UN_TRIMESTRE = (
    (1946, "1 800 anciens francs"),
    (1949, "le montant trimestriel de l'allocation aux vieux travailleurs salariés"),
    (1972, 200),
    (2014, 150),
)

#: Un franc vaut cent anciens francs, et un euro 6,55957 francs.
EUROS_PAR_ANCIEN_FRANC = 1 / 100 / 6.55957


def test_le_salaire_qui_valide_un_trimestre_est_celui_de_la_caisse():
    """Depuis 1972, des heures de Smic (`validation_trimestres.csv`) : 200 jusqu'en
    2013, 150 depuis ; de 1946 à 1971, un montant en euros
    (`salaire_validant_trimestre_avant_1972.csv`), 1 800 anciens francs jusqu'en
    1948, puis une ligne par année, que `cnav_avts.py` tire du barème de l'allocation
    aux vieux travailleurs salariés que l'exposé désigne."""
    heures = {int(ligne["annee"]): float(ligne["heures"])
              for ligne in _csv("validation_trimestres")}
    avant_1972 = {int(ligne["annee"]): float(ligne["valeur"])
                  for ligne in _csv("salaire_validant_trimestre_avant_1972")}
    debuts = [debut for debut, _ in SALAIRE_VALIDANT_UN_TRIMESTRE]
    for rang, (debut, regle) in enumerate(SALAIRE_VALIDANT_UN_TRIMESTRE):
        fin = debuts[rang + 1] if rang + 1 < len(debuts) else 2027
        for annee in range(debut, fin):
            if isinstance(regle, int):
                assert heures[max(d for d in heures if d <= annee)] == regle, annee
            elif annee < 1949:
                assert avant_1972[annee] == pytest.approx(1800 * EUROS_PAR_ANCIEN_FRANC), annee
            else:
                assert avant_1972[annee] > avant_1972[1948], annee
    assert min(heures) == 1972 and max(avant_1972) == 1971
