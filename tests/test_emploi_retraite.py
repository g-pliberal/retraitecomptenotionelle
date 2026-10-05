"""L'activité exercée après le départ, le cumul emploi-retraite (fiches
``cumul_emploi_retraite_et_retraite_progressive``, ``droits_apres_la_premiere_pension``
et ``seconde_pension``).

La saisie la déclare — sa date, sa fin, son statut, son revenu, l'employeur —,
la chronologie la date comme une période d'activité postérieure au départ, et
la carrière en garde les années à part : la première liquidation, que le
départ arrête, ne les voit pas.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


BASE = {"naissance": "1960", "sexe": "F", "debut": "20", "liquidation": "62",
        "unite_revenu": "moyen", "salaire": "1"}

#: Deux ans d'activité après le départ, chez un autre employeur, à la moitié
#: du salaire moyen.
EMPLOI = {"age": 63.0, "fin": 65.0, "affiliation": "salarie_prive_non_cadre",
          "niveau_salaire": 0.5, "employeur": "autre"}


def _carriere(simulateur: Simulateur, emploi: dict | None = EMPLOI) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        age_liquidation=62, macro=simulateur.macro, emploi_retraite=emploi)


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_porte_l_activite_apres_le_depart():
    saisie = Saisie.depuis_requete({**BASE, "emploi_retraite": "2023-03",
                                    "emploi_retraite_fin": "2025-01",
                                    "emploi_retraite_salaire": "0.5",
                                    "emploi_retraite_employeur": "dernier"})
    assert saisie.emploi_retraite_declare() == {
        "age": pytest.approx(63 + 1 / 12), "fin": pytest.approx(64 + 11 / 12),
        "affiliation": "salarie_prive_non_cadre", "niveau_salaire": 0.5,
        "employeur": "dernier"}
    requete = saisie.requete()
    for morceau in ("emploi_retraite=2023-03", "emploi_retraite_fin=2025-01",
                    "emploi_retraite_salaire=0.5", "emploi_retraite_employeur=dernier"):
        assert morceau in requete
    # Sans statut ni revenu, ceux du dernier métier.
    defaut = Saisie.depuis_requete({**BASE, "emploi_retraite": "2023-03",
                                    "emploi_retraite_fin": "2025-01"})
    assert defaut.emploi_retraite_declare()["niveau_salaire"] == 1.0
    assert "emploi_retraite_employeur" not in defaut.requete()


@pytest.mark.parametrize("champs, message", [
    ({"emploi_retraite_fin": "2025-01"}, "dites aussi quand elle commence"),
    ({"emploi_retraite": "2021-01", "emploi_retraite_fin": "2025-01"}, "elle suit le départ"),
    ({"emploi_retraite": "2023-03"}, "dites quand elle finit"),
    ({"emploi_retraite": "2023-03", "emploi_retraite_fin": "2023-02"},
     "elle finit après avoir commencé"),
    ({"emploi_retraite": "2023-03", "emploi_retraite_fin": "2024-02",
      "emploi_retraite_statut": "maladie"}, "n'est pas une activité"),
    ({"emploi_retraite": "2023-03", "emploi_retraite_fin": "2024-02",
      "emploi_retraite_salaire": "20"}, "entre 0,1 et 10 fois"),
])
def test_la_saisie_refuse_une_activite_qui_ne_se_tient_pas(champs, message):
    with pytest.raises(ErreurSaisie, match=message):
        Saisie.depuis_requete({**BASE, **champs})


# -- la chronologie et la carrière ------------------------------------------------

def test_la_chronologie_date_l_activite_apres_le_depart(simulateur):
    carriere = _carriere(simulateur)
    fait = chrono.emploi_retraite(carriere.chronologie, carriere.personne)
    assert fait["sorte"] == chrono.EMPLOI and fait["attributs"]["apres_depart"]
    assert (fait["debut"], fait["fin"]) == ("2023-02-01", "2025-02-01")
    assert fait not in chrono.periodes(carriere.chronologie, carriere.personne)
    assert carriere.emploi_retraite == {
        "debut": DateMois(2023, 2), "fin": DateMois(2025, 2),
        "affiliation": "salarie_prive_non_cadre", "employeur": "autre"}


def test_la_carriere_garde_ses_annees_a_part(simulateur):
    """Les années d'après le départ ne sont pas des lignes : la première
    liquidation ne les voit pas, et les copies de la carrière les gardent."""
    avec, sans = _carriere(simulateur), _carriere(simulateur, None)
    assert [l.annee for l in avec.lignes] == [l.annee for l in sans.lignes]
    assert [l.annee for l in avec.lignes_apres_depart] == [2023, 2024, 2025]
    premiere = avec.lignes_apres_depart[0]
    assert premiere.fraction_annee == pytest.approx(11 / 12)
    assert premiere.trimestres_valides <= 3
    assert avec.liquidee_au(DateMois(2023, 1)).lignes_apres_depart == avec.lignes_apres_depart
    assert avec.avec_lignes(avec.lignes).lignes_apres_depart == avec.lignes_apres_depart
    moteur = simulateur.scenario_actuel
    assert (moteur.calculer(avec).pension_annuelle
            == pytest.approx(moteur.calculer(sans).pension_annuelle))


# -- le cumul (droit/cumul.py) ------------------------------------------------------

from retraite_notionnelle.droit import cumul  # noqa: E402


def _cumul(simulateur: Simulateur, naissance: int, depart: float, emploi: dict,
           metiers: list[Metier] | None = None):
    """Le cumul que l'échéancier calcule pour cette carrière, et l'échéancier."""
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="F",
        metiers=metiers or [Metier("salarie_prive_non_cadre", 26.0)],
        age_liquidation=depart, macro=simulateur.macro, emploi_retraite=emploi)
    echeancier = simulateur.echeancier(carriere)
    return echeancier.au_depart.cumul, echeancier


def _emploi(age: float, fin: float, employeur: str = "autre",
            affiliation: str = "salarie_prive_non_cadre", niveau: float = 1.0) -> dict:
    return {"age": age, "fin": fin, "affiliation": affiliation, "niveau_salaire": niveau,
            "employeur": employeur}


def _pension(tranche, regime):
    return next(p for p in tranche.par_regime if p.regime == regime)


def test_le_cumul_integral_sert_la_pension_entiere(simulateur):
    """Toutes les pensions liquidées, à l'âge légal avec la durée : rien ne se
    réduit, ni la base ni l'Agirc-Arrco, et le délai de six mois ne joue pas."""
    resultat, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 64, "dernier"),
                         [Metier("salarie_prive_non_cadre", 20.0)])
    assert resultat.integral_depuis == resultat.debut
    assert {p.statut for t in resultat.tranches for p in t.par_regime} == {cumul.INTEGRAL}
    assert resultat.non_servi == 0


