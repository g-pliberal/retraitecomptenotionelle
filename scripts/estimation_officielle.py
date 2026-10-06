"""Confronter une carrière réelle à « Mon estimation retraite », âge par âge.

« Mon estimation retraite » (info-retraite.fr) est le seul simulateur officiel
qui chiffre une pension entière : brut mensuel, par régime, pour chaque âge de
départ, les points comptés à leur valeur actuelle. Elle se lit derrière
FranceConnect, sur la carrière réelle de l'assuré : c'est la troisième voie de
`docs/architecture.md` (§ 3.5). Le propriétaire s'y connecte lui-même ; Claude
peut en lire la page, et n'y change une hypothèse qu'avec son accord.

    python scripts/estimation_officielle.py --modele > ~/estimation.yaml
    python scripts/estimation_officielle.py --releve ~/releve.pdf --estimation ~/estimation.yaml

`--releve` lit le relevé de carrière que l'assuré a téléchargé : le PDF par
`scripts/fetch/lecture_pdf.py`, ou ses lignes de texte, puis
`web/releve_lu.lire_releve`, qui en rend la saisie du simulateur.
`--estimation` lit ce que la caisse affiche, recopié âge par âge dans le
gabarit que `--modele` imprime, avec la convention de la page mot pour mot.
Pour chaque âge, le scénario 1 est liquidé à la même date, ramené à la même
convention — brut mensuel, euros de l'année de la page — régime par régime,
puis étage par étage, et l'écart se dit en euros et en pour cent.

**Les revenus à venir.** Le relevé s'arrête à sa dernière année ; l'estimation
suppose une activité jusqu'au départ, à partir du revenu qu'elle prête à la
situation actuelle (`convention.revenu_annuel`, en euros de la page), à défaut
de celui de la dernière année du relevé. `--revenus-futurs` dit comment le
poursuivre : `salaire_moyen` (par défaut) le fait suivre le salaire moyen,
comme `Carriere.prolongee`, ce qui est au plus près de l'« évolution régulière
de vos revenus » que la page applique par défaut (lue le 4 octobre 2026) ;
`prix` le garde constant en euros ; `aucun` s'arrête au relevé, pour qui ne
travaille plus.

**Ce que le relevé porte, et ce qu'il ne porte pas.** Le relevé du seul régime
général porte un revenu PLAFONNÉ, et les points Agirc-Arrco n'y servent que
d'indice du statut cadre (`web/releve_lu.py`) : une année au plafond minore la
complémentaire du modèle sans qu'aucune règle n'y soit pour rien. Le relevé
tous régimes d'info-retraite, lui, porte le « revenu d'activité soumis à
cotisations retraite », plafond franchi compris. Le script dit lequel des deux
il a lu, avant le tableau. Une année que la lecture a mal lue se corrige à la
main dans l'estimation (`releve.corrections`), d'après le relevé lui-même, et
le rapport le dit.

**Rien de personnel n'entre au dépôt.** Le script n'écrit aucun fichier : il
imprime. Il refuse un relevé ou une estimation rangés dans un dépôt git sans y
être ignorés, et c'est hors du dépôt, dans le répertoire de la session, que
ces deux fichiers se tiennent. Seuls l'écart trouvé et la règle qu'il met en
cause se consignent, dans la feuille de route.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "scripts" / "fetch"))

from retraite_notionnelle.somme import somme_ordonnee
from retraite_notionnelle.calendrier import MOIS_PAR_AN  # noqa: E402
from retraite_notionnelle.carriere import salaire_moyen_annuel  # noqa: E402
from retraite_notionnelle.contexte import Contexte  # noqa: E402
from retraite_notionnelle.donnees.chargement import (  # noqa: E402
    charger_periodes_non_travaillees,
)
from retraite_notionnelle.saisie import ErreurSaisie, Saisie  # noqa: E402
from retraite_notionnelle.web.releve_lu import Lecture, arrondi, lire_releve  # noqa: E402

#: Les étages d'une pension du système 1, dans l'ordre où le site les écrit
#: (`ETAGES_ACTUEL` de `moteur/js/pages.js`) : le régime intégré tient lieu de
#: la base.
ETAGES = (
    ("integre", "régime intégré"),
    ("base", "retraite de base"),
    ("complementaire", "retraite complémentaire"),
    ("additionnel", "retraite additionnelle"),
)

#: Les régimes du modèle que nomme chaque ligne de l'estimation, quand la
#: recopie ne les dit pas (`codes`). La page nomme la caisse qui paie : la
#: liquidation unique des régimes alignés fait servir par l'Assurance retraite
#: les années d'indépendant d'avant 2020, et l'Agirc-Arrco sert les points
#: Arrco et Agirc d'avant leur fusion de 2019 avec les siens.
ALIAS = {
    "assurance retraite": ("regime_general", "rsi", "organic", "cancava"),
    "l assurance retraite": ("regime_general", "rsi", "organic", "cancava"),
    "regime general": ("regime_general", "rsi", "organic", "cancava"),
    "cnav": ("regime_general", "rsi", "organic", "cancava"),
    "carsat": ("regime_general", "rsi", "organic", "cancava"),
    "agirc arrco": ("agirc_arrco", "agirc", "arrco", "arrco_tranche_2",
                    "agirc_entreprises_nouvelles",
                    "arrco_tranche_2_entreprises_nouvelles", "arrco_cultes"),
    "ircantec": ("ircantec",),
    "service des retraites de l etat": ("fonction_publique_etat",),
    "sre": ("fonction_publique_etat",),
    "rafp": ("rafp",),
    "retraite additionnelle de la fonction publique": ("rafp",),
    "cnracl": ("cnracl",),
    "msa": ("msa_salaries", "msa_non_salaries"),
    "retraite complementaire des independants": ("rci",),
}

#: Comment le modèle poursuit la carrière après la dernière année du relevé.
REVENUS_FUTURS = {
    "salaire_moyen": "au rythme du salaire moyen, comme Carriere.prolongee",
    "prix": "constants en euros",
    "aucun": "aucun : la carrière s'arrête à la dernière année du relevé",
}

#: Un revenu du régime général à un pour cent du plafond de la Sécurité sociale
#: près est réputé plafonné : le relevé n'en porte pas le dépassement. Au-delà,
#: le relevé porte le revenu entier.
TOLERANCE_DU_PLAFOND = 0.01

#: Les statuts dont un relevé du régime général porte le revenu plafonné : le
#: salarié du privé, et le contractuel public, que le régime général couvre
#: aussi — la lecture du relevé le reconnaît à l'Ircantec.
STATUTS_PLAFONNES = ("salarie_prive_non_cadre", "salarie_prive_cadre",
                     "contractuel_public")

GABARIT = """\
# « Mon estimation retraite » (info-retraite.fr), recopiée le jour de la lecture
# pour scripts/estimation_officielle.py. CE FICHIER EST PERSONNEL : il se range
# hors du dépôt, et le script refuse un chemin du dépôt que git n'ignore pas.
# Les montants se recopient tels que la page les affiche, âge par âge et régime
# par régime ; la convention, mot pour mot.
lu_le: AAAA-MM-JJ
convention:
  # La phrase de la page qui dit ce que sont les montants, mot pour mot.
  texte: ""
  # Ce que dit cette phrase : brut ou net, mensuel ou annuel, euros de quelle
  # année. Le script ne compare que des bruts mensuels.
  montants: brut
  periodicite: mensuel
  euros_de: AAAA
  # L'hypothèse de la page sur les revenus à venir, mot pour mot.
  revenus_futurs: ""
  # Le revenu brut annuel que la page prête à la situation actuelle, s'il y
  # est (« Revenus bruts annuels ») : la carrière à venir part de lui.
  revenu_annuel:
