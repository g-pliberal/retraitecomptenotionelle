"""L'oracle au-delà des carrières simples : OpenFisca, une famille de profils à la fois.

``tests/test_oracle.py`` ne confronte à OpenFisca-France-Pension que des
carrières continues à traitement nominal constant, sans enfant ni temps partiel :
la convention l'avait voulu, pour que la traduction d'un modèle à l'autre ne
devienne pas l'objet du test (action 136). L'action 153 l'étend une famille de
profils à la fois, chacune avec sa convention de traduction ÉCRITE : dans le
script qui la fige, et dans le témoin, qui porte la convention et les entrées
qu'OpenFisca a reçues. Chaque famille vérifie d'abord que son témoin suit sa
convention, puis confronte, grandeur par grandeur ; un écart connu y est déclaré,
avec le texte qui le tranche, et le test vérifie que chacun des deux modèles rend
exactement ce que SA règle commande — c'est ainsi qu'on sait de quel côté est
l'écart, et qu'il n'est que celui-là.

* **Le temps partiel des fonctionnaires et le départ anticipé des parents de
  trois enfants** (``scripts/fetch/openfisca_temps_partiel_et_parents.py``,
  le 13 octobre 2026). Le temps partiel : rien à corriger, tout tombe au centime.
  Les parents : quatre écarts, tous chez lui — la durée de la génération au
  lieu de celle de l'année des conditions, le départ fermé avant juillet 2011 à
  qui n'a ni son âge d'ouverture avant 2016 ni ses conditions avant 2003, le
  départ d'après juin 2011 servi à la seule raison « famille », qu'il date du
  départ, et les quinze ans comptés sur les services réduits par la quotité.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import liquider, ouvrir, releve
from retraite_notionnelle.simulateur import Simulateur

TEMOINS = Path(__file__).resolve().parent / "temoins"
TEMOIN_TEMPS_PARTIEL_ET_PARENTS = TEMOINS / "openfisca_temps_partiel_et_parents.json"
TEMOIN_FONCTION_PUBLIQUE = TEMOINS / "openfisca_fonction_publique.json"

#: Ce que le témoin appelle chaque régime : le statut qui y conduit au dépôt, et
#: le préfixe des variables d'OpenFisca.
AFFILIATIONS = {
    "fonction_publique_etat": "fonctionnaire_etat",
    "cnracl": "fonctionnaire_territorial_hospitalier",
}
PREFIXES = {"fonction_publique_etat": "fonction_publique", "cnracl": "cnracl"}

TEMPS_PARTIEL = "temps_partiel"
PARENTS = "parents_de_trois_enfants"

#: Comptages et tables : à l'unité près. OpenFisca calcule en simple précision,
#: d'où la tolérance relative de ses montants.
TOLERANCE_EXACTE = 1e-4
PRECISION_OPENFISCA = 1e-6

TAUX_PLEIN = 0.75
SERVICES_PAR_AN = 4
#: L. 13, I : le pourcentage maximum, porté par les bonifications jusqu'à 80 %.
POURCENTAGE_MAXIMUM_BONIFIE = 80 / 75
#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "duree_de_service_cotisee_annuelle", "quotite_de_travail", "taux_de_prime",
    "nombre_enfants", "date_naissance_enfant", "nombre_enfants_nes_avant_2004",
    "raison_depart_taux_plein_anticipe", "non_traduit", "dates",
}

_PRORATA = re.compile(r"× (\d+)/(\d+)")


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN_TEMPS_PARTIEL_ET_PARENTS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _quotites(profil: dict) -> dict[int, float]:
    return {annee: quotite for debut, fin, quotite in profil.get("temps_partiel", ())
            for annee in range(debut, fin + 1)}


def _notre_calcul(simulateur: Simulateur, profil: dict) -> dict:
    """La pension civile du scénario 1, sur la carrière que le profil décrit.

    Une année à temps partiel porte sa quotité et le traitement qu'elle a payé,
    le traitement à temps plein réduit d'autant : ce que le formulaire en fait
    (fiche ``temps_partiel_fonction_publique``). Les enfants sont les naissances
    datées du profil, que la chronologie ne présume pas."""
    code = profil["regime"]
    partiel = _quotites(profil)
    lignes = [
        AnneeCarriere(
            annee=annee, revenu=profil["traitement"] * partiel.get(annee, 1.0),
            affiliation=AFFILIATIONS[code], trimestres_valides=SERVICES_PAR_AN,
            quotite=partiel.get(annee, 1.0),
        )
        for annee in range(profil["debut"], profil["liquidation"])
    ]
    naissances = tuple(profil.get("naissances", ()))
    carriere = Carriere(
        annee_naissance=profil["naissance"], sexe=profil.get("sexe", "H"), lignes=lignes,
        age_liquidation=float(profil["liquidation"] - profil["naissance"]),
        identifiant=profil["code"], jour_naissance=1,
        nombre_enfants=len(naissances), naissances_enfants=naissances,
    )
    scenario = simulateur.scenario_actuel
    resultat = scenario.calculer(carriere)
    periode = simulateur.catalogue[code].periode(profil["liquidation"])
    requis, _ = ouvrir.duree_requise(scenario, periode, carriere)
    proratisation, _ = liquider.duree_proratisation(scenario, periode, carriere, requis)
    _, age_annulation, _ = liquider.decote_opposable(
        scenario, periode, carriere, profil["liquidation"])
    durees = releve.construire(scenario, carriere).durees
    pension = next(p for p in resultat.pensions_par_regime if p.regime == code)
    avantages = {a.code: a.montant for a in resultat.avantages_appliques}
    prorata = _PRORATA.search(pension.detail)
    return {
        "duree_assurance": resultat.trimestres_valides,
        "services": durees.services_effectifs((code,)),
        "services_et_bonifications": durees.services_liquidables((code,)),
        "proratisation": proratisation,
        "prorata_du_detail": tuple(int(n) for n in prorata.groups()) if prorata else None,
        "decote_trimestres": liquider.trimestres_de_decote(
            scenario, periode, carriere, resultat.trimestres_valides, requis,
            profil["liquidation"] - profil["naissance"], age_annulation),
        "taux_de_liquidation": resultat.taux_liquidation,
        "traitement_de_reference": liquider.salaire_de_reference(
            scenario, code, carriere, periode, profil["liquidation"], False,
            profil["naissance"], True),
        "pension": pension.montant,
        "pension_avant_minimum": pension.montant - avantages.get("minimum_garanti", 0.0),
        "majoration_pension": avantages.get("majoration_enfants", 0.0),
        "liquidation_ouverte": resultat.liquidation_ouverte,
        "depart": ouvrir.depart_parent_trois_enfants(scenario, periode, carriere),
    }


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _notre_calcul(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, regle: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] == regle]


def _meres(temoin: dict) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in _de_la_regle(temoin, PARENTS)
            if entree["profil"]["sexe"] == "F"]


def _coefficient_de_proratisation(services: float, bonifications: float, duree: float
                                  ) -> float:
    """L. 13 : les services jusqu'au pourcentage maximum, que les
    bonifications portent jusqu'à 80 %."""
    return max(min(1.0, services / duree),
               min(POURCENTAGE_MAXIMUM_BONIFIE,
                   (min(services, duree) + bonifications) / duree))


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin):
    """Le témoin dit d'où il vient, porte sa convention, et chaque profil les
    entrées qu'OpenFisca a reçues : la traduction se relit, et se vérifie ici
    avant toute comparaison. Une traduction fausse serait l'objet du test."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    profils = temoin["profils"]
    assert {e["profil"]["regle"] for e in profils.values()} == {TEMPS_PARTIEL, PARENTS}
    for code, entree in profils.items():
        profil, recu, eux = entree["profil"], entree["entrees_openfisca"], entree["openfisca"]
        prefixe = PREFIXES[profil["regime"]]
        # Les barèmes de sa fonction publique s'arrêtent en 2020.
        assert 2009 <= profil["liquidation"] <= 2020, code
        # Le garde-fou du récupérateur : un oracle silencieusement nul
        # validerait n'importe quoi.
        assert eux["duree_assurance"] > 0 and eux["pension_brute"] > 0, code
        assert recu["sexe"] is (profil["sexe"] == "F"), code
        naissances = profil.get("naissances", [])
        assert recu["nombre_enfants"] == len(naissances), code
        if naissances:
            # Toutes pendant les services : ni la bonification ni
            # l'interruption ne lisent alors une période hors du code.
            assert all(profil["debut"] <= int(n[:4]) < profil["liquidation"]
                       for n in naissances), code
            assert recu["date_naissance_enfant"] == sorted(naissances)[2], code
            assert recu[f"{prefixe}_nombre_enfants_nes_avant_2004"] == sum(
                n < "2004-01-01" for n in naissances), code
        assert recu.get("raison_depart_taux_plein_anticipe") == profil.get("raison"), code
        partiel = _quotites(profil)
        assert recu.get(f"{prefixe}_quotite_de_travail", {}) == {
            str(a): q for a, q in partiel.items()}, code
        assert recu.get(f"{prefixe}_duree_de_service_cotisee_annuelle", {}) == {
            str(a): pytest.approx(SERVICES_PAR_AN * q) for a, q in partiel.items()}, code


# -- le temps partiel des fonctionnaires -----------------------------------------

def test_le_temps_partiel_garde_la_duree_et_reduit_les_services(temoin, nous):
    """L. 14, I, et L. 11, 1° : la durée d'assurance compte le temps partiel en
    entier, les services à sa quotité — et les deux modèles comptent pareil,
    trimestre pour trimestre."""
    for code, entree in _de_la_regle(temoin, TEMPS_PARTIEL):
        profil, eux = entree["profil"], entree["openfisca"]
        annees = profil["liquidation"] - profil["debut"]
        partiel = _quotites(profil)
        reduits = round(SERVICES_PAR_AN * (annees - len(partiel)) + sum(
            SERVICES_PAR_AN * q for q in partiel.values()))
        assert nous[code]["duree_assurance"] == eux["duree_assurance"] \
            == SERVICES_PAR_AN * annees, code
        assert nous[code]["services"] == eux["services"] == reduits, code
        assert reduits < SERVICES_PAR_AN * annees, code


def test_les_services_a_temps_partiel_s_arrondissent_une_fois(temoin, nous):
    """Trois ans à 70 % font 8,4 trimestres : arrondis une fois, au décompte
    final (R. 26), ils en laissent 148 sur 152 ; arrondis année par année,
    trois fois 2,8 en feraient 149. OpenFisca arrondit à la liquidation, le
    dépôt compte au jour : les deux en laissent 148."""
    entree = temoin["profils"]["temps_partiel_70_trois_ans_1952"]
    profil = entree["profil"]
    annee_par_annee = SERVICES_PAR_AN * (profil["liquidation"] - profil["debut"]) - sum(
        SERVICES_PAR_AN - round(SERVICES_PAR_AN * q) for q in _quotites(profil).values())
    assert annee_par_annee == 149
    assert nous["temps_partiel_70_trois_ans_1952"]["services"] \
        == entree["openfisca"]["services"] == 148


def test_la_pension_a_temps_partiel_concorde_au_centime(temoin, nous):
    """Décote, taux, proratisation, traitement : chaque maillon, puis la
    pension, sur les six profils."""
    for code, entree in _de_la_regle(temoin, TEMPS_PARTIEL):
        moi, eux = nous[code], entree["openfisca"]
        assert moi["decote_trimestres"] == eux["decote_trimestres"], code
        assert moi["taux_de_liquidation"] == pytest.approx(
            eux["taux_de_liquidation"], abs=TOLERANCE_EXACTE), code
        assert moi["prorata_du_detail"] == (
            min(moi["services_et_bonifications"], moi["proratisation"]),
            moi["proratisation"]), code
        assert _coefficient_de_proratisation(
            moi["services"], 0, moi["proratisation"]) == pytest.approx(
                eux["coefficient_de_proratisation"], abs=TOLERANCE_EXACTE), code
        assert moi["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=PRECISION_OPENFISCA), code
        assert moi["pension_avant_minimum"] == pytest.approx(
            eux["pension_avant_minimum"], rel=PRECISION_OPENFISCA), code


def test_le_traitement_du_temps_partiel_se_liquide_a_temps_plein(temoin, nous, simulateur):
    """L. 15 : à 80 % jusqu'au départ, le fonctionnaire liquide le traitement
    « auquel [il] pourrai[t] prétendre [à] plein temps ». Le dépôt le lit sur
    une ligne qui porte 80 % du traitement ; OpenFisca, à qui la convention
    donne le temps plein, l'en tire. Les deux tombent sur celui du temps
    plein, que la même carrière sans temps partiel liquide aussi."""
    entree = temoin["profils"]["temps_partiel_jusqu_au_depart_1953"]
    profil = entree["profil"]
    assert _quotites(profil)[profil["liquidation"] - 1] == 0.8
    plein = _notre_calcul(simulateur, {k: v for k, v in profil.items() if k != "temps_partiel"})
    moi = nous["temps_partiel_jusqu_au_depart_1953"]
    assert moi["traitement_de_reference"] == pytest.approx(
        plein["traitement_de_reference"], rel=1e-12)
    assert moi["traitement_de_reference"] == pytest.approx(
        entree["openfisca"]["traitement_de_reference"], rel=PRECISION_OPENFISCA)


def test_le_minimum_garanti_lit_les_services_reduits(temoin, nous, simulateur):
    """L. 17 : le minimum garanti est un barème sur les services. Les deux
    modèles s'écartent sur sa référence — le point d'indice de l'année chez
    OpenFisca, celle de 2004 revalorisée chez nous, l'écart étant le sien
    (``tests/test_oracle.py``) —, mais d'un même rapport à date égale : sur le
    profil à mi-temps dix ans et sur la carrière entière à temps plein liquidée
    la même année (``minimum_garanti_1946``), le rapport est le même. Leurs
    barèmes lisent donc les mêmes services, réduits par la quotité, ce que
    l'action 154 voulait vérifier (point 4)."""
    code = "temps_partiel_minimum_garanti_1946"
    eux, moi = temoin["profils"][code]["openfisca"], nous[code]
    reference = json.loads(TEMOIN_FONCTION_PUBLIQUE.read_text(encoding="utf-8"))[
        "profils"]["minimum_garanti_1946"]
    assert reference["profil"]["liquidation"] == temoin["profils"][code]["profil"]["liquidation"]
    plein = _notre_calcul(simulateur, reference["profil"])
    # Les deux minima jouent, des deux côtés.
    assert moi["pension"] > moi["pension_avant_minimum"]
    assert plein["pension"] > plein["pension_avant_minimum"]
    assert eux["pension_brute"] == pytest.approx(eux["minimum_garanti"], rel=1e-9)
    assert moi["pension"] / eux["minimum_garanti"] == pytest.approx(
        plein["pension"] / reference["openfisca"]["minimum_garanti"], rel=PRECISION_OPENFISCA)
    assert moi["pension"] < plein["pension"]


