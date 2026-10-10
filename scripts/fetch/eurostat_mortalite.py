#!/usr/bin/env python3
"""Récupération des données de mortalité françaises auprès d'Eurostat.

    python scripts/fetch/eurostat_mortalite.py

Trois usages :

* ``demo_mlexpec`` — espérance de vie à 60 et 65 ans. Sert de **contrôle
  croisé** : l'espérance à 65 ans vient de l'OCDE, qui couvre 1960-2024 là où
  Eurostat s'arrête à 1986 (voir scripts/fetch/oecd_esperance_vie.py). Les deux
  sources doivent coïncider, puisque toutes deux reprennent les chiffres INSEE.

* ``demo_mager`` et ``demo_pjan`` — les **décès par année de naissance**
  (l'âge atteint dans l'année) et la **population au 1er janvier**, par âge.
  Le dépôt en tire ses quotients de mortalité observés de 1986 à 2024, comme
  l'INSEE calcule les siens : génération par génération, puis convertis à
  l'âge exact comme les quotients projetés. Déposés dans
  ``data/reference/mortalite/quotients_periode.csv``, ils priment sur la loi
  de Gompertz-Makeham sans qu'aucune ligne du moteur ne change.

* ``demo_mlifetable`` — la table du moment qu'Eurostat publie. Le dépôt la
  lisait telle quelle jusqu'au 10 octobre 2026 ; elle ne donne plus que ses
  cases — les années et les âges que couvre la table du dépôt — et un
  contrôle des quotients refaits.

Deux territoires sont demandés, et leur ordre de priorité est délibéré :

* ``FX`` — France métropolitaine, 1986-2012, sur le même champ que les séries
  INSEE du modèle ;
* ``FR`` — France y compris départements d'outre-mer, 1998-2024, qui prolonge.

Avant 1986, Eurostat ne publie pas de table française ; le dépôt y lit les
tables de Vallin et Meslé (scripts/fetch/ined_vallin_mesle.py).

POURQUOI PAR GÉNÉRATION, ET NON LA TABLE D'EUROSTAT TELLE QUELLE
-----------------------------------------------------------------
Eurostat calcule le quotient de l'âge x en t sur un carré du diagramme de
Lexis : les décès d'âge révolu x pendant l'année t, rapportés à la moyenne
des populations d'âge x au 1er janvier de t et de t + 1. Ces deux populations
sont deux générations, nées en t − x − 1 et en t − x, et la moyenne suppose
que chacune passe une demi-année dans le carré : c'est vrai quand ses
naissances se répartissent également sur l'année. Celles de 1940 et de 1941
ne s'y répartissent pas. Les naissances s'effondrent au cours de 1940, neuf
mois après la mobilisation, et ne reprennent qu'en 1941 : la génération 1940
est née plutôt en début d'année, celle de 1941 plutôt en fin. Les décès
d'Eurostat le disent eux-mêmes : de 55 à 80 ans, 53,7 % de ceux que la
génération 1940 compte dans une année tombent après son anniversaire, 49,5 %
de ceux de 1941, 51,5 à 52,3 % pour les générations voisines. Le carré qui les
sépare compte donc moins de personnes-années que la moyenne ne le dit, et son
quotient est trop bas, de 4 à 5 % en moyenne. Le modèle lit ses tables de
génération le long de la diagonale, et la génération 1941 traverse tous ces
carrés : de 60 à 83 ans, ses quotients étaient de 5 à 10 % sous ceux de 1940
et de 1942, et son espérance de vie à 60 ans dépassait celle de l'INSEE de
0,32 an pour les hommes et de 0,22 pour les femmes. Les naissances de la
Grande Guerre font les mêmes marches, aux diagonales des générations 1915 et
1916, 1919 et 1920.

L'INSEE ne fait pas cette hypothèse : il calcule chaque quotient sur une seule
génération, celle qui atteint l'âge x dans l'année t, entre ses deux effectifs
au 1er janvier, quelle que soit la date de ses naissances :

    m = D(x, t) / ½ [P(x − 1, t) + P(x, t + 1)],    q'(x, t) = 2m / (2 + m),

D(x, t) étant les décès de l'année t de la génération née en t − x, et
P(x, t) la population d'âge révolu x au 1er janvier t. Le carré se tire des
deux parallélogrammes qui l'encadrent, comme pour les quotients projetés
(scripts/fetch/insee_projections_mortalite.py) :

    1 − q(x, t) = √[(1 − q'(x, t)) · (1 − q'(x + 1, t))].

Chaque carré mêle encore deux générations, mais chacune y entre avec son
propre quotient, et non plus avec une exposition supposée. À 0 et 1 an, le
carré reste celui d'Eurostat (``PREMIER_AGE_PAR_GENERATION``).

Deux contrôles l'autorisent, reconduits à chaque exécution ; le script échoue
si l'un casse :

* les quotients par âge atteint retrouvent ceux que l'INSEE publie
  (« Mortalité en 2019 », tableaux de séries longues, tableau 69), de 40 à
  94 ans, à l'arrondi près pour la métropole et à 0,2 % près en médiane pour
  la France entière, dont les populations de 2019 ont été révisées depuis ;
* les carrés convertis restent, année par année, à 1 % près en médiane de
  ceux d'Eurostat : ils ne s'en écartent qu'aux diagonales des générations
  de guerre, que le script imprime.
"""