assure:
  # La date de naissance, quand le relevé ne la porte pas en tête.
  naissance: AAAA-MM-JJ
  sexe: H            # H ou F
  enfants: 0         # le nombre d'enfants que l'estimation retient
  # naissances: [AAAA-MM-JJ]   # facultatif : la naissance de chacun
releve:
  # Les années que la lecture du relevé a mal lues, corrigées à la main
  # d'après le relevé lui-même : « année: revenu », en euros de l'année.
  corrections: {}
departs:
  - age: ""          # tel que la page l'écrit : « 62 ans et 9 mois »
    date: AAAA-MM-01 # le premier jour du mois de départ
    trimestres:      # la durée tous régimes que la page annonce, si elle la dit
    regimes:
      # `codes` : les régimes du modèle que la ligne couvre ; facultatif pour
      # les caisses que le script connaît (ALIAS).
      - libelle: Assurance retraite
        codes: [regime_general, rsi, organic, cancava]
        brut:
      - libelle: Agirc-Arrco
        codes: [agirc_arrco, agirc, arrco, arrco_tranche_2]
        brut:
    total_brut:      # le total brut que la page affiche
    net:             # le net qu'elle affiche, pour mémoire
"""


class Refus(Exception):
    """Ce que le script refuse de faire, et pourquoi."""


# ---------------------------------------------------------------------------
# Les fichiers personnels, hors du dépôt
# ---------------------------------------------------------------------------

def _git(dossier: Path, *arguments: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", "-C", str(dossier), *arguments],
                              capture_output=True, text=True, check=False)
    except OSError:
        return None


def hors_du_depot(chemin: Path) -> Path:
    """Le chemin absolu d'un fichier personnel, s'il ne peut pas entrer au dépôt.

    Un fichier rangé dans un dépôt git sans y être ignoré finit par y entrer,
    au premier `git add -A` : il est refusé, AVANT d'être lu. Le dépôt est
    celui où le fichier se trouve, quel qu'il soit — le dossier principal ou
    le worktree d'une session —, et c'est à git de dire s'il l'ignore. Sans
    git, un chemin sous ce dépôt-ci est refusé, faute de pouvoir le vérifier.
    """
    absolu = chemin.expanduser().resolve()
    dossier = absolu.parent
    while not dossier.exists() and dossier != dossier.parent:
        dossier = dossier.parent
    dedans = _git(dossier, "rev-parse", "--is-inside-work-tree")
    if dedans is None:
        if absolu.is_relative_to(RACINE.resolve()):
            raise Refus(f"{chemin} : sous le dépôt, et git est introuvable pour "
                        "dire s'il l'ignore ; le ranger hors du dépôt.")
        return absolu
    if dedans.returncode != 0 or dedans.stdout.strip() != "true":
        return absolu
    ignore = _git(dossier, "check-ignore", "-q", "--", str(absolu))
    if ignore is None or ignore.returncode != 0:
        raise Refus(f"{chemin} : dans un dépôt git sans y être ignoré. Une donnée "
                    "personnelle n'entre pas au dépôt : ranger le fichier hors du "
                    "dépôt, dans le répertoire de la session.")
    return absolu


# ---------------------------------------------------------------------------
# Le relevé
# ---------------------------------------------------------------------------

def lignes_du_releve(chemin: Path) -> list[str]:
    """Les lignes de texte d'un relevé : celles du PDF, ou celles d'un texte collé."""
    octets = chemin.read_bytes()
    if octets.startswith(b"%PDF"):
        from lecture_pdf import lignes_pdf
        return lignes_pdf(octets)
    return octets.decode("utf-8").splitlines()


def lire(chemin: Path) -> Lecture:
    lecture = lire_releve(lignes_du_releve(chemin))
    if lecture.vide:
        raise Refus(f"{chemin} : aucune année de carrière lue. Le relevé est-il un "
                    "PDF de texte, et non une image numérisée ?")
    return lecture


def _par_rapport_au_plafond(lecture: Lecture, plafond) -> list[tuple[int, float]]:
    """Chaque année d'emploi du régime général, et son revenu rapporté au plafond."""
    return [(ligne.annee, ligne.revenu / plafond(ligne.annee)) for ligne in lecture.lignes
            if ligne.statut in STATUTS_PLAFONNES and ligne.motif is None
            and ligne.annee >= plafond.premiere_annee]