def test_la_surcote_a_temps_partiel_lit_la_duree_entiere(temoin, nous):
    """L. 14, III : la surcote compte la durée d'assurance au-delà de la durée
    requise, que le temps partiel ne réduit pas. À 90 % depuis ses soixante
    ans, le fonctionnaire né en 1949 a 172 trimestres pour 161 requis : onze
    de surcote à 1,25 %, des deux côtés, quand ses services n'en font que 170."""
    code = "temps_partiel_surcote_1949"
    eux, moi = temoin["profils"][code]["openfisca"], nous[code]
    assert eux["surcote_trimestres"] == moi["duree_assurance"] - moi["proratisation"] == 11
    assert moi["services"] == eux["services"] == 170
    assert moi["taux_de_liquidation"] == pytest.approx(
        TAUX_PLEIN * (1 + 0.0125 * 11), abs=TOLERANCE_EXACTE)
    assert eux["taux_de_liquidation"] == pytest.approx(
        moi["taux_de_liquidation"], abs=TOLERANCE_EXACTE)


# -- le départ anticipé des parents de trois enfants -----------------------------

#: L'année dont chaque modèle lit la durée requise et la décote du parent de
#: trois enfants — la nôtre, la sienne —, et pourquoi elles diffèrent.
#: L'année des conditions réunies, dans l'ancien calcul (loi n° 2003-775,
#: article 66, II et III ; loi n° 2010-1330, article 44, IV, 1° et 2°) ; celle
#: des soixante ans dans le nouveau (article 44, IV).
ANNEES_DES_PARENTS = {
    "mere_conditions_1992": (1992, 1992),
    "cnracl_mere_conditions_2007": (2007, 2007),
    "mere_conditions_2009": (2009, 2009),
    # Ses quinze ans, que L. 5 compte en entier, sont acquis en 2004 ; lui les
    # compte sur les services réduits, et ne les lui donne qu'en 2006.
    "mere_temps_partiel_conditions_2004": (2004, 2006),
    # Il lui ferme le départ : son âge d'ouverture, soixante ans en 2022.
    "cnracl_mere_nee_en_1962": (2004, 2022),
    # Partie en 2012 : ses soixante ans, en 2016 ; lui, son âge d'ouverture.
    "mere_partie_en_2012": (2016, 2018),
    # La raison « famille » : il date les conditions du départ.
    "mere_partie_en_2012_raison_famille": (2016, 2012),
}

