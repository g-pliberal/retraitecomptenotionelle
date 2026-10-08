"""Le décompte des services du code des pensions au jour, et la référence du
minimum garanti.

Action 138, étape 17 : les deux écarts que la confrontation à TRAJECTOiRE
laissait ouverts (``tests/test_trajectoire.py``, ``ARRONDI_SERVICES`` et
``MINIMUM_GARANTI``), tranchés au texte. Fiche
``decompte_des_services_fonction_publique``.

* **Le décompte final.** « Dans le décompte final des trimestres liquidables,
  la fraction de trimestre égale ou supérieure à quarante-cinq jours est
  comptée pour un trimestre » (R. 26 ; décret n° 2003-1306, article 16) ; « il
  n'y a donc pas lieu de procéder à des arrondis intermédiaires » (CNRACL). Le
  modèle arrondissait les services année par année.
* **La durée de la décote** ne s'arrondit pas, ses trimestres manquants
  s'arrondissent à l'entier supérieur (L. 14, I), et la pension que l'arrondi
  porte au pourcentage maximum ne subit pas de décote (Conseil d'État,
  2 février 2010, n° 311495).
* **La référence du minimum garanti** est la valeur de l'indice majoré 227 au
  1er janvier 2004 « revalorisé dans les conditions prévues à l'article L. 16 »
  (L. 17) : la chaîne des revalorisations des pensions civiles, qui redonne au
  centime chaque montant publié depuis 2021 ; le modèle portait pour 2020 un
  montant revalorisé de 0,3 % au lieu de 1 %, et projetait les autres années
  sur les prix.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.droit.compter import arrondir_les_services
from retraite_notionnelle.saisie import ErreurSaisie, Saisie

RACINE = Path(__file__).resolve().parents[1]
FICHE = RACINE / "data" / "reference" / "regles" / "decompte_des_services_fonction_publique.yaml"

#: Les deux unités du décompte final : le trimestre depuis 2004, le semestre de
#: 1964 à 2003.
TRIMESTRE = {"unite_jours": 90, "seuil_jours": 45}
SEMESTRE = {"unite_jours": 180, "seuil_jours": 90}


@pytest.mark.parametrize(("jours", "trimestres"), [
    # CNRACL, « Trimestres liquidables » : 20 ans 6 mois et 13 jours de
    # services, 1 an 1 mois et 2 jours de bonifications, « soit 86 trimestres
    # et 45 jours donc 87 trimestres ».
    (20 * 360 + 6 * 30 + 13 + 360 + 30 + 2, 87),
    # Conseil d'État, 2 février 2010, n° 311495 : « 155 trimestres, deux mois
    # et vingt-deux jours », comptés pour 156.
    (155 * 90 + 2 * 30 + 22, 156),
    # Service des retraites de l'État, « La formule de calcul » : vingt-neuf ans
    # à temps plein et dix à 80 % font 148 trimestres.
    (29 * 360 + 10 * 360 * 0.8, 148),
    (30, 0), (44, 0), (45, 1), (60, 1), (90 + 44, 1), (90 + 45, 2),
])
def test_le_decompte_final_compte_la_fraction_de_quarante_cinq_jours(jours, trimestres):
    assert arrondir_les_services(jours, TRIMESTRE) == trimestres


@pytest.mark.parametrize(("jours", "trimestres"), [
    # R. 26 de 1964 : « la fraction de semestre égale ou supérieure à trois mois
    # est comptée pour six mois ».
    (89, 0), (90, 2), (180 + 89, 2), (180 + 90, 4), (37 * 360 + 3 * 30, 150),
])
def test_avant_2004_le_decompte_final_compte_au_semestre(jours, trimestres):
    assert arrondir_les_services(jours, SEMESTRE) == trimestres


def _releve(entree: str, depart: str, annees: range, traitement: float = 20000.0,
            statut: str = "fonctionnaire_etat") -> str:
    """Un relevé de fonctionnaire : l'année d'entrée et celle du départ avec
    leurs trimestres, fractions comprises, et des années pleines entre elles."""
    lignes = [f"{annees.start - 1}:{statut}:{traitement / 3:.0f}:{entree}"]
    lignes += [f"{annee}:{statut}:{traitement:.0f}:4" for annee in annees]
    lignes.append(f"{annees.stop}:{statut}:{traitement / 2:.0f}:{depart}")
    return ",".join(lignes)


#: Le cas du Conseil d'État, au mois : né en août 1946, parti le 1er août 2006
#: à soixante ans, entré en septembre 1967 — quatre mois en 1967, sept en 2006,
#: 155 trimestres et deux mois, quand 156 ouvrent en 2006 le pourcentage
#: maximum. Le relevé année par année en trimestres entiers (1 et 2) en
#: comptait 155, et une décote.
CONSEIL_D_ETAT = {"naissance": "1946-08-01", "sexe": "H", "liquidation": "2006-08",
                  "releve": _releve("1.33", "2.33", range(1968, 2006))}


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


def _fonction_publique(contexte: Contexte, requete: dict):
    actuel = contexte.simuler(Saisie.depuis_requete(requete)).actuel
    pension = next(p for p in actuel.pensions_par_regime
                   if p.regime == "fonction_publique_etat")
    return actuel, pension


def test_l_arrondi_porte_au_pourcentage_maximum_et_efface_la_decote(contexte):
    actuel, pension = _fonction_publique(contexte, CONSEIL_D_ETAT)
    assert actuel.trimestres_requis == 156
    assert "× 156/156" in pension.detail, pension.detail
    assert actuel.taux_liquidation == pytest.approx(0.75)


def test_en_trimestres_entiers_annee_par_annee_le_modele_en_perdait_un(contexte):
    entiers = {**CONSEIL_D_ETAT, "releve": _releve("1", "2", range(1968, 2006))}
    actuel, pension = _fonction_publique(contexte, entiers)
    assert "× 155/156" in pension.detail, pension.detail
    assert actuel.taux_liquidation < 0.75


def test_un_mois_de_trop_peu_fait_une_decote(contexte):
    """Trois mois en 1967 et sept en 2006 : 155 trimestres et un mois, que le
    décompte final néglige ; la durée d'assurance, au jour, manque d'un
    deux-tiers de trimestre, que L. 14 arrondit à l'entier supérieur."""
    court = {**CONSEIL_D_ETAT, "releve": _releve("1", "2.33", range(1968, 2006))}
    actuel, pension = _fonction_publique(contexte, court)
    assert "× 155/156" in pension.detail, pension.detail
    assert actuel.taux_liquidation < 0.75


