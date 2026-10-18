"""Le portage calcule ``exp``, ``log`` et ``pow`` comme la libm de Linux.

Le moteur Python tient ses ``math.exp``, ``math.log`` et ``**`` de la libm
de sa plateforme ; ``moteur/js/libm.js`` refait celles de la glibc, depuis sa
version 2.28, sur x86_64 avec la multiplication-addition fusionnée (FMA) : la
machine de GitHub, où la suite fabrique les témoins. Le pont du coût (action
161, étape 5) veut les témoins et les agrégats identiques à l'octet, quel que
soit le moteur qui les calcule : le portage doit rendre, au bit près, ce que
rend la libm du Python.

La confrontation ne vaut que sur cette plateforme-là : ailleurs, la libm du
Python est une autre (celle de Windows, de macOS), et le test se tait. La
multiplication-addition fusionnée, elle, se confronte partout, à un calcul en
rationnels exacts. ``tests/js/libm.test.js`` fixe en plus, pour node seul,
les valeurs spéciales et des cas où V8 s'écarte de la glibc.
"""

from __future__ import annotations

import json
import math
import platform
import random
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
LIBM = RACINE / "moteur" / "js" / "libm.js"

#: Le programme node : il lit les entrées en JSON, et rend les résultats.
PROGRAMME = f"""
import {{ readFileSync }} from "node:fs";
import {{ exp, fma, log, pow }} from {json.dumps(LIBM.as_uri())};
const d = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify({{
  exp: d.exp.map((x) => exp(x)),
  log: d.log.map((x) => log(x)),
  pow: d.pow.map(([x, y]) => pow(x, y)),
  fma: d.fma.map(([a, b, c]) => fma(a, b, c)),
}}));
"""


def _hors_reference() -> str | None:
    """Pourquoi la libm du Python n'est pas celle que le portage refait, ou
    ``None`` quand elle l'est."""
    if sys.platform != "linux" or platform.machine() != "x86_64":
        return f"{sys.platform} {platform.machine()}, non Linux x86_64"
    nom, version = platform.libc_ver()
    if nom != "glibc" or tuple(int(v) for v in version.split(".")[:2]) < (2, 28):
        return f"libc {nom} {version}, non glibc 2.28 ou après"
    try:
        drapeaux = next(ligne for ligne in Path("/proc/cpuinfo").read_text().splitlines()
                        if ligne.startswith("flags")).split()
    except (OSError, StopIteration):
        return "/proc/cpuinfo illisible"
    if "fma" not in drapeaux or "avx2" not in drapeaux:
        return "processeur sans FMA ni AVX2 : la glibc y prend une autre variante"
    return None


def _portage(entrees: dict) -> dict:
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", PROGRAMME], input=json.dumps(entrees),
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    # Un flottant entier s'écrit sans virgule : il se relit en flottant.
    return json.loads(execution.stdout, parse_int=float)


def _echantillon() -> dict:
    """Les plages que le moteur emploie — survies, forces de mortalité,
    capitalisations —, puis tout l'éventail des flottants finis."""
    alea = random.Random(20261018)

    def large(bas: int = -1000, haut: int = 1000) -> float:
        return math.ldexp(alea.uniform(1.0, 2.0), alea.randint(bas, haut))

    exp_ = ([-alea.uniform(0.0, 1.0) for _ in range(6000)]
            + [alea.uniform(-10.0, 10.0) for _ in range(6000)]
            + [alea.uniform(-700.0, 700.0) for _ in range(3000)])
    log_ = ([alea.uniform(0.93, 1.07) for _ in range(6000)]
            + [alea.uniform(0.01, 3.0) for _ in range(6000)]
            + [large() for _ in range(3000)])
    pow_ = ([[1.0 + alea.uniform(0.0, 0.06), alea.randint(0, 80) + alea.choice((0.0, 0.5))]
             for _ in range(5000)]
            + [[alea.uniform(0.5, 1.0), alea.uniform(0.3, 3.0)] for _ in range(5000)]
            + [[alea.uniform(0.1, 10.0), alea.uniform(-30.0, 30.0)] for _ in range(4000)]
            + [[-alea.uniform(0.5, 2.0), float(alea.randint(-40, 40))] for _ in range(1000)])
    fma_ = []
    for _ in range(3000):
        # L'annulation, que seule la fusion rend juste.
        a, b = alea.uniform(-2.0, 2.0), alea.uniform(-2.0, 2.0)
        fma_.append([a, b, -(a * b) * alea.choice((1.0, 1.0 + 2.0 ** -52, 1.0 - 2.0 ** -53))])
    for _ in range(3000):
        fma_.append([alea.uniform(0.7, 1.4), alea.uniform(0.7, 1.4), -1.0])
    for _ in range(3000):
        # Hors de [2^-400, 2^400], le calcul en entiers exacts, sous-normaux compris.
        fma_.append([large(-560, 500) * alea.choice((1.0, -1.0)), large(-560, 500),
                     large() * alea.choice((1.0, -1.0))])
    return {"exp": exp_, "log": log_, "pow": pow_, "fma": fma_}