#: La durée de services et bonifications exigée pour le pourcentage maximum,
#: selon l'année retenue : celle de l'article 66, II, de la loi n° 2003-775
#: jusqu'en 2008 (150 « Jusqu'en 2003 », 152 en 2004, 158 en 2007), puis celle
#: « des fonctionnaires atteignant [soixante ans] l'année à compter de laquelle
#: la liquidation peut intervenir » (article 5, VI, rédaction du 11 novembre
#: 2010) : 161 en 2009, la génération 1949 ; 166 en 2016, la génération 1956.
DUREE_DE_L_ANNEE = {1992: 150, 2004: 152, 2007: 158, 2009: 161, 2016: 166}

#: Le coefficient de minoration par trimestre, selon l'année retenue : « Sans
#: objet » jusqu'en 2005, puis le tableau de l'article 66, III, de la loi
#: n° 2003-775 ; 1,25 % au-delà de 2014, et après 2019 celui de L. 14, I.
#: OpenFisca lit au-delà de 2015 la ligne de 2015.
COEFFICIENT_DE_DECOTE = {2006: 0.00125, 2007: 0.0025, 2008: 0.00375, 2009: 0.005,
                         2010: 0.00625, 2011: 0.0075, 2012: 0.00875, 2013: 0.01,
                         2014: 0.01125}
