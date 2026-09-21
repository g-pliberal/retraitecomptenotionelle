"""Tests des scénarios et du simulateur, au niveau du comportement attendu."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import (
    AnneeCarriere,
    Carriere,
    LigneRelevee,
    Metier,
)
from retraite_notionnelle.config import (
    RACINE_DONNEES,
    AgeConversionDroitsAcquis,
    ModeAgeReference,
    PartCotisation,
    ModeIndexation,
    Neutralisations,
    Parametres,
    SituationFoyer,
    SourceCotisations,
)
from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Simulateur

#: Témoins versionnés : ce que des sources extérieures ont réellement publié.
RACINE_TEMOINS = Path(__file__).resolve().parent / "temoins"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def test_la_trajectoire_d_emploi_ne_deplace_que_les_systemes_reformes():
    """Le système 1 ne lit ni la masse salariale ni le PIB : il ne bouge pas.

    Les systèmes 2 à 6 sont indexés sur la masse salariale, que la trajectoire
    d'emploi compose : pour une carrière qui s'achève dans la bosse d'emploi
    du COR (années 2030-2040), leur pension monte ; elle monte moins, ou
    baisse, pour qui liquide après le recul. Le système 1 est identique au
    centime dans les deux cas.
    """
    cor = Simulateur(Parametres(trajectoire_emploi="cor_2026"))
    constant = Simulateur(Parametres(trajectoire_emploi="constant"))
    pensions = {}
    for nom, sim in (("cor", cor), ("constant", constant)):
        carriere = sim.carriere_simple(
            annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=22, age_liquidation=64,
        )
        comparaison = sim.simuler(carriere)
        pensions[nom] = {
            scenario: getattr(comparaison, scenario).pension_annuelle
            for scenario in ("actuel", "notionnel_retroactif",
                             "notionnel_retroactif_employeur", "notionnel_liberal")
        }
    assert pensions["cor"]["actuel"] == pensions["constant"]["actuel"]
    for scenario in ("notionnel_retroactif", "notionnel_retroactif_employeur",
                     "notionnel_liberal"):
        assert pensions["cor"][scenario] > pensions["constant"][scenario]
        assert pensions["cor"][scenario] / pensions["constant"][scenario] < 1.06


@pytest.fixture(scope="module")
def salarie_moyen(simulateur) -> Carriere:
    return simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=21, age_liquidation=62, identifiant="salarié moyen",
    )


# -- construction de carrière ------------------------------------------------


def test_carriere_couvre_les_bonnes_annees(salarie_moyen):
    assert salarie_moyen.premiere_annee == 1981
    assert salarie_moyen.derniere_annee == 2021
    assert salarie_moyen.annee_liquidation == 2022


def test_interruptions_ne_produisent_aucune_cotisation(simulateur):
    carriere = simulateur.carriere_simple(
        annee_naissance=1970, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
        interruptions={annee: "education_enfant" for annee in range(2000, 2005)},
    )
    for annee in range(2000, 2005):
        ligne = carriere.ligne(annee)
        assert ligne is not None and not ligne.cotise and ligne.revenu == 0.0


# -- plusieurs métiers dans une vie ------------------------------------------


def test_un_seul_metier_donne_exactement_la_carriere_simple(simulateur):
    """Le chemin général et le raccourci ne peuvent pas diverger.

    ``carriere_simple`` n'est plus qu'un appel à ``carriere_parcours`` avec un
    métier unique : si les deux ne rendaient pas la même carrière au centime
    près, tout le passé du modèle aurait bougé sans que personne le demande.
    """
    commun = dict(annee_naissance=1975, sexe="H", age_liquidation=64)
    simple = simulateur.carriere_simple(
        affiliation="salarie_prive_non_cadre", age_debut=21,
        niveau_salaire=1.3, profil_carriere="ascendant", **commun,
    )
    parcours = simulateur.carriere_parcours(
        metiers=[Metier("salarie_prive_non_cadre", 21, 1.3)],
        profil_carriere="ascendant", **commun,
    )
    assert [ligne.revenu for ligne in parcours.lignes] == [
        ligne.revenu for ligne in simple.lignes
    ]
    assert parcours.lignes == simple.lignes


def test_chaque_metier_couvre_ses_annees(simulateur):
    carriere = simulateur.carriere_parcours(
        annee_naissance=1975, sexe="H", age_liquidation=64,
        metiers=[
            Metier("salarie_prive_non_cadre", 21),
            Metier("fonctionnaire_etat", 40),
            Metier("artisan", 55),
        ],
    )
    assert carriere.ligne(1996).affiliation == "salarie_prive_non_cadre"
    assert carriere.ligne(2014).affiliation == "salarie_prive_non_cadre"
    assert carriere.ligne(2015).affiliation == "fonctionnaire_etat"
    assert carriere.ligne(2029).affiliation == "fonctionnaire_etat"
    assert carriere.ligne(2030).affiliation == "artisan"
    assert carriere.affiliations_utilisees() == (
        "salarie_prive_non_cadre", "fonctionnaire_etat", "artisan",
    )


def test_l_annee_du_changement_additionne_les_deux_revenus(simulateur):
    """Un an à deux métiers paie ce que les deux ont versé, au prorata des mois.

    Le moteur ne connaît qu'une ligne par année civile : le STATUT de l'année
    est celui qui l'occupe le plus longtemps, mais le REVENU reste la somme.
    Rattacher l'année entière au nouveau métier ferait apparaître un salaire
    qui n'a jamais été perçu.
    """
    commun = dict(annee_naissance=1975, sexe="H", mois_naissance=5,
                  age_liquidation=64, profil_carriere="plat")
    carriere = simulateur.carriere_parcours(
        metiers=[Metier("salarie_prive_non_cadre", 21, 1.0),
                 Metier("artisan", 42, 3.0)], **commun)
    # Né en mai 1975, il change de métier en mai 2017 : quatre mois au premier
    # niveau, huit au second. Les deux carrières de référence n'ont ni le même
    # statut ni le même niveau, mais la même année et le même profil : ce qui
    # les sépare est exactement ce que le prorata doit retrouver.
    premier = simulateur.carriere_parcours(
        metiers=[Metier("salarie_prive_non_cadre", 21, 1.0)], **commun)
    second = simulateur.carriere_parcours(
        metiers=[Metier("artisan", 21, 3.0)], **commun)
    attendu = (premier.ligne(2017).revenu * 4 / 12
               + second.ligne(2017).revenu * 8 / 12)

    assert carriere.ligne(2017).revenu == pytest.approx(attendu)
    assert carriere.ligne(2017).affiliation == "artisan"
    assert carriere.ligne(2017).fraction_annee == 1.0


def test_l_annee_partagee_en_deux_revient_au_metier_qui_l_ouvre(simulateur):
    """Six mois contre six mois : l'égalité va au métier qui commence l'année.

    Il faut bien trancher — une année n'a qu'un statut —, et la convention est
    écrite ici pour qu'elle ne se découvre pas par surprise.
    """
    carriere = simulateur.carriere_parcours(
        annee_naissance=1975, sexe="H", mois_naissance=7, age_liquidation=64,
        metiers=[
            Metier("salarie_prive_non_cadre", 21),
            Metier("artisan", 42),
        ],
    )
    assert carriere.ligne(2017).affiliation == "salarie_prive_non_cadre"
    assert carriere.ligne(2018).affiliation == "artisan"


def test_changer_pour_un_regime_plus_cotise_remplit_davantage_le_compte(simulateur):
    """C'est ce que la carrière multiple sert à mesurer.

    Un artisan verse une cotisation retraite plus lourde qu'un salarié non
    cadre, part patronale mise à part : une seconde moitié de carrière sous ce
    statut porte donc plus au compte notionnel qu'une carrière entière sous le
    premier.
    """
    commun = dict(annee_naissance=1975, sexe="H", age_liquidation=64)
    salarie = simulateur.simuler(simulateur.carriere_parcours(
        metiers=[Metier("salarie_prive_non_cadre", 21)], **commun))
    reconverti = simulateur.simuler(simulateur.carriere_parcours(
        metiers=[Metier("salarie_prive_non_cadre", 21),
                 Metier("artisan", 42)], **commun))
    artisan = simulateur.simuler(simulateur.carriere_parcours(
        metiers=[Metier("artisan", 21)], **commun))

    cotise = lambda resultat: resultat.notionnel_retroactif.compte.cotisations_versees
    assert cotise(salarie) < cotise(reconverti) < cotise(artisan)


def test_des_metiers_qui_ne_se_suivent_pas_sont_rejetes(simulateur):
    commun = dict(annee_naissance=1975, sexe="H", age_liquidation=64)
    with pytest.raises(ValueError, match="se suivre"):
        simulateur.carriere_parcours(
            metiers=[Metier("salarie_prive_non_cadre", 21),
                     Metier("artisan", 20)], **commun)
    with pytest.raises(ValueError, match="après la liquidation"):
        simulateur.carriere_parcours(
            metiers=[Metier("salarie_prive_non_cadre", 21),
                     Metier("artisan", 70)], **commun)
    with pytest.raises(ValueError, match="au moins un métier"):
        simulateur.carriere_parcours(metiers=[], **commun)


def test_un_metier_de_statut_inconnu_est_rejete(simulateur):
    with pytest.raises(KeyError, match="affiliation inconnue"):
        simulateur.carriere_parcours(
            annee_naissance=1975, sexe="H", age_liquidation=64,
            metiers=[Metier("salarie_prive_non_cadre", 21),
                     Metier("boulanger_lunaire", 40)],
        )


def test_affiliation_inconnue_est_rejetee(simulateur):
    with pytest.raises(KeyError, match="affiliation inconnue"):
        simulateur.carriere_simple(1970, "H", "boulanger_lunaire", 20, 64)


def test_liquidation_avant_debut_est_rejetee(simulateur):
    with pytest.raises(ValueError, match="antérieur"):
        simulateur.carriere_simple(1970, "H", "salarie_prive_non_cadre", 40, 30)


def test_carriere_sans_age_de_liquidation_est_signalee():
    carriere = Carriere(
        annee_naissance=1960, sexe="H",
        lignes=[AnneeCarriere(1990, 20000.0, "salarie_prive_non_cadre")],
    )
    with pytest.raises(ValueError, match="âge de liquidation"):
        _ = carriere.annee_liquidation


# -- la carrière lue sur un relevé -------------------------------------------


def _releve(premiere: int, derniere: int,
            statut: str = "salarie_prive_non_cadre") -> list[LigneRelevee]:
    return [LigneRelevee(annee=annee, affiliation=statut,
                         revenu=20000.0 + 500 * (annee - premiere), trimestres=4)
            for annee in range(premiere, derniere + 1)]


def test_le_releve_porte_les_revenus_tels_qu_ils_sont_declares(simulateur):
    """Rien n'est reconstitué : ni le revenu, ni les trimestres de l'année."""
    carriere = simulateur.carriere_releve(
        annee_naissance=1960, sexe="H", releve=_releve(1985, 2021),
        age_liquidation=62,
    )
    assert carriere.premiere_annee == 1985
    assert carriere.derniere_annee == 2021
    assert carriere.ligne(1985).revenu == 20000.0
    assert carriere.ligne(2000).revenu == 27500.0
    assert all(ligne.trimestres_valides == 4 for ligne in carriere.lignes)
    # Une ligne vaut une année civile pleine : le relevé donne l'année, pas le
    # mois, et le modèle ne peut rien annualiser qu'il ne sache pas.
    assert all(ligne.fraction_annee == 1.0 for ligne in carriere.lignes)


def test_les_trimestres_omis_se_deduisent_du_montant(simulateur):
    """Sans quatrième champ, le relevé retombe sur la règle du montant cotisé.

    Un revenu dérisoire ne valide pas quatre trimestres — 150 fois le SMIC
    horaire en vaut un —, et c'est ce que le modèle recalcule quand le relevé
    se tait.
    """
    carriere = simulateur.carriere_releve(
        annee_naissance=1960, sexe="H", age_liquidation=62,
        releve=[LigneRelevee(annee=2000, affiliation="salarie_prive_non_cadre",
                             revenu=1500.0)],
    )
    assert carriere.ligne(2000).trimestres_valides < 4


def test_une_annee_posterieure_au_depart_est_rejetee(simulateur):
    with pytest.raises(ValueError, match="postérieure au départ"):
        simulateur.carriere_releve(
            annee_naissance=1960, sexe="H", age_liquidation=62,
            releve=_releve(1985, 2023),
        )


def test_un_releve_vide_est_rejete(simulateur):
    with pytest.raises(ValueError, match="au moins une ligne"):
        simulateur.carriere_releve(
            annee_naissance=1960, sexe="H", age_liquidation=62, releve=[],
        )


def test_la_periode_non_cotisee_du_releve_suit_les_memes_regles(simulateur):
    """Le chemin lu et le chemin paramétrique partagent la règle, pas le code.

    Ce qu'une période assimilée ouvre — des trimestres gratuits, des points
    complémentaires financés par l'UNEDIC — est écrit une seule fois : une
    ligne de relevé déclarée au chômage doit donc en sortir comme l'année
    qu'une plage d'interruption aurait produite.
    """
    carriere = simulateur.carriere_releve(
        annee_naissance=1960, sexe="H", age_liquidation=62,
        releve=[LigneRelevee(annee=2000, affiliation="salarie_prive_non_cadre",
                             revenu=30000.0, trimestres=4,
                             type_periode="chomage_indemnise")],
    )
    ligne = carriere.ligne(2000)
    assert not ligne.cotisations_versees
    assert ligne.revenu == 0.0
    assert ligne.revenu_reference == 30000.0
    assert ligne.familles_cotisantes == ("complementaire_prive",)


# -- les trois scénarios -----------------------------------------------------


def test_les_trois_scenarios_sont_calcules(simulateur, salarie_moyen):
    comparaison = simulateur.simuler(salarie_moyen)
    assert comparaison.actuel.pension_annuelle > 0
    assert comparaison.notionnel_retroactif.pension_annuelle > 0
    assert comparaison.notionnel_prospectif.pension_annuelle > 0


def test_retraite_deja_liquidee_est_inchangee_dans_le_scenario_prospectif(simulateur):
    """Un retraité de 2005 ne peut pas voir ses droits recalculés en 2026."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=60,
    )
    comparaison = simulateur.simuler(carriere)
    assert comparaison.notionnel_prospectif.pension_annuelle == pytest.approx(
        comparaison.actuel.pension_annuelle
    )
    assert comparaison.variation("notionnel_prospectif") == pytest.approx(0.0)


def test_convertir_les_droits_acquis_a_l_age_de_depart_les_preserve(simulateur):
    """La convention de conversion est le seul abattement sur des droits ouverts.

    Converti au diviseur de l'âge de référence, un droit déjà acquis perd le
    rapport des deux diviseurs dès lors que l'assuré liquide avant cet âge.
    Converti à l'âge de départ effectif, il ne perd rien : la sanction
    d'anticipation ne joue plus que sur les cotisations, comme prévu.

    Les deux conventions ne se séparent que si les deux âges diffèrent : le
    cliquet est donc nommé ici, là où le défaut fixe la référence à 64 ans et
    fait coïncider les deux sur un départ à 64 ans. C'est le sujet du test, pas
    un détail de montage.
    """
    cliquet = Parametres().avec(mode_age_reference=ModeAgeReference.CLIQUET_LEGAL)
    simulateur = Simulateur(cliquet)
    neutre = Simulateur(
        cliquet.avec(
            age_conversion_droits_acquis=AgeConversionDroitsAcquis.LIQUIDATION
        )
    )
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=64,
    )
    reference = simulateur.simuler(carriere).notionnel_prospectif
    liquidation = neutre.simuler(carriere).notionnel_prospectif

    assert reference.droits_acquis.age_conversion == pytest.approx(67.0)
    assert liquidation.droits_acquis.age_conversion == pytest.approx(64.0)
    # Un diviseur plus élevé à 64 ans qu'à 67 : le capital d'ouverture monte.
    assert liquidation.capital_droits_acquis > reference.capital_droits_acquis
    assert liquidation.pension_annuelle > reference.pension_annuelle
    # Les cotisations postérieures à la bascule, elles, ne bougent pas.
    assert liquidation.compte.capital == pytest.approx(reference.compte.capital)


def test_le_pot_des_droits_acquis_ne_depend_que_du_passe():
    """La raison pour laquelle l'action 24 a été abandonnée, tenue par un test.

    Les droits d'avant la bascule sont une pension annuelle ; la convertir en
    capital demande un âge. Sous le défaut ``REFERENCE``, cet âge ne dépend pas
    de l'assuré : un même passé constitue donc le MÊME pot, qu'on parte à 60 ans
    ou à 67. Sous ``LIQUIDATION``, l'âge est celui du départ, et le pot enfle
    quand on part tôt — 28 % d'écart pour un passé identique, ce qu'aucune
    différence de carrière ne justifie.

    La conséquence est l'incitation, et c'est elle qui a tranché : le pot
    rétrécissant avec l'âge à peu près au rythme où les cotisations nouvelles le
    remplissent, les deux s'annulent, et sept années de travail de plus ne font
    presque plus monter le capital. Les bornes ci-dessous sont larges exprès —
    c'est un ORDRE DE GRANDEUR qu'on tient, pas un instantané, et un test qui
    fige un chiffre au centime finit par être relâché plutôt que lu.
    """
    reference = Simulateur(Parametres())
    liquidation = Simulateur(Parametres().avec(
        age_conversion_droits_acquis=AgeConversionDroitsAcquis.LIQUIDATION))

    def mesure(sim, age):
        carriere = sim.carriere_simple(
            annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=21, age_liquidation=age,
        )
        resultat = sim.simuler(carriere).notionnel_prospectif
        return resultat.droits_acquis.capital_a_la_bascule, resultat.capital_notionnel

    pots_reference = [mesure(reference, age)[0] for age in (60, 62, 64, 67)]
    pots_liquidation = [mesure(liquidation, age)[0] for age in (60, 62, 64, 67)]

    # Le passé est le même dans les quatre cas : seul l'âge de départ change.
    assert pots_reference[0] == pytest.approx(pots_reference[-1])
    assert all(p == pytest.approx(pots_reference[0]) for p in pots_reference)

    # Sous l'autre convention, il enfle quand on part tôt, et strictement.
    assert all(a > b for a, b in zip(pots_liquidation, pots_liquidation[1:]))
    assert pots_liquidation[0] / pots_liquidation[-1] > 1.20

    # Et c'est ce qui annule l'incitation à travailler plus longtemps.
    capital_reference = [mesure(reference, age)[1] for age in (60, 67)]
    capital_liquidation = [mesure(liquidation, age)[1] for age in (60, 67)]
    gain_reference = capital_reference[1] / capital_reference[0] - 1.0
    gain_liquidation = capital_liquidation[1] / capital_liquidation[0] - 1.0
    assert gain_reference > 0.20, gain_reference
    assert gain_liquidation < 0.05, gain_liquidation


def test_la_cascade_des_droits_acquis_reconstitue_le_capital(simulateur):
    """Les étapes publiées doivent redonner le capital, sinon elles mentent."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=64,
    )
    prospectif = simulateur.simuler(carriere).notionnel_prospectif
    acquis = prospectif.droits_acquis

    assert acquis.capital_a_la_bascule == pytest.approx(
        acquis.pension_figee * acquis.diviseur
    )
    assert acquis.capital == pytest.approx(
        acquis.capital_a_la_bascule * acquis.coefficient_revalorisation
    )
    assert prospectif.capital_notionnel == pytest.approx(
        acquis.capital + prospectif.compte.capital
    )
    assert prospectif.pension_annuelle == pytest.approx(
        prospectif.capital_notionnel / prospectif.conversion.diviseur
    )


def test_sans_carriere_avant_la_bascule_il_n_y_a_aucun_droit_acquis(simulateur):
    """Une carrière entièrement postérieure à 2026 n'a rien à convertir."""
    carriere = simulateur.carriere_simple(
        annee_naissance=2010, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64,
    )
    prospectif = simulateur.simuler(carriere).notionnel_prospectif
    assert prospectif.droits_acquis is None
    assert prospectif.capital_droits_acquis == 0.0


def test_une_carriere_sans_aucune_cotisation_ne_produit_pas_de_capital(simulateur):
    """Des droits acquis existent formellement, mais ils valent zéro.

    Le cas est réel — une carrière intégralement interrompue — et la page de
    simulation doit le traverser sans diviser par le capital.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=21, age_liquidation=64,
        interruptions={annee: "sans_activite" for annee in range(1996, 2039)},
    )
    prospectif = simulateur.simuler(carriere).notionnel_prospectif
    assert prospectif.droits_acquis is not None
    assert prospectif.capital_notionnel == 0.0
    assert prospectif.pension_annuelle == 0.0


def test_le_motif_de_l_interruption_change_les_droits_ouverts(simulateur):
    """Chômage indemnisé et non indemnisé n'ouvrent pas les mêmes droits.

    Pendant un chômage indemnisé, l'UNEDIC verse de vraies cotisations aux
    régimes complémentaires : des points sont acquis. Le régime de base, lui,
    ne reçoit rien — la période y est seulement assimilée. Le modèle
    enregistrait le motif sans jamais le lire, et traitait les deux à
    l'identique.
    """
    commun = dict(annee_naissance=1975, sexe="F",
                  affiliation="salarie_prive_non_cadre",
                  age_debut=22, age_liquidation=64)
    resultats = {}
    for motif in ("chomage_indemnise", "chomage_non_indemnise", "sans_activite"):
        carriere = simulateur.carriere_simple(
            **commun,
            interruptions={annee: motif for annee in range(2000, 2005)},
        )
        resultats[motif] = simulateur.simuler(carriere)

    def complementaires(comparaison):
        return sum(p.montant for p in comparaison.actuel.pensions_par_regime
                   if p.type_calcul == "points")

    # Le chômage indemnisé préserve les points complémentaires, pas les autres.
    assert complementaires(resultats["chomage_indemnise"]) > complementaires(
        resultats["chomage_non_indemnise"]
    )
    # Et il alimente le compte notionnel, puisque des cotisations sont versées.
    assert (resultats["chomage_indemnise"].notionnel_retroactif.capital_notionnel
            > resultats["chomage_non_indemnise"].notionnel_retroactif.capital_notionnel)
    # « sans_activite » ne valide même pas de trimestre assimilé.
    assert (resultats["sans_activite"].actuel.trimestres_valides
            < resultats["chomage_non_indemnise"].actuel.trimestres_valides)


def test_un_temps_tres_partiel_ne_valide_pas_quatre_trimestres(simulateur):
    """Un trimestre s'acquiert par un montant cotisé, pas par le temps.

    150 fois le SMIC horaire depuis 2014, 200 avant. Le modèle validait quatre
    trimestres par année travaillée quelle que soit la rémunération.
    """
    trimestres = {}
    for niveau in (0.10, 0.20, 1.0):
        carriere = simulateur.carriere_simple(
            annee_naissance=1975, sexe="F",
            affiliation="salarie_prive_non_cadre", age_debut=22,
            age_liquidation=64, niveau_salaire=niveau, profil_carriere="plat",
        )
        trimestres[niveau] = carriere.trimestres_actuels
    assert trimestres[0.10] < trimestres[0.20] < trimestres[1.0]
    # Une carrière au salaire moyen valide bien quatre trimestres par an.
    assert trimestres[1.0] == 4 * 42


def test_un_depart_plus_tardif_ameliore_la_pension_notionnelle(simulateur):
    """Double effet : plus de cotisations, et un diviseur plus faible."""
    pensions = []
    for age in (60, 62, 64, 67):
        carriere = simulateur.carriere_simple(
            annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=22, age_liquidation=age,
        )
        pensions.append(
            simulateur.simuler(carriere).notionnel_retroactif.pension_annuelle
        )
    assert pensions == sorted(pensions)


def test_carriere_interrompue_perd_davantage_en_notionnel(simulateur):
    """Les périodes non cotisées n'ouvrent aucun droit : c'est le principe."""
    commun = dict(annee_naissance=1975, sexe="F",
                  affiliation="salarie_prive_non_cadre", age_debut=22,
                  age_liquidation=64)
    complete = simulateur.simuler(simulateur.carriere_simple(**commun))
    interrompue = simulateur.simuler(simulateur.carriere_simple(
        **commun, interruptions={annee: "education_enfant" for annee in range(2005, 2013)}
    ))
    assert (interrompue.notionnel_retroactif.pension_annuelle
            < complete.notionnel_retroactif.pension_annuelle)


def test_regime_special_a_depart_precoce_est_le_plus_touche(simulateur):
    """Le cas emblématique : quinze ans d'anticipation."""
    sncf = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1955, sexe="H", affiliation="agent_sncf",
        age_debut=20, age_liquidation=50,
    ))
    prive = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1955, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=62,
    ))
    assert sncf.notionnel_retroactif.ecart_age.ecart == pytest.approx(15.0)
    assert (sncf.variation("notionnel_retroactif")
            < prive.variation("notionnel_retroactif"))