def test_le_cumul_plafonne_reduit_chaque_pension_de_base_du_depassement(simulateur):
    """Première pension de 2022 sans la durée : les pensions et le revenu, à son
    assiette de CSG, passent le plafond ; la pension du régime général perd le
    dépassement, l'Agirc-Arrco est suspendue (D. 161-2-16, II)."""
    resultat, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 64))
    assert resultat.integral_depuis is None
    for tranche in resultat.tranches:
        base = _pension(tranche, "regime_general")
        assert base.statut == cumul.REDUITE
        assert base.regle == cumul.REDUCTION_2015
        depassement = (tranche.pensions + tranche.revenu * cumul.assiette_csg(tranche.debut.annee)
                       - base.plafond)
        assert base.reduction == pytest.approx(min(base.montant, depassement))
        assert base.plafond >= 1.6 * simulateur.macro.smic_horaire(tranche.debut.annee) * 1820 / 12
        assert _pension(tranche, "agirc_arrco").statut == cumul.SUSPENDUE


def test_le_dernier_employeur_attend_six_mois(simulateur):
    """Retour chez le dernier employeur trois mois après la pension de mai 2022 :
    rien n'est dû jusqu'à fin octobre, le sixième mois ; le plafond joue ensuite
    (D. 161-2-15)."""
    resultat, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 63.5, "dernier"))
    premiere = resultat.tranches[0]
    assert (premiere.debut, premiere.fin) == (DateMois(2022, 8), DateMois(2022, 11))
    assert {p.statut for p in premiere.par_regime} == {cumul.NON_DUE}
    assert premiere.reduction == pytest.approx(premiere.pensions)
    assert resultat.tranches[1].statut != cumul.NON_DUE


