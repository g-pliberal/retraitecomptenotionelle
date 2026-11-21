"""Les deux filets de la carte de justesse (action 194, étape B).

Ils ne prouvent rien : ils disent où regarder d'abord. Ni l'un ni l'autre ne
change l'état d'une partie de la carte (``justesse.py``).

Le balayage de cohérence
------------------------

Cotiser plus ne baisse jamais la pension. Trois perturbations, que la loi ne
traite pas de même, se comptent à part :

    a   plus de salaire une année, à carrière et départ égaux ;
    b   une année d'activité de plus, à départ égal (le début avancé d'un an) ;
    c   un trimestre de départ plus tard.

Une baisse n'est admise que si une ligne de la liste des baisses légales
(:data:`LISTE`) la rattache à un texte cité, sous une condition que le
balayage vérifie (:data:`CONDITIONS`) ; en (c), aussi quand une borne de
version — une date d'effet où une fiche du paquet change de version — tombe
entre les deux départs. Le reste est « à expliquer ».

Et aucun saut du taux de remplacement entre deux générations voisines (un mois
d'écart, à âge de départ égal) au-delà de :data:`SEUIL_DE_SAUT`, hors de ceux
qu'une borne explique : une table du paquet dont une ligne commence à la
génération d'après ou à la date du départ d'après, ou une version qui y
commence (:func:`bornes_du_paquet`). Le taux de remplacement neutralise la
croissance des salaires : la carrière est écrite en part du salaire moyen de
chaque année, et la pension rapportée au dernier revenu.

La neutralisation
-----------------

Chaque partie de la carte — une version de fiche, ou la fiche entière — est
mutée, et les témoins rejoués. Trois mutations, dans cet ordre :

    parametres    ±1 sur un entier, ×1,01 sur un nombre réel, dans le contenu
                  de la version (``parametres`` et ``table``) ;
    source        la même mutation sur les colonnes ou les clés de la source
                  que la fiche nomme (``code.parametres``), pour la fiche
                  entière ;
    interrupteur  les interrupteurs de la fiche (``code.interrupteurs``)
                  inversés, pour la fiche entière.

Une mutation qui laisse le paquet identique n'atteint pas le moteur : elle ne
dit rien. Une partie est ``gardee`` si un témoin change sous une mutation qui
l'atteint, ``non_gardee`` si aucune n'en fait changer, ``hors_d_atteinte`` si
aucune n'atteint le paquet. Une partie non gardée n'est pas fausse : elle n'est
pas surveillée. Une mutation que la fabrique refuse (``refus…`` pour
empreinte) n'atteint pas le moteur ; la partie le dit (``refusee``). Seuls les témoins de simulation se rejouent : la garde est une
borne basse.
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Callable, Iterable
from pathlib import Path

from ..config import RACINE_DONNEES

RACINE = RACINE_DONNEES.parent
DOSSIER = RACINE / "tests" / "cliquets_de_justesse"
#: Le dernier rapport des deux filets, que ``scripts/filets.py`` écrit.
RAPPORT = DOSSIER / "filets_rapport.yaml"
#: Le cliquet : ce que le rapport ne peut que faire baisser.
CLIQUET = DOSSIER / "filets.yaml"
#: Les baisses légales, chacune rattachée à un texte cité.
LISTE = DOSSIER / "baisses_legales.yaml"

#: Un saut se compte au-delà de 1 % du taux de remplacement (écart relatif).
SEUIL_DE_SAUT = 0.01
#: Une baisse se compte au-delà d'un millionième de la pension : en deçà, ce
#: sont les arrondis du calcul.
TOLERANCE_DE_BAISSE = 1e-6
PERTURBATIONS = ("a", "b", "c")
#: Ce qui admet un saut que suit un trimestre validé de plus (ou de moins),
#: dans son sens : la durée se compte au trimestre, validé au salaire de
#: l'année civile (code de la sécurité sociale, L. 351-2 et R. 351-9).
TRIMESTRE_VALIDE = "trimestre validé (L. 351-2, R. 351-9)"

#: Les conditions qu'une ligne de la liste peut poser, et ce que chacune lit
#: de la paire ``(base, perturbe)``.
CONDITIONS: dict[str, Callable[[dict, dict, object], bool]] = {
    # La carrière perturbée commence avant cette année.
    "debut_avant": lambda base, perturbe, annee: perturbe["debut"] < int(annee),
    # Les régimes qui servent la pension ne sont pas les mêmes.
    "regimes_changent": lambda base, perturbe, oui: (
        set(base["regimes"]) != set(perturbe["regimes"])) == bool(oui),
    # Au moins deux de ces régimes servent l'une des deux pensions.
    "plusieurs_parmi": lambda base, perturbe, regimes: max(
        len(set(base["regimes"]) & set(regimes)),
        len(set(perturbe["regimes"]) & set(regimes))) >= 2,
    # Le départ perturbé a lieu avant ce mois (« AAAA-MM »).
    "depart_avant": lambda base, perturbe, mois: perturbe["depart"] < _rang_du_texte(mois),
}

# --- Les rangs de mois -------------------------------------------------------


def _rang_du_texte(texte: str) -> int:
    annee, mois = str(texte).split("-")[:2]
    return int(annee) * 12 + int(mois) - 1


def _rang_d_une_annee(valeur: float) -> int:
    """1951.5 est juillet 1951 ; les fractions se lisent au mois le plus
    proche (1961.667 est septembre 1961)."""
    return round(float(valeur) * 12)


def _rang_d_une_date(date: str) -> int:
    """Le premier départ qu'une date d'effet régit : le premier du mois qui la
    suit, ou ce jour s'il est le premier."""
    annee, mois, jour = (int(x) for x in str(date)[:10].split("-"))
    return annee * 12 + mois - 1 + (1 if jour > 1 else 0)