def test_sans_cotisation_aucun_droit_notionnel(simulateur):
    """Suppression des minima : peu cotisé, peu de retraite, sans plancher."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64, niveau_salaire=0.3,
    )
    riche = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64, niveau_salaire=3.0,
    )
    faible = simulateur.simuler(carriere).notionnel_retroactif.pension_annuelle
    forte = simulateur.simuler(riche).notionnel_retroactif.pension_annuelle
    # Strictement proportionnel au salaire tant que le plafond n'est pas atteint :
    # aucun effet de seuil ne subsiste.
    assert forte > faible * 5


def test_capitalisation_reste_dans_un_compartiment_separe(simulateur):
    """Les droits RAFP ne rejoignent jamais le capital notionnel."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1980, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=25, age_liquidation=64, part_primes=0.20,
    )
    resultat = simulateur.simuler(carriere).notionnel_retroactif
    assert resultat.capital_capitalisation > 0
    assert resultat.rente_capitalisation_annuelle > 0
    assert resultat.rente_capitalisation_annuelle not in (resultat.pension_annuelle,)


# -- neutralisations ---------------------------------------------------------


def test_les_avantages_familiaux_ne_jouent_que_dans_le_systeme_actuel(simulateur):
    commun = dict(annee_naissance=1975, sexe="F",
                  affiliation="salarie_prive_non_cadre",
                  age_debut=22, age_liquidation=64)
    sans = simulateur.simuler(simulateur.carriere_simple(**commun, nombre_enfants=0))
    avec = simulateur.simuler(simulateur.carriere_simple(**commun, nombre_enfants=3))
    assert (avec.notionnel_retroactif.pension_annuelle
            == pytest.approx(sans.notionnel_retroactif.pension_annuelle))


def test_le_systeme_actuel_applique_ses_avantages_sans_condition(simulateur):
    """Le scénario 1 est le droit positif : ses minima s'appliquent toujours.

    Les drapeaux :class:`Neutralisations` décrivent ce que les scénarios
    notionnels RETIRENT. Les lire dans le scénario 1 amputait l'étalon de la
    majoration pour trois enfants, de la MDA et du minimum contributif —
    c'est-à-dire précisément de ce qui protège les carrières que le notionnel
    pénalise le plus, ce qui minorait l'écart mesuré.
    """
    commun = dict(annee_naissance=1975, sexe="F",
                  affiliation="salarie_prive_non_cadre",
                  age_debut=22, age_liquidation=64)
    sans = simulateur.simuler(
        simulateur.carriere_simple(**commun, nombre_enfants=0)
    ).actuel
    avec = simulateur.simuler(
        simulateur.carriere_simple(**commun, nombre_enfants=3)
    ).actuel

    # Majoration de 10 % pour trois enfants, et huit trimestres par enfant.
    assert avec.trimestres_valides == sans.trimestres_valides + 24
    assert avec.pension_annuelle > sans.pension_annuelle * 1.09

    # Les neutralisations ne doivent rien y changer : elles ne concernent que
    # les scénarios notionnels.
    neutralise = Simulateur(
        Parametres(neutralisations=Neutralisations(majoration_enfants=False))
    )
    autre = neutralise.simuler(
        neutralise.carriere_simple(**commun, nombre_enfants=3)
    ).actuel
    assert autre.pension_annuelle == pytest.approx(avec.pension_annuelle)


def test_a_salaire_egal_le_statut_est_compare_a_la_meme_grandeur(simulateur):
    """Un compte notionnel ne connaît que des euros cotisés.

    Les fiches publiques ne portent que la retenue de l'agent, les fiches
    privées le total salarié + employeur. Les comparer telles quelles faisait
    apparaître entre un fonctionnaire et un salarié de même rémunération un
    écart de 37 % qui ne traduisait aucune règle de retraite, mais un périmètre
    comptable.

    La `part_salariale` des fiches referme cet écart de périmètre : les deux
    scénarios comparent maintenant la même grandeur des deux côtés. Ce qui reste
    est réel — les taux salariaux ne sont pas identiques d'un régime à l'autre —
    et se compte en points, non en dizaines de points.
    """
    # Le profil est NOMMÉ, et plat : ce test isole le périmètre de cotisation,
    # ce qui suppose la même trajectoire de salaire des deux côtés. Le défaut la
    # choisit sur l'affiliation — profil de l'État contre profil des employés du
    # privé —, et comparerait alors deux carrières au lieu de deux barèmes.
    commun = dict(annee_naissance=1975, sexe="H", age_debut=22, age_liquidation=64,
                  profil_carriere="plat")

    def pension(affiliation, scenario):
        carriere = simulateur.carriere_simple(affiliation=affiliation, **commun)
        return getattr(simulateur.simuler(carriere), scenario).pension_annuelle

    public = pension("fonctionnaire_etat", "notionnel_retroactif")
    prive = pension("salarie_prive_non_cadre", "notionnel_retroactif")
    # Quelques points d'écart, là où le périmètre comptable en faisait 37.
    assert 0.90 < public / prive < 1.10


def test_l_ancienne_convention_egalise_les_statuts(simulateur):
    """`TOTALE_ALIGNEE` prête au public le taux du privé : les deux se rejoignent."""
    aligne = Simulateur(Parametres().avec(
        part_cotisation=PartCotisation.TOTALE_ALIGNEE
    ))
    # Profil nommé, et plat : ce que ce test veut voir se rejoindre est le
    # TAUX, et deux profils différents feraient diverger les deux carrières
    # avant même qu'on prélève.
    commun = dict(annee_naissance=1975, sexe="H", age_debut=22, age_liquidation=64,
                  profil_carriere="plat")
    pensions = [
        aligne.simuler(
            aligne.carriere_simple(affiliation=affiliation, **commun)
        ).notionnel_retroactif.pension_annuelle
        for affiliation in ("salarie_prive_non_cadre", "fonctionnaire_etat")
    ]
    assert pensions[1] == pytest.approx(pensions[0], rel=1e-9)


def test_l_ancienne_convention_d_alignement_reste_accessible():
    """`TOTALE_ALIGNEE` prête au public la part employeur du privé.

    C'est ce que le modèle faisait par défaut avant que la répartition
    salarié/employeur soit dans les fiches. Conservée comme contrefactuel, elle
    doit rester entre la part salariale seule et la contribution publique
    réelle, qui est bien plus lourde.
    """
    profil = dict(annee_naissance=1975, sexe="H", affiliation="fonctionnaire_etat",
                  age_debut=22, age_liquidation=64)

    def pension(part):
        sim = Simulateur(Parametres().avec(part_cotisation=part))
        return sim.simuler(
            sim.carriere_simple(**profil)
        ).notionnel_retroactif.pension_annuelle

    salariale = pension(PartCotisation.SALARIALE)
    alignee = pension(PartCotisation.TOTALE_ALIGNEE)
    totale = pension(PartCotisation.TOTALE)
    assert salariale < alignee < totale


# -- scénarios 4 et 5 : les cotisations employeur du public -------------------


def test_les_six_scenarios_sont_calcules(simulateur, salarie_moyen):
    comparaison = simulateur.simuler(salarie_moyen)
    for cle, _, _ in SCENARIOS_NOTIONNELS:
        assert getattr(comparaison, cle).pension_annuelle > 0, cle


def test_sans_employeur_les_quatre_scenarios_se_reduisent_a_deux(simulateur):
    """Un artisan paie tout : il n'y a pas de part patronale à ajouter.

    Un non-salarié relève pourtant souvent d'un régime partagé avec des
    salariés — un artisan cotise au régime général, dont la fiche porte la
    répartition 41/59 d'un salarié. Sans le drapeau `sans_employeur` du statut,
    les scénarios 4 et 5 lui prêteraient un employeur qu'il n'a pas.
    """
    for affiliation in ("artisan", "profession_liberale", "exploitant_agricole"):
        carriere = simulateur.carriere_simple(
            annee_naissance=1975, sexe="H", affiliation=affiliation,
            age_debut=27, age_liquidation=64,
        )
        comparaison = simulateur.simuler(carriere)
        assert (comparaison.notionnel_retroactif_employeur.pension_annuelle
                == pytest.approx(comparaison.notionnel_retroactif.pension_annuelle)), affiliation
        assert (comparaison.notionnel_prospectif_employeur.pension_annuelle
                == pytest.approx(comparaison.notionnel_prospectif.pension_annuelle)), affiliation
        assert not comparaison.contribution_employeur.a_un_employeur, affiliation


def test_le_prive_aussi_a_une_part_patronale(simulateur, salarie_moyen):
    """L'axe n'est pas public/privé : il est salarial/patronal, pour tous.

    La fiche du régime général porte le total ; sa `part_salariale` dit combien
    l'employeur y met. Les scénarios 4 et 5 doivent donc déplacer un salarié du
    privé, et pas seulement un fonctionnaire.
    """
    comparaison = simulateur.simuler(salarie_moyen)
    assert (comparaison.notionnel_retroactif_employeur.pension_annuelle
            > comparaison.notionnel_retroactif.pension_annuelle * 1.5)
    employeur = comparaison.contribution_employeur
    assert employeur.a_un_employeur
    # Aucune série publique n'intervient : la fiche porte la répartition.
    assert not employeur.concerne_un_regime_public
    assert 0.5 < employeur.part < 0.65


def test_le_scenario_4_est_le_2_avec_les_cotisations_employeur(simulateur):
    """82 % de contribution employeur portés au compte, cela se voit."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.20,
    )
    comparaison = simulateur.simuler(carriere)
    assert (comparaison.notionnel_retroactif_employeur.pension_annuelle
            > comparaison.notionnel_retroactif.pension_annuelle * 1.5)


def test_le_scenario_5_est_le_3_avec_les_cotisations_employeur(simulateur):
    """Les droits acquis sont ceux du scénario 3 ; seul le flux postérieur change.

    Le régime unique applique après la bascule un taux unique qui efface toute
    trace de l'employeur public : sans le traitement du taux unifié, ce scénario
    serait rigoureusement identique au scénario 3, et ne servirait à rien.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1990, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.20,
    )
    comparaison = simulateur.simuler(carriere)
    prospectif = comparaison.notionnel_prospectif
    avec_employeur = comparaison.notionnel_prospectif_employeur

    assert avec_employeur.pension_annuelle > prospectif.pension_annuelle * 1.2
    # Les droits figés à la bascule, eux, sont les mêmes des deux côtés.
    assert (avec_employeur.droits_acquis.capital
            == pytest.approx(prospectif.droits_acquis.capital))


def test_le_scenario_5_reste_inferieur_au_scenario_4(simulateur):
    """Le 5 ne compte l'employeur qu'à partir de la bascule, le 4 depuis 1995."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.20,
    )
    comparaison = simulateur.simuler(carriere)
    assert (comparaison.notionnel_prospectif_employeur.pension_annuelle
            < comparaison.notionnel_retroactif_employeur.pension_annuelle)


def test_le_regime_unique_herite_de_la_repartition_de_ses_pivots(simulateur):
    """Après la bascule, plus de fonction publique : un seul régime, un seul taux.

    Son taux est celui du statut pivot privé, et il en hérite la répartition.
    C'est elle, et non une contribution publique retrouvée décret par décret,
    qui sépare le scénario 5 du scénario 3 après la bascule.
    """
    fusionne = simulateur.regime_fusionne
    carriere = simulateur.carriere_simple(
        annee_naissance=1990, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.25,
    )
    comparaison = simulateur.simuler(carriere)

    salariale = next(c for c in comparaison.notionnel_prospectif.compte.cotisations
                     if c.annee == 2030)
    totale = next(c for c in comparaison.notionnel_prospectif_employeur.compte.cotisations
                  if c.annee == 2030)
    assert salariale.taux_effectif == pytest.approx(fusionne.taux_cotisation_salarie)
    assert totale.taux_effectif == pytest.approx(fusionne.taux_cotisation_retraite)
    assert totale.taux_effectif > salariale.taux_effectif


def test_le_repli_est_compte_quand_aucune_serie_n_existe(simulateur):
    """Aucun taux employeur SNCF avant 1992 : le modèle estime, et il le dit.

    La part patronale est alors celle d'un salarié du privé de la même année.
    C'est une estimation, pas une somme retrouvée : elle est comptée comme telle
    dans le décompte des années, et la fiabilité du scénario retombe.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1940, sexe="H", affiliation="agent_sncf",
        age_debut=20, age_liquidation=50,
    )
    comparaison = simulateur.simuler(carriere)
    employeur = comparaison.contribution_employeur
    assert set(employeur.annees_par_origine) == {"repli"}
    assert employeur.annees_trouvees == 0
    assert employeur.a_un_employeur
    assert (comparaison.notionnel_retroactif_employeur.fiabilite
            < comparaison.notionnel_retroactif.fiabilite)


def test_une_carriere_sncf_a_cheval_sur_1992_melange_les_deux(simulateur):
    """Le II de l'article 8 du décret de 1991 coupe cette carrière en deux.

    Elle était entièrement en repli tant que le dépôt n'avait pas lu ce texte.
    La moitié qui l'a quitté vaut 28,44 % de contribution employeur là où le
    repli lui prêtait l'effort d'un salarié du privé.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1955, sexe="H", affiliation="agent_sncf",
        age_debut=20, age_liquidation=50,
    )
    employeur = simulateur.simuler(carriere).contribution_employeur
    assert set(employeur.annees_par_origine) == {"repli", "appelee"}
    # 1975-1991 estimées, 1992-2004 lues dans le décret.
    assert employeur.annees_par_origine["repli"] == 17
    assert employeur.annees_trouvees == 13


def test_la_part_employeur_est_decomposee(simulateur):
    """Agent + employeur = total, et l'employeur pèse le plus lourd."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.20,
    )
    employeur = simulateur.simuler(carriere).contribution_employeur
    assert employeur.concerne_un_regime_public
    assert employeur.agent + employeur.employeur == pytest.approx(employeur.total)
    assert 0.7 < employeur.part < 0.95
    # Carrière 1998-2038 : taux implicite jusqu'en 2005, appelé ensuite.
    assert set(employeur.annees_par_origine) == {"implicite", "appelee"}
    assert employeur.annees_par_origine["implicite"] == 8
    assert employeur.annees_repli == 0


def test_les_scenarios_4_et_5_ne_qualifient_pas_la_fiabilite_d_ensemble(simulateur):
    """Un repli du scénario 4 ne doit pas dégrader l'étalon ni le scénario 2."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1955, sexe="H", affiliation="agent_sncf",
        age_debut=20, age_liquidation=50,
    )
    comparaison = simulateur.simuler(carriere)
    assert comparaison.fiabilite == min(
        comparaison.actuel.fiabilite,
        comparaison.notionnel_retroactif.fiabilite,
        comparaison.notionnel_prospectif.fiabilite,
    )
    assert (comparaison.notionnel_retroactif_employeur.fiabilite
            <= comparaison.notionnel_retroactif.fiabilite)


# -- scénario 6 : la proposition libérale --------------------------------------


def _carriere_modeste(simulateur, age_liquidation: float, **kwargs) -> Carriere:
    """Un demi-salaire moyen, entré à 21 ans : sous le plancher à coup sûr."""
    return simulateur.carriere_simple(
        annee_naissance=1960, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=21, age_liquidation=age_liquidation, niveau_salaire=0.5,
        **kwargs,
    )


def test_le_scenario_6_preleve_18_pour_cent_pour_tous_a_compter_de_la_bascule(simulateur):
    """Les taux réels avant la bascule, 18 % pour tous à compter d'elle.

    Une personne née en 1975 a cotisé sous le système actuel de 1996 à 2025 :
    ces années sont portées au compte telles qu'elles ont été prélevées, à
    l'euro près celles du scénario 4. De 2026 à son départ, un seul taux,
    salariale et patronale confondues, prélevé une fois sur la rémunération —
    le même pour le salarié et pour le fonctionnaire.
    """
    bascule = simulateur.parametres.annee_bascule
    for affiliation in ("salarie_prive_non_cadre", "fonctionnaire_etat"):
        comparaison = simulateur.simuler(simulateur.carriere_simple(
            annee_naissance=1975, sexe="F", affiliation=affiliation,
            age_debut=21, age_liquidation=64, niveau_salaire=0.5,
        ))
        liberal = {c.annee: c for c in comparaison.notionnel_liberal.compte.cotisations}
        quatre = {c.annee: c for c in
                  comparaison.notionnel_retroactif_employeur.compte.cotisations}
        assert set(liberal) == set(quatre)
        avant = [a for a in liberal if a < bascule and not liberal[a].nulle]
        apres = [a for a in liberal if a >= bascule and not liberal[a].nulle]
        assert avant and apres, affiliation
        for annee in avant:
            assert liberal[annee].cotisation == pytest.approx(quatre[annee].cotisation), (
                affiliation, annee)
        for annee in apres:
            assert liberal[annee].taux_effectif == pytest.approx(0.18), (affiliation, annee)
            assert liberal[annee].cotisation == pytest.approx(
                0.18 * liberal[annee].assiette_retenue)


def test_avant_la_bascule_le_scenario_6_est_le_scenario_4(simulateur):
    """Qui a liquidé avant la bascule n'a aucune année à 18 % : son compte est
    exactement celui du scénario 4, et seule la garantie peut l'en séparer."""
    comparaison = simulateur.simuler(_carriere_modeste(simulateur, 62))
    assert comparaison.carriere.annee_liquidation < simulateur.parametres.annee_bascule
    liberal = comparaison.notionnel_liberal
    employeur = comparaison.notionnel_retroactif_employeur
    assert liberal.capital_notionnel == pytest.approx(employeur.capital_notionnel)
    assert liberal.conversion.diviseur == employeur.conversion.diviseur
    assert liberal.ecart_age == employeur.ecart_age
    assert liberal.garantie_vieillesse is not None
    assert liberal.garantie_vieillesse.pension_contributive == pytest.approx(
        employeur.pension_annuelle
    )


def test_la_garantie_reproduit_le_tableau_de_la_proposition(simulateur):
    """Les cinq lignes du tableau de la proposition, en euros de 2026.

    300 € et 300 € → 1 000 € ; 300 € et 1 500 € → 500 € ; 900 € et 900 € →
    0 € ; 300 € et 5 000 € → 500 € ; une personne seule à 300 € → 750 €. La
    garantie étant individualisée, un couple est deux personnes calculées
    séparément, chacune contre le plancher de 800 €.
    """
    carriere = _carriere_modeste(simulateur, 66)   # liquide en 2026 : coefficient 1
    assert carriere.annee_liquidation == 2026

    def aide(simulateur_, pension_mensuelle: float) -> float:
        garantie = simulateur_.scenario_liberal._garantie_vieillesse(
            carriere, pension_mensuelle * 12.0
        )
        assert garantie.coefficient_prix == pytest.approx(1.0)
        return garantie.complement / 12.0

    en_couple = Simulateur(Parametres(situation_foyer=SituationFoyer.COUPLE))
    assert aide(en_couple, 300) + aide(en_couple, 300) == pytest.approx(1000)
    assert aide(en_couple, 300) + aide(en_couple, 1500) == pytest.approx(500)
    assert aide(en_couple, 900) + aide(en_couple, 900) == pytest.approx(0)
    assert aide(en_couple, 300) + aide(en_couple, 5000) == pytest.approx(500)
    assert aide(simulateur, 300) == pytest.approx(750)


def test_la_garantie_n_est_servie_qu_a_partir_de_65_ans(simulateur):
    """Avant 65 ans on ne touche rien ; à 65 ans on touche, même parti plus tôt.

    C'est la règle de l'ASPA qu'elle remplace, et le modèle la sert désormais
    en entier : qui liquide à 62 ans perçoit sa seule pension contributive
    pendant trois ans, puis la garantie s'ouvre. Le complément est donc
    CALCULÉ dans les deux cas — il est dû —, et il n'entre dans la pension
    affichée que lorsqu'il est dû dès le départ.
    """
    avant = simulateur.simuler(_carriere_modeste(simulateur, 62)).notionnel_liberal
    garantie_avant = avant.garantie_vieillesse
    assert not garantie_avant.age_atteint
    assert not garantie_avant.servie_a_la_liquidation
    assert garantie_avant.differee and garantie_avant.servie
    assert garantie_avant.complement > 0.0
    # La pension affichée reste la contributive : à 62 ans, rien de plus.
    assert avant.pension_annuelle == pytest.approx(garantie_avant.pension_contributive)
    # Et l'ouverture est datée : l'année des 65 ans, pas celle du départ.
    assert garantie_avant.annee_ouverture == (
        simulateur.simuler(_carriere_modeste(simulateur, 62)).carriere.annee_naissance + 65
    )

    apres = simulateur.simuler(_carriere_modeste(simulateur, 65)).notionnel_liberal
    garantie = apres.garantie_vieillesse
    assert garantie.age_atteint and garantie.servie_a_la_liquidation
    assert not garantie.differee
    assert apres.pension_annuelle == pytest.approx(garantie.plancher_annuel)
    assert apres.pension_annuelle == pytest.approx(
        garantie.pension_contributive + garantie.complement
    )


def test_la_garantie_regarde_les_deux_etages_obligatoires(simulateur):
    """18 % de répartition et 5 % capitalisés : le plancher voit les deux.

    Une allocation différentielle compte les ressources, non leur origine. La
    rente du pilier obligatoire réduit donc le complément, euro pour euro,
    dès qu'elle existe — c'est-à-dire pour les carrières qui cotisent après la
    bascule.
    """
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1975, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=30, age_liquidation=67, niveau_salaire=0.45,
    ))
    liberal = comparaison.notionnel_liberal
    garantie = liberal.garantie_vieillesse
    assert liberal.capitalisation is not None
    assert garantie.rente_capitalisee == pytest.approx(
        liberal.capitalisation.rente_annuelle)
    assert garantie.rente_capitalisee > 0.0
    assert garantie.ressources == pytest.approx(
        garantie.pension_contributive + garantie.rente_capitalisee)
    if garantie.servie:
        assert garantie.complement == pytest.approx(
            garantie.plancher_annuel - garantie.ressources)
        # Sans le pilier, le complément aurait été plus gros d'autant.
        assert garantie.complement < garantie.plancher_annuel - garantie.pension_contributive


def test_le_plancher_suit_les_prix_depuis_2026(simulateur):
    """800 € et 250 € sont des euros de 2026 : une liquidation de 2025 les
    déflate par l'indice des prix, exactement comme l'ASPA entre deux ancres."""
    comparaison = simulateur.simuler(_carriere_modeste(simulateur, 65))
    garantie = comparaison.notionnel_liberal.garantie_vieillesse
    assert comparaison.carriere.annee_liquidation == 2025
    coefficient = simulateur.macro.coefficient_prix(2026, 2025)
    assert garantie.coefficient_prix == pytest.approx(coefficient)
    assert garantie.base_annuelle == pytest.approx(800 * 12 * coefficient)
    assert garantie.isolement_annuel == pytest.approx(250 * 12 * coefficient)


def test_une_grosse_pension_ne_recoit_aucune_garantie(simulateur):
    """Différentielle : au-dessus du plancher, rien — et le scénario 6 est un
    compte notionnel à taux unique, sans plus."""
    comparaison = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=23, age_liquidation=65, niveau_salaire=2.5,
    ))
    garantie = comparaison.notionnel_liberal.garantie_vieillesse
    assert garantie.age_atteint and not garantie.servie
    assert garantie.pension_contributive > garantie.plancher_annuel


# -- taux d'acquisition commun (paramètre, pas scénario) ----------------------


def test_le_taux_uniforme_ne_compte_pas_deux_fois_la_meme_tranche():
    """Régime général et Arrco découpent la même première tranche.

    Sous un taux unique, les additionner prélèverait deux fois sur les mêmes
    euros. Le compte d'un cadre ne doit donc pas dépasser ce que le taux
    prélève sur sa rémunération plafonnée.
    """
    simulateur = Simulateur(Parametres().avec(
        source_cotisations=SourceCotisations.TAUX_UNIFORME
    ))
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=23, age_liquidation=64,
    )
    compte = simulateur.simuler(carriere).notionnel_retroactif.compte
    taux = simulateur.parametres.taux_cotisation_uniforme
    for cotisation in compte.cotisations:
        if cotisation.nulle:
            continue
        assert cotisation.cotisation <= cotisation.revenu * taux + 1e-6, cotisation.annee


