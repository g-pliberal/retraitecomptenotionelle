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
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.web.site import ErreurSite

from outils_pont import refus_de_la_saisie, saisie_du_portage


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


#: L'assurée naît le 15 janvier : le jour se déclare, puisque les dates de
#: l'activité et du cumul se comptent depuis lui ; celui que la présomption
#: pose a son test (``test_chronologie.py`` ; feuille de route, action 135,
#: levier 2).
BASE = {"naissance": "1960-01-15", "sexe": "F", "debut": "20", "liquidation": "62",
        "unite_revenu": "moyen", "salaire": "1"}

#: Deux ans d'activité après le départ, chez un autre employeur, à la moitié
#: du salaire moyen.
EMPLOI = {"age": 63.0, "fin": 65.0, "affiliation": "salarie_prive_non_cadre",
          "niveau_salaire": 0.5, "employeur": "autre"}


def _carriere(simulateur: Simulateur, emploi: dict | None = EMPLOI) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        age_liquidation=62, macro=simulateur.macro, jour_naissance=15,
        emploi_retraite=emploi)


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_porte_l_activite_apres_le_depart():
    saisie = saisie_du_portage({**BASE, "emploi_retraite": "2023-03",
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
    defaut = saisie_du_portage({**BASE, "emploi_retraite": "2023-03",
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
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(message)):
        saisie_du_portage({**BASE, **champs})


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
    """Le cumul que l'échéancier calcule pour cette carrière, d'une assurée
    née le 15 janvier, et l'échéancier."""
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="F",
        metiers=metiers or [Metier("salarie_prive_non_cadre", 26.0)],
        age_liquidation=depart, macro=simulateur.macro, jour_naissance=15,
        emploi_retraite=emploi)
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


#: La pension complémentaire de l'artisan et du commerçant : le RCI, et les
#: points du RCO des artisans et du NRCO des commerçants, qu'il sert depuis
#: 2013 (fiche ``cumul_emploi_retraite_complementaire_des_independants``).
COMPLEMENTAIRES_DES_INDEPENDANTS = ("rci", "rco_artisans", "nric")


def _complementaires(tranche):
    return [p for p in tranche.par_regime if p.regime in COMPLEMENTAIRES_DES_INDEPENDANTS]


@pytest.mark.parametrize("naissance, depart, metier, base, complementaires", [
    (1949, 60.5, "artisan", "rsi", {"rco_artisans"}),
    (1952, 61.0, "artisan", "rsi", {"rci", "rco_artisans"}),
    (1952, 61.0, "commercant", "rsi", {"rci", "nric"}),
])
def test_la_complementaire_de_l_independant_est_suspendue_avec_sa_base(
        simulateur, naissance, depart, metier, base, complementaires):
    """Première pension d'avant 2015 : au-delà de la moitié du plafond de la
    sécurité sociale, la pension de base est suspendue (L. 634-6 de 2008), et
    « le service de la pension de vieillesse complémentaire est suspendu pour
    la même durée » — règlements du RCO et du NRCO de 2009, articles 23, II,
    et 10, que la caisse applique depuis le 1er janvier 2009, puis du RCI,
    article 27, de 2013 : rien n'est servi, ni du RCI, ni des points qu'il a
    repris."""
    resultat, _ = _cumul(simulateur, naissance, depart,
                         _emploi(depart + 0.5, depart + 2, affiliation=metier),
                         [Metier(metier, 26.0)])
    assert resultat.tranches
    for tranche in resultat.tranches:
        assert _pension(tranche, base).statut == cumul.SUSPENDUE
        servies = _complementaires(tranche)
        assert {p.regime for p in servies} == complementaires
        for pension in servies:
            assert (pension.statut, pension.regle, pension.motif) == (
                cumul.SUSPENDUE, cumul.RCI_2009, "depassement")
            assert pension.reduction == pytest.approx(pension.montant)
            assert pension.plafond == pytest.approx(_pension(tranche, base).plafond)


def test_avant_2009_la_complementaire_de_l_independant_est_servie_entiere(simulateur):
    """Avant les règlements de 2009, la règle de service de la complémentaire
    n'est pas lue : le modèle la sert entière, et le dit par sa version
    supposée."""
    resultat, _ = _cumul(simulateur, 1942, 60.5, _emploi(61, 62.5, affiliation="artisan"),
                         [Metier("artisan", 26.0)])
    assert {t.debut.annee for t in resultat.tranches} <= set(range(2003, 2009))
    assert {(p.regime, p.statut, p.regle, p.motif, p.reduction)
            for t in resultat.tranches for p in _complementaires(t)} == {
        ("rco_artisans", cumul.LIBRE, cumul.RCI_AVANT_2009, "non_lue", 0.0)}


def test_la_complementaire_n_est_reduite_comme_sa_base_que_depuis_juillet_2024(simulateur):
    """Première pension de 2022, artisane à 60 % du salaire moyen d'août 2022 à
    janvier 2025 : sa pension de base perd le dépassement de la moitié du
    plafond (D. 634-11-2, D. 634-11-5). Jusqu'en juin 2024, l'article 27 ne
    suspend la complémentaire qu'avec la base, que rien ne suspend plus : elle
    est servie entière. L'arrêté du 19 juin 2024 rend « applicables au service
    de la pension » du RCI « les dispositions de la section 3 » du code, en
    vigueur le 26 juin : depuis juillet, elle perd elle aussi le dépassement
    entier, réparti entre ses points du RCI et du RCO."""
    resultat, _ = _cumul(simulateur, 1960, 62.25,
                         _emploi(62.5, 65, affiliation="artisan", niveau=0.6),
                         [Metier("artisan", 26.0)])
    juillet = DateMois(2024, 7)
    assert {t.debut < juillet for t in resultat.tranches} == {True, False}
    assert juillet in {t.debut for t in resultat.tranches}
    for tranche in resultat.tranches:
        seuil = simulateur.macro.plafond_securite_sociale(tranche.debut.annee) / 2 / 12
        depassement = tranche.revenu - seuil
        assert _pension(tranche, "regime_general").statut == cumul.REDUITE
        servies = _complementaires(tranche)
        assert {p.regime for p in servies} == {"rci", "rco_artisans"}
        total = sum(p.montant for p in servies)
        assert 0 < depassement < total
        if tranche.debut < juillet:
            assert {(p.statut, p.regle, p.motif, p.reduction) for p in servies} == {
                (cumul.PLAFONNEE, cumul.RCI_2009, "base_reduite", 0.0)}
            continue
        for pension in servies:
            assert (pension.statut, pension.regle, pension.motif) == (
                cumul.REDUITE, cumul.RCI_2024, "depassement")
            assert pension.plafond == pytest.approx(seuil)
            assert pension.reduction == pytest.approx(depassement * pension.montant / total)


def test_en_cumul_integral_la_complementaire_de_l_independant_est_entiere(simulateur):
    """L'artisane partie en 2022 avec la durée requise, toutes ses pensions
    liquidées : « L'assuré peut bénéficier du service intégral de sa pension
    de vieillesse complémentaire lorsque les conditions [du cumul intégral]
    sont remplies » (article 27)."""
    resultat, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 64, affiliation="artisan"),
                         [Metier("artisan", 20.0)])
    assert {(p.statut, p.regle) for t in resultat.tranches for p in _complementaires(t)} == {
        (cumul.INTEGRAL, cumul.RCI_2009)}


