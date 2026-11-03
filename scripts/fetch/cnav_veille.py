#!/usr/bin/env python3
"""La veille de la base de législation de la Cnav : ce qu'elle a changé depuis
le registre.

    python scripts/fetch/cnav_veille.py   # ce que python scripts/veille_droit.py en imprime

POURQUOI IL EXISTE (action 175, étape 5). Le registre,
``data/reference/legislation/cnav/``, porte chaque objet de la base avec son
sort et la date de la version qui l'a reçu. L'exploitation de la base ne reste
entière que si l'on voit ce qu'elle change ensuite : un barème ou un exposé
modifié, un objet neuf, une circulaire nouvelle. Ce module le dit, sans rien
écrire, et ``scripts/veille_droit.py``, le premier et le dernier geste d'une
session qui touche au scénario 1, l'imprime. Le registre, c'est
``cnav_legislation.py`` qui le tient : il inscrit le neuf ``a_lire``, et
prend la date de ce qui attend encore.

CE QU'IL DEMANDE, quatre requêtes à la fois. D'un appel chacune, les
collections que l'API date — ``/baremes``, ``/expose``, les trois des fenêtres
d'information, les avis de mise à jour (``/mises-a-jour``) — et ``/liste``,
qu'elle ne date pas ; ses dernières circulaires
(``/reference/dernieresCirculaires/``) ; sa recherche, à l'année de la veille
et à la précédente, qui sert des références que rien ne lie. Ni les
références une à une, que l'API ne date pas, ni les documents joints, que le
site sert un par un hors de l'API : le récupérateur les relit, et dit ceux
qui ont changé.

CE QU'IL DIT, par genre : ce que le registre ne porte pas ; ce dont la date a
changé depuis son sort, qui se relit, sort compris ; ce dont la date a changé
quand il attend encore d'être lu, que le récupérateur redatera ; ce que la
base ne sert plus. Puis les références que le registre ne porte pas, ou sans
titre, parmi les dernières circulaires et ce que sert la recherche ; le geste
qui les inscrit ; et ce que le registre garde à lire, qui mesure
l'exploitation : quand il n'y reste rien, la ligne ``cnav_legislation_portail``
du vivier passe ``epuise``. Une base qui ne répond pas se dit d'une ligne.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cnav_api  # noqa: E402,F401  (l'adresse et l'en-tête, par cnav_legislation)
import cnav_legislation  # noqa: E402

#: Le registre que la veille compare à la base, lu à chaque veille.
REGISTRE = cnav_legislation.REGISTRE
#: Les collections que la veille demande, par genre : leurs routes, la clé du
#: nom d'un objet, celle de sa date — aucune pour une liste, que l'API ne date
#: pas.
COLLECTIONS = {
    "baremes": (("/baremes",), "fileLeafRef", "dateModification"),
    "exposes": (("/expose",), "fileLeafRef", "dateModification"),
    "listes": (("/liste",), "file_leaf_ref", None),
    "fenetres": (tuple(f"/{cle}" for cle in cnav_legislation.NATURES), "file_leaf_ref",
                 "date_modification"),
    "mises_a_jour": (("/mises-a-jour",), "id", "dateModification"),
}
#: Au-delà, la recherche tait le reste : la recherche entière la mène par mois.
PLAFOND = 250
LIBELLES = {"baremes": "barèmes", "exposes": "exposés", "listes": "listes",
            "references": "références", "fenetres": "fenêtres d'information",
            "mises_a_jour": "avis de mise à jour", "documents": "documents joints"}
#: Ce que dit chaque changement, et ce qu'il demande.
CHANGEMENTS = {"neufs": "pas au registre",
               "modifies": "date changée depuis le sort, à relire",
               "redates": "date changée, encore à lire",
               "disparus": "plus à la base"}
#: Ce que lève une base qui ne répond pas, ou pas en JSON ; et une réponse dont
#: la forme a changé, que la veille ne sait plus lire.
PANNES = (urllib.error.URLError, TimeoutError, OSError, ValueError)
ILLISIBLES = (KeyError, TypeError, AttributeError)
#: Les éléments qu'une ligne énumère, avant de compter les autres.
ENUMERES = 12


# -- ce que la base sert ----------------------------------------------------


def lire_la_base(annees: list[int]) -> dict:
    """Ce que la veille demande à la base. ``servis`` : par genre et par nom,
    le titre et la date de modification de chaque objet que sert sa
    collection — la plus récente d'un objet servi deux fois, sans la zone que
    l'API y accroche —, et le jour d'un avis. ``circulaires`` : les dernières,
    telles que l'API les sert. ``recherche`` : à chaque année, les références
    que sert la recherche, par nom, avec leur titre, ou rien si elle n'a pas
    répondu ; ``plafonnees``, celles qui ont atteint le plafond. Les
    dernières circulaires, quelques kilo-octets, se demandent d'abord, deux
    fois au plus : une base injoignable se dit en deux secondes, et non en
    une demi-minute de reprises."""
    circulaires = cnav_legislation._obtenir(cnav_legislation.DERNIERES_CIRCULAIRES, essais=2)
    routes = [route for routes, _, _ in COLLECTIONS.values() for route in routes]
    phrases = [str(annee) for annee in annees]
    with ThreadPoolExecutor(cnav_legislation.EN_PARALLELE) as pool:
        reponses = dict(zip(routes, pool.map(cnav_legislation._obtenir, routes)))
        resultats = dict(pool.map(cnav_legislation._chercher, phrases))
    servis: dict[str, dict[str, dict]] = {}
    for genre, (routes_du_genre, cle, cle_date) in COLLECTIONS.items():
        fiches = [fiche for route in routes_du_genre for fiche in reponses[route] or []]
        servis[genre] = {}
        for nom, memes in cnav_legislation._index(fiches, cle).items():
            servi = {"titre": cnav_legislation._titre(memes[0].get("titre") or "")}
            if cle_date:
                servi["modifie_le"] = cnav_legislation.instant(
                    max(fiche.get(cle_date) or "" for fiche in memes))
            if genre == "mises_a_jour":
                servi["date_maj"] = cnav_legislation.date_du_texte(memes[0].get("dateMaj") or "")
            servis[genre][str(nom)] = servi
    recherche: dict[str, dict[str, str] | None] = {}
    for phrase, liste in resultats.items():
        if liste is None:
            recherche[phrase] = None
            continue
        recherche[phrase] = {}
        for resultat in liste:
            nom = (resultat.get("filename") or "").strip()
            if nom.lower().endswith((".aspx", ".pdf")) and nom not in recherche[phrase]:
                recherche[phrase][nom] = cnav_legislation._titre(resultat.get("titre") or "")
    return {"servis": servis,
            "circulaires": circulaires or [],
            "recherche": recherche,
            "plafonnees": sorted(phrase for phrase, liste in resultats.items()
                                 if liste is not None and len(liste) >= PLAFOND)}


# -- ce qui a changé --------------------------------------------------------


def comparer(registre: dict[str, dict[str, dict]],
             servis: dict[str, dict[str, dict]]) -> dict[str, dict[str, list[str]]]:
    """Pour chaque genre que la base a servi, ce qui a changé depuis le
    registre : ``neufs``, ce qu'il ne porte pas ; ``modifies``, ce dont la date
    a changé depuis son sort ; ``redates``, ce dont la date a changé quand il
    attend encore d'être lu ; ``disparus``, ce que la base ne sert plus. Un
    objet que le registre porte sans titre, que la base nomme sans le servir,
    ne disparaît pas."""
    changements: dict[str, dict[str, list[str]]] = {}
    for genre, lus in servis.items():
        portes = registre.get(genre, {})
        cle = cnav_legislation.DATES[genre]
        trouves: dict[str, list[str]] = {quoi: [] for quoi in CHANGEMENTS}
        for nom, lu in lus.items():
            ancien = portes.get(nom)
            if ancien is None:
                trouves["neufs"].append(nom)
            elif cle and lu.get(cle) != ancien.get(cle):
                trouves["redates" if ancien["sort"] == "a_lire" else "modifies"].append(nom)
        trouves["disparus"] = [nom for nom, ancien in portes.items()
                               if nom not in lus and (ancien.get("titre") or "").strip()]
        changements[genre] = {quoi: sorted(noms) for quoi, noms in trouves.items()}
    return changements


def references_nouvelles(references: dict[str, dict], noms) -> list[str]:
    """Les références nommées que le registre ne porte sous aucune casse — la
    base en lie sous une majuscule fautive —, ou qu'il porte sans titre,
    nommées par la base sans être servies : une référence n'a pas de date de
    modification, elle n'est que nouvelle ou connue."""
    connues = {nom.lower() for nom, ligne in references.items()
               if (ligne.get("titre") or "").strip()}
    return sorted({nom for nom in noms if nom and nom.lower() not in connues})


