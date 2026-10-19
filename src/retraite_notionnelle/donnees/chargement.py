"""Primitives de chargement, avec suivi de la fiabilité des données.

Principe directeur : aucune valeur ne circule dans le modèle sans son niveau de
fiabilité. Une simulation qui repose sur des séries reconstituées doit le dire,
et doit pouvoir refuser de s'exécuter si l'utilisateur exige mieux.
"""

from __future__ import annotations

import copy
import csv
import functools
import json
import pickle
import threading
from bisect import bisect_left, bisect_right
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Callable, Iterator, TypeVar

import yaml
from ..somme import somme_ordonnee

T = TypeVar("T")


class Fiabilite(IntEnum):
    """Niveau de certification d'une donnée, du plus faible au plus fort."""

    ESTIMEE = 0     # reconstitution, ordre de grandeur
    MOYENNE = 1     # valeur publiée mais champ ou base incertains
    HAUTE = 2       # valeur publiée, recopiée, non recontrôlée
    CERTIFIEE = 3   # valeur recontrôlée automatiquement contre la source

    @classmethod
    def depuis_texte(cls, texte: str) -> "Fiabilite":
        cle = (texte or "").strip().lower()
        correspondance = {
            "estimee": cls.ESTIMEE,
            "estimée": cls.ESTIMEE,
            "projetee": cls.ESTIMEE,
            "projetée": cls.ESTIMEE,
            "moyenne": cls.MOYENNE,
            "haute": cls.HAUTE,
            "certifiee": cls.CERTIFIEE,
            "certifiée": cls.CERTIFIEE,
        }
        if cle not in correspondance:
            raise ValueError(f"niveau de fiabilité inconnu : {texte!r}")
        return correspondance[cle]

    def __str__(self) -> str:  # pragma: no cover - confort d'affichage
        return self.name.lower()


class DonneeInsuffisante(RuntimeError):
    """Levée quand la fiabilité disponible est inférieure à celle exigée."""


@dataclass(frozen=True)
class ValeurAnnuelle:
    annee: int
    valeur: float
    fiabilite: Fiabilite


class SerieAnnuelle:
    """Série indexée par année, avec fiabilité et interpolation contrôlée.

    Trois comportements sont distingués, et le choix répond à une seule
    question : QUE VEUT DIRE UNE ANNÉE ABSENTE ?

    * ``escalier`` (défaut) — elle n'a pas changé. La valeur est celle de la
      dernière année renseignée, et elle garde sa fiabilité. C'est le
      comportement correct pour des paramètres juridiques : un taux reste en
      vigueur jusqu'à sa modification, et c'est la loi qui le dit.
    * ``lineaire`` — la grandeur est continue et on n'en tient que des points.
      On interpole, et jamais au-dessus de ``haute`` : l'espérance de vie à
      60 ans est désormais renseignée chaque année, celle à 65 ans ne l'est
      qu'avant 1986 par points espacés.
    * ``ponctuelle`` — elle n'a pas été MESURÉE. La valeur du bord est
      reconduite comme dans l'escalier, mais elle tombe à ``estimee``. C'est le
      comportement des séries d'ENQUÊTE, où un trou est un trou : la DREES ne
      publie pas la coordination RATP en 2022, et reconduire 2021 sous le
      niveau ``certifiee`` prêterait au producteur un chiffre qu'il n'a pas
      publié.

    La distinction n'est pas décorative : la fiabilité se propage jusqu'au
    résultat affiché, et c'est elle qui dit au lecteur ce qui est recontrôlé
    contre le fichier d'une institution et ce qui ne l'est pas.
    """

    def __init__(
        self,
        valeurs: dict[int, ValeurAnnuelle],
        nom: str,
        interpolation: str = "escalier",
    ) -> None:
        self.nom = nom
        self.interpolation = interpolation
        self._valeurs = dict(sorted(valeurs.items()))
        if not self._valeurs:
            raise ValueError(f"série {nom!r} vide")
        self._annees = list(self._valeurs)
        self._memo: dict[int, ValeurAnnuelle] = {}

    # -- accès ---------------------------------------------------------------

    @property
    def premiere_annee(self) -> int:
        return self._annees[0]

    @property
    def derniere_annee(self) -> int:
        return self._annees[-1]

    def brut(self, annee: int) -> ValeurAnnuelle:
        """Valeur avec sa fiabilité, en appliquant la règle d'interpolation.

        Appelée six millions de fois par la construction des témoins, dont
        l'écrasante majorité sur les mêmes années : le résultat est mémorisé.
        La série ne change jamais après `__init__` — `prolongee` en construit
        une neuve —, donc la mémorisation ne peut pas se désynchroniser.
        """
        connue = self._memo.get(annee)
        if connue is not None:
            return connue
        valeur = self._calculer(annee)
        self._memo[annee] = valeur
        return valeur

    def _calculer(self, annee: int) -> ValeurAnnuelle:
        if annee in self._valeurs:
            return self._valeurs[annee]

        if annee < self.premiere_annee:
            base = self._valeurs[self.premiere_annee]
            return ValeurAnnuelle(annee, base.valeur, Fiabilite.ESTIMEE)
        if annee > self.derniere_annee:
            base = self._valeurs[self.derniere_annee]
            return ValeurAnnuelle(annee, base.valeur, Fiabilite.ESTIMEE)

        # `_annees` est trié : on encadre par dichotomie. Le balayage complet
        # qu'il y avait ici (`max(a for a in ... if a < annee)`, deux fois)
        # coûtait la longueur de la série à chaque interpolation.
        rang = bisect_left(self._annees, annee)
        precedente, suivante = self._annees[rang - 1], self._annees[rang]
        avant, apres = self._valeurs[precedente], self._valeurs[suivante]

        if self.interpolation in ("escalier", "ponctuelle"):
            # ESCALIER : le fichier décrit un BARÈME, et une année absente est
            # une année sans changement. La valeur de 2016 sous un seuil fixé
            # en 2015 est celle de 2015, et elle est aussi certifiée qu'elle :
            # c'est la loi qui le dit, pas une interpolation.
            #
            # PONCTUELLE : le fichier décrit des MESURES, et une année absente
            # est une année non mesurée. La DREES ne publie pas la coordination
            # RATP en 2022 ; reconduire 2021 est une estimation raisonnable, et
            # la dire « certifiée » serait prêter au producteur un chiffre
            # qu'il n'a pas publié. La valeur ne change donc pas, la fiabilité
            # si — et c'est ce qui la rend discernable.
            fiabilite = (avant.fiabilite if self.interpolation == "escalier"
                         else Fiabilite.ESTIMEE)
            return ValeurAnnuelle(annee, avant.valeur, fiabilite)

        poids = (annee - precedente) / (suivante - precedente)
        valeur = avant.valeur + poids * (apres.valeur - avant.valeur)
        # L'interpolation ne peut pas être plus fiable que ses bornes, et une
        # valeur interpolée n'est jamais « certifiée ».
        fiabilite = min(avant.fiabilite, apres.fiabilite, Fiabilite.HAUTE)
        return ValeurAnnuelle(annee, valeur, fiabilite)

    def __call__(self, annee: int, fiabilite_minimale: Fiabilite = Fiabilite.ESTIMEE) -> float:
        v = self.brut(annee)
        if v.fiabilite < fiabilite_minimale:
            raise DonneeInsuffisante(
                f"série {self.nom!r}, année {annee} : fiabilité {v.fiabilite} "
                f"< minimum exigé {fiabilite_minimale}"
            )
        return v.valeur

    def fiabilite(self, annee: int) -> Fiabilite:
        return self.brut(annee).fiabilite

    def annees(self) -> Iterator[int]:
        return iter(self._annees)

    def prolongee(self, valeur: float, jusqu_a: int,
                  fiabilite: Fiabilite = Fiabilite.ESTIMEE) -> "SerieAnnuelle":
        """Nouvelle série prolongée par une valeur constante jusqu'à ``jusqu_a``.

        Sert à projeter au-delà de la dernière observation. La série d'origine
        n'est pas modifiée, et les années ajoutées portent la fiabilité
        indiquée — jamais celle des années observées.
        """
        valeurs = dict(self._valeurs)
        for annee in range(self.derniere_annee + 1, jusqu_a + 1):
            valeurs[annee] = ValeurAnnuelle(annee, valeur, fiabilite)
        return SerieAnnuelle(valeurs, self.nom, self.interpolation)

    def fiabilite_minimale_sur(self, debut: int, fin: int) -> Fiabilite:
        """Maillon le plus faible sur une plage — c'est lui qui qualifie un résultat."""
        return min((self.brut(a).fiabilite for a in range(debut, fin + 1)), default=Fiabilite.ESTIMEE)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SerieAnnuelle({self.nom!r}, {self.premiere_annee}-{self.derniere_annee}, "
            f"{len(self._valeurs)} points, {self.interpolation})"
        )