def test_la_premiere_pension_d_avant_2015_est_suspendue(simulateur):
    """La première pension de 2011 garde la rédaction de L. 161-22 qui suspend :
    au-delà du plafond, rien n'est servi."""
    resultat, _ = _cumul(simulateur, 1951, 60.5, _emploi(61, 62))
    for tranche in resultat.tranches:
        base = _pension(tranche, "regime_general")
        assert (base.statut, base.regle) == (cumul.SUSPENDUE, cumul.LIBERALISE_2009)
        assert base.reduction == pytest.approx(base.montant)


def test_la_reduction_du_depassement_attend_avril_2017(simulateur):
    """La première pension de 2016 est suspendue jusqu'en mars 2017, puis
    réduite du dépassement : le décret de la réduction (n° 2017-416) ne vaut que
    pour les activités exercées depuis le 1er avril 2017."""
    resultat, _ = _cumul(simulateur, 1954, 62.0, _emploi(62.5, 64))
    statuts = {(t.debut, _pension(t, "regime_general").statut,
                _pension(t, "regime_general").regle) for t in resultat.tranches}
    avant = {s for s in statuts if s[0] < DateMois(2017, 4)}
    apres = {s for s in statuts if s[0] >= DateMois(2017, 4)}
    assert avant and {(s[1], s[2]) for s in avant} == {(cumul.SUSPENDUE, cumul.PREMIERES_2015)}
    assert apres and {(s[1], s[2]) for s in apres} == {(cumul.REDUITE, cumul.REDUCTION_2015)}


@pytest.mark.parametrize("employeur, statut", [("dernier", cumul.NON_DUE),
                                               ("autre", cumul.LIBRE)])
def test_avant_2004_seul_le_dernier_employeur_prive_de_la_pension(simulateur, employeur,
                                                                   statut):
    """La pension de 1995 suppose la rupture avec l'employeur : chez lui, elle
    n'est pas servie ; chez un autre, elle l'est entière."""
    resultat, _ = _cumul(simulateur, 1934, 61.0, _emploi(61.5, 63, employeur),
                         [Metier("salarie_prive_non_cadre", 20.0)])
    assert {_pension(t, "regime_general").statut for t in resultat.tranches} == {statut}
    assert {_pension(t, "regime_general").regle for t in resultat.tranches} == {
        cumul.RUPTURE_1983}


def test_le_fonctionnaire_perd_l_excedent_sur_le_tiers_de_sa_pension(simulateur):
    """L. 85 : l'excédent des revenus de l'année sur le tiers de la pension et la
    moitié du minimum garanti est déduit de la pension, réparti sur les mois
    d'activité de l'année."""
    resultat, _ = _cumul(simulateur, 1962, 62.5,
                         _emploi(63, 64.5, affiliation="contractuel_public"),
                         [Metier("fonctionnaire_etat", 24.0)])
    moteur = simulateur.scenario_actuel
    for tranche in resultat.tranches:
        pension = _pension(tranche, "fonction_publique_etat")
        assert pension.regle == cumul.FP_2015
        annee = tranche.debut.annee
        plafond = (pension.montant * 12 / 3
                   + moteur.minimum_garanti.reference(annee)[0] / 2)
        mois = sum(t.mois for t in resultat.tranches if t.debut.annee == annee)
        attendue = min(pension.montant, max(0.0, tranche.revenu * mois - plafond) / mois)
        assert pension.reduction == pytest.approx(attendue)
        assert pension.plafond == pytest.approx(plafond / 12)