def test_l_activite_salariee_laisse_la_complementaire_de_l_independant_entiere(simulateur):
    """L'ancienne artisane salariée après son départ : l'article 27 ne vise que
    « les activités relevant des régimes des professions artisanales,
    industrielles et commerciales », la section 3 que l'activité indépendante
    (L. 634-6) ; sa complémentaire est servie entière, avant comme après juin
    2024."""
    resultat, _ = _cumul(simulateur, 1960, 62.25, _emploi(62.5, 65),
                         [Metier("artisan", 26.0)])
    assert {(p.statut, p.motif) for t in resultat.tranches for p in _complementaires(t)} == {
        (cumul.LIBRE, "autre_regime")}
    assert any(t.debut >= DateMois(2024, 7) for t in resultat.tranches)


def test_la_premiere_pension_de_2027_reduit_la_complementaire_apres_la_base(simulateur):
    """Carrière longue d'artisane, partie en 2028, à 60 % du salaire moyen :
    avant l'âge légal, la réduction de tout le revenu « est appliquée, par
    priorité, sur les pensions versées par les régimes de retraite de base »
    (L. 161-22, III, A, de 2027), auquel le règlement du RCI soumet sa pension
    depuis le 1er janvier 2027 : la complémentaire ne perd que ce que la base
    n'absorbe pas, au prorata de ses points ; passé l'âge légal, le seuil
    n'étant pas publié, elle est servie entière, comme la base."""
    resultat, _ = _cumul(simulateur, 1968, 60.0,
                         _emploi(61, 64, affiliation="artisan", niveau=0.6),
                         [Metier("artisan", 17.0)])
    avant = [t for t in resultat.tranches
             if _pension(t, "regime_general").statut == cumul.REDUITE]
    assert avant and len(avant) < len(resultat.tranches)
    for tranche in resultat.tranches:
        servies = _complementaires(tranche)
        assert {p.regle for p in servies} == {cumul.RCI_2027}
        if tranche not in avant:
            assert {p.statut for p in servies} == {cumul.SEUIL_NON_PUBLIE}
            continue
        base = _pension(tranche, "regime_general")
        revenu = tranche.revenu * cumul.assiette_csg(tranche.debut.annee)
        total = sum(p.montant for p in servies)
        reste = revenu - base.montant
        assert base.reduction == pytest.approx(base.montant)
        assert 0 < reste < total
        for pension in servies:
            assert (pension.statut, pension.motif) == (cumul.REDUITE, "avant_l_age_legal")
            assert pension.reduction == pytest.approx(reste * pension.montant / total)


def test_la_premiere_pension_de_2027_reduit_d_abord_la_base(simulateur):
    """La même, à 40 % du salaire moyen : son revenu n'épuise pas sa pension de
    base, qui absorbe toute la réduction ; la complémentaire est servie
    entière."""
    resultat, _ = _cumul(simulateur, 1968, 60.0,
                         _emploi(61, 64, affiliation="artisan", niveau=0.4),
                         [Metier("artisan", 17.0)])
    avant = [t for t in resultat.tranches
             if _pension(t, "regime_general").statut == cumul.REDUITE]
    assert avant
    for tranche in avant:
        assert _pension(tranche, "regime_general").reduction < _pension(
            tranche, "regime_general").montant
        assert {(p.statut, p.regle, p.motif, p.reduction) for p in _complementaires(tranche)} == {
            (cumul.PLAFONNEE, cumul.RCI_2027, "imputee_sur_la_base", 0.0)}


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


# -- les autres complémentaires : l'Ircantec, la RCO agricole, les sections libérales --


def _servies(resultat, regime):
    """Ce que chaque tranche fait de la pension de ce régime."""
    return [(t, _pension(t, regime)) for t in resultat.tranches
            if any(p.regime == regime for p in t.par_regime)]


def _liberale(metier: str) -> list[Metier]:
    """Une carrière libérale de trente ans, après quatre ans de salariat : la
    durée qu'elle valide reste sous la durée requise, et le cumul n'est pas
    intégral à l'âge légal."""
    return [Metier("salarie_prive_non_cadre", 26.0), Metier(metier, 30.0)]


def test_l_ircantec_suit_l_161_22_pour_l_activite_qui_y_cotise(simulateur):
    """Arrêté du 30 décembre 1970, article 14, depuis 2004 : « La reprise
    d'activité est autorisée dans les conditions prévues à l'article L. 161-22 »,
    puis, depuis 2011, le cumul « avec l'exercice d'une activité professionnelle
    entraînant un assujettissement à l'IRCANTEC ». L'agente contractuelle partie
    en 2011, de nouveau contractuelle au-delà du plafond : sa pension du régime
    général est suspendue, son allocation de l'Ircantec aussi."""
    resultat, _ = _cumul(simulateur, 1951, 60.5,
                         _emploi(61, 62, affiliation="contractuel_public"),
                         [Metier("contractuel_public", 26.0)])
    servies = _servies(resultat, "ircantec")
    assert servies
    for tranche, ircantec in servies:
        assert _pension(tranche, "regime_general").statut == cumul.SUSPENDUE
        assert (ircantec.statut, ircantec.regle, ircantec.motif) == (
            cumul.SUSPENDUE, cumul.IRCANTEC_2004, "depassement")
        assert ircantec.reduction == pytest.approx(ircantec.montant)


def test_l_ircantec_se_reduit_du_depassement_jusqu_en_2020(simulateur):
    """Première pension de 2020, contractuelle d'août 2020 à décembre 2021 :
    jusqu'en décembre 2020, l'article 14 applique L. 161-22 entier, dont le
    troisième alinéa — « chacune des pensions servies par ces régimes est
    réduite à due concurrence du dépassement » ; depuis l'arrêté du 16 décembre
    2020, en vigueur le 19, il l'applique « à l'exception de son troisième
    alinéa », et l'Ircantec « continue de vous verser la totalité » (sa page du
    cumul emploi-retraite) : servie entière quand la base est réduite."""
    resultat, _ = _cumul(simulateur, 1958, 62.25,
                         _emploi(62.5, 64, affiliation="contractuel_public"),
                         [Metier("contractuel_public", 26.0)])
    janvier = DateMois(2021, 1)
    servies = _servies(resultat, "ircantec")
    assert {t.debut < janvier for t, _ in servies} == {True, False}
    for tranche, ircantec in servies:
        base = _pension(tranche, "regime_general")
        assert (base.statut, base.regle) == (cumul.REDUITE, cumul.REDUCTION_2015)
        depassement = (tranche.pensions + tranche.revenu * cumul.assiette_csg(tranche.debut.annee)
                       - base.plafond)
        if tranche.debut < janvier:
            assert (ircantec.statut, ircantec.regle, ircantec.motif) == (
                cumul.REDUITE, cumul.IRCANTEC_2004, "depassement")
            assert ircantec.reduction == pytest.approx(min(ircantec.montant, depassement))
        else:
            assert (ircantec.statut, ircantec.regle, ircantec.motif, ircantec.reduction) == (
                cumul.PLAFONNEE, cumul.IRCANTEC_2020, "sans_le_troisieme_alinea", 0.0)