def test_le_taux_uniforme_est_bien_le_taux_retenu():
    """Un salarié non cadre sous le plafond doit voir exactement le taux choisi."""
    simulateur = Simulateur(Parametres().avec(
        source_cotisations=SourceCotisations.TAUX_UNIFORME,
        taux_cotisation_uniforme=0.20,
    ))
    carriere = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=23, age_liquidation=64, niveau_salaire=0.9,
    )
    compte = simulateur.simuler(carriere).notionnel_retroactif.compte
    annee = next(c for c in compte.cotisations if c.annee == 2010)
    assert annee.cotisation == pytest.approx(annee.revenu * 0.20)


def test_le_compartiment_de_capitalisation_garde_ses_taux():
    """Le RAFP n'est pas un compte notionnel : le taux unique ne s'y applique pas."""
    reference = Simulateur(Parametres())
    uniforme = Simulateur(Parametres().avec(
        source_cotisations=SourceCotisations.TAUX_UNIFORME
    ))
    profil = dict(
        annee_naissance=1975, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.20,
    )
    attendu = reference.simuler(
        reference.carriere_simple(**profil)
    ).notionnel_retroactif.capital_capitalisation
    obtenu = uniforme.simuler(
        uniforme.carriere_simple(**profil)
    ).notionnel_retroactif.capital_capitalisation
    assert obtenu == pytest.approx(attendu)


def test_la_cascade_des_avantages_est_exactement_additive(simulateur):
    """Sous-total contributif + avantages = pension. Sinon la page ment."""
    for enfants, salaire, debut in ((0, 1.0, 22), (1, 1.0, 22), (3, 2.0, 22),
                                    (3, 0.4, 37), (4, 0.8, 25)):
        carriere = simulateur.carriere_simple(
            annee_naissance=1965, sexe="F",
            affiliation="salarie_prive_non_cadre", age_debut=debut,
            age_liquidation=62, niveau_salaire=salaire, nombre_enfants=enfants,
            profil_carriere="plat",
        )
        actuel = simulateur.simuler(carriere).actuel
        somme = actuel.total_contributif + sum(
            a.montant for a in actuel.avantages_appliques
        )
        assert somme == pytest.approx(actuel.pension_annuelle), (
            f"cascade non additive pour {enfants} enfants, salaire {salaire}"
        )


def test_sans_enfant_aucun_avantage_familial_n_est_cite(simulateur):
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=62,
    )
    actuel = simulateur.simuler(carriere).actuel
    codes = {a.code for a in actuel.avantages_appliques}
    assert "majoration_enfants" not in codes
    assert "majoration_duree_assurance" not in codes
    assert actuel.total_contributif == pytest.approx(actuel.pension_annuelle)


def test_la_fonction_publique_majore_de_cinq_points_par_enfant_au_dela_de_trois():
    """10 % à trois enfants, puis 5 % par enfant supplémentaire."""
    simulateur = Simulateur(Parametres())
    montants = {}
    for enfants in (3, 5):
        carriere = simulateur.carriere_simple(
            annee_naissance=1965, sexe="F", affiliation="fonctionnaire_etat",
            age_debut=22, age_liquidation=62, nombre_enfants=enfants,
        )
        actuel = simulateur.simuler(carriere).actuel
        majoration = next(
            a for a in actuel.avantages_appliques if a.code == "majoration_enfants"
        )
        montants[enfants] = majoration.montant / actuel.total_contributif
    # 20 % à cinq enfants contre 10 % à trois : le rapport doit valoir 2.
    assert montants[5] / montants[3] == pytest.approx(2.0, rel=0.02)


def test_la_surcote_suit_l_age_legal_de_la_generation():
    """Né en 1968, l'âge légal est 64 : partir à 64 ans ne surcote pas.

    Né en 1958, il est de 62 : les deux dernières années surcotent. Lire l'âge
    à l'année de liquidation donnait 64 ans à tout le monde depuis 2023.
    """
    simulateur = Simulateur(Parametres())
    taux = {}
    for naissance in (1958, 1968):
        carriere = simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H",
            affiliation="salarie_prive_non_cadre", age_debut=18,
            age_liquidation=64,
        )
        taux[naissance] = simulateur.simuler(carriere).actuel.taux_liquidation
    assert taux[1958] > 0.50  # surcote de huit trimestres
    assert taux[1968] == pytest.approx(0.50)  # aucun trimestre au-delà de l'âge légal


def test_le_minimum_contributif_est_ecrete_pour_les_grosses_pensions(simulateur):
    """Un cadre à carrière complète ne doit jamais toucher le minimum."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=22, age_liquidation=64, niveau_salaire=3.0,
    )
    assert simulateur.simuler(carriere).actuel.minimum_applique is False


def test_le_minimum_contributif_releve_les_petites_pensions(simulateur):
    """Une carrière courte au SMIC relève du minimum : c'est son objet.

    À condition d'être liquidée au taux plein : ici par l'âge, la génération
    1965 l'obtenant sans condition de durée à 67 ans.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=37, age_liquidation=67, niveau_salaire=0.4,
        profil_carriere="plat",
    )
    resultat = simulateur.simuler(carriere).actuel
    assert resultat.minimum_applique is True


def test_le_minimum_contributif_est_refuse_a_une_pension_decotee(simulateur):
    """L'article L. 351-10 réserve le minimum aux pensions au taux plein.

    La même carrière liquidée cinq ans plus tôt n'a ni la durée requise ni
    l'âge d'annulation de la décote : le droit ne la relève pas. Le modèle la
    relevait, et faisait ainsi garantir par le système actuel un départ que le
    droit sanctionne — sur le segment même où l'écart avec les comptes
    notionnels se mesure.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=37, age_liquidation=62, niveau_salaire=0.4,
        profil_carriere="plat",
    )
    resultat = simulateur.simuler(carriere).actuel
    assert resultat.trimestres_valides < resultat.trimestres_requis
    assert resultat.minimum_applique is False


def test_la_majoration_du_minimum_suit_la_seule_duree_cotisee(simulateur):
    """Deux durées proratisent le minimum, et ce ne sont pas les mêmes.

    Le montant de base suit la durée d'ASSURANCE acquise dans le régime, sa
    majoration la seule durée COTISÉE (D. 351-2-2). Deux carrières de même
    durée d'assurance, dont l'une est pour moitié du chômage indemnisé, ne
    reçoivent donc pas le même plancher.
    """
    commun = dict(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=42, age_liquidation=67, niveau_salaire=0.4,
        profil_carriere="plat",
    )
    entierement_cotisee = simulateur.simuler(
        simulateur.carriere_simple(**commun)
    ).actuel
    moitie_chomee = simulateur.simuler(simulateur.carriere_simple(
        interruptions={annee: "chomage_indemnise"
                       for annee in range(1965 + 42, 1965 + 54)},
        **commun,
    )).actuel

    # Même durée d'assurance — le chômage indemnisé valide ses trimestres.
    assert entierement_cotisee.trimestres_valides == moitie_chomee.trimestres_valides
    assert entierement_cotisee.minimum_applique
    assert moitie_chomee.minimum_applique
    minimum = {r.code: r.montant for r in entierement_cotisee.avantages_appliques}
    minimum_chome = {r.code: r.montant for r in moitie_chomee.avantages_appliques}
    assert (minimum["minimum_contributif"]
            > minimum_chome["minimum_contributif"])


# -- restitution -------------------------------------------------------------


def test_le_tableau_mentionne_l_ecart_d_age(simulateur, salarie_moyen):
    texte = simulateur.simuler(salarie_moyen).tableau()
    # La ligne ne nomme plus un mode : le dépôt en a quatre, et le défaut
    # n'est plus le cliquet.
    assert "Âge de référence :" in texte
    assert "anticipation" in texte


def test_dictionnaire_est_serialisable(simulateur, salarie_moyen):
    import json

    donnees = simulateur.simuler(salarie_moyen).dictionnaire()
    json.dumps(donnees, ensure_ascii=False)
    assert set(donnees["scenarios"]) == {
        "actuel", "notionnel_retroactif", "notionnel_prospectif",
        "notionnel_retroactif_employeur", "notionnel_prospectif_employeur",
        "notionnel_liberal",
    }
    # La garantie vieillesse n'existe que dans le scénario 6, et y est
    # toujours décrite, servie ou non.
    assert donnees["scenarios"]["notionnel_retroactif_employeur"]["garantie_vieillesse"] is None
    garantie = donnees["scenarios"]["notionnel_liberal"]["garantie_vieillesse"]
    assert garantie["situation"] == "seul"
    assert garantie["plancher_annuel"] == pytest.approx(
        garantie["base_annuelle"] + garantie["isolement_annuel"]
    )
    assert donnees["unite"]["euros_constants_de"] == 2026


def test_euros_constants_rendent_les_generations_comparables(simulateur):
    """Deux liquidations éloignées doivent être ramenées à la même unité."""
    ancienne = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1940, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=62,
    ))
    recente = simulateur.simuler(simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=62,
    ))
    assert ancienne.coefficient_euros_constants > 1.0   # euros de 2002 -> 2026
    assert recente.coefficient_euros_constants < 1.0    # euros de 2052 -> 2026


def test_l_ecart_entre_regles_d_indexation_croit_avec_l_anciennete_de_la_carriere():
    """L'effet du mélange réel/nominal se concentre sur les décennies inflationnistes.

    Pour une carrière liquidée dans les années 2010, l'essentiel du capital a
    été constitué après 1990, période où les deux règles se rejoignent : l'écart
    reste modeste. Pour une carrière des années 1950-1980, il devient massif.
    C'est pourquoi le choix de la règle pèse surtout sur le scénario rétroactif
    appliqué aux générations anciennes.
    """
    litteral = Simulateur(
        Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)
    )
    nominal = Simulateur(Parametres(
        mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE_NOMINAL
    ))

    def rapport(annee_naissance: int) -> float:
        commun = dict(annee_naissance=annee_naissance, sexe="H",
                      affiliation="salarie_prive_non_cadre",
                      age_debut=20, age_liquidation=62)
        a = litteral.simuler(litteral.carriere_simple(**commun))
        b = nominal.simuler(nominal.carriere_simple(**commun))
        return (b.notionnel_retroactif.pension_annuelle
                / a.notionnel_retroactif.pension_annuelle)

    ancienne = rapport(1925)   # carrière 1945-1986
    recente = rapport(1970)    # carrière 1990-2031
    assert ancienne > recente > 1.0


# -- régimes en points -------------------------------------------------------


def test_les_complementaires_sont_calculees_en_points(simulateur, salarie_moyen):
    """La retraite complémentaire ne passe plus par un rendement estimé.

    Depuis l'intégration des valeurs d'achat et de service du point, la pension
    Arrco est le produit de points réellement acquis par la valeur de service
    de l'année de liquidation. Le libellé le dit, et c'est ce libellé qui
    distingue les deux modes de calcul.
    """
    pensions = {p.regime: p for p in simulateur.simuler(salarie_moyen).actuel.pensions_par_regime}
    assert "arrco" in pensions
    assert "points × valeur de service" in pensions["arrco"].detail
    assert pensions["arrco"].montant > 0


def test_les_points_d_un_regime_fusionne_sont_convertis(simulateur):
    """Un régime fermé ne sert plus ses points : son successeur les sert.

    Et il les sert au coefficient que l'accord de fusion a fixé, non au rapport
    de deux valeurs de service prises où les séries s'arrêtent. L'accord national
    interprofessionnel du 17 novembre 2017 convertit les points Arrco UN POUR UN
    et les points Agirc au coefficient 0,347798289 — celui qui figure sur les
    relevés de carrière.

    Ce test opposait auparavant le rapport `arrco(2018) / agirc_arrco(2019)`,
    qui vaut 0,990 : la valeur du régime unifié y était prise au 31 décembre
    2019, après la revalorisation de novembre, quand la conversion s'opère au
    1er janvier. Un pour cent de moins sur tous les points d'avant 2019.
    """
    from retraite_notionnelle.scenarios.actuel import ValeursPoint

    valeurs = ValeursPoint(simulateur.parametres.racine_donnees)
    scenario = simulateur.scenario_actuel
    derniere_arrco = valeurs.derniere_annee_servie("arrco")
    assert derniere_arrco == 2018

    avant, _ = valeurs.service("arrco", derniere_arrco)
    apres, _ = scenario.valeur_du_point("arrco", 2022)
    assert apres > avant, "les points Arrco n'ont pas suivi la fusion de 2019"

    service_2022, _ = valeurs.service("agirc_arrco", 2022)
    assert apres == pytest.approx(service_2022), "un point Arrco vaut un point Agirc-Arrco"

    agirc, _ = scenario.valeur_du_point("agirc", 2022)
    assert agirc / service_2022 == pytest.approx(0.347798289, rel=1e-6)


def test_un_regime_ferme_ne_vaut_jamais_plus_que_son_successeur(simulateur):
    """Une conversion aux fusions préserve les droits : elle ne les multiplie pas.

    Ce test attrape d'un coup les trois défauts de la chaîne de succession, tous
    dus à une date de reprise mal choisie : le point UNIRS valorisé quinze fois
    trop cher pour toute liquidation postérieure à 1998, les points IPACTE et
    IGRANTE cinquante-quatre fois trop chers au-delà de 2022, et le pour cent
    perdu à la fusion de 2019 parce que la valeur du régime unifié était prise au
    31 décembre et non au 1er janvier.
    """
    scenario = simulateur.scenario_actuel
    chaines = (
        ("unirs", "arrco"), ("ipacte", "ircantec"), ("igrante", "ircantec"),
        ("agirc", "agirc_arrco"), ("arrco", "agirc_arrco"),
    )
    for code, successeur in chaines:
        reprise = scenario.conversions_points.fusion(code, successeur)
        assert reprise is not None, f"aucun coefficient déclaré : {code} -> {successeur}"
        assert 0 < reprise.coefficient <= 1.0, (code, reprise.coefficient)
        # La comparaison n'a de sens qu'à compter de la reprise : avant elle, le
        # successeur n'existe pas et sa « valeur » n'est qu'un repli sur les prix.
        for annee in range(reprise.annee_effet, 2061):
            valeur = scenario.valeur_du_point(code, annee)
            reference = scenario.valeur_du_point(successeur, annee)
            if valeur is None or reference is None:
                continue
            assert valeur[0] <= reference[0] * 1.001, (code, annee, valeur[0], reference[0])


def test_le_rendement_du_point_ne_saute_pas_d_une_annee_sur_l_autre(simulateur):
    """Cent euros cotisés une année ou la suivante donnent des pensions voisines.

    Une rupture signale un changement d'ÉCHELLE que le moteur n'a pas traité.
    C'était le cas de l'Arrco en 1999 : les valeurs d'avant sont celles de
    l'UNIRS, celles d'après celles du régime unifié, et le moteur accumulait des
    points dans la première unité pour les liquider dans la seconde. Cent euros
    cotisés en 1998 produisaient 30,31 € de pension annuelle, les mêmes cent
    euros de 1999 n'en produisaient que 11,15 — un facteur 2,7 en une année,
    pour une unification qui, par construction, ne changeait aucun droit.
    """
    scenario = simulateur.scenario_actuel
    liquidation = 2029
    # La borne est large à dessein : elle vise les changements d'UNITÉ, qui se
    # comptent en facteurs, et non les mouvements de barème, qui peuvent être
    # brusques sans être faux — le taux d'appel de l'Ircantec passe de 0,60 à
    # 0,80 en 1983, et c'est le droit.
    for code in ("arrco", "agirc", "ircantec"):
        valeur_service = scenario.valeur_du_point(code, liquidation)
        assert valeur_service is not None
        precedent = None
        for annee in range(1962, 2019):
            achat = scenario.valeurs_point.achat(code, annee)
            if achat is None:
                continue
            reference, appel, _ = achat
            echelle, _ = scenario.conversions_points.echelle(code, annee, liquidation)
            rendu = 100.0 / (appel * reference) * echelle * valeur_service[0]
            if precedent is not None:
                assert 0.5 < rendu / precedent < 2.0, (code, annee, precedent, rendu)
            precedent = rendu


def test_la_duree_de_proratisation_n_est_pas_la_duree_requise(simulateur):
    """Article R. 351-6 : deux durées, et elles ne montent pas ensemble.

    La loi du 22 juillet 1993 fait passer la durée REQUISE de 150 à 160
    trimestres pour les générations 1934-1943. Elle ne touche à la durée
    maximale prise en compte par la PRORATISATION que pour les générations
    1944-1948, et de deux trimestres par génération.

    Le modèle n'en avait qu'une, et divisait donc par 160 la carrière d'un
    assuré né en 1945 auquel le droit oppose 154.
    """
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["regime_general"].periode(2010)
    assert periode.duree_requise_par_generation

    attendu = {1940: 150, 1943: 150, 1944: 152, 1945: 154,
               1946: 156, 1947: 158, 1948: 160}
    for generation, trimestres in attendu.items():
        carriere = simulateur.carriere_simple(
            annee_naissance=generation, sexe="H",
            affiliation="salarie_prive_non_cadre", age_debut=25, age_liquidation=62,
        )
        requis, _ = scenario._duree_requise(periode, carriere)
        proratisation, _ = scenario._duree_proratisation(periode, carriere, requis)
        assert proratisation == trimestres, generation
        assert proratisation <= requis, generation

    # À compter de 1949 il n'y a plus deux paramètres : la table s'arrête, et
    # c'est la durée requise qui répond. La prolonger en escalier rendrait
    # l'erreur dans l'autre sens — 160 trimestres à qui en doit 172.
    for generation in (1949, 1955, 1965, 1975):
        carriere = simulateur.carriere_simple(
            annee_naissance=generation, sexe="H",
            affiliation="salarie_prive_non_cadre", age_debut=25, age_liquidation=62,
        )
        requis, _ = scenario._duree_requise(periode, carriere)
        proratisation, _ = scenario._duree_proratisation(periode, carriere, requis)
        assert proratisation == requis, generation


def test_la_proratisation_ne_penalise_pas_une_carriere_qui_atteint_sa_duree(simulateur):
    """Le cas qui a révélé le défaut : né en 1945, 156 trimestres, parti en 2007.

    Le droit lui oppose 160 trimestres pour le taux — il est décoté de quatre —
    mais 154 pour la proratisation : son coefficient vaut 1. Le modèle divisait
    par 160 et lui retirait 2,5 % de pension de base en plus de la décote.
    """
    lignes = [
        AnneeCarriere(annee=annee, revenu=25000.0,
                      affiliation="salarie_prive_non_cadre", trimestres_valides=4)
        for annee in range(1968, 2007)
    ]
    carriere = Carriere(annee_naissance=1945, sexe="H", lignes=lignes,
                        age_liquidation=62.0)
    resultat = simulateur.scenario_actuel.calculer(carriere)
    assert resultat.trimestres_valides == 156
    base = next(p for p in resultat.pensions_par_regime
                if p.regime == "regime_general")
    assert "154/154" in base.detail, base.detail


def test_les_trimestres_de_decote_sont_des_entiers(simulateur):
    """Article R. 351-27 : le nombre de trimestres est arrondi à l'entier supérieur.

    Les âges d'annulation de la décote des générations 1951 à 1954 valent 65,33,
    65,75, 66,17 et 66,58 ans. Sans arrondi, on opposait 13,32 trimestres à un
    assuré né en 1951 parti à 62 ans, quand le droit lui en oppose 14 : un taux
    de 40,01 % au lieu de 39,50 %.
    """
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["regime_general"].periode(2015)
    for generation in range(1945, 1976):
        for age_depart in (60.0, 61.0, 62.0, 63.0, 64.0, 65.0):
            carriere = simulateur.carriere_simple(
                annee_naissance=generation, sexe="H",
                affiliation="salarie_prive_non_cadre",
                age_debut=30, age_liquidation=age_depart,
            )
            _, age_annulation, _ = scenario._decote(
                periode, carriere, carriere.annee_liquidation
            )
            retenus = scenario._trimestres_de_decote(
                periode, carriere, carriere.trimestres_actuels, 168, age_depart,
                age_annulation,
            )
            assert retenus == int(retenus), (generation, age_depart, retenus)


def test_les_neutralisations_ne_commandent_rien(simulateur):
    """Elles DÉCLARENT ce que les scénarios notionnels retirent, sans le piloter.

    La suppression n'est pas une option qu'on active : elle est la conséquence
    mécanique de la règle d'accumulation. Ce test fige la propriété, pour qu'on
    ne redonne pas à ces drapeaux un pouvoir qu'ils n'ont pas — et pour que la
    documentation cesse de le laisser croire.
    """
    carriere = dict(
        annee_naissance=1975, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=22, age_liquidation=64, niveau_salaire=0.45, nombre_enfants=3,
    )
    tous_actifs = Simulateur(Parametres()).simuler(
        Simulateur(Parametres()).carriere_simple(**carriere)
    )
    aucun = Simulateur(
        Parametres(neutralisations=Neutralisations(
            minimum_contributif=False, majoration_enfants=False,
            majoration_duree_assurance=False, minimum_vieillesse_aspa=False,
        ))
    )
    resultat = aucun.simuler(aucun.carriere_simple(**carriere))
    for cle, _, _ in SCENARIOS_NOTIONNELS:
        assert (getattr(resultat, cle).pension_annuelle
                == pytest.approx(getattr(tous_actifs, cle).pension_annuelle))
    assert resultat.actuel.pension_annuelle == pytest.approx(
        tous_actifs.actuel.pension_annuelle
    )


def test_rendement_instantane_reproduit_le_repere_publie(simulateur):
    """Agirc-Arrco 2025 : le régime publie un rendement de 5,61 %.

    C'est le seul chiffre que la caisse communique directement, et il enchaîne
    les trois grandeurs du fichier. S'il tombe juste, elles sont cohérentes.
    """
    from retraite_notionnelle.scenarios.actuel import ValeursPoint

    valeurs = ValeursPoint(simulateur.parametres.racine_donnees)
    reference, taux_appel, _ = valeurs.achat("agirc_arrco", 2025)
    service, _ = valeurs.service("agirc_arrco", 2025)
    assert service / (reference * taux_appel) == pytest.approx(0.0561, abs=0.0002)


def test_un_regime_sans_valeur_de_point_garde_le_rendement(simulateur):
    """La bascule est régime par régime, pas globale.

    La part proportionnelle de la MSA n'a pas de prix d'achat du point dans le
    dépôt : elle doit continuer d'être calculée au rendement instantané, sans
    que rien ne casse. Le régime de base des libéraux tenait ce rôle jusqu'à ce
    que ses deux façons d'acquérir des points soient toutes deux paramétrées —
    cent points par trimestre validé avant 2004, un barème en points depuis —
    et il ne passe donc plus par le rendement.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1960, sexe="F", affiliation="exploitant_agricole",
        age_debut=25, age_liquidation=64,
    )
    pensions = {p.regime: p for p in simulateur.simuler(carriere).actuel.pensions_par_regime}
    assert "msa_non_salaries" in pensions
    assert "rendement" in pensions["msa_non_salaries"].detail
    assert pensions["msa_non_salaries"].montant > 0


def test_le_prix_du_point_n_est_pas_prolonge_au_dela_du_publie(simulateur):
    """Un barème inconnu ne doit pas être supposé gelé.

    Prolonger le dernier prix d'achat connu ferait acheter les points trop bon
    marché et gonflerait la pension sans que rien ne le signale. Ces années
    doivent retomber sur le rendement instantané, qui, lui, s'annonce approximatif.
    """
    from retraite_notionnelle.scenarios.actuel import ValeursPoint

    valeurs = ValeursPoint(simulateur.parametres.racine_donnees)
    assert valeurs.achat("agirc", 2018) is not None
    assert valeurs.achat("agirc", 2019) is None, "barème Agirc prolongé après sa fermeture"
    assert valeurs.achat("rafp", 2005) is not None


def test_rafp_et_rci_sont_calcules_en_points(simulateur):
    """Les deux régimes que la recherche de sources a permis d'ajouter."""
    fonctionnaire = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="fonctionnaire_etat",
        age_debut=23, age_liquidation=64, part_primes=0.20,
    )
    artisan = simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="artisan",
        age_debut=25, age_liquidation=64,
    )
    for carriere, code in ((fonctionnaire, "rafp"), (artisan, "rci")):
        pensions = {p.regime: p for p in simulateur.simuler(carriere).actuel.pensions_par_regime}
        assert code in pensions, code
        assert "points × valeur de service" in pensions[code].detail, code