from __future__ import annotations

import json
import statistics
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from insee_projections_mortalite import convertir  # noqa: E402
from lecture_xlsx import feuilles  # noqa: E402
from source_locale import lire_ou_telecharger  # noqa: E402

RACINE_API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
TERRITOIRES = ("FX", "FR")  # ordre de priorité croissante : FR écrase FX
SEXES = {"M": "H", "F": "F"}

ESPERANCES = f"{RACINE_API}/demo_mlexpec?format=JSON&age=Y60&age=Y65&sex=M&sex=F&unit=YR"
TABLE = f"{RACINE_API}/demo_mlifetable?format=JSON&sex=M&sex=F&indic_de=PROBDEATH"
DECES = f"{RACINE_API}/demo_mager?format=JSON&sex=M&sex=F&sinceTimePeriod=1986"
POPULATION = f"{RACINE_API}/demo_pjan?format=JSON&sex=M&sex=F&sinceTimePeriod=1986"

#: Les quotients par âge atteint que l'INSEE publie, 1962-2019 pour la
#: métropole, 1994-2019 pour la France entière.
INSEE = {
    "FX": "https://www.insee.fr/fr/statistiques/fichier/5390366/fm_t69qmort.xlsx",
    "FR": "https://www.insee.fr/fr/statistiques/fichier/5390366/fe_t69qmort.xlsx",
}

SORTIE_ESPERANCES = Path("data/brut/eurostat_esperance_vie.json")
SORTIE_QUOTIENTS = Path("data/brut/eurostat_quotients.json")

DECIMALES = 6

#: Le premier âge calculé par génération. À 0 et 1 an, le carré d'Eurostat :
#: les décès de la première année se concentrent dans ses premières semaines,
#: ce que la moyenne de deux parallélogrammes ignore — elle diviserait par
#: deux le quotient de 0 an et gonflerait des deux tiers celui de 1 an. Aucun
#: calcul du modèle ne part de la naissance, mais la table n'a pas à y être
#: fausse, et les naissances d'après 1985 sont trop régulières pour que le
#: carré d'Eurostat s'y trompe.
PREMIER_AGE_PAR_GENERATION = 2