@pytest.mark.parametrize("naissance, depart, emploi, attendu", [
    (1951, 60.5, _emploi(61, 62), (cumul.LIBRE, "", "autre_regime")),
    (1938, 62.0, _emploi(62.5, 64, affiliation="contractuel_public"),
     (cumul.LIBRE, "servie_entiere_avant_2004", "non_lue")),
])
def test_hors_de_son_champ_ou_avant_2004_l_ircantec_est_entiere(simulateur, naissance, depart,
                                                                  emploi, attendu):
    """L'ancienne contractuelle salariée du privé : l'article 14 ne vise que
    l'activité qui cotise à l'Ircantec, son allocation est servie entière. Avant
    2004, l'article ne dit que la cessation qui ouvre le droit : le modèle la sert
    entière, par une version supposée."""
    resultat, _ = _cumul(simulateur, naissance, depart, emploi,
                         [Metier("contractuel_public", 26.0)])
    servies = _servies(resultat, "ircantec")
    assert servies
    assert {(p.statut, p.regle, p.motif) for _, p in servies} == {attendu}


@pytest.mark.parametrize("affiliation, attendu", [
    ("exploitant_agricole", (cumul.NON_CALCULE, "suit_la_base_2003", "regle_non_lue")),
    ("salarie_agricole", (cumul.LIBRE, "", "autre_regime")),
])
def test_la_rco_agricole_suit_la_regle_de_la_base(simulateur, affiliation, attendu):
    """« Les dispositions des articles L. 732-39 et L. 732-40 sont applicables à
    la pension de retraite complémentaire obligatoire » (D. 732-157, depuis 2003) :
    la complémentaire de l'exploitant suit la règle de sa base, que le modèle
    n'a pas lue pour l'activité agricole non salariée, et que l'activité salariée
    ne touche pas."""
    resultat, _ = _cumul(simulateur, 1955, 62.0, _emploi(62.5, 64, affiliation=affiliation),
                         [Metier("exploitant_agricole", 20.0)])
    servies = _servies(resultat, "msa_rco")
    assert servies
    assert {(p.statut, p.regle, p.motif) for _, p in servies} == {attendu}


def test_la_complementaire_des_dentistes_est_suspendue_avec_leur_base(simulateur):
    """Statuts de la CARCDSF de 2011, article 47 : « Lorsque l'assuré est soumis
    à une suspension de sa pension dans le régime de base en application des
    deuxième et troisième alinéas de l'article L. 643-6 [...], le service de la
    pension du régime complémentaire de vieillesse est suspendu pour la même
    durée ». La dentiste partie en 2012, de nouveau en cabinet au-delà du
    plafond de la sécurité sociale : sa base est suspendue, sa complémentaire
    aussi ; partie en 2016 et en cabinet depuis 2017, sa base n'est que réduite
    du dépassement, et sa complémentaire est servie entière."""
    metiers = _liberale("chirurgien_dentiste_ou_sage_femme")
    emploi = dict(affiliation="chirurgien_dentiste_ou_sage_femme", niveau=2.0)
    avant, _ = _cumul(simulateur, 1951, 61.5, _emploi(62, 63.5, **emploi), metiers)
    servies = _servies(avant, "carcdsf_complementaire")
    assert servies
    for tranche, complementaire in servies:
        assert _pension(tranche, "cnavpl").statut == cumul.SUSPENDUE
        assert (complementaire.statut, complementaire.regle, complementaire.motif) == (
            cumul.SUSPENDUE, cumul.SECTIONS_STATUTS, "depassement")
        assert complementaire.reduction == pytest.approx(complementaire.montant)
    depuis, _ = _cumul(simulateur, 1954, 62.0, _emploi(63, 64.5, **emploi), metiers)
    servies = _servies(depuis, "carcdsf_complementaire")
    assert servies
    for tranche, complementaire in servies:
        assert _pension(tranche, "cnavpl").statut == cumul.REDUITE
        assert (complementaire.statut, complementaire.motif, complementaire.reduction) == (
            cumul.PLAFONNEE, "base_reduite", 0.0)


def test_avant_2011_la_dentiste_qui_reprend_perd_sa_complementaire(simulateur):
    """Statuts de 2007, article 25 : « Le versement de la retraite complémentaire
    est suspendu pour tout allocataire qui reprend l'exercice de la profession de
    chirurgien-dentiste » — sous le seuil de la base aussi."""
    resultat, _ = _cumul(simulateur, 1946, 62.0,
                         _emploi(62.5, 64, affiliation="chirurgien_dentiste_ou_sage_femme",
                                 niveau=0.3),
                         _liberale("chirurgien_dentiste_ou_sage_femme"))
    servies = _servies(resultat, "carcdsf_complementaire")
    assert servies and all(t.debut < DateMois(2011, 2) for t, _ in servies)
    for tranche, complementaire in servies:
        assert _pension(tranche, "cnavpl").statut == cumul.PLAFONNEE
        assert (complementaire.statut, complementaire.motif) == (cumul.SUSPENDUE, "reprise")
        assert complementaire.reduction == pytest.approx(complementaire.montant)


@pytest.mark.parametrize("niveau", [3.0, 1.3])
def test_la_complementaire_des_medecins_perd_ce_que_la_base_n_absorbe_pas(simulateur, niveau):
    """Statuts de la CARMF, article 15, 3, depuis 2011 : au-delà du seuil, « le
    service de la pension est suspendu, conjointement à celui des autres
    pensions des régimes obligatoires de vieillesse versées par la caisse et à
    concurrence du montant du dépassement ». La base du médecin parti en 2016
    perd le dépassement depuis 2017 ; la complémentaire, ce qu'il en reste —
    à trois fois le salaire moyen, une part ; à 1,3 fois, rien."""
    resultat, _ = _cumul(simulateur, 1954, 62.0,
                         _emploi(63, 64.5, affiliation="medecin_liberal", niveau=niveau),
                         _liberale("medecin_liberal"))
    servies = _servies(resultat, "carmf_complementaire")
    assert servies
    for tranche, complementaire in servies:
        base = _pension(tranche, "cnavpl")
        seuil = simulateur.macro.plafond_securite_sociale(tranche.debut.annee) / 12
        reste = tranche.revenu - seuil - base.montant
        assert base.statut == cumul.REDUITE
        assert complementaire.regle == cumul.SECTIONS_STATUTS
        if niveau == 3.0:
            assert 0 < reste
            assert (complementaire.statut, complementaire.motif) == (cumul.REDUITE,
                                                                     "depassement")
            assert complementaire.reduction == pytest.approx(min(complementaire.montant, reste))
        else:
            assert reste <= 0 < tranche.revenu - seuil
            assert (complementaire.statut, complementaire.motif, complementaire.reduction) == (
                cumul.PLAFONNEE, "imputee_sur_la_base", 0.0)


