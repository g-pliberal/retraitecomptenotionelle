"""La confrontation hebdomadaire à TRAJECTOiRE, versions 3 : ce qui prévient.

`scripts/confronter_trajectoire.py` rejoue, dans GitHub Actions et sans poste,
la confrontation du scénario 1 à TRAJECTOiRE (`.github/workflows/
trajectoire.yml`), et compare ses écarts à la référence figée,
`tests/temoins/trajectoire_3/ecarts.json`. Ces tests tiennent la règle de
l'alerte — une quantité qui concordait et s'écarte est une rupture, rien
d'autre ne l'est —, la référence et son témoin, et le fait que la confrontation
reste à l'écart des envois : elle ne lance ici ni R ni le scénario 1, que le
workflow lance chaque semaine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))

import confronter_trajectoire as confrontation  # noqa: E402

WORKFLOW = RACINE / ".github" / "workflows" / "trajectoire.yml"


def _mesure(**quantites) -> dict:
    return {"cas": {"cas_a": {"quantites": {
        nom: {"ecart": ecart, "statut": statut} for nom, (ecart, statut) in quantites.items()}}}}


def test_une_quantite_qui_concordait_et_s_ecarte_est_une_rupture():
    reference = _mesure(taux=(0.0, "concorde"), regime_general=(0.001, "concorde"))
    mesure = _mesure(taux=(-0.0125, "ecart"), regime_general=(0.001, "concorde"))
    bilan = confrontation.comparer(reference, mesure)
    assert bilan["ruptures"] == ["cas_a, taux : -0.0125, concordait (+0.0000)"]
    assert not bilan["accords"] and not bilan["deplaces"] and not bilan["nouveaux"]


def test_une_quantite_qui_concordait_et_n_est_plus_mesuree_est_une_rupture():
    reference = _mesure(taux=(0.0, "concorde"), rafp=(0.05, "ecart"))
    bilan = confrontation.comparer(reference, _mesure())
    assert bilan["ruptures"] == ["cas_a, taux : n'est plus mesuré, concordait"]
    assert confrontation.comparer(reference, {"cas": {}})["ruptures"] == bilan["ruptures"]


def test_un_accord_nouveau_un_ecart_deplace_une_quantite_nouvelle_ne_rompent_rien():
    reference = _mesure(taux=(-0.0125, "ecart"), rafp=(0.05, "ecart"), cnavpl=(None, "ecart"))
    mesure = _mesure(taux=(0.0, "concorde"), rafp=(0.08, "ecart"), cnavpl=(None, "ecart"),
                     asv=(0.02, "ecart"))
    bilan = confrontation.comparer(reference, mesure)
    assert not bilan["ruptures"]
    assert bilan["accords"] == ["cas_a, taux : +0.0000, s'écartait (-0.0125)"]
    assert bilan["deplaces"] == ["cas_a, rafp : +0.0800, était +0.0500"]
    assert bilan["nouveaux"] == ["cas_a, asv : +0.0200 (ecart)"]


def test_un_ecart_qui_bouge_de_moins_que_le_seuil_n_a_pas_bouge():
    reference = _mesure(rafp=(0.0500, "ecart"))
    bilan = confrontation.comparer(reference, _mesure(rafp=(0.0515, "ecart")))
    assert bilan == {"ruptures": [], "accords": [], "deplaces": [], "nouveaux": []}


def test_la_reference_et_son_temoin_disent_la_version_epinglee():
    reference = json.loads(confrontation.REFERENCE.read_text(encoding="utf-8"))
    temoin = json.loads(confrontation.TEMOIN.read_text(encoding="utf-8"))
    version = confrontation.ETIQUETTE.removeprefix("v")
    assert reference["version"].startswith(version)
    assert temoin["version"].startswith(version)
    assert temoin["commit"] == confrontation.COMMIT
    assert temoin["licence"] == "EUPL-1.2" and "n'entre pas au dépôt" in temoin["origine"]
    assert set(reference["cas"]) == set(temoin["cas"])
    # La date de l'exécution ferait une référence différente chaque semaine.
    assert "execute_le" not in temoin


def test_la_reference_porte_les_cas_types_que_les_versions_3_ajoutent():
    reference = json.loads(confrontation.REFERENCE.read_text(encoding="utf-8"))
    medecin = reference["cas"]["cor_13_1960"]["quantites"]
    assert {"cnavpl", "carmf_complementaire", "asv_conventionnes"} <= set(medecin)
    assert {"msa_non_salaries", "msa_rco"} <= set(reference["cas"]["cor_12_1960"]["quantites"])
    for cas in reference["cas"].values():
        for valeur in cas["quantites"].values():
            assert valeur["statut"] in ("concorde", "ecart")


def test_le_script_r_appelle_trajectoire_sans_le_recopier():
    """Le script R charge le paquet installé à part et n'appelle que ce qu'il
    exporte : aucune ligne de TRAJECTOiRE, dont chaque fichier porte l'en-tête
    de la DREES, n'y entre."""
    texte = confrontation.SCRIPT_R.read_text(encoding="utf-8")
    assert "Logiciel elabore par l'État, via la Drees" not in texte
    assert "library(trajectoire)" in texte and "lancerCasTypesCor(" in texte
    assert "genererRapport = FALSE" in texte


def test_la_confrontation_reste_a_l_ecart_des_envois():
    """Elle se lance chaque semaine ou à la demande, jamais à un envoi sur
    main : la suite complète n'en est pas allongée. Elle installe la version
    que le script épingle."""
    texte = WORKFLOW.read_text(encoding="utf-8")
    declencheurs = texte.split("\njobs:")[0]
    assert "schedule:" in declencheurs and "workflow_dispatch:" in declencheurs
    assert "push:" not in declencheurs and "pull_request" not in declencheurs
    assert "confronter_trajectoire.py --epingle" in texte
    assert "git.drees.fr" in texte