def test_le_producteur_prime_sur_la_transcription(simulateur):
    """L'Ircantec est le seul régime dont on ait les deux sources.

    Ses barèmes viennent de la Caisse des dépôts, qui gère le régime, et non
    d'OpenFisca qui les transcrit. Là où le producteur publie, ses valeurs
    doivent être certifiées ; ailleurs, la transcription reprend au niveau
    « haute ».
    """
    import csv

    from retraite_notionnelle.donnees.chargement import Fiabilite

    chemin = (simulateur.parametres.racine_donnees / "reference" / "regimes"
              / "valeurs_point.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))
            if l["regime"] == "ircantec"]

    niveaux = {int(l["annee"]): l["fiabilite"] for l in lignes}
    assert niveaux[1971] == "certifiee"
    assert niveaux[2021] == "certifiee"
    assert niveaux[2022] == "haute", "hors couverture du producteur, la transcription"
    assert Fiabilite.depuis_texte("certifiee") > Fiabilite.depuis_texte("haute")


def test_les_baremes_d_avant_la_fusion_viennent_de_la_federation(simulateur):
    """L'Agirc, l'Arrco et l'UNIRS sont lus dans la compilation Agirc-Arrco.

    Ces barèmes pèsent, dans la pension d'un salarié du privé, plus lourd que
    tous les autres réunis, et ils venaient d'une transcription. La fédération
    publie les siens depuis 1947 : ce qu'elle couvre est certifié.

    Les lignes `arrco` d'avant 1999 font exception, et c'est voulu : leur
    VALEUR est celle de l'UNIRS, certifiée sous ce nom, mais la substitution
    d'une caisse au régime est une décision du dépôt, que nulle source ne
    porte. Elles restent donc au niveau « moyenne », à la valeur près, qui doit
    être exactement celle du producteur.
    """
    import csv

    chemin = (simulateur.parametres.racine_donnees / "reference" / "regimes"
              / "valeurs_point.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))]
    table = {(l["regime"], int(l["annee"]), l["mesure"]): l for l in lignes}

    for cle in (("agirc", 1947, "valeur_service"), ("agirc", 2018, "valeur_service"),
                ("arrco", 1999, "salaire_reference"), ("unirs", 1961, "valeur_service"),
                ("unirs", 1998, "salaire_reference")):
        assert table[cle]["fiabilite"] == "certifiee", cle

    for annee in (1961, 1998):
        for mesure in ("valeur_service", "salaire_reference"):
            substituee = table[("arrco", annee, mesure)]
            assert substituee["fiabilite"] == "moyenne"
            assert substituee["valeur"] == table[("unirs", annee, mesure)]["valeur"]

    # 26,00 anciens francs de 1947, à la parité irrévocable : la conversion est
    # exacte, et c'est elle qui distingue la lecture du producteur de l'arrondi
    # à quatre décimales que portait la transcription.
    assert float(table[("agirc", 1947, "salaire_reference")]["valeur"]) == pytest.approx(
        0.26 / 6.55957, abs=5e-7)


def test_valeurs_du_point_des_avocats_sont_sourcees(simulateur):
    """Les barèmes de la CNBF, seule source qui porte la valeur du point des avocats.

    Elles sont rangées sous ``cnbf_complementaire``, et **le moteur s'en sert
    depuis que la fiche est scindée** : le régime de base des avocats est
    forfaitaire, le complémentaire est en points, et les agréger en un seul taux
    au rendement instantané effaçait les deux règles à la fois.
    """
    import csv

    from retraite_notionnelle.scenarios.actuel import ValeursPoint

    chemin = (simulateur.parametres.racine_donnees / "reference" / "regimes"
              / "valeurs_point.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))
            if l["regime"] == "cnbf_complementaire"]

    valeurs = {(int(l["annee"]), l["mesure"]): float(l["valeur"]) for l in lignes}
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert valeurs[(2026, "salaire_reference")] == pytest.approx(12.5229)
    assert valeurs[(2026, "valeur_service")] == pytest.approx(1.0262)

    # Le rendement d'un régime complémentaire décroît : c'est ce qui permet de
    # détecter une lecture de travers dans le PDF du barème.
    annees = sorted({a for a, _ in valeurs})
    rendements = [valeurs[(a, "valeur_service")] / valeurs[(a, "salaire_reference")]
                  for a in annees]
    assert all(apres < avant for avant, apres in zip(rendements, rendements[1:]))
    assert 0.08 < rendements[-1] < 0.11

    # Le catalogue porte ce code, et le prix d'achat lui est attaché — pas au
    # régime de base, qui n'a pas de point.
    assert "cnbf_complementaire" in simulateur.catalogue
    valeurs_point = ValeursPoint(simulateur.parametres.racine_donnees)
    assert valeurs_point.achat("cnbf", 2026) is None
    assert valeurs_point.achat("cnbf_complementaire", 2026) is not None


def test_valeur_du_point_des_liberaux_est_sourcee(simulateur):
    """La CNAVPL publie sa valeur du point dans ses recueils, et nulle part ailleurs.

    Le décret annuel ne fixe qu'un coefficient de revalorisation : ni le
    Journal officiel ni la législation consolidée ne portent le montant, ce que
    quatre dépouillements ont établi. Ces valeurs viennent donc de la caisse.

    Le moteur ne s'en sert pas encore : le prix d'acquisition d'un point se
    déduit du taux de tranche et d'un plafond de points que le recueil ne
    livre pas sous une forme relisible. Tant qu'il manque, la CNAVPL reste au
    rendement instantané.
    """
    import csv

    from retraite_notionnelle.scenarios.actuel import ValeursPoint

    chemin = (simulateur.parametres.racine_donnees / "reference" / "regimes"
              / "valeurs_point.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))
            if l["regime"] == "cnavpl"]

    valeurs = {(int(l["annee"]), l["mesure"]): float(l["valeur"]) for l in lignes}
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert valeurs[(2025, "valeur_service")] == pytest.approx(0.6540)
    # 8,73 % en 2025 : le taux de T1 a été relevé avec la réforme de l'assiette
    # des indépendants, et le barème en points a suivi — 557 points au plafond
    # au lieu de 525, soit le rapport exact des deux taux. Les recueils 2024 et
    # 2025 portent l'un et l'autre ce tableau, et ils concordent. La série le
    # lisait à 8,23 %, taux pris dans une phrase de l'historique qui décrit la
    # réforme de 2015 et non l'année du recueil.
    assert valeurs[(2025, "taux_t1")] == pytest.approx(0.0873)
    assert valeurs[(2024, "taux_t1")] == pytest.approx(0.0823)
    assert valeurs[(2025, "taux_t2")] == pytest.approx(0.0187)

    services = [valeurs[(a, "valeur_service")]
                for a in sorted({a for a, m in valeurs if m == "valeur_service"})]
    assert all(apres > avant for avant, apres in zip(services, services[1:]))

    # Faute de prix d'acquisition, le moteur doit rester sur le rendement.
    assert ValeursPoint(simulateur.parametres.racine_donnees).achat("cnavpl", 2025) is None


def test_valeur_du_point_agirc_arrco_est_recoupee_par_l_insee(simulateur):
    """Deux transcriptions publiques indépendantes, et elles concordent.

    Les barèmes de l'Agirc et de l'Arrco pèsent plus lourd que tous les autres
    réunis dans la pension d'un salarié du privé, et leur seule source était
    jusqu'ici OpenFisca — invérifiable, la caisse ne publiant pas de série.
    L'INSEE en diffuse la valeur de service depuis 2001 sous trois idbanks ;
    ``controle_vraisemblance_point_insee`` compare les deux à chaque exécution.

    Ce test garde ce que ce recoupement a rapporté : l'année 2025, que seule
    la série INSEE couvre, la transcription s'arrêtant à 2024. Sans elle une
    liquidation de 2025 convertissait ses points au barème de 2024.
    """
    import csv

    chemin = (simulateur.parametres.racine_donnees / "reference" / "regimes"
              / "valeurs_point.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))
            if l["mesure"] == "valeur_service"]

    par_regime: dict[str, dict[int, float]] = {}
    for ligne in lignes:
        par_regime.setdefault(ligne["regime"], {})[int(ligne["annee"])] = float(
            ligne["valeur"])

    # Les valeurs de part et d'autre de la fusion, au 31 décembre — la
    # convention du fichier. La dernière de l'Arrco, 1,2588 €, est celle que
    # l'Agirc-Arrco reprend au 1er janvier 2019 avant de la revaloriser en
    # novembre : la continuité du point est vérifiable, l'Agirc restant à part
    # puisque ses points ont été convertis dans le rapport des deux valeurs.
    assert par_regime["arrco"][2018] == pytest.approx(1.2588, abs=1e-4)
    assert par_regime["agirc"][2018] == pytest.approx(0.4378, abs=1e-4)
    assert par_regime["agirc_arrco"][2019] == pytest.approx(1.2714, abs=1e-4)

    # Ce que le recoupement a ajouté : la dernière année, absente d'OpenFisca.
    assert par_regime["agirc_arrco"][2025] == pytest.approx(1.4386, abs=1e-4)

    # La valeur de service ne recule jamais : elle est gelée, jamais rabotée.
    for regime in ("arrco", "agirc", "agirc_arrco"):
        annees = sorted(a for a in par_regime[regime] if a >= 2001)
        valeurs = [par_regime[regime][a] for a in annees]
        assert all(apres >= avant for avant, apres in zip(valeurs, valeurs[1:]))


def test_valeur_du_point_de_la_complementaire_agricole_est_sourcee(simulateur):
    """La dernière caisse en points sans série a fini par en avoir une.

    Elle ne vient ni de la MSA ni de son service statistique — les « Chiffres
    utiles » sont un annuaire d'effectifs — mais du code rural lui-même, dont
    l'article D. 732-166 fixe la valeur chaque année depuis 2005. La base LEGI
    de la DILA en garde toutes les versions datées ; c'est la publication
    officielle, d'où le niveau du producteur.

    Les valeurs sont rangées sous ``msa_rco``, code qui a désormais sa propre
    fiche : la RCO a été scindée du régime de base, faute de quoi tout verser
    dans le complémentaire aurait fait disparaître la base. Ce test garde cette
    séparation autant que les valeurs.
    """
    import csv

    from retraite_notionnelle.donnees import CatalogueRegimes

    chemin = (simulateur.parametres.racine_donnees / "reference" / "regimes"
              / "valeurs_point.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = [l for l in csv.DictReader(
            x for x in flux if not x.lstrip().startswith("#"))
            if l["regime"] == "msa_rco"]

    valeurs = {int(l["annee"]): float(l["valeur"]) for l in lignes}
    assert {l["fiabilite"] for l in lignes} == {"certifiee"}
    assert {l["mesure"] for l in lignes} == {"valeur_service"}

    # Bornes de la série, et l'année 2019 — que seul un décret fixant deux
    # années d'un coup fait entrer : aucun texte ne lui est propre.
    assert valeurs[2005] == pytest.approx(0.2972)
    assert valeurs[2019] == pytest.approx(0.3392)
    assert valeurs[2024] == pytest.approx(0.3835)

    annees = sorted(valeurs)
    assert annees == list(range(annees[0], annees[-1] + 1)), "la série a un trou"
    assert all(valeurs[b] >= valeurs[a] for a, b in zip(annees, annees[1:]))

    # La fiche est désormais scindée : la RCO a la sienne, et c'est elle qui
    # porte le barème en points ; la base garde la sienne, et son étage
    # proportionnel reste au rendement instantané faute de barème publié.
    catalogue = CatalogueRegimes(simulateur.parametres.racine_donnees)
    assert "msa_rco" in catalogue
    assert "msa_non_salaries" in catalogue
    rco = catalogue["msa_rco"].periode(2020)
    assert rco.type_calcul == "points"
    # Le barème est en POINTS : 100 points pour 1 820 SMIC, et le nombre de
    # points ne dépend donc pas du taux de cotisation — ce qui est heureux,
    # puisque c'est le barème qui est publié, pas le prix d'achat.
    assert rco.points_maximum == 100
    assert rco.assiette_repere_smic == 1820
    assert rco.assiette_plancher is True


# -- montée en charge des réformes, lue à la génération ----------------------


def test_les_salaires_anciens_sont_revalorises_sur_les_salaires(simulateur):
    """Le compte n'a pas toujours été revalorisé sur les prix.

    Les arrêtés annuels de revalorisation ont suivi les SALAIRES jusqu'en 1986
    avant de suivre les prix. Sur les Trente Glorieuses, les salaires ont crû
    nettement plus vite que les prix : appliquer la règle des prix à ces
    années-là ramenait au compte des salaires très en dessous de ce que le
    droit y a inscrit, et minorait le salaire de référence d'autant.
    """
    macro = simulateur.macro
    salaires = macro.coefficient_revalorisation_salaires(1960, 2025)
    prix = macro.coefficient_prix(1960, 2025)
    assert salaires > prix

    # À partir de 1987, les deux règles ne font plus qu'une.
    assert macro.coefficient_revalorisation_salaires(1990, 2025) == pytest.approx(
        macro.coefficient_prix(1990, 2025)
    )
    # Et le coefficient reste réversible, comme celui des prix.
    assert macro.coefficient_revalorisation_salaires(2025, 1960) == pytest.approx(
        1.0 / salaires
    )


def test_les_coefficients_de_revalorisation_reproduisent_les_circulaires(simulateur):
    """Le contrôle qui compte : ce que la CAISSE a publié, colonne par colonne.

    La Cnav publie, à chaque revalorisation, la table entière des coefficients
    des salaires portés au compte. Le témoin en fige dix, de 2017 à 2026 ; ce
    test oppose au modèle chacune d'elles, année de perception par année de
    perception.

    C'est une vérification par la SOURCE, pas par une seconde implémentation :
    la table d'OpenFisca, que le dépôt a d'abord reprise, s'écarte de la
    circulaire de 2023 de −3 % à −5,5 % après 1990 (il lui manque la
    revalorisation exceptionnelle de 4 % du 1er juillet 2022) et de −17 % à
    +10 % sur les années 1950.

    Les colonnes dont la date d'effet n'est pas le 1er janvier sont comparées
    hors de leur propre année : le modèle raisonne à l'année et retient l'état
    au 1er janvier, quand ces colonnes portent déjà la revalorisation de leur
    millésime.
    """
    import json

    temoin = json.loads(
        (RACINE_TEMOINS / "cnav_revalorisation_salaires.json").read_text(
            encoding="utf-8"
        )
    )
    colonnes = temoin["colonnes"]
    assert len(colonnes) >= 8
    macro = simulateur.macro
    pire = (0.0, None, None)
    for effet, publiee in colonnes.items():
        annee = int(effet[:4])
        if not effet.endswith("-01-01"):
            continue
        for perception, publie in publiee.items():
            perception = int(perception)
            if perception >= annee:
                continue
            nous = macro.coefficient_revalorisation_portee_au_compte(perception, annee)
            ecart = abs(nous - publie) / publie
            if ecart > pire[0]:
                pire = (ecart, effet, perception)
    # Le modèle sert la colonne publiée quand elle existe : sur ces années-là
    # l'écart est nul. Il ne reste que les colonnes que le témoin porte sans que
    # le CSV les serve — aucune aujourd'hui, d'où une borne très serrée.
    assert pire[0] < 1e-9, f"{pire[1]}, perception {pire[2]} : {pire[0]:.3%}"


def test_la_reconstruction_entre_colonnes_reste_dans_sa_derive(simulateur):
    """Ce que coûte une année de liquidation SANS colonne publiée.

    Toutes les liquidations n'ont pas leur circulaire : le modèle reconstruit
    alors depuis la colonne la plus proche, par rapport de deux de ses valeurs.
    Ce test mesure ce que cette reconstruction coûte, en la faisant sur des
    années dont on a justement la colonne — le seul endroit où l'erreur est
    observable.

    La dérive vient de la caisse elle-même : elle arrondit sa table à trois
    décimales et repart chaque année de la précédente, si bien que les arrondis
    s'accumulent. Mesuré : 0,01 % depuis la colonne voisine, contre 0,16 %
    depuis celle de 2026. C'est ce rapport de dix qui justifie d'ancrer sur la
    plus proche plutôt que sur la plus récente, et c'est lui que ce test
    protège.
    """
    import json

    colonnes = json.loads(
        (RACINE_TEMOINS / "cnav_revalorisation_salaires.json").read_text(
            encoding="utf-8"
        )
    )["colonnes"]
    tables = {
        int(effet[:4]): {int(a): v for a, v in table.items()}
        for effet, table in colonnes.items() if effet.endswith("-01-01")
    }
    pire_voisine, pire_lointaine = 0.0, 0.0
    for annee, publiee in tables.items():
        voisines = sorted(
            (abs(a - annee), a) for a in tables
            if a != annee and annee in tables[a]
        )
        if not voisines:
            continue
        for ancre, garder in ((voisines[0][1], "voisine"), (max(tables), "lointaine")):
            if ancre == annee or annee not in tables[ancre]:
                continue
            diviseur = tables[ancre][annee]
            for perception, publie in publiee.items():
                if perception >= annee or perception not in tables[ancre]:
                    continue
                ecart = abs(tables[ancre][perception] / diviseur - publie) / publie
                if garder == "voisine":
                    pire_voisine = max(pire_voisine, ecart)
                else:
                    pire_lointaine = max(pire_lointaine, ecart)
    assert pire_voisine < 2e-3, f"reconstruction depuis la voisine : {pire_voisine:.3%}"
    # Et la plus proche doit rester nettement meilleure que la plus récente,
    # sans quoi la règle d'ancrage ne vaudrait plus la complexité qu'elle coûte.
    assert pire_voisine < pire_lointaine


def test_le_coefficient_de_revalorisation_est_le_rapport_de_deux_valeurs(simulateur):
    """Une colonne, deux valeurs, un rapport — et la neutralité sur place.

    Le modèle ne stocke pas un coefficient par couple d'années mais une colonne
    par circulaire. Cela suppose que la revalorisation d'une année soit un
    coefficient UNIQUE, appliqué à tous les salaires déjà portés au compte
    quelle que soit leur année de perception ; les deux tests précédents le
    vérifient contre la source, celui-ci vérifie que le modèle applique bien la
    règle, et qu'il reste réversible et neutre sur place.
    """
    macro = simulateur.macro
    colonnes = macro.revalorisation_portee_au_compte
    assert [annee for annee, _, _ in colonnes] == sorted(
        annee for annee, _, _ in colonnes
    )
    assert macro.derniere_liquidation_revalorisee == colonnes[-1][0]

    lu = macro.coefficient_revalorisation_portee_au_compte
    derniere, _, recente = colonnes[-1]
    assert lu(1970, derniere) == pytest.approx(recente[1970])

    # Une année de liquidation sans colonne publiée passe par la PLUS PROCHE,
    # et non par la plus récente : c'est ce qui divise la dérive par dix.
    proche = min(colonnes, key=lambda c: abs(c[0] - 1990))[2]
    assert lu(1970, 1990) == pytest.approx(proche[1970] / proche[1990])
    assert lu(1970, 1990) != pytest.approx(recente[1970] / recente[1990])

    assert lu(2000, 2000) == 1.0
    assert lu(2018, 1970) == pytest.approx(1.0 / lu(1970, 2018))


def test_les_coefficients_lus_corrigent_l_ancienne_approximation(simulateur):
    """« Les salaires jusqu'en 1986, les prix depuis » sur-revalorisait.

    L'approximation décrit les arrêtés dans les grandes lignes, mais ignore
    leurs revalorisations semestrielles, leurs gels, leurs revalorisations
    exceptionnelles et leurs changements de délai d'application. Elle reste en
    vigueur hors de la plage publiée : ce test mesure ce qu'elle coûte là où
    elle ne l'est plus.
    """
    macro = simulateur.macro
    for depart, arrivee in ((1970, 2018), (1980, 2018), (1960, 2026)):
        approche = macro.coefficient_revalorisation_salaires(depart, arrivee)
        lu = macro.coefficient_revalorisation_portee_au_compte(depart, arrivee)
        assert approche > lu, (depart, arrivee)
        assert approche / lu < 1.30, (depart, arrivee)


def test_le_coefficient_de_revalorisation_s_ancre_sur_la_derniere_circulaire(
        simulateur):
    """Une liquidation postérieure aux circulaires lit quand même les arrêtés.

    Les circulaires publiées s'arrêtent à une année ; au-delà, tout approcher
    rendrait la table inutile là où le site simule le plus. Le modèle ancre donc
    sur la dernière colonne et n'approche que le bout du chemin.
    """
    macro = simulateur.macro
    colonnes = macro.revalorisation_portee_au_compte
    derniere, _, table = colonnes[-1]

    attendu = table[1970] * macro.coefficient_revalorisation_salaires(
        derniere, derniere + 4
    )
    assert macro.coefficient_revalorisation_portee_au_compte(
        1970, derniere + 4
    ) == pytest.approx(attendu)

    # En deçà de la première année publiée, il n'y a rien sur quoi ancrer :
    # l'approximation reprend toute la main, et le modèle ne fait pas semblant.
    avant = min(min(t) for _, _, t in colonnes) - 5
    assert macro.coefficient_revalorisation_portee_au_compte(avant, derniere) == (
        pytest.approx(macro.coefficient_revalorisation_salaires(avant, derniere))
    )


def test_le_dernier_traitement_ne_recoit_pas_les_coefficients_du_regime_general(
        simulateur):
    """Les arrêtés ne valent que pour un salaire PORTÉ AU COMPTE.

    Une pension civile se liquide sur le traitement des six derniers mois de
    service : rien n'y est porté à un compte, et rien n'y est donc revalorisé
    par les coefficients de la CNAV. Leur appliquer serait une erreur de
    catégorie. Ce qui ramène le traitement de l'année d'avant à l'année du
    départ, c'est le POINT D'INDICE : le fonctionnaire garde son indice, et
    c'est ce que la confrontation à OpenFisca-France-Pension a fait voir — le
    modèle passait par les prix, et s'en écartait de 0,5 à 0,8 %.
    """
    from retraite_notionnelle.carriere import (
    AnneeCarriere,
    Carriere,
    LigneRelevee,
    Metier,
)

    lignes = [
        AnneeCarriere(annee=annee, revenu=30000.0,
                      affiliation="fonctionnaire_etat", trimestres_valides=4)
        for annee in range(1980, 2020)
    ]
    carriere = Carriere(annee_naissance=1958, sexe="H", lignes=lignes,
                        age_liquidation=62.0, identifiant="fp")
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["fonction_publique_etat"].periode(2020)
    assert periode.salaire_reference == "derniers_6_mois"
    assert periode.assiette == "hors_primes"
    reference = scenario.salaire_de_reference(
        "fonction_publique_etat", carriere, periode, 2020, False, 1958, True,
    )
    # Le dernier traitement, primes exclues, ramené en euros de l'année de
    # liquidation par le POINT D'INDICE — gelé de 2019 à 2020, donc inchangé —
    # et non par l'arrêté de la CNAV, qui donne 1,01 pour ce même passage, ni
    # par les prix, qui donnaient 1,0048.
    derniere = carriere.lignes[-1]
    traitement = derniere.revenu * (1.0 - derniere.part_primes)
    macro = simulateur.macro
    point = scenario.minimum_garanti.ratio_point_indice(derniere.annee, 2020)
    assert point == pytest.approx(1.0)
    assert reference == pytest.approx(traitement * point)
    assert reference != pytest.approx(
        traitement * macro.coefficient_revalorisation_salaires(derniere.annee, 2020)
    )
    assert reference != pytest.approx(
        traitement * macro.coefficient_revalorisation_portee_au_compte(
            derniere.annee, 2020,
        )
    )


def test_le_nombre_d_annees_du_salaire_de_reference_suit_la_generation(simulateur):
    """Dix à vingt-cinq années, à raison d'une par génération, de 1934 à 1948.

    Lu à l'année de liquidation, le paramètre opposait vingt-cinq années à des
    assurés auxquels la loi n'en a jamais demandé plus de dix — et étendre la
    moyenne aux années les plus faibles ne peut que l'abaisser.
    """
    from retraite_notionnelle.scenarios.actuel import AnneesSalaireReference

    table = AnneesSalaireReference(simulateur.parametres.racine_donnees)
    assert table.annees(1930)[0] == 10
    assert table.annees(1938)[0] == 15
    assert table.annees(1948)[0] == 25
    assert table.annees(1975)[0] == 25

    # Deux générations qui liquident à trente ans d'écart, même carrière type :
    # la plus ancienne relève de dix années, la plus récente de vingt-cinq.
    scenario = simulateur.scenario_actuel
    ancien = simulateur.carriere_simple(
        annee_naissance=1930, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=64, profil_carriere="ascendant",
    )
    recent = simulateur.carriere_simple(
        annee_naissance=1975, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=20, age_liquidation=64, profil_carriere="ascendant",
    )
    catalogue = simulateur.catalogue
    periode_ancienne = catalogue["regime_general"].periode(
        ancien.annee_liquidation)
    periode_recente = catalogue["regime_general"].periode(recent.annee_liquidation)
    dix = scenario.salaire_de_reference(
        "regime_general", ancien, periode_ancienne,
        ancien.annee_liquidation, True, 1930)
    vingt_cinq = scenario.salaire_de_reference(
        "regime_general", ancien, periode_ancienne,
        ancien.annee_liquidation, True, 1975)
    assert dix > vingt_cinq
    assert periode_recente.salaire_reference_par_generation


