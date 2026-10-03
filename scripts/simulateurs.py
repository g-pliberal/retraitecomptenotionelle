"""Saisir un simulateur officiel, peu et bien : le budget, la feuille, la transcription.

Les simulateurs anonymes des caisses disent le droit tel qu'elles l'appliquent.
`docs/architecture.md` (§ 3.5) les fait interroger une saisie par borne, dans un
budget tenu au registre des sources (`data/sources_a_explorer.yaml`), par une
personne ou par Claude sous le contrôle du propriétaire — jamais par un robot.
Ce script ne va sur aucun site : il fait tout ce qui entoure la saisie.

    python scripts/simulateurs.py budget
    python scripts/simulateurs.py fiche union_retraite_age_depart --sortie feuille.yaml
    python scripts/simulateurs.py transcrire feuille.yaml [--essai]

`fiche` écrit la feuille de saisie : les entrées à taper, d'abord celles
qu'aucun exemple officiel ne couvre encore, les générations les plus jeunes en
tête, jusqu'au budget restant ; et, pour chacune, la PRÉDICTION du modèle,
écrite avant la réponse. La feuille va hors du dépôt, dans le répertoire de la
session : les réponses brutes n'y entrent pas.

`transcrire` fait de chaque réponse collée un exemple officiel
(`tests/temoins/exemples_officiels.yaml`), et le rejoue aussitôt contre le
scénario 1, par les fonctions mêmes de `tests/test_oracle.py` : un écart s'y lit
tout de suite, et ne s'accepte jamais en silence (§ 3.3). La lecture de chaque
réponse — l'âge, la durée — se fait seule quand la réponse n'en porte qu'une ;
sinon elle s'écrit dans `lu`, et chacun de ses nombres doit se retrouver dans
la réponse. Le script demande pytest, qu'importe le module de l'oracle.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
REGISTRE = RACINE / "data" / "sources_a_explorer.yaml"
EXEMPLES = RACINE / "tests" / "temoins" / "exemples_officiels.yaml"
ORACLE = RACINE / "tests" / "test_oracle.py"

sys.path.insert(0, str(RACINE / "src"))

#: Le budget qu'un simulateur reçoit à sa première saisie, avant que le
#: propriétaire ne le change dans le registre : le quart des entrées que son
#: formulaire offre quand il en offre un nombre fini, dix sinon. Une saisie par
#: borne ne borne rien quand chaque entrée est une borne.
PART_DE_L_ESPACE = 4
BUDGET_ESPACE_OUVERT = 10

#: Un âge comme les simulateurs l'écrivent : « 62 ans et 9 mois », « 64 ans ».
_AGE = re.compile(r"(\d{2})\s+ans(?:\s+et\s+(\d{1,2})\s+mois)?")
#: Une durée d'assurance : « 172 trimestres ».
_DUREE = re.compile(r"(\d{3})\s+trimestres")


class Refus(Exception):
    """Ce que le script refuse de faire, et pourquoi."""


# ---------------------------------------------------------------------------
# Le registre et les exemples
# ---------------------------------------------------------------------------

def registre(chemin: Path = REGISTRE) -> dict[str, dict]:
    """Les lignes du registre des sources, par identifiant."""
    sources = yaml.safe_load(chemin.read_text(encoding="utf-8"))["sources"]
    return {source["id"]: source for source in sources}


def exemples(chemin: Path = EXEMPLES) -> list[dict]:
    return yaml.safe_load(chemin.read_text(encoding="utf-8"))["exemples"]


def saisies(simulateur: str, tous: list[dict]) -> dict[str, list[str]]:
    """Les saisies déjà faites dans un simulateur, et les exemples que chacune a
    donnés. Le budget compte les SAISIES : une réponse qui coupe une année en
    trois donne trois exemples pour une saisie."""
    faites: dict[str, list[str]] = {}
    for exemple in tous:
        source = exemple["source"]
        if source.get("simulateur") == simulateur:
            faites.setdefault(str(source["saisie"]), []).append(exemple["id"])
    return faites


def budget_par_defaut(espace: int | None) -> int:
    if espace is None:
        return BUDGET_ESPACE_OUVERT
    return math.ceil(espace / PART_DE_L_ESPACE)


# ---------------------------------------------------------------------------
# Les âges et les dates
# ---------------------------------------------------------------------------

def _plat(texte: str) -> str:
    """Le texte sans ses espaces insécables ni ses retours à la ligne."""
    return re.sub(r"\s+", " ", texte.replace(" ", " ").replace(" ", " ")).strip()


def age_lu(texte: str) -> tuple[int, int]:
    """« 62 ans et 9 mois » en (62, 9)."""
    trouve = _AGE.fullmatch(_plat(texte))
    if not trouve:
        raise Refus(f"« {texte} » n'est pas un âge écrit « N ans » ou « N ans et M mois »")
    return int(trouve[1]), int(trouve[2] or 0)


def age_ecrit(age: float) -> str:
    """62,75 en « 62 ans et 9 mois », comme les simulateurs l'écrivent."""
    ans = int(age + 1e-9)
    mois = round((age - ans) * 12)
    return f"{ans} ans" if mois == 0 else f"{ans} ans et {mois} mois"