DERNIER_ANNEE_SANS_DECOTE = 2005
COEFFICIENT_AU_DELA = 0.0125
#: Les profils décotés le sont tous des vingt trimestres du plafond de L. 14, I.
DECOTE_PLAFONNEE = 20


def _coefficient_de_decote(annee: int) -> float:
    if annee <= DERNIER_ANNEE_SANS_DECOTE:
        return 0.0
    return COEFFICIENT_DE_DECOTE.get(annee, COEFFICIENT_AU_DELA)


def _annee(date_iso: str) -> int:
    return int(date_iso[:4])


def _annee_des_quinze_ans(profil: dict, *, a_la_quotite: bool) -> int:
    """L'année au cours de laquelle quinze ans de services s'achèvent : en
    années entières, comme L. 5 les compte pour constituer le droit, ou en
    services réduits par la quotité, comme OpenFisca les compte."""
    partiel = _quotites(profil) if a_la_quotite else {}
    cumul = 0.0
    for annee in range(profil["debut"], profil["liquidation"]):
        cumul += SERVICES_PAR_AN * partiel.get(annee, 1.0)
        if cumul >= 15 * SERVICES_PAR_AN - 1e-9:
            return annee
    raise AssertionError(f"{profil['code']} : moins de quinze ans de services")


def test_les_parents_reunissent_les_conditions_la_meme_annee(temoin, nous):
    """Trois enfants et quinze ans de services : la dernière des deux
    conditions date le droit. OpenFisca la date du 1er janvier, le dépôt du
    mois (la convention) ; l'année est la même, à temps plein — sauf quand
    lui la date du départ, à la raison « famille ». Le père n'a rien chez
    nous : son cas est plus bas."""
    for code, entree in _meres(temoin):
        profil, eux, depart = entree["profil"], entree["openfisca"], nous[code]["depart"]
        troisieme = int(sorted(profil["naissances"])[2][:4])
        notre_annee = profil["naissance"] + int(depart.age_ouverture + 1e-9)
        assert notre_annee == max(troisieme, _annee_des_quinze_ans(profil, a_la_quotite=False)), code
        if profil.get("raison") == "famille":
            assert eux["conditions_reunies_le"] == f"{profil['liquidation']}-01-01", code
        elif profil.get("temps_partiel"):
            assert _annee(eux["conditions_reunies_le"]) == max(
                troisieme, _annee_des_quinze_ans(profil, a_la_quotite=True)), code
        else:
            assert _annee(eux["conditions_reunies_le"]) == notre_annee, code


