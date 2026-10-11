"""Les trimestres utiles de la DREES, rejoués sur le scénario 1.

L'Études et résultats n° 1283 de la DREES (Romain Guirriec, octobre 2023)
mesure, avec TRAJECTOiRE, ce que les majorations de durée d'assurance pour
enfants rapportent aux femmes nées en 1958. Un trimestre y est « utile » si,
retiré, il change la pension à âge inchangé : la méthode les retire un à un,
en recalculant le taux de liquidation, qui se lit tous régimes, et le
coefficient de proratisation, régime par régime. Son encadré 3 en donne cinq
exemples, pour la génération 1958 : âge légal de 62 ans, taux plein à 67 ans,
167 trimestres requis. Ce fichier les rejoue (action 137, note du 11 octobre
2026 ; registre des modèles, `trajectoire`).

La DREES ne publie de chaque exemple que la durée, l'âge, la décote ou la
surcote, les coefficients et le décompte des trimestres utiles. Chaque
carrière est donc la plus simple qui les rende : une femme née le 15 janvier
1958, salariée du privé, dont les deux enfants, nés en 1985 et en 1988, valent
huit trimestres chacun au régime général. Le polycotisant a ses seize
trimestres dans un régime de 55, et aucun dans l'autre : au scénario 1, c'est
une fonctionnaire de l'État passée par le privé, dont les quatre enfants, nés
avant 2004, valent une année de bonification chacun dans la fonction publique,
que R. 173-15 fait passer avant le régime général (`test_priorite_enfants.py`).
L'étude, elle, range la majoration dans le régime de la naissance (son
encadré 1) ; sa note 2 rappelle que la fonction publique passe d'abord « dans
les faits », et le code public de TRAJECTOiRE suit l'ordre de R. 173-15.

Le retrait se fait comme la DREES le décrit : la durée tous régimes et celle
du régime qui porte les trimestres en perdent un, l'âge et la carrière ne
bougent pas ; la décote et la surcote du modèle rendent le taux, le plafond de
chaque régime son coefficient. Les deux bouts se vérifient sur la liquidation
entière : rien retiré, celle de la carrière ; tout retiré, celle de la même
carrière sans enfant.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import liquider, ouvrir, releve
from retraite_notionnelle.simulateur import Simulateur

PRIVE = "salarie_prive_non_cadre"
ETAT = "fonctionnaire_etat"
REGIME_GENERAL = "regime_general"
FONCTION_PUBLIQUE = "fonction_publique_etat"

#: Ce que l'étude rappelle du droit qu'elle applique : le taux plein de chaque
#: régime, et la décote et la surcote, 1,25 % par trimestre.
TAUX_PLEIN = {REGIME_GENERAL: 0.50, FONCTION_PUBLIQUE: 0.75}
PAR_TRIMESTRE = 0.0125

#: Les salaires, constants : ce qui se compare ne dépend que des durées. Celui
#: de la fonctionnaire tient sa pension au-dessus du minimum garanti.
SALAIRES = {PRIVE: 25_000.0, ETAT: 40_000.0}

#: Huit trimestres chacun au régime général.
DEUX_ENFANTS = ("1985-05-10", "1988-03-02")
#: Nés avant 2004, une année de bonification chacun dans la fonction publique.
QUATRE_ENFANTS = ("1979-02-10", "1981-04-12", "1983-06-14", "1985-08-16")


def _periode(affiliation: str, debut: int, fin: int, premiere: int = 4,
             derniere: int = 4) -> tuple[AnneeCarriere, ...]:
    """Les années ``debut`` à ``fin`` : pleines, sauf la première et la
    dernière, qui ont ``premiere`` et ``derniere`` trimestres, à la part de
    l'année et au salaire qu'ils couvrent."""
    lignes = []
    for annee in range(debut, fin + 1):
        trimestres = premiere if annee == debut else derniere if annee == fin else 4
        lignes.append(AnneeCarriere(
            annee=annee, revenu=SALAIRES[affiliation] * trimestres / 4,
            affiliation=affiliation, trimestres_valides=trimestres,
            fraction_annee=trimestres / 4))
    return tuple(lignes)


@dataclass(frozen=True)
class Exemple:
    """Un exemple de l'encadré 3 : la carrière, puis ce que la DREES en publie."""

    nom: str
    age: int
    enfants: tuple[str, ...]
    lignes: tuple[AnneeCarriere, ...]
    #: Le régime qui porte les trimestres des enfants.
    porteur: str
    #: Ce que la DREES publie : la durée tous régimes, les trimestres de décote
    #: et de surcote, le numérateur du coefficient de chaque régime, sur 167,
    #: et les trimestres utiles au taux et à la proratisation.
    duree: int
    decote: int
    surcote: int
    coefficients: dict[str, int]
    utiles_au_taux: int
    utiles_a_la_proratisation: int