# -- l'instantané : le temps d'un calcul, le disque ne se regarde qu'une fois --

#: Ce que les chargeurs ont rendu dans l'instantané ouvert par ce fil, par
#: chargeur et par arguments ; ``None`` hors d'un instantané.
_FIL = threading.local()


@contextmanager
def instantane() -> Iterator[None]:
    """Le temps d'un calcul, les données sont celles de son début.

    Les chargeurs du disque se gardent sur la signature du fichier, sa date et
    sa taille, pour relire une donnée modifiée sans qu'on ait à rien vider :
    c'est un ``stat`` à chaque appel. Sous Windows, il coûte deux à trois cents
    microsecondes, et la construction des carrières en faisait près de trois
    cent mille par coût agrégé, le tiers de son temps (feuille de route,
    action 135). Dans un instantané, un chargeur marqué
    :func:`une_fois_par_instantane` ne s'appelle qu'une fois par arguments : ce
    qu'il a rendu, il le rend encore, sans regarder le disque. Un calcul voit
    donc ses données telles qu'elles étaient à son début, ce qui vaut mieux
    qu'un mélange si l'une change en cours de route ; le suivant les relit.
    Imbriqué, l'instantané est celui du dehors ; il ne vaut que pour le fil
    qui l'ouvre.
    """
    if getattr(_FIL, "vu", None) is not None:
        yield
        return
    _FIL.vu = {}
    try:
        yield
    finally:
        _FIL.vu = None


def dans_un_instantane(calcul: Callable[..., T]) -> Callable[..., T]:
    """Le calcul décoré s'exécute dans un instantané (:func:`instantane`)."""

    @functools.wraps(calcul)
    def enrobe(*args, **kwargs):
        if getattr(_FIL, "vu", None) is not None:
            return calcul(*args, **kwargs)
        with instantane():
            return calcul(*args, **kwargs)

    return enrobe


def une_fois_par_instantane(chargeur: Callable[..., T]) -> Callable[..., T]:
    """Dans un instantané, le chargeur décoré ne s'appelle qu'une fois par
    arguments ; hors d'un instantané, il s'appelle comme avant.

    Seulement pour ce qui se partage déjà, d'un appel à l'autre, sans copie :
    un objet que personne ne modifie, ou un nombre. ``charger_yaml``, qui rend
    une copie que l'appelant peut modifier, n'en est pas.
    """

    @functools.wraps(chargeur)
    def enrobe(*args, **kwargs):
        vu = getattr(_FIL, "vu", None)
        if vu is None or kwargs:
            return chargeur(*args, **kwargs)
        cle = (enrobe, *args)
        try:
            return vu[cle]
        except KeyError:
            pass
        except TypeError:        # un argument qui ne se hache pas
            return chargeur(*args)
        resultat = vu[cle] = chargeur(*args)
        return resultat

    return enrobe


# Même raison que pour le YAML plus bas : les mêmes CSV sont relus des dizaines
# de fois par une construction de témoins, une fois par jeu de données rebâti.
# La série rendue est partagée et non copiée — c'est sûr, et même souhaitable :
# `SerieAnnuelle` ne change jamais après son constructeur (`prolongee` en rend
# une neuve), et sa mémoire d'interpolation profite alors à tous les appelants.
_SERIES_EN_CACHE: dict[tuple, SerieAnnuelle] = {}


def charger_serie_annuelle(
    chemin: Path,
    colonne_valeur: str,
    nom: str | None = None,
    interpolation: str = "escalier",
    filtre: dict[str, str] | None = None,
) -> SerieAnnuelle:
    """Charge un CSV ``annee,<colonne_valeur>,fiabilite`` en série annuelle.

    Les lignes commençant par ``#`` sont des commentaires : elles portent la
    documentation de provenance et sont ignorées à la lecture.

    ``interpolation`` DIT CE QU'UNE ANNÉE ABSENTE VEUT DIRE, et c'est le seul
    endroit où cette question se tranche :

    * ``escalier`` — un BARÈME. L'année absente n'a pas changé, et la valeur
      reconduite est aussi fiable que celle qui la précède.
    * ``lineaire`` — une grandeur CONTINUE, dont on tient deux points. On
      interpole, et jamais au-dessus de ``haute``.
    * ``ponctuelle`` — des MESURES. L'année absente n'a pas été mesurée : la
      valeur du bord est reconduite comme dans l'escalier, mais elle tombe à
      ``estimee``, parce que le producteur ne l'a pas publiée.

    Le défaut est ``escalier`` parce que la plupart des fichiers du dépôt sont
    des barèmes. Une série d'ENQUÊTE laissée au défaut prête au producteur des
    chiffres qu'il n'a pas publiés, et c'était le cas de la coordination RATP
    en 2022 jusqu'au 20 septembre 2026.
    """
    try:
        etat = chemin.stat()
        cle = (str(chemin), etat.st_mtime_ns, etat.st_size, colonne_valeur, nom,
               interpolation, tuple(sorted((filtre or {}).items())))
    except OSError:  # pragma: no cover - le fichier manquant lèvera plus bas
        cle = None
    if cle is not None and cle in _SERIES_EN_CACHE:
        return _SERIES_EN_CACHE[cle]

    valeurs: dict[int, ValeurAnnuelle] = {}
    with chemin.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        for enregistrement in csv.DictReader(lignes):
            if filtre and any(enregistrement.get(k) != v for k, v in filtre.items()):
                continue
            annee = int(enregistrement["annee"])
            valeurs[annee] = ValeurAnnuelle(
                annee=annee,
                valeur=float(enregistrement[colonne_valeur]),
                fiabilite=Fiabilite.depuis_texte(enregistrement["fiabilite"]),
            )
    if not valeurs:
        raise ValueError(f"aucune ligne exploitable dans {chemin} (filtre={filtre})")
    serie = SerieAnnuelle(valeurs, nom or f"{chemin.stem}.{colonne_valeur}", interpolation)
    if cle is not None:
        _SERIES_EN_CACHE[cle] = serie
    return serie