def annees_au_plafond(lecture: Lecture, plafond) -> list[int]:
    """Les années où le revenu du régime général est le plafond, à un pour cent
    près : le relevé n'y porte pas ce qui le dépasse."""
    return sorted({annee for annee, part in _par_rapport_au_plafond(lecture, plafond)
                   if abs(part - 1.0) <= TOLERANCE_DU_PLAFOND})


def annees_au_dessus_du_plafond(lecture: Lecture, plafond) -> list[int]:
    """Les années où le revenu dépasse le plafond : ce relevé-là porte le revenu
    entier, et non sa seule part plafonnée."""
    return sorted({annee for annee, part in _par_rapport_au_plafond(lecture, plafond)
                   if part > 1.0 + TOLERANCE_DU_PLAFOND})


# ---------------------------------------------------------------------------
# L'estimation recopiée
# ---------------------------------------------------------------------------

def _plat(texte: str) -> str:
    sans = unicodedata.normalize("NFKD", str(texte))
    sans = "".join(c for c in sans if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", sans).split())


def _date(valeur, nom: str) -> dt.date:
    if isinstance(valeur, dt.date):
        return valeur
    trouve = re.fullmatch(r"(\d{4})-(\d{2})(?:-(\d{2}))?", str(valeur or "").strip())
    if trouve is None:
        raise Refus(f"{nom} : une date AAAA-MM-JJ, à remplir (lu : {valeur!r}).")
    return dt.date(int(trouve[1]), int(trouve[2]), int(trouve[3] or 1))


def _montant(valeur, nom: str) -> float:
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise Refus(f"{nom} : un montant en euros, à remplir (lu : {valeur!r}).")
    return float(valeur)


@dataclass(frozen=True)
class LigneCaisse:
    """Une ligne de l'estimation : la caisse qui paie, et ce qu'elle affiche."""

    libelle: str
    codes: tuple[str, ...]
    brut: float


@dataclass(frozen=True)
class Depart:
    """Un âge de départ de l'estimation."""

    age: str
    date: dt.date
    trimestres: int | None
    regimes: tuple[LigneCaisse, ...]
    total_brut: float
    net: float | None


@dataclass(frozen=True)
class Estimation:
    lu_le: dt.date
    texte: str
    euros_de: int
    revenus_futurs: str
    #: Le revenu brut annuel que la page prête à la situation actuelle, en
    #: euros de ``euros_de`` ; ``None`` quand elle ne le dit pas.
    revenu_annuel: float | None
    naissance: dt.date | None
    sexe: str
    enfants: int
    naissances: tuple[str, ...]
    #: Les années du relevé corrigées à la main : année, revenu de l'année.
    corrections: dict[int, float]
    departs: tuple[Depart, ...]


def _codes(ligne: dict, nom: str, catalogue) -> tuple[str, ...]:
    codes = ligne.get("codes")
    if codes is None:
        codes = ALIAS.get(_plat(ligne.get("libelle", "")))
        if codes is None:
            raise Refus(f"{nom} : la caisse « {ligne.get('libelle')} » n'est pas connue "
                        "du script ; dire dans `codes` les régimes du modèle qu'elle couvre.")
    codes = tuple(str(code) for code in codes)
    inconnus = [code for code in codes if code not in catalogue.codes]
    if inconnus:
        raise Refus(f"{nom} : régimes absents du catalogue : {', '.join(inconnus)}.")
    etages = {catalogue[code].etage for code in codes}
    if len(etages) > 1:
        raise Refus(f"{nom} : « {ligne.get('libelle')} » mêle les étages "
                    f"{', '.join(sorted(etages))} ; une ligne de la caisse n'en a qu'un.")
    return codes


def _depart(brut: dict, nom: str, catalogue) -> Depart:
    date = _date(brut.get("date"), f"{nom}, date")
    if date.day != 1:
        raise Refus(f"{nom} : une pension prend effet le premier jour d'un mois "
                    f"(lu : {date.isoformat()}).")
    regimes = tuple(
        LigneCaisse(str(ligne.get("libelle") or ""),
                    _codes(ligne, f"{nom}, « {ligne.get('libelle')} »", catalogue),
                    _montant(ligne.get("brut"), f"{nom}, « {ligne.get('libelle')} »"))
        for ligne in brut.get("regimes") or [])
    if not regimes:
        raise Refus(f"{nom} : aucun régime recopié.")
    vus = [code for ligne in regimes for code in ligne.codes]
    if len(vus) != len(set(vus)):
        raise Refus(f"{nom} : un régime du modèle couvert par deux lignes.")
    somme = somme_ordonnee(ligne.brut for ligne in regimes)
    total = (somme if brut.get("total_brut") is None
             else _montant(brut.get("total_brut"), f"{nom}, total_brut"))
    # La page arrondit chaque ligne à l'euro : un euro par ligne au plus.
    if abs(total - somme) > len(regimes):
        raise Refus(f"{nom} : les lignes font {somme:.0f} € et la page affiche "
                    f"{total:.0f} € ; la recopie est à revoir.")
    trimestres = brut.get("trimestres")
    return Depart(
        age=str(brut.get("age") or ""), date=date,
        trimestres=None if trimestres is None else int(trimestres),
        regimes=regimes, total_brut=total,
        net=None if brut.get("net") is None else _montant(brut.get("net"), f"{nom}, net"))


def lire_estimation(donnees: dict, catalogue) -> Estimation:
    """L'estimation recopiée, vérifiée : la convention que le script sait
    reproduire, une date par départ, et des lignes qui font le total affiché."""
    if not isinstance(donnees, dict):
        raise Refus("l'estimation n'est pas un dictionnaire YAML : partir de --modele.")
    convention = donnees.get("convention") or {}
    if convention.get("montants") != "brut" or convention.get("periodicite") != "mensuel":
        raise Refus("convention : le script compare des bruts mensuels ; recopier les "
                    "montants bruts mensuels de la page (montants: brut, "
                    "periodicite: mensuel).")
    for cle in ("texte", "revenus_futurs"):
        if not str(convention.get(cle) or "").strip():
            raise Refus(f"convention.{cle} : à recopier mot pour mot depuis la page.")
    euros_de = convention.get("euros_de")
    if isinstance(euros_de, bool) or not isinstance(euros_de, int):
        raise Refus(f"convention.euros_de : l'année des euros de la page (lu : {euros_de!r}).")
    revenu = convention.get("revenu_annuel")
    assure = donnees.get("assure") or {}
    sexe = str(assure.get("sexe") or "").upper()
    if sexe not in ("H", "F"):
        raise Refus(f"assure.sexe : H ou F (lu : {assure.get('sexe')!r}).")
    naissance = assure.get("naissance")
    corrections = ((donnees.get("releve") or {}).get("corrections")) or {}
    departs = tuple(_depart(brut, f"départ {rang}", catalogue)
                    for rang, brut in enumerate(donnees.get("departs") or [], start=1))
    if not departs:
        raise Refus("departs : aucun âge de départ recopié.")
    return Estimation(
        lu_le=_date(donnees.get("lu_le"), "lu_le"),
        texte=" ".join(str(convention["texte"]).split()),
        euros_de=euros_de,
        revenus_futurs=" ".join(str(convention["revenus_futurs"]).split()),
        revenu_annuel=None if revenu is None else _montant(revenu, "convention.revenu_annuel"),
        naissance=None if naissance in (None, "AAAA-MM-JJ") else _date(naissance,
                                                                       "assure.naissance"),
        sexe=sexe,
        enfants=int(assure.get("enfants") or 0),
        naissances=tuple(str(n) for n in assure.get("naissances") or ()),
        corrections={int(annee): _montant(valeur, f"releve.corrections, {annee}")
                     for annee, valeur in corrections.items()},
        departs=departs,
    )


# ---------------------------------------------------------------------------
# Le scénario 1, liquidé à chaque date de l'estimation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Servi:
    """Ce que le modèle sert à un départ, brut mensuel, en euros de la page."""

    par_regime: dict[str, float]
    #: Le minimum vieillesse, qu'aucun régime ne sert et que l'estimation ignore.
    minimum_vieillesse: float
    trimestres: int
    ouverte: bool
    motif_ouverture: str


def servi(comparaison) -> Servi:
    """Le brut mensuel de chaque régime, en euros de la page : sa pension, minima
    compris, et la part qu'il sert de la majoration pour enfants, que le moteur
    compte à côté (`etagesActuels` de `moteur/js/pages.js`)."""
    actuel = comparaison.actuel
    passage = comparaison.coefficient_euros_constants / MOIS_PAR_AN
    par_regime: dict[str, float] = {}
    for pension in actuel.pensions_par_regime:
        par_regime[pension.regime] = par_regime.get(pension.regime, 0.0) + pension.montant
    minimum = 0.0
    for avantage in actuel.avantages_appliques:
        if avantage.code == "majoration_enfants":
            for code, part in avantage.par_regime:
                par_regime[code] = par_regime.get(code, 0.0) + part
        elif avantage.code == "minimum_vieillesse":
            minimum += avantage.montant
    return Servi(
        par_regime={code: montant * passage for code, montant in par_regime.items()},
        minimum_vieillesse=minimum * passage,
        trimestres=actuel.trimestres_valides,
        ouverte=actuel.liquidation_ouverte,
        motif_ouverture=actuel.motif_ouverture,
    )


class Confrontation:
    """Le relevé lu, l'estimation recopiée, et le modèle qui les relie."""

    def __init__(self, lecture: Lecture, estimation: Estimation,
                 revenus_futurs: str = "salaire_moyen", contexte: Contexte | None = None,
                 croissance: float = 0.0):
        if revenus_futurs not in REVENUS_FUTURS:
            raise Refus(f"--revenus-futurs : {', '.join(REVENUS_FUTURS)}.")
        if croissance and revenus_futurs != "prix":
            raise Refus("--croissance ne s'ajoute qu'aux prix (--revenus-futurs prix).")
        self.lecture, self.estimation = lecture, estimation
        self.revenus_futurs, self.croissance = revenus_futurs, croissance
        self.contexte = contexte or Contexte()
        self.naissance = self._naissance()
        self.derniere_annee = max(ligne.annee for ligne in lecture.lignes)
        # Les réglages ne dépendent pas du départ : celui du premier suffit.
        self.simulateur = self.contexte.simulateur(
            self._saisie(estimation.departs[0].date).parametres(self.contexte.base))
        self.catalogue = self.simulateur.catalogue
        self.macro = self.simulateur.macro
        self.motifs = charger_periodes_non_travaillees(self.macro.racine)
        self.releve = self._releve_corrige()

    def _naissance(self) -> str:
        lue, recopiee = self.lecture.naissance, self.estimation.naissance
        # Le relevé d'info-retraite ne porte que le mois de naissance, par le
        # numéro de sécurité sociale : il ne remplace pas la date recopiée, dont
        # le jour compte, mais il la contrôle.
        mois = self.lecture.mois_de_naissance
        if lue and recopiee and lue != recopiee.isoformat():
            raise Refus(f"la naissance du relevé ({lue}) n'est pas celle de "
                        f"l'estimation ({recopiee.isoformat()}).")
        if mois and recopiee and recopiee.isoformat()[:7] != mois:
            raise Refus(f"le relevé dit une naissance en {mois}, l'estimation le "
                        f"{recopiee.isoformat()}.")
        if not lue and not recopiee:
            raise Refus("le relevé ne porte pas la date de naissance"
                        + (f" — son numéro de sécurité sociale n'en dit que le mois, "
                           f"{mois}" if mois else "")
                        + " : la recopier dans assure.naissance.")
        return lue or recopiee.isoformat()

    def _releve_corrige(self) -> str:
        """La saisie du relevé, les années corrigées à la main remplacées."""
        lignes = self.lecture.parametres()["releve"].split("\n")
        for annee, revenu in sorted(self.estimation.corrections.items()):
            rangs = [rang for rang, ligne in enumerate(lignes)
                     if ligne.startswith(f"{annee}:")]
            if len(rangs) != 1:
                raise Refus(f"releve.corrections : l'année {annee} est sur "
                            f"{len(rangs)} lignes de la lecture, et non sur une.")
            champs = lignes[rangs[0]].split(":")
            champs[2] = str(arrondi(revenu))
            lignes[rangs[0]] = ":".join(champs)
        return "\n".join(lignes)

    def _saisie(self, depart: dt.date, releve: str | None = None) -> Saisie:
        parametres = self.lecture.parametres()
        requete = {
            "naissance": self.naissance, "sexe": self.estimation.sexe,
            "liquidation": f"{depart.year}-{depart.month:02d}",
            "releve": parametres["releve"] if releve is None else releve,
            "interruptions": parametres["interruptions"],
            "enfants": str(self.estimation.enfants),
            "euros": str(self.estimation.euros_de),
        }
        if self.estimation.naissances:
            requete["naissances"] = ",".join(self.estimation.naissances)
        try:
            return Saisie.depuis_requete(requete)
        except ErreurSaisie as erreur:
            raise Refus(f"départ du {depart.isoformat()} : {erreur}") from erreur

    def revenus_a_venir(self) -> tuple[list[tuple[str, float]], int]:
        """Ce qui se poursuit après le relevé : les emplois, chacun avec son
        revenu annuel, et l'année des euros de ce revenu."""
        dernieres = [ligne for ligne in self.lecture.lignes
                     if ligne.annee == self.derniere_annee and ligne.motif is None]
        if self.estimation.revenu_annuel is None:
            corrige = self.estimation.corrections.get(self.derniere_annee)
            return ([(ligne.statut, ligne.revenu if corrige is None else corrige)
                     for ligne in dernieres], self.derniere_annee)
        if not dernieres:
            raise Refus(f"la dernière année du relevé, {self.derniere_annee}, ne porte "
                        "aucun emploi à poursuivre.")
        principale = max(dernieres, key=lambda ligne: ligne.revenu)
        return [(principale.statut, self.estimation.revenu_annuel)], self.estimation.euros_de

    def _facteur(self, depuis: int, annee: int) -> float:
        if self.revenus_futurs == "prix":
            return (self.macro.coefficient_prix(depuis, annee)
                    * (1 + self.croissance / 100) ** (annee - depuis))
        return salaire_moyen_annuel(self.macro, annee) / salaire_moyen_annuel(self.macro, depuis)

    def releve_prolonge(self, depart: dt.date) -> str:
        """Le relevé, et les années qui le séparent du départ : chaque emploi
        poursuivi à son revenu, l'année du départ au prorata des mois travaillés
        avant lui. Leurs trimestres, le modèle les déduit."""
        if self.revenus_futurs == "aucun":
            return self.releve
        emplois, depuis = self.revenus_a_venir()
        lignes = [self.releve]
        for annee in range(self.derniere_annee + 1, depart.year + 1):
            mois = MOIS_PAR_AN if annee < depart.year else depart.month - 1
            if mois <= 0:
                continue
            facteur = self._facteur(depuis, annee) * mois / MOIS_PAR_AN
            lignes += [f"{annee}:{statut}:{arrondi(revenu * facteur)}"
                       for statut, revenu in emplois]
        return "\n".join(lignes)

    def carriere(self, depart: dt.date):
        if depart.year <= self.derniere_annee:
            raise Refus(f"départ du {depart.isoformat()} : le relevé porte encore "
                        f"{self.derniere_annee}, qui le suivrait.")
        saisie = self._saisie(depart, self.releve_prolonge(depart))
        # Le relevé est déjà prolongé, à la convention que --revenus-futurs
        # choisit ; « aucun » l'arrête à sa dernière année, et le site, qui
        # prolonge le sien, ne doit pas y revenir.
        return self.contexte._carriere_relevee(self.simulateur, saisie, self.motifs,
                                               prolonger=False)

    def servi(self, depart: Depart) -> Servi:
        return servi(self.simulateur.simuler(self.carriere(depart.date)))


# ---------------------------------------------------------------------------
# Le tableau des écarts
# ---------------------------------------------------------------------------

def euros(montant: float) -> str:
    return f"{montant:,.0f}".replace(",", " ")


def ecart(modele: float, caisse: float) -> str:
    texte = f"{modele - caisse:+,.0f}".replace(",", " ")
    if abs(caisse) < 0.5:
        return f"{texte:>8}        —"
    pour_cent = f"{100 * (modele - caisse) / caisse:+.1f}".replace(".", ",")
    return f"{texte:>8} {pour_cent:>6} %"


def tableau(depart: Depart, servi_: Servi, catalogue) -> list[str]:
    """Un départ : la caisse et le modèle, ligne de la caisse par ligne, puis
    étage par étage, puis le total — l'écart, modèle moins caisse."""
    sortie = [f"Départ le {depart.date.isoformat()}"
              + (f" ({depart.age})" if depart.age else "")
              + (f" — trimestres : caisse {depart.trimestres}, modèle {servi_.trimestres}"
                 if depart.trimestres is not None
                 else f" — trimestres du modèle : {servi_.trimestres}")]
    if not servi_.ouverte:
        sortie.append("  le modèle n'ouvre pas ce départ : son montant ne décrit "
                      "aucune pension servie.")
    rangees, couverts = [], set()
    for ligne in depart.regimes:
        modele = somme_ordonnee(servi_.par_regime.get(code, 0.0) for code in ligne.codes)
        couverts.update(ligne.codes)
        rangees.append((f"  {ligne.libelle}", ligne.brut, modele))
    for code, montant in sorted(servi_.par_regime.items()):
        if code not in couverts and round(montant) != 0:
            rangees.append((f"  {catalogue[code].nom} (absent de la page)", 0.0, montant))
    for etage, libelle in ETAGES:
        caisse = somme_ordonnee(ligne.brut for ligne in depart.regimes
                     if catalogue[ligne.codes[0]].etage == etage)
        modele = somme_ordonnee(montant for code, montant in servi_.par_regime.items()
                     if catalogue[code].etage == etage)
        if round(caisse) or round(modele):
            rangees.append((f"  = {libelle}", caisse, modele))
    rangees.append(("  = total", depart.total_brut, somme_ordonnee(servi_.par_regime.values())))
    largeur = max(len(libelle) for libelle, _, _ in rangees)
    sortie.append(f"{'':{largeur}} {'caisse':>8} {'modèle':>8} {'écart':>8}")
    sortie += [f"{libelle:{largeur}} {euros(caisse):>8} {euros(modele):>8} "
               f"{ecart(modele, caisse)}" for libelle, caisse, modele in rangees]
    if servi_.minimum_vieillesse:
        sortie.append(f"  minimum vieillesse du modèle, hors de l'estimation : "
                      f"{euros(servi_.minimum_vieillesse)} €")
    if depart.net is not None:
        sortie.append(f"  net de la caisse : {euros(depart.net)} € ; le net du modèle "
                      "attend les prélèvements officiels (action 138, étape 2).")
    return sortie


def _annees(annees: list[int]) -> str:
    return ", ".join(str(annee) for annee in annees)


def rapport(confrontation: Confrontation) -> str:
    estimation, lecture = confrontation.estimation, confrontation.lecture
    plafond = confrontation.macro.plafond_securite_sociale
    if confrontation.revenus_futurs == "aucun":
        a_venir = REVENUS_FUTURS["aucun"]
    else:
        emplois, depuis = confrontation.revenus_a_venir()
        origine = ("le revenu annuel que la page retient"
                   if estimation.revenu_annuel is not None
                   else f"les revenus de {confrontation.derniere_annee}, dernière année "
                        "du relevé")
        rythme = REVENUS_FUTURS[confrontation.revenus_futurs]
        if confrontation.croissance:
            rythme = (f"au rythme des prix, plus {confrontation.croissance:.2f} % par an"
                      .replace(".", ","))
        a_venir = (f"{origine}, en euros de {depuis}, {rythme}, "
                   f"à partir de {confrontation.derniere_annee + 1}")
    sortie = [
        f"« Mon estimation retraite », lue le {estimation.lu_le.isoformat()} : brut "
        f"mensuel, euros de {estimation.euros_de}.",
        f"  la page : « {estimation.texte} »",
        f"  revenus à venir, la page : « {estimation.revenus_futurs} »",
        f"  revenus à venir, le modèle : {a_venir}.",
        f"Le relevé : {len(lecture.lignes)} années lues, de "
        f"{min(l.annee for l in lecture.lignes)} à {confrontation.derniere_annee}"
        + (f", {len(lecture.ignorees)} lignes ignorées" if lecture.ignorees else "")
        + ".",
    ]
    sortie += [f"  {note}" for note in lecture.notes]
    au_dessus = annees_au_dessus_du_plafond(lecture, plafond)
    if au_dessus:
        sortie.append(
            f"  {len(au_dessus)} année(s) au-dessus du plafond de la Sécurité sociale "
            f"({_annees(au_dessus)}) : ce relevé porte le revenu entier, et non sa seule "
            "part plafonnée, quoi qu'en dise la lecture ; la complémentaire du modèle "
            "compte ce qui dépasse.")
    au_plafond = annees_au_plafond(lecture, plafond)
    if au_plafond and not au_dessus:
        sortie.append(
            f"  {len(au_plafond)} année(s) au plafond de la Sécurité sociale, la "
            f"dernière en {au_plafond[-1]} : le relevé n'y porte pas la part du "
            "salaire au-dessus du plafond, et la complémentaire du modèle en est "
            "minorée sans qu'aucune règle n'y soit pour rien.")
    if estimation.corrections:
        sortie.append(f"  corrigées à la main, d'après le relevé : "
                      f"{_annees(sorted(estimation.corrections))}.")
    sortie.append("L'écart est celui du modèle à la caisse : positif, le modèle sert plus.")
    for depart in estimation.departs:
        sortie.append("")
        sortie += tableau(depart, confrontation.servi(depart), confrontation.catalogue)
    return "\n".join(sortie)


# ---------------------------------------------------------------------------
# La ligne de commande
# ---------------------------------------------------------------------------

def main(arguments: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # la console de Windows lit cp1252
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    lecteur.add_argument("--modele", action="store_true",
                         help="imprimer le gabarit vide de l'estimation")
    lecteur.add_argument("--releve", type=Path, help="le relevé de carrière, PDF ou texte")
    lecteur.add_argument("--estimation", type=Path, help="l'estimation recopiée (YAML)")
    lecteur.add_argument("--revenus-futurs", choices=sorted(REVENUS_FUTURS),
                         default="salaire_moyen",
                         help="comment poursuivre la carrière après le relevé")
    lecteur.add_argument("--croissance", type=float, default=0.0,
                         help="avec --revenus-futurs prix : ce que les revenus gagnent "
                              "chaque année au-delà des prix, en pour cent")
    options = lecteur.parse_args(arguments)
    if options.modele:
        print(GABARIT, end="")
        return 0
    if options.releve is None or options.estimation is None:
        lecteur.error("--releve et --estimation, ou --modele")
    try:
        releve = hors_du_depot(options.releve)
        chemin = hors_du_depot(options.estimation)
        contexte = Contexte()
        estimation = lire_estimation(
            yaml.safe_load(chemin.read_text(encoding="utf-8")),
            contexte.simulateur().catalogue)
        print(rapport(Confrontation(lire(releve), estimation, options.revenus_futurs,
                                    contexte, options.croissance)))
        return 0
    except Refus as refus:
        print(f"refusé : {refus}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