def test_le_notaire_liberal_n_a_pas_droit_a_sa_complementaire(simulateur):
    """Statuts de la CPRN, depuis 2017 : « Le droit aux allocations est
    compatible avec l'exercice de la profession de notaire salarié [...] Il est
    incompatible avec l'exercice de la profession de notaire libéral » — sous
    le seuil de la base aussi."""
    resultat, _ = _cumul(simulateur, 1960, 62.25,
                         _emploi(62.5, 64, affiliation="notaire", niveau=0.3),
                         _liberale("notaire"))
    servies = _servies(resultat, "cprn_complementaire")
    assert servies
    for tranche, complementaire in servies:
        assert _pension(tranche, "cnavpl").statut == cumul.PLAFONNEE
        assert (complementaire.statut, complementaire.regle, complementaire.motif) == (
            cumul.NON_DUE, cumul.SECTIONS_STATUTS, "notaire_liberal")
        assert complementaire.reduction == pytest.approx(complementaire.montant)


def test_la_complementaire_des_officiers_ministeriels_change_de_regle_en_2026(simulateur):
    """Statuts de la CAVOM de 2020, article 15 : la base est diminuée du
    dépassement, puis, « Si le revenu dépasse le seuil après cette diminution,
    le montant du régime complémentaire est diminué à due concurrence du
    montant du dépassement » ; règlement de 2026, article 2 : « le montant du
    régime complémentaire est diminué à due concurrence du montant du
    dépassement », depuis août 2026, le premier mois entier de sa rédaction."""
    resultat, _ = _cumul(simulateur, 1962, 62.5,
                         _emploi(63, 65, affiliation="officier_ministeriel", niveau=3.0),
                         _liberale("officier_ministeriel"))
    aout = DateMois(2026, 8)
    servies = _servies(resultat, "cavom_complementaire")
    assert {t.debut < aout for t, _ in servies} == {True, False}
    for tranche, complementaire in servies:
        base = _pension(tranche, "cnavpl")
        seuil = simulateur.macro.plafond_securite_sociale(tranche.debut.annee) / 12
        depassement = tranche.revenu - seuil
        assert (complementaire.statut, complementaire.motif) == (cumul.REDUITE, "depassement")
        attendu = depassement - base.montant if tranche.debut < aout else depassement
        assert complementaire.reduction == pytest.approx(min(complementaire.montant, attendu))


@pytest.mark.parametrize("naissance, depart, attendu", [
    (1951, 61.0, (cumul.REDUITE, "depassement")),
    (1960, 62.25, (cumul.LIBRE, "sans_suspension")),
])
def test_la_complementaire_des_veterinaires_jusqu_en_2021(simulateur, naissance, depart,
                                                          attendu):
    """Statuts de la CARPV de 2011 : « le service de la pension est suspendu
    pendant la durée qui aurait procuré au vétérinaire un montant brut
    d'allocations au titre du régime complémentaire égal au montant du
    dépassement » — elle perd le dépassement ; les statuts de 2021, en vigueur
    en 2022, n'y laissent qu'une « cotisation non attributive de points »."""
    resultat, _ = _cumul(simulateur, naissance, depart,
                         _emploi(depart + 0.5, depart + 2, affiliation="veterinaire",
                                 niveau=2.0),
                         _liberale("veterinaire"))
    servies = _servies(resultat, "carpv_complementaire")
    assert servies
    for tranche, complementaire in servies:
        assert (complementaire.statut, complementaire.motif) == attendu
        if attendu[0] == cumul.REDUITE:
            seuil = simulateur.macro.plafond_securite_sociale(tranche.debut.annee) / 12
            assert complementaire.reduction == pytest.approx(
                min(complementaire.montant, tranche.revenu - seuil))
        else:
            assert complementaire.reduction == 0.0


def test_la_complementaire_des_agents_d_assurance_suit_sa_base_depuis_2026(simulateur):
    """Règlement de la CAVAMAC de 2026, article 3 : « Un assuré peut poursuivre
    ou reprendre une activité professionnelle dans les mêmes conditions que pour
    le régime de base » ; avant, « suspendu pour la même durée » que la base
    (statuts de 2011, article 14). La base réduite du dépassement : la
    complémentaire, entière jusqu'en juillet 2026, perd depuis août le
    dépassement comme elle."""
    resultat, _ = _cumul(simulateur, 1962, 62.5,
                         _emploi(63, 65, affiliation="agent_general_assurance", niveau=2.0),
                         _liberale("agent_general_assurance"))
    aout = DateMois(2026, 8)
    servies = _servies(resultat, "cavamac_complementaire")
    assert {t.debut < aout for t, _ in servies} == {True, False}
    for tranche, complementaire in servies:
        assert _pension(tranche, "cnavpl").statut == cumul.REDUITE
        if tranche.debut < aout:
            assert (complementaire.statut, complementaire.motif) == (cumul.PLAFONNEE,
                                                                     "base_reduite")
            continue
        seuil = simulateur.macro.plafond_securite_sociale(tranche.debut.annee) / 12
        assert (complementaire.statut, complementaire.motif) == (cumul.REDUITE, "depassement")
        assert complementaire.reduction == pytest.approx(
            min(complementaire.montant, tranche.revenu - seuil))


@pytest.mark.parametrize("metier, emploi, regime, attendu", [
    ("chirurgien_dentiste_ou_sage_femme", _emploi(62.5, 64), "carcdsf_complementaire",
     (cumul.LIBRE, "autre_regime")),
    ("pharmacien", _emploi(62.5, 64, affiliation="pharmacien", niveau=2.0),
     "cavp_complementaire", (cumul.LIBRE, "non_lue")),
])
def test_sans_activite_liberale_ou_sans_regle_lue_la_complementaire_est_entiere(
        simulateur, metier, emploi, regime, attendu):
    """La dentiste salariée après son départ : L. 643-6 ne vise que l'activité
    libérale, que ses statuts suivent ; le pharmacien, dont les statuts lus ne
    suspendent rien."""
    resultat, _ = _cumul(simulateur, 1960, 62.25, emploi, _liberale(metier))
    servies = _servies(resultat, regime)
    assert servies
    assert {(p.statut, p.motif) for _, p in servies} == {attendu}


