"""Deux activités à la fois : ce que le modèle en fait, et ce qu'il refuse.

Une activité cumulée ne se devine pas : elle se déclare, par ``Metier.cumul``.
Le droit la traite régime par régime — chacun encaisse sur son revenu et sert
ses droits —, mais il borne tout ce qui se compte TOUS RÉGIMES : quatre
trimestres au plus par année civile (R. 351-5, et le 2° de R. 173-4-4-1 pour
la réunion des régimes alignés), et, dans la liquidation unique, un revenu
annuel formé de la somme des deux activités, écrêté une seule fois au plafond.
"""

from __future__ import annotations

import json
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle.carriere import Metier
from retraite_notionnelle.web.site import ErreurSite, disponible, rendre

from facade import Carriere, Simulateur

from outils_pont import Saisies, refus_de_la_saisie, saisie_du_portage, servi_et_fige


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, *cumuls: Metier, niveau: float = 1.0,
              naissance: int = 1962, liquidation: float = 67.0) -> Carriere:
    return simulateur.carriere_parcours(
        annee_naissance=naissance,
        sexe="H",
        metiers=[Metier(affiliation="salarie_prive_non_cadre", age_debut=22.0,
                        niveau_salaire=niveau), *cumuls],
        age_liquidation=liquidation,
    )


def test_sans_declaration_rien_n_est_cumule(simulateur):
    """Un métier qui ne se déclare pas cumulé SUCCÈDE au précédent."""
    carriere = simulateur.carriere_parcours(
        annee_naissance=1962, sexe="H",
        metiers=[Metier(affiliation="salarie_prive_non_cadre", age_debut=22.0),
                 Metier(affiliation="artisan", age_debut=40.0)],
        age_liquidation=67.0,
    )
    assert all(len(carriere.lignes_de(annee)) == 1
               for annee in {ligne.annee for ligne in carriere.lignes})


def test_l_activite_cumulee_s_ajoute_sans_rien_deplacer(simulateur):
    seule = _carriere(simulateur)
    cumulee = _carriere(simulateur, Metier(
        affiliation="artisan", age_debut=40.0, niveau_salaire=0.3,
        cumul=True, age_fin=50.0))
    # L'activité principale est intacte, ligne pour ligne, et reste en tête.
    for ligne in seule.lignes:
        assert cumulee.ligne(ligne.annee) == ligne
    ajoutees = [l for l in cumulee.lignes if l.affiliation == "artisan"]
    assert [l.annee for l in ajoutees] == list(range(2002, 2012))
    assert all(l.revenu > 0 for l in ajoutees)
    assert cumulee.date_entree("artisan").annee == 2002


def test_la_duree_tous_regimes_ne_depasse_pas_quatre_trimestres(simulateur):
    """Deux activités pleines la même année : quatre trimestres, pas huit."""
    seule = _carriere(simulateur)
    cumulee = _carriere(simulateur, Metier(
        affiliation="artisan", age_debut=40.0, niveau_salaire=0.5, cumul=True))
    assert cumulee.trimestres_actuels == seule.trimestres_actuels
    resultat = simulateur.scenario_actuel.calculer(cumulee)
    assert resultat.trimestres_valides == (
        simulateur.scenario_actuel.calculer(seule).trimestres_valides)


def test_la_liquidation_unique_somme_puis_ecrete(simulateur):
    """Salarié au-dessus du plafond, plus une activité d'artisan : la retraite
    unique des régimes alignés ne bouge pas. Le revenu de l'année est écrêté
    une fois au plafond, que le salaire atteint déjà seul, et la durée ne
    gagne rien sur des années déjà pleines."""
    scenario = simulateur.scenario_actuel
    seule = _carriere(simulateur, niveau=2.0)
    cumulee = _carriere(simulateur, Metier(
        affiliation="artisan", age_debut=40.0, niveau_salaire=0.5, cumul=True),
        niveau=2.0)

    def base(carriere) -> float:
        return sum(p.montant for p in scenario.calculer(carriere).pensions_par_regime
                   if p.type_calcul == "annuites")

    assert base(cumulee) == pytest.approx(base(seule), rel=1e-9)


def test_un_regime_distinct_sert_sa_propre_pension(simulateur):
    """Salarié qui exerce aussi en libéral : la caisse des libéraux sert ses
    points, en plus de ce que le régime général servait déjà."""
    scenario = simulateur.scenario_actuel
    seule = scenario.calculer(_carriere(simulateur))
    cumulee = scenario.calculer(_carriere(simulateur, Metier(
        affiliation="medecin_liberal", age_debut=35.0, niveau_salaire=0.8,
        cumul=True)))
    regimes_seule = {p.regime for p in seule.pensions_par_regime}
    nouveaux = [p for p in cumulee.pensions_par_regime
                if p.regime not in regimes_seule]
    assert nouveaux and all(p.montant > 0 for p in nouveaux)
    assert cumulee.pension_annuelle > seule.pension_annuelle


