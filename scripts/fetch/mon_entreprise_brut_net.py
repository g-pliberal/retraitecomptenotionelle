#!/usr/bin/env python3
"""Le salaire net de quelques salariés du privé, par le simulateur de l'Urssaf.

    python scripts/fetch/mon_entreprise_brut_net.py

À quoi il sert. La fiche de paie du moteur (``moteur/js/remuneration.js``)
passe d'un salaire brut à son net, et du net saisi au brut. Ses taux viennent
d'OpenFisca (``openfisca_prelevements.py``), mais aucune source extérieure ne
refaisait le calcul entier. Mon-entreprise, le simulateur de l'Urssaf, le
refait par ses règles publicodes (``modele-social``), que son API publique
évalue sans rien installer : https://mon-entreprise.urssaf.fr/api/v1/evaluate.

Le fichier produit, ``tests/temoins/brut_net_mon_entreprise.json``, est
VERSIONNÉ : ``tests/test_brut_net_mon_entreprise.py`` rejoue la
confrontation hors ligne.

La situation. Un CDI à temps plein, l'année de la date que l'API retient,
sans commune ni forme d'entreprise : ce que la fiche du moteur suppose
d'un employeur type, rien de plus. Mon-entreprise retient par défaut une
complémentaire santé de 40 € par mois, partagée par moitié, que le moteur
reprend (L. 911-7 du code de la sécurité sociale ; action 138).
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

SORTIE = (Path(__file__).resolve().parents[2] / "tests" / "temoins"
          / "brut_net_mon_entreprise.json")

API = "https://mon-entreprise.urssaf.fr/api/v1/evaluate"

#: Les salaires bruts mensuels : le SMIC de 2026 (12,02 € × 151,67 h), des
#: salaires courants, le plafond mensuel, quatre plafonds et au-delà, où
#: l'abattement d'assiette de la CSG s'arrête.
BRUTS = (1823.03, 2000.0, 2500.0, 3000.0, 4005.0, 5000.0, 8000.0, 17000.0)

#: Les grandeurs relevées, mensuelles, en euros.
GRANDEURS = {
    "net": "salarié . rémunération . net . à payer avant impôt",
    "csg_crds": "salarié . cotisations . CSG-CRDS",
    "vieillesse": "salarié . cotisations . vieillesse . salarié",
    "retraite_complementaire": "salarié . cotisations . retraite complémentaire . salarié",
    "ceg": "salarié . cotisations . CEG . salarié",
    "cet": "salarié . cotisations . CET . salarié",
    "apec": "salarié . cotisations . APEC . salarié",
    "sante": "salarié . cotisations . prévoyances . santé . salarié",
    "prevoyances": "salarié . cotisations . prévoyances . salarié",
    "cotisations_salariales": "salarié . cotisations . salarié",
}


def evaluer(situation: dict, expressions: list[str]) -> list:
    corps = json.dumps({"situation": situation, "expressions": expressions}).encode()
    requete = urllib.request.Request(API, corps, {"content-type": "application/json"})
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return json.load(reponse)["evaluate"]


def cas(brut: float, cadre: bool) -> dict:
    situation = {
        "salarié . contrat . salaire brut": f"{brut} €/mois",
        "salarié . contrat": "'CDI'",
        "salarié . contrat . statut cadre": "oui" if cadre else "non",
    }
    noms = list(GRANDEURS)
    resultats = evaluer(situation, [GRANDEURS[n] for n in noms] + ["date"])
    valeurs = {nom: (None if r.get("nodeValue") is None else round(float(r["nodeValue"]), 6))
               for nom, r in zip(noms, resultats)}
    return {"brut": brut, "cadre": cadre, "date": resultats[-1].get("nodeValue"), **valeurs}


def main() -> int:
    cas_releves = [cas(brut, cadre) for cadre in (False, True) for brut in BRUTS]
    sortie = {
        "source": API,
        "recupere_le": date.today().isoformat(),
        "situation": "CDI à temps plein, statut cadre ou non, rien d'autre de dit",
        "grandeurs": GRANDEURS,
        "cas": cas_releves,
    }
    SORTIE.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(cas_releves)} cas écrits dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