# -- ce que la veille imprime -----------------------------------------------


def _enumerer(elements: list[str]) -> str:
    restent = len(elements) - ENUMERES
    return " ; ".join(elements[:ENUMERES]) + (f" ; et {restent} autres" if restent > 0 else "")


def _decrire(quoi: str, nom: str, ancien: dict | None, lu: dict | None) -> str:
    """Un objet qui a changé : un neuf, de son titre — et d'un avis, de son
    jour — ; ce qui a changé depuis son sort, du script qui le lit ou de son
    renvoi ; ce que la base ne sert plus, de son sort."""
    if quoi == "neufs" and lu:
        jour = f"{lu['date_maj']}, " if lu.get("date_maj") else ""
        return f"{nom} ({jour}{lu.get('titre') or 'sans titre'})"
    if quoi == "modifies" and ancien:
        return f"{nom} [{ancien['sort']} : {ancien.get('script') or ancien.get('renvoi')}]"
    if quoi == "disparus" and ancien and ancien["sort"] != "a_lire":
        return f"{nom} [{ancien['sort']}]"
    return nom


def _chemin(dossier: Path) -> str:
    try:
        return dossier.relative_to(cnav_legislation.RACINE).as_posix() + "/"
    except ValueError:
        return str(dossier)


def a_lire(registre: dict[str, dict[str, dict]]) -> str:
    """Ce que le registre garde à lire, qui mesure l'exploitation de la base."""
    total = restent = 0
    par_genre = []
    for genre in cnav_legislation.GENRES:
        lignes = registre.get(genre, {})
        total += len(lignes)
        attendent = len([ligne for ligne in lignes.values() if ligne["sort"] == "a_lire"])
        restent += attendent
        if attendent:
            par_genre.append(f"{LIBELLES[genre]} {attendent}")
    detail = f" — {', '.join(par_genre)}" if par_genre else ""
    return (f"  Le registre : {total} objets, dont {restent} à lire{detail} ; quand il n'y "
            "reste rien à lire, la ligne cnav_legislation_portail du vivier passe epuise.")


