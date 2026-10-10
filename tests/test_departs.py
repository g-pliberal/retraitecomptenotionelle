"""Le départ de chaque régime (docs/architecture.md, § 7.4 ; fiche
``liquidation_regime_par_regime``).

Le droit ne connaît pas de départ « tous régimes » : chaque régime sert sa
pension quand l'assuré en remplit les conditions. L'aide-soignante passée du
privé à l'hôpital part à cinquante-sept ans, son régime général attend l'âge
légal ; le militaire passé au privé touche sa pension dès sa sortie de
l'armée ; le RAFP attend l'âge légal. Tout le reste liquide au départ
déclaré, et une carrière d'un seul départ ne change pas. Chaque départ voit
servies les pensions des précédents : le minimum contributif s'écrête sur
elles (R. 173-7). Le résultat est dans les euros du départ déclaré, chaque
pension gardant sa date et son montant à cette date, que « faire vivre »
reprend.
"""

from __future__ import annotations

from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import departs, liquidation
from retraite_notionnelle.revalorisation import faire_vivre
from retraite_notionnelle.saisie import AGE_LIQUIDATION_MAXIMAL
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, metiers: list[Metier], naissance: int = 1962,
              liquidation: float = 64, sexe: str = "H", **kwargs) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, **kwargs)


def _aide_soignante(simulateur: Simulateur, liquidation: float = 57) -> Carriere:
    """Dix ans dans le privé, puis vingt-sept à l'hôpital en catégorie active."""
    return _carriere(simulateur, [Metier("salarie_prive_non_cadre", 20.0),
                                  Metier("fonctionnaire_territorial_hospitalier_actif", 30.0)],
                     naissance=1965, liquidation=liquidation, sexe="F")


def _militaire_puis_prive(simulateur: Simulateur) -> Carriere:
    """Dix-sept ans sous l'uniforme, puis le privé jusqu'à soixante-quatre ans."""
    return _carriere(simulateur, [Metier("militaire", 18.0),
                                  Metier("salarie_prive_non_cadre", 35.0)], naissance=1965)


def _resume(liste) -> list[tuple[DateMois, list[str], str]]:
    return [(depart.date, sorted(depart.regimes), depart.motif) for depart in liste]


# -- quand chaque régime liquide -----------------------------------------------

def test_le_regime_general_de_l_agent_de_categorie_active_attend_l_age_legal(simulateur):
    """Partie de l'hôpital à cinquante-sept ans, l'aide-soignante n'a pas l'âge
    légal : son régime général et ses complémentaires attendent le leur."""
    moteur = simulateur.scenario_actuel
    carriere = _aide_soignante(simulateur)
    legal = carriere.date_de_l_age(departs.age_legal(moteur, carriere))
    assert _resume(departs.departs(moteur, carriere)) == [
        (carriere.date_liquidation, ["cnracl"], departs.MOTIF_DEPART),
        (legal, ["arrco", "arrco_tranche_2", "regime_general"], departs.MOTIF_OUVERTURE),
    ]


def test_la_pension_militaire_est_servie_des_la_sortie_de_l_armee(simulateur):
    """Le militaire qui a ses services liquide en quittant l'armée : c'est la
    seule pension que la présomption fasse demander avant le départ."""
    moteur = simulateur.scenario_actuel
    carriere = _militaire_puis_prive(simulateur)
    liste = departs.departs(moteur, carriere)
    assert _resume(liste)[0] == (DateMois(2000, 1), ["fonction_publique_etat"],
                                 departs.MOTIF_SORTIE)
    assert liste[-1].date == carriere.date_liquidation
    assert "regime_general" in liste[-1].regimes


def test_le_rafp_attend_l_age_legal(simulateur):
    """Le policier parti à cinquante-quatre ans touche sa pension ; sa retraite
    additionnelle attend l'âge de L. 161-17-2 (décret n° 2004-569, article 6)."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("fonctionnaire_etat_super_actif", 22.0)],
                         naissance=1970, liquidation=54, part_primes=0.25)
    legal = carriere.date_de_l_age(departs.age_legal(moteur, carriere))
    assert _resume(departs.departs(moteur, carriere)) == [
        (carriere.date_liquidation, ["fonction_publique_etat"], departs.MOTIF_DEPART),
        (legal, ["rafp"], departs.MOTIF_OUVERTURE),
    ]


def test_sans_primes_le_rafp_ne_fait_pas_un_depart_de_plus(simulateur):
    """Le fonctionnaire qui n'a pas de primes n'acquiert rien au RAFP : il n'y
    a pas de pension nulle à attendre."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("fonctionnaire_etat_super_actif", 22.0)],
                         naissance=1970, liquidation=54)
    assert _resume(departs.departs(moteur, carriere)) == [
        (carriere.date_liquidation, [], departs.MOTIF_DEPART)]