#: Tables indexées sur la GÉNÉRATION et non sur l'année, mémorisées sur la même
#: signature de fichier que les séries annuelles. Elles ne peuvent pas passer par
#: ``charger_serie_annuelle`` : leur clé s'écrit en années décimales — 1961,667
#: pour « né à compter du 1er septembre 1961 » —, là où une série annuelle est
#: indexée par des entiers.
_TABLES_GENERATION_EN_CACHE: dict[tuple, tuple[dict, tuple]] = {}


def charger_table_par_generation(
    chemin: Path, colonne: str,
) -> tuple[dict[float, tuple[float, Fiabilite]], tuple[float, ...]]:
    """Charge un CSV ``generation,<colonne>,fiabilite``, mémorisé.

    Rend la table et ses générations triées. Un fichier absent rend deux
    conteneurs vides : c'est à l'appelant de dire ce qu'il en fait, la fiche du
    régime reprenant en général la main.
    """
    try:
        etat = chemin.stat()
        cle = (str(chemin), etat.st_mtime_ns, etat.st_size, colonne)
    except OSError:
        return {}, ()
    if cle in _TABLES_GENERATION_EN_CACHE:
        return _TABLES_GENERATION_EN_CACHE[cle]

    table: dict[float, tuple[float, Fiabilite]] = {}
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            table[float(ligne["generation"])] = (
                float(ligne[colonne]),
                Fiabilite.depuis_texte(ligne["fiabilite"]),
            )
    resultat = (table, tuple(sorted(table)))
    _TABLES_GENERATION_EN_CACHE[cle] = resultat
    return resultat


#: Tables à clé composite — (année, tranche), (catégorie, tranche) —, mémorisées
#: sur la signature du fichier comme les séries annuelles. Ni l'une ni l'autre
#: des deux autres formes ne convient : la clé n'est pas un entier, et elle n'est
#: pas unique.
_TABLES_CSV_EN_CACHE: dict[tuple, tuple[dict, tuple]] = {}


@une_fois_par_instantane
def charger_table_csv(
    chemin: Path, cles: tuple[str, ...], colonne: str,
) -> tuple[dict[tuple[str, ...], float], tuple[Fiabilite, ...]]:
    """Charge un CSV à clé composite, mémorisé. Rend la table et ses fiabilités.

    Les clés sont rendues telles qu'elles sont écrites, en texte : c'est à
    l'appelant de les interpréter, une année et une tranche d'âge n'ayant pas
    le même type.
    """
    try:
        etat = chemin.stat()
        signature = (str(chemin), etat.st_mtime_ns, etat.st_size, cles, colonne)
    except OSError:
        return {}, ()
    if signature in _TABLES_CSV_EN_CACHE:
        return _TABLES_CSV_EN_CACHE[signature]

    table: dict[tuple[str, ...], float] = {}
    fiabilites: list[Fiabilite] = []
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            table[tuple(ligne[c] for c in cles)] = float(ligne[colonne])
            fiabilites.append(Fiabilite.depuis_texte(ligne["fiabilite"]))
    resultat = (table, tuple(fiabilites))
    _TABLES_CSV_EN_CACHE[signature] = resultat
    return resultat


def valeur_par_generation(
    table: dict[float, tuple[float, Fiabilite]],
    generations: tuple[float, ...],
    generation: float,
) -> tuple[float, Fiabilite] | None:
    """Dernière valeur dont la génération ne dépasse pas celle demandée.

    En deçà de la première génération du fichier, ``None`` : le paramètre ne
    dépendait pas encore de la génération à cette date-là.
    """
    if not generations or generation < generations[0]:
        return None
    rang = bisect_right(generations, generation)
    return table[generations[rang - 1]]


# Le chargeur C de libyaml quand il est là, le chargeur Python sinon : à
# contenu égal le premier lit cinq à dix fois plus vite, et rien d'autre ne
# change. `yaml.safe_load` ne le choisit jamais de lui-même.
_LECTEUR = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

# Les fiches de régimes pèsent 1,4 Mo de YAML, relus en entier à chaque
# construction d'un contexte : c'était 1,5 s par simulation partie de zéro, et
# l'essentiel des sept minutes de la suite de tests. On garde donc l'arbre
# analysé, indexé par la signature du fichier (mtime et taille) pour qu'une
# donnée modifiée soit relue sans qu'on ait à vider quoi que ce soit.
# La valeur gardée est la forme `pickle` de l'arbre, et non l'arbre : la
# recharger revient à en faire une copie neuve, trois fois plus vite que
# `deepcopy` (1,0 ms contre 2,9 ms sur la plus grosse fiche). Un contenu que
# `pickle` refuserait — il n'y en a pas, `safe_load` ne rend que des types
# simples — retombe sur `deepcopy`.
_YAML_EN_CACHE: dict[tuple[str, int, int], bytes | dict] = {}

#: Qui veut voir ce que le modèle lit de chaque YAML : ``scripts/lectures_du_modele.py``
#: y substitue au dictionnaire rendu un dictionnaire qui note les champs lus
#: (feuille de route, action 135). ``None`` hors de ce relevé.
SUIVI: Callable[[Path, dict], dict] | None = None


def _copie(garde: bytes | dict) -> dict:
    if isinstance(garde, bytes):
        return pickle.loads(garde)
    return copy.deepcopy(garde)


def _a_garder(contenu: dict) -> bytes | dict:
    try:
        return pickle.dumps(contenu, protocol=pickle.HIGHEST_PROTOCOL)
    except (pickle.PicklingError, TypeError, RecursionError):  # pragma: no cover
        return contenu