EXEMPLES = (
    # 165 trimestres dans un seul régime, dont 16 de majoration, au départ à
    # 62 ans : deux trimestres de décote, 165/167 ; « chaque trimestre de
    # moins lui ajoute un trimestre de décote » et un 167e de moins.
    Exemple("premier", 62, DEUX_ENFANTS, _periode(PRIVE, 1982, 2019, premiere=1),
            REGIME_GENERAL, duree=165, decote=2, surcote=0,
            coefficients={REGIME_GENERAL: 165},
            utiles_au_taux=16, utiles_a_la_proratisation=16),
    # 155 dont 16 : douze trimestres de décote, 155/167 ; huit seulement sont
    # utiles au taux, la décote butant ensuite sur les vingt trimestres qui
    # séparent 62 ans de 67.
    Exemple("deuxieme", 62, DEUX_ENFANTS, _periode(PRIVE, 1985, 2019, premiere=3),
            REGIME_GENERAL, duree=155, decote=12, surcote=0,
            coefficients={REGIME_GENERAL: 155},
            utiles_au_taux=8, utiles_a_la_proratisation=16),
    # 185 dont 16, au départ à 67 ans, après dix-huit trimestres validés entre
    # 62 et 67 ans : dix-huit trimestres de surcote, le coefficient plafonné à
    # 1 ; chaque trimestre retiré ôte un trimestre de surcote.
    Exemple("troisieme", 67, DEUX_ENFANTS,
            _periode(PRIVE, 1982, 2019, premiere=3)
            + _periode(PRIVE, 2020, 2024, premiere=3, derniere=3),
            REGIME_GENERAL, duree=185, decote=0, surcote=18,
            coefficients={REGIME_GENERAL: 167},
            utiles_au_taux=16, utiles_a_la_proratisation=0),
    # Le polycotisant : 185 trimestres, dont 16 dans un régime de 55, et 130
    # dans un autre, au départ à 62 ans ; ni décote ni surcote, 55/167 et
    # 130/167, le plafond jouant caisse par caisse.
    Exemple("polycotisant", 62, QUATRE_ENFANTS,
            _periode(PRIVE, 1977, 2009, premiere=2) + _periode(ETAT, 2010, 2019, premiere=3),
            FONCTION_PUBLIQUE, duree=185, decote=0, surcote=0,
            coefficients={FONCTION_PUBLIQUE: 55, REGIME_GENERAL: 130},
            utiles_au_taux=0, utiles_a_la_proratisation=16),
    # 185 dont 16, au départ à 62 ans : le taux plein, le coefficient
    # plafonné ; aucun trimestre utile.
    Exemple("dernier", 62, DEUX_ENFANTS, _periode(PRIVE, 1977, 2019, premiere=1),
            REGIME_GENERAL, duree=185, decote=0, surcote=0,
            coefficients={REGIME_GENERAL: 167},
            utiles_au_taux=0, utiles_a_la_proratisation=0),
)

#: Ce que le détail d'une pension en annuités dit de son calcul.
DETAIL = re.compile(r"× taux ([\d.]+)% × (\d+)/(\d+)$")


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _carriere(exemple: Exemple, avec_enfants: bool = True) -> Carriere:
    enfants = exemple.enfants if avec_enfants else ()
    return Carriere(annee_naissance=1958, sexe="F", lignes=list(exemple.lignes),
                    age_liquidation=float(exemple.age), jour_naissance=15,
                    identifiant=f"er_1283_{exemple.nom}", nombre_enfants=len(enfants),
                    naissances_enfants=enfants)


