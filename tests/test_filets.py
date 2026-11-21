"""Les deux filets de la carte de justesse (action 194, étape B).

Ils ne prouvent rien : ils disent où regarder d'abord.

- Le BALAYAGE DE COHÉRENCE : cotiser plus ne baisse jamais la pension — plus
  de salaire une année (a), une année d'activité de plus (b), un trimestre de
  départ plus tard (c) —, sauf baisse qu'une liste rattache à un texte cité ;
  et aucun saut du taux de remplacement entre deux générations voisines hors
  d'une borne qu'une table ou une version du paquet pose.
- La NEUTRALISATION : chaque partie de la carte mutée — ses paramètres, ou la
  source que sa fiche nomme, ou ses interrupteurs coupés —, les témoins
  rejoués ; une partie dont aucun témoin ne bouge n'est pas gardée.

Ce fichier dit ces règles sur des cas fabriqués, puis tient le cliquet : le
nombre d'anomalies « à expliquer » du dernier rapport ne peut que baisser, et
l'échantillon fixe du rapport, rejoué sur le moteur du jour, n'en montre pas
plus que le rapport n'en a compté.
"""

from __future__ import annotations

import copy

import pytest
import yaml

from retraite_notionnelle.noyau import filets

RAPPORT = filets.RAPPORT
CLIQUET = filets.CLIQUET


def rang(annee: int, mois: int = 1) -> int:
    return annee * 12 + mois - 1


# --- Les bornes que le paquet pose ------------------------------------------

def test_les_bornes_se_lisent_aux_tables_et_aux_versions_du_paquet():
    """Une table par génération (clés numériques, 1951.5 pour juillet 1951),
    une ligne de table de version ([début, fin, …]) et une borne de version
    (une date d'effet : le premier départ qu'elle régit est le premier jour
    du mois qui la suit, ou ce jour s'il est le premier) posent chacune une
    borne, au mois."""
    paquet = {
        "durees_requises": {"1900": [150.0, 2], "1951.5": [163.0, 2]},
        "fiches_datees": {"age_legal": {"id": "age_legal", "versions": [
            {"id": "v1", "bornes": {"liquidation.date_effet": [None, "1985-12-21"]},
             "parametres": {"age": 60}},
            {"id": "v2", "bornes": {"liquidation.date_effet": ["1985-12-21", "2011-07-01"]},
             "table": [[1900.0, 1955.25, 60.0, 3], [1955.25, None, 62.0, 3]]}]}},
        "versions_des_fiches": {},
    }
    bornes = filets.bornes_du_paquet(paquet)
    assert "durees_requises" in bornes[rang(1951, 7)]
    assert rang(1951, 1) not in bornes or "durees_requises" not in bornes[rang(1951, 1)]
    assert "age_legal / v2" in bornes[rang(1955, 4)]
    versions = filets.bornes_de_version(paquet)
    assert "age_legal / v2" in versions[rang(1986, 1)]
    assert "age_legal / v2" in versions[rang(2011, 7)] or "age_legal / v1" in versions[rang(2011, 7)]


def test_les_bornes_se_lisent_aussi_aux_lignes_datees():
    """Une revalorisation (« AAAA-MM-JJ » en tête de ligne) et une valeur de
    service datée ([année, mois, valeur]) posent une borne au mois de leur
    effet."""
    paquet = {"revalorisation_pensions": {"generales": [["1949-04-01", 1.15, None]]},
              "valeurs_service_datees": {"agirc_arrco": [[2022, 11, 1.3498, 3]]}}
    bornes = filets.bornes_du_paquet(paquet)
    assert "revalorisation_pensions.generales" in bornes[rang(1949, 4)]
    assert "valeurs_service_datees.agirc_arrco" in bornes[rang(2022, 11)]


# --- Les sauts entre générations voisines ----------------------------------

def _point(generation, depart, taux):
    return {"generation": generation, "depart": depart, "taux": taux}


def test_un_saut_a_une_generation_ou_une_table_commence_est_admis_ailleurs_signale():
    bornes = {rang(1951, 7): ["durees_requises"]}
    avant = _point(rang(1951, 6), rang(2011, 6), 0.50)
    apres = _point(rang(1951, 7), rang(2011, 7), 0.45)
    saut = filets.classer_saut(avant, apres, bornes)
    assert saut["statut"] == "admis" and saut["bornes"] == ["durees_requises"]
    ailleurs = filets.classer_saut(_point(rang(1953, 2), rang(2013, 2), 0.50),
                                   _point(rang(1953, 3), rang(2013, 3), 0.45), bornes)
    assert ailleurs["statut"] == "a_expliquer" and ailleurs["bornes"] == []