def charger_yaml(chemin: Path) -> dict:
    """Lit un YAML, en mémorisant l'arbre analysé d'un appel à l'autre.

    L'appelant reçoit une copie profonde, comme avant : le dictionnaire rendu
    reste librement modifiable sans que la mémorisation en garde trace. La
    copie coûte cent fois moins cher que l'analyse (4 ms contre 400 ms pour la
    plus grosse fiche), et le cache se périme tout seul dès que le fichier
    change sur le disque.
    """
    try:
        etat = chemin.stat()
        cle = (str(chemin), etat.st_mtime_ns, etat.st_size)
    except OSError:  # pragma: no cover - le fichier manquant lèvera plus bas
        cle = None
    if cle is not None and cle in _YAML_EN_CACHE:
        contenu = _copie(_YAML_EN_CACHE[cle])
    else:
        with chemin.open(encoding="utf-8") as flux:
            contenu = yaml.load(flux, Loader=_LECTEUR) or {}
        if cle is not None:
            _YAML_EN_CACHE[cle] = _a_garder(contenu)
    return contenu if SUIVI is None else SUIVI(chemin, contenu)


def compter_institutions(racine: Path) -> int:
    """Combien d'institutions le manifeste des sources cite.

    La page Données l'affichait en dur — « 28 » — quand le manifeste en portait
    36 : le compte était celui d'un jour de 2026, et rien ne le relisait.
    `docs/methodologie.md` l'écrivait en toutes lettres, « vingt-huit », et
    s'était trompé au même endroit. Il se lit maintenant là où il vit.
    """
    return len(charger_yaml(racine / "sources.yaml").get("institutions", {}))


def journal_certification(racine: Path) -> dict:
    """Trace du dernier recontrôle des séries contre leurs sources.

    Écrite par ``scripts/verifier_donnees.py --appliquer``. Les téléchargements
    bruts ne sont pas versionnés : ce journal est la seule pièce qui, sur un
    dépôt cloné, dise d'où viennent les valeurs marquées ``certifiee``. Son
    absence n'est pas une erreur — elle signifie qu'aucune certification n'a
    encore eu lieu.

    Chaque fiche de série porte ``verifiee_le``, le jour où elle a été relue
    contre sa source ; ``dernier_passage_le`` est la date du dernier passage
    du vérificateur, quelles que soient les séries qu'il a atteintes.
    """
    chemin = racine / "derive" / "certification.json"
    if not chemin.exists():
        return {}
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):  # pragma: no cover - fichier abîmé
        return {}


@dataclass(frozen=True)
class PeriodeNonTravaillee:
    """Ce qu'ouvre une période non travaillée, selon son motif."""

    motif: str
    trimestres_assimiles: int
    ouvre_droits_complementaires: bool
    #: Les points complémentaires de la période sont-ils PAYÉS par quelqu'un ?
    #: Oui du chômage indemnisé, dont l'Unédic verse les cotisations ; non de
    #: la maladie, de la maternité, de l'invalidité et de l'accident du
    #: travail, que l'Agirc-Arrco attribue « sans contrepartie de
    #: cotisations ». Le scénario 1 sert les uns et les autres ; un compte
    #: notionnel, qui ne porte que ce qui a été versé, les premiers seuls.
    cotisations_complementaires_versees: bool = False
    #: Le parent est-il affilié à l'assurance vieillesse des parents au foyer
    #: pendant cette période ? La CNAF cotise alors au régime général sur une
    #: assiette forfaitaire égale au SMIC, et ce salaire est PORTÉ AU COMPTE :
    #: c'est ce qui distingue l'AVPF d'une période assimilée, laquelle valide
    #: des trimestres sans jamais ajouter de salaire.
    avpf: bool = False
    #: Cette période entre-t-elle dans les SERVICES d'un régime de la fonction
    #: publique ? La pension y est proratisée sur les services et bonifications
    #: (L. 13 du code des pensions), et l'article L. 9 refuse le temps passé
    #: « dans une position statutaire ne comportant pas l'accomplissement de
    #: services effectifs au sens de l'article L. 5 », sauf une liste fermée.
    #: La durée d'assurance, elle, retient la période dans tous les cas : ce
    #: sont deux cases distinctes, et les confondre servait à un fonctionnaire
    #: au chômage la pension d'une carrière pleine.
    services_fonction_publique: bool = True
    #: Limite, EN TRIMESTRES PAR ENFANT, des services ainsi ouverts — le 1° de
    #: L. 9 excepte le congé parental « dans la limite de trois ans par
    #: enfant ». Zéro quand la période n'est pas plafonnée.
    services_plafond_trimestres_par_enfant: int = 0
    #: Nature de cette période au sens de l'article D. 351-1-2, qui la RÉPUTE
    #: COTISÉE pour la carrière longue sous une limite que chaque rédaction
    #: fixe (fiche ``carriere_longue_reputes_cotises_autres``). Vide quand
    #: elle ne l'est jamais — le chômage non indemnisé, que l'article ne
    #: reprend pas.
    reputes_cotises_nature: str = ""
    fiabilite: Fiabilite = Fiabilite.ESTIMEE


def _services(ligne: dict[str, str]) -> tuple[bool, int]:
    """Ce qu'une ligne de la table dit des services de la fonction publique.

    Trois valeurs, et une seule en porte un plafond : ``oui`` la position
    comporte des services effectifs ou L. 9 l'excepte nommément, ``non`` elle
    n'en comporte pas, ``plafonne`` elle est exceptée dans une limite, que la
    colonne voisine donne en ANNÉES par enfant.
    """
    valeur = ligne.get("services_fonction_publique", "oui").strip().lower()
    plafond = ligne.get("services_plafond_annees_par_enfant", "").strip()
    if valeur == "plafonne":
        return True, 4 * int(plafond) if plafond else 0
    return valeur == "oui", 0


@dataclass(frozen=True)
class AssietteMinimale:
    """Une ligne de ``legislation/assiette_minimale_independants.csv``."""

    statuts: frozenset[str]
    regimes: frozenset[str]
    debut: int
    fin: int | None
    heures_smic: float | None
    part_pass: float | None
    proratise: bool
    jours_minimum: int

    def montant(self, pass_annuel: float, smic_horaire: float,
                part: float) -> float:
        """L'assiette minimale de l'année, pour une année couverte à ``part``.

        Nulle en deçà de ``jours_minimum`` d'affiliation ; proratisée quand le
        texte le dit, entière sinon.
        """
        if part * 365 + 1e-6 < self.jours_minimum:
            return 0.0
        if self.heures_smic is not None:
            montant = self.heures_smic * smic_horaire
        else:
            montant = (self.part_pass or 0.0) * pass_annuel
        return montant * part if self.proratise else montant


_ASSIETTES_MINIMALES: dict[tuple[str, int, int], tuple[AssietteMinimale, ...]] = {}


