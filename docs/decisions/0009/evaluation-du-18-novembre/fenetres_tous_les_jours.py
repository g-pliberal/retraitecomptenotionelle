"""L'essai de fenetres.py, refait sur chaque jour de naissance de 1923 à 1975."""
import datetime as dt
import fenetres as f

ecarts = []; refermes = []; n = 0
jour = dt.date(1923, 1, 1)
while jour <= dt.date(1975, 12, 31):
    naissance = jour
    par_table = f.premier_du_mois_a_partir(f.atteint(naissance, f.fusionnee(naissance)))
    ouvert_avant = False; premier = None
    for e in f.effets(dt.date(naissance.year + 59, 1, 1), dt.date(naissance.year + 66, 1, 1)):
        if e < dt.date(1983, 4, 1): continue
        ok = f.atteint(naissance, f.version(e)(naissance)) <= e
        if ok and premier is None: premier = e
        if ouvert_avant and not ok: refermes.append((naissance, e))
        ouvert_avant = ok
    n += 1
    if premier != par_table and par_table >= dt.date(1983, 4, 1):
        ecarts.append((naissance, par_table, premier))
    jour += dt.timedelta(days=1)
print(n, "naissances ;", len(ecarts), "écarts ;", len(refermes), "droits ouverts puis refermés")
for e in ecarts[:10]: print("  écart :", *e)
for e in refermes[:10]: print("  refermé :", *e)