def test_la_premiere_pension_de_2027_reduit_les_complementaires_apres_les_bases(simulateur):
    """L. 161-22, III, A, de 2027 : « Une pension de vieillesse personnelle
    servie au titre d'un régime légal ou rendu légalement obligatoire, de base ou
    complémentaire » ; la réduction « est appliquée, par priorité, sur les
    pensions versées par les régimes de retraite de base », et la somme des
    réductions ne peut excéder la réduction. La contractuelle devenue médecin,
    carrière longue partie en 2028 : avant l'âge légal, sa base perd tout son
    revenu, et ses deux complémentaires, l'Ircantec et la CARMF, se partagent ce
    qui reste au prorata de leurs montants."""
    resultat, _ = _cumul(simulateur, 1968, 60.0, _emploi(61, 64, niveau=0.45),
                         [Metier("contractuel_public", 17.0), Metier("medecin_liberal", 35.0)])
    complementaires = ("ircantec", "carmf_complementaire")
    avant = [t for t in resultat.tranches
             if _pension(t, "regime_general").statut == cumul.REDUITE]
    assert avant and len(avant) < len(resultat.tranches)
    for tranche in resultat.tranches:
        servies = [_pension(tranche, regime) for regime in complementaires]
        assert {p.regle for p in servies} == {cumul.RCI_2027}
        if tranche not in avant:
            assert {p.statut for p in servies} == {cumul.SEUIL_NON_PUBLIE}
            continue
        bases = [p for p in tranche.par_regime if p.regime in ("regime_general", "cnavpl")]
        revenu = tranche.revenu * cumul.assiette_csg(tranche.debut.annee)
        reste = revenu - sum(p.montant for p in bases)
        total = sum(p.montant for p in servies)
        assert 0 < reste < total
        for pension in servies:
            assert (pension.statut, pension.motif) == (cumul.REDUITE, "avant_l_age_legal")
            assert pension.reduction == pytest.approx(reste * pension.montant / total)


def test_les_regles_des_sections_sont_celles_de_leur_fiche():
    """La table des sections que les deux moteurs redisent est celle de la fiche
    ``cumul_emploi_retraite_complementaires_des_liberaux`` : chaque section, la
    règle de ses statuts et le premier mois où elle vaut."""
    from retraite_notionnelle.noyau import carte

    fiche = carte.fiches()["cumul_emploi_retraite_complementaires_des_liberaux"]
    version, = [v for v in fiche["versions"] if v["id"] == cumul.SECTIONS_STATUTS]
    table = {regime: [(str(debut), regle) for debut, regle in regles]
             for regime, regles in version["contenu"]["parametres"]["sections"].items()}
    assert table == {regime: [(f"{mois.annee:04d}-{mois.mois:02d}-01", regle)
                              for mois, regle in regles]
                     for regime, regles in cumul.REGLES_DES_SECTIONS.items()}


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
    """Chaque règle que le cumul cite est une version d'une des six fiches, et
    la règle de 2027 de chaque complémentaire est une version de la sienne."""
    from retraite_notionnelle.noyau import carte

    toutes = carte.fiches()
    versions = set()
    for fiche in ("cumul_emploi_retraite_et_retraite_progressive",
                  "cumul_emploi_retraite_fonction_publique",
                  "cumul_emploi_retraite_complementaire_des_independants",
                  "cumul_emploi_retraite_ircantec", "cumul_emploi_retraite_rco_agricole",
                  "cumul_emploi_retraite_complementaires_des_liberaux"):
        versions |= {v["id"] for v in toutes[fiche]["versions"]}
    citees = {valeur for nom, valeur in vars(cumul).items()
              if nom.isupper() and isinstance(valeur, str) and "_" in valeur
              and nom in ("AVANT_1983", "RUPTURE_1983", "PLAFOND_2004", "LIBERALISE_2009",
                          "PREMIERES_2015", "REDUCTION_2015", "AGES_2027", "FP_1970",
                          "FP_2004", "FP_2009", "FP_2015", "FP_2027", "RCI_AVANT_2009",
                          "RCI_2009", "RCI_2024", "RCI_2027", "IRCANTEC_AVANT_2004",
                          "IRCANTEC_2004", "IRCANTEC_2020", "RCO_AGRICOLE_2003",
                          "SECTIONS_STATUTS")}
    assert len(citees) == 21
    assert citees <= versions, citees - versions
    for fiche in ("cumul_emploi_retraite_ircantec", "cumul_emploi_retraite_rco_agricole",
                  "cumul_emploi_retraite_complementaires_des_liberaux"):
        assert cumul.RCI_2027 in {v["id"] for v in toutes[fiche]["versions"]}, fiche


# -- la suspension de la base des non-salariés, et la durée requise du libéral -----

def _cumul_prete(simulateur: Simulateur, naissance: int, depart: float, metiers: list[Metier],
                 emploi: dict, pensions: dict, revenus: dict):
    """Le cumul de cette carrière, d'une assurée née le 15 janvier, quand chaque
    régime de ``pensions`` sert cette pension annuelle et que l'activité rapporte,
    chaque année de ``revenus``, ce revenu brut : ce qu'un exemple de la caisse
    pose (``_cumul_exemple``, dans ``test_oracle.py``)."""
    from dataclasses import replace

    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="F", metiers=metiers, age_liquidation=depart,
        macro=simulateur.macro, jour_naissance=15, emploi_retraite=emploi)
    carriere = replace(carriere, lignes_apres_depart=tuple(
        replace(ligne, revenu=revenus.get(ligne.annee, ligne.revenu))
        for ligne in carriere.lignes_apres_depart))
    moteur = simulateur.scenario_actuel
    return cumul.cumuler(moteur, carriere, moteur.calculer(carriere),
                         lambda annee: (dict(pensions), 0.0),
                         simulateur.parametres.annee_courante)


def _mois_par_mois(resultat, regime) -> dict:
    """Le sort de la pension de ce régime, mois par mois : son statut, son motif
    et ce qui n'en est pas servi."""
    return {tranche.debut.plus_mois(k): (p.statut, p.motif, p.reduction)
            for tranche in resultat.tranches for p in tranche.par_regime
            if p.regime == regime for k in range(tranche.mois)}


