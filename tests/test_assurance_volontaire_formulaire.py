"""Le formulaire du simulateur dit l'assurance volontaire des expatriés.

Chaque période hors de France porte sa catégorie d'assurance volontaire
(L. 742-1, R. 742-4), que la saisie lit sous ``etranger<n>_avv`` ; les règles
qu'elle en tire sont essayées dans ``tests/js/assurance-volontaire.test.js``.
"""

from __future__ import annotations

import re

from retraite_notionnelle.web.site import rendre


def _choix(corps: str, nom: str) -> dict[str, bool]:
    liste = re.search(rf'<select[^>]*name="{nom}"[^>]*>(.*?)</select>', corps, re.S)
    assert liste is not None, f"pas de liste {nom}"
    return {valeur: "selected" in attributs for valeur, attributs
            in re.findall(r'<option value="([^"]*)"([^>]*)>', liste.group(1))}


def test_chaque_periode_hors_de_france_propose_les_trois_categories():
    _, corps = rendre("/simuler", {"naissance": "1962"})
    assert set(_choix(corps, "etranger1_avv")) == {"", "1", "2", "3"}


def test_la_categorie_saisie_reste_choisie():
    _, corps = rendre("/simuler", {
        "naissance": "1962-03-15", "debut": "1984-01-01",
        "etranger1_pays": "autre", "etranger1_debut": "2015-01-01",
        "etranger1_fin": "2025-01-01", "etranger1_avv": "3"})
    choix = _choix(corps, "etranger1_avv")
    assert choix["3"] and not choix[""]