@pytest.mark.parametrize("metiers, liquidation", [
    ([Metier("salarie_prive_non_cadre", 22.0)], 64),
    # Tout est ouvert au départ : un seul, même entre deux régimes.
    ([Metier("salarie_prive_non_cadre", 22.0), Metier("fonctionnaire_etat", 40.0)], 64),
    # Rien n'est ouvert au départ : un seul, que la page dit non ouvert.
    ([Metier("salarie_prive_non_cadre", 22.0)], 55),
])
def test_un_seul_depart_quand_tout_liquide_ensemble(simulateur, metiers, liquidation):
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, metiers, liquidation=liquidation)
    assert _resume(departs.departs(moteur, carriere)) == [
        (carriere.date_liquidation, [], departs.MOTIF_DEPART)]


def test_l_agent_de_categorie_active_parti_trop_tot_n_a_qu_un_depart(simulateur):
    """Aucune unité n'est ouverte à cinquante-deux ans : le départ reste unique,
    et la liquidation le dit non ouverte, comme avant."""
    moteur = simulateur.scenario_actuel
    carriere = _aide_soignante(simulateur, liquidation=52)
    assert len(departs.departs(moteur, carriere)) == 1
    assert not moteur.calculer(carriere).liquidation_ouverte


# -- chaque départ liquidé -------------------------------------------------------

def test_chaque_depart_ne_liquide_que_ses_regimes_sur_la_carriere_a_sa_date(simulateur):
    moteur = simulateur.scenario_actuel
    carriere = _aide_soignante(simulateur)
    liste = departs.departs(moteur, carriere)
    liquidations = departs.liquider_les_departs(
        moteur, carriere, liquidation.Contexte(moteur), liste=liste)
    for depart, liquidee in zip(liste, liquidations):
        assert {p.regime for p in liquidee.regimes} == set(depart.regimes)
        assert liquidee.demande.date_effet == depart.date_effet
        assert liquidee.carriere.date_liquidation == depart.date
        assert liquidee.ouverture.ouverte