def test_les_services_d_avant_1948_entrent_au_decompte_de_l_etat():
    """Trente-quatre ans de services de 1946 à 1979, dont deux aux pensions
    civiles d'avant 1948, que le régime de l'État liquide avec les siens : 136
    trimestres. Le décompte au jour ne les comptait d'abord que dans les trois
    régimes de la fiche, et en perdait huit."""
    from retraite_notionnelle.carriere import Carriere, Metier
    from retraite_notionnelle.droit import liquidation
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur()
    carriere = Carriere.depuis_parcours(
        annee_naissance=1925, sexe="H", metiers=[Metier("fonctionnaire_etat", 21.0, 1.0)],
        age_liquidation=55.0, macro=simulateur.macro, mois_naissance=1)
    liquidee = liquidation.liquider(
        liquidation.demande_de_depart(carriere), liquidation.Etat(carriere),
        liquidation.Contexte(simulateur.scenario_actuel, frozenset()))
    pension = next(p for p in liquidee.complements.regimes
                   if p.regime == "fonction_publique_etat")
    assert "× 136/150" in pension.detail and "pensions_civiles_1853" in pension.detail, \
        pension.detail


def test_une_fraction_ne_se_declare_que_des_services_de_la_fonction_publique(contexte):
    prive = {**CONSEIL_D_ETAT,
             "releve": _releve("1.33", "2.33", range(1968, 2006), statut="salarie_prive_non_cadre")}
    with pytest.raises(ErreurSaisie, match="une fraction de trimestre ne se déclare que"):
        contexte.simuler(Saisie.depuis_requete(prive))


