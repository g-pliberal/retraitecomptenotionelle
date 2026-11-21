"""Les deux calculs d'une règle, et les unités communes.

Une génération est un mois de naissance, ``annee * 12 + (mois - 1)`` ; une date
d'effet au 1er d'un mois, le même rang ; un âge, un nombre de mois. La durée
requise, dont les versions se bornent au jour, prend la date en entier
``AAAAMMJJ``."""
from __future__ import annotations

import datetime

import z3

AUCUN = -1   # « la version ne dit rien »


class Py:
    """Le calcul ordinaire : des entiers et des booléens Python."""
    If = staticmethod(lambda c, a, b: a if c else b)
    And = staticmethod(lambda *xs: all(xs))
    Or = staticmethod(lambda *xs: any(xs))


class Z3:
    """Le même calcul, en termes que Z3 sait interroger."""
    If = staticmethod(z3.If)
    And = staticmethod(lambda *xs: z3.And(*xs) if xs else z3.BoolVal(True))
    Or = staticmethod(lambda *xs: z3.Or(*xs) if xs else z3.BoolVal(False))


def dans(B, lo, hi, x):
    """lo <= x < hi, une borne absente ne bornant pas."""
    return B.And(*([lo <= x] if lo is not None else []), *([x < hi] if hi is not None else []))


def mois(x):
    """Des années décimales (1961.667, 62.75) au mois entier le plus proche."""
    return None if x is None else round(x * 12)


def gen(annee: int, mois_: int) -> int:
    return annee * 12 + mois_ - 1


def rang_du_jour(s):
    """Le rang du premier 1er du mois qui n'est pas avant le jour s : une
    version qui commence le 21 décembre 1985 vaut pour les pensions du
    1er janvier 1986."""
    if s is None:
        return None
    a, m, j = map(int, str(s).split("-"))
    return a * 12 + m - 1 + (1 if j > 1 else 0)


def entier_du_jour(s):
    if s is None:
        return None
    if isinstance(s, datetime.date):
        return s.year * 10000 + s.month * 100 + s.day
    return int(str(s).replace("-", ""))


def ecrire_mois(rang: int) -> str:
    """Le rang d'un mois, en ``AAAA-MM`` (la forme des cas attendus)."""
    return f"{rang // 12}-{rang % 12 + 1:02d}"


def ecrire_jour(entier: int) -> str:
    return f"{entier // 10000}-{entier // 100 % 100:02d}-{entier % 100:02d}"


def mois_lu(rang: int) -> str:
    """Le rang d'un mois, pour un lecteur : ``08/2026``."""
    return f"{rang % 12 + 1:02d}/{rang // 12}"


def jour_lu(entier: int) -> str:
    return f"{entier % 100:02d}/{entier // 100 % 100:02d}/{entier // 10000}"


def age_ecrit(m: int) -> str:
    if m == AUCUN:
        return "aucun"
    return f"{m // 12} ans" + (f" {m % 12} mois" if m % 12 else "")