@pytest.mark.parametrize("naissance, depart, regles", [
    (1952, 60.0, {(cumul.LIBRE, cumul.FP_2009, "employeur_prive")}),
    (1962, 62.5, {(cumul.REDUITE, cumul.FP_2015, "depassement"),
                  (cumul.PLAFONNEE, cumul.FP_2015, "sous_le_plafond")}),
])
def test_le_civil_parti_depuis_2015_est_plafonne_chez_tout_employeur(simulateur, naissance,
                                                                     depart, regles):
    """Le fonctionnaire civil parti en 2012 travaille librement dans le privé ;
    pour une première pension de 2015 ou après, tout employeur compte (L. 84 de
    2014) : l'excédent se déduit, et la dernière année, d'un mois, reste sous le
    plafond."""
    resultat, _ = _cumul(simulateur, naissance, depart, _emploi(depart + 0.5, depart + 1.5),
                         [Metier("fonctionnaire_etat", 24.0)])
    pensions = [_pension(t, "fonction_publique_etat") for t in resultat.tranches]
    assert {(p.statut, p.regle, p.motif) for p in pensions} == regles


def test_chaque_regime_ne_reduit_que_ses_pensions(simulateur):
    """Le salarié devenu artisan garde sa pension entière ; l'artisan redevenu
    artisan perd ce qui dépasse la moitié du plafond de la sécurité sociale
    (L. 634-6), sur la pension des régimes alignés que le régime général sert."""
    salarie, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 64, affiliation="artisan"))
    assert {(p.statut, p.motif) for t in salarie.tranches for p in t.par_regime} == {
        (cumul.LIBRE, "autre_regime")}
    artisan, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 64, affiliation="artisan"),
                        [Metier("artisan", 26.0)])
    for tranche in artisan.tranches:
        base = _pension(tranche, "regime_general")
        seuil = simulateur.macro.plafond_securite_sociale(tranche.debut.annee) / 2 / 12
        assert base.plafond == pytest.approx(seuil)
        assert base.reduction == pytest.approx(min(base.montant, tranche.revenu - seuil))


def test_la_premiere_pension_de_2027_est_reduite_de_tout_le_revenu_avant_l_age_legal(
        simulateur):
    """Carrière longue partie en 2028 : avant l'âge légal, la pension est réduite de
    tout le revenu ; ensuite, le seuil de 2027 n'étant pas publié, elle est
    servie entière, et le cumul le dit."""
    resultat, _ = _cumul(simulateur, 1968, 60.0, _emploi(61, 64),
                         [Metier("salarie_prive_non_cadre", 17.0)])
    statuts = [_pension(t, "regime_general").statut for t in resultat.tranches]
    assert statuts[0] == cumul.REDUITE
    assert statuts[-1] == cumul.SEUIL_NON_PUBLIE
    assert {_pension(t, "regime_general").regle for t in resultat.tranches} == {
        cumul.AGES_2027}


def test_le_journal_sert_la_pension_reduite_pendant_l_activite(simulateur):
    """La pension réduite s'inscrit dans sa lignée pour les mois où elle l'est :
    le journal sert la réduite pendant l'activité, l'entière ensuite."""
    resultat, echeancier = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 64))
    tranche = resultat.tranches[1]
    base = _pension(tranche, "regime_general")
    servies = {e.contenu["regime"]: e for e in echeancier.journal.servi(
        cumul.jour(tranche.debut), cumul.jour(tranche.debut.plus_mois(1)), "composante")
        if isinstance(e.contenu, dict) and "regime" in e.contenu}
    assert servies["regime_general"].id.startswith("cumul_regime_general_")
    assert servies["regime_general"].contenu["montant"]["annuel"] == pytest.approx(
        (base.montant - base.reduction) * 12)
    apres = {e.contenu["regime"]: e for e in echeancier.journal.servi(
        cumul.jour(resultat.fin), None, "composante")
        if isinstance(e.contenu, dict) and "regime" in e.contenu}
    assert not apres["regime_general"].id.startswith("cumul_")


