"""Primitives de chargement, avec suivi de la fiabilité des données.

Principe directeur : aucune valeur ne circule dans le modèle sans son niveau de
fiabilité. Une simulation qui repose sur des séries reconstituées doit le dire,
et doit pouvoir refuser de s'exécuter si l'utilisateur exige mieux.
"""

from __future__ import annotations

import copy
import csv
import json
import pickle
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Iterator

import yaml


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

    Deux comportements sont distingués :

    * ``escalier`` (défaut) — la valeur d'une année absente est celle de la
      dernière année renseignée. C'est le comportement correct pour des
      paramètres juridiques : un taux reste en vigueur jusqu'à sa modification.
    * ``lineaire`` — interpolation entre les deux années encadrantes. Correct
      pour des grandeurs continues : l'espérance de vie à 60 ans est désormais
      renseignée chaque année, celle à 65 ans ne l'est qu'avant 1986 par points
      espacés, et c'est là que l'interpolation sert encore.
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

        if self.interpolation == "escalier":
            return ValeurAnnuelle(annee, avant.valeur, avant.fiabilite)

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
        return _copie(_YAML_EN_CACHE[cle])
    with chemin.open(encoding="utf-8") as flux:
        contenu = yaml.load(flux, Loader=_LECTEUR) or {}
    if cle is not None:
        _YAML_EN_CACHE[cle] = _a_garder(contenu)
    return contenu


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
    #: Le parent est-il affilié à l'assurance vieillesse des parents au foyer
    #: pendant cette période ? La CNAF cotise alors au régime général sur une
    #: assiette forfaitaire égale au SMIC, et ce salaire est PORTÉ AU COMPTE :
    #: c'est ce qui distingue l'AVPF d'une période assimilée, laquelle valide
    #: des trimestres sans jamais ajouter de salaire.
    avpf: bool = False
    fiabilite: Fiabilite = Fiabilite.ESTIMEE


def charger_periodes_non_travaillees(racine: Path) -> dict[str, PeriodeNonTravaillee]:
    """Table des motifs d'interruption et de ce que chacun ouvre."""
    chemin = racine / "reference" / "legislation" / "periodes_non_travaillees.csv"
    table: dict[str, PeriodeNonTravaillee] = {}
    if not chemin.exists():
        return table
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        for ligne in csv.DictReader(lignes):
            table[ligne["motif"]] = PeriodeNonTravaillee(
                motif=ligne["motif"],
                trimestres_assimiles=int(ligne["trimestres_assimiles"]),
                ouvre_droits_complementaires=(
                    ligne["ouvre_droits_complementaires"].strip().lower() == "oui"
                ),
                avpf=ligne.get("avpf", "non").strip().lower() == "oui",
                fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
            )
    return table