#: Les âges des contrôles : ceux qui pilotent le diviseur, et où l'arrondi de
#: l'INSEE, au cent-millième, ne pèse plus.
AGES_CONTROLE = range(40, 95)
#: Écart médian toléré aux quotients de l'INSEE, par année et par sexe. Un an
#: de décalage en vaudrait 1 à 3 %, le recul annuel de la mortalité.
TOLERANCE_INSEE_MEDIANE = 0.005
#: Écart toléré à chaque quotient de l'INSEE, au-delà de son arrondi. Un an
#: d'âge de décalage en vaudrait 8 à 10 %.
TOLERANCE_INSEE = 0.03
#: Écart médian toléré aux carrés d'Eurostat, par année et par sexe.
TOLERANCE_EUROSTAT_MEDIANE = 0.01


def _telecharger(url: str) -> dict:
    return json.loads(_telecharger_octets(url))


def _telecharger_octets(url: str) -> bytes:
    demande = urllib.request.Request(
        url, headers={"User-Agent": "retraite-notionnelle/0.1"}
    )
    with urllib.request.urlopen(demande, timeout=300) as reponse:
        return reponse.read()


def _coordonnees(charge: dict):
    """Itère sur les valeurs d'une réponse JSON-stat, coordonnées décodées.

    Eurostat renvoie un tableau creux : la position d'une valeur encode les
    coordonnées de toutes les dimensions, de la plus lente à la plus rapide.
    """
    dimensions = charge["id"]
    tailles = charge["size"]
    index = {
        nom: {rang: code
              for code, rang in charge["dimension"][nom]["category"]["index"].items()}
        for nom in dimensions
    }
    for position, valeur in charge["value"].items():
        if valeur is None:
            continue
        reste = int(position)
        point = {}
        for rang in reversed(range(len(dimensions))):
            nom = dimensions[rang]
            point[nom] = index[nom][reste % tailles[rang]]
            reste //= tailles[rang]
        yield point, float(valeur)


def _age_numerique(code: str) -> int | None:
    """Traduit un code d'âge Eurostat en âge entier.

    Les classes ouvertes (``Y_GE85``, ``Y_GE95``, ``Y_OPEN``) et l'âge inconnu
    sont écartés : ils ne sont pas un âge donné, et le modèle doit continuer à
    traiter la queue de table par sa loi paramétrique plutôt que par une
    valeur agrégée.
    """
    if code == "Y_LT1":
        return 0
    if code.startswith("Y") and code[1:].isdigit():
        return int(code[1:])
    return None


def _par_age(url: str) -> dict[tuple[int, str, int], float]:
    """Une série Eurostat par année, sexe et âge entier."""
    table = {}
    for point, valeur in _coordonnees(_telecharger(url)):
        sexe = SEXES.get(point["sex"])
        age = _age_numerique(point["age"])
        if sexe is not None and age is not None:
            table[(int(point["time"]), sexe, age)] = valeur
    return table


def esperances() -> dict[str, float]:
    serie: dict[str, float] = {}
    for territoire in TERRITOIRES:
        valeurs = {}
        for point, valeur in _coordonnees(_telecharger(f"{ESPERANCES}&geo={territoire}")):
            sexe = SEXES.get(point["sex"])
            if sexe is None:
                continue
            mesure = "e" + point["age"].removeprefix("Y")
            valeurs[f"{point['time']}|{sexe}|{mesure}"] = valeur
        serie.update(valeurs)
        print(f"OK      espérances {territoire} : {len(valeurs)} valeurs")
    return serie


def quotients_par_age_atteint(deces: dict, population: dict) -> dict[tuple[int, str], dict[int, float]]:
    """Les quotients de chaque génération dans chaque année, ``(annee, sexe)
    -> âge atteint -> q'``, dès 1 an : voir l'en-tête du module."""
    atteints: dict[tuple[int, str], dict[int, float]] = {}
    for (annee, sexe, age), morts in deces.items():
        debut = population.get((annee, sexe, age - 1))
        fin = population.get((annee + 1, sexe, age))
        if age == 0 or debut is None or fin is None:
            continue
        taux = morts / (0.5 * (debut + fin))
        atteints.setdefault((annee, sexe), {})[age] = 2.0 * taux / (2.0 + taux)
    return atteints


