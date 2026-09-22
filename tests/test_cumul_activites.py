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
import math
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.web.pages import Contexte


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


def _sans_nan(valeur):
    if isinstance(valeur, float) and math.isnan(valeur):
        return None
    if isinstance(valeur, dict):
        return {cle: _sans_nan(v) for cle, v in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [_sans_nan(v) for v in valeur]
    return valeur


def _ecarts(obtenu, attendu, chemin="") -> list[str]:
    if isinstance(attendu, dict):
        if not isinstance(obtenu, dict):
            return [f"{chemin} : {obtenu!r} au lieu d'un objet"]
        ecarts = []
        for cle in attendu.keys() | obtenu.keys():
            ecarts += _ecarts(obtenu.get(cle), attendu.get(cle), f"{chemin}.{cle}")
        return ecarts
    if isinstance(attendu, list):
        if not isinstance(obtenu, list) or len(obtenu) != len(attendu):
            return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
        return [e for i, (o, a) in enumerate(zip(obtenu, attendu))
                for e in _ecarts(o, a, f"{chemin}[{i}]")]
    if (isinstance(attendu, (int, float)) and not isinstance(attendu, bool)
            and isinstance(obtenu, (int, float)) and not isinstance(obtenu, bool)):
        if math.isclose(obtenu, attendu, rel_tol=1e-9, abs_tol=1e-9):
            return []
    elif obtenu == attendu:
        return []
    return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]


def test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard():
    """Les témoins figés n'exercent qu'un statut à la fois : aucun ne cumule.

    On tire donc des parcours au hasard — graine fixe —, chacun avec une à deux
    activités cumulées, on les simule ici et dans le site, et chaque valeur de
    la comparaison doit se retrouver des deux côtés, refus compris.
    """
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")

    contexte = Contexte()
    simulateur = contexte.simulateur()
    alea = random.Random(20260922)
    statuts = list(simulateur.affiliations.codes)
    parcours = []
    for _ in range(40):
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

    attendus = []
    for options in parcours:
        try:
            carriere = simulateur.carriere_parcours(
                **{**options, "metiers": [Metier(**m) for m in options["metiers"]]})
            attendus.append({"resultat": _sans_nan(
                simulateur.simuler(carriere).dictionnaire())})
        except (ValueError, KeyError) as erreur:
            attendus.append({"erreur": str(erreur)})
    assert sum("resultat" in a for a in attendus) >= 20, "trop peu de parcours simulés"

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

    for numero, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        if "erreur" in attendu:
            assert "erreur" in obtenu, f"parcours {numero} : Python refuse, pas le site"
            continue
        assert "resultat" in obtenu, f"parcours {numero} : {obtenu.get('erreur')}"
        ecarts = _ecarts(obtenu["resultat"], attendu["resultat"])
        assert not ecarts, f"parcours {numero} : " + "; ".join(ecarts[:5])


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
