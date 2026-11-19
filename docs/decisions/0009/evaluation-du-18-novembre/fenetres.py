"""Essai : l'âge légal en cinq versions choisies à la date d'effet, contre la table fusionnée.
Âges en mois. Générations : (année, mois, jour) de naissance."""
import datetime as dt

def m(ans, mois=0):
    return ans * 12 + mois

def table_2010(n):
    if n < dt.date(1951, 7, 1): return m(60)
    if n <= dt.date(1951, 12, 31): return m(60, 4)
    if n.year == 1952: return m(60, 8)
    if n.year == 1953: return m(61)
    if n.year == 1954: return m(61, 4)
    if n.year == 1955: return m(61, 8)
    return m(62)

def table_2011(n):
    if n < dt.date(1951, 7, 1): return m(60)
    if n <= dt.date(1951, 12, 31): return m(60, 4)
    if n.year == 1952: return m(60, 9)
    if n.year == 1953: return m(61, 2)
    if n.year == 1954: return m(61, 7)
    return m(62)

def table_2023(n):
    if n < dt.date(1961, 9, 1): return table_2011(n)
    if n.year == 1961: return m(62, 3)
    if n.year == 1962: return m(62, 6)
    if n.year == 1963: return m(62, 9)
    if n.year == 1964: return m(63)
    if n.year == 1965: return m(63, 3)
    if n.year == 1966: return m(63, 6)
    if n.year == 1967: return m(63, 9)
    return m(64)

def table_2025(n):
    if n < dt.date(1961, 9, 1): return table_2023(n)   # « sa rédaction antérieure »
    if n.year == 1961: return m(62, 3)
    if n.year == 1962: return m(62, 6)
    if n < dt.date(1965, 4, 1): return m(62, 9)
    if n.year == 1965: return m(63)
    if n.year == 1966: return m(63, 3)
    if n.year == 1967: return m(63, 6)
    if n.year == 1968: return m(63, 9)
    return m(64)

VERSIONS = [  # (première date d'effet, table)
    (dt.date(1983, 4, 1), lambda n: m(60)),
    (dt.date(2011, 7, 1), table_2010),
    (dt.date(2011, 12, 23), table_2011),
    (dt.date(2023, 9, 1), table_2023),
    (dt.date(2026, 9, 1), table_2025),
]
fusionnee = table_2025   # la plus récente l'emportant, génération par génération

def version(effet):
    t = None
    for debut, table in VERSIONS:
        if effet >= debut: t = table
    return t

def atteint(naissance, age_mois):
    """Le jour où l'âge est atteint."""
    a, mo = divmod((naissance.month - 1) + age_mois, 12)
    an = naissance.year + a
    jour = naissance.day
    while True:
        try:
            return dt.date(an, mo + 1, jour)
        except ValueError:
            jour -= 1

def premier_du_mois_a_partir(d):
    if d.day == 1: return d
    return dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)

def effets(debut, fin):
    d = debut
    while d <= fin:
        yield d
        d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)

ecarts = []; non_monotones = []; n = 0
for an in range(1923, 1976):
    for mois in range(1, 13):
        for jour in (1, 2, 15, 28):
            naissance = dt.date(an, mois, jour)
            par_table = premier_du_mois_a_partir(atteint(naissance, fusionnee(naissance)))
            ouvert_avant = False; premier = None
            for e in effets(dt.date(an + 59, 1, 1), dt.date(an + 66, 1, 1)):
                if e < dt.date(1983, 4, 1): continue
                ok = atteint(naissance, version(e)(naissance)) <= e
                if ok and premier is None: premier = e
                if ouvert_avant and not ok: non_monotones.append((naissance, e))
                ouvert_avant = ok
            n += 1
            if premier != par_table and par_table >= dt.date(1983, 4, 1):
                ecarts.append((naissance, par_table, premier))
print(n, "naissances essayées ;", len(ecarts), "écarts ;", len(non_monotones), "droits ouverts puis refermés")
for e in ecarts[:20]: print("  écart :", *e)
for e in non_monotones[:20]: print("  refermé :", *e)
