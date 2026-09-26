"""La chronologie datée et le réseau de personnes.

``docs/architecture.md``, § 5, et le contrat C.1
(``data/reference/contrats/chronologie.yaml``). Une personne est une
chronologie : des faits datés — sa naissance, ses périodes d'emploi et celles
où l'emploi s'interrompt, son départ —, dans un réseau de personnes que des
liens datés relient. Le réseau est aujourd'hui l'assuré et ses enfants ; le
reste attend son domaine (§ 13.5).

La chronologie est une DONNÉE, au format JSON, la même dans les deux moteurs
(§ 7.1) : des tables et des listes, jamais des objets. Son jumeau est
``moteur/js/chronologie.js``, fonction pour fonction. Elle passe par trois
temps :

1. **construire** ce que la personne déclare : :func:`du_parcours` (le
   formulaire, métier par métier), :func:`du_releve` (un relevé déposé, année
   par année) et :func:`du_resume` (une carrière que l'appelant a construite
   ligne à ligne, et dont seuls la naissance, les enfants et le départ sont
   des faits) ;
2. **compléter** par les présomptions ce qu'elle ne dit pas (§ 5.6) :
   :func:`completer`. Le fait présumé porte ``origine: presume`` et le nom de
   sa présomption ; un fait déclaré n'est jamais remplacé ;
3. **lire** : la carrière du moteur d'aujourd'hui en est la vue
   (:meth:`Carriere.depuis_chronologie`). C'est un pont : la phase 4 le
   remplacera par l'acquisition en étapes, qui lira la chronologie elle-même.

Les dates sont au jour (§ 4.6). Une date que la saisie ne connaît qu'au mois
tombe le premier du mois, et le fait le dit (``precision: mois``). Une période
vaut [début, fin), comme les bornes des versions.

Ce que les faits portent, par sorte :

* ``naissance`` — ``sexe`` et ``precision`` pour l'assuré ; rien pour un
  enfant dont la naissance est présumée ;
* ``periode_d_activite`` — ``affiliation`` ; d'un parcours, le
  ``niveau_salaire`` (en multiples du salaire moyen par tête de l'année) et le
  ``profil`` de progression, et ``cumul`` pour une activité qui s'ajoute à la
  principale ; d'un relevé, le ``revenu`` de l'année, en euros courants, et
  ses ``trimestres`` quand le relevé les porte ; dans les deux cas, la
  ``part_primes`` de la rémunération ;
* ``periode_d_interruption`` — le ``motif`` ; d'un relevé, aussi
  l'``affiliation``, le ``revenu`` de référence et les ``trimestres`` ;
* ``acte_de_la_personne`` — pour le départ : ``acte: depart``, le ``motif``,
  et l'``age`` que la personne déclare, en années décimales.

Les trimestres qu'un relevé déposé porte font foi : ce sont des résultats
observés, que la phase 4 fera entrer au relevé des droits, là où ils auraient
été calculés (§ 5.5). En attendant, la période les garde.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from .calendrier import DateMois, en_mois
from .noyau import vocabulaire

if TYPE_CHECKING:  # pragma: no cover - annotations seulement
    from .carriere import LigneRelevee, Metier

#: La version du contrat C.1 que la chronologie suit.
SCHEMA_VERSION = 1

#: La personne dont on calcule les droits, quand l'appelant n'en nomme pas
#: d'autre.
ASSURE = "assure"

#: Les sortes de faits qui sont des périodes de la carrière.
EMPLOI, INTERRUPTION = "periode_d_activite", "periode_d_interruption"

#: Le niveau d'un fait que la personne déclare, et celui d'un fait présumé.
DECLAREE, PRESUMEE = "haute", "estimee"


# -- les faits et les liens -----------------------------------------------------

def _jour(date: DateMois) -> str:
    """Le premier jour du mois, au format ISO."""
    return f"{date.annee:04d}-{date.mois:02d}-01"


def _plus_ans(jour: str, ans: int) -> str:
    """La même date, ``ans`` années plus tard ; un 29 février tombe le 28."""
    annee, mois, quantieme = int(jour[:4]) + ans, int(jour[5:7]), int(jour[8:10])
    bissextile = annee % 4 == 0 and (annee % 100 != 0 or annee % 400 == 0)
    if mois == 2 and quantieme == 29 and not bissextile:
        quantieme = 28
    return f"{annee:04d}-{mois:02d}-{quantieme:02d}"


def fait(ident: str, personne: str, sorte: str, debut: str, fin: str | None = None,
         attributs: dict | None = None, presomption: str | None = None) -> dict:
    """Un fait du contrat C.1 : déclaré, ou posé par la présomption qu'il
    nomme."""
    resultat = {
        "schema_version": SCHEMA_VERSION,
        "id": ident,
        "personne": personne,
        "sorte": sorte,
        "debut": debut,
        "fin": fin,
        "attributs": dict(attributs or {}),
        "origine": "presume" if presomption else "declare",
        "fiabilite": PRESUMEE if presomption else DECLAREE,
    }
    if presomption:
        resultat["presomption"] = presomption
    return resultat


def lien(ident: str, de: str, vers: str, sorte: str, roles: dict,
         debut: str | None = None) -> dict:
    """Un lien déclaré du contrat C.1. Une filiation commence à la naissance
    de l'enfant : tant qu'elle n'est pas connue, ``debut`` reste vide, et
    :func:`completer` le recopie du fait de naissance."""
    return {
        "schema_version": SCHEMA_VERSION,
        "id": ident,
        "de": de,
        "vers": vers,
        "sorte": sorte,
        "roles": dict(roles),
        "debut": debut,
        "fin": None,
        "origine": "declare",
    }


# -- construire : ce que la personne déclare -----------------------------------

def _personne(annee_naissance: int, mois_naissance: int, sexe: str,
              age_liquidation: float | None, nombre_enfants: int
              ) -> tuple[list[dict], list[dict], list[dict]]:
    """Ce que toute saisie déclare de l'assuré : sa naissance, son départ et
    ses enfants. Rend la naissance, le départ (vide sans âge de départ) et les
    liens de filiation, que :func:`completer` datera."""
    naissance = DateMois(annee_naissance, mois_naissance)
    faits_naissance = [fait(f"naissance_{ASSURE}", ASSURE, "naissance", _jour(naissance),
                            attributs={"sexe": sexe, "precision": "mois"})]
    depart = [] if age_liquidation is None else [
        fait(f"depart_{ASSURE}", ASSURE, "acte_de_la_personne",
             _jour(naissance.plus_mois(en_mois(age_liquidation))),
             attributs={"acte": "depart", "motif": "vieillesse", "age": age_liquidation})]
    role = "mere" if sexe == "F" else "pere"
    liens = [lien(f"filiation_enfant_{rang}", ASSURE, f"enfant_{rang}", "filiation",
                  {ASSURE: role, f"enfant_{rang}": "enfant"})
             for rang in range(1, nombre_enfants + 1)]
    return faits_naissance, depart, liens


def du_resume(annee_naissance: int, sexe: str, mois_naissance: int = 1,
              age_liquidation: float | None = None, nombre_enfants: int = 0) -> dict:
    """La chronologie d'une carrière construite ligne à ligne : la naissance,
    le départ et les enfants, sans ses périodes, que l'appelant a déjà
    traduites en années."""
    naissance, depart, liens = _personne(annee_naissance, mois_naissance, sexe,
                                         age_liquidation, nombre_enfants)
    return {"schema_version": SCHEMA_VERSION, "faits": naissance + depart, "liens": liens}


def du_parcours(annee_naissance: int, sexe: str, metiers: list["Metier"],
                age_liquidation: float, mois_naissance: int = 1,
                profil_carriere: str = "auto", interruptions: dict[int, str] | None = None,
                nombre_enfants: int = 0, part_primes: float = 0.0) -> dict:
    """La chronologie d'un parcours : un fait par métier, daté au mois, et un
    par année d'interruption.

    Un métier principal court jusqu'au début du suivant, le dernier jusqu'au
    départ ; une activité cumulée, de son âge de début à son âge de fin, ou
    au départ. Les contrôles sont ceux du parcours : les métiers se suivent,
    le premier n'est pas cumulé, rien ne dépasse le départ.
    """
    if not metiers:
        raise ValueError("une carrière compte au moins un métier")
    if metiers[0].cumul:
        raise ValueError(
            "une activité cumulée s'ajoute à une activité principale : la "
            "carrière ne peut pas commencer par elle"
        )
    cumuls = [metier for metier in metiers if metier.cumul]
    principaux = [metier for metier in metiers if not metier.cumul]

    date_naissance = DateMois(annee_naissance, mois_naissance)
    bornes = [date_naissance.plus_mois(en_mois(metier.age_debut)) for metier in principaux]
    debut = bornes[0]
    # La pension prend effet ce mois-là : il n'est plus travaillé, la borne
    # est donc EXCLUE.
    fin = date_naissance.plus_mois(en_mois(age_liquidation))
    if fin.rang <= debut.rang:
        raise ValueError("âge de liquidation antérieur à l'âge de début d'activité")
    # Chaque métier s'arrête où commence le suivant : les périodes se touchent
    # bout à bout et couvrent la carrière exactement une fois.
    for precedente, suivante in zip(bornes, bornes[1:]):
        if suivante.rang <= precedente.rang:
            raise ValueError(
                "les métiers doivent se suivre : chacun commence après le "
                "précédent"
            )
    if bornes[-1].rang >= fin.rang:
        raise ValueError("le dernier métier commence après la liquidation")

    periodes = []
    for rang, (metier, ouverture, cloture) in enumerate(
            zip(principaux, bornes, bornes[1:] + [fin]), 1):
        periodes.append(fait(f"emploi_{rang}", ASSURE, EMPLOI, _jour(ouverture), _jour(cloture), {
            "affiliation": metier.affiliation, "niveau_salaire": metier.niveau_salaire,
            "profil": profil_carriere, "part_primes": part_primes}))
    for rang, metier in enumerate(cumuls, 1):
        ouverture = date_naissance.plus_mois(en_mois(metier.age_debut))
        cloture = (fin if metier.age_fin is None
                   else date_naissance.plus_mois(en_mois(metier.age_fin)))
        if ouverture.rang < debut.rang:
            raise ValueError(
                "une activité cumulée commence après le début de la "
                "carrière : elle s'ajoute à une activité déjà là"
            )
        if cloture.rang > fin.rang:
            raise ValueError(
                "une activité cumulée s'arrête au plus tard à la liquidation"
            )
        if cloture.rang <= ouverture.rang:
            raise ValueError(
                "une activité cumulée doit s'arrêter après avoir commencé"
            )
        periodes.append(fait(f"cumul_{rang}", ASSURE, EMPLOI, _jour(ouverture), _jour(cloture), {
            "affiliation": metier.affiliation, "niveau_salaire": metier.niveau_salaire,
            "profil": profil_carriere, "part_primes": part_primes, "cumul": True}))
    for annee in sorted(interruptions or {}):
        periodes.append(fait(f"interruption_{annee}", ASSURE, INTERRUPTION,
                             f"{annee:04d}-01-01", f"{annee + 1:04d}-01-01",
                             {"motif": interruptions[annee]}))

    naissance, depart, liens = _personne(annee_naissance, mois_naissance, sexe,
                                         age_liquidation, nombre_enfants)
    return {"schema_version": SCHEMA_VERSION, "faits": naissance + periodes + depart,
            "liens": liens}


def du_releve(annee_naissance: int, sexe: str, releve: list["LigneRelevee"],
              age_liquidation: float, mois_naissance: int = 1,
              nombre_enfants: int = 0, part_primes: float = 0.0) -> dict:
    """La chronologie d'un relevé : un fait par ligne, une année civile
    chacun, dans l'ordre du relevé — la première ligne d'une année est
    l'activité principale."""
    if not releve:
        raise ValueError("un relevé compte au moins une ligne")
    periodes = []
    for rang, ligne in enumerate(releve, 1):
        attributs = {"affiliation": ligne.affiliation, "revenu": ligne.revenu,
                     "trimestres": ligne.trimestres, "part_primes": part_primes}
        emploi = ligne.type_periode == "emploi"
        if not emploi:
            attributs["motif"] = ligne.type_periode
        periodes.append(fait(f"releve_{rang}", ASSURE, EMPLOI if emploi else INTERRUPTION,
                             f"{ligne.annee:04d}-01-01", f"{ligne.annee + 1:04d}-01-01",
                             attributs))
    naissance, depart, liens = _personne(annee_naissance, mois_naissance, sexe,
                                         age_liquidation, nombre_enfants)
    return {"schema_version": SCHEMA_VERSION, "faits": naissance + periodes + depart,
            "liens": liens}