def carres(atteints: dict[int, float], ages: list[int]) -> dict[int, float]:
    """Les quotients d'âge exact des ``ages`` demandés, dès
    ``PREMIER_AGE_PAR_GENERATION``, tirés des quotients par âge atteint ;
    chacun exige le parallélogramme de l'âge suivant."""
    plage = range(PREMIER_AGE_PAR_GENERATION, ages[-1] + 2)
    manquants = [age for age in plage if age not in atteints]
    if manquants:
        raise ValueError(f"âges atteints sans quotient : {manquants[:5]}")
    exacts = convertir({age: atteints[age] for age in plage})
    return {age: exacts[age] for age in ages if age >= PREMIER_AGE_PAR_GENERATION}


def _quotients_insee(donnees: bytes) -> dict[tuple[int, str, int], float]:
    """Le tableau 69 de l'INSEE : une feuille par sexe, les années en lignes,
    les âges atteints en colonnes, pour 100 000."""
    table = {}
    for grille in feuilles(donnees).values():
        titre = next((v for v in grille.values()
                      if isinstance(v, str) and "Sexe " in v), "")
        sexe = "F" if "féminin" in titre else "H" if "masculin" in titre else None
        if sexe is None:
            continue
        ligne_ages = next(ligne for (ligne, colonne), v in grille.items()
                          if colonne == 1 and v == "0 an")
        ages = {colonne: int(v.split()[0]) for (ligne, colonne), v in grille.items()
                if ligne == ligne_ages and colonne > 0 and isinstance(v, str)
                and v.split()[0].isdigit()}
        for (ligne, colonne), valeur in grille.items():
            annee = str(grille.get((ligne, 0), "")).removesuffix(".0").strip()
            if (ligne > ligne_ages and colonne in ages and annee.isdigit()
                    and isinstance(valeur, float)):
                table[(int(annee), sexe, ages[colonne])] = valeur / 100_000.0
    if not table:
        raise ValueError("aucun quotient lu dans le tableau 69")
    return table


def controler_insee(territoire: str, atteints: dict) -> str:
    """Les quotients par âge atteint contre ceux que l'INSEE publie."""
    publies = _quotients_insee(lire_ou_telecharger(INSEE[territoire], _telecharger_octets))
    medianes, pire = [], (0.0, None)
    for (annee, sexe), table in sorted(atteints.items()):
        relatifs = []
        for age in AGES_CONTROLE:
            insee, refait = publies.get((annee, sexe, age)), table.get(age)
            if insee is None or refait is None or insee <= 0:
                continue
            relatifs.append((refait - insee) / insee)
            # L'INSEE arrondit au cent-millième.
            au_dela = max(0.0, abs(refait - insee) - 0.5e-5) / insee
            if au_dela > pire[0]:
                pire = (au_dela, (annee, sexe, age))
        if relatifs:
            medianes.append((abs(statistics.median(relatifs)), (annee, sexe)))
    if not medianes:
        raise ValueError(f"{territoire} : aucune année commune avec l'INSEE")
    mediane = max(medianes)
    if mediane[0] > TOLERANCE_INSEE_MEDIANE or pire[0] > TOLERANCE_INSEE:
        raise ValueError(f"{territoire} : quotients loin de ceux de l'INSEE, écart "
                         f"médian {mediane}, plus grand écart {pire}")
    annees = sorted({annee for _, (annee, _) in medianes})
    return (f"{len(medianes)} tables de {annees[0]} à {annees[-1]}, écart médian "
            f"au plus {mediane[0]:.2%} ({mediane[1][0]}), au-delà de l'arrondi "
            f"au plus {pire[0]:.2%} ({'/'.join(map(str, pire[1])) if pire[1] else '-'})")