@une_fois_par_instantane
def charger_assiettes_minimales(racine: Path) -> tuple[AssietteMinimale, ...]:
    """Assiette minimale du régime de base des indépendants, par statut.

    Lue à chaque construction d'une carrière : on la garde donc, indexée sur
    la signature du fichier, comme les autres points de passage du disque.
    """
    chemin = racine / "reference" / "legislation" / "assiette_minimale_independants.csv"
    if not chemin.exists():
        return ()
    etat = chemin.stat()
    cle = (str(chemin), etat.st_mtime_ns, etat.st_size)
    if cle in _ASSIETTES_MINIMALES:
        return _ASSIETTES_MINIMALES[cle]
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        table = tuple(
            AssietteMinimale(
                statuts=frozenset(ligne["statuts"].split()),
                regimes=frozenset(ligne["regimes"].split()),
                debut=int(ligne["debut"]),
                fin=int(ligne["fin"]) if ligne["fin"].strip() else None,
                heures_smic=(float(ligne["heures_smic"])
                             if ligne["heures_smic"].strip() else None),
                part_pass=(float(ligne["part_pass"])
                           if ligne["part_pass"].strip() else None),
                proratise=ligne["proratise"].strip().lower() == "oui",
                jours_minimum=int(ligne["jours_minimum"] or 0),
            )
            for ligne in csv.DictReader(lignes)
        )
    _ASSIETTES_MINIMALES[cle] = table
    return table


def assiette_minimale(table: tuple[AssietteMinimale, ...], statut: str,
                      annee: int) -> AssietteMinimale | None:
    """La règle d'assiette minimale que ce statut subit cette année-là."""
    for regle in table:
        if (statut in regle.statuts and regle.debut <= annee
                and (regle.fin is None or annee <= regle.fin)):
            return regle
    return None


@dataclass(frozen=True)
class DispenseAssietteMinimale:
    """Un motif de ``legislation/dispenses_assiette_minimale.yaml``."""

    motif: str
    debut: int
    fin: int | None
    statuts: frozenset[str]
    #: Écarte-t-il aussi l'assiette minimale des complémentaires des libéraux
    #: (L. 644-1 et L. 644-2) ?
    complementaires: bool

    def s_applique(self, statut: str, annee: int) -> bool:
        """Le texte dispense-t-il ce statut cette année-là ?"""
        return (statut in self.statuts and self.debut <= annee
                and (self.fin is None or annee <= self.fin))


@une_fois_par_instantane
def charger_dispenses_assiette_minimale(
        racine: Path) -> dict[str, DispenseAssietteMinimale]:
    """Les dispenses de l'assiette minimale des indépendants, par motif
    (L. 613-11, D. 642-4 ; action 138, étape 18)."""
    chemin = racine / "reference" / "legislation" / "dispenses_assiette_minimale.yaml"
    if not chemin.exists():
        return {}
    donnees = charger_yaml(chemin)
    familles = donnees["familles"]
    return {
        motif: DispenseAssietteMinimale(
            motif=motif,
            debut=int(regle["debut"]),
            fin=None if regle.get("fin") is None else int(regle["fin"]),
            statuts=frozenset(s for f in regle["familles"] for s in familles[f]),
            complementaires=bool(regle["complementaires"]),
        )
        for motif, regle in donnees["dispenses"].items()
    }


def dispense_assiette_minimale(table: dict[str, DispenseAssietteMinimale],
                               motif: str, statut: str, annee: int) -> str:
    """Le motif que la ligne retient : ``motif`` si le texte en dispense ce
    statut cette année-là, vide sinon — l'assuré qui se dit au RSA en 2010
    cotise sur l'assiette minimale, que rien ne lui épargnait encore. Un motif
    inconnu est refusé."""
    if not motif:
        return ""
    if motif not in table:
        raise ValueError(f"dispense de l'assiette minimale inconnue : {motif!r} "
                         f"(motifs : {', '.join(sorted(table))})")
    return motif if table[motif].s_applique(statut, annee) else ""


def dispense_les_complementaires(racine: Path, motif: str) -> bool:
    """Le motif retenu par une ligne écarte-t-il aussi l'assiette minimale des
    complémentaires des libéraux (L. 644-1, L. 644-2) ? Le RSA, la prime
    d'activité et l'activité saisonnière, oui (L. 613-11) ; les dispenses
    de D. 642-4, non."""
    if not motif:
        return False
    regle = charger_dispenses_assiette_minimale(racine).get(motif)
    return regle is not None and regle.complementaires


@une_fois_par_instantane
def charger_validation_micro(racine: Path) -> dict[str, dict[int, float]]:
    """Le revenu qui valide les trimestres du micro-entrepreneur, rapporté à
    son revenu abattu, par activité et par année
    (``legislation/micro_social.yaml`` ; action 138, étape 12).

    La caisse valide sur le « revenu cotisé » : le chiffre d'affaires fois le
    taux global (D. 613-4), fois la part de base (D. 613-6), divisé par le
    taux de base (D. 633-3, ou la première tranche de la CNAVPL pour la
    Cipav). Le modèle porte le revenu abattu, le chiffre d'affaires fois
    (1 - abattement) : le rapport des deux le convertit. L'année prend la
    moyenne de ses douze mois ; seules figurent les années qu'une version
    couvre entières. Une version marquée ``valide: false`` répartit le forfait
    sans valider : la Cipav d'avant octobre 2022.
    """
    chemin = racine / "reference" / "legislation" / "micro_social.yaml"
    if not chemin.exists():
        return {}
    donnees = charger_yaml(chemin)
    table: dict[str, dict[int, float]] = {}
    for activite, toutes in donnees["versions"].items():
        versions = [v for v in toutes if v.get("valide", True)]
        part_abattue = 1.0 - donnees["abattements"][activite]
        debuts = [tuple(int(x) for x in v["debut"].split("-")) for v in versions]
        premiere = debuts[0][0] + (0 if debuts[0][1] == 1 else 1)
        derniere = max(annee for annee, _ in debuts)
        par_annee = {}
        for annee in range(premiere, derniere + 1):
            mensuels = []
            for mois in range(1, 13):
                rang = max(i for i, d in enumerate(debuts) if d <= (annee, mois))
                v = versions[rang]
                mensuels.append(v["taux_global"] * v["part_base"] / v["taux_base"])
            par_annee[annee] = somme_ordonnee(mensuels) / 12.0 / part_abattue
        table[activite] = par_annee
    return table