def test_les_regles_du_cumul_sont_des_versions_des_fiches(simulateur):
    """Chaque règle que le cumul cite est une version d'une des deux fiches."""
    from retraite_notionnelle.noyau import carte

    toutes = carte.fiches()
    versions = set()
    for fiche in ("cumul_emploi_retraite_et_retraite_progressive",
                  "cumul_emploi_retraite_fonction_publique"):
        versions |= {v["id"] for v in toutes[fiche]["versions"]}
    citees = {valeur for nom, valeur in vars(cumul).items()
              if nom.isupper() and isinstance(valeur, str) and "_" in valeur
              and nom in ("AVANT_1983", "RUPTURE_1983", "PLAFOND_2004", "LIBERALISE_2009",
                          "PREMIERES_2015", "REDUCTION_2015", "AGES_2027", "FP_1970",
                          "FP_2004", "FP_2009", "FP_2015", "FP_2027")}
    assert len(citees) == 12
    assert citees <= versions, citees - versions


# -- les droits de l'activité et la nouvelle pension (droit/seconde.py) -------------

from retraite_notionnelle.droit import liquider as _liquider  # noqa: E402
from retraite_notionnelle.droit import seconde  # noqa: E402


def _droits(simulateur: Simulateur, naissance: int, depart: float, emploi: dict,
            metiers: list[Metier] | None = None):
    resultat, echeancier = _cumul(simulateur, naissance, depart, emploi, metiers)
    return echeancier.au_depart.droits_apres_depart, echeancier


def test_le_cumul_integral_ouvre_une_nouvelle_pension(simulateur):
    """Au taux plein depuis 2022, la salariée qui travaille de février 2023 à
    janvier 2025 se constitue une nouvelle pension au régime général — le
    salaire mensuel moyen des années qui valident un trimestre, au taux plein,
    proratisé par la durée requise — et des points de l'Agirc-Arrco sur la
    tranche 1, servis sans coefficient (L. 161-22-1-1, R. 351-29, III)."""
    droits, echeancier = _droits(simulateur, 1960, 62.25, _emploi(63, 65, niveau=0.5),
                                 [Metier("salarie_prive_non_cadre", 20.0)])
    assert [(p.motif, p.regle) for p in droits.periodes] == [
        (seconde.NOUVELLE_PENSION, seconde.LOI_2023)]
    base = next(p for p in droits.pensions if p.regime == "regime_general")
    requis = echeancier.au_depart.trimestres_requis
    assert base.date_effet == DateMois(2025, 2)
    assert 0 < base.trimestres <= 8
    assert base.brute == pytest.approx(
        base.salaire_mensuel * 12 * 0.5 * min(1.0, base.trimestres / requis))
    assert base.plafond == pytest.approx(0.05 * simulateur.macro.plafond_securite_sociale(2025))
    assert base.montant == pytest.approx(min(base.brute, base.plafond))
    complementaire = next(p for p in droits.pensions if p.regime == "agirc_arrco")
    valeur = _liquider.valeur_du_point(simulateur.scenario_actuel, "agirc_arrco", 2025)[0]
    assert complementaire.points > 0
    assert complementaire.montant == pytest.approx(complementaire.points * valeur)


def test_la_seconde_retraite_agirc_arrco_attend_le_1er_janvier_2024(simulateur):
    """Un cumul achevé en 2023 : la nouvelle pension du régime général part au
    1er septembre 2023 au plus tôt, la seconde retraite de l'Agirc-Arrco au
    1er janvier 2024 (accord du 17 novembre 2017, article 91, rédaction de
    l'avenant n° 16), et ses points se comptent au taux de calcul, 6,20 %."""
    droits, _ = _droits(simulateur, 1960, 62.25, _emploi(63, 63.5, niveau=0.5),
                        [Metier("salarie_prive_non_cadre", 20.0)])
    dates = {p.regime: p.date_effet for p in droits.pensions}
    assert dates == {"regime_general": DateMois(2023, 9), "agirc_arrco": DateMois(2024, 1)}


def test_la_nouvelle_pension_ne_depasse_pas_cinq_pour_cent_du_plafond(simulateur):
    """Trois fois le salaire moyen quatre ans durant : la nouvelle pension est
    écrêtée à 5 % du plafond de la sécurité sociale (D. 161-2-22-1)."""
    droits, _ = _droits(simulateur, 1960, 62.25, _emploi(63, 67, niveau=3.0),
                        [Metier("salarie_prive_non_cadre", 20.0)])
    base = next(p for p in droits.pensions if p.regime == "regime_general")
    assert base.brute > base.plafond
    assert base.montant == pytest.approx(
        0.05 * simulateur.macro.plafond_securite_sociale(base.date_effet.annee))


