"""Le relevé d'une saisie, prolongé jusqu'au départ, sur tout le site.

Un relevé s'arrête à sa dernière année. Le site le poursuit jusqu'au départ
(:meth:`~retraite_notionnelle.contexte.Contexte.releve_prolonge`), à la
convention de :meth:`~retraite_notionnelle.carriere.Carriere.prolongee` — la
dernière année se prolonge —, comme le dernier métier d'un parcours court
jusqu'à lui et comme « Mon estimation retraite » prolonge les revenus. Qui ne
travaille plus le déclare dans « Interruptions ». Décidé par le propriétaire le
4 octobre 2026 (action 142). Les relevés sont fictifs.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import salaire_moyen_annuel
from retraite_notionnelle.donnees.chargement import charger_periodes_non_travaillees
from retraite_notionnelle.saisie import Saisie
from outils_web import contexte  # noqa: F401 — la fixture partagée

#: Né le 10 mars 1980, au régime général de 2002 à 2024 : 64 ans le 1er avril
#: 2044, les âges se comptant du mois qui suit la naissance.
RELEVE = "\n".join(f"{annee}:salarie_prive_non_cadre:{20_000 + 600 * (annee - 2002)}"
                   for annee in range(2002, 2025))
BASE = {"naissance": "1980-03-10", "liquidation": "64", "releve": RELEVE}
DERNIER_REVENU = 20_000 + 600 * (2024 - 2002)


def _ajoutees(contexte, **requete):
    """La saisie, et les lignes que le site ajoute à son relevé."""
    saisie = Saisie.depuis_requete({**BASE, **requete})
    return saisie, contexte.releve_prolonge(saisie)[len(saisie.releve_analyse()):]


def _macro(contexte, saisie):
    return contexte.simulateur(saisie.parametres(contexte.base)).macro


def test_la_derniere_annee_du_releve_se_poursuit_jusqu_au_depart(contexte):
    """Même statut, un revenu qui suit le salaire moyen, l'année du départ au
    prorata de ses mois : trois, de janvier à mars 2044. Les trimestres, le
    modèle les déduit du revenu."""
    saisie, ajoutees = _ajoutees(contexte)
    assert str(saisie.date_liquidation) == "avril 2044"
    assert [ligne.annee for ligne in ajoutees] == list(range(2025, 2045))
    macro = _macro(contexte, saisie)
    for ligne in ajoutees:
        assert ligne.affiliation == "salarie_prive_non_cadre"
        assert (ligne.type_periode, ligne.trimestres) == ("emploi", None)
        mois = 12 if ligne.annee < 2044 else 3
        assert ligne.revenu == pytest.approx(
            DERNIER_REVENU * salaire_moyen_annuel(macro, ligne.annee)
            / salaire_moyen_annuel(macro, 2024) * mois / 12)
    carriere = contexte.carriere(saisie)
    assert [ligne.annee for ligne in carriere.lignes][-1] == 2044


def test_qui_ne_travaille_plus_le_declare_et_garde_la_pension_de_son_releve(contexte):
    """« 2025:2044:sans_activite » : les années ajoutées sont sans activité, et
    chacun des six scénarios sert la pension du relevé arrêté à sa dernière
    année — celle que le site servait à tous avant le 4 octobre 2026."""
    saisie, ajoutees = _ajoutees(contexte, interruptions="2025:2044:sans_activite")
    assert {ligne.type_periode for ligne in ajoutees} == {"sans_activite"}
    simulateur = contexte.simulateur(saisie.parametres(contexte.base))
    motifs = charger_periodes_non_travaillees(simulateur.macro.racine)
    arretee = simulateur.simuler(
        contexte._carriere_relevee(simulateur, saisie, motifs, prolonger=False))
    declaree = contexte.simuler(saisie)
    poursuivie = contexte.simuler(Saisie.depuis_requete(BASE))
    for scenario in ("actuel", "notionnel_retroactif", "notionnel_prospectif",
                     "notionnel_retroactif_employeur", "notionnel_prospectif_employeur",
                     "notionnel_liberal"):
        assert (getattr(declaree, scenario).pension_annuelle
                == pytest.approx(getattr(arretee, scenario).pension_annuelle))
    assert poursuivie.actuel.pension_annuelle > 1.5 * declaree.actuel.pension_annuelle


def test_une_periode_a_l_etranger_vide_les_annees_qu_elle_occupe(contexte):
    """Comme pour une carrière de métiers : une année passée plus qu'à moitié
    hors de France est sans activité en France, et le champ « Interruptions »
    garde le dernier mot."""
    etranger = {"etranger1_pays": "DE", "etranger1_debut": "2030-01",
                "etranger1_fin": "2035-01", "etranger1_activite": "salariee"}
    _, ajoutees = _ajoutees(contexte, **etranger)
    assert [ligne.annee for ligne in ajoutees
            if ligne.type_periode == "sans_activite"] == list(range(2030, 2035))
    _, ajoutees = _ajoutees(contexte, interruptions="2031:2031:chomage_indemnise", **etranger)
    motifs = {ligne.annee: ligne.type_periode for ligne in ajoutees}
    assert (motifs[2030], motifs[2031], motifs[2035]) == (
        "sans_activite", "chomage_indemnise", "emploi")


def test_la_retraite_progressive_met_les_annees_ajoutees_a_temps_partiel(contexte):
    """À 62 ans, le 1er avril 2042, à 60 % : trois mois pleins en 2042, puis le
    temps partiel, dont le revenu est celui que le relevé porterait."""
    _, pleines = _ajoutees(contexte)
    saisie, partielles = _ajoutees(contexte, progressive="62", quotite="60")
    quotites = {pleine.annee: partielle.revenu / pleine.revenu
                for pleine, partielle in zip(pleines, partielles)}
    assert quotites[2041] == 1.0
    assert quotites[2042] == pytest.approx((3 + 9 * 0.6) / 12)
    assert quotites[2043] == pytest.approx(0.6)
    assert quotites[2044] == pytest.approx(0.6)
    # La chronologie la date du même mois que la prolongation.
    assert contexte.carriere(saisie).retraite_progressive == (DateMois(2042, 4), 0.6)


def test_la_radiation_pour_invalidite_arrete_l_emploi_qu_elle_clot(contexte):
    """Le fonctionnaire radié en juin 2030 travaille jusqu'à sa radiation, et
    plus au-delà : ce qui la suit, le relevé ne le dit pas. Sans cet arrêt, le
    contrôle de la radiation refuserait la carrière que le site a prolongée."""
    releve = RELEVE.replace("salarie_prive_non_cadre", "fonctionnaire_etat")
    saisie, ajoutees = _ajoutees(contexte, releve=releve, radiation_invalidite="2030-06",
                                 taux_invalidite="60")
    assert [ligne.annee for ligne in ajoutees] == list(range(2025, 2031))
    macro = _macro(contexte, saisie)
    assert ajoutees[-1].revenu == pytest.approx(
        DERNIER_REVENU * salaire_moyen_annuel(macro, 2030)
        / salaire_moyen_annuel(macro, 2024) * 5 / 12)
    carriere = contexte.carriere(saisie)
    assert carriere.radiation_pour_invalidite.date == DateMois(2030, 6)
    assert not carriere.lignes_de(2031)
    assert contexte.simuler(saisie).actuel.pension_annuelle > 0


def test_qui_est_deja_parti_garde_son_releve_tel_quel(contexte):
    """Parti en 2022 : son relevé dit toute sa carrière, et ce qui y manque
    — de 2018 au départ — n'a pas été travaillé."""
    releve = "\n".join(f"{annee}:salarie_prive_non_cadre:20000" for annee in range(1980, 2018))
    saisie, ajoutees = _ajoutees(contexte, naissance="1958-03-10", releve=releve)
    assert saisie.date_liquidation.annee < saisie.parametres(contexte.base).annee_courante
    assert ajoutees == []