def rapport(registre: dict[str, dict[str, dict]], base: dict, dossier: Path = REGISTRE) -> list[str]:
    """Les lignes de la veille : ce que chaque collection a changé depuis le
    registre, les références qu'il ne porte pas, le geste qui les inscrit, et
    ce qu'il garde à lire."""
    lignes = [f"La base de législation de la Cnav, comparée à son registre ({_chemin(dossier)}) :"]
    changements = comparer(registre, base["servis"])
    for genre, trouves in changements.items():
        servis = base["servis"][genre]
        if not any(trouves.values()):
            lignes.append(f"  {LIBELLES[genre]} : {len(servis)} à la base, rien de changé")
            continue
        lignes.append(f"  {LIBELLES[genre]} : {len(servis)} à la base")
        for quoi, noms in trouves.items():
            if noms:
                lignes.append(f"    {CHANGEMENTS[quoi]} ({len(noms)}) : " + _enumerer([
                    _decrire(quoi, nom, registre.get(genre, {}).get(nom), servis.get(nom))
                    for nom in noms]))

    references = registre.get("references", {})
    circulaires = {(fiche.get("file_leaf_ref") or "").strip(): fiche
                   for fiche in base["circulaires"]}
    nouvelles = references_nouvelles(references, circulaires)
    entete = (f"  dernières circulaires ({cnav_legislation.DERNIERES_CIRCULAIRES}) : "
              f"{len(circulaires)} à la base")
    lignes.append(entete + ("" if nouvelles else ", toutes au registre"))
    if nouvelles:
        lignes.append(f"    pas au registre ({len(nouvelles)}) :")
        for nom in nouvelles:
            fiche = circulaires[nom]
            lignes.append(f"      - {cnav_legislation._titre(fiche.get('titre') or nom)} : "
                          f"{cnav_legislation._titre(fiche.get('objet') or '')} ({nom})")

    recherche = base["recherche"]
    servies = {nom: titre for titres in recherche.values() if titres
               for nom, titre in titres.items()}
    deja = {nom.lower() for nom in nouvelles}
    autres = [nom for nom in references_nouvelles(references, servies) if nom.lower() not in deja]
    entete = (f"  recherche des années {' et '.join(recherche)} : "
              f"{len(servies)} références servies")
    lignes.append(entete + ("" if autres else ", rien d'autre de neuf"))
    if autres:
        lignes.append(f"    pas au registre, hors des dernières circulaires ({len(autres)}) :")
        lignes += [f"      - {servies[nom] or 'sans titre'} ({nom})" for nom in autres]
    muettes = [phrase for phrase, titres in recherche.items() if titres is None]
    if muettes:
        lignes.append(f"    sans réponse : {', '.join(muettes)} — relancer la veille")
    if base.get("plafonnees"):
        lignes.append(f"    plafonnée à {PLAFOND} résultats : {', '.join(base['plafonnees'])} — "
                      "python scripts/fetch/cnav_legislation.py --chercher la mène par mois")

    if any(any(trouves.values()) for trouves in changements.values()) or nouvelles or autres:
        lignes.append("  Le neuf entre au registre, à lire, et ce qui attend y prend sa date : "
                      "python scripts/fetch/cnav_legislation.py, qui relit aussi les documents "
                      "joints ; ce qui a changé depuis son sort se relit, sort compris.")
    else:
        lignes.append("  Rien de neuf depuis le registre ; les documents joints, "
                      "python scripts/fetch/cnav_legislation.py les relit.")
    lignes.append(a_lire(registre))
    return lignes