def test_le_coefficient_de_minoration_suit_la_generation(simulateur):
    """2,5 % par trimestre avant 1944, 1,25 % à partir de 1953.

    La table de l'article R. 351-27 vaut aussi bien pour l'ancien droit —
    1,25 point retiré au taux de 50 %, soit 2,5 % de ce taux — que pour la
    montée en charge de la loi Fillon.
    """
    from retraite_notionnelle.scenarios.actuel import CoefficientsMinoration

    table = CoefficientsMinoration(simulateur.parametres.racine_donnees)
    assert table.coefficient(1940)[0] == pytest.approx(0.025)
    assert table.coefficient(1944)[0] == pytest.approx(0.02375)
    assert table.coefficient(1952)[0] == pytest.approx(0.01375)
    assert table.coefficient(1953)[0] == pytest.approx(0.0125)
    assert table.coefficient(1990)[0] == pytest.approx(0.0125)


def test_la_decote_est_plafonnee_a_vingt_trimestres(simulateur):
    """Le taux ne descend pas sous 37,5 %, quelle que soit l'anticipation.

    Sans ce plafond, un départ dix ans avant l'heure retirait la moitié de la
    pension de base là où le droit n'en retire que le quart.
    """
    resultats = {}
    for age in (52, 57, 62):
        carriere = simulateur.carriere_simple(
            annee_naissance=1965, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=25, age_liquidation=age,
        )
        resultats[age] = simulateur.scenario_actuel.calculer(carriere)

    # 50 % × (1 − 1,25 % × 20) = 37,5 %, et pas moins.
    assert resultats[52].taux_liquidation == pytest.approx(0.375)
    assert resultats[57].taux_liquidation == pytest.approx(0.375)
    assert resultats[62].taux_liquidation == pytest.approx(0.375)


def test_l_age_d_annulation_de_la_decote_suit_la_generation(simulateur):
    """65 ans jusqu'à la génération 1950, 67 à partir de 1955.

    Les fiches portaient l'âge CIBLE de la loi de 2010 dès son entrée en
    vigueur, opposant 67 ans à des générations auxquelles la loi n'a jamais
    demandé plus de 65.
    """
    from retraite_notionnelle.scenarios.actuel import AgesAnnulationDecote

    table = AgesAnnulationDecote(simulateur.parametres.racine_donnees)
    assert table.age(1940)[0] == pytest.approx(65.0)
    assert table.age(1953)[0] == pytest.approx(66.17)
    assert table.age(1960)[0] == pytest.approx(67.0)

    # Une carrière courte liquidée à 65 ans : la génération 1945 y est au taux
    # plein d'office, la génération 1960 non.
    taux = {}
    for generation in (1945, 1960):
        carriere = simulateur.carriere_simple(
            annee_naissance=generation, sexe="H",
            affiliation="salarie_prive_non_cadre",
            age_debut=40, age_liquidation=65,
        )
        taux[generation] = simulateur.scenario_actuel.calculer(carriere).taux_liquidation
    assert taux[1945] == pytest.approx(0.50)
    assert taux[1960] < 0.50


# -- abattement propre aux complémentaires -----------------------------------


def test_les_coefficients_d_anticipation_sont_ceux_de_l_agirc_arrco():
    """Le barème du régime, et non la décote du régime de base.

    Deux tables — trimestres manquants, et âge — dont la plus avantageuse est
    retenue. L'exemple que la caisse publie elle-même : un participant né en
    1959 qui demande sa retraite à 63 ans et 2 mois (0,83 par l'âge) et totalise
    155 trimestres sur 167 requis (0,88 pour douze trimestres manquants) se voit
    appliquer 0,88.
    """
    from retraite_notionnelle.scenarios.actuel import _coefficient_anticipation

    # Table des trimestres manquants : un point par trimestre jusqu'à douze,
    # un point et quart ensuite, et rien au-delà de vingt.
    assert _coefficient_anticipation(0, 20) == pytest.approx(1.0)
    assert _coefficient_anticipation(1, 20) == pytest.approx(0.99)
    assert _coefficient_anticipation(12, 20) == pytest.approx(0.88)
    assert _coefficient_anticipation(20, 20) == pytest.approx(0.78)
    assert _coefficient_anticipation(21, 20) is None

    # Table des âges : elle descend un palier plus bas, jusqu'à 0,43.
    assert _coefficient_anticipation(40, 40) == pytest.approx(0.43)

    # Les trimestres sont arrondis AU SUPÉRIEUR : trois ans et dix mois
    # d'anticipation valent seize trimestres, pas quinze.
    assert _coefficient_anticipation(15 + 1 / 3, 40) == pytest.approx(0.83)


def test_l_abattement_de_la_complementaire_n_est_pas_celui_de_la_base(simulateur):
    """À dix ans d'anticipation, 0,43 chez l'Agirc-Arrco, 0,75 à la base.

    Les deux barèmes ne se recoupent pas : le régime complémentaire est plus
    doux sur les carrières courtes et beaucoup plus dur sur l'âge. Retenir la
    décote de la base, comme le faisait le modèle, était faux dans les deux
    sens.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="salarie_prive_non_cadre",
        age_debut=25, age_liquidation=57,
    )
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["agirc_arrco"].periode(2019)
    requis = scenario.durees_requises.trimestres(1965)[0]
    abattement = scenario._abattement_points(
        periode, carriere, 100, requis, 57.0, 2022)
    assert abattement == pytest.approx(0.43)

    # Au taux plein, aucun abattement, quel que soit l'âge.
    assert scenario._abattement_points(
        periode, carriere, requis, requis, 57.0, 2022) == pytest.approx(1.0)


def test_la_majoration_pour_enfants_de_la_complementaire_est_plafonnee(simulateur):
    """10 % à la base, mais au plus 2 367 € par an à l'Agirc-Arrco.

    Sans ce plafond, les familles très nombreuses de salariés du privé étaient
    surestimées : le cadre qui touche 30 000 € de complémentaire s'en voyait
    majorer de 3 000 € au lieu des 2 367 € que le régime sert au maximum.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="F", affiliation="salarie_prive_cadre",
        age_debut=23, age_liquidation=64, niveau_salaire=3.0,
        profil_carriere="fortement_ascendant", nombre_enfants=4,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    majoration = next(a for a in resultat.avantages_appliques
                      if a.code == "majoration_enfants")
    complementaire = sum(
        p.montant for p in resultat.pensions_par_regime
        if p.regime in ("agirc", "arrco", "agirc_arrco")
    )
    assert "plafonnée" in majoration.detail
    assert majoration.montant < 0.10 * (
        complementaire + sum(p.montant for p in resultat.pensions_par_regime
                             if p.regime == "regime_general")
    )


def test_la_mda_compte_dans_la_proratisation_du_regime_qui_la_porte(simulateur):
    """Le droit attribue les trimestres DANS un régime, pas au-dessus d'eux.

    Ils jouaient sur la décote tous régimes confondus mais restaient hors du
    rapport durée acquise / durée requise du régime qui les accorde, ce qui
    amputait la mère de famille de la part que la MDA est censée lui rendre.
    """
    commun = dict(annee_naissance=1975, sexe="F",
                  affiliation="salarie_prive_non_cadre",
                  age_debut=30, age_liquidation=64)
    sans = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(**commun, nombre_enfants=0))
    avec = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(**commun, nombre_enfants=2))

    base_sans = next(p for p in sans.pensions_par_regime
                     if p.regime == "regime_general")
    base_avec = next(p for p in avec.pensions_par_regime
                     if p.regime == "regime_general")
    assert avec.trimestres_valides == sans.trimestres_valides + 16
    # La carrière est trop courte pour le taux plein : les seize trimestres
    # relèvent le taux ET la proratisation, et la pension de base monte plus
    # que du seul effet de décote.
    assert base_avec.montant > base_sans.montant
    assert "/" in base_avec.detail


def test_les_trimestres_pour_enfants_suivent_la_date_le_sexe_et_le_regime(simulateur):
    """Huit trimestres par enfant, à tout le monde et de tout temps : c'est ce
    que le module servait, et le droit n'en a jamais servi autant.

    La majoration de durée d'assurance naît en 1972 à un an par enfant, passe à
    deux ans en 1975, et va à la mère. La fonction publique ne l'applique pas :
    elle a sa bonification, un an par enfant né avant 2004 et deux trimestres
    pour les enfants nés depuis. Un père de trois enfants recevait douze
    trimestres — trois ans de durée d'assurance — que la loi ne lui a jamais
    donnés.
    """
    def trimestres(**kw):
        reglages = dict(affiliation="salarie_prive_non_cadre", age_debut=30,
                        age_liquidation=60, nombre_enfants=2, sexe="F")
        reglages.update(kw)
        carriere = simulateur.carriere_simple(**reglages)
        resultat = simulateur.scenario_actuel.calculer(carriere)
        sans = simulateur.scenario_actuel.calculer(
            simulateur.carriere_simple(**{**reglages, "nombre_enfants": 0})
        )
        return resultat.trimestres_valides - sans.trimestres_valides

    # La MDA se lit à l'ANNÉE DE LIQUIDATION : rien avant la loi Boulin, un an
    # par enfant jusqu'en 1974, deux ans ensuite.
    assert trimestres(annee_naissance=1910) == 0     # liquidation en 1970
    assert trimestres(annee_naissance=1913) == 8     # en 1973, 4 par enfant
    assert trimestres(annee_naissance=1920) == 16    # en 1980, 8 par enfant
    assert trimestres(annee_naissance=1960) == 16

    # Elle va à la mère : l'attribution par défaut des quatre trimestres
    # d'éducation ouverts en 2010 est la sienne, faute d'accord des parents.
    assert trimestres(annee_naissance=1960, sexe="H") == 0

    # La fonction publique sert sa propre bonification, lue à l'année de
    # naissance de l'enfant — présumé né aux trente ans de sa mère.
    fonctionnaire = dict(affiliation="fonctionnaire_etat")
    assert trimestres(annee_naissance=1960, **fonctionnaire) == 8   # nés en 1990
    assert trimestres(annee_naissance=1985, **fonctionnaire) == 4   # nés en 2015

    # Les régimes alignés appliquent les règles familiales du régime général
    # (article L. 634-2), ce que leur fiche ne disait pas.
    assert trimestres(annee_naissance=1950, affiliation="artisan") == 16


def test_les_trimestres_pour_enfants_nomment_le_dispositif_qui_les_accorde(simulateur):
    """La cascade doit dire ce qu'elle applique : la fonction publique ne sert
    pas une MDA, mais une bonification, et le montant n'est pas le même."""
    commun = dict(annee_naissance=1960, sexe="F", age_debut=30,
                  age_liquidation=62, nombre_enfants=3)
    privee = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(affiliation="salarie_prive_non_cadre", **commun))
    publique = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(affiliation="fonctionnaire_etat", **commun))

    def avantage(resultat):
        return next(a for a in resultat.avantages_appliques
                    if a.code == "majoration_duree_assurance")

    assert avantage(privee).libelle == "Majoration de durée d'assurance"
    assert "24 trimestres" in avantage(privee).detail
    assert avantage(publique).libelle == "Bonification pour enfants"
    assert "12 trimestres" in avantage(publique).detail


def test_la_loi_boulin_ne_visait_que_les_meres_de_deux_enfants(simulateur):
    """Le seuil de trois enfants du projet a été abaissé à deux au débat, pas à
    un : jusqu'en 1974, une mère d'un enfant unique n'avait droit à rien."""
    def trimestres(nombre_enfants, annee_naissance):
        commun = dict(annee_naissance=annee_naissance, sexe="F",
                      affiliation="salarie_prive_non_cadre",
                      age_debut=30, age_liquidation=60)
        avec = simulateur.scenario_actuel.calculer(
            simulateur.carriere_simple(**commun, nombre_enfants=nombre_enfants))
        sans = simulateur.scenario_actuel.calculer(
            simulateur.carriere_simple(**commun, nombre_enfants=0))
        return avec.trimestres_valides - sans.trimestres_valides

    # Liquidation en 1973, sous la loi Boulin.
    assert trimestres(1, 1913) == 0
    assert trimestres(2, 1913) == 8
    # Liquidation en 1980 : la loi du 3 janvier 1975 sert dès le premier enfant.
    assert trimestres(1, 1920) == 8


def test_la_surcote_parentale_recompense_l_annee_imposee_par_la_reforme_de_2023(
        simulateur):
    """L'avantage familial le plus récent, et le modèle l'ignorait.

    La loi du 14 avril 2023 a reculé l'âge légal à 64 ans : qui avait sa durée
    requise à 63 ans s'est vu imposer une année de travail de plus qui ne lui
    rapportait rien, la surcote ordinaire ne comptant qu'au-delà de l'âge légal.
    L'article L. 351-1-2-1 la paie 1,25 % par trimestre, quatre au plus, à qui
    détient un trimestre de majoration de durée d'assurance pour enfants.
    """
    def surcote(**kw):
        reglages = dict(annee_naissance=1969, sexe="F",
                        affiliation="salarie_prive_non_cadre",
                        age_debut=18, age_liquidation=64, nombre_enfants=2)
        reglages.update(kw)
        resultat = simulateur.scenario_actuel.calculer(
            simulateur.carriere_simple(**reglages))
        return next((a for a in resultat.avantages_appliques
                     if a.code == "surcote_parentale"), None)

    # Génération 1969 : âge légal 64 ans, donc quatre trimestres entre 63 et 64.
    # (C'était la génération 1968 avant la suspension de 2026, qui lui laisse
    # 63 ans et 9 mois, donc trois trimestres.)
    acquise = surcote()
    assert acquise is not None
    assert "4 trimestres" in acquise.detail and "5.00%" in acquise.detail
    assert "3 trimestres" in surcote(annee_naissance=1968).detail

    # Sans trimestre pour enfants, pas de surcote parentale : c'est ce trimestre
    # qui ouvre le droit, et il va par défaut à la mère.
    assert surcote(sexe="H") is None
    assert surcote(nombre_enfants=0) is None

    # Sans la durée requise à 63 ans, pas de surcote parentale non plus.
    assert surcote(age_debut=30) is None

    # Avant le 1er septembre 2023, le dispositif n'existe pas.
    assert surcote(annee_naissance=1955) is None

    # Génération 1958 : l'âge légal est de 62 ans, la fenêtre 63 → âge légal est
    # vide, et la surcote ordinaire prend seule le relais.
    assert surcote(annee_naissance=1958) is None


def test_la_surcote_est_passee_a_1_25_pour_cent_au_1er_janvier_2009(simulateur):
    """La fiche servait 0,75 % jusqu'en 2010, la loi 1,25 % depuis 2009 — pour
    les trimestres accomplis depuis 2009, les autres gardant leur taux.

    Le taux de la loi Fillon a été relevé par la loi de financement de la
    sécurité sociale pour 2009 : deux années de liquidations recevaient ici une
    surcote deux tiers trop faible. Puis le modèle a appliqué le taux de
    l'année du départ à tous les trimestres ; il lit maintenant le taux à la
    date de chacun.
    """
    def taux(annee_liquidation):
        carriere = simulateur.carriere_simple(
            annee_naissance=annee_liquidation - 62, sexe="H",
            affiliation="salarie_prive_non_cadre", age_debut=18,
            age_liquidation=62,
        )
        resultat = simulateur.scenario_actuel.calculer(carriere)
        return next(p.detail for p in resultat.pensions_par_regime
                    if p.regime == "regime_general")

    # Le barème est DATÉ, trimestre par trimestre (D. 351-1-4, circulaire Cnav
    # 2018-04) : la période de référence part du trimestre civil qui suit
    # l'âge légal — sept trimestres pour qui part à soixante-deux ans, né en
    # janvier —, et chaque trimestre garde le taux en vigueur quand il a été
    # accompli. Parti en janvier 2009 : quatre trimestres à 0,75 % puis trois
    # à 1 % (barème de 2007-2008), 6 %. Parti en janvier 2010 : trois de 2008
    # à 0,75 % et quatre de 2009 à 1,25 %, 7,25 %. Le modèle servait 8 × 0,75 %
    # jusqu'en 2010 ; puis 8 × 1,25 % à tous, y compris aux trimestres de 2008.
    assert "taux 53.000%" in taux(2008)
    assert "taux 53.000%" in taux(2009)
    assert "taux 53.625%" in taux(2010)


def test_le_bareme_2007_de_la_surcote_majore_au_dela_de_65_ans(simulateur):
    """L'âge du barème de 2007-2008 n'est écrit nulle part dans les données.

    `surcote_baremes.csv` porte les taux et un DRAPEAU, `apres_65_ans` : le
    seuil lui-même — soixante-cinq ans — ne vit que dans une constante du
    moteur, et `limites.md` l'annonce au lecteur. Ce test est ce qui la tient :
    il ne juge pas le calcul, que les tests voisins couvrent, mais le fait que
    le barème et le moteur parlent du même âge. Le changer d'un côté sans
    l'autre échoue ici, et la prose qui le cite s'appuie sur ce nom.
    """
    from retraite_notionnelle.scenarios.actuel import ScenarioActuel

    assert ScenarioActuel.SURCOTE_AGE_MAJORE == 65

    chemin = (RACINE_DONNEES / "reference" / "legislation"
              / "surcote_baremes.csv")
    with chemin.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        bareme = [l for l in csv.DictReader(lignes)
                  if l["bareme"] == "regime_general" and l["debut"] == "2007"]
    majores = [l for l in bareme if l["apres_65_ans"] == "1"]
    assert [l["taux"] for l in majores] == ["0.0125"], (
        "le barème de 2007-2008 doit porter une ligne, et une seule, pour les "
        "trimestres acquis au-delà de l'âge majoré")
    assert {l["taux"] for l in bareme if l not in majores} == {"0.0075", "0.0100"}


def test_la_surcote_parentale_se_cumule_avec_la_surcote_ordinaire(simulateur):
    """Les deux ne comptent pas les mêmes trimestres : l'une entre 63 ans et
    l'âge légal, l'autre au-delà. Elles s'ajoutent sans se recouvrir."""
    commun = dict(annee_naissance=1969, sexe="F",
                  affiliation="salarie_prive_non_cadre",
                  age_debut=18, nombre_enfants=2)
    tardive = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(**commun, age_liquidation=67))
    base = next(p for p in tardive.pensions_par_regime
                if p.regime == "regime_general")
    # Taux plein majoré de la surcote ordinaire — onze trimestres civils
    # entiers entre 64 et 67 ans, celui de l'anniversaire ne comptant pas
    # (D. 351-1-4) —, puis surcote parentale de 5 % par-dessus.
    assert "taux 56.875%" in base.detail
    assert "surcote parentale 5.00%" in base.detail


# -- régimes que le barème en points fait sortir du rendement instantané -----


def test_le_regime_de_base_des_liberaux_est_calcule_en_points(simulateur):
    """525 points au plafond, 25 sur la seconde tranche : c'est un barème.

    Le régime n'attribue pas un nombre de points proportionnel à la cotisation
    mais un nombre PLAFONNÉ de points par tranche. C'est cette règle — et non
    un prix d'achat, que la caisse ne publie pas — qui convertit le revenu en
    droits, et c'est elle qui manquait au moteur.
    """
    tranches = simulateur.catalogue["cnavpl"].periodes_actives(2020)
    assert [p.points_maximum for p in tranches] == [525.0, 25.0]
    assert [p.assiette for p in tranches] == ["plafonnee", "plafonnee_5_pass"]

    carriere = simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="profession_liberale",
        age_debut=27, age_liquidation=66, niveau_salaire=2.5,
    )
    pension = next(p for p in simulateur.scenario_actuel.calculer(
        carriere).pensions_par_regime if p.regime == "cnavpl")
    assert "points × valeur de service" in pension.detail

    # Un revenu au-dessus du plafond n'ouvre pas plus de 525 points par an sur
    # la première tranche : c'est tout l'objet du plafonnement.
    riche = simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="profession_liberale",
        age_debut=27, age_liquidation=66, niveau_salaire=8.0,
    )
    # La formule s'ouvre par une parenthèse quand un coefficient d'anticipation
    # multiplie la somme de ses termes : elle se retire avant de lire le nombre.
    points_riche = float(next(p for p in simulateur.scenario_actuel.calculer(
        riche).pensions_par_regime if p.regime == "cnavpl"
    ).detail.split(" points")[0].lstrip("(").replace(",", ""))
    annees = 66 - 27
    assert points_riche < 550 * annees