@une_fois_par_instantane
def charger_cotisation_micro(racine: Path) -> dict[str, tuple[tuple[str, str],
                                                              dict[int, tuple[float, float]]]]:
    """Le forfait de retraite que verse le micro-entrepreneur, rapporté à son
    revenu abattu, par activité et par année (``legislation/micro_social.yaml``
    ; action 138, étape 12).

    Le compte notionnel porte ce qui a été versé : le chiffre d'affaires fois
    le taux global (D. 613-4), fois la part de base et la part complémentaire
    de D. 613-6, et non le barème du commerçant ou du libéral sur le revenu
    abattu. Chaque activité donne les deux régimes qui les reçoivent, puis,
    par année, les deux taux sur le revenu abattu : moyenne des douze mois,
    les seules années qu'une version couvre entières, comme
    ``charger_validation_micro`` ; et un troisième, la part du taux de base
    qui va à la seconde tranche de la CNAVPL (D. 642-3, 2°), dont les points
    se comptent à part (D. 643-1), nulle hors de la Cipav.
    """
    chemin = racine / "reference" / "legislation" / "micro_social.yaml"
    if not chemin.exists():
        return {}
    donnees = charger_yaml(chemin)
    table = {}
    for activite, versions in donnees["versions"].items():
        part_abattue = 1.0 - donnees["abattements"][activite]
        debuts = [tuple(int(x) for x in v["debut"].split("-")) for v in versions]
        premiere = debuts[0][0] + (0 if debuts[0][1] == 1 else 1)
        derniere = max(annee for annee, _ in debuts)
        par_annee = {}
        for annee in range(premiere, derniere + 1):
            bases, complementaires, secondes = [], [], []
            for mois in range(1, 13):
                rang = max(i for i, d in enumerate(debuts) if d <= (annee, mois))
                v = versions[rang]
                bases.append(v["taux_global"]
                             * (v["part_base"] + v.get("part_base_seconde", 0.0)))
                complementaires.append(v["taux_global"] * v["part_complementaire"])
                secondes.append(v["taux_global"] * v.get("part_base_seconde", 0.0))
            par_annee[annee] = (somme_ordonnee(bases) / 12.0 / part_abattue,
                                somme_ordonnee(complementaires) / 12.0 / part_abattue,
                                somme_ordonnee(secondes) / 12.0 / part_abattue)
        base, complementaire = donnees["regimes_du_forfait"][activite]
        table[activite] = ((base, complementaire), par_annee)
    return table


def forfait_micro(table, activite: str, annee: int
                  ) -> tuple[tuple[str, str], tuple[float, float, float]] | None:
    """Les deux régimes du forfait et leurs taux sur le revenu abattu, cette
    année-là, puis la part du taux de base qui va à la seconde tranche de la
    CNAVPL ; ``None`` avant la première année lue, où le compte porte le
    barème sur le revenu abattu ; au-delà de la dernière, la dernière."""
    entree = table.get(activite)
    if not entree:
        return None
    regimes, par_annee = entree
    if annee < min(par_annee):
        return None
    return regimes, par_annee[min(annee, max(par_annee))]


def rapport_validation_micro(table: dict[str, dict[int, float]], activite: str,
                             annee: int) -> float | None:
    """Le rapport du revenu validant au revenu abattu, cette année-là ; ``None``
    avant la première année lue, où le revenu abattu valide ; au-delà de la
    dernière, la dernière."""
    par_annee = table.get(activite)
    if not par_annee:
        return None
    premiere, derniere = min(par_annee), max(par_annee)
    if annee < premiere:
        return None
    return par_annee[min(annee, derniere)]


@une_fois_par_instantane
def charger_compensation_micro(racine: Path) -> dict:
    """La compensation de l'État aux caisses de l'auto-entrepreneur, de 2009
    à 2015 (``legislation/micro_social.yaml`` ; L. 133-6-8-2, D. 131-6-4 ;
    action 138, étape 12) : les ``activites`` qu'elle touche, et, par année,
    en heures de SMIC, le ``plancher`` que le revenu validant atteint au
    moins et le ``seuil`` du revenu abattu sous lequel rien ne valide."""
    chemin = racine / "reference" / "legislation" / "micro_social.yaml"
    if not chemin.exists():
        return {"activites": (), "plancher": {}, "seuil": {}}
    compensation = charger_yaml(chemin).get("compensation") or {}
    return {
        "activites": tuple(compensation.get("activites", ())),
        "plancher": {int(a): float(h) for a, h in (compensation.get("plancher") or {}).items()},
        "seuil": {int(a): float(h) for a, h in (compensation.get("seuil") or {}).items()},
    }


def validant_compense(compensation: dict, activite: str, annee: int, revenu: float,
                      validant: float, smic_horaire: float, part: float = 1.0) -> float:
    """Le revenu qui valide, une fois la compensation de l'État appliquée :
    rien sous le ``seuil`` — 1 885 € abattus en 2014, sous 200 heures de
    SMIC (1 906 €), ne valident plus le trimestre que 150 heures achetaient —,
    et au moins le ``plancher`` — 870 € abattus en 2009 en valident un —,
    sur une année civile entière seulement (``part``, la part de l'année
    travaillée). Un revenu pile sur le seuil est compensé : il ne lui est
    pas inférieur."""
    if activite not in compensation["activites"]:
        return validant
    seuil = compensation["seuil"].get(annee)
    if seuil is not None and revenu / (seuil * smic_horaire) + 1e-9 < 1.0:
        return 0.0
    plancher = compensation["plancher"].get(annee)
    if plancher is not None and part + 1e-9 >= 1.0:
        return max(validant, plancher * smic_horaire)
    return validant


@une_fois_par_instantane
def charger_seuils_micro(racine: Path) -> dict[str, dict[int, tuple[float, ...]]]:
    """Les seuils de 2017 à 2019 que la caisse publie, par activité et par
    année : le revenu abattu qui valide un, deux, trois et quatre trimestres
    (``legislation/micro_social.yaml`` ; action 138, étape 12).

    De 2016 à 2021, le forfait va d'abord à la CSG et à la CRDS, puis à la
    maladie, puis à la vieillesse de base (L. 133-6-8-3, L. 613-9, D. 133-4) :
    aucune clef ne fait ces seuils, que le barème de la Cnav donne en chiffre
    d'affaires, et que le modèle, qui porte le revenu abattu, abat comme lui."""
    chemin = racine / "reference" / "legislation" / "micro_social.yaml"
    if not chemin.exists():
        return {}
    donnees = charger_yaml(chemin)
    return {
        activite: {int(annee): tuple(seuil * (1.0 - donnees["abattements"][activite])
                                     for seuil in seuils)
                   for annee, seuils in par_annee.items()}
        for activite, par_annee in (donnees.get("seuils") or {}).items()
    }


def trimestres_aux_seuils_micro(table: dict[str, dict[int, tuple[float, ...]]],
                                activite: str, annee: int, revenu: float) -> int | None:
    """Les trimestres que ``revenu``, abattu, valide aux seuils publiés de
    l'année ; ``None`` les années qui n'en ont pas. Un revenu pile sur un seuil
    le valide : « CA pour valider »."""
    seuils = table.get(activite, {}).get(annee)
    if seuils is None:
        return None
    return len([seuil for seuil in seuils if revenu / seuil + 1e-9 >= 1.0])