def texte_du_rang(rang: int) -> str:
    return f"{rang // 12}-{rang % 12 + 1:02d}"


# --- Les bornes du paquet ----------------------------------------------------

#: Ce que le paquet porte sans que le droit d'une carrière s'y lise : séries
#: macroéconomiques, agrégats, certification, coût.
HORS_DU_DROIT = frozenset({
    "agregats", "bilan_equilibre", "certification", "series", "hypotheses", "depenses",
    "effectifs_cotisants", "effectifs_retraites", "population", "populations",
    "distribution_pensions", "distribution_pensions_sexes", "patrimoine_menages",
    "quotients", "quotients_projetes", "quotients_projetes_variantes", "courbe_taux_sans_risque",
    "credits_ministeres", "caracteristiques_retraites", "inventaire", "institutions_citees",
    "frontiere", "constats", "univers", "version", "fiches_datees", "versions_des_fiches",
})


def _est_annee(cle) -> bool:
    try:
        valeur = float(cle)
    except (TypeError, ValueError):
        return False
    return 1850.0 <= valeur <= 2150.0


def _ajouter(bornes: dict[int, list[str]], rang: int, source: str) -> None:
    sources = bornes.setdefault(rang, [])
    if source not in sources:
        sources.append(source)


def _est_date(valeur) -> bool:
    texte = str(valeur)
    return (isinstance(valeur, str) and len(texte) >= 10 and texte[4] == "-"
            and texte[7] == "-" and texte[:4].isdigit())


def _tables_par_annee(objet, chemin: str, bornes: dict[int, list[str]]) -> None:
    """Toute table du paquet dont les clés sont des années (une génération ou
    une date) pose une borne à chacune de ses lignes ; toute liste de lignes
    datées (« AAAA-MM-JJ », ou [année, mois, …] pour les valeurs de service),
    à la date de chacune."""
    if isinstance(objet, list):
        for ligne in objet:
            if isinstance(ligne, list) and ligne and _est_date(ligne[0]):
                _ajouter(bornes, _rang_d_une_date(ligne[0]), chemin)
            elif (chemin.startswith("valeurs_service_datees") and isinstance(ligne, list)
                  and len(ligne) > 2 and isinstance(ligne[1], int) and 1 <= ligne[1] <= 12):
                _ajouter(bornes, int(ligne[0]) * 12 + ligne[1] - 1, chemin)
        return
    if isinstance(objet, dict):
        if objet and all(_est_annee(cle) for cle in objet):
            for cle in objet:
                _ajouter(bornes, _rang_d_une_annee(cle), chemin)
            return
        for cle, valeur in objet.items():
            _tables_par_annee(valeur, f"{chemin}.{cle}" if chemin else str(cle), bornes)