def _liquidee(simulateur: Simulateur, carriere: Carriere) -> dict[str, tuple[float, int, int]]:
    """Le taux et le coefficient que la liquidation de chaque régime de base a
    retenus, lus dans le détail de sa pension."""
    resultat = simulateur.scenario_actuel.calculer(carriere)
    assert not resultat.minimum_applique, carriere.identifiant
    lus = {}
    for pension in resultat.pensions_par_regime:
        if pension.regime in TAUX_PLEIN:
            taux, numerateur, denominateur = DETAIL.search(pension.detail).groups()
            lus[pension.regime] = (float(taux) / 100, int(numerateur), int(denominateur))
    return lus


def _retraits(simulateur: Simulateur, exemple: Exemple, carriere: Carriere
              ) -> list[tuple[float, float, dict[str, int]]]:
    """Pour chaque nombre de trimestres pour enfants retirés, de zéro à tous :
    les trimestres de décote et le coefficient de surcote du taux, tous
    régimes, et le numérateur du coefficient de chaque régime."""
    actuel = simulateur.scenario_actuel
    annee = carriere.annee_liquidation
    periode = simulateur.catalogue[REGIME_GENERAL].periode(annee)
    requis, _ = ouvrir.duree_requise(actuel, periode, carriere)
    proratisation, _ = liquider.duree_proratisation(actuel, periode, carriere, requis)
    _, age_annulation, _ = liquider.decote_opposable(actuel, periode, carriere, annee)
    age_surcote = ouvrir.age_surcote(actuel, periode, carriere)
    durees = releve.construire(actuel, carriere).durees
    assert durees.enfants.par_regime() == {exemple.porteur: (16, 16)}, exemple.nom
    etats = []
    for retires in range(durees.enfants.trimestres + 1):
        total = durees.trimestres - retires
        decote = liquider.trimestres_de_decote(actuel, periode, carriere, total, requis,
                                               carriere.age_liquidation, age_annulation)
        surcote, _ = liquider.coefficient_surcote_datee(
            actuel, periode, carriere, total, requis, max(0, total - requis), age_surcote)
        numerateurs = {
            code: min(durees.trimestres_par_regime[code]
                      - (retires if code == exemple.porteur else 0), proratisation)
            for code in exemple.coefficients}
        etats.append((float(decote), surcote, numerateurs))
    return etats


@pytest.mark.parametrize("exemple", EXEMPLES, ids=lambda e: e.nom)
def test_la_liquidation_est_celle_de_la_drees(simulateur, exemple):
    """La durée, la décote ou la surcote et le coefficient de chaque régime
    que l'encadré 3 publie, tels que la liquidation du scénario 1 les retient ;
    et la même liquidation, sans enfant, au bout du retrait."""
    carriere = _carriere(exemple)
    assert simulateur.scenario_actuel.calculer(carriere).trimestres_valides == exemple.duree
    etats = _retraits(simulateur, exemple, carriere)
    decote, surcote, numerateurs = etats[0]
    assert decote == exemple.decote
    assert surcote == pytest.approx(1 + PAR_TRIMESTRE * exemple.surcote)
    assert numerateurs == exemple.coefficients
    for bout, avec_enfants in ((etats[0], True), (etats[-1], False)):
        decote, surcote, numerateurs = bout
        lus = _liquidee(simulateur, _carriere(exemple, avec_enfants))
        assert set(lus) == set(exemple.coefficients), exemple.nom
        for code, (taux, numerateur, denominateur) in lus.items():
            assert taux == pytest.approx(
                TAUX_PLEIN[code] * (1 - PAR_TRIMESTRE * decote) * surcote, abs=5e-6), code
            assert (numerateur, denominateur) == (numerateurs[code], 167), code


@pytest.mark.parametrize("exemple", EXEMPLES, ids=lambda e: e.nom)
def test_les_trimestres_utiles_sont_ceux_de_la_drees(simulateur, exemple):
    """Retirés un à un, à âge inchangé : un trimestre est utile au taux s'il
    change la décote ou la surcote, à la proratisation s'il change un
    coefficient."""
    etats = _retraits(simulateur, exemple, _carriere(exemple))
    paires = list(zip(etats, etats[1:]))
    assert sum(avant[:2] != apres[:2] for avant, apres in paires) == exemple.utiles_au_taux
    assert (sum(avant[2] != apres[2] for avant, apres in paires)
            == exemple.utiles_a_la_proratisation)
