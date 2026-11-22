"""La pension de l'État liquidée sous le code de 1948 : les annuités
liquidables et la majoration pour enfants.

Loi n° 48-1450 du 20 septembre 1948 (JO du 21 septembre 1948, p. 9298-9307),
transcrite dans ``data/reference/textes/apportes/``, pour les droits ouverts
après sa promulgation (art. 64) et jusqu'au code de 1964. Fiches
``decompte_des_services_fonction_publique`` et
``majoration_enfants_plafond_fonction_publique``, version
``loi_du_20_septembre_1948``. Les attendus sont posés à la main depuis le
texte :

* **les services sédentaires ne comptent que pour cinq sixièmes** (art. 16,
  I, b, 1°), et les services actifs aussi, dans les trente premières années,
  pour qui n'a droit à pension qu'après trente ans (art. 16, I, b, 2°) ;
  l'agent de la catégorie B, qui a droit après vingt-cinq ans, compte ses
  services actifs entiers, et les sédentaires qui complètent ses vingt-cinq
  premières années (art. 16, I, a, 1° et 4°) ;
* **le décompte final se fait au semestre** : la fraction d'au moins trois
  mois compte pour six mois, la plus courte est négligée (art. 16, II) ;
* **la pension d'ancienneté demande trente ans de services** (vingt-cinq dans
  la catégorie B), les bonifications ne réduisant pas cette durée de plus
  d'un cinquième (art. 6, I ; art. 8, III) ; sans eux, la pension n'est que
  proportionnelle (art. 6, III, 3°), plafonnée à vingt-cinq annuités
  (art. 16, IV) et sans majoration pour enfants (art. 18, V, qui ne nomme que
  la pension d'ancienneté) ;
* **la pension majorée ne peut excéder les émoluments de base** (art. 18, V).

Les carrières commencent en 1930 : le modèle ne catalogue les pensions civiles
d'avant 1948 qu'à partir de cette année-là. La pension est de 2 % par annuité
(art. 18, I), soit 75 % × trimestres / 150.
"""

from __future__ import annotations

import pytest

from facade import Simulateur
from outils_pont import Saisies

SEDENTAIRE = "fonctionnaire_etat"
ACTIF = "fonctionnaire_etat_actif"


def _releve(*morceaux: tuple[str, int, int, str | None]) -> str:
    """Un relevé de fonctionnaire de l'État : ``(statut, première année,
    dernière année, trimestres de la première année)``, des années pleines
    ensuite."""
    lignes = []
    for statut, debut, fin, entree in morceaux:
        for annee in range(debut, fin + 1):
            trimestres = entree if (annee == debut and entree) else "4"
            lignes.append(f"{annee}:{statut}:20000:{trimestres}")
    return ",".join(lignes)


def _requete(naissance: str, *morceaux, sexe: str = "H", enfants: int = 0,
             liquidation: str = "1963-01") -> dict:
    requete = {"naissance": naissance, "sexe": sexe, "liquidation": liquidation,
               "releve": _releve(*morceaux)}
    if enfants:
        requete["enfants"] = enfants
    return requete


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies(Simulateur)


def _etat(saisies: Saisies, requete: dict):
    actuel = saisies.simuler(requete).actuel
    pension = next(p for p in actuel.pensions_par_regime
                   if p.regime == "fonction_publique_etat")
    majoration = sum(a.montant for a in actuel.avantages_appliques
                     if a.code == "majoration_enfants")
    return actuel, pension, majoration


@pytest.mark.parametrize(("entree", "trimestres"), [
    # Trente-deux ans et demi de services sédentaires : 9 750 jours aux cinq
    # sixièmes, 54 semestres et un mois, que le décompte final néglige.
    ("2", 108),
    # Trente-deux ans et neuf mois : 9 825 jours, 54 semestres et trois mois et
    # demi, comptés pour six mois.
    ("3", 110),
])
def test_les_services_sedentaires_comptent_cinq_sixiemes_au_semestre(saisies, entree,
                                                                      trimestres):
    _, pension, _ = _etat(saisies, _requete("1903-01-01", (SEDENTAIRE, 1930, 1962, entree)))
    assert f"× {trimestres}/150" in pension.detail, pension.detail
    assert "proportionnelle" not in pension.detail, pension.detail