@pytest.mark.parametrize("revenu, suspendus", [(22010.0, 5), (17610.0, 1), (40000.0, 12)])
def test_la_base_de_l_independant_n_est_suspendue_que_les_mois_du_depassement(
        simulateur, revenu, suspendus):
    """D. 634-11-5 de 2010 : la suspension vaut « pour un nombre de mois égal au
    rapport entre le montant du dépassement constaté et le montant mensuel net de
    la pension, arrondi à l'entier inférieur, sans que ce nombre puisse être
    inférieur à un, ni supérieur au nombre de mois » de l'activité de l'année ; la
    complémentaire « est suspendu[e] pour la même durée » (règlement du RCO de
    2009, article 23, II), ce que la circulaire RSI 2010/013 redit. L'artisane
    partie en 2008 reprend toute l'année 2010 ; sa pension de base, 1 000 € par
    mois, en vaut 929 net, la CSG et la CRDS de 2010 ôtées (7,1 %). Au-delà de la
    moitié du plafond, 17 310 €, 4 700 € font 5,06 mois : cinq, où la pension
    brute en ferait quatre ; 300 €, un mois, le minimum ; 22 690 €, 24 mois, que
    les douze de l'activité bornent. Le modèle place les mois suspendus à la fin
    de l'année : la caisse suspend après avoir constaté le dépassement."""
    resultat = _cumul_prete(simulateur, 1948, 60 + 4 / 12, [Metier("artisan", 30.0)],
                            _emploi(61 + 11 / 12, 62 + 11 / 12, affiliation="artisan"),
                            {"rsi": 12000.0, "rco_artisans": 3000.0}, {2010: revenu})
    base, complementaire = (_mois_par_mois(resultat, "rsi"),
                            _mois_par_mois(resultat, "rco_artisans"))
    assert sorted(base) == [DateMois(2010, m) for m in range(1, 13)]
    for mois, sort in base.items():
        if mois.mois > 12 - suspendus:
            assert sort == (cumul.SUSPENDUE, "depassement", 1000.0)
            assert complementaire[mois] == (cumul.SUSPENDUE, "depassement", 250.0)
        else:
            assert sort == (cumul.PLAFONNEE, cumul.HORS_DES_MOIS_SUSPENDUS, 0.0)
            assert complementaire[mois] == (cumul.PLAFONNEE, cumul.HORS_DES_MOIS_SUSPENDUS, 0.0)


@pytest.mark.parametrize("depassement, suspendus", [(1400.0, 3), (400.0, 0)])
def test_la_base_du_liberal_n_est_suspendue_que_les_mois_du_depassement(
        simulateur, depassement, suspendus):
    """D. 643-10-2, depuis le 17 janvier 2011 : le même rapport, arrondi à
    l'entier inférieur, « sans que ce nombre puisse être supérieur » aux mois
    d'affiliation de l'année — et sans minimum. La dentiste partie en 2012
    exerce toute l'année 2013 ; sa pension de base de 500 € par mois en vaut
    463,38 net, la CSG, la CRDS et la CASA d'avril ôtées (7,325 % sur l'année).
    1 400 € au-delà du plafond la suspendent trois mois, où la pension brute en
    ferait deux ; 400 €, aucun. Sa complémentaire, que les statuts de la CARCDSF
    suspendent « pour la même durée » que la base, la suit."""
    resultat = _cumul_prete(
        simulateur, 1951, 61.5, _liberale("chirurgien_dentiste_ou_sage_femme"),
        _emploi(61 + 11 / 12, 62 + 11 / 12, affiliation="chirurgien_dentiste_ou_sage_femme"),
        {"cnavpl": 6000.0, "carcdsf_complementaire": 12000.0},
        {2013: simulateur.macro.plafond_securite_sociale(2013) + depassement})
    base, complementaire = (_mois_par_mois(resultat, "cnavpl"),
                            _mois_par_mois(resultat, "carcdsf_complementaire"))
    assert sorted(base) == [DateMois(2013, m) for m in range(1, 13)]
    for mois, sort in base.items():
        if mois.mois > 12 - suspendus:
            assert sort == (cumul.SUSPENDUE, "depassement", 500.0)
            assert complementaire[mois] == (cumul.SUSPENDUE, "depassement", 1000.0)
        else:
            assert sort == (cumul.PLAFONNEE, cumul.HORS_DES_MOIS_SUSPENDUS, 0.0)
            assert complementaire[mois] == (cumul.PLAFONNEE, cumul.HORS_DES_MOIS_SUSPENDUS, 0.0)


def test_la_complementaire_des_medecins_perd_ce_que_les_mois_suspendus_n_absorbent_pas(
        simulateur):
    """Statuts de la CARMF, article 15, 3 : la complémentaire est suspendue
    « conjointement à celui des autres pensions [...] versées par la caisse et à
    concurrence du montant du dépassement ». Le médecin parti en 2012 exerce
    toute l'année 2013, 2 270 € au-delà du plafond : sa base de 500 € par mois
    est suspendue quatre mois (2 270 sur 463,38 € nets, 4,9), de septembre à
    décembre ; les 2 000 € qu'ils retiennent laissent 270 € du dépassement à la
    complémentaire, 22,50 € par mois."""
    resultat = _cumul_prete(
        simulateur, 1951, 61.5, _liberale("medecin_liberal"),
        _emploi(61 + 11 / 12, 62 + 11 / 12, affiliation="medecin_liberal"),
        {"cnavpl": 6000.0, "carmf_complementaire": 12000.0},
        {2013: simulateur.macro.plafond_securite_sociale(2013) + 2270.0})
    base, complementaire = (_mois_par_mois(resultat, "cnavpl"),
                            _mois_par_mois(resultat, "carmf_complementaire"))
    assert [mois.mois for mois, sort in sorted(base.items())
            if sort[0] == cumul.SUSPENDUE] == [9, 10, 11, 12]
    assert {sort[:2] for sort in complementaire.values()} == {(cumul.REDUITE, "depassement")}
    assert sum(sort[2] for sort in complementaire.values()) == pytest.approx(270.0)


@pytest.mark.parametrize("part_du_plafond, statut", [(0.7, cumul.PLAFONNEE),
                                                     (1.2, cumul.SUSPENDUE)])
def test_avant_2011_le_seuil_du_liberal_est_le_plafond_de_l_annee(simulateur, part_du_plafond,
                                                                 statut):
    """D. 643-10, de 2004 au 16 janvier 2011 : le seuil « est égal, annuellement,
    au plafond », que seule la rédaction de 2011 rapporte « à la durée
    d'affiliation » ; au-delà, « le service de sa pension est suspendu »
    (L. 643-6), sans décret qui en compte les mois. Le médecin parti en 2008
    exerce de juillet à décembre 2009 : à 70 % du plafond de l'année, il reste
    sous le seuil ; à 120 %, sa pension est suspendue chacun des six mois."""
    resultat = _cumul_prete(
        simulateur, 1946, 62.0, _liberale("medecin_liberal"),
        _emploi(63 + 5 / 12, 63 + 11 / 12, affiliation="medecin_liberal"),
        {"cnavpl": 6000.0},
        {2009: part_du_plafond * simulateur.macro.plafond_securite_sociale(2009)})
    base = _mois_par_mois(resultat, "cnavpl")
    assert sorted(base) == [DateMois(2009, m) for m in range(7, 13)]
    assert {sort[0] for sort in base.values()} == {statut}