def test_un_releve_qui_touche_le_depart_ne_gagne_que_les_mois_qui_lui_manquent(contexte):
    """Né en janvier 1975, le 15 présumé, parti le 1er février 2039 : un relevé
    qui finit en 2038 gagne janvier 2039, un douzième de son revenu avancé
    d'une année ; un relevé qui porte 2039, ou un départ de janvier, rien."""
    jusqu_en_2038 = "\n".join(f"{annee}:salarie_prive_non_cadre:20000"
                              for annee in range(1998, 2039))
    saisie, ajoutees = _ajoutees(contexte, naissance="1975", releve=jusqu_en_2038)
    assert str(saisie.date_liquidation) == "février 2039"
    macro = _macro(contexte, saisie)
    assert [(ligne.annee, ligne.type_periode) for ligne in ajoutees] == [(2039, "emploi")]
    assert ajoutees[0].revenu == pytest.approx(
        20_000 * salaire_moyen_annuel(macro, 2039) / salaire_moyen_annuel(macro, 2038) / 12)
    _, ajoutees = _ajoutees(contexte, naissance="1975",
                            releve=jusqu_en_2038 + "\n2039:salarie_prive_non_cadre:2000")
    assert ajoutees == []
    _, ajoutees = _ajoutees(contexte, naissance="1975-01-01", releve=jusqu_en_2038)
    assert ajoutees == []


def test_la_proposition_poursuit_le_releve_prolonge_jusqu_a_son_age_legal(contexte):
    """Le relevé prolongé touche son départ : la proposition, qui reporte le
    départ à son âge légal, le poursuit donc jusque-là. Un relevé arrêté avant
    son départ ne l'était pas (action 134, point 3)."""
    comparaison = contexte.simuler(Saisie.depuis_requete(BASE))
    reportee = comparaison.carriere_liberal
    assert reportee.age_liquidation == comparaison.parametres.age_legal_liberal == 65.0
    assert str(reportee.date_liquidation) == "avril 2045"
    assert [ligne.annee for ligne in reportee.lignes][-1] == 2045