def test_le_compte_notionnel_porte_les_deux_cotisations(simulateur):
    seule = simulateur.simuler(_carriere(simulateur))
    cumulee = simulateur.simuler(_carriere(simulateur, Metier(
        affiliation="medecin_liberal", age_debut=35.0, niveau_salaire=0.8,
        cumul=True)))
    assert (cumulee.notionnel_retroactif.pension_annuelle
            > seule.notionnel_retroactif.pension_annuelle)


def _parcours_tires_au_hasard(graine: int, nombre: int) -> list[dict]:
    """Les parcours tirés — graine fixe —, chacun avec une à deux activités
    cumulées, parmi les statuts du paquet que le portage lit."""
    paquet = Path(__file__).resolve().parents[1] / "moteur" / "donnees.json"
    statuts = list(json.loads(paquet.read_text(encoding="utf-8"))["affiliations"])
    alea = random.Random(graine)
    parcours = []
    for _ in range(nombre):
        debut = alea.randint(16 * 12, 28 * 12) / 12
        liquidation = alea.randint(60 * 12, 69 * 12) / 12
        metiers = [{"affiliation": alea.choice(statuts), "age_debut": debut,
                    "niveau_salaire": round(alea.uniform(0.3, 3.0), 3)}]
        changement = alea.randint(int(debut) + 2, int(liquidation) - 2)
        if alea.random() < 0.5:
            metiers.append({"affiliation": alea.choice(statuts),
                            "age_debut": float(changement),
                            "niveau_salaire": round(alea.uniform(0.3, 3.0), 3)})
        for _ in range(alea.randint(1, 2)):
            ouverture = alea.randint(int(debut * 12) + 1, int(liquidation * 12) - 13)
            cumul = {"affiliation": alea.choice(statuts),
                     "age_debut": ouverture / 12,
                     "niveau_salaire": round(alea.uniform(0.1, 1.5), 3),
                     "cumul": True}
            if alea.random() < 0.5:
                cumul["age_fin"] = alea.randint(ouverture + 6,
                                                int(liquidation * 12)) / 12
            metiers.append(cumul)
        parcours.append({
            "annee_naissance": alea.randint(1940, 1995),
            "mois_naissance": alea.randint(1, 12),
            "sexe": alea.choice(["H", "F"]),
            "age_liquidation": liquidation,
            "nombre_enfants": alea.randint(0, 3),
            "metiers": metiers,
        })
    return parcours


def test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard():
    """Les témoins figés n'exercent qu'un statut à la fois : aucun ne cumule.

    On tire donc des parcours au hasard — graine fixe —, chacun avec une à deux
    activités cumulées, et le site les simule. Le moteur Python les simulait
    aussi, et chaque valeur de la comparaison se retrouvait des deux côtés,
    refus compris : ce que le portage rend est figé au témoin des valeurs
    (action 161, étape 8k), et le moteur Python ne refait plus les parcours.
    """
    from outils_valeurs import valeur_figee

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    parcours = _parcours_tires_au_hasard(20260922, 40)
    racine = Path(__file__).resolve().parents[1]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(parcours, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer-cumul.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False,
        )
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr
    obtenus = json.loads(execution.stdout)

    assert len(obtenus) == len(parcours)
    assert sum("resultat" in o for o in obtenus) >= 20, "trop peu de parcours simulés"
    assert valeur_figee("cumuls_tires_au_hasard", obtenus) == obtenus


# -- l'activité accessoire de l'agent d'un régime spécial ----------------------
#
# « Les travailleurs mentionnés à l'article D. 171-2 qui bénéficient pour tout
# ou partie des risques d'un régime spécial de sécurité sociale, sont,
# lorsqu'ils exercent simultanément et à titre accessoire une activité salariée
# ou assimilée, relevant du régime général de sécurité sociale, dispensés au
# titre de cette activité de la cotisation d'assurance vieillesse incombant au
# salarié en vertu de l'article L. 241-3. Ils n'ont droit qu'aux prestations
# prévues par le régime auquel ils sont affiliés au titre de leur activité
# principale » (D. 171-4 CSS, LEGIARTI000006735484, du 21 décembre 1985 au
# 18 juillet 2015). D. 171-2 (LEGIARTI000006735483) vise les travailleurs des
# branches de R. 711-1 — 1° l'État, pour ses fonctionnaires et ses ouvriers ;
# 2° et 3° les collectivités et leurs établissements ; 6° la SNCF ; 8° les IEG…
# La Cnav : « Avant le 19/07/2015, le fonctionnaire qui exerçait, à titre
# accessoire, une activité salariée relevant du régime général, ne cotisait pas
# à l'assurance vieillesse du régime général. Cette activité ne lui ouvre pas
# de droit au régime général » ; depuis, « Cette activité lui donne des droits
# au régime général » (exposé « Taux des cotisations », circulaire Cnav
# 2016/15). Le cas, posé à la main : né le 15 janvier 1960, entré à 22 ans,
# parti à 62, et salarié du privé EN PLUS, à 0,3 fois le salaire moyen, de 40 à
# 45 ans (2000 à 2004) ou de 56 à 61 ans (2016 à 2020).