@pytest.mark.parametrize("debut, depart, integral", [(26.0, 62.0, False), (21.0, 63.0, True)])
def test_le_liberal_ne_cumule_entierement_qu_avec_la_duree_requise(simulateur, debut, depart,
                                                                   integral):
    """L. 643-6 : la pension « peut être entièrement cumulée » à l'âge légal
    « lorsque l'assuré justifie d'une durée d'assurance [...] au moins égale à la
    limite » de L. 351-1 — celle du régime général pour sa génération, 165
    trimestres pour 1954 —, même quand aucun de ses régimes, tous en points, ne
    la lui oppose. Le médecin seulement libéral, à 144 trimestres, n'y est pas :
    sa base perd le dépassement ; à 168, il cumule entièrement."""
    resultat, echeancier = _cumul(
        simulateur, 1954, depart,
        _emploi(depart + 1, depart + 2.5, affiliation="medecin_liberal", niveau=3.0),
        [Metier("medecin_liberal", debut)])
    assert echeancier.au_depart.trimestres_requis == 0
    statuts = {_pension(t, "cnavpl").statut for t in resultat.tranches}
    if integral:
        assert resultat.integral_depuis == resultat.debut
        assert statuts == {cumul.INTEGRAL}
    else:
        assert resultat.integral_depuis is None
        assert statuts == {cumul.REDUITE}


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


def test_la_nouvelle_pension_de_l_independant_porte_son_revenu_annuel_moyen(simulateur):
    """Le commerçant en cumul intégral de février 2023 à juillet 2025 se
    constitue sa nouvelle pension sur son revenu annuel moyen, et non sur le
    salaire mensuel moyen du salarié (R. 351-29, III) : de 2023 à 2025,
    D. 634-1 écarte R. 351-29, et R. 634-1 fait la moyenne des revenus des
    années civiles qui valident un trimestre, « il est tenu compte du revenu
    annuel de l'année durant laquelle la pension mentionnée à l'article
    L. 161-22-1-1 prend effet » ; depuis 2026, D. 634-3 applique R. 351-29,
    dont « Les III et IV ne sont pas applicables ». Ses trente mois tombent
    sur trois années civiles, 2025, l'année de l'effet, comprise : la moyenne
    de ses revenus revalorisés vaut dix fois le salaire mensuel moyen d'une
    salariée au même revenu, et non douze."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0)]
    emploi = _emploi(63, 65.5, affiliation="commercant", niveau=0.5)
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=metiers, age_liquidation=62.25,
        macro=simulateur.macro, jour_naissance=15, emploi_retraite=emploi)
    echeancier = simulateur.echeancier(carriere)
    [base] = [p for p in echeancier.au_depart.droits_apres_depart.pensions
              if p.regime == "regime_general"]
    salariee, _ = _droits(simulateur, 1960, 62.25, emploi | {
        "affiliation": "salarie_prive_non_cadre"}, metiers)
    [du_salarie] = [p for p in salariee.pensions if p.regime == "regime_general"]
    assert base.date_effet == DateMois(2025, 8)
    assert base.trimestres == du_salarie.trimestres == 12
    # Les revenus de 2023, 2024 et 2025, sur onze, douze et sept mois, chacun
    # sous le plafond de ses mois, revalorisés au mois de l'effet.
    macro = simulateur.macro
    lignes = {ligne.annee: ligne.revenu for ligne in carriere.lignes_apres_depart}
    assert sorted(lignes) == [2023, 2024, 2025]
    for annee, mois in ((2023, 11), (2024, 12), (2025, 7)):
        assert lignes[annee] < macro.plafond_securite_sociale(annee) * mois / 12
    revalorises = [lignes[annee] * macro.coefficient_revalorisation_portee_au_compte(
        annee, 2025, 8) for annee in (2023, 2024, 2025)]
    assert base.revenu_annuel_moyen == pytest.approx(sum(revalorises) / 3, rel=1e-12)
    assert base.revenu_annuel_moyen == pytest.approx(du_salarie.salaire_mensuel * 10,
                                                     rel=1e-12)
    assert base.salaire_mensuel == 0.0
    requis = echeancier.au_depart.trimestres_requis
    assert base.brute == pytest.approx(base.revenu_annuel_moyen * 0.5 * min(1.0, 12 / requis))
    assert base.montant == pytest.approx(min(base.brute, base.plafond))
    # Le journal dit sur quoi elle se calcule.
    servies = {e.id: e for e in echeancier.journal.servi(
        cumul.jour(base.date_effet), None, "composante")}
    assert "revenu annuel moyen" in servies["seconde_regime_general"].contenu["detail"]


def test_la_nouvelle_pension_du_micro_entrepreneur_porte_son_revenu_cotise(simulateur):
    """Le micro-entrepreneur en cumul intégral se constitue sa nouvelle pension
    sur le revenu que son forfait cotise, celui de ses trimestres et de son
    revenu annuel moyen (circulaire Cnav n° 2024-23, point 4 ; R. 634-1, puis
    R. 351-29, I, B, et D. 634-3), et non sur son revenu abattu. De février 2023
    à juillet 2024, ses ventes portent 12,3 % × 41,80 % / 17,75 % de leur
    montant, 0,9988 fois leur revenu abattu (D. 613-4, D. 613-6, D. 633-3)."""
    emploi = _emploi(63, 64.5, affiliation="micro_entrepreneur", niveau=0.5)
    metiers = [Metier("salarie_prive_non_cadre", 20.0)]
    abattu, _ = _droits(simulateur, 1960, 62.25, emploi, metiers)
    cotise, _ = _droits(simulateur, 1960, 62.25, emploi | {"micro": "vente"}, metiers)
    [base_abattue] = [p for p in abattu.pensions if p.regime == "regime_general"]
    [base_cotisee] = [p for p in cotise.pensions if p.regime == "regime_general"]
    assert base_cotisee.trimestres == base_abattue.trimestres > 0
    assert base_abattue.revenu_annuel_moyen > 0
    assert base_cotisee.revenu_annuel_moyen == pytest.approx(
        base_abattue.revenu_annuel_moyen * 0.123 * 0.418 / 0.1775 / 0.29, rel=1e-9)


def test_la_cotisation_minimale_porte_la_nouvelle_pension_de_l_artisane(simulateur):
    """L'artisane en cumul intégral de janvier 2024 à décembre 2025 déclare 5 %
    du salaire moyen, quelque 2 000 € par an. Elle cotise pourtant sur « 450
    fois le montant horaire du salaire minimum de croissance en vigueur le 1er
    janvier de l'année considérée » (D. 633-2), que rien n'écarte pour le
    pensionné, et ces cotisations valident trois trimestres par an (R. 351-9).
    Sa nouvelle pension « correspond aux cotisations versées » (R. 634-1 ;
    R. 351-29, I, B, par D. 634-3) : six trimestres, sur le revenu annuel moyen
    des deux assiettes minimales revalorisées, 450 × 11,65 € en 2024 et
    450 × 11,88 € en 2025, et non deux trimestres sur son revenu déclaré."""
    emploi = _emploi(63 + 11 / 12, 65 + 11 / 12, affiliation="artisan", niveau=0.05)
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        age_liquidation=62.25, macro=simulateur.macro, jour_naissance=15,
        emploi_retraite=emploi)
    minimales = {2024: 450 * 11.65, 2025: 450 * 11.88}
    lignes = {ligne.annee: ligne for ligne in carriere.lignes_apres_depart}
    assert sorted(lignes) == [2024, 2025]
    assert all(lignes[annee].fraction_annee == 1.0 for annee in lignes)
    assert all(lignes[annee].revenu < minimales[annee] / 2 for annee in lignes)
    droits = simulateur.echeancier(carriere).au_depart.droits_apres_depart
    [base] = [p for p in droits.pensions if p.regime == "regime_general"]
    assert base.date_effet == DateMois(2026, 1)
    assert base.trimestres == 6
    macro = simulateur.macro
    revalorisees = [minimales[annee] * macro.coefficient_revalorisation_portee_au_compte(
        annee, 2026, 1) for annee in (2024, 2025)]
    assert base.revenu_annuel_moyen == pytest.approx(sum(revalorisees) / 2, rel=1e-12)


def test_le_rci_ouvre_une_seconde_retraite_sur_les_periodes_de_2025(simulateur):
    """Le commerçant en cumul intégral de février 2023 à juillet 2025 se
    constitue des droits au RCI, mais sur ses seuls mois de 2025 : le règlement
    du régime ne les ouvre en cumul intégral que par son article 27, dans la
    rédaction de l'arrêté du 19 juin 2024, en vigueur le 1er janvier 2025
    (article 2 de l'arrêté) ; jusque-là, « les cotisations versées au présent
    régime par un retraité de ce régime afférentes à des périodes postérieures à
    la date d'arrêt du compte ne sont pas productives de droits » (article 4).
    Ses points s'achètent avec 8,1 % de son revenu sous le plafond (D. 635-7),
    au prix de 2025, 21,532 € ; la seconde pension, « calculée, liquidée et
    servie dans les conditions applicables à la pension de vieillesse du présent
    régime » et demandée « en même temps que celle du régime de base », les sert
    sans coefficient, la nouvelle pension de base étant au taux plein, à sa
    date, au point de 2025, 1,335 €."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0)]
    emploi = _emploi(63, 65.5, affiliation="commercant", niveau=0.5)
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=metiers, age_liquidation=62.25,
        macro=simulateur.macro, jour_naissance=15, emploi_retraite=emploi)
    droits = simulateur.echeancier(carriere).au_depart.droits_apres_depart
    pensions = {p.regime: p for p in droits.pensions}
    assert set(pensions) == {"regime_general", "rci"}
    rci = pensions["rci"]
    assert rci.date_effet == pensions["regime_general"].date_effet == DateMois(2025, 8)
    [revenu] = [ligne.revenu for ligne in carriere.lignes_apres_depart if ligne.annee == 2025]
    assert revenu < simulateur.macro.plafond_securite_sociale(2025) * 7 / 12
    assert rci.points == pytest.approx(revenu * 0.081 / 21.532, rel=1e-12)
    assert rci.montant == pytest.approx(rci.points * 1.335, rel=1e-12)
    assert (rci.trimestres, rci.plafond, rci.revenu_annuel_moyen) == (0, None, 0.0)
    # Quarante points et plus : elle est servie (règlement, article 39).
    assert rci.points >= 40 and rci.capital is None