def test_le_minimum_contributif_s_ecrete_sur_les_pensions_deja_servies(simulateur):
    """R. 173-7 : le plafond d'écrêtement compte les pensions du mois de la
    date d'effet, celles que les départs précédents servent comprises."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 20.0, 0.3)])
    demande = liquidation.demande_de_depart(carriere)
    contexte = liquidation.Contexte(moteur)
    seule = liquidation.liquider(demande, liquidation.Etat(carriere), contexte)
    assert seule.complements.minimum_applique
    servie = departs.PensionServie("fonction_publique_etat", 100_000.0)
    etat = liquidation.Etat(carriere, servies=(servie,))
    assert etat.total_servi == 100_000.0
    ecretee = liquidation.liquider(demande, etat, contexte)
    assert not ecretee.complements.minimum_applique
    assert ecretee.total < seule.total


# -- le résultat, en euros du départ déclaré -------------------------------------

def test_le_resultat_est_la_pension_complete_en_euros_du_depart(simulateur):
    """Chaque pension garde sa date et son montant à cette date ; celle qui ne
    commence qu'après le départ y est ramenée par les prix, et le total est la
    pension complète."""
    moteur = simulateur.scenario_actuel
    carriere = _aide_soignante(simulateur)
    resultat = moteur.calculer(carriere)
    assert [(d.date_effet, d.motif) for d in resultat.departs] == [
        ("2022-02-01", departs.MOTIF_DEPART), ("2027-11-01", departs.MOTIF_OUVERTURE)]
    prix = moteur.macro.coefficient_prix(2027, 2022)
    for pension in resultat.pensions_par_regime:
        if pension.date_effet == "2027-11-01":
            assert pension.montant == pytest.approx(pension.montant_a_l_effet * prix)
            assert "servie à partir du 1er novembre 2027" in pension.detail
        else:
            assert pension.montant == pension.montant_a_l_effet
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    assert resultat.pension_annuelle == pytest.approx(
        sum(p.montant for p in resultat.pensions_par_regime) + majoration
        - resultat.pension_hors_repartition)
    assert sum(d.montant for d in resultat.departs) == pytest.approx(
        resultat.pension_annuelle + resultat.pension_hors_repartition)


def test_la_pension_servie_avant_le_depart_y_est_revalorisee(simulateur):
    moteur = simulateur.scenario_actuel
    resultat = moteur.calculer(_militaire_puis_prive(simulateur))
    [militaire] = [p for p in resultat.pensions_par_regime
                   if p.regime == "fonction_publique_etat"]
    assert militaire.date_effet == "2000-01-01"
    assert militaire.montant > militaire.montant_a_l_effet
    assert "servie depuis le 1er janvier 2000" in militaire.detail


def test_la_pension_militaire_d_avant_2004_a_son_minimum_garanti(simulateur):
    """Liquidée à sa sortie de l'armée en 2000, la pension de dix-sept ans de
    services est portée au minimum garanti de L. 17 d'avant 2004 : 4 % de la
    référence « par année de services effectifs et de bonifications prévues à
    l'article L. 12 » (LEGIARTI000006362711) — dix-sept ans, et trois ans et
    demi de bonification du cinquième (L. 12, i) : 82 %."""
    moteur = simulateur.scenario_actuel
    resultat = moteur.calculer(_militaire_puis_prive(simulateur))
    [militaire] = [p for p in resultat.pensions_par_regime
                   if p.regime == "fonction_publique_etat"]
    plancher, _ = moteur.minimum_garanti.montant(2000, 82)
    assert militaire.montant_a_l_effet == pytest.approx(plancher)
    assert plancher == pytest.approx(0.82 * moteur.minimum_garanti.reference(2000)[0])
    assert "porté au minimum garanti" in militaire.detail
    assert any(a.code == "minimum_garanti" for a in resultat.avantages_appliques)


def test_la_liquidation_fictive_valorise_tout_a_une_date(simulateur):
    """La valorisation des droits acquis liquide tout à la date qu'elle
    demande : elle ne suit pas les départs."""
    moteur = simulateur.scenario_actuel
    resultat = moteur.calculer(_aide_soignante(simulateur), nature="fictive")
    assert resultat.departs == ()
    assert all(p.date_effet is None for p in resultat.pensions_par_regime)


def test_un_seul_depart_ne_date_aucune_pension(simulateur):
    moteur = simulateur.scenario_actuel
    resultat = moteur.calculer(_carriere(simulateur, [Metier("salarie_prive_non_cadre", 22.0)]))
    assert resultat.departs == ()
    assert all(p.date_effet is None and p.montant_a_l_effet is None
               for p in resultat.pensions_par_regime)


# -- l'échéancier, et faire vivre ---------------------------------------------------

def test_l_echeancier_inscrit_un_depart_par_date(simulateur):
    """Le départ déclaré est un acte ; les autres dates, la présomption
    ``depart_de_chaque_regime`` les induit."""
    carriere = _aide_soignante(simulateur)
    journal = simulateur.echeancier(carriere).journal
    evenements = {e.contenu.id: e.contenu for e in journal if e.sorte == "evenement"}
    assert evenements["depart_assure_2022-02-01"].origine == "acte"
    assert evenements["depart_assure_2027-11-01"].origine == "induit"
    assert evenements["depart_assure_2027-11-01"].vise == {
        "regimes": ["arrco", "arrco_tranche_2", "regime_general"]}
    assert sum(e.sorte == "liquidation" for e in journal) == 2


def test_faire_vivre_ne_sert_une_pension_qu_a_partir_de_sa_date(simulateur):
    """À l'échéance de 2026, le régime général de l'aide-soignante ne lui est
    pas encore servi ; il l'est en 2028, parti de son propre montant."""
    moteur = simulateur.scenario_actuel
    carriere = _aide_soignante(simulateur)
    resultat = moteur.calculer(carriere)
    en_2026 = faire_vivre(simulateur, carriere, resultat, 2026)
    assert {r.regime for r in en_2026.regimes} == {"cnracl"}
    en_2028 = faire_vivre(simulateur, carriere, resultat, 2028)
    general = {r.regime: r for r in en_2028.regimes}["regime_general"]
    [pension] = [p for p in resultat.pensions_par_regime if p.regime == "regime_general"]
    assert general.au_depart == pension.montant_a_l_effet


