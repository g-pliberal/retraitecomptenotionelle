"""La saisie des périodes assimilées (action 130, sixième domaine, étape 5).

Le formulaire déclare les périodes — stages de la formation professionnelle,
TUC et stages d'insertion, sportifs de haut niveau, congé supplémentaire de
naissance — et la ligne de carrière qui est un contrat d'apprentissage ; les
fiches décident de ce que chacune valide (``droit/compter.py``). Ce fichier
tient la lecture, les refus, l'adresse réécrite, et les deux moteurs d'accord.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.web.site import ErreurSite

from outils_pont import Saisies, refus_de_la_saisie, saisie_du_portage

RACINE = Path(__file__).resolve().parent.parent

#: Une ancienne des TUC, entrée au régime général en 1987 ; la même, apprentie
#: avant ; une stagiaire de la formation professionnelle, au jour près ; un
#: relevé, que la période complète.
BASE = {"naissance": "1966-04-10", "debut": "1987-09", "liquidation": "2030-05",
        "unite_revenu": "euros_mois"}
TUC = {"assimilee1_motif": "stage_d_insertion", "assimilee1_dispositif": "tuc",
       "assimilee1_debut": "1985-10-01", "assimilee1_fin": "1986-09-30"}
CAS = [
    {**BASE, **TUC},
    {**BASE, "debut": "1983-09", "apprentissage": "1", "metier2_debut": "1985-09",
     "metier2_statut": "salarie_prive_non_cadre", "metier2_salaire": "2500"},
    {**BASE, "debut": "1984-09", "metier2_debut": "2016-01",
     "metier2_statut": "chomage_non_indemnise",
     "metier2_salaire": "", "metier3_debut": "2017-01",
     "metier3_statut": "salarie_prive_non_cadre", "metier3_salaire": "3000",
     "assimilee1_motif": "stage_de_formation_professionnelle",
     "assimilee1_debut": "2016-03-07", "assimilee1_fin": "2016-07-01",
     "assimilee1_jours": "80"},
]
REFUS = [
    ({**BASE, "assimilee1_motif": "rachat", "assimilee1_debut": "1985",
      "assimilee1_fin": "1986"}, "n'est pas un motif possible"),
    ({**BASE, "assimilee1_motif": "stage_d_insertion", "assimilee1_debut": "1985",
      "assimilee1_fin": "1986"}, "nomme son dispositif"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_dispositif": "tuc",
      "assimilee1_debut": "1985", "assimilee1_fin": "1986"}, "seul un stage d'insertion"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_debut": "1985",
      "assimilee1_fin": "1984"}, "après avoir commencé"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_debut": "1985-13",
      "assimilee1_fin": "1986"}, "attendu en AAAA"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_debut": "1960",
      "assimilee1_fin": "1986"}, "après la naissance"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_debut": "2031",
      "assimilee1_fin": "2032"}, "avant le départ"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_debut": "1985",
      "assimilee1_fin": "1986", "assimilee1_jours": "366"}, "de 1 à 365"),
    ({**BASE, "assimilee1_debut": "1985", "assimilee1_fin": "1986"}, "indiquer son motif"),
    ({**BASE, "assimilee1_motif": "sportif_de_haut_niveau", "assimilee1_debut": "1985"},
     "celui où elle finit"),
    ({**BASE, "apprentissage": "2"}, "n'existe pas"),
    ({**BASE, "apprentissage": "2", "metier2_debut": "2016-01",
      "metier2_statut": "chomage_non_indemnise"},
     "période sans emploi"),
    ({**BASE, "apprentissage": "1", "releve": "2020:salarie_prive_non_cadre:30000"},
     "un relevé de carrière ne le porte pas"),
]

def test_la_saisie_declare_les_periodes_a_la_chronologie():
    """Les lignes lues deviennent les tables que la chronologie reçoit, et
    l'adresse réécrite les relit à l'identique ; sans elles, rien n'est dit
    et la présomption tient."""
    saisie = saisie_du_portage(CAS[0])
    assert saisie.periodes_assimilees_declarees() == [
        {"motif": "stage_d_insertion", "debut": "1985-10-01", "fin": "1986-09-30",
         "dispositif": "tuc"}]
    relue = saisie_du_portage(dict(parse_qsl(saisie.requete(), keep_blank_values=True)))
    assert relue.assimilees == saisie.assimilees
    assert saisie_du_portage(BASE).periodes_assimilees_declarees() == []
    stagiaire = saisie_du_portage(CAS[2])
    assert stagiaire.periodes_assimilees_declarees()[0]["jours"] == 80
    carriere = Saisies().carriere(CAS[0])
    periodes = chrono.periodes_assimilees(carriere.chronologie, chrono.ASSURE)
    assert [p["attributs"]["dispositif"] for p in periodes] == ["tuc"]


def test_l_apprentissage_se_pose_sur_sa_ligne_de_carriere():
    """Le rang désigne la ligne ; le métier, et lui seul, porte l'attribut
    dans la chronologie, et l'adresse le récrit."""
    saisie = saisie_du_portage(CAS[1])
    carriere = Saisies().carriere(CAS[1])
    emplois = [p for p in chrono.periodes(carriere.chronologie, chrono.ASSURE)
               if p["sorte"] == chrono.EMPLOI]
    assert [bool(p["attributs"].get("apprentissage")) for p in emplois] == [True, False]
    assert "apprentissage=1" in saisie.requete()


def test_les_periodes_comptent():
    """Les TUC de 1985-1986 ajoutent des trimestres à la carrière qui les
    déclare : ce que la fiche valide, la saisie le fait jouer."""
    saisies = Saisies()
    sans = saisies.simuler(BASE).actuel.trimestres_valides
    avec = saisies.simuler(CAS[0]).actuel.trimestres_valides
    assert avec > sans


@pytest.mark.parametrize(("requete", "message"), REFUS)
def test_la_saisie_refuse(requete, message):
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(message)):
        saisie_du_portage(requete)


def test_les_deux_moteurs_lisent_les_memes_periodes():
    """Le résultat entier est le même en Python et en JavaScript, sur la
    carrière que la saisie du portage bâtit : ses refus, sans jumelle, ont
    leur test plus haut."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini
    saisies = Saisies()
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas in CAS]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(json.dumps(attendus, ensure_ascii=False))
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]
