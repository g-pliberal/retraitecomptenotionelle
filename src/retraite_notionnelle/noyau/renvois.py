"""Les renvois des versions, contrôlés d'une fiche à l'autre.

Note de décision 0009 et son second rectificatif (« Un renvoi nomme une
valeur, et se contrôle à la fabrication »). Le partage (:mod:`.partage`) ne
regarde qu'une fiche à la fois ; un renvoi en relie deux. Une version peut
porter deux sortes de renvois, dont le contrat de la fiche fixe la forme
(``data/reference/contrats/fiche.yaml``) :

- ``contenu.renvois`` — des renvois datés : la version lit une valeur dans la
  version d'une autre fiche, que choisit la date nommée ;
- ``contenu.redaction_anterieure`` — ce que son texte laisse à sa rédaction
  antérieure, une autre version de la même fiche, nommée par son identifiant.

Ce module dit ce qui ne tient pas : la fiche lue n'existe pas, ne se choisit
pas à la seule date du renvoi, n'a pas une version et une seule sur toute
l'étendue des bornes de la version qui lit, ne porte pas la valeur nommée ;
la rédaction antérieure n'est pas une autre version de la fiche ; une chaîne
de renvois boucle. La carte le joue (:func:`..carte.controler`), et la
fabrication des vues avant d'écrire : un renvoi sans cible ne passe pas dans
les données. L'arrêt du calcul, dans le moteur, ne reste que comme ceinture.
"""

from __future__ import annotations

from datetime import date

from .partage import BAS, HAUT, _date

Noeud = tuple[str, str]


def _versions(fiche: dict) -> list[dict]:
    return [v for v in fiche.get("versions") or [] if isinstance(v, dict)]


def _contenu(version: dict) -> dict:
    contenu = version.get("contenu")
    return contenu if isinstance(contenu, dict) else {}


def renvois_de(version: dict) -> list[dict]:
    """Les renvois datés d'une version."""
    return [r for r in _contenu(version).get("renvois") or [] if isinstance(r, dict)]


def anterieure_de(version: dict) -> dict | None:
    """Le renvoi d'une version à sa rédaction antérieure, s'il y en a un."""
    anterieure = _contenu(version).get("redaction_anterieure")
    return anterieure if isinstance(anterieure, dict) else None


def _intervalle(version: dict, nom: str) -> tuple[date, date]:
    debut, fin = (version.get("bornes") or {}).get(nom) or [None, None]
    return _date(debut) or BAS, _date(fin) or HAUT


def _valent(fiche: dict, nom: str, jour: date) -> list[dict]:
    """Les versions de la fiche qui valent ce jour-là, exceptions levées."""
    valent = [v for v in _versions(fiche)
              if _intervalle(v, nom)[0] <= jour < _intervalle(v, nom)[1]]
    return [v for v in valent
            if not any(autre.get("exception_de") == v["id"] for autre in valent)]


def _lues(lisante: dict, fiche: dict, lue: dict, nom: str) -> tuple[list[dict], list[str]]:
    """Les versions de ``lue`` que la version ``lisante`` peut lire à la date
    ``nom``, et ce qui empêche qu'il y en ait une et une seule à chaque jour
    de son étendue, coupée à chaque borne de la fiche lue qui y tombe."""
    etendue = _intervalle(lisante, nom) if nom in (fiche.get("dates_qui_decident") or []) \
        else (BAS, HAUT)
    bords = {etendue[0], etendue[1]}
    for version in _versions(lue):
        bords |= {x for x in _intervalle(version, nom) if etendue[0] < x < etendue[1]}
    lues: dict[str, dict] = {}
    erreurs = []
    # Entre deux bords, les mêmes versions valent : le premier jour suffit.
    for jour in sorted(bords)[:-1]:
        valent = _valent(lue, nom, jour)
        lues.update({v["id"]: v for v in valent})
        if not valent:
            erreurs.append(f"aucune version de « {lue['id']} » pour {nom} = {jour}")
        elif len(valent) > 1:
            erreurs.append(f"{' et '.join(v['id'] for v in valent)} de « {lue['id']} » "
                           f"valent ensemble pour {nom} = {jour}")
    return list(lues.values()), erreurs[:3]


