"""Le partage des versions d'une fiche, à chaque date d'observation.

``docs/architecture.md``, § 4.1 et § 6.7. Tiré de l'outil que la session qui a
conçu l'architecture a laissé pour la phase 2
(``docs/decisions/0001/partage_fiche.py``), sans rien changer à ses règles :

- à chaque date d'observation, les versions connues d'une fiche forment un
  partage de ses dates qui décident : chaque situation relève d'une version et
  d'une seule, aux exceptions déclarées près (``exception_de``) ;
- une combinaison impossible du vocabulaire des dates — un enfant né après la
  date d'effet de la pension — n'a pas à relever d'une version ;
- une borne ne vaut qu'une fois connue la version qui la ferme : celle que la
  fiche déclare (``fermee_par``), sinon l'une de celles qui commencent là ;
- une version est connue à la publication du texte qui la fait naître
  (``nee_de``, sinon ses textes) ; faute de date de publication, à l'entrée en
  vigueur de ce texte ; sans texte (supposée, « sans droit »), toujours.

Chaque borne produit deux cas de bascule, la veille et le jour (§ 6.7).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from . import vocabulaire

BAS, HAUT = date(1850, 1, 1), date(2200, 1, 1)


def _date(valeur) -> date | None:
    if valeur is None:
        return None
    if isinstance(valeur, datetime):
        return valeur.date()
    return valeur if isinstance(valeur, date) else date.fromisoformat(str(valeur))


def connue_le(version: dict) -> date:
    """La date où la version est connue : la publication du texte qui la fait
    naître, à défaut son entrée en vigueur ; ``BAS`` sans texte."""
    textes = [t for t in version.get("textes") or [] if isinstance(t, dict)]
    if version.get("nee_de"):
        textes = [t for t in textes if t.get("id") == version["nee_de"]]
    dates = [_date(t.get("publie_le") or t.get("en_vigueur")) for t in textes
             if t.get("publie_le") or t.get("en_vigueur")]
    return min(dates) if dates else BAS


def _fermantes(fiche: dict, version: dict, nom: str) -> set[str]:
    """Les versions qui ferment la borne de ``version`` sur la date ``nom``."""
    declaree = (version.get("fermee_par") or {}).get(nom)
    if declaree:
        return {declaree}
    fin = _date((version.get("bornes", {}).get(nom) or [None, None])[1])
    return {autre["id"] for autre in fiche["versions"]
            if autre is not version and fin
            and _date((autre.get("bornes", {}).get(nom) or [None, None])[0]) == fin}


@dataclass
class Verdict:
    """Le partage d'une fiche vu à une date d'observation."""
    observation: date
    versions: int
    situations: int
    trous: list[dict] = field(default_factory=list)
    chevauchements: list[tuple[dict, list[str]]] = field(default_factory=list)


def _impossible(situation: dict[str, date], combinaisons: list[dict]) -> bool:
    return any(c["date"] in situation and c["apres"] in situation
               and situation[c["date"]] > situation[c["apres"]] for c in combinaisons)


def verifier(fiche: dict, observation: date, combinaisons: list[dict] | None = None) -> Verdict:
    """Les trous et les chevauchements du partage, à une date d'observation :
    chaque situation est jouée aux bornes des versions, la veille et le jour."""
    if combinaisons is None:
        combinaisons = vocabulaire.dates()["combinaisons_impossibles"]
    noms = fiche["dates_qui_decident"]
    connues = {v["id"]: v for v in fiche["versions"] if connue_le(v) <= observation}
    versions = []
    for v in connues.values():
        bornes = {}
        for nom in noms:
            debut, fin = v.get("bornes", {}).get(nom) or [None, None]
            ferment = _fermantes(fiche, v, nom)
            if fin and ferment and not ferment & set(connues):
                fin = None                      # la suivante n'est pas encore connue
            bornes[nom] = (_date(debut) or BAS, _date(fin) or HAUT)
        versions.append((v["id"], v.get("exception_de"), bornes))
    bords = {n: sorted({BAS, HAUT} | {x for _, _, b in versions for x in b[n]}) for n in noms}

    def points(nom):
        for a, z in zip(bords[nom], bords[nom][1:]):
            yield from sorted({a, z - timedelta(days=1)})

    verdict = Verdict(observation, len(connues), 0)
    for combinaison in itertools.product(*(list(points(n)) for n in noms)):
        situation = dict(zip(noms, combinaison))
        if _impossible(situation, combinaisons):
            continue
        verdict.situations += 1
        valent = [(vid, exc) for vid, exc, b in versions
                  if all(b[n][0] <= situation[n] < b[n][1] for n in noms)]
        restent = [vid for vid, _ in valent if not any(exc == vid for _, exc in valent)]
        if not restent:
            verdict.trous.append(situation)
        elif len(restent) > 1:
            verdict.chevauchements.append((situation, restent))
    return verdict


def observations(fiche: dict) -> list[date]:
    """Les dates où ce que la fiche sait change : chaque date où une version
    devient connue, puis « toutes connues » (``HAUT``)."""
    return sorted({connue_le(v) for v in fiche["versions"]} - {BAS}) + [HAUT]


def bascules(fiche: dict) -> list[tuple[str, date, date]]:
    """Chaque borne de chaque version, en deux cas : la veille et le jour."""
    jours = sorted({(nom, _date(x)) for v in fiche["versions"]
                    for nom, intervalle in (v.get("bornes") or {}).items()
                    for x in intervalle if x is not None})
    return [(nom, jour - timedelta(days=1), jour) for nom, jour in jours]


def controler(fiche: dict) -> list[str]:
    """Ce qui empêche les versions d'une fiche de former un partage : rien,
    s'il tient à chaque date d'observation. Une fiche sans version ou sans
    date qui décide n'a rien à partager : c'est un manque, que le contrat
    compte."""
    if not fiche.get("versions") or not fiche.get("dates_qui_decident"):
        return []
    nom = fiche.get("id")
    erreurs = []
    ids = {v["id"] for v in fiche["versions"]}
    for v in fiche["versions"]:
        for cible in (v.get("fermee_par") or {}).values():
            if cible not in ids:
                erreurs.append(f"{nom}.{v['id']} : fermée par « {cible} », "
                               "qui n'est pas une version de la fiche")
        if v.get("nee_de") and not any(isinstance(t, dict) and t.get("id") == v["nee_de"]
                                       for t in v.get("textes") or []):
            erreurs.append(f"{nom}.{v['id']} : née de « {v['nee_de']} », "
                           "qui n'est pas l'un de ses textes")
        if v.get("exception_de") and v["exception_de"] not in ids:
            erreurs.append(f"{nom}.{v['id']} : exception de « {v['exception_de']} », "
                           "qui n'est pas une version de la fiche")
    if erreurs:
        return erreurs
    for observation in observations(fiche):
        verdict = verifier(fiche, observation)
        quand = "toutes versions connues" if observation == HAUT else f"observée le {observation}"
        for situation in verdict.trous[:3]:
            erreurs.append(f"{nom}, {quand} : aucune version pour "
                           + ", ".join(f"{k} = {v}" for k, v in situation.items()))
        for situation, restent in verdict.chevauchements[:3]:
            erreurs.append(f"{nom}, {quand} : {' et '.join(restent)} se chevauchent pour "
                           + ", ".join(f"{k} = {v}" for k, v in situation.items()))
    return erreurs