def test_la_complementaire_agricole_ouvre_cent_points_a_l_assiette_minimale(simulateur):
    """1 820 SMIC cotisés valent 100 points, et l'assiette ne descend pas plus bas.

    Le nombre de points ne dépend pas du taux de cotisation : c'est le barème
    qui est publié, pas le prix d'achat — et c'est ce qui débloque le calcul,
    la valeur d'achat du point de RCO restant introuvable.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="exploitant_agricole",
        age_debut=20, age_liquidation=64, niveau_salaire=0.2,
    )
    pension = next(p for p in simulateur.scenario_actuel.calculer(
        carriere).pensions_par_regime if p.regime == "msa_rco")
    points = float(pension.detail.split(" points")[0].replace(",", ""))
    # 2003 à 2023 inclus, cent points par an au minimum.
    assert points == pytest.approx(100 * 21, rel=0.01)
    assert pension.montant > 0


# -- minimum contributif, désormais sourcé dans le code ----------------------


def test_le_minimum_contributif_distingue_le_montant_majore(simulateur):
    """Deux montants, pas un : le majoré vaut près d'un cinquième de plus.

    Le majoré ne récompense que les périodes COTISÉES. Le modèle servait le
    montant de base à tout le monde — c'est-à-dire le plus faible des deux, et
    précisément pas celui qui s'applique à la carrière complète que le minimum
    est fait de protéger.
    """
    minimum = simulateur.scenario_actuel.minimum_contributif
    base, majore, plafond, _ = minimum.valeurs(2025)

    assert majore > base * 1.15

    # Les montants publiés par les caisses pour 2025 : 8 972 € et 10 721 €
    # par an. L'ancre du code, revalorisée sur le SMIC, doit les retrouver.
    assert base == pytest.approx(8972.28, rel=0.01)
    assert majore == pytest.approx(10720.68, rel=0.01)
    assert plafond == pytest.approx(16738.32, rel=0.01)


def test_le_minimum_contributif_est_revalorise_sur_le_smic(simulateur):
    """Le SMIC, et non les prix : c'est ce que la loi dit depuis 2014 et 2023.

    L'index ne dépend pas de l'ancre mais de l'ANNÉE TRAVERSÉE. Prendre celui
    de l'ancre appliquerait à quinze ans de revalorisations une règle que la
    loi n'a introduite qu'en 2023.
    """
    minimum = simulateur.scenario_actuel.minimum_contributif
    macro = simulateur.macro

    # Le plafond bascule sur le SMIC en 2014. Une année qui n'a pas de montant
    # connu se projette donc sur le SMIC depuis cette ancre — et le SMIC monte
    # plus vite que les prix.
    ancre, _ = minimum._revalorise("plafond_ecretement", 2014)
    porte, _ = minimum._revalorise("plafond_ecretement", 2018)
    assert porte == pytest.approx(ancre * macro.coefficient_smic(2014, 2018))
    assert porte > ancre * macro.coefficient_prix(2014, 2018)

    # 2025, lui, a un montant connu : aucune projection ne s'y applique.
    assert minimum._revalorise("plafond_ecretement", 2025)[0] == pytest.approx(
        1394.86 * 12
    )

    # Les deux minima ne basculent qu'en 2023. Une année antérieure se
    # revalorise donc sur les prix, depuis l'ancre de 2007.
    depuis_2007, _ = minimum._revalorise("montant_base", 2007)
    en_2012, _ = minimum._revalorise("montant_base", 2012)
    assert en_2012 == pytest.approx(depuis_2007 * macro.coefficient_prix(2007, 2012))


def test_les_montants_reellement_servis_priment_sur_toute_projection(simulateur):
    """Ce que les caisses ont payé passe avant ce que le modèle calcule.

    Le fichier porte deux sortes de valeurs : les ancres du code, certifiées,
    et les montants réellement servis, transcrits de leur publication. Les
    secondes ne sont que `haute` — ce sont des transcriptions — et elles
    l'emportent pourtant, parce qu'une valeur transcrite qui dit vrai vaut
    mieux qu'une valeur calculée qui dit faux.
    """
    minimum = simulateur.scenario_actuel.minimum_contributif

    # Réponse du ministère à la question écrite n° 32630 (Assemblée nationale) :
    # 642,93 €/mois en 2020, majoré à 702,55 €, plafond 1 191,57 € — que les
    # circulaires Cnav transcrites par OpenFisca-France-Pension recoupent à
    # quelques centimes près, douze mensualités arrondies contre un annuel.
    servis = {
        2020: (642.93 * 12, 702.55 * 12, 1191.57 * 12),
        2024: (733.03 * 12, 876.13 * 12, 1394.86 * 12),
        2025: (747.69 * 12, 893.39 * 12, 1394.86 * 12),
    }
    for annee, (base, majore, plafond) in servis.items():
        assert minimum.valeurs(annee)[0] == pytest.approx(base), annee
        assert minimum.valeurs(annee)[1] == pytest.approx(majore), annee
        assert minimum.valeurs(annee)[2] == pytest.approx(plafond), annee


def test_une_reforme_ne_glisse_pas_dans_le_passe(simulateur):
    """La projection part de la valeur EN VIGUEUR, jamais d'une postérieure.

    La réforme du 14 avril 2023 a relevé le minimum majoré de plus de 30 %.
    Ramener cette valeur en arrière, comme le faisait la règle de l'ancre la
    plus proche, surestimait de 7,6 % le montant de 2020 — celui-là même que
    l'État a rappelé dans sa réponse à une question écrite.
    """
    minimum = simulateur.scenario_actuel.minimum_contributif
    ancres = sorted(a for (mesure, a) in minimum._table if mesure == "montant_majore")
    assert ancres[0] == 2007 and 2023 in ancres

    # 2015 n'est pas au fichier : il est projeté depuis l'ancre de 2007, donc
    # reste très en dessous du montant d'après réforme.
    projete, _ = minimum._revalorise("montant_majore", 2015)
    avant_reforme = minimum._table[("montant_majore", 2007)][0]
    apres_reforme = minimum._table[("montant_majore", 2023)][0]
    assert avant_reforme < projete < apres_reforme * 0.9

    # Et une année antérieure à toute ancre se projette depuis la première.
    ancien, _ = minimum._revalorise("montant_majore", 1990)
    assert ancien < avant_reforme


# -- mortalité observée avant 1986 -------------------------------------------


def test_les_quotients_observes_remontent_avant_eurostat(simulateur):
    """Eurostat s'arrête à 1986 ; l'INED, lui, remonte au XIXe siècle.

    `docs/limites.md` tenait la Human Mortality Database pour la seule source à
    remonter plus haut, et donc la série pour hors de portée puisqu'elle exige
    une inscription. Les tables de Vallin et Meslé, que l'INED sert librement,
    la remplacent : le modèle a désormais de vrais quotients là où il n'avait
    que sa loi de Gompertz-Makeham.
    """
    quotients = simulateur.mortalite._quotients_observes
    assert quotients is not None

    annees = sorted({annee for annee, _ in quotients})
    assert annees[0] <= 1899
    assert 1950 in annees and 1985 in annees and 2020 in annees

    # Avant 1986, les âges vont jusqu'à 104 ans : le raccord paramétrique ne
    # sert plus sur ces années-là.
    ages_1950 = quotients[(1950, "H")]
    assert max(ages_1950) >= 104
    # Un quotient reste une probabilité, et croît en tendance avec l'âge.
    assert all(0 < q <= 1 for q in ages_1950.values())
    assert ages_1950[90] > ages_1950[60] > ages_1950[30]

    # Et le moteur les emploie : la survie d'une année couverte ne passe plus
    # par la loi paramétrique.
    attendu = 1.0 - ages_1950[70]
    assert simulateur.mortalite.survie_annuelle(70, 1950, "H") == pytest.approx(attendu)


# -- ce que le droit positif fait, et que l'étalon ne faisait pas -------------


def test_le_salaire_de_reference_ne_retient_que_les_annees_du_regime(simulateur):
    """Un régime ne liquide que ce qui lui a été déclaré.

    Le salaire de référence portait sur TOUTE la carrière, régime par régime
    confondu : un polypensionné passé de la fonction publique au privé
    liquidait sa pension civile sur son dernier salaire privé — pendant que le
    prorata de durée, lui, restait celui du régime. Le modèle rapportait donc
    une part de carrière publique à une assiette qui ne l'était pas.
    """
    from retraite_notionnelle.carriere import (
    AnneeCarriere,
    Carriere,
    LigneRelevee,
    Metier,
)

    publiques = [AnneeCarriere(annee=a, revenu=20_000.0,
                               affiliation="fonctionnaire_etat")
                 for a in range(1980, 2000)]
    privees = [AnneeCarriere(annee=a, revenu=60_000.0,
                             affiliation="salarie_prive_cadre")
               for a in range(2000, 2022)]

    melangee = simulateur.scenario_actuel.calculer(Carriere(
        annee_naissance=1960, sexe="H", lignes=publiques + privees,
        age_liquidation=62,
    ))
    publique_seule = simulateur.scenario_actuel.calculer(Carriere(
        annee_naissance=1960, sexe="H", lignes=list(publiques), age_liquidation=62,
    ))

    pension = {p.regime: p for p in melangee.pensions_par_regime}
    seule = {p.regime: p for p in publique_seule.pensions_par_regime}
    # Même assiette des deux côtés : la pension civile ne connaît que le
    # traitement des années passées dans la fonction publique — celui de 1999,
    # ramené à 2022 par le point d'indice, l'indice restant acquis.
    assert "SR 22,361.92 €" in pension["fonction_publique_etat"].detail
    assert "SR 22,361.92 €" in seule["fonction_publique_etat"].detail
    # Et le salaire annuel moyen du régime général ne connaît que les années
    # privées : y verser les années publiques, plus faibles, l'abaissait.
    privee_seule = simulateur.scenario_actuel.calculer(Carriere(
        annee_naissance=1960, sexe="H", lignes=list(privees), age_liquidation=62,
    ))
    reference = {p.regime: p for p in privee_seule.pensions_par_regime}
    assert (pension["regime_general"].detail.split("×")[0]
            == reference["regime_general"].detail.split("×")[0])


def test_les_annees_posterieures_a_la_liquidation_n_ouvrent_rien(simulateur):
    """On ne cotise pas après être parti.

    La boucle d'acquisition ne bornait pas à l'année de liquidation : des
    années postérieures achetaient des points et validaient des trimestres,
    ce qui annulait jusqu'à la décote de qui, précisément, part tôt.
    """
    from retraite_notionnelle.carriere import (
    AnneeCarriere,
    Carriere,
    LigneRelevee,
    Metier,
)

    avant = [AnneeCarriere(annee=a, revenu=40_000.0,
                           affiliation="salarie_prive_non_cadre")
             for a in range(1985, 2022)]
    apres = [AnneeCarriere(annee=a, revenu=40_000.0,
                           affiliation="salarie_prive_non_cadre")
             for a in range(2022, 2030)]

    borne = simulateur.scenario_actuel.calculer(Carriere(
        annee_naissance=1960, sexe="H", lignes=list(avant), age_liquidation=62))
    prolongee = simulateur.scenario_actuel.calculer(Carriere(
        annee_naissance=1960, sexe="H", lignes=avant + apres, age_liquidation=62))

    assert borne.pension_annuelle == pytest.approx(prolongee.pension_annuelle)
    assert borne.trimestres_valides == prolongee.trimestres_valides


def test_la_decote_de_la_fonction_publique_est_celle_de_l_article_l14(simulateur):
    """Ni le coefficient du privé, ni son âge d'annulation.

    Trois écarts, tous dans le même sens. La décote n'existe qu'à compter de
    2006 ; son coefficient monte d'un huitième de point par an, de 0,125 % en
    2006 à 1,25 % en 2015 ; et son âge d'annulation n'est pas un âge en propre
    mais la LIMITE D'ÂGE du grade, diminuée d'un nombre décroissant de
    trimestres jusqu'en 2020.
    """
    scenario = simulateur.scenario_actuel

    # 2005 : la décote n'existe pas encore dans la fonction publique.
    carriere = simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="fonctionnaire_etat",
        age_debut=25, age_liquidation=60, niveau_salaire=1.2,
    )
    resultat = scenario.calculer(carriere)
    assert resultat.trimestres_valides < resultat.trimestres_requis
    assert resultat.taux_liquidation == pytest.approx(0.75)

    # 2012 : coefficient de 0,875 %, âge d'annulation à la limite d'âge moins
    # huit trimestres — 63 ans et neuf mois pour la génération 1952, dont la
    # limite d'âge est de 65 ans et neuf mois.
    periode = simulateur.catalogue["fonction_publique_etat"].periode(2012)
    carriere = simulateur.carriere_simple(
        annee_naissance=1952, sexe="H", affiliation="fonctionnaire_etat",
        age_debut=25, age_liquidation=60, niveau_salaire=1.2,
    )
    coefficient, age_annulation, _ = scenario._decote(periode, carriere, 2012)
    assert coefficient == pytest.approx(0.00875)
    assert age_annulation == pytest.approx(65.75 - 2.0)

    # 2020 : la montée en charge est finie, l'âge d'annulation EST la limite
    # d'âge et le coefficient vaut 1,25 %.
    periode = simulateur.catalogue["fonction_publique_etat"].periode(2020)
    carriere = simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="fonctionnaire_etat",
        age_debut=25, age_liquidation=60, niveau_salaire=1.2,
    )
    coefficient, age_annulation, _ = scenario._decote(periode, carriere, 2020)
    assert coefficient == pytest.approx(0.0125)
    assert age_annulation == pytest.approx(67.0)


def test_le_marin_parti_avant_cinquante_cinq_ans_plafonne_a_vingt_cinq_annuites(
        simulateur):
    """L'âge y borne la durée, et c'est le seul régime où cela se voit.

    Article R. 13 du code des pensions de retraite des marins : « le maximum
    des annuités liquidables dans les pensions d'ancienneté dont la liquidation
    est demandée avant cinquante-cinq ans est fixé à vingt-cinq annuités ».
    Trente ans de mer ne valent donc pas 60 % du salaire forfaitaire à cinquante
    ans, mais 50 %.
    """
    scenario = simulateur.scenario_actuel
    avant = scenario.calculer(simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="marin",
        age_debut=20, age_liquidation=54, niveau_salaire=1.0,
    ))
    apres = scenario.calculer(simulateur.carriere_simple(
        annee_naissance=1960, sexe="H", affiliation="marin",
        age_debut=20, age_liquidation=55, niveau_salaire=1.0,
    ))
    assert "100/150" in avant.pensions_par_regime[0].detail
    assert "140/150" in apres.pensions_par_regime[0].detail
    # Le plafond ne joue que sous l'âge : la pension de cinquante-cinq ans vaut
    # plus de la moitié de plus, pour une année de mer de plus.
    assert apres.pension_annuelle > avant.pension_annuelle * 1.35


def test_le_marin_cotise_et_liquide_sur_le_forfait_de_sa_categorie(simulateur):
    """R. 11 : la pension est calculée sur « le salaire forfaitaire de la
    catégorie dans laquelle le marin a été classé », non sur sa paie.

    Un marin à 40 000 € en 2024 est de treizième catégorie, 41 467,86 € ; c'est
    ce forfait, et non les 40 000 €, que le compte notionnel reçoit et que le
    scénario 1 liquide.
    """
    from retraite_notionnelle.carriere import salaire_moyen_annuel

    # Profil plat : ce test vise la GRILLE des forfaits, et un marin à
    # 40 000 € doit tomber dans la treizième catégorie. Le défaut déformerait
    # ce salaire avec l'âge et le ferait changer de catégorie.
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H", affiliation="marin",
        age_debut=20, age_liquidation=60, niveau_salaire=1.0,
        profil_carriere="plat",
    )
    ligne = carriere.ligne(2024)
    forfait = simulateur.scenario_actuel.grilles.forfait(
        "marins", 2024, ligne.revenu_annualise,
        lambda a: salaire_moyen_annuel(simulateur.macro, a),
    )
    assert forfait[1] == 13
    assert forfait[0] == pytest.approx(41467.86)
    assert abs(ligne.revenu - 40000.0) < 2000.0
    cotisation = simulateur.constructeur.cotisation_annuelle(carriere, 2024)
    assert cotisation.assiette_retenue == pytest.approx(41467.86)
    actuel = simulateur.scenario_actuel.calculer(carriere)
    assert "150/150" in actuel.pensions_par_regime[0].detail
    # 2 % par annuité, 37,5 annuités : 75 % du forfait de la dernière année de
    # mer, 2024 — le départ tombe en janvier 2025 —, ramené en euros de 2025.
    forfait_depart = forfait[0] * simulateur.macro.coefficient_prix(2024, 2025)
    assert actuel.pension_annuelle == pytest.approx(0.75 * forfait_depart, rel=1e-6)


def test_les_points_carmf_d_avant_1991_valent_un_tiers_de_plus(simulateur):
    """Statuts de la CARMF : les points acquis avant la réforme de 1991 sont
    servis affectés d'un coefficient de 1,33."""
    conversions = simulateur.scenario_actuel.conversions_points
    assert conversions.echelle("carmf_complementaire", 1985, 2020)[0] == pytest.approx(1.333333)
    assert conversions.echelle("carmf_complementaire", 1995, 2020)[0] == 1.0
    assert conversions.echelle("carmf_complementaire", 1985, 1990)[0] == 1.0


def test_la_decote_des_regimes_speciaux_arrive_quatre_ans_apres(simulateur):
    """La réforme de 2008 leur donne la décote de la fonction publique, en 2010.

    Le V des décrets de réforme est écrit mot pour mot à l'identique dans les
    six régimes concernés : « le coefficient de minoration […] n'est applicable
    qu'aux personnes remplissant les conditions […] à compter du 1er juillet
    2010 […] il est fixé par trimestre manquant à un dixième du taux prévu ».
    Servir 1,25 % dès 2009, comme le faisaient les fiches, c'est décoter dix
    fois trop — et retirer un quart de la pension au lieu d'un quarantième.

    Et le barème se lit à l'année où l'assuré RÉUNIT LES CONDITIONS — l'âge
    d'ouverture du régime —, non à celle du départ : c'est la lettre du texte,
    et c'est ce que la confrontation de la pension civile à
    OpenFisca-France-Pension a fait voir. Chaque contrôle prend donc l'agent
    dont le droit s'ouvre l'année visée.
    """
    scenario = simulateur.scenario_actuel

    def agent(annee_naissance: int):
        return simulateur.carriere_simple(
            annee_naissance=annee_naissance, sexe="H", affiliation="agent_sncf",
            age_debut=25, age_liquidation=55, niveau_salaire=1.2,
        )

    # 2009 : le régime n'a pas encore de décote — droit ouvert à 50 ans en 2009.
    periode = simulateur.catalogue["sncf"].periode(2009)
    coefficient, _, _ = scenario._decote(periode, agent(1959), 2009)
    assert coefficient is None

    # Un droit ouvert en 2005 n'en acquiert pas une parce que le départ a lieu
    # en 2012 : les conditions étaient réunies avant le 1er juillet 2010.
    periode = simulateur.catalogue["sncf"].periode(2012)
    coefficient, _, _ = scenario._decote(periode, agent(1955), 2012)
    assert coefficient is None

    # Droit ouvert en 2012 : deux dixièmes du taux plein, soit 0,25 % — la
    # marche du 1er juillet 2011, que la table porte au millésime suivant pour
    # ne jamais opposer à l'assuré plus que le droit. C'est le taux de la
    # fonction publique quatre ans plus tôt, et le septième de celui que la
    # fiche servait. L'âge d'annulation est l'âge de référence du régime,
    # 55 ans, diminué de quatorze trimestres.
    coefficient, age_annulation, _ = scenario._decote(periode, agent(1962), 2012)
    assert coefficient == pytest.approx(0.0025)
    assert age_annulation == pytest.approx(55.0 - 14.0 / 4.0)

    # 2025 : la montée en charge est finie. L'âge de référence est celui de la
    # période — et depuis le relèvement de la loi du 14 avril 2023, étalé par
    # génération aux pensions prenant effet en 2025 (décret n° 2023-967,
    # art. 37-1), il vaut cette année-là cinquante-deux ans et trois mois
    # d'ouverture, plus cinq ans. Un agent né en janvier 1973 les atteint en
    # avril 2025.
    periode = simulateur.catalogue["sncf"].periode(2025)
    coefficient, age_annulation, _ = scenario._decote(periode, agent(1973), 2025)
    assert coefficient == pytest.approx(0.0125)
    assert age_annulation == pytest.approx(57.25)


