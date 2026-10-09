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

La naissance de l'assuré fait exception : son jour décide du mois d'où ses
âges se comptent (:func:`~retraite_notionnelle.calendrier.origine_des_ages`),
et donc des dates de sa carrière, que la saisie donne en âges. Quand la saisie
ne le dit pas, la présomption ``jour_de_naissance`` le pose dès la
construction, en son nom, avant que ces dates ne se calculent.

Ce que les faits portent, par sorte :

* ``naissance`` — ``sexe`` et ``precision`` pour l'assuré, le jour s'il est
  déclaré, le mois sinon ; ``precision`` pour un enfant dont la naissance est
  déclarée — l'année, le mois ou le jour, la date tombant au premier jour de
  ce qui n'est pas dit ; rien pour un enfant dont la naissance est présumée ;
* ``periode_d_activite`` — ``affiliation`` ; d'un parcours, le
  ``niveau_salaire`` (en multiples du salaire moyen par tête de l'année) et le
  ``profil`` de progression, et ``cumul`` pour une activité qui s'ajoute à la
  principale ; d'un relevé, le ``revenu`` de l'année, en euros courants, et
  ses ``trimestres`` quand le relevé les porte ; dans les deux cas, la
  ``part_primes`` de la rémunération ;
* ``periode_d_interruption`` — le ``motif`` ; d'un relevé, aussi
  l'``affiliation``, le ``revenu`` de référence et les ``trimestres`` ;
* ``acte_de_la_personne`` — pour le départ : ``acte: depart``, le ``motif``,
  et l'``age`` que la personne déclare, en années décimales ; pour une
  retraite progressive : ``acte: retraite_progressive``, son ``age`` et la
  ``quotite`` du temps partiel qu'elle garde, jusqu'au départ ; pour la
  pension d'un régime qu'elle demande à une date dite :
  ``acte: demande_de_pension``, le ``regime`` et l'``age``, un acte par régime ;
* ``periode_a_l_etranger`` — l'``activite``, salariée ou non ; son État est
  son ``territoire``, le code du tableau des accords, ou ``autre`` ;
* ``acte_de_la_caisse`` — pour une pension étrangère : ``acte: liquidation``
  et l'``age`` où elle commence ; son ``montant`` mensuel, en euros de cette
  date ; l'État qui la sert pour ``territoire`` ;
* ``residence`` — l'État où la personne réside après son départ, pour
  ``territoire``, quand ce n'est pas la France.

L'activité exercée APRÈS le départ, le cumul emploi-retraite, est une
``periode_d_activite`` comme les autres, qui porte ``apres_depart`` et
l'``employeur`` — ``dernier`` ou ``autre`` — ; :func:`periodes` l'écarte des
périodes de la carrière, et :func:`emploi_retraite` la rend.

Les trimestres qu'un relevé déposé porte font foi : ce sont des résultats
observés, que la phase 4 fera entrer au relevé des droits, là où ils auraient
été calculés (§ 5.5). En attendant, la période les garde.
"""

from __future__ import annotations

import datetime
from functools import lru_cache
from typing import TYPE_CHECKING

from .calendrier import MOIS_PAR_AN, DateMois, en_mois, origine_des_ages
from .noyau import vocabulaire

if TYPE_CHECKING:  # pragma: no cover - annotations seulement
    from .carriere import LigneRelevee, Metier

#: La version du contrat C.1 que la chronologie suit.
SCHEMA_VERSION = 1

#: La personne dont on calcule les droits, quand l'appelant n'en nomme pas
#: d'autre.
ASSURE = "assure"
#: Le conjoint de l'assuré, que le mariage lui relie (§ 5.1).
CONJOINT = "conjoint"
#: Ses précédents conjoints, divorcés : « ex_conjoint_1 », « ex_conjoint_2 ».
EX_CONJOINT = "ex_conjoint"
#: Les formes d'une union (vocabulaire, ``formes_d_union``) : celle où le
#: conjoint survivant vit après le décès en est une.
FORMES_D_UNION = ("mariage", "pacs", "concubinage")

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


def annees_revolues(debut: str, fin: str) -> int:
    """Les années révolues de ``debut`` à ``fin`` (AAAA-MM-JJ) : les
    anniversaires de l'un atteints au plus tard à l'autre, zéro si ``fin`` le
    précède. L'âge d'un enfant à la date d'effet d'une pension, ou les années
    d'éducation accomplies avant elle."""
    ans = int(fin[:4]) - int(debut[:4])
    if ans > 0 and _plus_ans(debut, ans) > fin:
        ans -= 1
    return max(ans, 0)


def fait(ident: str, personne: str, sorte: str, debut: str, fin: str | None = None,
         attributs: dict | None = None, presomption: str | None = None,
         montant: dict | None = None, territoire: str | None = None) -> dict:
    """Un fait du contrat C.1 : déclaré, ou posé par la présomption qu'il
    nomme. ``montant`` — un montant et sa monnaie — ne s'écrit que s'il est
    donné : les ressources d'une personne en portent un. ``territoire`` de
    même : un fait qui ne le dit pas a lieu en métropole, le défaut du
    contrat, et seuls ceux d'une carrière hors de France le disent."""
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
    if montant is not None:
        resultat["montant"] = dict(montant)
    if territoire is not None:
        resultat["territoire"] = territoire
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

def naissance_declaree(valeur) -> tuple[str, str]:
    """La naissance déclarée d'un enfant : sa date (AAAA-MM-JJ) et sa
    précision. On déclare une année (``1995``), un mois (``1995-06``) ou un
    jour (``1995-06-14``) ; ce qui n'est pas dit tombe au premier du mois, ou
    au 1er janvier, comme pour le mois de naissance de l'assuré."""
    texte = str(valeur).strip()
    morceaux = texte.split("-")
    try:
        nombres = [int(m) for m in morceaux]
    except ValueError:
        nombres = []
    if not 1 <= len(nombres) <= 3 or any(len(m) != n for m, n in zip(morceaux, (4, 2, 2))):
        raise ValueError(f"naissance d'un enfant attendue en AAAA, AAAA-MM ou "
                         f"AAAA-MM-JJ, reçu {valeur!r}")
    annee, mois, jour = (nombres + [1, 1])[:3]
    try:
        date = _date(annee, mois, jour)
    except ValueError:
        raise ValueError(f"naissance d'un enfant impossible : {valeur!r}") from None
    return date, ("annee", "mois", "jour")[len(nombres) - 1]


def date_declaree(valeur, quoi: str) -> tuple[str, str]:
    """Une date déclarée — le décès de l'assuré, la naissance de son
    conjoint, leur mariage — et sa précision, comme :func:`naissance_declaree`
    lit celle d'un enfant : une année, un mois ou un jour ; ce qui n'est pas
    dit tombe au premier du mois, ou au 1er janvier. ``quoi`` nomme la date
    dans le message d'erreur."""
    texte = str(valeur).strip()
    morceaux = texte.split("-")
    try:
        nombres = [int(m) for m in morceaux]
    except ValueError:
        nombres = []
    if not 1 <= len(nombres) <= 3 or any(len(m) != n for m, n in zip(morceaux, (4, 2, 2))):
        raise ValueError(f"{quoi} attendu(e) en AAAA, AAAA-MM ou AAAA-MM-JJ, reçu {valeur!r}")
    annee, mois, jour = (nombres + [1, 1])[:3]
    try:
        date = _date(annee, mois, jour)
    except ValueError:
        raise ValueError(f"{quoi} impossible : {valeur!r}") from None
    return date, ("annee", "mois", "jour")[len(nombres) - 1]


def _date(annee: int, mois: int, jour: int) -> str:
    """Une date AAAA-MM-JJ, contrôlée."""
    return datetime.date(annee, mois, jour).isoformat()


def jour_de(date: str) -> int:
    """Le quantième d'une date de la chronologie : 15 pour « 1962-03-15 »."""
    return int(date[8:10])


def naissance_de_l_assure(annee_naissance: int, mois_naissance: int, sexe: str,
                          jour_naissance: int | None = None,
                          presomptions: dict | None = None) -> dict:
    """Le fait de naissance de l'assuré, au jour qu'il déclare, ou à celui
    que la présomption ``jour_de_naissance`` pose quand il ne le dit pas.

    Le jour se pose ici, et non dans :func:`completer`, parce que les dates
    de la carrière se comptent depuis lui : la saisie les donne en âges, et
    un âge ne devient une date que rapporté au mois d'où les âges se
    comptent (:func:`~retraite_notionnelle.calendrier.origine_des_ages`).
    Le fait présumé garde ``precision: mois`` : l'année et le mois sont
    déclarés, le jour seul est présumé. ``presomptions`` est la table où lire
    la valeur, le vocabulaire à défaut."""
    if jour_naissance is None:
        return fait(f"naissance_{ASSURE}", ASSURE, "naissance",
                    _date(annee_naissance, mois_naissance,
                          valeur("jour_de_naissance", presomptions)),
                    attributs={"sexe": sexe, "precision": "mois"},
                    presomption="jour_de_naissance")
    try:
        date = _date(annee_naissance, mois_naissance, jour_naissance)
    except ValueError:
        raise ValueError(f"naissance impossible : le {jour_naissance} du mois "
                         f"{mois_naissance} de {annee_naissance}") from None
    return fait(f"naissance_{ASSURE}", ASSURE, "naissance", date,
                attributs={"sexe": sexe, "precision": "jour"})


def origine_de(naissance: dict) -> DateMois:
    """Le mois d'où comptent les âges de qui est né à ce fait de naissance."""
    return origine_des_ages(mois_de(naissance["debut"]), jour_de(naissance["debut"]))


def _personne(annee_naissance: int, mois_naissance: int, sexe: str,
              age_liquidation: float | None, nombre_enfants: int,
              naissances_enfants: list | tuple = (),
              jour_naissance: int | None = None, presomptions: dict | None = None,
              conjoint: dict | None = None, deces: str | None = None,
              retraite_progressive: dict | None = None,
              emploi_retraite: dict | None = None,
              demandes_de_pension: dict[str, float] | None = None,
              invalidite: dict | None = None,
              etranger: dict | None = None,
              ) -> tuple[list[dict], list[dict], list[dict]]:
    """Ce que toute saisie déclare de l'assuré : sa naissance, son départ,
    ses enfants, et, s'il les dit, son conjoint et son décès. Rend les
    naissances — celle de l'assuré, puis celles des enfants qu'elle déclare,
    puis celle du conjoint —, les événements de sa vie — le départ (vide sans
    âge de départ), le décès —, et les liens : de filiation, et le mariage.

    ``naissances_enfants`` déclare la naissance des premiers enfants, dans
    l'ordre (:func:`naissance_declaree`) ; :func:`completer` présume celles
    des autres, et date leur filiation. Le départ tombe à l'âge déclaré,
    compté depuis le mois d'où les âges se comptent.

    ``conjoint`` déclare le conjoint (docs/architecture.md, § 5.1) : sa
    ``naissance`` et son ``sexe``, la date du ``mariage`` — que
    :func:`completer` présume sinon (``mariage_des_conjoints``) —, ses
    ``ressources`` annuelles, et ce qui en vient de son activité
    (``revenus_d_activite``), la ``nouvelle_union`` où il vit après le décès
    — mariage, pacs ou concubinage — et les ressources que son nouveau
    conjoint y apporte (``ressources_du_nouveau_conjoint``), depuis le mois
    qu'il dit (``nouvelle_union_depuis``) ou le décès, son ``invalidite``,
    une décision médicale datée, et sa ``retraite``, l'acte de son propre
    départ, daté, s'il les dit ; et les précédents conjoints de
    l'assuré (``ex_conjoints``) : la naissance de chacun, son mariage, que le
    divorce clôt, et son remariage, s'il le dit. ``deces`` date le décès de
    l'assuré, qui ouvre la réversion de son conjoint : il clôt le mariage.
    ``retraite_progressive`` déclare la demande d'une retraite progressive :
    son ``age``, compté comme celui du départ, qu'elle précède, et la
    ``quotite`` du temps partiel gardé jusqu'au départ, entre zéro et un.
    ``emploi_retraite`` déclare l'activité exercée après le départ : son
    ``age`` et sa ``fin``, comptés comme le départ, qu'elle ne précède pas,
    son ``affiliation``, son ``niveau_salaire`` et l'``employeur``.
    ``demandes_de_pension`` déclare, régime par régime, l'âge auquel la
    personne demande sa pension, compté comme le départ : la présomption
    ``depart_de_chaque_regime`` la date sinon (:mod:`.droit.departs`).
    ``invalidite`` déclare l'invalidité et l'inaptitude : la ``pension``
    d'invalidité, l'âge où elle a commencé, compté comme un début d'activité,
    avant le départ ; l'``inaptitude``, reconnue à la demande de la pension,
    donc au départ ; la ``radiation`` pour invalidité d'un fonctionnaire, son
    ``age``, compté de même, au plus tard au départ, son ``imputable`` au
    service et son ``taux`` d'invalidité en pour cent ; le ``handicap``,
    l'âge depuis lequel l'incapacité permanente atteint 50 %, compté de même,
    au plus tard au départ ; le ``deporte`` titulaire de la carte, les
    ``mois_de_guerre`` de captivité et de services de guerre, le
    ``travail_manuel`` des quinze années d'avant le départ, constatés au
    départ. Trois décisions médicales et une radiation, que
    :func:`decision_medicale` et :func:`radiation_pour_invalidite` relisent,
    deux titres et une exposition, que :func:`titre` et :func:`exposition`
    relisent.
    ``etranger`` déclare la carrière hors de France : ses ``periodes`` —
    l'État (``pays``), le ``debut`` et la ``fin``, comptés comme un début
    d'activité, au plus tard au départ, et l'``activite`` —, ses ``pensions``
    étrangères — l'État, l'``age`` où elle commence, compté de même, et son
    montant ``mensuel`` en euros de cette date —, l'État de ``residence``
    après le départ, et les ``mois_en_france`` de chaque année. Des périodes à
    l'étranger, des actes de la caisse de chaque État, une résidence, que
    :func:`periodes_a_l_etranger`, :func:`pensions_etrangeres` et
    :func:`residence` relisent."""
    assure = naissance_de_l_assure(annee_naissance, mois_naissance, sexe,
                                   jour_naissance, presomptions)
    faits_naissance = [assure]
    if len(naissances_enfants) > nombre_enfants:
        raise ValueError(
            f"{len(naissances_enfants)} naissances d'enfants déclarées pour "
            f"{nombre_enfants} enfant{'s' if nombre_enfants > 1 else ''}")
    declarees = [naissance_declaree(valeur) for valeur in naissances_enfants]
    for jour, _ in declarees:
        if jour <= assure["debut"]:
            raise ValueError(f"un enfant né le {jour}, avant son parent")
    faits_naissance += [
        fait(f"naissance_enfant_{rang}", f"enfant_{rang}", "naissance", jour,
             attributs={"precision": precision})
        for rang, (jour, precision) in enumerate(declarees, 1)]
    depart = [] if age_liquidation is None else [
        fait(f"depart_{ASSURE}", ASSURE, "acte_de_la_personne",
             _jour(origine_de(assure).plus_mois(en_mois(age_liquidation))),
             attributs={"acte": "depart", "motif": "vieillesse", "age": age_liquidation})]
    if retraite_progressive is not None:
        age, quotite = retraite_progressive["age"], retraite_progressive["quotite"]
        if age_liquidation is None or en_mois(age) >= en_mois(age_liquidation):
            raise ValueError("une retraite progressive précède le départ")
        if not 0.0 < quotite < 1.0:
            raise ValueError(f"la quotité d'une retraite progressive : entre 0 et 1, "
                             f"reçu {quotite}")
        depart.insert(0, fait(
            f"retraite_progressive_{ASSURE}", ASSURE, "acte_de_la_personne",
            _jour(origine_de(assure).plus_mois(en_mois(age))),
            attributs={"acte": "retraite_progressive", "age": age, "quotite": quotite}))
    if demandes_de_pension:
        if age_liquidation is None:
            raise ValueError("une pension demandée à une date suppose un départ")
        for code in sorted(demandes_de_pension):
            age = demandes_de_pension[code]
            if age < 0:
                raise ValueError(f"la pension de {code} demandée avant la naissance")
            depart.append(fait(
                f"demande_de_pension_{code}_{ASSURE}", ASSURE, "acte_de_la_personne",
                _jour(origine_de(assure).plus_mois(en_mois(age))),
                attributs={"acte": "demande_de_pension", "regime": code, "age": age}))
    if emploi_retraite is not None:
        age, fin = emploi_retraite["age"], emploi_retraite["fin"]
        if age_liquidation is None or en_mois(age) < en_mois(age_liquidation):
            raise ValueError("une activité après le départ ne précède pas le départ")
        if en_mois(fin) <= en_mois(age):
            raise ValueError("une activité après le départ finit après avoir commencé")
        if emploi_retraite["employeur"] not in ("dernier", "autre"):
            raise ValueError(f"l'employeur d'une activité après le départ : le dernier ou "
                             f"un autre, reçu {emploi_retraite['employeur']!r}")
        depart.append(fait(
            f"emploi_retraite_{ASSURE}", ASSURE, EMPLOI,
            _jour(origine_de(assure).plus_mois(en_mois(age))),
            _jour(origine_de(assure).plus_mois(en_mois(fin))),
            {"affiliation": emploi_retraite["affiliation"],
             "niveau_salaire": emploi_retraite["niveau_salaire"], "profil": "plat",
             "part_primes": 0.0, "apres_depart": True,
             "employeur": emploi_retraite["employeur"]}))
    if invalidite is not None:
        depart += _invalidite(assure, age_liquidation, invalidite)
    if etranger is not None:
        depart += _etranger(assure, age_liquidation, etranger)
    role = "mere" if sexe == "F" else "pere"
    liens = [lien(f"filiation_enfant_{rang}", ASSURE, f"enfant_{rang}", "filiation",
                  {ASSURE: role, f"enfant_{rang}": "enfant"},
                  debut=declarees[rang - 1][0] if rang <= len(declarees) else None)
             for rang in range(1, nombre_enfants + 1)]
    jour_deces = None
    if deces is not None:
        jour_deces, precision = date_declaree(deces, "le décès de l'assuré")
        if jour_deces <= assure["debut"]:
            raise ValueError(f"un décès le {jour_deces}, avant la naissance")
        depart.append(fait(f"deces_{ASSURE}", ASSURE, "deces", jour_deces,
                           attributs={"precision": precision}))
    if conjoint is not None:
        epoux = _naissance_du_conjoint(conjoint)
        faits_naissance.append(epoux)
        union = lien(f"union_{CONJOINT}", ASSURE, CONJOINT, "union",
                     {ASSURE: "conjoint", CONJOINT: "conjoint"})
        union["forme"] = "mariage"
        if conjoint.get("mariage") is not None:
            union["debut"] = date_declaree(conjoint["mariage"], "le mariage")[0]
            if union["debut"] <= max(assure["debut"], epoux["debut"]):
                raise ValueError(f"un mariage le {union['debut']}, avant la naissance d'un époux")
        if jour_deces is not None:
            if union["debut"] is not None and union["debut"] >= jour_deces:
                raise ValueError(f"un mariage le {union['debut']}, après le décès")
            union["fin"] = {"date": jour_deces, "cause": "deces"}
        liens.append(union)
        if conjoint.get("ressources") is not None:
            faits_naissance.append(fait(
                f"ressources_{CONJOINT}", CONJOINT, "ressources",
                jour_deces or epoux["debut"],
                attributs={"periode": "annuelle"},
                montant={"annuel": float(conjoint["ressources"]), "monnaie": "EUR"}))
        if conjoint.get("revenus_d_activite") is not None:
            # La part de ces ressources que lui rapporte son activité, que le
            # plafond de la réversion abat après cinquante-cinq ans (R. 353-1).
            faits_naissance.append(fait(
                f"revenus_d_activite_{CONJOINT}", CONJOINT, "ressources",
                jour_deces or epoux["debut"],
                attributs={"periode": "annuelle", "nature": "revenus_d_activite"},
                montant={"annuel": float(conjoint["revenus_d_activite"]), "monnaie": "EUR"}))
        if conjoint.get("nouvelle_union") is not None:
            # Le ménage où il vit après le décès : la forme de sa nouvelle union,
            # et ce que son nouveau conjoint y apporte, s'il le dit — « ses
            # ressources personnelles ou celles du ménage » (L. 353-1).
            forme = conjoint["nouvelle_union"]
            if forme not in FORMES_D_UNION:
                raise ValueError(f"une union « {forme} » : mariage, pacs ou concubinage")
            apport = conjoint.get("ressources_du_nouveau_conjoint")
            debut = jour_deces or epoux["debut"]
            if conjoint.get("nouvelle_union_depuis") is not None:
                # Le mois où elle commence, s'il le dit : la réversion d'un
                # régime qui la perd au remariage s'arrête là.
                debut = date_declaree(conjoint["nouvelle_union_depuis"],
                                      "le début de sa nouvelle union")[0]
                if jour_deces is not None and debut <= jour_deces:
                    raise ValueError(f"une nouvelle union le {debut}, avant le décès")
            faits_naissance.append(fait(
                f"menage_{CONJOINT}", CONJOINT, "ressources", debut,
                attributs={"periode": "annuelle", "nature": "menage", "forme": forme},
                montant=None if apport is None else {"annuel": float(apport), "monnaie": "EUR"}))
        if conjoint.get("invalidite") is not None:
            jour, precision = date_declaree(conjoint["invalidite"], "l'invalidité du conjoint")
            if jour <= epoux["debut"]:
                raise ValueError(f"une invalidité du conjoint le {jour}, avant sa naissance")
            faits_naissance.append(fait(
                f"invalidite_{CONJOINT}", CONJOINT, "decision_medicale", jour,
                attributs={"decision": "invalidite", "precision": precision}))
        if conjoint.get("retraite") is not None:
            # Le jour où sa propre retraite prend effet : ses retraites
            # personnelles ne commencent qu'alors, et la limite de cumul de sa
            # réversion d'avant juillet 2004 s'applique ce jour-là.
            jour, precision = date_declaree(conjoint["retraite"], "la retraite du conjoint")
            if jour <= epoux["debut"]:
                raise ValueError(f"une retraite du conjoint le {jour}, avant sa naissance")
            faits_naissance.append(fait(
                f"depart_{CONJOINT}", CONJOINT, "acte_de_la_personne", jour,
                attributs={"acte": "depart", "precision": precision}))
        for rang, ex in enumerate(conjoint.get("ex_conjoints") or (), 1):
            faits, mariage = _ex_conjoint(assure, rang, ex)
            faits_naissance.extend(faits)
            liens.append(mariage)
    return faits_naissance, depart, liens


def _ex_conjoint(assure: dict, rang: int, ex: dict) -> tuple[list[dict], dict]:
    """Un précédent conjoint de l'assuré : sa naissance, le mariage qui les a
    unis, que le divorce clôt, et, s'il le dit, son remariage — le ménage où il
    vit depuis, comme celui du conjoint survivant."""
    personne = f"{EX_CONJOINT}_{rang}"
    jour, precision = date_declaree(ex["naissance"], "la naissance d'un précédent conjoint")
    faits = [fait(f"naissance_{personne}", personne, "naissance", jour,
                  attributs={"precision": precision})]
    mariage = lien(f"union_{personne}", ASSURE, personne, "union",
                   {ASSURE: "conjoint", personne: "conjoint"},
                   debut=date_declaree(ex["mariage"], "le mariage")[0])
    mariage["forme"] = "mariage"
    if mariage["debut"] <= max(assure["debut"], jour):
        raise ValueError(f"un mariage le {mariage['debut']}, avant la naissance d'un époux")
    divorce = date_declaree(ex["divorce"], "le divorce")[0]
    if divorce <= mariage["debut"]:
        raise ValueError(f"un divorce le {divorce}, avant le mariage")
    mariage["fin"] = {"date": divorce, "cause": "divorce"}
    if ex.get("remariage") is not None:
        remariage = date_declaree(ex["remariage"], "le remariage")[0]
        if remariage <= divorce:
            raise ValueError(f"un remariage le {remariage}, avant le divorce")
        faits.append(fait(f"menage_{personne}", personne, "ressources", remariage,
                          attributs={"periode": "annuelle", "nature": "menage",
                                     "forme": "mariage"}))
    return faits, mariage


def _invalidite(assure: dict, age_liquidation: float | None, invalidite: dict) -> list[dict]:
    """Les faits de l'invalidité et de l'inaptitude que la saisie déclare (voir
    :func:`_personne`) : la pension d'invalidité, l'inaptitude et
    l'incapacité permanente, trois décisions médicales, la radiation pour
    invalidité d'un fonctionnaire ; et les autres titres au taux plein de
    L. 351-8, deux titres et une exposition."""
    if age_liquidation is None:
        raise ValueError("l'invalidité ou l'inaptitude déclarée suppose un départ")
    naissance = mois_de(assure["debut"])
    depart = origine_de(assure).plus_mois(en_mois(age_liquidation))
    faits = []
    if invalidite.get("pension") is not None:
        age = invalidite["pension"]
        debut = naissance.plus_mois(en_mois(age))
        if debut.rang <= naissance.rang or debut.rang >= depart.rang:
            raise ValueError("une pension d'invalidité commence après la naissance et "
                             "avant le départ")
        faits.append(fait(f"pension_d_invalidite_{ASSURE}", ASSURE, "decision_medicale",
                          _jour(debut),
                          attributs={"decision": "pension_d_invalidite", "age": age}))
    if invalidite.get("inaptitude"):
        faits.append(fait(f"inaptitude_{ASSURE}", ASSURE, "decision_medicale", _jour(depart),
                          attributs={"decision": "inaptitude"}))
    radiation = invalidite.get("radiation")
    if radiation is not None:
        age, taux = radiation["age"], radiation.get("taux")
        debut = naissance.plus_mois(en_mois(age))
        if debut.rang <= naissance.rang or debut.rang > depart.rang:
            raise ValueError("une radiation pour invalidité tombe après la naissance et au "
                             "plus tard au départ")
        if taux is not None and not 0 < taux <= 100:
            raise ValueError(f"le taux d'invalidité : entre 0 et 100 %, reçu {taux}")
        faits.append(fait(f"radiation_pour_invalidite_{ASSURE}", ASSURE, "radiation",
                          _jour(debut),
                          attributs={"motif": "invalidite", "age": age,
                                     "imputable": bool(radiation.get("imputable")),
                                     "taux": taux}))
    if invalidite.get("handicap") is not None:
        # L'incapacité permanente d'au moins 50 % (fiche
        # ``retraite_anticipee_handicap``) : depuis le mois que la saisie dit,
        # qui peut précéder la carrière — un handicap de naissance —, jamais
        # le départ.
        age = invalidite["handicap"]
        debut = naissance.plus_mois(en_mois(age))
        if debut.rang <= naissance.rang or debut.rang > depart.rang:
            raise ValueError("une incapacité permanente est reconnue après la naissance et "
                             "au plus tard au départ")
        faits.append(fait(f"incapacite_permanente_{ASSURE}", ASSURE, "decision_medicale",
                          _jour(debut),
                          attributs={"decision": "incapacite_permanente", "age": age,
                                     "taux": TAUX_D_INCAPACITE_DECLARE}))
    # LES AUTRES TITRES AU TAUX PLEIN DE L. 351-8 (:mod:`.droit.categories`),
    # que la caisse constate à la demande de la pension, donc au départ : la
    # carte de déporté ou interné, deux titres ; le travail manuel des quinze
    # années qui précèdent la demande, une exposition.
    if invalidite.get("deporte"):
        faits.append(fait(f"deporte_ou_interne_{ASSURE}", ASSURE, "titre", _jour(depart),
                          attributs={"titre": "deporte_ou_interne"}))
    mois = invalidite.get("mois_de_guerre")
    if mois is not None:
        if not 0 < int(mois):
            raise ValueError(f"la captivité et les services de guerre : en mois, reçu {mois}")
        faits.append(fait(f"ancien_combattant_ou_prisonnier_{ASSURE}", ASSURE, "titre",
                          _jour(depart),
                          attributs={"titre": "ancien_combattant_ou_prisonnier",
                                     "mois": int(mois)}))
    if invalidite.get("travail_manuel"):
        faits.append(fait(f"travail_manuel_{ASSURE}", ASSURE, "exposition", _jour(depart),
                          attributs={"exposition": "travail_manuel",
                                     "nature": invalidite["travail_manuel"]}))
    return faits


#: Le taux d'incapacité permanente que la saisie déclare : « au moins 50 % ».
#: Ce que le droit exige à d'autres dates, 80 % avant 2015, elle ne l'établit pas.
TAUX_D_INCAPACITE_DECLARE = 50


#: La nature d'une activité exercée hors de France : salariée, ou non.
ACTIVITES_A_L_ETRANGER = ("salariee", "non_salariee")


def _etat_etranger(code) -> str:
    """Le code d'un État étranger, tel qu'un fait le porte pour territoire ;
    jamais la France, ni la métropole."""
    if not isinstance(code, str) or not code or code in ("FR", "metropole"):
        raise ValueError(f"un État étranger : son code, reçu « {code} »")
    return code


def _etranger(assure: dict, age_liquidation: float | None, etranger: dict) -> list[dict]:
    """Les faits de la carrière hors de France que la saisie déclare (voir
    :func:`_personne`) : une période à l'étranger par période, son État pour
    territoire ; un acte de la caisse de l'État par pension étrangère, la
    liquidation qu'elle notifie, avec son montant ; la résidence, à compter
    du départ."""
    if age_liquidation is None:
        raise ValueError("une carrière hors de France déclarée suppose un départ")
    naissance = mois_de(assure["debut"])
    depart = origine_de(assure).plus_mois(en_mois(age_liquidation))
    faits = []
    bornes = []
    for rang, periode in enumerate(etranger.get("periodes") or [], 1):
        debut = naissance.plus_mois(en_mois(periode["debut"]))
        fin = naissance.plus_mois(en_mois(periode["fin"]))
        if debut.rang <= naissance.rang or fin.rang <= debut.rang or fin.rang > depart.rang:
            raise ValueError("une période à l'étranger commence après la naissance, finit "
                             "après avoir commencé, et au plus tard au départ")
        if periode.get("activite") not in ACTIVITES_A_L_ETRANGER:
            raise ValueError(f"l'activité d'une période à l'étranger : salariée ou non, reçu "
                             f"« {periode.get('activite')} »")
        bornes.append((debut.rang, fin.rang))
        faits.append(fait(f"etranger_{rang}", ASSURE, "periode_a_l_etranger", _jour(debut),
                          _jour(fin), {"activite": periode["activite"]},
                          territoire=_etat_etranger(periode.get("pays"))))
    bornes.sort()
    if any(suivante[0] < precedente[1] for precedente, suivante in zip(bornes, bornes[1:])):
        raise ValueError("deux périodes à l'étranger se chevauchent")
    for rang, pension in enumerate(etranger.get("pensions") or [], 1):
        age = pension["age"]
        debut = naissance.plus_mois(en_mois(age))
        if debut.rang <= naissance.rang:
            raise ValueError("une pension étrangère commence après la naissance")
        if not pension["mensuel"] > 0:
            raise ValueError(f"le montant d'une pension étrangère : positif, reçu "
                             f"{pension['mensuel']}")
        faits.append(fait(f"pension_etrangere_{rang}", ASSURE, "acte_de_la_caisse",
                          _jour(debut), attributs={"acte": "liquidation", "age": age},
                          montant={"mensuel": pension["mensuel"], "monnaie": "EUR"},
                          territoire=_etat_etranger(pension.get("pays"))))
    mois = etranger.get("mois_en_france")
    if mois is not None and not 0 <= mois <= MOIS_PAR_AN:
        raise ValueError(f"les mois en France chaque année : de 0 à 12, reçu {mois}")
    if etranger.get("residence") is not None or mois is not None:
        # Hors de France, son État ; en France, les mois qu'elle y passe.
        faits.append(fait(f"residence_{ASSURE}", ASSURE, "residence", _jour(depart),
                          attributs=None if mois is None else {"mois_en_france": mois},
                          territoire=(None if etranger.get("residence") is None
                                      else _etat_etranger(etranger["residence"]))))
    return faits


def _naissance_du_conjoint(conjoint: dict) -> dict:
    """Le fait de naissance du conjoint déclaré : sa date et son sexe."""
    jour, precision = date_declaree(conjoint["naissance"], "la naissance du conjoint")
    if conjoint.get("sexe") not in ("H", "F"):
        raise ValueError(f"le sexe du conjoint : H ou F, reçu {conjoint.get('sexe')!r}")
    return fait(f"naissance_{CONJOINT}", CONJOINT, "naissance", jour,
                attributs={"sexe": conjoint["sexe"], "precision": precision})


def du_resume(annee_naissance: int, sexe: str, mois_naissance: int = 1,
              age_liquidation: float | None = None, nombre_enfants: int = 0,
              naissances_enfants: list | tuple = (), jour_naissance: int | None = None,
              presomptions: dict | None = None, conjoint: dict | None = None,
              deces: str | None = None, retraite_progressive: dict | None = None,
              emploi_retraite: dict | None = None,
              demandes_de_pension: dict[str, float] | None = None,
              invalidite: dict | None = None, etranger: dict | None = None) -> dict:
    """La chronologie d'une carrière construite ligne à ligne : la naissance,
    le départ et les enfants, sans ses périodes, que l'appelant a déjà
    traduites en années."""
    naissance, depart, liens = _personne(annee_naissance, mois_naissance, sexe,
                                         age_liquidation, nombre_enfants,
                                         naissances_enfants, jour_naissance,
                                         presomptions, conjoint=conjoint, deces=deces,
                                         retraite_progressive=retraite_progressive,
                                         emploi_retraite=emploi_retraite,
                                         demandes_de_pension=demandes_de_pension,
                                         invalidite=invalidite, etranger=etranger)
    return {"schema_version": SCHEMA_VERSION, "faits": naissance + depart, "liens": liens}


def du_parcours(annee_naissance: int, sexe: str, metiers: list["Metier"],
                age_liquidation: float, mois_naissance: int = 1,
                profil_carriere: str = "auto", interruptions: dict[int, str] | None = None,
                nombre_enfants: int = 0, part_primes: float = 0.0,
                naissances_enfants: list | tuple = (), jour_naissance: int | None = None,
                presomptions: dict | None = None, conjoint: dict | None = None,
                deces: str | None = None, retraite_progressive: dict | None = None,
                emploi_retraite: dict | None = None,
                demandes_de_pension: dict[str, float] | None = None,
                invalidite: dict | None = None, etranger: dict | None = None) -> dict:
    """La chronologie d'un parcours : un fait par métier, daté au mois, et un
    par année d'interruption.

    Un métier principal court jusqu'au début du suivant, le dernier jusqu'au
    départ ; une activité cumulée, de son âge de début à son âge de fin, ou
    au départ. Un début ou une fin d'activité tombe dans le mois où l'âge est
    atteint, compté du mois de naissance : on commence un métier le jour
    qu'on veut. Le départ tombe au premier mois où l'âge est révolu, compté
    du mois que le jour de naissance désigne (:func:`naissance_de_l_assure`) :
    la pension prend effet le premier du mois qui suit l'anniversaire. Les
    contrôles sont ceux du parcours : les métiers se suivent, le premier n'est
    pas cumulé, rien ne dépasse le départ.
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

    naissance, depart, liens = _personne(annee_naissance, mois_naissance, sexe,
                                         age_liquidation, nombre_enfants,
                                         naissances_enfants, jour_naissance,
                                         presomptions, conjoint=conjoint, deces=deces,
                                         retraite_progressive=retraite_progressive,
                                         emploi_retraite=emploi_retraite,
                                         demandes_de_pension=demandes_de_pension,
                                         invalidite=invalidite, etranger=etranger)
    mois_de_naissance = mois_de(naissance[0]["debut"])
    bornes = [mois_de_naissance.plus_mois(en_mois(metier.age_debut)) for metier in principaux]
    debut = bornes[0]
    # La pension prend effet ce mois-là : il n'est plus travaillé, la borne
    # est donc EXCLUE.
    fin = origine_de(naissance[0]).plus_mois(en_mois(age_liquidation))
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
        ouverture = mois_de_naissance.plus_mois(en_mois(metier.age_debut))
        cloture = (fin if metier.age_fin is None
                   else mois_de_naissance.plus_mois(en_mois(metier.age_fin)))
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

    return {"schema_version": SCHEMA_VERSION, "faits": naissance + periodes + depart,
            "liens": liens}


def du_releve(annee_naissance: int, sexe: str, releve: list["LigneRelevee"],
              age_liquidation: float, mois_naissance: int = 1,
              nombre_enfants: int = 0, part_primes: float = 0.0,
              naissances_enfants: list | tuple = (), jour_naissance: int | None = None,
              presomptions: dict | None = None, conjoint: dict | None = None,
              deces: str | None = None, retraite_progressive: dict | None = None,
              emploi_retraite: dict | None = None,
              demandes_de_pension: dict[str, float] | None = None,
              invalidite: dict | None = None, etranger: dict | None = None) -> dict:
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
                                         age_liquidation, nombre_enfants,
                                         naissances_enfants, jour_naissance,
                                         presomptions, conjoint=conjoint, deces=deces,
                                         retraite_progressive=retraite_progressive,
                                         emploi_retraite=emploi_retraite,
                                         demandes_de_pension=demandes_de_pension,
                                         invalidite=invalidite, etranger=etranger)
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

    Deux présomptions posent ici un fait ou un lien : ``naissance_des_enfants``
    date la naissance de chaque enfant dont la date n'est pas déclarée aux
    trente ans de son parent, et la filiation commence à cette naissance ;
    ``mariage_des_conjoints`` date le mariage que la saisie ne date pas aux
    vingt-sept ans de l'assuré. ``jour_de_naissance`` pose le sien à la
    construction, parce que les dates de la carrière en dépendent
    (:func:`naissance_de_l_assure`). Les autres présomptions du vocabulaire
    s'appliquent là où leur fait sera lu, et le disent (``appliquee_par``).

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
    for union in liens:
        if union["sorte"] != "union" or union.get("debut") is not None:
            continue
        epoux = naissances.get(union["de"])
        if epoux is None:
            continue
        union["debut"] = _plus_ans(epoux["debut"],
                                   valeur("mariage_des_conjoints", presomptions))
        union["origine"] = "presume"
        union["presomption"] = "mariage_des_conjoints"
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


def _divorce(union_: dict) -> bool:
    """L'union est-elle close par un divorce ?"""
    return (union_.get("fin") or {}).get("cause") == "divorce"


def conjoint(chronologie: dict, personne: str) -> str | None:
    """Le conjoint d'une personne : celui que son mariage lui relie, que le
    divorce n'a pas clos, ou ``None``. Le modèle n'en connaît qu'un, qui lui
    survit."""
    union_ = union(chronologie, personne)
    if union_ is None:
        return None
    return union_["vers"] if union_["de"] == personne else union_["de"]


def union(chronologie: dict, personne: str) -> dict | None:
    """Le mariage d'une personne que le divorce n'a pas clos, s'il est dit."""
    for lien_ in chronologie.get("liens") or []:
        if (lien_["sorte"] == "union" and personne in (lien_["de"], lien_["vers"])
                and not _divorce(lien_)):
            return lien_
    return None


def ex_conjoints(chronologie: dict, personne: str) -> list[tuple[str, dict]]:
    """Les précédents conjoints d'une personne, et le mariage que le divorce a
    clos, dans l'ordre de la chronologie."""
    return [(lien_["vers"] if lien_["de"] == personne else lien_["de"], lien_)
            for lien_ in chronologie.get("liens") or []
            if lien_["sorte"] == "union" and personne in (lien_["de"], lien_["vers"])
            and _divorce(lien_)]


def deces(chronologie: dict, personne: str) -> dict | None:
    """Le décès d'une personne, s'il est dit."""
    faits = faits_de(chronologie, personne, "deces")
    return faits[0] if faits else None


def _ressources_de_nature(chronologie: dict, personne: str, nature: str | None) -> dict | None:
    """Le fait de ressources d'une personne qui a cette nature : toutes ses
    ressources sans nature dite, ou une part d'elles, ou celles de son
    ménage."""
    return next((f for f in faits_de(chronologie, personne, "ressources")
                 if f["attributs"].get("nature") == nature), None)


def ressources(chronologie: dict, personne: str) -> float | None:
    """Les ressources annuelles qu'une personne déclare, ou ``None``."""
    fait_ = _ressources_de_nature(chronologie, personne, None)
    return None if fait_ is None else float(fait_["montant"]["annuel"])


def revenus_d_activite(chronologie: dict, personne: str) -> float | None:
    """La part de ses ressources que son activité rapporte à une personne, si
    elle la déclare, ou ``None``."""
    fait_ = _ressources_de_nature(chronologie, personne, "revenus_d_activite")
    return None if fait_ is None else float(fait_["montant"]["annuel"])


def menage(chronologie: dict, personne: str) -> tuple[str, float | None] | None:
    """Le ménage où une personne dit vivre : la forme de son union, et les
    ressources annuelles que l'autre y apporte, ou ``None`` quand il ne les dit
    pas ; ``None`` pour qui vit seul."""
    fait_ = _ressources_de_nature(chronologie, personne, "menage")
    if fait_ is None:
        return None
    montant = fait_.get("montant")
    return fait_["attributs"]["forme"], None if not montant else float(montant["annuel"])


def debut_du_menage(chronologie: dict, personne: str) -> str | None:
    """Le jour où commence le ménage où une personne dit vivre — son union
    nouvelle, ou son remariage —, ou ``None`` pour qui vit seul."""
    fait_ = _ressources_de_nature(chronologie, personne, "menage")
    return None if fait_ is None else fait_["debut"]


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


def retraite_progressive(chronologie: dict, personne: str) -> dict | None:
    """La demande de retraite progressive d'une personne, si elle la déclare."""
    for acte in faits_de(chronologie, personne, "acte_de_la_personne"):
        if acte["attributs"].get("acte") == "retraite_progressive":
            return acte
    return None


def demandes_de_pension(chronologie: dict, personne: str) -> list[dict]:
    """Les pensions dont une personne déclare la date de demande : un acte par
    régime, dans l'ordre de leurs codes."""
    return [acte for acte in faits_de(chronologie, personne, "acte_de_la_personne")
            if acte["attributs"].get("acte") == "demande_de_pension"]


def decision_medicale(chronologie: dict, personne: str, decision: str) -> dict | None:
    """La décision médicale d'une personne, de cette nature — ``pension_d_invalidite``,
    ``inaptitude`` ou ``incapacite_permanente`` de l'assuré, ``invalidite`` de son
    conjoint —, si elle est dite."""
    for f in faits_de(chronologie, personne, "decision_medicale"):
        if f["attributs"].get("decision") == decision:
            return f
    return None


def titre(chronologie: dict, personne: str, nom: str) -> dict | None:
    """Le titre d'une personne, de ce nom — ``deporte_ou_interne``,
    ``ancien_combattant_ou_prisonnier`` —, s'il est dit."""
    for f in faits_de(chronologie, personne, "titre"):
        if f["attributs"].get("titre") == nom:
            return f
    return None


def exposition(chronologie: dict, personne: str, nom: str) -> dict | None:
    """L'exposition d'une personne, de ce nom — ``travail_manuel`` —, si elle est
    dite."""
    for f in faits_de(chronologie, personne, "exposition"):
        if f["attributs"].get("exposition") == nom:
            return f
    return None


def radiation_pour_invalidite(chronologie: dict, personne: str) -> dict | None:
    """La radiation des cadres pour invalidité d'une personne, si elle est dite."""
    for f in faits_de(chronologie, personne, "radiation"):
        if f["attributs"].get("motif") == "invalidite":
            return f
    return None


def periodes_a_l_etranger(chronologie: dict, personne: str) -> list[dict]:
    """Les périodes qu'une personne a passées hors de France, dans leur ordre :
    leur État est leur territoire."""
    return faits_de(chronologie, personne, "periode_a_l_etranger")


def pensions_etrangeres(chronologie: dict, personne: str) -> list[dict]:
    """Les pensions étrangères d'une personne, dans leur ordre : les
    liquidations que la caisse d'un autre État lui notifie, celui-ci pour
    territoire."""
    return [acte for acte in faits_de(chronologie, personne, "acte_de_la_caisse")
            if acte["attributs"].get("acte") == "liquidation"
            and acte.get("territoire", "metropole") != "metropole"]


def residence(chronologie: dict, personne: str) -> dict | None:
    """La résidence qu'une personne déclare après son départ, si elle la dit :
    hors de France, son État pour territoire ; en France, la métropole, et
    les ``mois_en_france`` qu'elle y passe chaque année."""
    faits = faits_de(chronologie, personne, "residence")
    return faits[0] if faits else None


def periodes(chronologie: dict, personne: str) -> list[dict]:
    """Les périodes d'emploi et d'interruption d'une personne, dans leur
    ordre, jusqu'à son départ : l'activité d'après le départ n'en est pas
    (:func:`emploi_retraite`)."""
    return [f for f in faits_de(chronologie, personne) if f["sorte"] in (EMPLOI, INTERRUPTION)
            and not f["attributs"].get("apres_depart")]


def emploi_retraite(chronologie: dict, personne: str) -> dict | None:
    """L'activité qu'une personne exerce après son départ, si elle la
    déclare : le cumul emploi-retraite."""
    for periode in faits_de(chronologie, personne, EMPLOI):
        if periode["attributs"].get("apres_depart"):
            return periode
    return None


def enfants(chronologie: dict, personne: str) -> list[str]:
    """Les enfants d'une personne, dans l'ordre de leurs filiations."""
    return [l["vers"] for l in chronologie.get("liens") or []
            if l["sorte"] == "filiation" and l["de"] == personne]


def annee_de(jour: str) -> int:
    """L'année d'une date de la chronologie."""
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
