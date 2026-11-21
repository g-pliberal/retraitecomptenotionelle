"""La pension de base du régime général rapportée au salaire annuel moyen, en
arithmétique exacte, pour Z3 :

    pension / SAM = taux × min(T, D) / D × (1 + surcote)
    taux = 50 % × (1 − c × n),  n = min(manque de durée, manque d'âge, 20)

T, trimestres validés (un seul régime) ; la durée requise de `duree`, à la date
d'effet ; D, durée de proratisation : min(table, durée requise) ; c, âges
d'ouverture et d'annulation : les tables du moteur (`moteur.extraire`). Le
taux de 50 % et les vingt trimestres sont ceux de R. 351-27 et de la décote du
moteur ; la surcote, celle de `coefficientSurcoteDatee` (circulaire Cnav
2018-04) : chaque trimestre civil entier après le trimestre de l'âge légal
(celui de la version de la date d'effet), après la durée requise et après le
1er janvier 2004, au taux de la version de la fiche `surcote_regime_general`
que la date d'effet choisit, taux lus dans le paquet.

Hors champ : majoration de durée après le taux plein, minimum contributif,
carrière longue, inaptitude. Assuré né le 1er du mois, pension au 1er d'un mois
depuis le 1er avril 1983 ; pour la surcote, CARRIÈRE CONTINUE : un trimestre
cotisé par trimestre civil jusqu'au départ, ses T − durée requise derniers
trimestres étant ceux d'après la durée requise."""
from __future__ import annotations

from fractions import Fraction

import z3

from . import duree, fiches
from .calcul import Z3, gen, rang_du_jour

R = lambda v: z3.RealVal(str(Fraction(str(v))))
zmax = lambda a, b: z3.If(a > b, a, b)
zmin = lambda a, b: z3.If(a < b, a, b)
mois_entiers = lambda v: round(v * 12)


def date_effet(m):
    """Le 1er du mois m, en AAAAMMJJ."""
    return (m / 12) * 10000 + (m % 12 + 1) * 100 + 1


class Modele:
    def __init__(self, racine, extrait, versions_duree=None, paquet=None):
        self.tables = extrait["tables"]
        versions_duree = versions_duree or duree.lire_versions(racine)
        self.rg = duree.regle(versions_duree, Z3, extrait["durees_avant_le_decret"])
        F = paquet or fiches.charger(racine)
        self.L = fiches.age_legal(Z3, F)
        self.surcotes = fiches.versions_triees(F["surcote_regime_general"])

    def par_paliers(self, cle, g, conv):
        """La table du moteur, en paliers de générations, comme terme Z3."""
        t = self.tables
        paliers = [(t[0]["mois"], t[0][cle])]
        for x in t[1:]:
            if x[cle] != paliers[-1][1]:
                paliers.append((x["mois"], x[cle]))
        terme = conv(paliers[0][1])
        for debut, v in paliers[1:]:
            terme = z3.If(g >= debut, conv(v), terme)
        return terme

    # ------------------------------------------------------------ surcote
    @staticmethod
    def _surcote_de_la_version(v, g, s, e):
        """La somme des taux des trimestres civils [s, e), rangés 1, 2, …,
        sous la version v. Les lignes du paquet sont de trois formes : le taux
        de tout trimestre depuis une date, celui des trimestres de rang 5 et
        plus, celui des trimestres d'après l'âge majoré ; la meilleure
        l'emporte, ce qui se compte en trois parts."""
        p = v["parametres"]
        lignes = p["lignes"]
        if not lignes:
            return R(0)
        q_majore = None if p["age_majore"] is None else (g + 12 * p["age_majore"]) / 3
        base = [l for l in lignes if not l["apres_l_age_majore"] and l["rang_minimum"] == 1]
        rang5 = [l for l in lignes if l["rang_minimum"] == 5]
        majo = [l for l in lignes if l["apres_l_age_majore"]]
        if len(lignes) != len(base) + len(rang5) + len(majo):
            raise ValueError(f"surcote, version {v['id']} : une ligne d'une forme inconnue")
        t_base = {l["taux"] for l in base if l["avant"] is not None} or {l["taux"] for l in base}
        (t1,) = t_base
        t5 = rang5[0]["taux"] if rang5 else t1
        premier = min((l["depuis"] for l in base), default=None)
        forts = [l for l in base if l["avant"] is None and l["depuis"] != premier]
        X = None
        if majo:
            X = q_majore + 1
            tfort = majo[0]["taux"]
        if forts:
            (f,) = forts
            qf = rang_du_jour(f["depuis"]) // 3
            X = qf if X is None else zmin(X, qf)
            if majo and majo[0]["taux"] != f["taux"]:
                raise ValueError(f"surcote, version {v['id']} : deux taux forts")
            tfort = f["taux"]
        if X is None:
            return R(t1) * z3.ToReal(zmax(0, e - s))
        avant = zmax(0, zmin(e, X) - s)
        n1 = zmin(4, avant) if rang5 else avant
        return (R(t1) * z3.ToReal(n1) + R(t5) * z3.ToReal(avant - n1)
                + R(tfort) * z3.ToReal(zmax(0, e - zmax(s, X))))

    def surcote(self, g, m, T, requis):
        debut_age = (g + self.L(g, m)) / 3 + 1
        e = m / 3
        debut_duree = e - (T - requis)
        premier = min(rang_du_jour(l["depuis"]) for v in self.surcotes
                      for l in v["parametres"]["lignes"]) // 3
        s = zmax(zmax(debut_age, premier), debut_duree)
        total = R(0)
        for v in reversed(self.surcotes):
            a, b = v["bornes"]["liquidation.date_effet"]
            dedans = z3.And(*([m >= rang_du_jour(a)] if a else []), *([m < rang_du_jour(b)] if b else []))
            total = z3.If(dedans, self._surcote_de_la_version(v, g, s, e), total)
        return z3.If(T > requis, total, R(0)), s, e

    # ------------------------------------------------------------ pension
    def pension(self, g, m, T, avec_surcote=True):
        """Pension / SAM, et ses pièces."""
        a = m - g
        requis = self.rg(g, date_effet(m))
        A = self.par_paliers("annulation", g, mois_entiers)
        c = self.par_paliers("coefficient", g, R)
        table = self.par_paliers("proratisation", g, lambda v: 0 if v is None else v)
        D = z3.If(z3.And(table != 0, table < requis), table, requis)
        par_duree = zmax(requis - T, 0)
        par_age = z3.If(A - a > 0, (A - a + 2) / 3, 0)       # au trimestre supérieur
        n = zmin(zmin(par_duree, par_age), 20)
        taux = R("0.5") * (1 - c * z3.ToReal(n))
        if avec_surcote:
            sc, s, e = self.surcote(g, m, T, requis)
        else:
            sc, s, e = R(0), m / 3, m / 3
        p = taux * z3.ToReal(zmin(T, D)) / z3.ToReal(D) * (1 + sc)
        return p, dict(requis=requis, n=n, taux=taux, D=D, surcote=sc, s=s, e=e,
                       taux_liquidation=taux * (1 + sc))

    def admis(self, g, m, T):
        """Une pension possible : né de 1900 à 2010, à l'âge d'ouverture au
        moins, de 1983 à 2079, au moins un trimestre, au plus quatre par an
        depuis 14 ans."""
        O = self.par_paliers("ouverture", g, mois_entiers)
        return z3.And(g >= gen(1900, 1), g < gen(2011, 1), m >= gen(1983, 4), m < gen(2080, 1),
                      m - g >= O, T >= 1, T <= 4 * ((m - g) / 12 - 14))