def _versions_du_paquet(paquet: dict):
    for cle in ("fiches_datees", "versions_des_fiches"):
        for nom, fiche in (paquet.get(cle) or {}).items():
            for version in fiche.get("versions") or []:
                yield nom, version


def bornes_de_version(paquet: dict) -> dict[int, list[str]]:
    """Chaque date d'effet où une fiche du paquet change de version, au rang
    du premier départ que la nouvelle version régit."""
    bornes: dict[int, list[str]] = {}
    for nom, version in _versions_du_paquet(paquet):
        for debut_fin in (version.get("bornes") or {}).values():
            for date in debut_fin or ():
                if date:
                    _ajouter(bornes, _rang_d_une_date(date), f"{nom} / {version['id']}")
    return bornes


def bornes_du_paquet(paquet: dict) -> dict[int, list[str]]:
    """Chaque mois où une table ou une version du paquet commence une ligne :
    les tables par année du droit, les lignes des tables de version
    (``[début, fin, …]``, en années de naissance), les lignes des barèmes
    datés (la carrière longue, la surcote, les calendriers de durée requise),
    et les bornes de version (:func:`bornes_de_version`)."""
    bornes: dict[int, list[str]] = {}
    for cle, valeur in paquet.items():
        if cle not in HORS_DU_DROIT:
            _tables_par_annee(valeur, cle, bornes)
    for nom, version in _versions_du_paquet(paquet):
        for ligne in version.get("table") or []:
            if isinstance(ligne, list) and ligne and _est_annee(ligne[0]):
                _ajouter(bornes, _rang_d_une_annee(ligne[0]), f"{nom} / {version['id']}")
    for lignes in (paquet.get("carriere_longue") or {}).values():
        for ligne in lignes:
            _ajouter(bornes, _rang_d_une_annee(ligne[0]), "carriere_longue")
    for ligne in paquet.get("surcote_baremes") or []:
        for valeur in ligne[1:3]:
            if _est_annee(valeur):
                _ajouter(bornes, _rang_d_une_annee(valeur), "surcote_baremes")
    for nom, lignes in (paquet.get("calendriers_duree_requise") or {}).items():
        for ligne in lignes:
            _ajouter(bornes, int(ligne[0]), f"calendriers_duree_requise.{nom}")
    for nom, regle in (paquet.get("durees_requises_regimes") or {}).items():
        if isinstance(regle, dict) and isinstance(regle.get("depuis"), (int, float)):
            _ajouter(bornes, int(regle["depuis"]), f"durees_requises_regimes.{nom}")
    for rang, sources in bornes_de_version(paquet).items():
        for source in sources:
            _ajouter(bornes, rang, source)
    return bornes


# --- Classer un saut et une baisse ------------------------------------------


def _franchies(bornes: dict[int, list[str]], avant: int, apres: int) -> list[str]:
    sources: list[str] = []
    for rang in range(avant + 1, apres + 1):
        for source in bornes.get(rang, ()):
            if source not in sources:
                sources.append(source)
    return sources


def classer_saut(avant: dict, apres: dict, bornes: dict[int, list[str]],
                 seuil: float = SEUIL_DE_SAUT) -> dict | None:
    """``None`` sous le seuil ; sinon ``admis`` si une borne tombe à la
    génération d'après ou entre les deux départs, ``a_expliquer`` sinon.
    ``avant`` et ``apres`` : ``generation`` et ``depart`` en rangs de mois,
    ``taux`` de remplacement, et ``pension`` quand elle est connue : un saut
    du taux sans saut de la pension n'en est pas un ; ``effets``, la date où
    chaque régime sert sa pension, qui franchit une borne comme le départ."""
    if avant["taux"] <= 0:
        return None
    ecart = apres["taux"] / avant["taux"] - 1.0
    if abs(ecart) <= seuil:
        return None
    # Le dénominateur du taux change au 1er janvier : sans que la pension
    # bouge autant, ce n'est pas un saut de la pension.
    if avant.get("pension") and apres.get("pension") is not None and abs(
            apres["pension"] / avant["pension"] - 1.0) <= seuil:
        return None
    sources = _franchies(bornes, avant["generation"], apres["generation"])
    for source in _franchies(bornes, avant["depart"], apres["depart"]):
        if source not in sources:
            sources.append(source)
    effets_avant, effets_apres = avant.get("effets") or {}, apres.get("effets") or {}
    for regime in sorted(set(effets_avant) & set(effets_apres)):
        bas, haut = sorted((effets_avant[regime], effets_apres[regime]))
        if bas == haut:
            continue
        # Une revalorisation au jour même où la pension est servie la touche
        # ou non selon son texte : la borne compte des deux côtés.
        for source in _franchies(bornes, bas - 1, haut):
            if source not in sources:
                sources.append(source)
    duree = (apres.get("trimestres") or 0) - (avant.get("trimestres") or 0)
    if not sources and duree * ecart > 0:
        sources = [TRIMESTRE_VALIDE]
    return {"statut": "admis" if sources else "a_expliquer", "ecart": ecart,
            "bornes": sources}


