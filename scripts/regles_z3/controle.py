"""La question posée à Z3, et les cas attendus qui l'excusent.

Pour une propriété, Z3 cherche un contre-exemple HORS des cas attendus qui la
nomment : s'il n'en trouve aucun, elle est prouvée sur tout son champ, à ces
cas près ; s'il en trouve, ce sont des surprises, rendues chiffrées. Chaque cas
attendu est ensuite cherché seul : une déclaration que plus rien ne réalise
(le droit ou le moteur a changé) se signale aussi."""
from __future__ import annotations

import datetime
import time
from dataclasses import dataclass, field

import z3

from .calcul import ecrire_jour, ecrire_mois, entier_du_jour

DELAI_MS = 600_000      # au-delà, la propriété est « indécise »


@dataclass
class Resultat:
    propriete: object
    statut: str = "prouvee"          # prouvee, attendue, surprise, indecise
    surprises: list = field(default_factory=list)
    attendus: list = field(default_factory=list)   # (attendu, exemple)
    disparus: list = field(default_factory=list)
    duree: float = 0.0


def _valeur(genre: str, v):
    if genre == "mois":
        a, m = map(int, str(v).split("-")[:2])
        return a * 12 + m - 1
    if genre == "jour":
        return entier_du_jour(v)
    return int(v)


def _ecrire(genre: str, n: int):
    return ecrire_mois(n) if genre == "mois" else ecrire_jour(n) if genre == "jour" else n


def contrainte(prop, attendu):
    """Le cas attendu, en contrainte : une valeur, ou un intervalle [a, b]
    fermé, une borne nulle ne bornant pas."""
    parts = []
    for nom, v in attendu["cas"].items():
        terme, genre = prop.champs[nom]
        if isinstance(v, list):
            a, b = v
            if a is not None:
                parts.append(terme >= _valeur(genre, a))
            if b is not None:
                parts.append(terme <= _valeur(genre, b))
        else:
            parts.append(terme == _valeur(genre, v))
    return z3.And(*parts) if parts else z3.BoolVal(True)


def _exemple(prop, mod) -> dict:
    champs = {nom: _ecrire(genre, mod.eval(t, model_completion=True).as_long())
              for nom, (t, genre) in prop.champs.items()}
    return {"champs": champs, "texte": prop.lire(mod)}


def _solveur(prop, *contraintes):
    s = z3.Solver()
    s.set("timeout", DELAI_MS)
    s.add(*prop.hypotheses, *contraintes)
    return s


def realise(prop, attendu):
    """Un contre-exemple que le cas attendu couvre ; None s'il n'y en a plus.
    De préférence né depuis 1900 et pensionné depuis 1945 : l'exemple se lit
    mieux."""
    s = _solveur(prop, contrainte(prop, attendu))
    s.push()
    s.add(*[t >= (1900 * 12 if nom.startswith("ne") else 1945 * 12)
            for nom, (t, genre) in prop.champs.items() if genre == "mois"])
    if s.check() == z3.sat:
        return _exemple(prop, s.model())
    s.pop()
    return _exemple(prop, s.model()) if s.check() == z3.sat else None


def verifier(prop, attendus, maximum: int = 3) -> Resultat:
    t0 = time.time()
    miens = [a for a in attendus if a["propriete"] == prop.id]
    r = Resultat(prop)
    s = _solveur(prop, *([z3.Not(z3.Or(*[contrainte(prop, a) for a in miens]))] if miens else []))
    while len(r.surprises) < maximum:
        issue = s.check()
        if issue == z3.unknown:
            r.statut = "indecise"
            break
        if issue == z3.unsat:
            break
        mod = s.model()
        r.surprises.append(_exemple(prop, mod))
        s.add(z3.Or(*[t != mod.eval(t, model_completion=True) for t, _ in prop.champs.values()]))
    for a in miens:
        ex = realise(prop, a)
        if ex is None:
            r.disparus.append(a)
        else:
            r.attendus.append((a, ex))
    if r.surprises:
        r.statut = "surprise"
    elif r.statut != "indecise" and r.attendus:
        r.statut = "attendue"
    r.duree = time.time() - t0
    return r


def comparer(regle, lignes, maximum: int = 20):
    """La règle exécutée contre ce que rend le moteur : (n, écarts), un écart
    étant ((génération, date), valeur du moteur, valeur de la règle)."""
    n, ecarts = 0, []
    for g, d, attendu in lignes:
        n += 1
        nous = regle(g, d)
        if nous != attendu and len(ecarts) < maximum:
            ecarts.append(((g, d), attendu, nous))
    return n, ecarts