def test_l_age_d_annulation_du_ballet_de_l_opera_est_quarante_deux_ans(simulateur):
    """Le seul âge de référence qui ne soit pas l'âge d'ouverture plus cinq ans.

    Le II de l'article 14 du décret n° 68-382 déroge pour deux catégories :
    « toutefois, pour les artistes du ballet, l'âge de référence est fixé à
    42 ans et, pour les musiciens de l'orchestre, les chefs de chant et les
    pianistes, il est fixé à 62 ans ». Un danseur qui part à quarante ans se
    voit donc opposer huit trimestres de décote, non vingt.
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1980, sexe="F", affiliation="personnel_opera",
        age_debut=18, age_liquidation=40, niveau_salaire=1.0,
    )
    periode = simulateur.catalogue["opera_de_paris"].periode(2020)
    coefficient, age_annulation, _ = scenario._decote(periode, carriere, 2020)
    assert coefficient == pytest.approx(0.0125)
    assert age_annulation == pytest.approx(42.0)

    trimestres = scenario._trimestres_de_decote(
        periode, carriere, trimestres=88, requis=172, age_liquidation=40.0,
        age_annulation=age_annulation,
    )
    assert trimestres == 8


def test_le_taux_d_avant_1983_ne_depend_que_de_l_age(simulateur):
    """Le taux plein par la durée est une création de 1982.

    Le régime général servait 20 % à 60 ans, majorés de quatre points par année
    différée jusqu'à 40 % à 65 ans ; la loi Boulin a porté ces bornes à 25 % et
    50 %. Aucune durée, si longue fût-elle, n'ouvrait le taux plein avant
    l'âge — et le modèle servait pourtant le taux plein à tout âge.
    """
    scenario = simulateur.scenario_actuel

    def taux(naissance, age):
        return scenario.calculer(simulateur.carriere_simple(
            annee_naissance=naissance, sexe="H",
            affiliation="salarie_prive_non_cadre",
            age_debut=20, age_liquidation=age,
        )).taux_liquidation

    # Ordonnances de 1945 : 20 % à 60 ans, 40 % à 65.
    assert taux(1905, 60) == pytest.approx(0.20)
    assert taux(1905, 65) == pytest.approx(0.40)
    # Loi Boulin : 25 % à 60 ans, 50 % à 65 — malgré quarante ans de carrière.
    assert taux(1915, 60) == pytest.approx(0.25)
    assert taux(1915, 65) == pytest.approx(0.50)


def test_le_minimum_garanti_de_la_fonction_publique_est_servi(simulateur):
    """Le plancher de la fonction publique, déclaré mais jamais appliqué.

    Barème de l'article L. 17 : 57,5 % de la référence à quinze ans de
    services, 95 % à trente, la totalité à quarante. La référence est le
    traitement de l'indice majoré 227 au 1er janvier 2004 — 997,96 € par mois,
    soit exactement 227 fois le point d'indice de cette année-là — revalorisé
    comme les pensions depuis.
    """
    minimum = simulateur.scenario_actuel.minimum_garanti

    # 997,96 € est la valeur du traitement à l'indice majoré 227, celle que
    # l'article désigne comme référence. En 2004 le barème n'en était encore
    # qu'à l'indice 217 : la montée en charge court jusqu'en 2013.
    assert minimum.reference(2004)[0] / 12 == pytest.approx(
        997.96 * 217 / 227, rel=0.001)
    assert minimum.reference(2013)[0] / 12 > minimum.reference(2004)[0] / 12
    assert minimum.reference(2024)[0] / 12 == pytest.approx(1325.01, rel=0.001)
    assert minimum.reference(2025)[0] / 12 == pytest.approx(1354.16, rel=0.001)

    plein = minimum.reference(2025)[0]
    assert minimum.montant(2025, 15 * 4)[0] == pytest.approx(plein * 0.575)
    assert minimum.montant(2025, 30 * 4)[0] == pytest.approx(plein * 0.95)
    assert minimum.montant(2025, 40 * 4)[0] == pytest.approx(plein)
    assert minimum.montant(2025, 45 * 4)[0] == pytest.approx(plein)

    # Et il relève réellement une petite pension publique liquidée au taux
    # plein — ici par l'âge, la décote étant nulle à 67 ans.
    carriere = simulateur.carriere_simple(
        annee_naissance=1962, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=40, age_liquidation=67, niveau_salaire=0.5, part_primes=0.15,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    applique = {a.code: a.montant for a in resultat.avantages_appliques}
    assert applique["minimum_garanti"] > 0


def test_le_minimum_garanti_suppose_le_taux_plein_depuis_2011(simulateur):
    """La loi du 9 novembre 2010 l'a conditionné, et le modèle l'ignorait."""
    commun = dict(
        annee_naissance=1962, sexe="F", affiliation="fonctionnaire_etat",
        age_debut=40, niveau_salaire=0.5, part_primes=0.15,
    )
    decotee = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(age_liquidation=64, **commun))
    taux_plein = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(age_liquidation=67, **commun))

    assert all(a.code != "minimum_garanti" for a in decotee.avantages_appliques)
    assert any(a.code == "minimum_garanti" for a in taux_plein.avantages_appliques)


def test_le_droit_dit_si_la_liquidation_est_ouverte(simulateur):
    """Le modèle servait une pension à un âge où la loi n'en sert aucune.

    Un salarié du privé né en 1965 n'a pas le droit de liquider à 58 ans, sauf
    carrière longue — et la carrière longue exige d'avoir commencé tôt ET
    d'avoir la durée cotisée requise. Le montant reste calculé, parce qu'il
    faut comparer les trois scénarios sur la même carrière, mais le résultat
    dit désormais qu'il ne décrit aucune pension servie.
    """
    scenario = simulateur.scenario_actuel

    def ouverture(age_debut, age_liquidation):
        return scenario.calculer(simulateur.carriere_simple(
            annee_naissance=1965, sexe="H",
            affiliation="salarie_prive_non_cadre",
            age_debut=age_debut, age_liquidation=age_liquidation,
        ))

    tardif = ouverture(23, 60)
    assert tardif.liquidation_ouverte is False
    assert tardif.motif_ouverture == "non_ouverte"
    # 62 ans et 9 mois depuis la suspension de la réforme (LFSS 2026).
    assert tardif.age_ouverture_opposable == pytest.approx(62.75)

    # À l'âge légal de sa génération, elle l'est.
    legal = ouverture(23, 64)
    assert legal.liquidation_ouverte is True
    assert legal.motif_ouverture == "age_legal"

    # Entré à seize ans et fort de plus de trimestres cotisés que la durée
    # requise, le même assuré part à 60 ans : c'est la carrière longue.
    precoce = ouverture(16, 60)
    assert precoce.liquidation_ouverte is True
    assert precoce.motif_ouverture == "carriere_longue"
    assert precoce.age_ouverture_opposable == pytest.approx(60.0)

    # Mais pas à 58 ans : la durée cotisée n'y est pas encore.
    assert ouverture(16, 58).liquidation_ouverte is False


def test_l_avpf_porte_un_salaire_au_compte(simulateur):
    """Une période assimilée ne porte aucun salaire ; l'AVPF, si.

    C'est toute la différence, et le modèle ne la faisait pas : les années
    d'éducation d'un enfant validaient des trimestres sans jamais ajouter de
    salaire au compte, alors que la CNAF y cotise sur une assiette forfaitaire
    égale au SMIC. Le cas type « carrière interrompue » annonçait cette
    compensation sans que rien ne la calcule.
    """
    from retraite_notionnelle.donnees.chargement import (
        charger_periodes_non_travaillees,
    )

    motifs = charger_periodes_non_travaillees(
        simulateur.parametres.racine_donnees
    )
    assert motifs["education_enfant"].avpf is True
    assert motifs["chomage_indemnise"].avpf is False

    carriere = simulateur.carriere_simple(
        annee_naissance=1970, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=42, age_liquidation=64, niveau_salaire=1.2,
        profil_carriere="plat", nombre_enfants=2,
        interruptions={a: "education_enfant" for a in range(2014, 2019)},
    )
    interrompues = [l for l in carriere.lignes if l.revenu_avpf > 0]
    assert len(interrompues) == 5
    # L'assiette est le SMIC annuel : 1 820 heures au SMIC horaire de l'année.
    attendu = 1820.0 * simulateur.macro.smic_horaire(2014)
    assert interrompues[0].revenu_avpf == pytest.approx(attendu)

    # Sur une carrière de moins de vingt-cinq années portées au compte, ces
    # années au SMIC entrent dans la moyenne au lieu de la remplacer : le
    # salaire annuel moyen BAISSE. C'est la règle, et le modèle la montre.
    resultat = simulateur.scenario_actuel.calculer(carriere)
    applique = {a.code: a.montant for a in resultat.avantages_appliques}
    assert applique["avpf"] < 0


def test_le_minimum_vieillesse_complete_les_toutes_petites_pensions(simulateur):
    """L'ASPA, dernier plancher du système actuel, jamais servie jusqu'ici.

    Allocation différentielle : elle porte les ressources au barème d'une
    personne seule, 1 034,28 € par mois en 2025. Et elle ne s'ouvre qu'à
    65 ans, ce que le modèle respecte — il ne suit pas l'assuré au-delà de sa
    liquidation.
    """
    plafond = simulateur.scenario_actuel.minimum_vieillesse.plafond(2025)
    assert plafond[0] / 12 == pytest.approx(1034.28, rel=0.001)

    commun = dict(
        annee_naissance=1960, sexe="F", affiliation="salarie_prive_non_cadre",
        age_debut=50, niveau_salaire=0.5,
    )
    avant = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(age_liquidation=64, **commun))
    apres = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(age_liquidation=65, **commun))

    assert all(a.code != "minimum_vieillesse" for a in avant.avantages_appliques)
    applique = {a.code: a.montant for a in apres.avantages_appliques}
    assert applique["minimum_vieillesse"] > 0
    assert apres.pension_annuelle == pytest.approx(
        simulateur.scenario_actuel.minimum_vieillesse.plafond(2025)[0]
    )

    # Et le paramètre la retire d'un seul geste : ce n'est pas une pension.
    from retraite_notionnelle.simulateur import SCENARIOS_NOTIONNELS, Simulateur

    sans = Simulateur(simulateur.parametres.avec(
        minimum_vieillesse_dans_le_scenario_actuel=False
    ))
    depouillee = sans.scenario_actuel.calculer(
        sans.carriere_simple(age_liquidation=65, **commun))
    assert depouillee.pension_annuelle < apres.pension_annuelle


def test_la_garantie_minimale_de_points_agirc_est_servie(simulateur):
    """120 points par an, même quand la tranche B est nulle.

    Un cadre payé sous le plafond de la Sécurité sociale n'acquérait aucun
    point à l'Agirc, quand l'accord du 9 février 1988 lui en donnait 120 par
    an. La fiche du régime le déclarait ; le moteur ne le servait pas.
    """
    commun = dict(
        annee_naissance=1958, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=32, age_liquidation=64, profil_carriere="plat",
    )
    sous_plafond = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(niveau_salaire=0.8, **commun))
    agirc = {p.regime: p for p in sous_plafond.pensions_par_regime}["agirc"]

    # Vingt-neuf années cotisées de 1990 à 2018, toutes garanties.
    assert agirc.montant > 0
    # Les points s'affichent au centième depuis que la formule doit se
    # refaire : trente-quatre-cent-quatre-vingts, virgule zéro zéro.
    assert "3,480.00 points" in agirc.detail


def test_le_regime_de_base_des_avocats_est_forfaitaire(simulateur):
    """La pension de base d'un avocat ne dépend pas de son revenu.

    C'est la particularité du régime, et c'est ce qu'un compte notionnel
    supprime le plus radicalement. La fiche agrégeait pourtant la base et le
    complémentaire en un seul taux calculé au rendement instantané : la pension
    y était intégralement proportionnelle au revenu, exactement l'inverse de la
    règle. Depuis la scission, seul le complémentaire l'est.
    """
    commun = dict(
        annee_naissance=1975, sexe="H", affiliation="avocat",
        age_debut=25, age_liquidation=64, profil_carriere="fortement_ascendant",
    )
    modeste = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(niveau_salaire=0.8, **commun))
    aise = simulateur.scenario_actuel.calculer(
        simulateur.carriere_simple(niveau_salaire=4.0, **commun))

    base = {r.regime: r for r in modeste.pensions_par_regime}
    base_aise = {r.regime: r for r in aise.pensions_par_regime}
    assert base["cnbf"].montant == pytest.approx(base_aise["cnbf"].montant)
    assert "forfait" in base["cnbf"].detail
    # Le complémentaire, lui, suit le revenu.
    assert (base_aise["cnbf_complementaire"].montant
            > 4 * base["cnbf_complementaire"].montant)


def test_les_tranches_des_avocats_sont_en_euros_non_en_plafonds(simulateur):
    """La CNBF fixe ses tranches en euros et ne les indexe pas.

    42 507 € en 2023, en 2025 et en 2026, quand le plafond de la Sécurité
    sociale passait de 43 992 à 48 060 €. Les exprimer en plafonds, comme le
    fait le reste du catalogue, les ferait dériver d'année en année — d'où un
    champ écrit pour ce cas, et utilisable par tout régime qui ferait de même.
    """
    regime = simulateur.catalogue["cnbf_complementaire"]
    tranches = [p for p in regime.periodes_actives(2026)
                if p.borne_haute_euros is not None]
    assert len(tranches) == 5
    assert [p.borne_haute_euros for p in tranches] == [
        42507, 85014, 127521, 170028, 212535]
    assert [p.taux_cotisation_retraite for p in tranches] == [
        pytest.approx(t) for t in (0.07, 0.104, 0.122, 0.14, 0.158)]

    # Et les bornes restent en euros quel que soit le plafond de l'année.
    premiere = tranches[0]
    assert premiere.bornes_assiette_en_euros(48_060) == (0.0, 42507)
    assert premiere.bornes_assiette_en_euros(30_000) == (0.0, 42507)

    # Un régime ordinaire, lui, garde des bornes en plafonds.
    tranche_2 = next(p for p in simulateur.catalogue["agirc_arrco"]
                     .periodes_actives(2026) if p.assiette == "tranche_2")
    assert tranche_2.bornes_assiette_en_euros(48_060) == (48_060.0, 8 * 48_060.0)


def test_la_pension_ne_fait_plus_de_marche_au_milieu_de_l_annee(simulateur):
    """Deux mois d'écart déplaçaient la pension de six à sept pour cent.

    L'âge de liquidation était arrondi à l'année civile la plus proche : tout
    basculait entre 64 ans et 5 mois et 64 ans et 7 mois — une année entière de
    carrière gagnée ou perdue d'un coup, dans un sens pour le scénario 1, dans
    l'autre pour le scénario 3. La date étant désormais lue au mois, la pension
    progresse mois par mois.
    """
    from retraite_notionnelle.carriere import Carriere

    pensions = []
    for mois in range(12):
        carriere = Carriere.depuis_profil(
            1962, "H", "salarie_prive_cadre", 22, 64 + mois / 12,
            simulateur.macro, niveau_salaire=1.5, profil_carriere="plat",
        )
        pensions.append(
            simulateur.scenario_notionnel.retroactif(carriere).pension_annuelle
        )

    assert pensions == sorted(pensions)
    ecarts = [apres / avant - 1 for avant, apres in zip(pensions, pensions[1:])]
    # Aucun mois ne pèse plus de 1,5 % : la marche en valait plus de quatre à
    # lui seul, et elle tombait toujours au même endroit de l'année.
    assert max(ecarts) < 0.015
    # Douze mois de plus valent tout de même un gain net : les mois cotisés de
    # l'année du départ vont au compte, et le diviseur baisse.
    assert pensions[-1] / pensions[0] > 1.05


def test_les_generations_coupees_en_cours_d_annee_sont_lues_au_mois(simulateur):
    """La loi vise « les assurés nés à compter du 1er septembre 1961 ».

    Le modèle ne connaissait que l'année de naissance et opposait à toute la
    génération la valeur couvrant le plus de mois. L'approximation valait un
    trimestre d'âge légal et un trimestre de durée requise ; le mois de
    naissance la lève.
    """
    from retraite_notionnelle.carriere import Carriere

    def opposables(naissance, mois):
        carriere = Carriere.depuis_profil(
            naissance, "H", "salarie_prive_non_cadre", 20, 62.0,
            simulateur.macro, mois_naissance=mois,
        )
        resultat = simulateur.scenario_actuel.calculer(carriere)
        return resultat.age_ouverture_opposable, resultat.trimestres_requis

    # Loi du 9 novembre 2010 : 60 ans avant le 1er juillet 1951, 60 ans et
    # quatre mois à compter.
    assert opposables(1951, 6)[0] == pytest.approx(60.0)
    assert opposables(1951, 8)[0] == pytest.approx(60.33)
    # Loi du 14 avril 2023 : 62 ans et 168 trimestres avant le 1er septembre
    # 1961, 62 ans et trois mois et 169 trimestres à compter.
    assert opposables(1961, 8) == (pytest.approx(62.0), 168)
    assert opposables(1961, 10) == (pytest.approx(62.25), 169)
    # Une génération que nul texte ne coupe ne bouge pas avec le mois.
    assert opposables(1960, 2) == opposables(1960, 11)


def test_avant_l_asf_de_1983_l_abattement_se_lit_a_l_age_seul(simulateur):
    """Jusqu'à l'accord du 4 février 1983, l'Agirc et l'Arrco servaient le taux
    plein à soixante-cinq ans et abattaient toute anticipation, quelle que soit
    la durée. Une période sans durée requise porte ce droit : à soixante-deux
    ans, douze trimestres d'anticipation valent 0,88 même au taux plein du
    régime de base. Depuis 1983, la durée lue à la génération rend le taux
    plein dès soixante ans.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1920, sexe="H", affiliation="salarie_prive_cadre",
        age_debut=20, age_liquidation=62,
    )
    scenario = simulateur.scenario_actuel
    avant = simulateur.catalogue["agirc"].periode(1980)
    assert avant.duree_requise_trimestres is None
    assert not avant.duree_requise_par_generation
    assert scenario._abattement_points(
        avant, carriere, 168, 150, 62.0, 1982) == pytest.approx(0.88)

    apres = simulateur.catalogue["agirc"].periode(1984)
    assert apres.duree_requise_par_generation
    assert scenario._abattement_points(
        apres, carriere, 168, 150, 62.0, 1984) == pytest.approx(1.0)


def test_la_surcote_ircantec_suit_les_deux_taux_de_l_arrete(simulateur):
    """Le IV de l'article 16, taux par taux, sur une carrière écrite à la main.

    Son 1° majore de 0,75 % « par trimestre entier écoulé entre le
    soixante-cinquième anniversaire de l'assuré et la date d'entrée en
    jouissance » : du TEMPS, que rien ne conditionne. Son 2° majore de 0,625 %
    « par trimestre accompli » de durée cotisée au-delà de l'âge légal et de
    la durée requise, en deçà de ce même âge — et « en aucun cas une même
    période ne peut donner lieu à la fois » aux deux.
    """
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["ircantec"].periode(2012)
    assert periode.surcote_points == "ircantec"

    # Un agent né en 1945 — âge du taux plein 65 ans — qui liquide à 67 ans :
    # huit trimestres écoulés, et rien d'autre.
    carriere = simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="contractuel_public",
        age_debut=26, age_liquidation=67,
    )
    assert scenario._age_taux_plein(periode, carriere) == pytest.approx(65.0)
    assert scenario._abattement_points(
        periode, carriere, 164, 160, 67.0, 2012) == pytest.approx(1.06)

    # Le même, liquidé À l'âge du taux plein : le 1° ne donne rien, et le 2°
    # non plus — ses quatre trimestres de trop sont postérieurs à cet âge.
    assert scenario._abattement_points(
        periode, carriere, 164, 160, 65.0, 2010) == pytest.approx(1.0)


def test_la_surcote_ircantec_ne_paie_pas_deux_fois_la_meme_periode(simulateur):
    """Le 2° ne compte que ce que le 1° ne compte pas.

    Une carrière commencée à vingt ans atteint ses 160 trimestres à soixante,
    et tout ce qu'elle cotise ensuite est « accompli après l'âge et la limite
    prévus à l'article L. 351-1 ». Liquidée à soixante-cinq ans, elle reçoit
    vingt trimestres au 2° et rien au 1° ; liquidée deux ans plus tard, elle
    garde ces vingt trimestres — bornés par l'âge du taux plein — et reçoit
    huit trimestres de plus au 1°, non vingt-huit.
    """
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["ircantec"].periode(2012)
    carriere = simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="contractuel_public",
        age_debut=20, age_liquidation=67,
    )
    a_l_age_du_taux_plein = scenario._abattement_points(
        periode, carriere, 180, 160, 65.0, 2010)
    assert a_l_age_du_taux_plein == pytest.approx(1.0 + 0.00625 * 20)
    deux_ans_plus_tard = scenario._abattement_points(
        periode, carriere, 188, 160, 67.0, 2012)
    assert deux_ans_plus_tard == pytest.approx(1.0 + 0.00625 * 20 + 0.0075 * 8)


def test_la_surcote_ircantec_n_existe_pas_avant_2010(simulateur):
    """« À compter du 1er janvier 2010 », dit le paragraphe 4, et c'est ce qui
    coupe la fiche en deux au milieu de sa période 2009-2010. Une liquidation
    de 2009 ne reçoit rien ; la même, un an plus tard, reçoit la majoration
    entière. Aucun autre régime en points du catalogue ne porte CE barème-là :
    les neuf autres qui servent une majoration ont le leur, `regime_general`
    ou `par_age_seul`.
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1944, sexe="H", affiliation="contractuel_public",
        age_debut=26, age_liquidation=66,
    )
    avant = simulateur.catalogue["ircantec"].periode(2009)
    assert avant.surcote_points == "aucune"
    assert scenario._abattement_points(
        avant, carriere, 160, 160, 66.0, 2009) == pytest.approx(1.0)

    apres = simulateur.catalogue["ircantec"].periode(2010)
    assert apres.surcote_points == "ircantec"
    assert scenario._abattement_points(
        apres, carriere, 160, 160, 66.0, 2010) == pytest.approx(1.03)

    porteurs = {
        regime.code
        for regime in simulateur.catalogue
        for p in regime.periodes
        if p.surcote_points == "ircantec"
    }
    assert porteurs == {"ircantec"}, porteurs


def test_un_abattement_ircantec_ne_se_transforme_jamais_en_majoration(simulateur):
    """Abattu et majoré ne se rencontrent pas.

    Les deux majorations supposent l'une l'âge du taux plein dépassé, l'autre
    la durée requise dépassée : dans les deux cas, le coefficient
    d'anticipation est déjà revenu à 1. Une liquidation anticipée et
    incomplète reste donc abattue, et le barème de l'arrêté n'y ajoute rien.
    """
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["ircantec"].periode(2012)
    carriere = simulateur.carriere_simple(
        annee_naissance=1950, sexe="H", affiliation="contractuel_public",
        age_debut=30, age_liquidation=62,
    )
    assert scenario._abattement_points(
        periode, carriere, 128, 162, 62.0, 2012) < 1.0


# -- action 22 : la surcote des régimes en points ----------------------------


def _periode(simulateur, code, annee):
    return simulateur.catalogue[code].periode(annee)


def test_la_cnavpl_sert_la_surcote_du_regime_general(simulateur):
    """R. 643-8 : « au titre des périodes d'activité ayant donné lieu à
    cotisations à la charge de l'assuré accomplies à compter du 1er janvier
    2004 après l'âge prévu au premier alinéa de l'article L. 351-1 et au-delà
    de la limite mentionnée au deuxième alinéa du même article », 0,75 % par
    trimestre — et 1,25 % pour les trimestres accomplis à compter du
    1er septembre 2023, que la fiche applique aux liquidations de 2024.
    """
    scenario = simulateur.scenario_actuel
    periode = _periode(simulateur, "cnavpl", 2015)
    assert periode.surcote_points == "regime_general"
    # Né en 1953, entré à vingt-deux ans, parti à soixante-quatre : huit
    # trimestres cotisés au-delà de l'âge légal ET de la durée requise.
    carriere = simulateur.carriere_simple(
        annee_naissance=1953, sexe="H", affiliation="profession_liberale",
        age_debut=22, age_liquidation=64,
    )
    assert scenario._abattement_points(
        periode, carriere, 173, 165, 64.0, 2017) == pytest.approx(1.0 + 0.0075 * 8)
    # Le même, sans excédent de durée : rien.
    assert scenario._abattement_points(
        periode, carriere, 165, 165, 64.0, 2017) == pytest.approx(1.0)
    apres = _periode(simulateur, "cnavpl", 2024)
    assert apres.surcote_par_trimestre == pytest.approx(0.0125)


def test_la_carmf_majore_des_62_ans_puis_moins_apres_65_et_plus_rien_a_70(simulateur):
    """Article 15 des statuts depuis le 1er janvier 2017 : « 1,25 % par
    trimestre séparant le premier jour du trimestre civil suivant celui où le
    médecin atteint cet âge de la date d'effet de la retraite », « réduit à
    0,75 % par trimestre » après soixante-cinq ans, « sans pouvoir s'appliquer
    au-delà du premier jour du trimestre civil suivant le soixante-dixième
    anniversaire ». Ni durée ni cotisation : le temps seul.
    """
    scenario = simulateur.scenario_actuel
    periode = _periode(simulateur, "carmf_complementaire", 2020)
    assert periode.surcote_points == "par_age_seul"
    assert periode.decote_par_trimestre is None
    carriere = simulateur.carriere_simple(
        annee_naissance=1954, sexe="H", affiliation="medecin_liberal",
        age_debut=30, age_liquidation=66,
    )
    # Douze trimestres à 1,25 % de 62 à 65 ans, quatre à 0,75 % ensuite.
    assert scenario._abattement_points(
        periode, carriere, 144, 165, 66.0, 2020) == pytest.approx(1.0 + 0.0125 * 12 + 0.0075 * 4)
    # À soixante-douze ans, le compte s'arrête à soixante-dix : 15 % + 15 %.
    assert scenario._abattement_points(
        periode, carriere, 168, 165, 72.0, 2026) == pytest.approx(1.30)
    # À soixante-deux ans, rien — et pas de décote non plus, quelle que soit
    # la durée : c'est la retraite en temps choisi.
    assert scenario._abattement_points(
        periode, carriere, 100, 165, 62.0, 2016 + 1) == pytest.approx(1.0)
    # Avant 2017, le taux plein est à soixante-cinq ans, l'anticipation abat
    # 1,25 % par trimestre, et le différé se compte par années PLEINES.
    avant = _periode(simulateur, "carmf_complementaire", 2015)
    assert avant.surcote_pas_trimestres == 4
    assert scenario._abattement_points(
        avant, carriere, 140, 165, 66.5, 2015) == pytest.approx(1.05)
    assert scenario._abattement_points(
        avant, carriere, 140, 165, 63.0, 2015) == pytest.approx(0.90)
    # L'ASV suit les mêmes mots.
    asv = _periode(simulateur, "asv_conventionnes", 2020)
    assert scenario._abattement_points(
        asv, carriere, 144, 165, 66.0, 2020) == pytest.approx(1.0 + 0.0125 * 12 + 0.0075 * 4)


def test_la_cavec_majore_vingt_trimestres_au_plus_apres_65_ans(simulateur):
    """Article 13 des statuts : « une majoration de 0,75 % par trimestre plein
    de prorogation au-delà de cet âge, dans la limite maximale de 15 % » de
    2019 à 2025 ; 1,25 % et 25 % avant 2019 et depuis 2026. Le taux plein est
    « à 65 ans », sans durée.
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1953, sexe="H", affiliation="expert_comptable",
        age_debut=25, age_liquidation=67,
    )
    periode = _periode(simulateur, "cavec_complementaire", 2020)
    assert periode.age_taux_plein == 65.0 and periode.duree_requise_trimestres is None
    assert scenario._abattement_points(
        periode, carriere, 120, 165, 67.0, 2020) == pytest.approx(1.06)
    assert scenario._abattement_points(
        periode, carriere, 120, 165, 71.0, 2024) == pytest.approx(1.15)
    assert scenario._abattement_points(
        _periode(simulateur, "cavec_complementaire", 2027), carriere, 120, 165, 67.0, 2027,
    ) == pytest.approx(1.10)
    assert scenario._abattement_points(
        _periode(simulateur, "cavec_complementaire", 2000), carriere, 120, 165, 67.0, 2000,
    ) == pytest.approx(1.0)


def test_la_carpimko_majore_depuis_l_age_du_taux_plein_lu_a_la_generation(simulateur):
    """Article 12 ter, inséré par l'arrêté du 31 juillet 2015 : « 1,25 % par
    trimestre civil entier d'ajournement postérieur à l'âge du taux plein dans
    la limite de vingt trimestres ». Rien avant l'arrêté.
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1956, sexe="F", affiliation="auxiliaire_medical",
        age_debut=25, age_liquidation=68,
    )
    periode = _periode(simulateur, "carpimko_complementaire", 2024)
    assert scenario._age_taux_plein(periode, carriere) == pytest.approx(67.0)
    assert scenario._abattement_points(
        periode, carriere, 172, 169, 68.0, 2024) == pytest.approx(1.05)
    assert scenario._abattement_points(
        periode, carriere, 172, 169, 73.0, 2029) == pytest.approx(1.25)
    assert scenario._abattement_points(
        _periode(simulateur, "carpimko_complementaire", 2014), carriere, 172, 169, 68.0, 2014,
    ) == pytest.approx(1.0)


def test_la_cavp_majore_trois_ans_au_plus_a_un_demi_pour_cent(simulateur):
    """Article 12 des statuts (arrêté du 23 juin 2011) : « majorée lorsqu'elle
    est liquidée au-delà de l'âge permettant d'obtenir une retraite à taux
    plein et jusqu'à cet âge augmenté de 3 ans […]. Cette majoration est égale
    à 0,5 % par trimestre. »
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1956, sexe="H", affiliation="pharmacien",
        age_debut=25, age_liquidation=69,
    )
    periode = _periode(simulateur, "cavp_complementaire", 2025)
    assert scenario._abattement_points(
        periode, carriere, 176, 169, 69.0, 2025) == pytest.approx(1.04)
    assert scenario._abattement_points(
        periode, carriere, 176, 169, 72.0, 2028) == pytest.approx(1.06)


def test_la_cprn_majore_un_demi_pour_cent_jusqu_a_70_ans_puis_un_pour_cent_sans_borne(simulateur):
    """Arrêté du 16 décembre 2013 : « 0,5 % par trimestre au-delà de l'âge du
    taux plein, jusqu'à l'âge de 70 ans » ; arrêté du 29 novembre 2023, en
    vigueur le 1er janvier 2024 : « 1 % » et « fin d'activité ».
    """
    scenario = simulateur.scenario_actuel
    # Né en 1956 : l'âge du taux plein, lu à la génération, est 67 ans.
    carriere = simulateur.carriere_simple(
        annee_naissance=1956, sexe="H", affiliation="notaire",
        age_debut=28, age_liquidation=72,
    )
    avant = _periode(simulateur, "cprn_complementaire", 2020)
    assert avant.surcote_age_maximum == 70.0
    assert scenario._abattement_points(
        avant, carriere, 176, 169, 68.0, 2023) == pytest.approx(1.02)
    assert scenario._abattement_points(
        avant, carriere, 176, 169, 72.0, 2023) == pytest.approx(1.06)
    apres = _periode(simulateur, "cprn_complementaire", 2025)
    assert apres.surcote_age_maximum is None
    assert scenario._abattement_points(
        apres, carriere, 176, 169, 72.0, 2028) == pytest.approx(1.20)
    assert scenario._abattement_points(
        _periode(simulateur, "cprn_complementaire", 2010), carriere, 176, 165, 72.0, 2010,
    ) == pytest.approx(1.0)