def test_un_saut_sous_le_seuil_n_est_pas_un_saut():
    """Le seuil est relatif : 1 % du taux de remplacement."""
    assert filets.SEUIL_DE_SAUT == 0.01
    assert filets.classer_saut(_point(0, 0, 0.500), _point(1, 1, 0.504), {}) is None
    assert filets.classer_saut(_point(0, 0, 0.500), _point(1, 1, 0.494), {}) is not None


def test_un_saut_qui_suit_un_trimestre_valide_de_plus_dans_son_sens_est_admis():
    """La durée se compte au trimestre, validé au salaire de l'année civile
    (L. 351-2) : décaler d'un mois la naissance, et le départ avec elle, peut
    valider un trimestre de plus ou de moins. Le saut qui va dans le sens de la
    durée est admis ; celui qui va contre elle reste à expliquer."""
    avant = {**_point(rang(1943, 2), rang(2003, 3), 0.5445), "trimestres": 155}
    apres = {**_point(rang(1943, 3), rang(2003, 4), 0.5600), "trimestres": 156}
    saut = filets.classer_saut(avant, apres, {})
    assert saut["statut"] == "admis" and saut["bornes"] == [filets.TRIMESTRE_VALIDE]
    contre = {**apres, "taux": 0.53}
    assert filets.classer_saut(avant, contre, {})["statut"] == "a_expliquer"


def test_un_saut_du_seul_revenu_de_reference_n_est_pas_un_saut_de_la_pension():
    """Le taux de remplacement rapporte la pension au dernier revenu de
    l'année civile : un départ qui passe au 1er janvier change de
    dénominateur, pas de pension. Le saut se compte quand la pension aussi
    bouge au-delà du seuil."""
    avant = {**_point(rang(1969, 11), rang(2029, 12), 0.4708), "pension": 19426.5}
    apres = {**_point(rang(1969, 12), rang(2030, 1), 0.4595), "pension": 19426.5}
    assert filets.classer_saut(avant, apres, {}) is None
    apres["pension"] = 18900.0
    assert filets.classer_saut(avant, apres, {})["statut"] == "a_expliquer"


def test_la_date_ou_la_pension_est_servie_franchit_aussi_une_borne():
    """Un fonctionnaire gardé au-delà de sa limite d'âge a une pension servie
    depuis celle-ci : décaler la naissance d'un mois décale ce jour, qui peut
    franchir une revalorisation. La date réelle d'effet, que le résultat dit
    régime par régime, compte comme le départ."""
    bornes = {rang(2011, 4): ["revalorisation_pensions.generales"]}
    avant = {**_point(rang(1946, 3), rang(2016, 1), 0.7091), "pension": 28529.78,
             "effets": {"fonction_publique_etat": rang(2011, 4)}}
    apres = {**_point(rang(1946, 4), rang(2016, 2), 0.6945), "pension": 27942.98,
             "effets": {"fonction_publique_etat": rang(2011, 5)}}
    saut = filets.classer_saut(avant, apres, bornes)
    assert saut["statut"] == "admis"
    assert saut["bornes"] == ["revalorisation_pensions.generales"]


def test_le_resultat_du_pont_dit_la_date_ou_chaque_pension_est_servie():
    resultat = {"assure": {"annee_liquidation": 2016, "mois_liquidation": 1,
                           "trimestres_actuels": 191},
                "scenarios": {"actuel": {
                    "pension_annuelle": 1.0, "taux_remplacement": 0.5,
                    "par_regime": [
                        {"regime": "fonction_publique_etat",
                         "detail": "SR 30,889.88 € × taux 87.375% ; servie depuis le 1er "
                                   "avril 2011, 26,990.03 € à cette date"},
                        {"regime": "rafp", "detail": "points", "date_effet": "2015-12-01"},
                        {"regime": "ircantec", "detail": "servie à partir du 1er décembre 2018"},
                    ]}}}
    effets = filets.rendu_du_pont(resultat)["effets"]
    assert effets == {"fonction_publique_etat": rang(2011, 4), "rafp": rang(2015, 12),
                      "ircantec": rang(2018, 12)}


def test_une_borne_de_date_d_effet_admet_le_saut_du_depart_qui_la_franchit():
    bornes = {rang(2023, 9): ["age_legal / loi_de_2023"]}
    saut = filets.classer_saut(_point(rang(1961, 7), rang(2023, 8), 0.5),
                               _point(rang(1961, 8), rang(2023, 9), 0.4), bornes)
    assert saut["statut"] == "admis"