def quotients() -> tuple[dict[str, float], list[str]]:
    serie: dict[str, float] = {}
    rapport: list[str] = []
    for territoire in TERRITOIRES:
        publies = _par_age(f"{TABLE}&geo={territoire}")
        atteints = quotients_par_age_atteint(_par_age(f"{DECES}&geo={territoire}"),
                                             _par_age(f"{POPULATION}&geo={territoire}"))
        cases: dict[tuple[int, str], list[int]] = {}
        for annee, sexe, age in publies:
            cases.setdefault((annee, sexe), []).append(age)
        valeurs, diagonales, medianes = {}, {}, []
        for (annee, sexe), ages in sorted(cases.items()):
            ages.sort()
            if ages != list(range(len(ages))):
                raise ValueError(f"{territoire} {annee} {sexe} : âges publiés discontinus")
            exacts = carres(atteints.get((annee, sexe), {}), ages)
            relatifs = []
            for age in ages:
                publie = publies[(annee, sexe, age)]
                if age < PREMIER_AGE_PAR_GENERATION:
                    valeurs[f"{annee}|{sexe}|{age}"] = publie
                    continue
                valeurs[f"{annee}|{sexe}|{age}"] = round(exacts[age], DECIMALES)
                if age in AGES_CONTROLE and publie > 0:
                    relatifs.append(exacts[age] / publie - 1.0)
                    diagonales.setdefault(annee - age, []).append(exacts[age] / publie - 1.0)
            medianes.append((abs(statistics.median(relatifs)), (annee, sexe)))
        mediane = max(medianes)
        if mediane[0] > TOLERANCE_EUROSTAT_MEDIANE:
            raise ValueError(f"{territoire} : carrés loin de ceux d'Eurostat, écart "
                             f"médian {mediane}")
        print(f"OK      quotients {territoire} : {len(valeurs)} valeurs, à "
              f"{mediane[0]:.2%} au plus en médiane des carrés d'Eurostat ({mediane[1][0]})")
        ecarts = sorted(((statistics.mean(v), generation) for generation, v in diagonales.items()
                         if len(v) >= 5), key=lambda e: -abs(e[0]))[:6]
        ligne = ", ".join(f"{generation} {ecart:+.1%}" for ecart, generation in ecarts)
        print(f"        diagonales les plus éloignées d'Eurostat, par génération : {ligne}")
        controle = controler_insee(territoire, atteints)
        print(f"OK      contrôle INSEE {territoire} : {controle}")
        rapport.append(f"{territoire} — INSEE : {controle} ; diagonales : {ligne}")
        serie.update(valeurs)
    return serie, rapport


def _ecrire(chemin: Path, source, serie: dict[str, float], **autres) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(
        json.dumps({"source": source, "territoires": list(TERRITOIRES), **autres,
                    "serie": dict(sorted(serie.items()))},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    annees = sorted({int(cle.split("|")[0]) for cle in serie})
    couverture = f"{annees[0]}-{annees[-1]}" if annees else "vide"
    print(f"        {len(serie)} valeurs écrites dans {chemin} ({couverture})")


def main() -> int:
    try:
        _ecrire(SORTIE_ESPERANCES, ESPERANCES, esperances())
        serie, rapport = quotients()
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
        print(f"Eurostat indisponible : {erreur}", file=sys.stderr)
        return 1
    except (LookupError, ValueError, StopIteration) as erreur:
        print(f"ÉCHEC   {erreur}", file=sys.stderr)
        return 1
    _ecrire(SORTIE_QUOTIENTS, [DECES, POPULATION, TABLE, *INSEE.values()], serie,
            recupere_le=date.today().isoformat(),
            methode="Quotients d'âge exact tirés des décès par année de naissance et "
                    "des populations au 1er janvier : q' par âge atteint, comme "
                    "l'INSEE, puis 1 − q(x) = √[(1 − q'(x))(1 − q'(x + 1))], sur les "
                    "cases de la table d'Eurostat. Voir l'en-tête du récupérateur.",
            controles=rapport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