def porte(fiche: dict, version: dict, valeur: str, _vues: frozenset = frozenset()) -> bool:
    """La version porte-t-elle la valeur qu'un renvoi nomme ? Un de ses
    paramètres, la colonne de sa table, ou ce que porte la rédaction
    antérieure à laquelle elle renvoie."""
    contenu = _contenu(version)
    if valeur in (contenu.get("parametres") or {}):
        return True
    table = contenu.get("table")
    if isinstance(table, dict) and table.get("valeur") == valeur:
        return True
    anterieure = anterieure_de(version)
    if anterieure and version["id"] not in _vues:
        cible = next((v for v in _versions(fiche) if v["id"] == anterieure.get("version")), None)
        return cible is not None and porte(fiche, cible, valeur, _vues | {version["id"]})
    return False


def controler(fiches: dict[str, dict]) -> list[str]:
    """Ce qui ne tient pas dans les renvois des fiches : rien, s'ils tiennent.
    ``fiches`` : chaque fiche sous son identifiant."""
    erreurs: list[str] = []
    aretes: dict[Noeud, list[Noeud]] = {}
    for nom, fiche in fiches.items():
        ids = {v["id"] for v in _versions(fiche)}
        for version in _versions(fiche):
            ici = f"{nom}.{version['id']}"
            suivants = aretes.setdefault((nom, version["id"]), [])
            anterieure = anterieure_de(version)
            if anterieure:
                cible = anterieure.get("version")
                if cible == version["id"]:
                    erreurs.append(f"{ici} : sa rédaction antérieure est elle-même")
                elif cible not in ids:
                    erreurs.append(f"{ici} : sa rédaction antérieure, « {cible} », "
                                   "n'est pas une version de la fiche")
                else:
                    suivants.append((nom, cible))
            for renvoi in renvois_de(version):
                cible, date_nommee, valeur = (renvoi.get(c) for c in ("fiche", "date", "valeur"))
                lue = fiches.get(cible)
                if lue is None or cible == nom:
                    erreurs.append(f"{ici} : renvoie à « {cible} », qui n'est pas une "
                                   "autre fiche de la carte")
                    continue
                dates = list(lue.get("dates_qui_decident") or [])
                if dates != [date_nommee]:
                    erreurs.append(
                        f"{ici} : renvoie à « {cible} » à la date {date_nommee}, quand "
                        f"cette fiche se choisit à {', '.join(dates) or 'aucune date'}")
                    continue
                lues, trous = _lues(version, fiche, lue, date_nommee)
                erreurs += [f"{ici} : {trou}" for trou in trous]
                for autre in lues:
                    suivants.append((cible, autre["id"]))
                    if not porte(lue, autre, valeur):
                        erreurs.append(f"{ici} : lit « {valeur} », que {cible}.{autre['id']} "
                                       "ne porte pas")
    return erreurs + _boucles(aretes)


def _boucles(aretes: dict[Noeud, list[Noeud]]) -> list[str]:
    """Les chaînes de renvois qui reviennent à leur départ, chacune une fois."""
    erreurs, vus = [], set()
    etat: dict[Noeud, int] = {}          # 1 : en cours, 2 : fini

    def visiter(noeud: Noeud, chemin: list[Noeud]) -> None:
        etat[noeud] = 1
        for suivant in aretes.get(noeud, []):
            if etat.get(suivant) == 1:
                boucle = chemin[chemin.index(suivant):] if suivant in chemin else [suivant]
                cle = frozenset(boucle)
                if cle not in vus:
                    vus.add(cle)
                    erreurs.append("les renvois bouclent : " + " lit ".join(
                        f"{f}.{v}" for f, v in boucle + [suivant]))
            elif suivant not in etat:
                visiter(suivant, chemin + [suivant])
        etat[noeud] = 2

    for noeud in sorted(aretes):
        if noeud not in etat:
            visiter(noeud, [noeud])
    return erreurs