def charger_accords_internationaux(racine: Path) -> dict[str, dict]:
    """Le tableau des accords qui coordonnent les retraites françaises avec
    celles d'un autre État : pour chaque code d'État, son ``nom``, ses
    ``accords``, dans l'ordre, et son ``salaire_moyen`` s'il en a un, leurs
    dates en AAAA-MM-JJ, telles que le paquet du site les porte
    (``data/reference/legislation/accords_internationaux.yaml``)."""
    etats = charger_yaml(racine / "reference" / "legislation"
                         / "accords_internationaux.yaml")["etats"]

    def jours(valeur):
        """Les dates en AAAA-MM-JJ, jusque dans les listes lues."""
        if isinstance(valeur, dict):
            return {cle: jours(element) for cle, element in valeur.items()}
        if isinstance(valeur, list):
            return [jours(element) for element in valeur]
        return valeur.isoformat() if hasattr(valeur, "isoformat") else valeur

    return {code: {"nom": etat["nom"],
                   "accords": [jours(accord) for accord in etat["accords"]]}
            # Les activités dont le régime de l'État est « équivalent » pour
            # le salaire annuel moyen de la pension proratisée.
            | ({"salaire_moyen": jours(etat["salaire_moyen"])}
               if etat.get("salaire_moyen") else {})
            for code, etat in etats.items()}


def charger_periodes_non_travaillees(racine: Path) -> dict[str, PeriodeNonTravaillee]:
    """Table des motifs d'interruption et de ce que chacun ouvre."""
    chemin = racine / "reference" / "legislation" / "periodes_non_travaillees.csv"
    table: dict[str, PeriodeNonTravaillee] = {}
    if not chemin.exists():
        return table
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            services, plafond_services = _services(ligne)
            table[ligne["motif"]] = PeriodeNonTravaillee(
                motif=ligne["motif"],
                trimestres_assimiles=int(ligne["trimestres_assimiles"]),
                ouvre_droits_complementaires=(
                    ligne["ouvre_droits_complementaires"].strip().lower() == "oui"
                ),
                cotisations_complementaires_versees=(
                    ligne.get("cotisations_complementaires_versees", "non")
                    .strip().lower() == "oui"
                ),
                avpf=ligne.get("avpf", "non").strip().lower() == "oui",
                services_fonction_publique=services,
                services_plafond_trimestres_par_enfant=plafond_services,
                reputes_cotises_nature=ligne.get("reputes_cotises_nature", "").strip(),
                fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
            )
    return table

@dataclass(frozen=True)
class ChomageComplementaires:
    """Ce que les régimes complémentaires font d'une année de chômage indemnisé
    (``legislation/chomage_complementaires.yaml``) : le scénario 1 en tire les
    points, le compte notionnel ce qui a été versé. Le jumeau JavaScript est
    ``ChomageComplementaires`` de ``carriere.js``.
    """

    #: Motif de ``periodes_non_travaillees.csv`` → « assurance », « solidarite »
    #: ou « fne » (l'allocation spéciale du Fonds national de l'emploi).
    motifs: tuple[tuple[str, str], ...] = ()
    #: Borne du salaire de référence, en plafonds de la sécurité sociale.
    plafond_salaire_reference: float | None = None
    #: Premier mois validé, régime par régime : (code, année, mois).
    validation_depuis: tuple[tuple[str, int, int], ...] = ()
    #: Premier mois validé pour une affiliation que l'assurance chômage a
    #: couverte plus tard : (affiliation, année, mois).
    validation_depuis_affiliations: tuple[tuple[str, int, int], ...] = ()
    #: Affiliations dont le chômage n'est jamais validé : un autre régime que
    #: l'assurance chômage l'indemnise — la CAFAT en Nouvelle-Calédonie.
    sans_validation: frozenset[str] = frozenset()
    #: Année de naissance de la solidarité — celle de l'allocation, ou celle
    #: de la convention de l'allocation spéciale du FNE —, et part de ses
    #: cotisations que l'État verse.
    solidarite_depuis: int = 0
    solidarite_versement: float = 0.0
    #: Taux de la solidarité : (code, taux, première année de la rupture du
    #: contrat ou de la convention dont les points le prennent).
    solidarite_taux: tuple[tuple[str, float, int], ...] = ()
    #: Ce que l'Unédic verse : la part de la cotisation, et la part de
    #: l'assiette prise sur la participation de l'allocataire.
    assurance_part_cotisation: float = 1.0
    assurance_participation_reversee: float = 0.0
    #: Participation de l'allocataire : (année, mois, taux), dans l'ordre.
    participation: tuple[tuple[int, int, float], ...] = ()
    #: Jusqu'à cette année, une période plus courte que ce nombre de jours
    #: n'est pas validée.
    duree_minimale_jusqu: int = 0
    duree_minimale_jours: int = 0
    #: Borne du salaire de référence de l'allocation spéciale du FNE, en
    #: plafonds, pour une convention de l'année dite ou d'après.
    fne_plafond_salaire_reference: float | None = None
    fne_plafond_depuis: int = 0
    #: Premier mois où l'indemnisation cesse à l'âge légal pour qui a la
    #: durée requise (année, mois) ; l'âge d'annulation de la décote la coupe
    #: de tout temps (L. 5421-4 du code du travail).
    fin_indemnisation_duree_depuis: tuple[int, int] | None = None

    def nature(self, motif: str, annee: int, debut: int | None = None) -> str | None:
        """« assurance », « solidarite », « fne », ou ``None`` pour un motif
        qui n'est pas du chômage. La solidarité d'avant le 1er avril 1984 est
        de l'assurance : le régime était unique. L'allocation spéciale du FNE
        l'est quand sa convention est d'avant (``debut``, :meth:`debuts`) : le
        guide valide ces conventions-là « dans les mêmes conditions que les
        allocataires du régime d'assurance chômage », jusqu'au bout."""
        nature = dict(self.motifs).get(motif)
        date = debut if nature == "fne" and debut is not None else annee
        if nature in ("solidarite", "fne") and date < self.solidarite_depuis:
            return "assurance"
        return nature

    def debuts(self, lignes) -> dict[tuple[int, str], int]:
        """L'année qui tient lieu de date à une année de solidarité ou de
        préretraite, (année, motif) → année : pour l'allocation spéciale du
        FNE, celle de la convention, que le modèle prend au premier millésime
        de la préretraite ; pour l'allocation de solidarité, celle de la
        rupture du contrat, le premier millésime du chômage qui la précède sans
        emploi entre-temps, l'année où un emploi a pris fin comprise. Les
        lignes ne disent ni l'une ni l'autre."""
        motifs: dict[int, set[str]] = {}
        emploi: set[int] = set()
        for ligne in lignes:
            motifs.setdefault(ligne.annee, set()).add(ligne.type_periode)
            if ligne.cotise:
                emploi.add(ligne.annee)
        chomage = {motif for motif, nature in self.motifs
                   if nature in ("assurance", "solidarite")} | {"chomage_non_indemnise"}
        resultat: dict[tuple[int, str], int] = {}
        for annee, presents in motifs.items():
            for motif in presents:
                nature = dict(self.motifs).get(motif)
                debut = annee
                if nature == "fne":
                    while motif in motifs.get(debut - 1, ()):
                        debut -= 1
                elif nature == "solidarite":
                    while debut not in emploi and motifs.get(debut - 1, set()) & chomage:
                        debut -= 1
                else:
                    continue
                resultat[(annee, motif)] = debut
        return resultat

    def part_validee(self, code: str, annee: int,
                     affiliation: str | None = None) -> float:
        """Part de l'année que le régime ``code`` valide au titre du chômage :
        rien avant son premier jour, ni avant celui de l'affiliation, les mois
        qui le suivent l'année même ; rien du tout pour une affiliation dont
        un autre régime que l'assurance chômage indemnise le chômage."""
        if affiliation in self.sans_validation:
            return 0.0
        part = 1.0
        for cle, dates in ((code, self.validation_depuis),
                           (affiliation, self.validation_depuis_affiliations)):
            for nom, depuis, mois in dates:
                if nom == cle:
                    if annee < depuis:
                        return 0.0
                    if annee == depuis:
                        part = min(part, (13 - mois) / 12)
        return part

    def assez_long(self, annee: int, fraction: float) -> bool:
        """La période, qui dure ``fraction`` de l'année, dure-t-elle assez pour
        être validée ? Jusqu'en 1973, trente jours au moins ; ensuite, sans
        condition de durée. Un mois en vaut 365/12 : le modèle, qui compte en
        mois, ne tombe sous la borne qu'avec une ligne plus courte."""
        return (annee > self.duree_minimale_jusqu
                or fraction * 365 >= self.duree_minimale_jours)

    def plafond_preretraite(self, debut: int | None) -> float | None:
        """Borne du salaire de référence de l'allocation spéciale du FNE, en
        plafonds, pour une convention de l'année ``debut`` : deux pour une
        convention conclue depuis le 5 mai 1997, que le modèle date de 1998 ;
        ``None`` avant, la borne commune de quatre plafonds valant seule."""
        if (self.fne_plafond_salaire_reference is None or debut is None
                or debut < self.fne_plafond_depuis):
            return None
        return self.fne_plafond_salaire_reference

    def taux_solidarite(self, code: str, annee: int, points: bool,
                        rupture: int | None = None) -> float | None:
        """Taux contractuel de la solidarité au régime ``code`` : celui que
        prennent les points (``points``), ou celui que l'État finance.
        ``None`` : le régime traite cette année de solidarité comme
        l'assurance. L'Arrco ne sert ses 4 % qu'après une rupture du contrat,
        ou une convention du FNE, du 1er juin 2000 ou d'après (``rupture``,
        :meth:`debuts`) : avant, les taux obligatoires, quelle que soit
        l'année de l'allocation."""
        if annee < self.solidarite_depuis:
            return None
        date = annee if rupture is None else rupture
        for regime, taux, depuis in self.solidarite_taux:
            if regime == code:
                return None if points and date < depuis else taux
        return None

    def taux_participation(self, annee: int) -> float:
        """Participation de l'allocataire, en part du salaire de référence :
        la moyenne des mois de l'année, ou le taux de l'année entière."""
        taux_des_mois = []
        for mois in range(1, 13):
            taux = 0.0
            for depuis, debut, valeur in self.participation:
                if (depuis, debut) <= (annee, mois):
                    taux = valeur
            taux_des_mois.append(taux)
        if len(set(taux_des_mois)) == 1:
            return taux_des_mois[0]
        return somme_ordonnee(taux_des_mois) / 12