def test_le_temps_partiel_compte_en_entier_dans_les_quinze_ans(temoin, nous):
    """L. 5 : « Les services pris en compte dans la constitution du droit à
    pension sont : 1° Les services accomplis en qualité de fonctionnaire
    titulaire, la période pendant laquelle les intéressés ont été autorisés à
    accomplir un service à temps partiel [...] étant comptée pour la totalité
    de sa durée » (rédaction du 27 juillet 1991, LEGIARTI000006362669 ; celle
    de 2004 de même). Entrée en 1990, à 80 % de 1991 à 2000, la mère a ses
    quinze ans fin 2004 : 152 trimestres, aucune décote. OpenFisca les compte
    sur ses services réduits, qui n'en font soixante trimestres qu'en 2006 :
    l'année de la décote à 0,125 %. L'écart est le sien."""
    code = "mere_temps_partiel_conditions_2004"
    entree = temoin["profils"][code]
    profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
    assert moi["depart"].annee_des_parametres == _annee_des_quinze_ans(
        profil, a_la_quotite=False) == 2004
    assert _annee(eux["conditions_reunies_le"]) == _annee_des_quinze_ans(
        profil, a_la_quotite=True) == 2006
    # Le reste concorde : la durée, les services réduits, la bonification.
    assert moi["duree_assurance"] == eux["duree_assurance"] == 96
    assert moi["services"] == eux["services"] == 76