def test_avant_2025_le_rci_n_ouvre_rien_au_retraite(simulateur):
    """Le même commerçant, en cumul jusqu'en juillet 2024 : sa nouvelle pension
    de base, et rien au RCI, ses cotisations de retraité n'y étant « pas
    productives de droits » avant le 1er janvier 2025 (règlement, article 4)."""
    droits, _ = _droits(simulateur, 1960, 62.25,
                        _emploi(63, 64.5, affiliation="commercant", niveau=0.5),
                        [Metier("salarie_prive_non_cadre", 20.0)])
    assert {p.regime for p in droits.pensions} == {"regime_general"}


def test_le_micro_entrepreneur_achete_ses_points_de_rci_avec_son_forfait(simulateur):
    """Le micro-entrepreneur vendeur en cumul intégral jusqu'en juillet 2025 :
    ses points de RCI de 2025 s'achètent avec la part complémentaire de son
    forfait, 16,5 % de ses 12,3 % de ventes (D. 613-4, D. 613-6), comme ceux de
    sa première pension, au prix de 2025, 21,532 €."""
    emploi = _emploi(63, 65.5, affiliation="micro_entrepreneur", niveau=0.5) | {
        "micro": "vente"}
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        age_liquidation=62.25, macro=simulateur.macro, jour_naissance=15,
        emploi_retraite=emploi)
    droits = simulateur.echeancier(carriere).au_depart.droits_apres_depart
    [rci] = [p for p in droits.pensions if p.regime == "rci"]
    [abattu] = [ligne.revenu for ligne in carriere.lignes_apres_depart if ligne.annee == 2025]
    ventes = abattu / 0.29
    assert rci.points == pytest.approx(ventes * 0.123 * 0.165 / 21.532, rel=1e-12)
    assert rci.montant == pytest.approx(rci.points * 1.335, rel=1e-12)


def test_la_seconde_retraite_du_rci_de_moins_de_quarante_points_est_versee_en_une_fois(
        simulateur):
    """L'artisane qui déclare 5 % du salaire moyen en cumul intégral de janvier
    2024 à décembre 2025 : ses mois de 2025 lui achètent des points au RCI, 8,1 %
    de son revenu au prix de 2025, 21,532 €, moins de quarante. Sa seconde
    pension, « calculée, liquidée et servie dans les conditions applicables à la
    pension de vieillesse du présent régime » (article 27), est remplacée par un
    versement forfaitaire unique : ses points par le revenu de référence de sa
    date d'effet, janvier 2026, 21,726 € (article 39)."""
    emploi = _emploi(63 + 11 / 12, 65 + 11 / 12, affiliation="artisan", niveau=0.05)
    carriere = Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        age_liquidation=62.25, macro=simulateur.macro, jour_naissance=15,
        emploi_retraite=emploi)
    droits = simulateur.echeancier(carriere).au_depart.droits_apres_depart
    [rci] = [p for p in droits.pensions if p.regime == "rci"]
    [revenu] = [ligne.revenu for ligne in carriere.lignes_apres_depart if ligne.annee == 2025]
    assert rci.date_effet == DateMois(2026, 1)
    assert rci.points == pytest.approx(revenu * 0.081 / 21.532, rel=1e-12)
    assert rci.points < 40
    assert rci.capital == pytest.approx(rci.points * 21.726, rel=1e-12)
    assert rci.donnees()["capital"] == rci.capital


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