_ACCESSOIRE = {
    "naissance": "1960-01-15", "sexe": "H", "debut": "22", "liquidation": "62",
    "salaire": "1", "metier2_statut": "salarie_prive_non_cadre",
    "metier2_salaire": "0.3", "metier2_cumul": "oui",
}
_AVANT_2015 = {"metier2_debut": "40", "metier2_fin": "45"}
_APRES_2015 = {"metier2_debut": "56", "metier2_fin": "61"}
#: Les statuts de l'activité principale, et le numéro de R. 711-1 qui les vise.
_ORGANISATIONS_SPECIALES = {
    "fonctionnaire_etat": "1°", "ouvrier_etat": "1°",
    "fonctionnaire_territorial_hospitalier": "2° et 3°", "agent_sncf": "6°",
    "agent_ieg": "8°",
}


@pytest.fixture(scope="module")
def accessoires() -> dict[str, dict]:
    """Le scénario 1 de chaque cas, servi par le portage et confronté au témoin des servis (``servi_et_fige``)."""
    cas = [{"cle": f"{statut}/seul",
            "requete": {**{c: v for c, v in _ACCESSOIRE.items()
                           if not c.startswith("metier2")}, "statut": statut}}
           for statut in [*_ORGANISATIONS_SPECIALES, "militaire", "medecin_liberal"]]
    cas += [{"cle": f"{statut}/{quand}",
             "requete": {**_ACCESSOIRE, **dates, "statut": statut}}
            for statut in [*_ORGANISATIONS_SPECIALES, "militaire", "medecin_liberal"]
            for quand, dates in (("avant", _AVANT_2015), ("apres", _APRES_2015))]
    servis, refus = servi_et_fige(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


def _pensions(actuel: dict) -> dict[str, dict]:
    return {p["regime"]: p for p in actuel["pensions_par_regime"] if p["montant"] > 0}


@pytest.mark.parametrize("statut", _ORGANISATIONS_SPECIALES)
def test_l_activite_accessoire_d_avant_2015_n_ouvre_rien_au_regime_general(
        accessoires, statut):
    """De 2000 à 2004, l'agent dont l'activité principale relève de R. 711-1
    n'a « droit qu'aux prestations » de son régime : le régime général ne sert
    rien, et la durée tous régimes, que ses quatre trimestres par an
    remplissent déjà, ne bouge pas. Le modèle lui servait le régime général
    sur vingt trimestres (553,56 € par an pour le fonctionnaire de l'État)."""
    seul, avant = accessoires[f"{statut}/seul"], accessoires[f"{statut}/avant"]
    assert "regime_general" not in _pensions(avant)
    assert avant["trimestres_valides"] == seul["trimestres_valides"]
    principal = {regime: p["montant"] for regime, p in _pensions(seul).items()}
    assert {regime: _pensions(avant)[regime]["montant"] for regime in principal} == (
        pytest.approx(principal, rel=1e-12))


@pytest.mark.parametrize("statut", _ORGANISATIONS_SPECIALES)
def test_l_activite_accessoire_depuis_2016_ouvre_le_regime_general(accessoires, statut):
    """De 2016 à 2020, ses rémunérations sont « versées à partir du
    19/07/2015 » : le régime général les compte. Chaque année, 0,3 fois le
    salaire moyen dépasse 600 heures de SMIC (quatre fois 150, R. 351-9) :
    vingt trimestres en cinq ans."""
    detail = _pensions(accessoires[f"{statut}/apres"])["regime_general"]["detail"]
    assert "× 20/" in detail


@pytest.mark.parametrize("statut", ["militaire", "medecin_liberal"])
def test_hors_de_r_711_1_l_activite_cumulee_ouvre_le_regime_general(accessoires, statut):
    """Le médecin libéral n'est pas l'agent d'un régime spécial ; R. 711-1, 1°, ne vise
    à l'État que « les fonctionnaires, les magistrats et les ouvriers », et le
    modèle n'y range pas le militaire (lecture déclarée dans la fiche
    `un_statut_par_annee`) : leur activité salariée de 2000 à 2004 garde ses
    vingt trimestres au régime général."""
    detail = _pensions(accessoires[f"{statut}/avant"])["regime_general"]["detail"]
    assert "× 20/" in detail


@pytest.mark.parametrize("metiers, motif", [
    ([Metier(affiliation="artisan", age_debut=22.0, cumul=True)],
     "ne peut pas commencer"),
    ([Metier(affiliation="salarie_prive_non_cadre", age_debut=22.0),
      Metier(affiliation="artisan", age_debut=20.0, cumul=True)],
     "après le début"),
    ([Metier(affiliation="salarie_prive_non_cadre", age_debut=22.0),
      Metier(affiliation="artisan", age_debut=40.0, cumul=True, age_fin=70.0)],
     "au plus tard à la liquidation"),
    ([Metier(affiliation="salarie_prive_non_cadre", age_debut=22.0),
      Metier(affiliation="artisan", age_debut=40.0, cumul=True, age_fin=39.0)],
     "après avoir commencé"),
    ([Metier(affiliation="salarie_prive_non_cadre", age_debut=22.0),
      Metier(affiliation="salarie_prive_non_cadre", age_debut=40.0, cumul=True)],
     "même statut"),
])
def test_ce_que_le_cumul_refuse(simulateur, metiers, motif):
    with pytest.raises(ValueError, match=motif):
        simulateur.carriere_parcours(
            annee_naissance=1962, sexe="H", metiers=metiers, age_liquidation=67.0)


# -- le formulaire ------------------------------------------------------------

_SAISIE = {
    "naissance": "1968", "sexe": "H", "statut": "salarie_prive_non_cadre",
    "debut": "21", "liquidation": "64", "salaire": "1",
}


def test_le_formulaire_ne_cumule_que_ce_qui_est_declare():
    """Sans réponse au menu, la deuxième ligne REMPLACE la première."""
    remplace = saisie_du_portage({
        **_SAISIE, "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "0.5"})
    assert not remplace.metiers[0].cumul
    ajoute = saisie_du_portage({
        **_SAISIE, "metier2_debut": "40", "metier2_statut": "artisan",
        "metier2_salaire": "0.5", "metier2_cumul": "oui", "metier2_fin": "50"})
    metier = ajoute.metiers[0]
    assert metier.cumul and metier.fin == pytest.approx(50.0)


def test_le_formulaire_mene_le_cumul_jusqu_au_modele():
    requete = {**_SAISIE, "metier2_debut": "36", "metier2_statut": "medecin_liberal",
               "metier2_salaire": "0.6", "metier2_cumul": "oui", "metier2_fin": "58"}
    carriere = Saisies().carriere(requete)
    liberal = [l.annee for l in carriere.lignes if l.affiliation == "medecin_liberal"]
    assert liberal == list(range(2004, 2026))
    # L'activité principale n'a pas été interrompue par celle qui s'ajoute.
    assert all(carriere.ligne(annee).affiliation == "salarie_prive_non_cadre"
               for annee in liberal)
    # L'adresse partageable rejoue la même saisie.
    relue = saisie_du_portage(dict(parse_qsl(saisie_du_portage(requete).requete())))
    assert relue.metiers == saisie_du_portage(requete).metiers


@pytest.mark.parametrize("ajout, motif", [
    ({"metier2_fin": "50"}, "date de fin"),
    ({"metier2_cumul": "peut-etre"}, "réponse possible"),
    ({"metier2_cumul": "oui", "metier2_statut": "chomage_indemnise"},
     "sans emploi"),
    ({"metier2_cumul": "oui", "metier2_fin": "70"}, "au plus tard au départ"),
    ({"metier2_cumul": "oui", "saisie_par": "pension", "pension": "1500"},
     "par son revenu"),
])
def test_ce_que_le_formulaire_refuse(ajout, motif):
    requete = {**_SAISIE, "metier2_debut": "40", "metier2_statut": "artisan",
               "metier2_salaire": "0.5", **ajout}
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(motif)):
        saisie_du_portage(requete)


def test_la_page_dit_l_activite_ajoutee():
    if not disponible():
        pytest.skip("node absent : le site ne se lit pas sans lui")
    _, page = rendre("/simuler", {
        **_SAISIE, "metier2_debut": "36", "metier2_statut": "medecin_liberal",
        "metier2_salaire": "0.6", "metier2_cumul": "oui"})
    assert "Deuxième métier, en plus" in page
    assert 'name="metier2_fin"' in page
    assert '<option value="oui" selected' in page
    assert "et en même temps Médecin libéral en secteur 1 de 36 ans" in page