def test_la_cipav_majore_par_annees_pleines_a_qui_a_trente_ans_de_caisse(simulateur):
    """Fiche pratique 2022 : « 5 % par année pleine de différé si, à 67 ans,
    vous réunissez 30 années d'affiliation à la Cipav ». Une année et demie
    vaut une année ; vingt-neuf ans de caisse ne valent rien.
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1956, sexe="F", affiliation="profession_liberale",
        age_debut=25, age_liquidation=68,
    )
    periode = _periode(simulateur, "cipav_complementaire", 2024)
    assert periode.surcote_affiliation_minimale_trimestres == 120
    assert scenario._abattement_points(
        periode, carriere, 172, 169, 68.5, 2024, trimestres_regime=160,
    ) == pytest.approx(1.05)
    assert scenario._abattement_points(
        periode, carriere, 172, 169, 69.0, 2025, trimestres_regime=160,
    ) == pytest.approx(1.10)
    assert scenario._abattement_points(
        periode, carriere, 172, 169, 69.0, 2025, trimestres_regime=116,
    ) == pytest.approx(1.0)


def test_les_exploitants_agricoles_ont_la_surcote_du_regime_general(simulateur):
    """D. 732-42 : la durée « accomplie à compter du 1er janvier 2004, au-delà
    de l'âge fixé à l'article L. 732-18 et au-delà de la durée minimale prévue
    à l'article L. 732-25 », 1,25 % par trimestre depuis 2009 — servie, enfin,
    par la branche en points qui liquide ce régime mixte.
    """
    scenario = simulateur.scenario_actuel
    carriere = simulateur.carriere_simple(
        annee_naissance=1953, sexe="H", affiliation="exploitant_agricole",
        age_debut=22, age_liquidation=64,
    )
    periode = _periode(simulateur, "msa_non_salaries", 2017)
    assert periode.type_calcul == "mixte" and periode.surcote_points == "regime_general"
    assert scenario._abattement_points(
        periode, carriere, 173, 165, 64.0, 2017) == pytest.approx(1.0 + 0.0125 * 8)


def test_toute_surcote_ecrite_par_une_fiche_en_points_est_servie(simulateur):
    """Le garde-fou qui manquait : une période en points qui porte un taux de
    surcote porte aussi le barème qui le lit, et réciproquement. C'est ce
    test qui aurait signalé, sans qu'on le cherche, les neuf fiches dont la
    surcote n'était jamais servie.
    """
    orphelines = [
        (regime.code, p.debut)
        for regime in simulateur.catalogue
        for p in regime.periodes
        if p.type_calcul in ("points", "mixte")
        and bool(p.surcote_par_trimestre) != (p.surcote_points not in ("aucune", "ircantec"))
        and not (p.surcote_points == "ircantec" and not p.surcote_par_trimestre)
    ]
    assert not orphelines, orphelines
    servies = {
        regime.code
        for regime in simulateur.catalogue
        for p in regime.periodes
        if p.surcote_points in ("regime_general", "par_age_seul")
    }
    assert servies == {
        "cnavpl", "msa_non_salaries", "carmf_complementaire", "asv_conventionnes",
        "cavec_complementaire", "cipav_complementaire", "carpimko_complementaire",
        "cavp_complementaire", "cprn_complementaire",
    }, servies



# -- catégorie active et pension militaire -----------------------------------


def _pension_actuelle(simulateur, statut, generation, age, age_debut=22):
    carriere = simulateur.carriere_simple(
        annee_naissance=generation, sexe="H", affiliation=statut,
        age_debut=age_debut, age_liquidation=age, niveau_salaire=1.1,
        part_primes=0.22,
    )
    return simulateur.scenario_actuel.calculer(carriere)


def test_la_categorie_active_oppose_l_age_anticipe_et_non_l_age_legal(simulateur):
    """« Cinquante-sept ans s'il a accompli dix-sept ans de services dans des
    emplois classés dans la catégorie active » (L. 24, I, 1°), et cinquante-deux
    pour la super-active. Le drapeau existait dans `config.py` sans qu'aucun
    statut le porte : l'aide-soignant et le policier étaient calculés comme des
    sédentaires, et le modèle déclarait leur départ NON OUVERT.
    """
    sedentaire = _pension_actuelle(
        simulateur, "fonctionnaire_territorial_hospitalier", 1965, 57)
    assert sedentaire.motif_ouverture == "non_ouverte"

    actif = _pension_actuelle(
        simulateur, "fonctionnaire_territorial_hospitalier_actif", 1965, 57)
    assert actif.motif_ouverture == "age_legal"
    assert actif.age_ouverture_opposable == pytest.approx(57.0)

    super_actif = _pension_actuelle(
        simulateur, "fonctionnaire_etat_super_actif", 1965, 52)
    assert super_actif.motif_ouverture == "age_legal"
    assert super_actif.age_ouverture_opposable == pytest.approx(52.0)


def test_les_ages_classes_suivent_les_deux_montees_en_charge(simulateur):
    """Loi du 9 novembre 2010 : 55 -> 57 ans à compter du 1er juillet 1956,
    quatre mois puis cinq par génération (décret n° 2011-2103, article 2). Loi
    du 14 avril 2023 : 57 -> 59 ans à compter du 1er septembre 1966, trois mois
    par génération (article 10, XXIV, F).
    """
    def age(generation, mois=1):
        carriere = simulateur.carriere_simple(
            annee_naissance=generation, mois_naissance=mois, sexe="H",
            affiliation="fonctionnaire_etat_actif",
            age_debut=22, age_liquidation=62,
        )
        periode = simulateur.catalogue["fonction_publique_etat"].periode(2023)
        return simulateur.scenario_actuel._age_ouverture(periode, carriere)

    assert age(1950) == pytest.approx(55.0)
    assert age(1956, 3) == pytest.approx(55.0)
    assert age(1956, 9) == pytest.approx(55.33)
    assert age(1957) == pytest.approx(55.75)
    assert age(1960) == pytest.approx(57.0)
    assert age(1966, 3) == pytest.approx(57.0)
    assert age(1966, 10) == pytest.approx(57.25)
    # Suspension de 2026 (décret n° 2026-344, art. 3 D) : un trimestre de
    # moins des nés de septembre 1968 au 31 mars 1970, 59 ans à compter de 1974.
    assert age(1969) == pytest.approx(57.75)
    assert age(1970, 2) == pytest.approx(57.75)
    assert age(1970, 6) == pytest.approx(58.0)
    assert age(1973) == pytest.approx(58.75)
    assert age(1974) == pytest.approx(59.0)
    assert age(1980) == pytest.approx(59.0)


def test_sans_la_duree_de_services_classes_le_droit_commun_reprend(simulateur):
    """« Cette faculté est ouverte à la condition que le fonctionnaire puisse se
    prévaloir, au total, d'au moins dix-sept ans de services accomplis […] dits
    services actifs. » Dix ans d'emploi classé en fin de carrière ne l'ouvrent
    donc pas, et le statut déclaré n'y change rien.
    """
    def ouverture(age_bascule):
        carriere = simulateur.carriere_parcours(
            annee_naissance=1965, sexe="H", age_liquidation=57,
            metiers=[
                Metier("salarie_prive_non_cadre", 22, 1.1),
                Metier("fonctionnaire_territorial_hospitalier_actif",
                       age_bascule, 1.1),
            ],
        )
        return simulateur.scenario_actuel.calculer(carriere).motif_ouverture

    assert ouverture(47) == "non_ouverte"   # dix ans de services actifs
    assert ouverture(37) == "age_legal"     # vingt ans


def test_l_age_d_annulation_de_la_decote_d_un_actif_est_sa_limite_d_age(simulateur):
    """L'article L. 14 retranche ses trimestres de la LIMITE D'ÂGE du grade :
    soixante-deux ans en catégorie active, non soixante-sept. Un agent classé
    parti à soixante ans subit huit trimestres de décote quand un sédentaire du
    même âge en subit dix-huit — seize pour cent de pension d'écart (c'était
    vingt trimestres et vingt pour cent avant que la suspension de 2026 ne
    ramène la durée requise de la génération 1965 à cent soixante-dix), là où
    le plafond de vingt trimestres annulait l'écart à cinquante-sept ans.
    """
    periode = simulateur.catalogue["cnracl"].periode(2023)
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H",
        affiliation="fonctionnaire_territorial_hospitalier_actif",
        age_debut=22, age_liquidation=60,
    )
    assert simulateur.scenario_actuel._age_taux_plein(periode, carriere) == (
        pytest.approx(62.0))

    sedentaire = _pension_actuelle(
        simulateur, "fonctionnaire_territorial_hospitalier", 1965, 60)
    actif = _pension_actuelle(
        simulateur, "fonctionnaire_territorial_hospitalier_actif", 1965, 60)
    assert actif.pension_annuelle / sedentaire.pension_annuelle == (
        pytest.approx(0.9 / 0.775, abs=0.01))
    # À cinquante-sept ans, les deux décotes butent sur le plafond de vingt
    # trimestres et l'écart de pension redevient nul : c'est ce que
    # `docs/limites.md` disait du modèle d'avant, et qui reste vrai là.
    assert (_pension_actuelle(simulateur,
                              "fonctionnaire_territorial_hospitalier_actif",
                              1965, 57).pension_annuelle
            == pytest.approx(_pension_actuelle(
                simulateur, "fonctionnaire_territorial_hospitalier",
                1965, 57).pension_annuelle))


def test_la_surcote_d_un_actif_se_compte_depuis_l_age_legal_de_droit_commun(simulateur):
    """Le III de l'article L. 14 ne donne la majoration qu'« au-delà de l'âge
    mentionné à l'article L. 161-17-2 », et le D du XXIV de l'article 10 de la
    loi de 2023 le confirme pour les emplois classés : l'âge anticipé majoré de
    cinq années, c'est-à-dire l'âge légal. La compter depuis cinquante-sept ans
    paierait deux fois l'avantage du classement.
    """
    periode = simulateur.catalogue["cnracl"].periode(2023)
    carriere = simulateur.carriere_simple(
        annee_naissance=1965, sexe="H",
        affiliation="fonctionnaire_territorial_hospitalier_actif",
        age_debut=22, age_liquidation=60,
    )
    scenario = simulateur.scenario_actuel
    assert scenario._age_ouverture(periode, carriere) == pytest.approx(57.0)
    assert scenario._age_ouverture_commun(periode, carriere) == pytest.approx(62.75)


def test_la_pension_militaire_s_ouvre_a_une_duree_et_non_a_un_age(simulateur):
    """« Lorsqu'un militaire non officier […] réunit, à la date de son admission
    à la retraite, dix-sept ans de services effectifs » (L. 24, II, 2°), et
    vingt-sept ans pour un officier. C'est le départ le plus précoce du
    système : un engagé à dix-huit ans liquide à trente-cinq.
    """
    non_officier = _pension_actuelle(simulateur, "militaire", 1990, 40,
                                     age_debut=18)
    assert non_officier.motif_ouverture == "age_legal"
    assert non_officier.age_ouverture_opposable == pytest.approx(34.92, abs=0.1)

    officier = _pension_actuelle(simulateur, "militaire_officier", 1990, 50,
                                 age_debut=22)
    assert officier.age_ouverture_opposable == pytest.approx(48.92, abs=0.1)
    # Le même officier parti avant ses vingt-sept ans de services n'a pas la
    # jouissance immédiate : l'article L. 25 la lui diffère.
    tot = _pension_actuelle(simulateur, "militaire_officier", 1990, 45,
                            age_debut=22)
    assert tot.age_ouverture_opposable == pytest.approx(54.0)
    assert tot.motif_ouverture == "non_ouverte"


def test_la_duree_militaire_se_lit_a_l_annee_ou_l_ancienne_est_atteinte(simulateur):
    """Le relèvement de quinze à dix-sept ans est indexé sur « l'année au cours
    de laquelle sont atteintes les limites de durée de services […]
    antérieurement applicables » (décret n° 2011-2103, article 4), non sur la
    génération. Un engagé à dix-huit ans en 1990 réunit ses quinze ans en 2004
    et les garde ; engagé en 2000, il les réunit fin 2014 et en doit seize ans
    et sept mois ; engagé en 2003, fin 2017, et il en doit dix-sept.
    """
    def ouverture(generation):
        return _pension_actuelle(
            simulateur, "militaire", generation, 45, age_debut=18,
        ).age_ouverture_opposable

    assert ouverture(1972) == pytest.approx(32.92, abs=0.02)   # quinze ans
    assert ouverture(1982) == pytest.approx(34.50, abs=0.02)   # seize ans sept
    assert ouverture(1985) == pytest.approx(34.92, abs=0.02)   # dix-sept ans


def test_le_militaire_de_moins_de_quinze_ans_reste_au_droit_commun(simulateur):
    """Le 5° de l'article L. 25 : « lorsqu'ils ont accompli […] moins de quinze
    ans de services effectifs », la pension n'est due qu'à l'âge légal. Le
    militaire qui repart dans le privé après dix ans est alors un assuré comme
    un autre.
    """
    carriere = simulateur.carriere_parcours(
        annee_naissance=1975, sexe="H", age_liquidation=64,
        metiers=[Metier("militaire", 19, 1.0),
                 Metier("salarie_prive_non_cadre", 29, 1.0)],
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    assert resultat.age_ouverture_opposable == pytest.approx(64.0)


def test_la_decote_du_militaire_est_celle_du_II_de_l_article_L_14(simulateur):
    """Elle ne compte pas des âges mais des SERVICES : les trimestres manquants
    pour atteindre la durée d'ouverture augmentée de dix trimestres, dans la
    limite de dix. Un sous-officier parti à quarante ans avec dix-sept ans de
    services perd dix trimestres, non les vingt du barème des civils.
    """
    scenario = simulateur.scenario_actuel
    periode = simulateur.catalogue["fonction_publique_etat"].periode(2023)
    carriere = simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="militaire",
        age_debut=18, age_liquidation=35,
    )
    _, age_annulation, _ = scenario._decote(periode, carriere,
                                            carriere.annee_liquidation)
    trimestres = scenario._trimestres_de_decote(
        periode, carriere, trimestres=68, requis=172, age_liquidation=35.0,
        age_annulation=age_annulation,
    )
    assert trimestres == 10

    # Dix-neuf ans et demi de services : plus aucun trimestre manquant.
    longue = simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="militaire",
        age_debut=18, age_liquidation=38,
    )
    assert scenario._trimestres_de_decote(
        periode, longue, trimestres=80, requis=172, age_liquidation=38.0,
        age_annulation=age_annulation,
    ) == 0


def test_le_militaire_n_a_pas_de_surcote(simulateur):
    """Le III de l'article L. 14 ne la donne qu'au « fonctionnaire civil ». Sans
    cette réserve, l'âge d'ouverture très bas d'un militaire aurait fait
    surcoter chaque trimestre passé au-delà de trente-cinq ans.
    """
    carriere = simulateur.carriere_simple(
        annee_naissance=1990, sexe="H", affiliation="militaire",
        age_debut=18, age_liquidation=55,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    civile = next(pension for pension in resultat.pensions_par_regime
                  if pension.regime == "fonction_publique_etat")
    # Le taux plein de la fonction publique est de 75 % : une surcote le
    # dépasserait, et c'est ce que l'âge d'ouverture très bas d'un militaire
    # aurait produit sur chaque trimestre passé au-delà de trente-cinq ans.
    assert "taux 75.000%" in civile.detail


def test_la_derogation_ne_deborde_pas_sur_un_regime_special(simulateur):
    """Plusieurs régimes SPÉCIAUX servent eux aussi une catégorie active, et
    leur fiche le déclare — la SNCF a ses agents de conduite. Ce n'est pas la
    même : le droit dérogatoire ne vaut que dans les régimes que le statut
    classé route. Sans cette garde, un cheminot devenu agent territorial classé
    aurait vu sa pension SNCF liquidée à l'âge de la fonction publique et
    décotée sur une limite d'âge de grade qu'il n'a jamais eue.
    """
    carriere = simulateur.carriere_parcours(
        annee_naissance=1965, sexe="H", age_liquidation=57,
        metiers=[Metier("agent_sncf", 20, 1.1),
                 Metier("fonctionnaire_territorial_hospitalier_actif", 35, 1.1)],
    )
    scenario = simulateur.scenario_actuel
    sncf = simulateur.catalogue["sncf"].periode(2023)
    cnracl = simulateur.catalogue["cnracl"].periode(2023)
    assert "categorie_active" in sncf.avantages_non_contributifs
    assert scenario._age_ouverture(sncf, carriere) == pytest.approx(51.67, abs=0.01)
    assert scenario._age_ouverture(cnracl, carriere) == pytest.approx(57.0)
    assert scenario._age_taux_plein(sncf, carriere) == pytest.approx(56.67, abs=0.01)
    assert scenario._age_taux_plein(cnracl, carriere) == pytest.approx(62.0)


# -- un régime et celui qui lui succède (action 10 de la feuille de route) ------


def _carriere_par_statuts(*tranches: tuple[int, int, str], naissance: int,
                          liquidation: int, revenu: float = 40000.0) -> Carriere:
    lignes = [
        AnneeCarriere(annee=annee, revenu=revenu, affiliation=affiliation,
                      trimestres_valides=4)
        for debut, fin, affiliation in tranches
        for annee in range(debut, fin + 1)
    ]
    return Carriere(annee_naissance=naissance, sexe="H", lignes=lignes,
                    age_liquidation=float(liquidation - naissance))


def _pensions_de_base(resultat) -> dict[str, object]:
    return {p.regime: p for p in resultat.pensions_par_regime
            if p.regime in ("cancava", "organic", "rsi", "regime_general")}


def test_les_trois_noms_du_regime_de_l_artisan_liquident_ensemble(simulateur):
    """CANCAVA, RSI, régime général : trois noms, une pension.

    Un artisan de 1976 à 2020, parti en 2021, a cotisé sous trois caisses ;
    sa pension de base est UNE ligne, sous le nom de la dernière — le régime
    général, qui a le dossier —, avec un seul salaire de référence sur toute
    la carrière et une seule proratisation, et la ligne dit la succession.
    """
    carriere = _carriere_par_statuts(
        (1976, 2020, "artisan"), naissance=1956, liquidation=2021,
    )
    pensions = _pensions_de_base(simulateur.scenario_actuel.calculer(carriere))
    assert list(pensions) == ["regime_general"], list(pensions)
    ligne = pensions["regime_general"]
    assert "3 caisses liquidées ensemble (cancava, rsi puis regime_general)" in ligne.detail
    # 45 années validées, plafonnées à la durée de proratisation de la
    # génération 1956 : 166 trimestres, et non 40 + 48 + 12 en trois morceaux.
    assert "× 166/166" in ligne.detail, ligne.detail
    # Le salarié du privé payé pareil touche la même pension de base : c'est
    # l'alignement de l'article L. 634-2, et il ne tient qu'à cette fusion.
    salarie = simulateur.scenario_actuel.calculer(_carriere_par_statuts(
        (1976, 2020, "salarie_prive_non_cadre"), naissance=1956, liquidation=2021,
    ))
    assert ligne.montant == pytest.approx(
        _pensions_de_base(salarie)["regime_general"].montant, rel=1e-9
    )


def test_la_variante_coupee_garde_un_morceau_par_caisse(simulateur):
    """``liquider_successions=False`` retrouve le découpage d'avant, pour mesurer."""
    carriere = _carriere_par_statuts(
        (1976, 2020, "artisan"), naissance=1956, liquidation=2021,
    )
    entier = simulateur.scenario_actuel.calculer(carriere)
    coupe = simulateur.scenario_actuel.calculer(carriere, liquider_successions=False)
    assert sorted(_pensions_de_base(coupe)) == ["cancava", "regime_general", "rsi"]
    assert all("liquidées ensemble" not in p.detail
               for p in _pensions_de_base(coupe).values())
    # Trois morceaux de quarante, quarante-huit et douze trimestres sur 166.
    assert "× 120/166" in _pensions_de_base(coupe)["cancava"].detail
    assert "× 48/166" in _pensions_de_base(coupe)["rsi"].detail
    assert "× 12/166" in _pensions_de_base(coupe)["regime_general"].detail
    # Et la somme des morceaux n'est pas la pension entière : c'est l'écart
    # que la correction a fermé.
    somme = sum(p.montant for p in _pensions_de_base(coupe).values())
    assert somme != pytest.approx(entier.pension_annuelle, rel=1e-3)
    assert entier.trimestres_valides == coupe.trimestres_valides


def test_la_succession_ne_se_suit_qu_a_partir_de_la_fermeture(simulateur):
    """Un salarié devenu artisan a deux pensions en 2010, une seule en 2021.

    Le RSI ne ferme à ses affiliés qu'en 2018 : avant, le régime général et
    lui sont deux régimes distincts, et un polypensionné a une pension de
    chacun — la coordination entre régimes alignés distincts reste hors du
    modèle. Après, le RSI EST le régime général, et la carrière entière est
    liquidée d'un seul tenant. La CANCAVA, fermée en 2006, suit le RSI dans
    les deux cas.
    """
    tot = simulateur.scenario_actuel.calculer(_carriere_par_statuts(
        (1970, 1989, "salarie_prive_non_cadre"), (1990, 2009, "artisan"),
        naissance=1948, liquidation=2010,
    ))
    pensions = _pensions_de_base(tot)
    assert sorted(pensions) == ["regime_general", "rsi"], sorted(pensions)
    assert "2 caisses liquidées ensemble (cancava puis rsi)" in pensions["rsi"].detail
    assert "liquidées ensemble" not in pensions["regime_general"].detail
    assert "× 80/160" in pensions["regime_general"].detail
    assert "× 80/160" in pensions["rsi"].detail

    tard = simulateur.scenario_actuel.calculer(_carriere_par_statuts(
        (1981, 2000, "salarie_prive_non_cadre"), (2001, 2020, "artisan"),
        naissance=1959, liquidation=2021,
    ))
    pensions = _pensions_de_base(tard)
    assert list(pensions) == ["regime_general"], list(pensions)
    assert "3 caisses liquidées ensemble (cancava, rsi puis regime_general)" in (
        pensions["regime_general"].detail
    )
    assert "× 160/167" in pensions["regime_general"].detail, pensions["regime_general"].detail


def test_un_artisan_d_une_seule_caisse_n_est_pas_touche(simulateur):
    """Qui n'a connu qu'un nom garde sa ligne, sans mention de succession."""
    resultat = simulateur.scenario_actuel.calculer(_carriere_par_statuts(
        (1965, 2004, "artisan"), naissance=1945, liquidation=2005,
    ))
    pensions = _pensions_de_base(resultat)
    assert list(pensions) == ["cancava"]
    assert "liquidées ensemble" not in pensions["cancava"].detail


def test_carriere_longue_quatre_trimestres_pour_qui_est_ne_au_dernier_trimestre(simulateur):
    """D. 351-1-1 : cinq trimestres avant la fin de l'année civile des dix-huit
    ans, ou QUATRE pour qui est né entre le 1er octobre et le 31 décembre. Le
    modèle retenait cinq pour tout le monde tant qu'il ne connaissait que
    l'année de naissance. Deux assurés entrés le même mois de janvier 1983 avec
    quatre trimestres cette année-là : né en septembre, la porte des dix-huit
    ans reste fermée ; né en novembre, elle s'ouvre, et c'est le droit."""
    actuel = simulateur.scenario_actuel

    def carriere(mois, age_debut):
        return simulateur.carriere_simple(
            annee_naissance=1965, sexe="H", affiliation="salarie_prive_non_cadre",
            age_debut=age_debut, age_liquidation=60.25, niveau_salaire=1.0,
            mois_naissance=mois,
        )

    septembre = carriere(9, 17 + 4 / 12)
    novembre = carriere(11, 17 + 2 / 12)
    for c in (septembre, novembre):
        assert min(ligne.annee for ligne in c.lignes) == 1983
        assert sum(l.trimestres_valides for l in c.lignes if l.annee == 1983) == 4
    assert actuel.calculer(septembre).motif_ouverture == "non_ouverte"
    assert actuel.calculer(novembre).motif_ouverture == "carriere_longue"
    # Né en septembre, la porte des vingt ans reste la seule : 60 ans et
    # 9 mois pour la génération 1965 (D. 351-1-1, II). Né en novembre, celle
    # des dix-huit ans s'ouvre, à soixante ans, et la durée cotisée y est
    # (171 trimestres pour un né après mars 1965, suspension comprise).
    assert actuel.age_ouverture_droit(septembre) == pytest.approx(60.75)
    assert actuel.age_ouverture_droit(novembre) == pytest.approx(60.0)