def test_le_relevé_refuse_plus_de_quatre_trimestres():
    with pytest.raises(ErreurSaisie, match="trimestres attendus entre 0 et 4"):
        Saisie.depuis_requete({**CONSEIL_D_ETAT,
                               "releve": "2005:fonctionnaire_etat:20000:4.5"}).releve_analyse()


@pytest.mark.parametrize(("annee", "mois", "mensuel"), [
    # Les montants publiés : par le service des retraites de l'État au 1er
    # janvier de 2023 à 2026 (16 396,19 € par an), et 1 248,33 € en juillet
    # 2022, que des pages de 2023 recopiaient ; la chaîne les redonne au
    # centime. En 2020, 1 182,53 €, et non 1 174,33 €.
    (2020, 1, 1182.53), (2021, 1, 1187.26), (2022, 1, 1200.32), (2022, 7, 1248.33),
    (2023, 10, 1258.32), (2024, 1, 1325.01), (2025, 10, 1354.16), (2026, 1, 1366.35),
    # Février 2015 : la revalorisation d'avril 2013, aucune depuis.
    (2015, 2, 1156.90),
])
def test_la_reference_du_minimum_garanti_suit_les_revalorisations(contexte, annee, mois,
                                                                   mensuel):
    simulateur = contexte.simulateur(Saisie.depuis_requete(CONSEIL_D_ETAT).parametres(
        contexte.base))
    reference, _ = simulateur.scenario_actuel.minimum_garanti.reference(annee, mois)
    assert reference / 12 == pytest.approx(mensuel, abs=0.005)


#: Le cas type 10 du COR de 1960, tel que le témoin de TRAJECTOiRE le décrit : le
#: minimum garanti de janvier 2020, quatre-vingt-dix pour cent de 1 182,53 €.
def _cas_type_10_de_1960() -> dict:
    temoin = json.loads((RACINE / "tests" / "temoins" / "trajectoire.json")
                        .read_text(encoding="utf-8"))
    return temoin["cas"]["cor_10_1960"]["requete"]


def test_le_minimum_garanti_de_2020_est_celui_de_la_chaine(contexte):
    actuel = contexte.simuler(Saisie.depuis_requete(_cas_type_10_de_1960())).actuel
    pension = next(p for p in actuel.pensions_par_regime if p.regime == "cnracl")
    assert "porté au minimum garanti" in pension.detail, pension.detail
    assert pension.montant == pytest.approx(0.90 * 1182.53 * 12, abs=0.2)


def test_les_deux_moteurs_comptent_au_jour_a_l_identique():
    """Les mêmes liquidations en JavaScript : le relevé au jour, en trimestres
    entiers, celui que le contexte refuse, une carrière reconstituée entrée en
    novembre, et le minimum garanti du cas type 10."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _ecarts, _python

    requetes = [
        CONSEIL_D_ETAT,
        {**CONSEIL_D_ETAT, "releve": _releve("1", "2", range(1968, 2006))},
        {**CONSEIL_D_ETAT, "releve": _releve("1.33", "2.33", range(1968, 2006),
                                             statut="salarie_prive_non_cadre")},
        {"naissance": "1966-03-01", "sexe": "F", "liquidation": "2033-08",
         "statut": "fonctionnaire_territorial_hospitalier", "debut": "1988-11"},
        _cas_type_10_de_1960(),
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    assert "erreur" in attendus[2] and "fraction de trimestre" in attendus[2]["erreur"]
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])


def test_la_fiche_dit_le_semestre_puis_le_trimestre(contexte):
    simulateur = contexte.simulateur(Saisie.depuis_requete(CONSEIL_D_ETAT).parametres(
        contexte.base))
    fiches = simulateur.scenario_actuel.fiches_datees
    assert fiches.regle("decompte_des_services_fonction_publique", "1960-01-01")["existe"] is False
    ancien = fiches.regle("decompte_des_services_fonction_publique", "1990-06-01")
    assert (ancien["unite_jours"], ancien["seuil_jours"], ancien["duree_au_jour"]) == (180, 90, False)
    nouveau = fiches.regle("decompte_des_services_fonction_publique", "2026-10-01")
    assert (nouveau["unite_jours"], nouveau["seuil_jours"], nouveau["duree_au_jour"]) == (90, 45, True)
    assert FICHE.exists()