def test_la_bonification_et_la_duree_des_parents_concordent(temoin, nous):
    """L. 12, b : un an de bonification par enfant né avant 2004, à la mère que
    la présomption fait interrompre son activité — douze trimestres —, que la
    durée d'assurance compte aussi (L. 14, I). Le père n'en a pas, des deux
    côtés."""
    for code, entree in _de_la_regle(temoin, PARENTS):
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        bonification = SERVICES_PAR_AN * 3 if profil["sexe"] == "F" else 0
        assert moi["services_et_bonifications"] - moi["services"] \
            == eux["bonification"] == bonification, code
        assert moi["services"] == eux["services"], code
        assert moi["duree_assurance"] == eux["duree_assurance"], code


def test_la_duree_requise_des_parents_est_celle_de_l_annee_retenue(temoin, nous):
    """L'article 66, II, de la loi n° 2003-775 fixe le nombre de trimestres du
    pourcentage maximum selon l'« Année au cours de laquelle sont réunies les
    conditions mentionnées au I et au II de l'article L. 24 » : 150 jusqu'en
    2003. Son article 5, VI, prend ensuite la durée « en vigueur lorsqu'ils
    [...] remplissent les conditions de liquidation » (rédaction de 2006), puis
    celle des « fonctionnaires atteignant [soixante ans] l'année à compter de
    laquelle la liquidation peut intervenir » (rédaction du 11 novembre 2010).
    OpenFisca proratise toujours sur la durée de la génération : la mère née
    en 1953 qui réunit ses conditions en 1992 a chez lui 165 trimestres requis,
    150 chez nous. L'écart est le sien, et le test vérifie que chacun rend
    exactement ce que sa règle commande."""
    for code, entree in _meres(temoin):
        eux, moi = entree["openfisca"], nous[code]
        notre_annee, _ = ANNEES_DES_PARENTS[code]
        assert moi["proratisation"] == DUREE_DE_L_ANNEE[notre_annee], code
        assert moi["prorata_du_detail"] == (
            min(moi["services_et_bonifications"], moi["proratisation"]),
            moi["proratisation"]), code
        assert eux["coefficient_de_proratisation"] == pytest.approx(
            _coefficient_de_proratisation(eux["services"], eux["bonification"],
                                          eux["duree_requise_de_la_generation"]),
            abs=TOLERANCE_EXACTE), code


def test_la_decote_des_parents_est_celle_de_l_annee_retenue(temoin, nous):
    """La décote de l'année retenue, des deux côtés : le barème de l'article 66,
    III, « Sans objet » jusqu'en 2005, et son âge d'annulation, « Limite d'âge
    moins » tant de trimestres. Sur l'année des conditions, quand les deux la
    retiennent, ils concordent — 0,25 % en 2007, 0,5 % en 2009 ; ailleurs,
    chacun applique celui de l'année qu'il retient (``ANNEES_DES_PARENTS``)."""
    for code, entree in _meres(temoin):
        eux, moi = entree["openfisca"], nous[code]
        notre_annee, son_annee = ANNEES_DES_PARENTS[code]
        assert moi["taux_de_liquidation"] == pytest.approx(TAUX_PLEIN * (
            1 - _coefficient_de_decote(notre_annee) * DECOTE_PLAFONNEE),
            abs=TOLERANCE_EXACTE), code
        assert eux["taux_de_liquidation"] == pytest.approx(TAUX_PLEIN * (
            1 - _coefficient_de_decote(son_annee) * DECOTE_PLAFONNEE),
            abs=TOLERANCE_EXACTE), code