# -- compléter : les présomptions ------------------------------------------------

@lru_cache(maxsize=None)
def _vocabulaire() -> dict[str, dict]:
    """Les présomptions du vocabulaire, lues une fois : elles ne changent pas
    en cours de calcul, et on ne les modifie jamais."""
    return vocabulaire.presomptions()


def valeur(presomption: str, presomptions: dict | None = None):
    """La valeur d'une présomption (§ 5.6) : dans la table donnée — le
    paquet de données, côté site —, ou au vocabulaire."""
    table = _vocabulaire() if presomptions is None else presomptions
    if presomption not in table:
        raise KeyError(f"présomption inconnue : {presomption}")
    return table[presomption]["valeur"]


def completer(chronologie: dict, presomptions: dict | None = None) -> dict:
    """La chronologie complétée par les présomptions : une copie, où chaque
    fait qui manque et qu'une présomption sait poser est posé, en son nom.
    ``presomptions`` est la table où lire leurs valeurs, le vocabulaire à
    défaut.

    Aujourd'hui, une seule présomption pose un fait :
    ``naissance_des_enfants`` date la naissance de chaque enfant dont la date
    n'est pas déclarée aux trente ans de son parent. La filiation commence à
    cette naissance. Les autres présomptions du vocabulaire s'appliquent là
    où leur fait sera lu, et le disent (``appliquee_par``).

    Compléter deux fois ne change rien.
    """
    faits = [dict(f) for f in chronologie.get("faits") or []]
    liens = [dict(l) for l in chronologie.get("liens") or []]
    naissances: dict[str, dict] = {}
    for f in faits:
        if f["sorte"] == "naissance":
            naissances.setdefault(f["personne"], f)
    for filiation in liens:
        if filiation["sorte"] != "filiation":
            continue
        enfant = filiation["vers"]
        if enfant not in naissances:
            parent = naissances.get(filiation["de"])
            if parent is None:
                continue
            presume = fait(f"naissance_{enfant}", enfant, "naissance",
                           _plus_ans(parent["debut"],
                                     valeur("naissance_des_enfants", presomptions)),
                           presomption="naissance_des_enfants")
            faits.append(presume)
            naissances[enfant] = presume
        if filiation.get("debut") is None:
            filiation["debut"] = naissances[enfant]["debut"]
    return {"schema_version": chronologie.get("schema_version", SCHEMA_VERSION),
            "faits": faits, "liens": liens}