# --- Les baisses ------------------------------------------------------------

def _pension(montant, depart=rang(2024, 6), debut=1981, regimes=("regime_general",)):
    return {"pension": montant, "depart": depart, "debut": debut, "regimes": list(regimes)}


def test_une_hausse_ou_une_egalite_n_est_pas_une_baisse():
    assert filets.classer_baisse("a", _pension(100.0), _pension(100.0), {}, []) is None
    assert filets.classer_baisse("a", _pension(100.0), _pension(101.0), {}, []) is None


def test_une_baisse_sans_texte_est_a_expliquer_et_une_liste_qui_cite_un_texte_l_admet():
    base, perturbe = _pension(100.0, debut=1950), _pension(99.0, debut=1947)
    baisse = filets.classer_baisse("b", base, perturbe, {}, [])
    assert baisse["statut"] == "a_expliquer"
    liste = [{"id": "annees_d_avant_1948", "perturbation": "b",
              "texte": {"id": "LEGIARTI000000000001", "article": "R. 351-29"},
              "si": {"debut_avant": 1948}}]
    admise = filets.classer_baisse("b", base, perturbe, {}, liste)
    assert admise["statut"] == "admis" and admise["regle"] == "annees_d_avant_1948"
    # La ligne ne vaut que pour sa perturbation, et sous sa condition.
    assert filets.classer_baisse("a", base, perturbe, {}, liste)["statut"] == "a_expliquer"
    tard = _pension(99.0, debut=1960)
    assert filets.classer_baisse("b", base, tard, {}, liste)["statut"] == "a_expliquer"


def test_une_ligne_de_la_liste_sans_texte_cite_est_refusee():
    with pytest.raises(ValueError, match="texte"):
        filets.controler_liste([{"id": "sans_texte", "perturbation": "b", "si": {}}])
    with pytest.raises(ValueError, match="condition"):
        filets.controler_liste([{"id": "x", "perturbation": "b", "texte": {"id": "L"},
                                 "si": {"inconnue": 1}}])


def test_un_depart_plus_tard_qui_baisse_n_est_admis_que_si_une_borne_de_version_tombe_entre():
    base = _pension(100.0, depart=rang(2023, 8))
    perturbe = _pension(98.0, depart=rang(2023, 11))
    versions = {rang(2023, 9): ["age_legal / loi_de_2023"]}
    assert filets.classer_baisse("c", base, perturbe, versions, [])["statut"] == "admis"
    assert filets.classer_baisse("c", base, perturbe, {rang(2024, 1): ["x"]}, [])[
        "statut"] == "a_expliquer"


def test_un_changement_de_regime_n_admet_la_baisse_que_si_la_liste_le_dit():
    base = _pension(100.0, regimes=("regime_general",))
    perturbe = _pension(90.0, regimes=("fonction_publique_etat",))
    liste = [{"id": "seuil_de_la_fonction_publique", "perturbation": "b",
              "texte": {"id": "LEGIARTI000000000002"}, "si": {"regimes_changent": True}}]
    assert filets.classer_baisse("b", base, perturbe, {}, liste)["statut"] == "admis"
    assert filets.classer_baisse("b", base, _pension(90.0), {}, liste)["statut"] == "a_expliquer"


# --- Le balayage, sur un moteur fabriqué ------------------------------------

CAS = [{"code": "salarie", "statut": "salarie_prive_non_cadre", "debut": 21, "salaire": 1.0}]