def mois_de(periode: str) -> list[tuple[int, int]]:
    """Les mois de naissance d'une période : « 1966 », ou « 1965-04..1965-12 »."""
    if ".." not in periode:
        annee = int(periode)
        return [(annee, mois) for mois in range(1, 13)]
    debut, fin = (tuple(int(x) for x in borne.split("-")) for borne in periode.split(".."))
    rang, dernier = debut[0] * 12 + debut[1] - 1, fin[0] * 12 + fin[1] - 1
    return [(r // 12, r % 12 + 1) for r in range(rang, dernier + 1)]


MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")


def en_lettres(date: str) -> str:
    """« 1969-06-15 » en « 15 juin 1969 », « 1984-01 » en « janvier 1984 »."""
    parties = [int(x) for x in date.split("-")]
    mois = f"{MOIS[parties[1] - 1]} {parties[0]}"
    if len(parties) == 2:
        return mois
    return f"{'1er' if parties[2] == 1 else parties[2]} {mois}"


def periode_de(premier: tuple[int, int], dernier: tuple[int, int]) -> str:
    if premier[1] == 1 and dernier[1] == 12 and premier[0] == dernier[0]:
        return str(premier[0])
    return f"{premier[0]}-{premier[1]:02d}..{dernier[0]}-{dernier[1]:02d}"


def representant(periode: str, jour: int) -> dt.date:
    """La naissance qui représente une période : son mois du milieu, au jour dit."""
    mois = mois_de(periode)
    annee, m = mois[(len(mois) - 1) // 2]
    return dt.date(annee, m, jour)


def date_d_effet(naissance: dt.date, ans: int, mois: int) -> str:
    """Le premier mois où la pension peut prendre effet à cet âge : celui qui
    suit l'anniversaire, ou celui-ci pour qui est né un 1er (R. 351-37)."""
    rang = naissance.year * 12 + naissance.month - 1 + ans * 12 + mois
    if naissance.day != 1:
        rang += 1
    annee, m = divmod(rang, 12)
    return f"{annee}-{m + 1:02d}"


def grandeur_d_age(naissance: dt.date, ans: int, mois: int) -> dict:
    """L'âge publié, en la grandeur qui le compare sans arrondi : l'âge lui-même
    quand il tombe au trimestre, sinon la date d'effet qu'il ouvre — les tables
    portent 60,67 pour 60 ans et 8 mois (`ur_racl_1965_decembre`)."""
    if mois % 3 == 0:
        return {"age_ouverture": ans + mois / 12}
    return {"date_effet_au_plus_tot": date_d_effet(naissance, ans, mois)}


# ---------------------------------------------------------------------------
# Les simulateurs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Cas:
    """Une saisie : ce qu'on tape, champ par champ, et les naissances que sa
    réponse couvre."""

    saisie: tuple[tuple[str, str], ...]
    periode: str
    generation: int

    @property
    def cle(self) -> str:
        return " ; ".join(valeur for _, valeur in self.saisie)


class Adaptateur:
    """Ce qu'un simulateur demande, et comment sa réponse devient un exemple.

    `espace` est le nombre d'entrées que son formulaire offre, None s'il est
    ouvert ; `jour`, celui de la naissance qui représente une période ;
    `attendu`, les grandeurs que l'exemple compare."""

    simulateur: str
    intitule: str
    espace: int | None
    jour: int

    def cas(self) -> list[Cas]:
        raise NotImplementedError

    def couvertes(self, tous: list[dict]) -> set[int]:
        """Les générations qu'un exemple officiel couvre déjà, pour la règle que
        le simulateur exerce."""
        raise NotImplementedError

    def carriere(self, cas: Cas, periode: str, ans: int, mois: int) -> dict:
        raise NotImplementedError

    def attendu(self, naissance: dt.date, ans: int, mois: int,
                trimestres: int | None) -> dict:
        raise NotImplementedError

    def identifiant(self, cas: Cas, periode: str) -> str:
        raise NotImplementedError

    def decrire(self, carriere: dict) -> str:
        raise NotImplementedError

    def lire(self, cas: Cas, reponse: str) -> list[dict] | None:
        """La lecture d'une réponse qui ne porte qu'un âge : la seule qui se
        fasse seule. Plusieurs âges veulent une lecture écrite à la main."""
        texte = _plat(reponse)
        ages = {(int(a), int(m or 0)) for a, m in _AGE.findall(texte)}
        durees = self._durees(texte)
        if len(ages) != 1 or len(durees) > 1:
            return None
        ((ans, mois),) = ages
        lu = {"periode": cas.periode, "age": age_ecrit(ans + mois / 12)}
        if durees:
            lu["trimestres"] = durees[0]
        return [lu]

    def _durees(self, texte: str) -> list[int]:
        return sorted({int(n) for n in _DUREE.findall(texte)})

    def predire(self, contexte: "Contexte", cas: Cas) -> list[dict]:
        raise NotImplementedError


def _slug(periode: str) -> str:
    return periode.replace("..", "_").replace("-", "_")


class AgeLegal(Adaptateur):
    """« Âge légal de départ à la retraite » : l'année de naissance seule."""

    simulateur = "union_retraite_age_depart"
    intitule = "simulateur « Âge légal de départ à la retraite », info-retraite.fr"
    jour = 15  # la présomption, quand la naissance ne dit pas son jour
    ANNEES = tuple(range(1962, 1970))
    espace = len(ANNEES)
    CHAMP = "Votre année de naissance"

    def cas(self) -> list[Cas]:
        return [Cas(((self.CHAMP, "1969 et après" if annee == 1969 else str(annee)),),
                    str(annee), annee)
                for annee in self.ANNEES]

    def couvertes(self, tous: list[dict]) -> set[int]:
        return {int(str(e["carriere"]["naissance"])[:4]) for e in tous
                if {"age_ouverture", "date_age_legal", "date_effet_au_plus_tot"}
                & set(e["attendu"])
                and e["attendu"].get("motif_ouverture") != "carriere_longue"
                and "naissance" in e.get("carriere", {})}

    def carriere(self, cas: Cas, periode: str, ans: int, mois: int) -> dict:
        naissance = representant(periode, self.jour)
        return {"naissance": naissance.isoformat(), "sexe": "H",
                "affiliation": "salarie_prive_non_cadre",
                "liquidation": date_d_effet(naissance, 67, 0), "age_debut": 22}

    def attendu(self, naissance, ans, mois, trimestres) -> dict:
        attendu = grandeur_d_age(naissance, ans, mois)
        if trimestres is not None:
            attendu["trimestres_requis"] = trimestres
        return attendu

    def identifiant(self, cas: Cas, periode: str) -> str:
        return f"ur_age_legal_{_slug(periode)}"

    def lire(self, cas: Cas, reponse: str) -> list[dict] | None:
        """« Votre âge légal de départ* à la retraite est 63 ans et 9 mois. […]
        Le nombre de trimestres requis pour votre départ à taux plein est de
        172. Vous aurez atteint l'âge du taux plein automatique** à 67 ans. » :
        l'âge du taux plein automatique n'est pas l'âge légal, et la durée ne
        s'écrit pas « 172 trimestres »."""
        texte = _plat(reponse)
        ages = re.findall(r"âge légal de départ\**\s+à la retraite est "
                          r"(\d{2}) ans(?: et (\d{1,2}) mois)?", texte)
        durees = re.findall(r"trimestres requis pour votre départ à taux plein est de "
                            r"(\d{3})", texte)
        if len(ages) != 1 or len(durees) > 1:
            return None
        ((ans, mois),) = ages
        lu = {"periode": cas.periode, "age": age_ecrit(int(ans) + int(mois or 0) / 12)}
        if durees:
            lu["trimestres"] = int(durees[0])
        return [lu]

    def decrire(self, carriere: dict) -> str:
        return (f"La carrière d'exemple : un salarié du secteur privé né le "
                f"{en_lettres(carriere['naissance'])}, entré à vingt-deux ans et parti "
                "à soixante-sept ; seuls se comparent l'âge légal et la durée requise.")

    def predire(self, contexte: "Contexte", cas: Cas) -> list[dict]:
        """L'âge et la durée du modèle, mois de naissance par mois : la réponse
        d'une année que le modèle coupe se prédit coupée."""
        lectures = []
        for annee, mois in mois_de(cas.periode):
            periode = f"{annee}-{mois:02d}..{annee}-{mois:02d}"
            carriere = self.carriere(cas, periode, 67, 0)
            age, trimestres = contexte.mesurer(carriere, ("age_ouverture", "trimestres_requis"))
            lectures.append(((annee, mois), age_ecrit(age), trimestres))
        return _regrouper(lectures)


class CarriereLongue(Adaptateur):
    """« Départ anticipé pour carrière longue » : l'année de naissance, et l'âge
    avant lequel on a commencé à travailler."""

    simulateur = "union_retraite_carriere_longue"
    intitule = ("simulateur de départ anticipé pour carrière longue, "
                "info-retraite.fr")
    jour = 1  # né un 1er : le départ tombe au mois même de l'âge
    ANNEES = tuple(range(1964, 1971))
    BORNES = (16, 18, 20, 21)
    espace = len(ANNEES) * len(BORNES)
    #: L'année où la carrière d'exemple commence, comptée depuis la naissance :
    #: quatre trimestres seulement à la fin de l'année de la borne d'en dessous,
    #: assez pour la borne visée, et la durée requise atteinte au départ.
    DEBUT = {16: 15, 18: 16, 20: 18, 21: 20}

    def cas(self) -> list[Cas]:
        return [Cas((("Votre année de naissance", str(annee)),
                     ("Vous avez commencé à travailler avant", f"{borne} ans")),
                    str(annee), annee)
                for annee in self.ANNEES for borne in self.BORNES]

    def couvertes(self, tous: list[dict]) -> set[int]:
        return {int(str(e["carriere"]["naissance"])[:4]) for e in tous
                if e["attendu"].get("motif_ouverture") == "carriere_longue"}

    def _borne(self, cas: Cas) -> int:
        return int(dict(cas.saisie)["Vous avez commencé à travailler avant"].split()[0])

    def carriere(self, cas: Cas, periode: str, ans: int, mois: int) -> dict:
        naissance = representant(periode, self.jour)
        if naissance.month >= 10:
            raise Refus(
                f"{periode} : une naissance d'octobre à décembre n'a besoin que de "
                "quatre trimestres avant la borne, et la carrière d'exemple ne sait "
                "pas encore l'y placer ; cet exemple s'écrit à la main")
        return {"naissance": naissance.isoformat(), "sexe": "H",
                "affiliation": "salarie_prive_non_cadre",
                "liquidation": date_d_effet(naissance, ans, mois),
                "debut": f"{naissance.year + self.DEBUT[self._borne(cas)]}-01"}

    def attendu(self, naissance, ans, mois, trimestres) -> dict:
        attendu = grandeur_d_age(naissance, ans, mois)
        if trimestres is not None:
            attendu["trimestres_requis"] = trimestres
        attendu.update(motif_ouverture="carriere_longue", liquidation_ouverte=True,
                       non_ouverte_un_trimestre_plus_tot=True)
        return attendu

    def identifiant(self, cas: Cas, periode: str) -> str:
        return f"ur_racl_{_slug(periode)}_avant_{self._borne(cas)}"

    def decrire(self, carriere: dict) -> str:
        return (f"La carrière d'exemple : un salarié du secteur privé né le "
                f"{en_lettres(carriere['naissance'])}, au travail depuis "
                f"{en_lettres(carriere['debut'])}, qui part au premier mois que la "
                "réponse lui ouvre.")

    def _durees(self, texte: str) -> list[int]:
        # « au moins 172 trimestres et au moins 5 trimestres avant la fin de
        # l'année » : la durée est la première, les autres sont la borne.
        premiere = re.search(r"au moins (\d{3}) trimestres", texte)
        return [int(premiere[1])] if premiere else []

    def predire(self, contexte: "Contexte", cas: Cas) -> list[dict]:
        provisoire = self.carriere(cas, cas.periode, 67, 0)
        (age,) = contexte.mesurer(provisoire, ("age_ouverture",))
        ans, mois = int(age + 1e-9), round((age - int(age + 1e-9)) * 12)
        carriere = self.carriere(cas, cas.periode, ans, mois)
        trimestres, motif = contexte.mesurer(carriere, ("trimestres_requis", "motif_ouverture"))
        lu = {"periode": cas.periode, "age": age_ecrit(age), "trimestres": trimestres}
        if motif != "carriere_longue":
            lu["motif"] = motif
        return [lu]


def _regrouper(lectures: list) -> list[dict]:
    """Les mois consécutifs qui rendent la même réponse forment une période."""
    groupes: list[list] = []
    for mois, age, trimestres in lectures:
        if groupes and groupes[-1][2:] == [age, trimestres]:
            groupes[-1][1] = mois
        else:
            groupes.append([mois, mois, age, trimestres])
    return [{"periode": periode_de(premier, dernier), "age": age, "trimestres": trimestres}
            for premier, dernier, age, trimestres in groupes]


ADAPTATEURS = {adaptateur.simulateur: adaptateur
               for adaptateur in (AgeLegal(), CarriereLongue())}


# ---------------------------------------------------------------------------
# Le modèle, par l'oracle
# ---------------------------------------------------------------------------

class Contexte:
    """Le scénario 1, interrogé comme `tests/test_oracle.py` l'interroge."""

    def __init__(self):
        spec = importlib.util.spec_from_file_location("oracle_des_simulateurs", ORACLE)
        self.oracle = importlib.util.module_from_spec(spec)
        sys.modules.setdefault(spec.name, self.oracle)
        spec.loader.exec_module(self.oracle)
        from retraite_notionnelle.config import Parametres
        from retraite_notionnelle.simulateur import Simulateur

        self.simulateur = Simulateur(Parametres())

    def mesurer(self, carriere: dict, cles: tuple[str, ...]) -> tuple:
        exemple = {"id": "prediction", "carriere": carriere, "attendu": {}}
        construite, resultat = self.oracle._carriere_exemple(self.simulateur, exemple)
        return tuple(self.oracle._mesurer(self.simulateur, exemple, construite, resultat, cle)
                     for cle in cles)

    def confronter(self, exemple: dict) -> list[tuple]:
        return self.oracle._confronter(self.simulateur, exemple)


# ---------------------------------------------------------------------------
# Le budget et la feuille
# ---------------------------------------------------------------------------

def etat_des_budgets(lignes: dict[str, dict], tous: list[dict]) -> list[tuple]:
    """Par simulateur du registre : son budget, ses saisies, ce qui reste."""
    etat = []
    for identifiant, ligne in lignes.items():
        if ligne["nature"] != "simulateur":
            continue
        faites = len(saisies(identifiant, tous))
        budget = ligne.get("budget")
        etat.append((identifiant, budget, faites,
                     None if budget is None else budget - faites))
    return etat


def a_saisir(adaptateur: Adaptateur, lignes: dict[str, dict], tous: list[dict]) -> list[Cas]:
    """Les saisies de la prochaine feuille : jamais une saisie déjà faite ;
    d'abord les générations qu'aucun exemple officiel ne couvre, les plus jeunes
    en tête ; jusqu'au budget restant."""
    ligne = lignes.get(adaptateur.simulateur)
    if ligne is None:
        raise Refus(f"{adaptateur.simulateur} n'est pas au registre des sources")
    if ligne.get("budget") is None:
        raise Refus(
            f"{adaptateur.simulateur} n'a pas de budget au registre : le lui donner "
            f"d'abord — par défaut {budget_par_defaut(adaptateur.espace)}, le quart "
            "de ses entrées (docs/exploration_sources.md)")
    faites = saisies(adaptateur.simulateur, tous)
    reste = ligne["budget"] - len(faites)
    if reste <= 0:
        raise Refus(f"{adaptateur.simulateur} : budget épuisé ({len(faites)} saisies "
                    f"pour {ligne['budget']})")
    couvertes = adaptateur.couvertes(tous)
    candidats = [cas for cas in adaptateur.cas() if cas.cle not in faites]
    candidats.sort(key=lambda cas: (cas.generation in couvertes, -cas.generation))
    return candidats[:reste]


def feuille(adaptateur: Adaptateur, cas: list[Cas], contexte: Contexte,
            lignes: dict[str, dict], tous: list[dict], aujourd_hui: dt.date) -> str:
    """La feuille de saisie, en YAML commenté."""
    ligne = lignes[adaptateur.simulateur]
    faites = len(saisies(adaptateur.simulateur, tous))
    donnees = {
        "simulateur": adaptateur.simulateur,
        "adresse": ligne["url"],
        "preparee_le": aujourd_hui.isoformat(),
        "saisie_le": None,
        "cas": [{"saisie": dict(c.saisie),
                 "prediction": adaptateur.predire(contexte, c),
                 "reponse": None, "lu": None} for c in cas],
    }
    entete = [
        f"# Feuille de saisie : {adaptateur.intitule}",
        f"# Budget : {ligne['budget']} saisies, {faites} faites, {len(cas)} sur cette feuille.",
        "#",
        "# La prédiction est celle du modèle, écrite AVANT la réponse.",
        "# Pour chaque cas : taper `saisie` dans le simulateur, coller la réponse",
        "# telle quelle dans `reponse` ; écrire `lu` seulement si la réponse ne se",
        "# lit pas seule (une liste de {periode, age, trimestres}). Dater",
        "# `saisie_le`, puis :",
        "#     python scripts/simulateurs.py transcrire <ce fichier>",
        "# Claude ne saisit qu'un lot approuvé par le propriétaire, une entrée à la",
        "# fois, et s'arrête au premier captcha ou écran inattendu",
        "# (docs/architecture.md, § 3.5).",
    ]
    corps = yaml.safe_dump(donnees, allow_unicode=True, sort_keys=False, width=88)
    return "\n".join(entete) + "\n" + corps


# ---------------------------------------------------------------------------
# La transcription
# ---------------------------------------------------------------------------

def _scalaire(valeur) -> str:
    if valeur is True:
        return "true"
    if valeur is False:
        return "false"
    if isinstance(valeur, (int, float)):
        return repr(valeur)
    texte = str(valeur)
    if re.fullmatch(r"[a-z_][a-z0-9_]*|[A-Z]", texte) and texte not in {
            "y", "n", "yes", "no", "on", "off", "true", "false", "null"}:
        return texte
    return json.dumps(texte, ensure_ascii=False)


def _en_ligne(valeurs: dict) -> str:
    return "{" + ", ".join(f"{cle}: {_scalaire(v)}" for cle, v in valeurs.items()) + "}"


def _plie(texte: str, retrait: str = "      ", largeur: int = 78) -> list[str]:
    lignes, ligne = [], ""
    for mot in texte.split():
        if ligne and len(retrait) + len(ligne) + 1 + len(mot) > largeur:
            lignes.append(retrait + ligne)
            ligne = mot
        else:
            ligne = f"{ligne} {mot}" if ligne else mot
    if ligne:
        lignes.append(retrait + ligne)
    return lignes


def bloc(exemple: dict) -> str:
    """Un exemple écrit comme les autres du fichier : en ligne, et l'énoncé plié."""
    lignes = [f"  - id: {exemple['id']}",
              f"    source: {_en_ligne(exemple['source'])}",
              "    enonce: >-",
              *_plie(exemple["enonce"]),
              f"    carriere: {_en_ligne(exemple['carriere'])}",
              f"    attendu: {_en_ligne(exemple['attendu'])}"]
    return "\n".join(lignes) + "\n"


def _verifier_lecture(lu: dict, reponse: str) -> None:
    """Chaque nombre lu se retrouve dans la réponse : la lecture ne s'invente pas."""
    texte = _plat(reponse)
    if _plat(lu["age"]) not in texte:
        raise Refus(f"l'âge lu « {lu['age']} » n'est pas dans la réponse")
    if lu.get("trimestres") is not None and not re.search(
            rf"\b{int(lu['trimestres'])}\b", texte):
        raise Refus(f"la durée lue, {lu['trimestres']} trimestres, n'est pas dans la réponse")


def exemples_de_la_feuille(donnees: dict, lignes: dict[str, dict],
                           tous: list[dict]) -> list[dict]:
    """Les exemples que donnent les réponses remplies d'une feuille."""
    adaptateur = ADAPTATEURS.get(donnees["simulateur"])
    if adaptateur is None:
        raise Refus(f"aucun adaptateur pour {donnees['simulateur']}")
    saisie_le = donnees.get("saisie_le")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(saisie_le or "")):
        raise Refus("la feuille ne date pas sa saisie (`saisie_le`)")
    faites = saisies(adaptateur.simulateur, tous)
    deja = {e["id"] for e in tous}
    nouveaux, cles = [], set()
    for rang, entree in enumerate(donnees["cas"], start=1):
        if not entree.get("reponse"):
            continue
        cas = next((c for c in adaptateur.cas() if dict(c.saisie) == entree["saisie"]), None)
        if cas is None:
            raise Refus(f"cas {rang} : {entree['saisie']} n'est pas une entrée du simulateur")
        if cas.cle in faites:
            raise Refus(f"cas {rang} : la saisie « {cas.cle} » est déjà transcrite")
        reponse = _plat(str(entree["reponse"]))
        lectures = entree.get("lu") or adaptateur.lire(cas, reponse)
        if not lectures:
            raise Refus(f"cas {rang} : la réponse ne se lit pas seule — plusieurs âges, ou "
                        "aucun là où le simulateur l'écrit ; écrire `lu`")
        cles.add(cas.cle)
        for lu in lectures:
            _verifier_lecture(lu, reponse)
            ans, mois = age_lu(lu["age"])
            periode = str(lu.get("periode") or cas.periode)
            carriere = adaptateur.carriere(cas, periode, ans, mois)
            naissance = dt.date.fromisoformat(carriere["naissance"])
            exemple = {
                "id": adaptateur.identifiant(cas, periode),
                "source": {"editeur": "Union Retraite",
                           "reference": f"{adaptateur.intitule}, saisie « {cas.cle} »",
                           "verifie_le": str(saisie_le),
                           "simulateur": adaptateur.simulateur, "saisie": cas.cle},
                "enonce": f"« {reponse} » {adaptateur.decrire(carriere)}",
                "carriere": carriere,
                "attendu": adaptateur.attendu(naissance, ans, mois, lu.get("trimestres")),
            }
            if exemple["id"] in deja or any(e["id"] == exemple["id"] for e in nouveaux):
                raise Refus(f"cas {rang} : l'exemple {exemple['id']} existe déjà")
            nouveaux.append(exemple)
    budget = lignes[adaptateur.simulateur].get("budget")
    if budget is None or len(faites) + len(cles) > budget:
        raise Refus(f"{adaptateur.simulateur} : {len(faites) + len(cles)} saisies "
                    f"dépasseraient le budget ({budget})")
    return nouveaux


def ecrire(nouveaux: list[dict], chemin: Path = EXEMPLES) -> None:
    """Ajoute les exemples à la fin du fichier, puis vérifie qu'il se relit à
    l'identique."""
    texte = chemin.read_text(encoding="utf-8")
    if not texte.endswith("\n"):
        texte += "\n"
    for exemple in nouveaux:
        texte += "\n" + bloc(exemple)
    chemin.write_text(texte, encoding="utf-8", newline="\n")
    relus = {e["id"]: e for e in exemples(chemin)}
    for exemple in nouveaux:
        if relus.get(exemple["id"]) != exemple:
            raise Refus(f"{exemple['id']} ne se relit pas comme il a été écrit")


# ---------------------------------------------------------------------------
# La ligne de commande
# ---------------------------------------------------------------------------

def main(arguments: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # la console de Windows lit cp1252
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    lecteur.add_argument("--registre", type=Path, default=REGISTRE)
    lecteur.add_argument("--exemples", type=Path, default=EXEMPLES)
    commandes = lecteur.add_subparsers(dest="commande", required=True)
    commandes.add_parser("budget", help="le budget de chaque simulateur")
    fiche = commandes.add_parser("fiche", help="la feuille de saisie d'un simulateur")
    fiche.add_argument("simulateur", choices=sorted(ADAPTATEURS))
    fiche.add_argument("--sortie", type=Path, help="où l'écrire, hors du dépôt")
    transcrire = commandes.add_parser("transcrire", help="les réponses en exemples")
    transcrire.add_argument("feuille", type=Path)
    transcrire.add_argument("--essai", action="store_true",
                            help="montrer les exemples sans les écrire")
    options = lecteur.parse_args(arguments)

    lignes, tous = registre(options.registre), exemples(options.exemples)
    try:
        if options.commande == "budget":
            for identifiant, budget, faites, reste in etat_des_budgets(lignes, tous):
                print(f"{identifiant:42} budget {budget if budget is not None else '—':>3}"
                      f"  saisies {faites:>3}  reste {reste if reste is not None else '—':>3}")
            return 0
        if options.commande == "fiche":
            adaptateur = ADAPTATEURS[options.simulateur]
            cas = a_saisir(adaptateur, lignes, tous)
            texte = feuille(adaptateur, cas, Contexte(), lignes, tous, dt.date.today())
            if options.sortie:
                options.sortie.write_text(texte, encoding="utf-8", newline="\n")
                print(f"{len(cas)} saisies : {options.sortie}")
            else:
                print(texte)
            return 0
        donnees = yaml.safe_load(options.feuille.read_text(encoding="utf-8"))
        nouveaux = exemples_de_la_feuille(donnees, lignes, tous)
        if not nouveaux:
            print("aucune réponse remplie")
            return 0
        if options.essai:
            for exemple in nouveaux:
                print(bloc(exemple))
            return 0
        ecrire(nouveaux, options.exemples)
        contexte, ecarts = Contexte(), 0
        for exemple in nouveaux:
            problemes = contexte.confronter(exemple)
            ecarts += bool(problemes)
            print(f"{exemple['id']:40} "
                  + ("concorde" if not problemes else f"ÉCART : {problemes}"))
        if ecarts:
            print(f"\n{ecarts} écart(s) : corriger le modèle, ou déclarer l'écart connu "
                  "avec la fiche et le texte qui tranche (docs/architecture.md, § 3.3).")
        return 1 if ecarts else 0
    except Refus as refus:
        print(f"refusé : {refus}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