# -- la date que la personne dit ----------------------------------------------------

def _venue_du_prive(simulateur: Simulateur, **demandes: float) -> Carriere:
    """Treize ans dans le privé puis la fonction publique de l'État, partie à
    soixante-deux ans en 2022, sans la durée du taux plein."""
    return _carriere(simulateur, [Metier("salarie_prive_non_cadre", 25.25),
                                  Metier("fonctionnaire_etat", 38.25)],
                     naissance=1960, liquidation=62, sexe="F",
                     demandes_de_pension=demandes or None)


def test_une_pension_demandee_plus_tard_se_liquide_a_sa_date(simulateur):
    """Son régime général, demandé à soixante-sept ans, n'a plus de décote : il
    se liquide ce jour-là, avec ses complémentaires, et le départ est un acte
    de la personne, non une présomption."""
    moteur = simulateur.scenario_actuel
    presumee = _venue_du_prive(simulateur)
    carriere = _venue_du_prive(simulateur, regime_general=67)
    liste, demandes = departs.departs_et_demandes(moteur, carriere)
    assert _resume(liste) == [
        (carriere.date_liquidation, ["fonction_publique_etat"], departs.MOTIF_DEPART),
        (carriere.date_de_l_age(67), ["arrco", "arrco_tranche_2", "regime_general"],
         departs.MOTIF_DEMANDE),
    ]
    assert demandes == (departs.DemandeExaminee(
        "regime_general", carriere.date_de_l_age(67), carriere.date_de_l_age(67),
        departs.MOTIF_DEMANDE),)
    general = {p.regime: p for p in moteur.calculer(carriere).pensions_par_regime}
    decote = {p.regime: p for p in moteur.calculer(presumee).pensions_par_regime}
    assert general["regime_general"].montant_a_l_effet > 1.4 * decote["regime_general"].montant
    journal = simulateur.echeancier(carriere).journal
    evenements = {e.contenu.id: e.contenu for e in journal if e.sorte == "evenement"}
    demandee = departs.Depart(carriere.date_de_l_age(67)).date_effet
    assert evenements[f"depart_assure_{demandee}"].origine == "acte"


def test_une_demande_n_avance_jamais_une_pension(simulateur):
    """Demandé avant le départ, le régime général est servi au départ ;
    demandé avant l'âge légal par l'aide-soignante partie à cinquante-sept
    ans, il l'est à l'âge qui le lui ouvre. Chaque demande dit pourquoi."""
    moteur = simulateur.scenario_actuel
    carriere = _venue_du_prive(simulateur, regime_general=60)
    liste, [demande] = departs.departs_et_demandes(moteur, carriere)
    assert liste == (departs.Depart(carriere.date_liquidation),)
    assert (demande.retenue, demande.motif) == (carriere.date_liquidation,
                                                departs.MOTIF_DEPART)
    soignante = _aide_soignante(simulateur)
    tot = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 20.0),
                                 Metier("fonctionnaire_territorial_hospitalier_actif", 30.0)],
                    naissance=1965, liquidation=57, sexe="F",
                    demandes_de_pension={"regime_general": 60})
    legal = soignante.date_de_l_age(departs.age_legal(moteur, soignante))
    liste, [demande] = departs.departs_et_demandes(moteur, tot)
    assert _resume(liste) == _resume(departs.departs(moteur, soignante))
    assert (demande.retenue, demande.motif) == (legal, departs.MOTIF_OUVERTURE)


def test_une_complementaire_suit_son_regime_de_base_sauf_plus_tard(simulateur):
    """L'Arrco demandée avant son régime de base le suit ; demandée après
    lui, elle se liquide à sa date, seule."""
    moteur = simulateur.scenario_actuel
    avant = _venue_du_prive(simulateur, arrco=59)
    [demande] = departs.demandes(moteur, avant)
    assert (demande.retenue, demande.motif) == (avant.date_liquidation, departs.ENSEMBLE)
    apres = _venue_du_prive(simulateur, arrco=65)
    liste, [demande] = departs.departs_et_demandes(moteur, apres)
    assert _resume(liste)[-1] == (apres.date_de_l_age(65), ["arrco"], departs.MOTIF_DEMANDE)
    assert demande.motif == departs.MOTIF_DEMANDE