def _bits(x: float) -> str:
    return x.hex()


#: Les modules du portage qui ne calculent rien que le moteur Python calcule :
#: la présentation et la lecture des documents déposés. Eux seuls gardent les
#: fonctions de leur navigateur.
SANS_LIBM = {
    "libm.js": "le module lui-même",
    "pages.js": "le texte des pages, qui met en forme ce que le moteur a calculé",
    "format.js": "l'écriture des nombres, en entiers exacts",
    "releve-lu.js": "la lecture d'un relevé déposé, sans jumeau Python depuis l'étape 3",
}


def _code_seul(texte: str) -> str:
    """Le JavaScript sans ses commentaires ni ses chaînes : ce qui s'exécute."""
    sortie = []
    i, n = 0, len(texte)
    while i < n:
        deux = texte[i:i + 2]
        if deux == "//":
            i = texte.find("\n", i)
            i = n if i < 0 else i
        elif deux == "/*":
            fin = texte.find("*/", i + 2)
            i = n if fin < 0 else fin + 2
        elif texte[i] in "'\"`":
            guillemet = texte[i]
            i += 1
            while i < n and texte[i] != guillemet:
                i += 2 if texte[i] == "\\" else 1
            i += 1
        else:
            sortie.append(texte[i])
            i += 1
    return "".join(sortie)


def test_le_moteur_ne_calcule_ses_exponentielles_que_par_la_libm_du_portage():
    """Un ``Math.exp`` ou un ``**`` dans le moteur rendrait la libm de V8, et
    les témoins cesseraient d'être identiques au bit près : le moteur passe
    par ``exp``, ``log`` et ``pow`` de ``libm.js``."""
    import re

    dossier = RACINE / "moteur" / "js"
    interdits = re.compile(r"Math\s*\.\s*(?:exp|log|pow|expm1|log1p|log2|log10)\b|\*\*")
    fautes = []
    for chemin in sorted(dossier.rglob("*.js")):
        nom = chemin.relative_to(dossier).as_posix()
        if nom in SANS_LIBM:
            continue
        code = _code_seul(chemin.read_text(encoding="utf-8"))
        fautes += [f"{nom} : {trouve.group(0)}" for trouve in interdits.finditer(code)]
    assert not fautes, ("le moteur doit appeler exp, log et pow de libm.js : "
                        + ", ".join(fautes))
    absents = [nom for nom in SANS_LIBM if not (dossier / nom).exists()]
    assert not absents, f"exemptés mais absents du portage : {absents}"


def test_le_portage_rend_l_exp_le_log_et_le_pow_de_la_libm_au_bit_pres():
    raison = _hors_reference()
    if raison is not None:
        pytest.skip(f"la libm du Python n'est pas celle que le portage refait : {raison}")
    entrees = _echantillon()
    portage = _portage(entrees)
    ecarts = []
    for nom, f in (("exp", math.exp), ("log", math.log)):
        ecarts += [f"{nom}({x!r}) : {_bits(f(x))} ≠ {_bits(y)}"
                   for x, y in zip(entrees[nom], portage[nom]) if f(x) != y]
    ecarts += [f"pow({x!r}, {y!r}) : {_bits(x ** y)} ≠ {_bits(z)}"
               for (x, y), z in zip(entrees["pow"], portage["pow"]) if x ** y != z]
    assert not ecarts, f"{len(ecarts)} écarts, dont : " + " ; ".join(ecarts[:5])


def test_la_multiplication_addition_fusionnee_n_arrondit_qu_une_fois():
    """Partout : la référence est le rationnel exact a × b + c, arrondi une fois."""
    entrees = _echantillon()
    portage = _portage({**entrees, "exp": [], "log": [], "pow": []})
    ecarts = [f"fma({a!r}, {b!r}, {c!r}) : {_bits(z)}"
              for (a, b, c), z in zip(entrees["fma"], portage["fma"])
              if float(Fraction(a) * Fraction(b) + Fraction(c)) != z]
    assert not ecarts, f"{len(ecarts)} écarts, dont : " + " ; ".join(ecarts[:5])