def test_la_pension_des_parents_ne_s_ecarte_que_de_l_annee_retenue(temoin, nous):
    """Le bout de la chaîne : traitement, services et bonification concordent,
    et la pension de chacun se déduit de l'autre en échangeant seulement la
    durée requise et le taux que l'année retenue commande. Rien d'autre ne
    les sépare."""
    for code, entree in _meres(temoin):
        eux, moi = entree["openfisca"], nous[code]
        assert moi["traitement_de_reference"] == pytest.approx(
            eux["traitement_de_reference"], rel=PRECISION_OPENFISCA), code
        echangee = (moi["pension_avant_minimum"]
                    * moi["proratisation"] / eux["duree_requise_de_la_generation"]
                    * eux["taux_de_liquidation"] / moi["taux_de_liquidation"])
        assert echangee == pytest.approx(eux["pension_avant_minimum"],
                                         rel=PRECISION_OPENFISCA), code


#: Le départ que chacun ouvre — le nôtre, le sien —, et ce qui tranche quand
#: ils diffèrent.
DEPARTS = {
    "mere_conditions_1992": (True, True),
    "cnracl_mere_conditions_2007": (True, True),
    "mere_conditions_2009": (True, True),
    "mere_temps_partiel_conditions_2004": (True, True),
    # L. 24, I, 3°, en vigueur jusqu'au 1er juillet 2011, ouvre le départ à
    # tout parent de trois enfants qui a quinze ans de services ; lui le ferme
    # à qui n'a ni son âge d'ouverture avant 2016 ni ses conditions avant 2003.
    "cnracl_mere_nee_en_1962": (True, False),
    # Article 44, III, de la loi n° 2010-1330 : qui réunit les conditions
    # avant 2012 « conserve la possibilité de liquider sa pension par
    # anticipation ». Lui ne l'ouvre plus après juin 2011…
    "mere_partie_en_2012": (True, False),
    # … qu'à la raison « famille », qu'on lui déclare.
    "mere_partie_en_2012_raison_famille": (True, True),
    # L'interruption d'activité pour chaque enfant (L. 24, I, 3°, depuis la loi
    # du 30 décembre 2004) : le dépôt la présume de la mère seule, OpenFisca ne
    # la lit pas. Une limite de la traduction, non une erreur de l'un ou l'autre.
    "pere_conditions_1992": (False, True),
}


def test_chacun_ouvre_le_depart_des_parents_selon_sa_regle(temoin, nous):
    """Où les deux ouvrent le départ, et où un seul — ``DEPARTS`` dit pourquoi.
    L'ancien calcul (l'année des conditions) demeure aux pensions prenant
    effet au plus tard le 1er juillet 2011 et aux nées avant 1956 ; les mères
    parties en 2012 ont le nouveau, l'année de leurs soixante ans."""
    assert set(DEPARTS) == {code for code, _ in _de_la_regle(temoin, PARENTS)}
    for code, (le_notre, le_sien) in DEPARTS.items():
        moi, eux = nous[code], temoin["profils"][code]["openfisca"]
        assert (moi["depart"] is not None) is le_notre, code
        assert moi["liquidation_ouverte"] is le_notre, code
        assert bool(eux["depart_anticipe"]) is le_sien, code
        if le_notre:
            nouveau = temoin["profils"][code]["profil"]["liquidation"] > 2011
            assert moi["depart"].ancien_calcul is not nouveau, code
            assert moi["depart"].annee_des_parametres == ANNEES_DES_PARENTS[code][0], code


def test_la_majoration_de_pension_est_de_dix_pour_cent_des_deux_cotes(temoin, nous):
    """L. 18 : dix pour cent de la pension au parent de trois enfants, au père
    comme à la mère, sur la pension de chacun ; rien au fonctionnaire sans
    enfant."""
    for code, entree in temoin["profils"].items():
        eux, moi = entree["openfisca"], nous[code]
        taux = 0.10 if entree["profil"]["regle"] == PARENTS else 0.0
        assert moi["majoration_pension"] == pytest.approx(taux * moi["pension"], abs=1e-6), code
        assert eux["majoration_pension"] == pytest.approx(
            taux * eux["pension_brute"], rel=PRECISION_OPENFISCA, abs=1e-6), code