def test_la_premiere_pension_de_2027_attend_le_cumul_entier_sans_plafond(simulateur):
    """Carrière longue partie en 2028 : rien ne s'ouvre avant l'âge du taux plein
    automatique ; ensuite, la nouvelle pension n'a plus de plafond (rédaction
    de 2026)."""
    droits, echeancier = _droits(simulateur, 1968, 60.0, _emploi(61, 68),
                                 [Metier("salarie_prive_non_cadre", 17.0)])
    assert [(p.motif, p.regle) for p in droits.periodes] == [
        (seconde.ETEINTS, seconde.LFSS_2026), (seconde.NOUVELLE_PENSION, seconde.LFSS_2026)]
    carriere = echeancier.au_depart
    base = next(p for p in droits.pensions if p.regime == "regime_general")
    assert base.plafond is None and base.montant == pytest.approx(base.brute)
    assert droits.periodes[1].debut == echeancier.au_depart.cumul.integral_depuis
    assert carriere.cumul.integral_depuis > DateMois(2034, 12)


@pytest.mark.parametrize("naissance, debut, regles", [
    (1960, 26.0, [seconde.LOI_2014, seconde.LOI_2023]),
    (1954, 20.0, [seconde.LOI_2014]),
])
def test_hors_du_cumul_integral_l_activite_n_ouvre_rien(simulateur, naissance, debut,
                                                      regles):
    """Première pension de 2022 sans la durée : l'activité n'ouvre rien, ni avant
    2023 (L. 161-22-1 A) ni après (L. 161-22-1) ; première pension de 2016, au
    taux plein : rien non plus avant 2023, cumul intégral ou non."""
    depart = 62.25 if naissance == 1960 else 62.0
    droits, _ = _droits(simulateur, naissance, depart, _emploi(depart + 0.25, depart + 1.75),
                        [Metier("salarie_prive_non_cadre", debut)])
    assert [(p.motif, p.regle) for p in droits.periodes] == [
        (seconde.ETEINTS, regle) for regle in regles]
    assert droits.pensions == ()


def test_le_retour_chez_le_dernier_employeur_n_ouvre_jamais_de_droit(simulateur):
    """Au taux plein, mais revenue chez son dernier employeur trois mois après sa
    pension : aucun droit nouveau, même en cumul intégral (L. 161-22-1, 2°)."""
    droits, _ = _droits(simulateur, 1960, 62.25, _emploi(62.5, 64, "dernier", niveau=0.5),
                        [Metier("salarie_prive_non_cadre", 20.0)])
    assert droits.periodes[-1].motif == seconde.DERNIER_EMPLOYEUR
    assert droits.pensions == ()


def test_la_pension_militaire_n_eteint_pas_les_droits(simulateur):
    """Le militaire parti à quarante-cinq ans qui travaille dans le privé continue
    d'acquérir des droits dans les régimes qui ne lui servent pas de pension :
    L. 84 du code des pensions lui retire l'extinction."""
    droits, _ = _droits(simulateur, 1975, 45.0, _emploi(45.5, 50),
                        [Metier("militaire", 20.0)])
    assert {p.motif for p in droits.periodes} == {seconde.PENSION_MILITAIRE}


@pytest.mark.parametrize("metier, motif", [
    ("salarie_prive_non_cadre", seconde.REGIME_LIQUIDE),
    ("fonctionnaire_etat", seconde.REGIMES_NON_LIQUIDES),
])
def test_avant_2015_seuls_les_regimes_qui_n_ont_pas_liquide_ouvrent_des_droits(
        simulateur, metier, motif):
    """Première pension de 2011 : le salarié revenu au régime général n'y ouvre
    rien, sa pension étant définitive ; le fonctionnaire devenu salarié ouvre des
    droits au régime général, qui ne lui sert pas de pension."""
    droits, _ = _droits(simulateur, 1951, 60.5, _emploi(61, 62), [Metier(metier, 26.0)])
    assert {p.motif for p in droits.periodes} == {motif}
    assert {p.regle for p in droits.periodes} == {seconde.SANS_REGLE_GENERALE}