def veille(aujourd_hui: date | None = None) -> list[str]:
    """La section que ``scripts/veille_droit.py`` imprime : le registre et la
    base, lus à l'instant, comparés à l'année de la veille et à la précédente.
    Une base qui ne répond pas se dit, sans lever : la veille du droit
    continue."""
    aujourd_hui = aujourd_hui or date.today()
    registre = {genre: cnav_legislation.lire_registre(genre, REGISTRE)
                for genre in cnav_legislation.GENRES}
    try:
        base = lire_la_base(cnav_legislation.annees_recentes(aujourd_hui.year))
    except PANNES as erreur:
        return [f"La base de législation de la Cnav n'a pas répondu "
                f"({getattr(erreur, 'reason', erreur)}) : relancer python scripts/veille_droit.py "
                "pour la comparer à son registre.", a_lire(registre)]
    except ILLISIBLES as erreur:
        return [f"La base de législation de la Cnav a répondu sous une forme que la veille ne "
                f"lit pas ({type(erreur).__name__} : {erreur}) : scripts/fetch/cnav_veille.py "
                "est à reprendre.", a_lire(registre)]
    return rapport(registre, base, REGISTRE)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--date", help="date de la veille (AAAA-MM-JJ) : ses années de recherche")
    arguments = analyseur.parse_args(argv)
    print("\n".join(veille(date.fromisoformat(arguments.date) if arguments.date else None)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