def _moteur(salaire_qui_baisse=False, saut_en=None):
    """Un moteur fabriqué : la pension croît avec les années et le salaire, sauf
    quand la règle fabriquée la fait baisser avec le salaire."""
    def simuler(requetes):
        rendus = []
        for q in requetes:
            naissance = int(q["naissance"]) * 12 + int(q["naissance_mois"]) - 1
            age = int(q["liquidation"]) * 12 + int(q.get("liquidation_mois", 0))
            annees = (age // 12) - int(q["debut"])
            hausse = 1.0 if "metier2_salaire" in q else 0.0
            pension = 1000.0 + 10.0 * annees + (-5.0 if salaire_qui_baisse else 5.0) * hausse
            pension += age * 0.01
            if saut_en is not None and naissance >= saut_en:
                pension *= 0.9
            rendus.append({"pension": pension, "taux": pension / 2000.0, "ouverte": True,
                           "regimes": ["regime_general"], "depart": naissance + age})
        return rendus
    return simuler


def test_le_balayage_signale_une_regle_qui_baisse_la_pension_quand_le_salaire_monte():
    rapport = filets.balayer(CAS, generations_annees=[1960], generations_mois=[],
                             ages_mois=[64 * 12], simuler=_moteur(salaire_qui_baisse=True),
                             bornes={}, versions={}, liste=[])
    assert rapport["comptes"]["baisses"]["a"]["a_expliquer"] > 0
    assert rapport["comptes"]["baisses"]["b"]["a_expliquer"] == 0
    assert any(a["sorte"] == "baisse_a" for a in rapport["a_expliquer"])
    sain = filets.balayer(CAS, generations_annees=[1960], generations_mois=[],
                          ages_mois=[64 * 12], simuler=_moteur(), bornes={}, versions={},
                          liste=[])
    assert sain["comptes"]["a_expliquer"] == 0


def test_le_balayage_admet_un_saut_a_une_borne_et_signale_l_autre():
    generations = [rang(1960, m) for m in range(1, 13)]
    signale = filets.balayer(CAS, generations_annees=[], generations_mois=generations,
                             ages_mois=[64 * 12], simuler=_moteur(saut_en=rang(1960, 7)),
                             bornes={}, versions={}, liste=[])
    assert signale["comptes"]["sauts"]["a_expliquer"] == 1
    groupe = signale["a_expliquer"][0]
    assert groupe["sorte"] == "saut" and groupe["point"] == "1960-07" and groupe["pensions"] == 1
    admis = filets.balayer(CAS, generations_annees=[], generations_mois=generations,
                           ages_mois=[64 * 12], simuler=_moteur(saut_en=rang(1960, 7)),
                           bornes={rang(1960, 7): ["une_table"]}, versions={}, liste=[])
    assert admis["comptes"]["sauts"] == {"admis": 1, "a_expliquer": 0}


# --- La neutralisation ------------------------------------------------------

def test_une_mutation_ajoute_un_aux_entiers_et_un_pour_cent_aux_taux():
    contenu = {"parametres": {"trimestres": 160, "taux": 0.5, "existe": True, "nom": "x",
                              "lignes": [{"age": 62}]}}
    mute = filets.muter_valeurs(copy.deepcopy(contenu["parametres"]))
    assert mute == {"trimestres": 161, "taux": pytest.approx(0.505), "existe": True,
                    "nom": "x", "lignes": [{"age": 63}]}


def _fiche(valeur, interrupteur=None):
    fiche = {"id": "regle", "versions": [
        {"id": "v1", "contenu": {"droit": "…", "parametres": {"trimestres": valeur}}}]}
    if interrupteur is not None:
        fiche["code"] = {"interrupteurs": {interrupteur: True}}
    return fiche


def _rejouer_qui_lit(lue: bool):
    """Un rejeu fabriqué : le paquet porte la valeur de la fiche si elle est
    lue ; le témoin en dépend si elle l'est."""
    def rejouer(fiches):
        valeur = fiches["regle"]["versions"][0]["contenu"]["parametres"]["trimestres"]
        coupee = not ((fiches["regle"].get("code") or {}).get("interrupteurs") or {}).get(
            "coupe", True)
        paquet = f"{valeur}|{coupee}" if lue else "fixe"
        return paquet, {"temoin_1": {"pension": valeur if lue else 1}}
    return rejouer


def test_une_partie_dont_un_temoin_depend_est_gardee():
    parties = filets.neutraliser({"regle": _fiche(160)}, _rejouer_qui_lit(True))
    assert parties[("regle", "v1")]["etat"] == "gardee"
    assert parties[("regle", "v1")]["temoins"] == ["temoin_1"]


def test_une_partie_que_le_paquet_lit_sans_qu_aucun_temoin_en_depende_n_est_pas_gardee():
    def rejouer(fiches):
        valeur = fiches["regle"]["versions"][0]["contenu"]["parametres"]["trimestres"]
        return str(valeur), {"temoin_1": {"pension": 1}}
    parties = filets.neutraliser({"regle": _fiche(160)}, rejouer)
    assert parties[("regle", "v1")]["etat"] == "non_gardee"


def test_une_mutation_qui_n_atteint_pas_le_paquet_laisse_la_partie_hors_d_atteinte():
    parties = filets.neutraliser({"regle": _fiche(160)}, _rejouer_qui_lit(False))
    assert parties[("regle", "v1")]["etat"] == "hors_d_atteinte"


def test_sans_parametre_l_interrupteur_coupe_neutralise_la_regle():
    fiche = {"id": "regle", "code": {"interrupteurs": {"coupe": True}}}

    def rejouer(fiches):
        coupe = fiches["regle"]["code"]["interrupteurs"]["coupe"]
        return str(coupe), {"temoin_1": {"pension": 1 if coupe else 2}}
    parties = filets.neutraliser({"regle": fiche}, rejouer)
    assert parties[("regle", None)]["etat"] == "gardee"
    assert parties[("regle", None)]["mutation"] == "interrupteur"


# --- Le cliquet --------------------------------------------------------------

def test_le_rapport_et_le_cliquet_se_tiennent():
    """Le nombre d'anomalies « à expliquer » du dernier rapport ne dépasse pas
    celui que le cliquet tient : il ne peut que baisser. Une baisse se reporte
    au cliquet, avec le jour."""
    rapport = yaml.safe_load(RAPPORT.read_text(encoding="utf-8"))
    cliquet = yaml.safe_load(CLIQUET.read_text(encoding="utf-8"))
    assert rapport["balayage"]["comptes"]["a_expliquer"] <= cliquet["balayage"]["a_expliquer"]
    assert rapport["neutralisation"]["comptes"]["non_gardee"] <= cliquet["neutralisation"][
        "non_gardee"]


def test_l_echantillon_fixe_du_rapport_n_a_pas_plus_d_anomalies_que_le_rapport_n_en_compte():
    """Le balayage entier dure trop pour la suite : son échantillon fixe — un
    exemple de chaque anomalie, et des paires saines prises aux bornes — se
    rejoue sur le moteur du jour."""
    rapport = yaml.safe_load(RAPPORT.read_text(encoding="utf-8"))
    echantillon = rapport["balayage"]["echantillon"]
    rejoue = filets.rejouer_echantillon(echantillon)
    assert rejoue["a_expliquer"] <= echantillon["a_expliquer"], rejoue["nouvelles"]


# --- Le tableau de bord ----------------------------------------------------

def test_le_tableau_de_bord_ecrit_les_filets_a_part_de_la_carte():
    """Une section à part de la carte : elle ne change l'état d'aucune partie.
    Elle dit le seuil de saut, le compte des anomalies à expliquer par
    perturbation, les plus nombreuses, et les parties non gardées par
    famille."""
    import sys

    sys.path.insert(0, str(filets.RACINE / "scripts"))
    import tableau_de_bord

    rapport = {
        "balayage": {"le": "2026-11-21", "seuil_de_saut": 0.01, "comptes": {
            "calculs": 100, "fermees": 5, "sauts": {"admis": 3, "a_expliquer": 2},
            "baisses": {"a": {"admis": 0, "a_expliquer": 1}, "b": {"admis": 1, "a_expliquer": 0},
                        "c": {"admis": 0, "a_expliquer": 0}}, "a_expliquer": 3},
            "a_expliquer": [{"sorte": "saut", "cas": "agent_ieg", "point": "1954-04",
                             "pensions": 2, "ages": [61.0, 62.0], "ecart_max": -0.0119}]},
        "neutralisation": {"le": "2026-11-21", "temoins": 937, "comptes": {
            "parties": 3, "gardee": 1, "non_gardee": 1, "hors_d_atteinte": 1},
            "par_famille": {"base_prive": {"gardee": 1, "non_gardee": 1, "hors_d_atteinte": 1}},
            "parties": [{"fiche": "regle", "version": "v1", "famille": "base_prive",
                         "etat": "non_gardee", "mutation": "parametres", "changes": 0}]},
    }
    texte = "\n".join(tableau_de_bord.filets_de_la_carte(rapport))
    assert "**3 anomalies à expliquer**" in texte and "1 %" in texte
    assert "| saut | agent_ieg | 1954-04 | 2 |" in texte
    assert "`regle / v1`" in texte
    assert "ne change l'état d'aucune partie" in texte


def test_une_mutation_que_la_fabrique_refuse_ne_decide_rien_et_se_dit():
    """La fabrique refuse parfois une donnée mutée (un contrôle de cohérence) :
    la mutation n'atteint pas le moteur, et la partie le dit."""
    def executer(taches):
        yield "base", {"temoin_1": 1}
        for _ in taches[1:]:
            yield "refus: contrôle", None
    parties = filets.neutraliser({"regle": _fiche(160)}, executer=executer)
    assert parties[("regle", "v1")]["etat"] == "hors_d_atteinte"
    assert parties[("regle", "v1")]["refusee"] is True
