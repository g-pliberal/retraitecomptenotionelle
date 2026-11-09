"""Les deux constats de la page Partager, lus à leur source (action 189, étape 2).

Le 9 novembre 2026, le propriétaire arrête deux cartes de constat, une
information chacune : ce que l'État paie en 2026 pour les retraites de la SNCF
et de la RATP, et l'excédent de la caisse des industries électriques et
gazières que la contribution tarifaire d'acheminement (CTA) remplit, sur toute
facture d'électricité et de gaz. Le premier était déjà une donnée du dépôt, les
crédits du programme 198 au projet de loi de finances pour 2026 ; le second y
entre ici, lu dans la délibération de la Commission de régulation de l'énergie.
Les deux passent au paquet, où la page les lit : aucun montant de ces cartes
ne s'écrit à la main.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml

from retraite_notionnelle.donnees.chargement import charger_table_csv

RACINE = Path(__file__).resolve().parents[1]
REGIMES = RACINE / "data" / "reference" / "regimes"
EXCEDENT_CNIEG = REGIMES / "excedent_cnieg.csv"
PAP = REGIMES / "pap_regimes_subventionnes.csv"

#: La délibération n° 2026-14 de la CRE, du 15 janvier 2026 : son avis sur
#: l'arrêté qui baisse les taux de la CTA au 1er février 2026.
DELIBERATION = ("https://www.cre.fr/fileadmin/Documents/Deliberations/2026/"
                "260115_2026-14_Arrete_CTA.pdf")


def _construction():
    chemin = RACINE / "scripts" / "construire_donnees.py"
    specification = importlib.util.spec_from_file_location("construire_donnees", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_l_excedent_de_la_cnieg_est_celui_que_la_cre_estime():
    """« sans pour autant aboutir à équilibrer ses charges et ses recettes ni à
    résorber l'excédent estimé à fin 2025 de 2,2 Md€. Selon l'estimation de la
    CRE, cet excédent pourrait atteindre 4,4 Md€ en 2030 » : la délibération
    n° 2026-14, § 3.2, page 2, parlant de « l'excédent de trésorerie de la
    CNIEG ». La fin de 2025 est une estimation, 2030 une prévision."""
    table, _ = charger_table_csv(EXCEDENT_CNIEG, ("annee", "poste"), "montant_md")
    assert table == {("2025", "excedent_tresorerie"): 2.2,
                     ("2030", "excedent_tresorerie"): 4.4}
    natures = {ligne.split(",")[0]: ligne.split(",")[3]
               for ligne in EXCEDENT_CNIEG.read_text(encoding="utf-8").splitlines()
               if ligne[:4].isdigit()}
    assert natures == {"2025": "estimation", "2030": "prevision"}


def test_l_excedent_de_la_cnieg_nomme_sa_source_au_manifeste():
    """Le fichier nomme sa source, et le manifeste la porte avec l'adresse de la
    délibération : « d'où vient ce chiffre » a sa réponse dans le dépôt."""
    entete = [l for l in EXCEDENT_CNIEG.read_text(encoding="utf-8").splitlines()
              if l.startswith("#")]
    assert any("source_id: cre_deliberation_2026_14" in l for l in entete)
    manifeste = yaml.safe_load((RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))
    jeux = {jeu["id"]: jeu for institution in manifeste["institutions"].values()
            for jeu in institution.get("jeux") or []}
    jeu = jeux["cre_deliberation_2026_14"]
    assert jeu["url"] == DELIBERATION
    assert jeu["cible"] == "data/reference/regimes/excedent_cnieg.csv"


def test_le_paquet_porte_les_deux_constats_tels_que_les_donnees_les_disent():
    """Le paquet porte, sous ``constats``, les crédits de l'État de 2026 pour la
    SNCF et la RATP (programme 198 : 3 225,8 et 885,6 M€) et l'excédent de la
    CNIEG estimé à la fin de 2025 (2,2 Md€). Le paquet servi est celui que la
    construction rend."""
    constats = _construction()._constats()
    assert constats == {
        "credits_etat_sncf_ratp": {"annee": 2026, "sncf_meur": 3225.8, "ratp_meur": 885.6},
        "excedent_cnieg": {"annee": 2025, "montant_md": 2.2},
    }
    credits, _ = charger_table_csv(PAP, ("annee", "regime", "poste"), "valeur")
    assert credits[("2026", "sncf", "credits_etat_meur")] == 3225.8
    assert credits[("2026", "ratp", "credits_etat_meur")] == 885.6
    paquet = json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    assert paquet["constats"] == constats