def test_la_nouvelle_pension_s_inscrit_au_journal(simulateur):
    """La nouvelle pension s'inscrit à sa date d'effet, dans une lignée à elle, et
    le journal la sert à partir de cette date."""
    droits, echeancier = _droits(simulateur, 1960, 62.25, _emploi(63, 65, niveau=0.5),
                                 [Metier("salarie_prive_non_cadre", 20.0)])
    date = cumul.jour(droits.pensions[0].date_effet)
    servies = {e.id: e for e in echeancier.journal.servi(date, None, "composante")}
    for pension in droits.pensions:
        entree = servies[f"seconde_{pension.regime}"]
        assert entree.contenu["montant"]["annuel"] == pytest.approx(pension.montant)
    avant = {e.id for e in echeancier.journal.servi("2024-06-01", "2024-07-01", "composante")}
    assert not any(ident.startswith("seconde_") for ident in avant)


def test_les_regles_des_droits_sont_des_versions_des_fiches():
    """Chaque règle que les droits citent est une version de leur fiche."""
    from retraite_notionnelle.noyau import carte

    versions = {v["id"] for v in carte.fiches()["droits_apres_la_premiere_pension"]["versions"]}
    assert {seconde.SANS_REGLE_GENERALE, seconde.LOI_2014, seconde.LOI_2023,
            seconde.LFSS_2026} <= versions


def test_l_activite_ouvre_une_pension_dans_le_regime_qui_n_en_servait_pas(simulateur):
    """La fonctionnaire partie en 2011, salariée de 2012 à 2016 : sa pension de
    l'État ne bouge pas, et son activité lui ouvre, à sa fin, une pension du
    régime général et une retraite Arrco, liquidées comme les autres, sur la
    durée tous régimes."""
    droits, echeancier = _droits(simulateur, 1951, 60.5, _emploi(61, 65.5),
                                 [Metier("fonctionnaire_etat", 26.0)])
    assert {p.motif for p in droits.periodes} == {seconde.REGIMES_NON_LIQUIDES}
    nouveaux = {p.regime: p for p in droits.regimes_nouveaux}
    assert {"regime_general", "arrco"} <= set(nouveaux)
    assert {p.date_effet for p in droits.regimes_nouveaux} == {echeancier.au_depart.cumul.fin}
    liquidations = [e for e in echeancier.journal
                    if e.sorte == "liquidation" and "regimes_nouveaux" in e.id]
    assert len(liquidations) == 1
    assert {p.regime for p in liquidations[0].contenu.regimes} >= {"regime_general", "arrco"}
    assert all(p.regime not in nouveaux for p in echeancier.au_depart.pensions_par_regime)


def test_la_pension_militaire_ouvre_le_regime_general_a_son_age(simulateur):
    """Le militaire parti à quarante-cinq ans, salarié jusqu'à cinquante ans :
    son régime général n'ouvre qu'à l'âge légal, où ses droits se liquident."""
    droits, echeancier = _droits(simulateur, 1975, 45.0, _emploi(45.5, 50),
                                 [Metier("militaire", 20.0)])
    base = next(p for p in droits.regimes_nouveaux if p.regime == "regime_general")
    carriere = echeancier.au_depart
    assert base.date_effet > echeancier.au_depart.cumul.fin
    assert base.date_effet.annee >= 1975 + 62
    assert carriere.pensions_par_regime[0].regime == "fonction_publique_etat"


def test_apres_2015_l_activite_n_ouvre_aucun_regime_nouveau(simulateur):
    """Partie en 2016 de la fonction publique, salariée ensuite : rien ne
    s'ouvre au régime général (L. 161-22-1 A)."""
    droits, _ = _droits(simulateur, 1954, 62.0, _emploi(62.5, 64),
                        [Metier("fonctionnaire_etat", 26.0)])
    assert {p.motif for p in droits.periodes} == {seconde.ETEINTS}
    assert droits.regimes_nouveaux == ()
