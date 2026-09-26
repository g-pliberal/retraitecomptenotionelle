"""Préparer la chronologie (docs/architecture.md, § 7.2).

La première des quatre étapes qui construisent le relevé des droits : ce que
la saisie ne dit pas, une présomption le pose, en son nom, sans jamais
remplacer un fait déclaré (§ 5.6). L'étape lit une chronologie et en écrit
une : son schéma est le contrat C.1
(``data/reference/etapes/preparer_la_chronologie.yaml``).

Les constructeurs de la carrière, vue de la chronologie, l'appliquent avant
d'en tirer les années : la chronologie qu'une carrière porte est préparée.
Son jumeau est ``moteur/js/droit/preparer.js``.
"""

from __future__ import annotations

from .. import chronologie as chrono


def preparer(chronologie: dict, presomptions: dict | None = None) -> dict:
    """La chronologie complétée par les présomptions du vocabulaire, ou par
    celles que ``presomptions`` donne ({nom: {valeur}}) : voir
    :func:`~retraite_notionnelle.chronologie.completer`."""
    return chrono.completer(chronologie, presomptions)