def presomptions_employees(chronologie: dict) -> list[str]:
    """Les présomptions qui ont posé un fait ou un lien de la chronologie."""
    noms = {element["presomption"]
            for element in (chronologie.get("faits") or []) + (chronologie.get("liens") or [])
            if element.get("origine") == "presume"}
    return sorted(noms)


# -- lire ------------------------------------------------------------------------

def faits_de(chronologie: dict, personne: str, sorte: str | None = None) -> list[dict]:
    """Les faits d'une personne, d'une sorte s'il le faut, dans leur ordre."""
    return [f for f in chronologie.get("faits") or []
            if f["personne"] == personne and (sorte is None or f["sorte"] == sorte)]


def naissance(chronologie: dict, personne: str) -> dict | None:
    """Le fait de naissance d'une personne, s'il est connu."""
    trouves = faits_de(chronologie, personne, "naissance")
    return trouves[0] if trouves else None


def depart(chronologie: dict, personne: str) -> dict | None:
    """L'acte de départ d'une personne, s'il est déclaré."""
    for acte in faits_de(chronologie, personne, "acte_de_la_personne"):
        if acte["attributs"].get("acte") == "depart":
            return acte
    return None


def periodes(chronologie: dict, personne: str) -> list[dict]:
    """Les périodes d'emploi et d'interruption d'une personne, dans leur
    ordre."""
    return [f for f in faits_de(chronologie, personne) if f["sorte"] in (EMPLOI, INTERRUPTION)]