_CHOMAGE_COMPLEMENTAIRES: dict[tuple[str, int, int], ChomageComplementaires] = {}


@une_fois_par_instantane
def charger_chomage_complementaires(racine: Path) -> ChomageComplementaires:
    """Les règles du chômage aux régimes complémentaires, gardées comme les
    autres points de passage du disque, indexées sur la signature du fichier ;
    sans fichier, aucune règle."""
    chemin = racine / "reference" / "legislation" / "chomage_complementaires.yaml"
    if not chemin.exists():
        return ChomageComplementaires()
    etat = chemin.stat()
    cle = (str(chemin), etat.st_mtime_ns, etat.st_size)
    if cle in _CHOMAGE_COMPLEMENTAIRES:
        return _CHOMAGE_COMPLEMENTAIRES[cle]
    brut = charger_yaml(chemin)
    solidarite = brut.get("solidarite") or {}
    assurance = brut.get("assurance") or {}
    duree_minimale = brut.get("duree_minimale") or {}
    fne = brut.get("fne") or {}
    fin = brut.get("fin_indemnisation") or {}
    regles = ChomageComplementaires(
        motifs=tuple(sorted((brut.get("motifs") or {}).items())),
        plafond_salaire_reference=brut.get("plafond_salaire_reference"),
        validation_depuis=tuple(
            (code, jour.year, jour.month)
            for code, jour in sorted((brut.get("validation_depuis") or {}).items())
        ),
        validation_depuis_affiliations=tuple(
            (affiliation, jour.year, jour.month)
            for affiliation, jour in sorted(
                (brut.get("validation_depuis_affiliations") or {}).items())
        ),
        sans_validation=frozenset(brut.get("sans_validation") or ()),
        solidarite_depuis=int(solidarite.get("depuis", 0)),
        solidarite_versement=float(solidarite.get("versement", 0.0)),
        solidarite_taux=tuple(
            (code, float(regle["taux"]), int(regle.get("points_depuis", 0)))
            for code, regle in sorted((solidarite.get("taux") or {}).items())
        ),
        assurance_part_cotisation=float(assurance.get("part_cotisation", 1.0)),
        assurance_participation_reversee=float(
            assurance.get("participation_reversee", 0.0)),
        participation=tuple(sorted(
            (palier["depuis"].year, palier["depuis"].month, float(palier["taux"]))
            for palier in brut.get("participation_allocataire") or ()
        )),
        duree_minimale_jusqu=int(duree_minimale.get("jusqu", 0)),
        duree_minimale_jours=int(duree_minimale.get("jours", 0)),
        fne_plafond_salaire_reference=fne.get("plafond_salaire_reference"),
        fne_plafond_depuis=int(fne.get("plafond_depuis", 0)),
        fin_indemnisation_duree_depuis=(
            None if fin.get("duree_depuis") is None
            else (fin["duree_depuis"].year, fin["duree_depuis"].month)),
    )
    _CHOMAGE_COMPLEMENTAIRES[cle] = regles
    return regles