def controler_liste(liste: list[dict]) -> list[dict]:
    """Chaque ligne cite un texte, nomme sa perturbation et ne pose que des
    conditions que le balayage sait vérifier."""
    for ligne in liste:
        texte = ligne.get("texte") or {}
        if not texte.get("id"):
            raise ValueError(f"baisse légale {ligne.get('id')} : aucun texte cité")
        if ligne.get("perturbation") not in PERTURBATIONS:
            raise ValueError(f"baisse légale {ligne.get('id')} : perturbation inconnue")
        inconnues = set(ligne.get("si") or {}) - set(CONDITIONS)
        if inconnues:
            raise ValueError(f"baisse légale {ligne.get('id')} : condition inconnue "
                             f"{sorted(inconnues)}")
    return liste


def classer_baisse(perturbation: str, base: dict, perturbe: dict,
                   versions: dict[int, list[str]], liste: list[dict]) -> dict | None:
    """``None`` sans baisse ; sinon ``admis`` — par une borne de version entre
    les deux départs en (c), ou par une ligne de la liste —, ``a_expliquer``
    sinon. ``base`` et ``perturbe`` : ``pension``, ``depart`` (rang de mois),
    ``debut`` (année), ``regimes``."""
    if base["pension"] <= 0:
        return None
    ecart = perturbe["pension"] / base["pension"] - 1.0
    if ecart >= -TOLERANCE_DE_BAISSE:
        return None
    if perturbation == "c":
        sources = _franchies(versions, base["depart"], perturbe["depart"])
        if sources:
            return {"statut": "admis", "ecart": ecart, "regle": "borne_de_version",
                    "bornes": sources}
    for ligne in liste:
        if ligne["perturbation"] != perturbation:
            continue
        if all(CONDITIONS[nom](base, perturbe, valeur)
               for nom, valeur in (ligne.get("si") or {}).items()):
            return {"statut": "admis", "ecart": ecart, "regle": ligne["id"], "bornes": []}
    return {"statut": "a_expliquer", "ecart": ecart, "regle": None, "bornes": []}


# --- Le balayage ---------------------------------------------------------------