def enfants(chronologie: dict, personne: str) -> list[str]:
    """Les enfants d'une personne, dans l'ordre de leurs filiations."""
    return [l["vers"] for l in chronologie.get("liens") or []
            if l["sorte"] == "filiation" and l["de"] == personne]


def annee_de(jour: str) -> int:
    return int(jour[:4])


def mois_de(jour: str) -> DateMois:
    """Le mois d'une date de la chronologie, pour le moteur qui compte au
    mois."""
    return DateMois(int(jour[:4]), int(jour[5:7]))


# -- contrôler -------------------------------------------------------------------

def controler(chronologie: dict) -> list[str]:
    """Ce qui ne va pas dans une chronologie complétée : rien, si elle tient.

    Le contrat C.1, erreurs et manques ; un identifiant par fait et par lien ;
    une naissance pour chaque personne d'un lien ; une filiation qui commence
    à la naissance de l'enfant ; une période qui finit après avoir commencé.
    """
    from .noyau import contrats

    erreurs = [str(c) for c in contrats.Validateur("chronologie").valider(chronologie, "chronologie")]
    faits = chronologie.get("faits") or []
    liens = chronologie.get("liens") or []
    for genre, elements in (("fait", faits), ("lien", liens)):
        vus: set[str] = set()
        for element in elements:
            if element.get("id") in vus:
                erreurs.append(f"deux {genre}s portent l'identifiant {element.get('id')}")
            vus.add(element.get("id"))
    naissances = {f["personne"]: f for f in faits if f.get("sorte") == "naissance"}
    for l in liens:
        for personne in (l.get("de"), l.get("vers")):
            if personne not in naissances:
                erreurs.append(f"{l.get('id')} : {personne} n'a pas de naissance")
        if (l.get("sorte") == "filiation" and l.get("vers") in naissances
                and l.get("debut") != naissances[l["vers"]]["debut"]):
            erreurs.append(f"{l.get('id')} : la filiation commence à la naissance de l'enfant")
    for f in faits:
        if f.get("fin") is not None and not str(f["fin"]) > str(f.get("debut")):
            erreurs.append(f"{f.get('id')} : une période finit après avoir commencé")
    return erreurs