def test_un_regime_sans_pension_le_dit(simulateur):
    """Demander la pension d'un régime où la carrière n'a rien acquis ne
    change rien, et la demande le dit."""
    moteur = simulateur.scenario_actuel
    carriere = _venue_du_prive(simulateur, mines=64)
    liste, [demande] = departs.departs_et_demandes(moteur, carriere)
    assert liste == (departs.Depart(carriere.date_liquidation),)
    assert (demande.retenue, demande.motif) == (None, departs.SANS_PENSION)


def test_un_seul_regime_differe_se_liquide_a_la_date_demandee(simulateur):
    """La salariée d'un seul régime qui demande sa pension deux ans après son
    départ la touche à cette date : un seul départ, qui n'est pas le déclaré,
    et un montant du système 1 ramené aux prix de l'année du départ."""
    moteur = simulateur.scenario_actuel
    carriere = _carriere(simulateur, [Metier("salarie_prive_non_cadre", 25.25)],
                         naissance=1960, liquidation=62, sexe="F",
                         demandes_de_pension={"regime_general": 64})
    [depart] = departs.departs(moteur, carriere)
    assert (depart.date, depart.motif) == (carriere.date_de_l_age(64), departs.MOTIF_DEMANDE)
    resultat = moteur.calculer(carriere)
    assert [d.motif for d in resultat.departs] == [departs.MOTIF_DEMANDE]
    prix = simulateur.macro.coefficient_prix(2024, 2022)
    assert resultat.pension_annuelle == pytest.approx(
        sum(p.montant_a_l_effet for p in resultat.pensions_par_regime) * prix)


@pytest.mark.parametrize("requete, refus", [
    ({"demande_Regime": "2027-06"}, "minuscules"),
    ({"demande_regime_general": "1980-01"}, "début de la carrière"),
    ({"demande_regime_general": f"{1960 + AGE_LIQUIDATION_MAXIMAL + 1}-01"},
     f"au-delà de {AGE_LIQUIDATION_MAXIMAL} ans"),
])
def test_la_saisie_refuse_une_date_de_pension_illisible(requete, refus):
    from retraite_notionnelle.saisie import ErreurSaisie, Saisie
    base = {"naissance": "1960-05-10", "debut": "1985-09", "liquidation": "2022-06"}
    with pytest.raises(ErreurSaisie, match=refus):
        Saisie.depuis_requete({**base, **requete})


def test_la_date_de_chaque_pension_voyage_dans_l_adresse():
    """Un champ par régime, en date comme le départ, relu tel quel ; le
    contexte refuse un régime que le catalogue ne connaît pas."""
    from retraite_notionnelle.contexte import Contexte
    from retraite_notionnelle.saisie import ErreurSaisie, Saisie
    base = {"naissance": "1960-05-10", "debut": "1985-09", "liquidation": "2022-06"}
    saisie = Saisie.depuis_requete({**base, "demande_regime_general": "2027-06",
                                    "demande_arrco": ""})
    assert saisie.demandes_de_pension_declarees() == {"regime_general": 67.0}
    relue = Saisie.depuis_requete(dict(parse_qsl(saisie.requete())))
    assert relue.demandes == saisie.demandes
    with pytest.raises(ErreurSaisie, match="aucun régime « inconnu »"):
        Contexte().simuler(Saisie.depuis_requete({**base, "demande_inconnu": "2027-06"}))


def test_la_page_dit_la_pension_differee_et_la_demande_non_suivie():
    """Un seul départ, décalé : la page dit que la pension ne commence pas au
    départ ; une demande sans pension : la page dit pourquoi elle ne vaut rien."""
    from retraite_notionnelle.web.site import rendre
    base = {"unite_revenu": "moyen", "naissance": "1960-05-10", "debut": "1985-09",
            "liquidation": "2022-06"}
    page = rendre("/simuler", {**base, "demande_regime_general": "2024-06"})[1]
    assert "Votre pension ne commence pas à votre départ." in page
    assert "à la date où vous la demandez" in page
    page = rendre("/simuler", {**base, "demande_mines": "2025-01"})[1]
    assert "La date que vous demandez n'est pas retenue." in page
    assert "votre carrière n'y ouvre pas de droit" in page