def test_sans_trente_ans_de_services_la_pension_est_proportionnelle(saisies):
    """Vingt ans de services sédentaires à soixante ans : 6 000 jours aux cinq
    sixièmes, 33 semestres et deux mois, négligés ; 66 trimestres."""
    _, pension, _ = _etat(saisies, _requete("1903-01-01", (SEDENTAIRE, 1943, 1962, None)))
    assert "× 66/150" in pension.detail, pension.detail
    assert "pension proportionnelle" in pension.detail, pension.detail


def test_la_pension_proportionnelle_d_une_mere_n_est_pas_majoree(saisies):
    """Vingt-six ans de services et trois enfants : la bonification de trois ans
    ne porte la durée qu'à vingt-neuf ans, la pension est proportionnelle ;
    29 ans aux cinq sixièmes, 8 700 jours, 48 semestres et deux mois, négligés :
    96 trimestres. L'article 18, V, ne majore que la pension d'ancienneté."""
    _, pension, majoration = _etat(saisies, _requete(
        "1903-01-01", (SEDENTAIRE, 1937, 1962, None), sexe="F", enfants=3))
    assert "× 96/150" in pension.detail, pension.detail
    assert "pension proportionnelle" in pension.detail, pension.detail
    assert majoration == 0.0


def test_la_pension_d_anciennete_d_une_mere_est_majoree(saisies):
    """Vingt-huit ans de services et trois enfants : trente et un ans, la
    pension d'ancienneté ; 31 ans aux cinq sixièmes, 9 300 jours, 51 semestres
    et quatre mois, comptés pour six : 104 trimestres, majorés de 10 %."""
    _, pension, majoration = _etat(saisies, _requete(
        "1903-01-01", (SEDENTAIRE, 1935, 1962, None), sexe="F", enfants=3))
    assert "× 104/150" in pension.detail, pension.detail
    assert "proportionnelle" not in pension.detail, pension.detail
    assert majoration == pytest.approx(0.10 * pension.montant)


def test_la_categorie_b_compte_entiers_ses_services_actifs_et_ses_vingt_cinq_premieres_annees(
        saisies):
    """Vingt ans de services actifs de 1930 à 1949, puis treize sédentaires :
    les cinq premiers sédentaires complètent les vingt-cinq premières années et
    comptent entiers, les huit suivants pour cinq sixièmes ; 31 ans et 8 mois,
    11 400 jours, 63 semestres et deux mois, négligés : 126 trimestres."""
    _, pension, _ = _etat(saisies, _requete(
        "1903-01-01", (ACTIF, 1930, 1949, None), (SEDENTAIRE, 1950, 1962, None)))
    assert "× 126/150" in pension.detail, pension.detail


def test_la_pension_majoree_ne_depasse_pas_les_emoluments_de_base(saisies):
    """Trente-trois ans de services actifs, liquidés à cinquante-cinq ans :
    132 trimestres, 66 % du traitement ; douze enfants la majorent de 55 %, à
    102,3 %, que l'article 18, V, ramène au traitement."""
    actuel, pension, majoration = _etat(saisies, _requete(
        "1908-01-01", (ACTIF, 1930, 1962, None), enfants=12))
    assert "× 132/150" in pension.detail, pension.detail
    traitement = float(pension.detail.split("SR ")[1].split(" €")[0].replace(",", ""))
    assert pension.montant + majoration == pytest.approx(traitement, abs=0.01)


def test_le_code_de_1948_ne_vaut_pas_avant_sa_promulgation(saisies):
    fiches = saisies.simulateur(_requete("1903-01-01", (SEDENTAIRE, 1930, 1962, None))) \
        .scenario_actuel.fiches_datees
    assert fiches.regle("decompte_des_services_fonction_publique", "1948-09-01")["existe"] is False
    regle = fiches.regle("decompte_des_services_fonction_publique", "1948-10-01")
    assert (regle["unite_jours"], regle["seuil_jours"]) == (180, 90)
    assert regle["services_reduits"]["part"] == [5, 6]
    assert regle["pension_proportionnelle"]["maximum_trimestres"] == 100
    assert fiches.regle("majoration_enfants_plafond_fonction_publique",
                        "1948-10-01")["plafond"] == "traitement"


