"""La version d'une fiche qui s'applique à une situation (§ 4.1).

``docs/architecture.md``, § 4.1 et 6.7. Les versions d'une fiche forment un
partage de ses dates qui décident, que :mod:`.partage` contrôle sur chaque
fiche : pour des dates données, une version et une seule s'applique, aux
exceptions déclarées près (``exception_de``). Le moteur la lit ici, et ne lit
d'elle que ce qu'il calcule : ses bornes, son texte et les paramètres de son
contenu (``contenu.parametres``).

Une fiche que le moteur lit passe par :func:`preparer`, qui en garde ces
seules données, les dates écrites en texte (AAAA-MM-JJ) : c'est la forme que le
paquet du site porte, et que son jumeau, ``moteur/js/versions.js``, lit de la
même façon. Deux dates écrites ainsi se comparent comme deux textes.

Le moteur observe le droit à la date où il calcule : toutes les versions de la
fiche sont connues (§ 4.9 ; l'axe d'observation attend son domaine, § 13.5).
"""

from __future__ import annotations

from datetime import date, datetime


def _jour(valeur) -> str | None:
    """Une borne, écrite AAAA-MM-JJ ; ``None`` pour « sans borne »."""
    if valeur is None:
        return None
    if isinstance(valeur, datetime):
        valeur = valeur.date()
    if isinstance(valeur, date):
        return valeur.isoformat()
    return str(valeur)


def preparer(fiche: dict) -> dict:
    """Ce que le moteur lit d'une fiche : son identifiant, ses dates qui
    décident, et chaque version réduite à son identifiant, ses bornes, son
    exception, le texte qui la fait naître et ses paramètres."""
    versions = []
    for version in fiche.get("versions") or []:
        textes = [t for t in version.get("textes") or [] if isinstance(t, dict)]
        texte = version.get("nee_de") or next(
            (t.get("id") or t.get("reference") for t in textes), None)
        versions.append({
            "id": version["id"],
            "bornes": {nom: [_jour(debut), _jour(fin)]
                       for nom, (debut, fin) in (version.get("bornes") or {}).items()},
            "exception_de": version.get("exception_de"),
            "texte": texte,
            "parametres": dict((version.get("contenu") or {}).get("parametres") or {}),
        })
    return {"id": fiche["id"], "dates_qui_decident": list(fiche.get("dates_qui_decident") or []),
            "versions": versions}


def applicable(fiche: dict, dates: dict[str, str]) -> dict | None:
    """La version d'une fiche préparée (:func:`preparer`) qui s'applique à ces
    dates, ``{date nommée: AAAA-MM-JJ}`` ; ``None`` si aucune ne s'applique.

    Chaque date qui décide doit être donnée : une date qui manque, ou que la
    fiche ne déclare pas, arrête le calcul plutôt que de laisser choisir une
    version au hasard (§ 6.7). Quand deux versions s'appliquent, celle qui se
    déclare l'exception de l'autre l'emporte ; le partage, contrôlé sur chaque
    fiche, garantit qu'il n'en reste qu'une.
    """
    noms = fiche["dates_qui_decident"]
    inconnues = set(dates) - set(noms)
    manquantes = set(noms) - set(dates)
    if inconnues or manquantes:
        raise ValueError(
            f"{fiche['id']} : dates qui décident {sorted(noms)}, reçu {sorted(dates)}")
    valent = []
    for version in fiche["versions"]:
        for nom in noms:
            debut, fin = version["bornes"].get(nom) or [None, None]
            jour = dates[nom]
            if (debut is not None and jour < debut) or (fin is not None and jour >= fin):
                break
        else:
            valent.append(version)
    restent = [v for v in valent
               if not any(autre.get("exception_de") == v["id"] for autre in valent)]
    if len(restent) > 1:
        raise ValueError(f"{fiche['id']} : {[v['id'] for v in restent]} s'appliquent "
                         f"toutes à {dates}, et le partage n'en admet qu'une")
    return restent[0] if restent else None