def requete(cas: dict, generation: int, age_mois: int, **changes) -> dict:
    """La requête du simulateur d'un cas type, né au rang ``generation``,
    parti à ``age_mois`` mois : sa carrière en part du salaire moyen de chaque
    année, d'un profil plat."""
    naissance = generation // 12
    q = {"naissance": str(naissance), "naissance_mois": str(generation % 12 + 1),
         "statut": cas["statut"], "debut": str(cas["debut"]),
         "liquidation": str(age_mois // 12), "liquidation_mois": str(age_mois % 12),
         "salaire": str(cas["salaire"]), "unite_revenu": "moyen", "profil": "plat",
         "sexe": cas.get("sexe", "H"), "enfants": str(cas.get("enfants", 0))}
    if cas.get("primes"):
        q["primes"] = str(cas["primes"])
    if cas.get("interruptions_relatives"):
        q["interruptions"] = ", ".join(
            f"{naissance + int(cas['debut']) + rel}:{naissance + int(cas['debut']) + rel}:{motif}"
            for rel, motif in cas["interruptions_relatives"])
    q.update({cle: str(valeur) for cle, valeur in changes.items()})
    return q


def annees_de_hausse(cas: dict, generation: int, age_mois: int) -> list[int]:
    """Les années où la perturbation (a) hausse le salaire : la deuxième de la
    carrière, celle des quarante ans, et la dernière entière avant le départ."""
    naissance = generation // 12
    debut = naissance + int(cas["debut"])
    derniere = naissance + age_mois // 12 - 1
    choisies = [debut + 1, naissance + 40, derniere]
    return sorted({a for a in choisies if debut < a <= derniere})


def perturbations(cas: dict, generation: int, age_mois: int) -> list[tuple[str, int | None, dict]]:
    """Chaque perturbation d'un cas : sa lettre, l'année qu'elle touche, sa
    requête."""
    sortie = []
    for annee in annees_de_hausse(cas, generation, age_mois):
        sortie.append(("a", annee, requete(
            cas, generation, age_mois,
            metier2_statut=cas["statut"], metier2_debut=f"{annee}-01",
            metier2_salaire=round(float(cas["salaire"]) * 1.2, 6),
            metier3_statut=cas["statut"], metier3_debut=f"{annee + 1}-01",
            metier3_salaire=cas["salaire"])))
    sortie.append(("b", None, requete(cas, generation, age_mois, debut=int(cas["debut"]) - 1)))
    sortie.append(("c", None, requete(cas, generation, age_mois + 3)))
    return sortie


def _resume(requete_: dict, rendu: dict) -> dict:
    naissance = int(requete_["naissance"]) * 12 + int(requete_["naissance_mois"]) - 1
    return {"pension": rendu["pension"], "taux": rendu["taux"], "depart": rendu["depart"],
            "regimes": rendu["regimes"], "generation": naissance,
            "trimestres": rendu.get("trimestres"), "effets": rendu.get("effets") or {},
            "debut": int(requete_["naissance"]) + int(requete_["debut"])}


class _Anomalies:
    def __init__(self) -> None:
        self.groupes: dict[tuple, dict] = {}

    def noter(self, sorte: str, cas: str, point: str, age_mois: int, ecart: float,
              avant: dict, apres: dict) -> None:
        groupe = self.groupes.setdefault((sorte, cas, point), {
            "sorte": sorte, "cas": cas, "point": point, "pensions": 0,
            "ages": [age_mois, age_mois], "ecart_max": 0.0,
            "exemple": {"avant": avant, "apres": apres}})
        groupe["pensions"] += 1
        groupe["ages"] = [min(groupe["ages"][0], age_mois), max(groupe["ages"][1], age_mois)]
        if abs(ecart) > abs(groupe["ecart_max"]):
            groupe["ecart_max"] = ecart
            groupe["exemple"] = {"avant": avant, "apres": apres}

    def triees(self) -> list[dict]:
        sortie = []
        for groupe in sorted(self.groupes.values(),
                             key=lambda g: (-g["pensions"], g["sorte"], g["cas"], g["point"])):
            groupe = dict(groupe)
            groupe["ages"] = [round(a / 12, 2) for a in groupe["ages"]]
            groupe["ecart_max"] = round(groupe["ecart_max"], 6)
            sortie.append(groupe)
        return sortie


def balayer(cas_types: list[dict], generations_annees: Iterable[int],
            generations_mois: Iterable[int], ages_mois: Iterable[int],
            simuler: Callable[[list[dict]], list[dict]], bornes: dict[int, list[str]],
            versions: dict[int, list[str]], liste: list[dict],
            seuil: float = SEUIL_DE_SAUT) -> dict:
    """Le balayage : les baisses sur les générations ``generations_annees``
    (nées en janvier), les sauts sur les générations ``generations_mois``
    (rangs de mois, de mois en mois), à chaque âge de ``ages_mois``.
    ``simuler`` rend, pour chaque requête, ``pension``, ``taux``,
    ``ouverte``, ``regimes`` et ``depart`` (rang de mois), ou ``None`` quand
    le simulateur la refuse."""
    controler_liste(liste)
    ages = list(ages_mois)
    generations_mois = sorted(generations_mois)
    paires: list[tuple] = []   # (sorte, cas, age, requête de base, requête perturbée)
    for cas in cas_types:
        for age in ages:
            for annee in generations_annees:
                generation = annee * 12
                base = requete(cas, generation, age)
                for lettre, _annee, perturbee in perturbations(cas, generation, age):
                    paires.append((f"baisse_{lettre}", cas["code"], age, base, perturbee))
            for avant, apres in zip(generations_mois, generations_mois[1:]):
                if apres - avant == 1:
                    paires.append(("saut", cas["code"], age, requete(cas, avant, age),
                                   requete(cas, apres, age)))
    requetes: dict[str, dict] = {}
    for _sorte, _cas, _age, base, perturbee in paires:
        for q in (base, perturbee):
            requetes.setdefault(json.dumps(q, sort_keys=True), q)
    cles = list(requetes)
    rendus = dict(zip(cles, simuler([requetes[c] for c in cles])))
    return _classer_les_paires(paires, rendus, bornes, versions, liste, seuil, len(cles))


def _classer_les_paires(paires, rendus, bornes, versions, liste, seuil, calculs) -> dict:
    comptes = {"calculs": calculs, "fermees": 0,
               "sauts": {"admis": 0, "a_expliquer": 0},
               "baisses": {p: {"admis": 0, "a_expliquer": 0} for p in PERTURBATIONS},
               "a_expliquer": 0}
    anomalies = _Anomalies()
    saines: list[dict] = []
    for sorte, cas, age, base, perturbee in paires:
        r_base = rendus[json.dumps(base, sort_keys=True)]
        r_pert = rendus[json.dumps(perturbee, sort_keys=True)]
        if not r_base or not r_pert or not r_base["ouverte"] or not r_pert["ouverte"]:
            comptes["fermees"] += 1
            continue
        b, p = _resume(base, r_base), _resume(perturbee, r_pert)
        if sorte == "saut":
            verdict = classer_saut(b, p, bornes, seuil)
            compte = comptes["sauts"]
            point = texte_du_rang(p["generation"])
        else:
            verdict = classer_baisse(sorte[-1], b, p, versions, liste)
            compte = comptes["baisses"][sorte[-1]]
            point = texte_du_rang(b["generation"])
        if verdict is None:
            if len(saines) < 400 and (sorte != "saut" or _franchies(bornes, b["generation"],
                                                                     p["generation"])):
                saines.append({"sorte": sorte, "avant": base, "apres": perturbee})
            continue
        compte[verdict["statut"]] += 1
        if verdict["statut"] == "a_expliquer":
            comptes["a_expliquer"] += 1
            anomalies.noter(sorte, cas, point, age, verdict["ecart"], base, perturbee)
    groupes = anomalies.triees()
    return {"comptes": comptes, "a_expliquer": groupes,
            "echantillon": _echantillon(groupes, saines)}


#: L'échantillon fixe que le cliquet rejoue : un exemple de chaque groupe
#: d'anomalies, au plus :data:`ECHANTILLON_ANOMALIES`, et des paires saines.
ECHANTILLON_ANOMALIES = 150
ECHANTILLON_SAINES = 50


def _echantillon(groupes: list[dict], saines: list[dict]) -> dict:
    paires = [{"sorte": g["sorte"], **g["exemple"]} for g in groupes[:ECHANTILLON_ANOMALIES]]
    pas = max(1, len(saines) // ECHANTILLON_SAINES)
    paires += saines[::pas][:ECHANTILLON_SAINES]
    return {"a_expliquer": min(len(groupes), ECHANTILLON_ANOMALIES), "paires": paires}


# --- Le moteur du jour, par le pont ------------------------------------------


MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")
_SERVIE = re.compile(r"servie (?:depuis le|à partir du) 1er (" + "|".join(MOIS) + r") (\d{4})")


def effets_par_regime(par_regime: list[dict]) -> dict[str, int]:
    """La date où chaque pension est servie, quand le résultat la dit : son
    ``date_effet``, ou « servie depuis le 1er … » de son détail."""
    effets = {}
    for pension in par_regime:
        if pension.get("date_effet"):
            effets[pension["regime"]] = _rang_d_une_date(pension["date_effet"])
            continue
        trouve = _SERVIE.search(pension.get("detail") or "")
        if trouve:
            effets[pension["regime"]] = int(trouve.group(2)) * 12 + MOIS.index(trouve.group(1))
    return effets


def rendu_du_pont(resultat: dict) -> dict:
    """Ce que le balayage lit d'un résultat de ``Comparaison.dictionnaire()``."""
    actuel = resultat["scenarios"]["actuel"]
    assure = resultat["assure"]
    return {"pension": actuel["pension_annuelle"], "taux": actuel["taux_remplacement"],
            "ouverte": bool(actuel.get("liquidation_ouverte", True)),
            "regimes": sorted({r["regime"] for r in actuel["par_regime"]}),
            "depart": assure["annee_liquidation"] * 12 + assure["mois_liquidation"] - 1,
            "trimestres": assure.get("trimestres_actuels"),
            "effets": effets_par_regime(actuel["par_regime"])}


def simuler_par_le_pont(requetes: list[dict], paquet: bytes | None = None) -> list[dict | None]:
    """Chaque requête simulée par le portage (``pont.mjs``, demande
    ``simulations``), comme le site la simule ; ``None`` pour un refus."""
    from .. import pont

    cas = [{"cle": str(i), "requete": q} for i, q in enumerate(requetes)]
    reponse = pont._demander({"simulations": {"cas": cas}}, paquet)
    resultats = reponse["resultats"]
    return [rendu_du_pont(resultats[str(i)]["resultat"]) if str(i) in resultats else None
            for i in range(len(requetes))]


def paquet_du_depot() -> dict:
    return json.loads((RACINE / "moteur" / "donnees.json").read_text(encoding="utf-8"))


def charger_liste(chemin: Path = LISTE) -> list[dict]:
    import yaml

    return controler_liste(list((yaml.safe_load(chemin.read_text(encoding="utf-8")) or {})
                                .get("baisses") or []))


def rejouer_echantillon(echantillon: dict, simuler=None, paquet: dict | None = None,
                        liste: list[dict] | None = None) -> dict:
    """L'échantillon fixe d'un rapport, rejoué sur le moteur du jour : le
    nombre de ses paires encore à expliquer, et celles qui le sont devenues."""
    simuler = simuler_par_le_pont if simuler is None else simuler
    paquet = paquet_du_depot() if paquet is None else paquet
    liste = charger_liste() if liste is None else liste
    bornes, versions = bornes_du_paquet(paquet), bornes_de_version(paquet)
    paires = echantillon["paires"]
    requetes = [q for paire in paires for q in (paire["avant"], paire["apres"])]
    rendus = simuler(requetes)
    a_expliquer, nouvelles = 0, []
    for i, paire in enumerate(paires):
        r_base, r_pert = rendus[2 * i], rendus[2 * i + 1]
        if not r_base or not r_pert or not r_base["ouverte"] or not r_pert["ouverte"]:
            continue
        b, p = _resume(paire["avant"], r_base), _resume(paire["apres"], r_pert)
        verdict = (classer_saut(b, p, bornes) if paire["sorte"] == "saut"
                   else classer_baisse(paire["sorte"][-1], b, p, versions, liste))
        if verdict is not None and verdict["statut"] == "a_expliquer":
            a_expliquer += 1
            if i >= echantillon["a_expliquer"]:
                nouvelles.append(paire)
    return {"a_expliquer": a_expliquer, "nouvelles": nouvelles}


# --- La neutralisation ---------------------------------------------------------


def muter_valeurs(objet):
    """±1 sur un entier, ×1,01 sur un nombre réel ; le reste tel quel."""
    if isinstance(objet, bool) or objet is None:
        return objet
    if isinstance(objet, int):
        return objet + 1
    if isinstance(objet, float):
        return objet * 1.01 if objet != 0.0 else 0.01
    if isinstance(objet, dict):
        return {cle: muter_valeurs(valeur) for cle, valeur in objet.items()}
    if isinstance(objet, list):
        return [muter_valeurs(valeur) for valeur in objet]
    return objet


def _a_des_nombres(objet) -> bool:
    if isinstance(objet, bool):
        return False
    if isinstance(objet, (int, float)):
        return True
    if isinstance(objet, dict):
        return any(_a_des_nombres(v) for v in objet.values())
    if isinstance(objet, list):
        return any(_a_des_nombres(v) for v in objet)
    return False


def version_mutee(fiche: dict, version: str) -> dict | None:
    """La fiche, sa version ``version`` mutée (``parametres`` et ``table`` de
    son contenu) ; ``None`` si elle n'a aucun nombre à muter."""
    mutee = copy.deepcopy(fiche)
    for v in mutee.get("versions") or []:
        if v.get("id") != version:
            continue
        contenu = v.get("contenu") or {}
        cles = [c for c in ("parametres", "table") if _a_des_nombres(contenu.get(c))]
        if not cles:
            return None
        for cle in cles:
            contenu[cle] = muter_valeurs(contenu[cle])
        return mutee
    return None


def interrupteurs_coupes(fiche: dict) -> dict | None:
    """La fiche, ses interrupteurs inversés ; ``None`` sans interrupteur."""
    interrupteurs = (fiche.get("code") or {}).get("interrupteurs") or {}
    booleens = {cle: v for cle, v in interrupteurs.items() if isinstance(v, bool)}
    if not booleens:
        return None
    mutee = copy.deepcopy(fiche)
    mutee["code"]["interrupteurs"].update({cle: not v for cle, v in booleens.items()})
    return mutee


def a_une_source(fiche: dict) -> bool:
    """La fiche nomme-t-elle une source de paramètres, fichier et colonnes ?"""
    source = (fiche.get("code") or {}).get("parametres")
    return isinstance(source, str) and ":" in source


def neutraliser(fiches: dict[str, dict], rejouer: Callable[[dict], tuple] | None = None,
                executer: Callable[[list[dict]], Iterable[tuple]] | None = None,
                ) -> dict[tuple[str, str | None], dict]:
    """L'état de garde de chaque partie : ``gardee``, ``non_gardee`` ou
    ``hors_d_atteinte``, la mutation qui l'a décidé et les témoins qui
    changent.

    Une tâche est ``{"fiches": {nom: fiche mutée}, "source": nom ou None}`` :
    les fiches remplacées, et la fiche dont la source se mute. ``executer``
    rend, pour chaque tâche, ``(empreinte du paquet, résultats des
    témoins)`` ; sans lui, ``rejouer`` le fait sur les fiches entières, une
    tâche après l'autre (il ne sait pas muter une source)."""
    if executer is None:
        def executer(taches):
            for tache in taches:
                if tache["source"] is not None:
                    yield None, None
                else:
                    yield rejouer({**fiches, **tache["fiches"]})

    taches: list[dict] = [{"fiches": {}, "source": None}]
    plan: dict[tuple[str, str | None], list[tuple[str, int]]] = {}
    de_la_fiche: dict[str, list[tuple[str, int]]] = {}
    for nom, fiche in fiches.items():
        communes = []
        if a_une_source(fiche):
            taches.append({"fiches": {}, "source": nom})
            communes.append(("source", len(taches) - 1))
        coupee = interrupteurs_coupes(fiche)
        if coupee is not None:
            taches.append({"fiches": {nom: coupee}, "source": None})
            communes.append(("interrupteur", len(taches) - 1))
        de_la_fiche[nom] = communes
        for version in [v.get("id") for v in fiche.get("versions") or []] or [None]:
            propres = []
            if version is not None:
                mutee = version_mutee(fiche, version)
                if mutee is not None:
                    taches.append({"fiches": {nom: mutee}, "source": None})
                    propres.append(("parametres", len(taches) - 1))
            plan[(nom, version)] = propres + communes
    rendus = list(executer(taches))
    paquet_de_base, temoins_de_base = rendus[0]
    sortie = {}
    for partie, mutations in plan.items():
        etat = {"fiche": partie[0], "version": partie[1], "etat": "hors_d_atteinte",
                "mutation": None, "temoins": [], "changes": 0, "refusee": False}
        for sorte, indice in mutations:
            paquet, temoins = rendus[indice]
            if isinstance(paquet, str) and paquet.startswith("refus"):
                etat["refusee"] = True
                continue
            if paquet is None or paquet == paquet_de_base or temoins is None:
                continue
            changes = sorted(cle for cle in temoins_de_base
                             if temoins.get(cle) != temoins_de_base[cle])
            if changes:
                etat.update(etat="gardee", mutation=sorte, temoins=changes[:5],
                            changes=len(changes))
                break
            etat.update(etat="non_gardee", mutation=sorte)
        sortie[partie] = etat
    return sortie