@pytest.mark.parametrize(("morceaux", "trimestres"), [
    # Catégorie B, quinze ans sédentaires puis dix-huit actifs : les sédentaires
    # « complètent » les dix-huit ans actifs jusqu'à vingt-cinq, quel que soit
    # l'ordre des années ; sept comptent entiers, huit aux cinq sixièmes :
    # 31 ans et 8 mois, 11 400 jours, 63 semestres et deux mois : 126.
    (((SEDENTAIRE, 1930, 1944, None), (ACTIF, 1945, 1962, None)), 126),
    # Catégorie A, dix ans actifs puis vingt-trois sédentaires : les actifs qui
    # « complètent » les vingt-trois sédentaires jusqu'à trente comptent aux cinq
    # sixièmes, les trois au-delà entiers : 28 ans, 10 080 jours, 56 semestres.
    (((ACTIF, 1930, 1939, None), (SEDENTAIRE, 1940, 1962, None)), 112),
])
def test_les_premieres_annees_se_completent_quel_que_soit_l_ordre(saisies, morceaux,
                                                                  trimestres):
    _, pension, _ = _etat(saisies, _requete("1903-01-01", *morceaux))
    assert f"× {trimestres}/150" in pension.detail, pension.detail


def test_les_bonifications_ne_reduisent_la_duree_que_d_un_cinquieme(saisies):
    """Vingt-deux ans de services et huit enfants : la bonification ne compte
    que pour six ans à la durée de trente ans (art. 8, III) ; vingt-huit, la
    pension est proportionnelle. Liquidée, elle compte trente ans aux cinq
    sixièmes, 9 000 jours, 50 semestres : 100 trimestres, le maximum."""
    _, pension, majoration = _etat(saisies, _requete(
        "1903-01-01", (SEDENTAIRE, 1941, 1962, None), sexe="F", enfants=8))
    assert "× 100/150" in pension.detail, pension.detail
    assert "pension proportionnelle" in pension.detail, pension.detail
    assert majoration == 0.0


def test_les_services_des_collectivites_comptent_a_la_duree(saisies):
    """Vingt-cinq ans à l'État et huit dans une collectivité : trente-trois ans
    de services (art. 8, I, 5°), la pension d'ancienneté, que l'État liquide
    avec les services de la collectivité (art. 11, I, 1°) : 33 ans aux cinq
    sixièmes, 9 900 jours, 55 semestres : 110 trimestres."""
    _, pension, _ = _etat(saisies, _requete(
        "1903-01-01", (SEDENTAIRE, 1930, 1944, None),
        ("fonctionnaire_territorial_hospitalier", 1945, 1952, None),
        (SEDENTAIRE, 1953, 1962, None)))
    assert "× 110/150" in pension.detail, pension.detail
    assert "proportionnelle" not in pension.detail, pension.detail


@pytest.mark.parametrize(("liquidation", "trimestres", "proportionnelle"), [
    # Le code de 1964 ne vaut qu'au 1er décembre 1964 : en juin, vingt ans
    # sédentaires font 66 trimestres d'une pension proportionnelle ; en
    # décembre, 80, sans les cinq sixièmes.
    ("1964-06", 66, True), ("1964-12", 80, False),
])
def test_le_code_de_1948_vaut_jusqu_au_code_de_1964(saisies, liquidation, trimestres,
                                                    proportionnelle):
    _, pension, _ = _etat(saisies, _requete(
        "1904-01-01", (SEDENTAIRE, 1944, 1963, None), liquidation=liquidation))
    assert f"× {trimestres}/150" in pension.detail, pension.detail
    assert ("pension proportionnelle" in pension.detail) is proportionnelle
    fiches = saisies.simulateur(_requete("1904-01-01", (SEDENTAIRE, 1944, 1963, None),
                                         liquidation=liquidation)).scenario_actuel.fiches_datees
    assert fiches.version("majoration_enfants_plafond_fonction_publique",
                          f"{liquidation}-01")["id"] == (
        "loi_du_20_septembre_1948" if proportionnelle else "code_de_1964")
