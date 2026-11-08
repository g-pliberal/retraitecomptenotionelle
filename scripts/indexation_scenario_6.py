"""Le facteur démographique et le plancher, chiffrés au modèle, pour le seul scénario 6.

Action 186, chantier 5. Les décisions 41 (α = 1), 44 (un plancher en euros
avec rattrapage), 46 (payé par les retraités, par une dette au taux de la
masse salariale) et 49 (rendue au plus vite) laissent un nœud : la règle du
stock baisse en euros dès que l'inflation reste sous la hausse du nombre de
retraités par cotisant, et sa dette ne se rend pas. Le propriétaire demande
trois voies neuves, chiffrées au modèle, avec la règle d'avant pour comparer
(``data/reference/etudes/indexation_scenario_6.yaml``) :

1. une prime payée d'avance par le stock, mise en réserve, qui paie son
   plancher ;
2. l'effort démographique du stock pris d'avance à la bascule, puis les prix
   avec le plancher du droit actuel (L. 161-25) ;
3. la même règle pour toutes les pensions, la masse salariale par retraité,
   avec le plancher et sa dette.

CE QUE LE SCRIPT CALCULE. Pour chaque voie et chaque trajectoire, le coût du
dépôt (``memoire.cout(indexation_liberale=…)``) : la dépense du scénario 6,
sa garantie vieillesse, son solde et sa dette, de 2026 à 2070. Le stock et
les nouvelles se séparent ainsi : la masse du stock sous les prix est
mesurée une fois par trajectoire (le coût, le stock seul) ; toutes ses
pensions suivant le même chemin depuis la bascule, sa masse sous une voie est
celle-là fois le chemin d'un euro (``Detail``) ; les nouvelles sont le reste.

LES CONVENTIONS, à dire avec tout chiffre qui en sort.

- L'étalon est α = 1 sans plancher (la voie ``regle``) : ce que les
  retraités doivent porter. Ce qu'une voie dépense au-dessus, les cotisants
  le paient ; en dessous, les retraités paient plus que la règle.
- Les valeurs actuelles s'actualisent au taux de la masse salariale, celui du
  compte et de la dette (décision 46), de 2026 à 2070 ; les moyennes de part
  de PIB sont simples, la convention du solde moyen du dépôt.
- La dette du plancher est celle du groupe : ce que le plancher a servi
  au-dessus de la règle de la voie, portée au taux de la masse salariale,
  moins ce que les hausses ont repris — y compris la dette des retraités
  morts avant de l'avoir rendue, que personne ne rendra.
- La prime de la voie 1 se calibre sur un choc, tour à tour sur chacun des
  deux : elle finance exactement le plancher sous ce choc ; sous les autres
  trajectoires, la réserve finit en surplus ou en manque.
- La baisse de la voie 2 se calcule sous le COR, au jour de la bascule ; elle
  ne se révise pas quand la trajectoire s'en écarte.

LA VOIE 1 DÉCIDÉE (décisions 73 à 77) : une prime de 2,15 % qui baisse dès que
la réserve dépasse ce que le plancher peut encore coûter, et une dette du stock
quand la réserve manque. Ce que le plancher peut encore coûter se lit de
plusieurs façons, que le script chiffre toutes (``DECIDEES``) : la crise
assurée garde ses dates ou recommence à chaque date ; elle seule, ou aussi
l'inflation basse que la prime couvre (décision 74) ; la prime baisse dès que
la réserve et les primes à venir suffisent, ou seulement quand la réserve seule
suffit (``--seuil``). Sa réserve se mesure sur la masse du stock sous les prix,
que le coût donne, la même sous les trois trajectoires.

Usage : ``python scripts/indexation_scenario_6.py`` (une quarantaine de
calculs du coût, six secondes chacun, la grille gardée), ``--annees`` pour
chaque année de 2026 à 2070, ``--csv chemin`` pour tout écrire.
``--decidee`` n'imprime que la voie 1 décidée.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import indexation_programme as I  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

LIBERAL = "notionnel_liberal"
DEBUT, FIN = 2026, 2070
VUES = (2026, 2027, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070)
#: Les voies du fichier, la voie 1 dédoublée : sa prime calibrée sur chacun
#: des deux chocs.
CHOCS = ("inflation_basse", "emploi_ia")
#: La voie 1 décidée, en chacune des lectures de la décision 75 : la voie du
#: fichier (la crise à ses dates, ou recommencée), et ce qui change de son
#: stock — les risques sous lesquels se mesure ce que le plancher peut encore
#: coûter. Puis la contribution que le propriétaire a dite le 8 novembre,
#: « 1 % tout le temps », qui ne se mesure ni ne baisse.
DECIDEES = {
    "v1_dates": ("voie_1_crise_a_ses_dates", {"crise_assuree": ("emploi_ia",)}),
    "v1_dates_deux": ("voie_1_crise_a_ses_dates",
                      {"crise_assuree": ("emploi_ia", "inflation_basse")}),
    "v1_recommencee": ("voie_1_crise_recommencee", {"crise_assuree": ("emploi_ia",)}),
    "v1_recommencee_deux": ("voie_1_crise_recommencee",
                            {"crise_assuree": ("emploi_ia", "inflation_basse")}),
    "v1_un_pour_cent": ("voie_1_crise_a_ses_dates",
                        {"prime": 0.01, "reserve_rendue": "jamais", "crise_assuree": ()}),
}
CLES = ("avant", "regle", "decidee", *(f"voie_1_{choc}" for choc in CHOCS),
        "voie_2", "voie_3", *DECIDEES)


@dataclass
class Groupe:
    """Le stock, ou les nouvelles, sous une voie : des masses de droits
    directs en millions d'euros constants."""

    servi: dict[int, float] = field(default_factory=dict)
    #: Sous α = 1 sans plancher : l'étalon.
    etalon: dict[int, float] = field(default_factory=dict)
    #: Ce que le plancher a avancé et que les hausses n'ont pas repris.
    dette: dict[int, float] = field(default_factory=dict)
    #: ``Σ δ (servi − étalon) / Σ δ étalon`` : ce que le groupe touche de plus
    #: que α = 1 sur 2026-2070, en fraction de ce que α = 1 lui sert.
    valeur_actuelle_ecart: float = 0.0


@dataclass
class Resultat:
    voie: str
    trajectoire: str
    #: Parts de PIB, chaque année.
    depense: dict[int, float] = field(default_factory=dict)
    garantie: dict[int, float] = field(default_factory=dict)
    solde: dict[int, float] = field(default_factory=dict)
    dette_publique: dict[int, float] = field(default_factory=dict)
    #: Ce qui passe des millions d'euros constants à la part de PIB.
    vers_pib: dict[int, float] = field(default_factory=dict)
    stock: Groupe = field(default_factory=Groupe)
    nouvelles: Groupe = field(default_factory=Groupe)
    #: La réserve de la voie 1, en millions d'euros constants.
    reserve: dict[int, float] = field(default_factory=dict)
    reserve_actuelle: float = 0.0
    #: Un euro du stock à la bascule, et un euro liquidé en 2030 : euros
    #: constants, et la dette du plancher en euros courants.
    euro_stock: I.Detail | None = None
    euro_2030: I.Detail | None = None
    #: L'inflation de la trajectoire, pour les euros courants.
    inflation: dict[int, float] = field(default_factory=dict)
    #: La voie 1 décidée, sous la lecture « au seuil » : un euro du stock.
    euro_seuil: I.Detail | None = None

    def moyenne(self, serie: dict[int, float]) -> float:
        valeurs = [serie[a] for a in range(DEBUT, FIN + 1)]
        return somme_ordonnee(valeurs) / len(valeurs)

    def pib(self, masses: dict[int, float], annee: int) -> float:
        return masses[annee] * self.vers_pib[annee]


@dataclass
class Etude:
    voies: dict[str, I.Voie]
    trajectoires: dict[str, I.Trajectoire]
    baisse_voie_2: float
    primes: dict[str, float]
    resultats: dict[tuple[str, str], Resultat]

    def resultat(self, voie: str, trajectoire: str) -> Resultat:
        return self.resultats[(voie, trajectoire)]


# -- le modèle ----------------------------------------------------------------


def _voie(voies: dict[str, I.Voie], cle: str, baisse: float,
          primes: dict[str, float], retour: str = "progressif") -> I.Voie:
    if cle in DECIDEES:
        nom, options = DECIDEES[cle]
        voie = voies[nom]
        return replace(voie, stock=replace(voie.stock, retour=retour, **options))
    if cle.startswith("voie_1_"):
        return voies["voie_1"].calibree(prime=primes[cle.removeprefix("voie_1_")])
    if cle == "voie_2":
        return voies["voie_2"].calibree(baisse=baisse)
    return voies[cle]


def _cout(voie: I.Voie, trajectoire: I.Trajectoire, seulement: str | None = None,
          masses: tuple[tuple[int, float], ...] | None = None):
    from retraite_notionnelle import memoire

    return memoire.cout(indexation_liberale=I.IndexationLiberale(
        voie, trajectoire, seulement=seulement,
        masses_stock=masses if voie.stock.assuree else None))


def _pensions(voie: I.Voie, trajectoire: I.Trajectoire,
              masses: tuple[tuple[int, float], ...] | None = None) -> I.PensionsDuProgramme:
    """Les chemins d'un euro sous cette voie et cette trajectoire, sans
    calculer le coût : la revalorisation de la proposition que le coût
    construit, sur la masse salariale de la trajectoire."""
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.revalorisation import RevalorisationServie
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres()).pour_la_projection()
    revalorisation = RevalorisationServie(simulateur, 1990, FIN)
    if trajectoire.emploi is not None:
        revalorisation = revalorisation.pour_la_proposition(trajectoire.facteur_emploi)
    return I.IndexationLiberale(
        voie, trajectoire, masses_stock=masses if voie.stock.assuree else None).appliquer(
        revalorisation, simulateur).proposition


def _droits_directs(cout) -> dict[int, float]:
    return {ligne.annee: ligne.pensions_propres_constants(LIBERAL)
            for ligne in cout.avenir.annees if DEBUT <= ligne.annee <= FIN}


def _actualisation(pensions: I.PensionsDuProgramme) -> dict[int, float]:
    facteurs, facteur = {}, 1.0
    for annee in range(DEBUT, FIN + 1):
        if annee > DEBUT:
            facteur /= pensions.masse(annee)
        facteurs[annee] = facteur
    return facteurs


def _valeur_actuelle(delta: dict[int, float], serie: dict[int, float]) -> float:
    return somme_ordonnee(delta[a] * serie[a] for a in range(DEBUT, FIN + 1))


def _cumul(pensions: I.PensionsDuProgramme, flux: dict[int, float]) -> dict[int, float]:
    """Un stock qui reçoit ``flux`` chaque année et porte intérêt au taux
    réel de la masse salariale."""
    stock, resultat = 0.0, {}
    for annee in range(DEBUT, FIN + 1):
        if annee > DEBUT:
            stock *= pensions.masse(annee)
        stock += flux[annee]
        resultat[annee] = stock
    return resultat


def etudier() -> Etude:
    from retraite_notionnelle.cout import COMPOSANTE_GARANTIE

    voies, trajectoires = I.charger()
    avant, regle = voies["avant"], voies["regle"]

    # La masse du stock sous les prix, chaque trajectoire : le coût, le stock seul.
    stock_aux_prix = {nom: _droits_directs(_cout(avant, t, seulement="stock"))
                      for nom, t in trajectoires.items()}
    # Ce qui reste du stock, pour la réserve de la voie 1 décidée : le même
    # sous les trois trajectoires, qui ne touchent pas les retraités.
    masses = tuple(sorted(stock_aux_prix["cor"].items()))

    # La voie 2 : la baisse qui retire au stock, sous le COR et au jour de la
    # bascule, ce que α = 1 lui retire sur sa vie.
    cor = _pensions(regle, trajectoires["cor"])
    baisse = I.baisse_d_effort(
        stock_aux_prix["cor"], cor.detail_stock().servi,
        {a: cor.masse(a) for a in range(DEBUT + 1, FIN + 1)})

    # La voie 1 : la prime qui finance exactement le plancher sous chaque choc.
    primes = {}
    for choc in CHOCS:
        trajectoire = trajectoires[choc]
        sans_prime = _pensions(voies["voie_1"].calibree(prime=0.0), trajectoire)
        etalon = _pensions(regle, trajectoire)
        masses = stock_aux_prix[choc]
        primes[choc] = I.prime_d_equilibre(
            {a: m * etalon.detail_stock().servi[a] for a, m in masses.items()},
            {a: m * sans_prime.detail_stock().servi[a] for a, m in masses.items()},
            {a: etalon.masse(a) for a in range(DEBUT + 1, FIN + 1)})

    resultats: dict[tuple[str, str], Resultat] = {}
    for nom_t, trajectoire in trajectoires.items():
        masses_stock = stock_aux_prix[nom_t]
        etalon = _pensions(regle, trajectoire)
        delta = _actualisation(etalon)
        etalon_total = _droits_directs(_cout(regle, trajectoire))
        etalon_stock = {a: m * etalon.detail_stock().servi[a] for a, m in masses_stock.items()}
        etalon_nouvelles = {a: etalon_total[a] - etalon_stock[a] for a in etalon_stock}
        for cle in CLES:
            voie = _voie(voies, cle, baisse, primes)
            cout = _cout(voie, trajectoire, masses=masses)
            pensions = _pensions(voie, trajectoire, masses)
            avenir = {l.annee: l for l in cout.avenir.annees}
            solde = {l.annee: l for l in cout.solde.annees}
            resultat = Resultat(voie=cle, trajectoire=nom_t)
            for annee in range(DEBUT, FIN + 1):
                ligne = avenir[annee]
                resultat.vers_pib[annee] = 1.0 / ligne.coefficient_constants / ligne.pib
                resultat.depense[annee] = solde[annee].depense(LIBERAL)
                resultat.solde[annee] = solde[annee].solde(LIBERAL)
                resultat.garantie[annee] = (ligne.part_pib(COMPOSANTE_GARANTIE)
                                            - ligne.part_pib_reprises())
                resultat.dette_publique[annee] = cout.dette.stock(LIBERAL, annee)
                resultat.inflation[annee] = pensions.inflation(annee)
            total = _droits_directs(cout)
            euro = pensions.detail_stock()
            stock = {a: m * euro.servi[a] for a, m in masses_stock.items()}
            nouvelles = {a: total[a] - stock[a] for a in stock}
            resultat.euro_stock = euro
            resultat.euro_2030 = pensions.detail_nouvelle(2030)

            # La dette du plancher : ce qu'il sert au-dessus de la règle de la
            # voie, portée au taux de la masse salariale.
            avance_stock = ({a: m * (euro.servi[a] - euro.regle[a])
                             for a, m in masses_stock.items()}
                            if voie.stock.plancher == "dette" else {a: 0.0 for a in stock})
            prix = {DEBUT: 1.0}
            for annee in range(DEBUT + 1, FIN + 1):
                prix[annee] = prix[annee - 1] * (1.0 + resultat.inflation[annee])
            avance_nouvelles = ({a: nouvelles[a] - etalon_nouvelles[a] for a in stock}
                                if voie.nouvelles == voies["decidee"].nouvelles
                                else {a: 0.0 for a in stock})
            # La voie 1 décidée : la dette des euros du stock encore vivants
            # (décision 76), en euros constants ; celle des morts est perdue.
            dette_stock = ({a: m * euro.dette[a] / prix[a] for a, m in masses_stock.items()}
                           if voie.stock.assuree else _cumul(etalon, avance_stock))
            resultat.stock = Groupe(
                servi=stock, etalon=etalon_stock, dette=dette_stock,
                valeur_actuelle_ecart=(
                    _valeur_actuelle(delta, {a: stock[a] - etalon_stock[a] for a in stock})
                    / _valeur_actuelle(delta, etalon_stock)))
            resultat.nouvelles = Groupe(
                servi=nouvelles, etalon=etalon_nouvelles,
                dette=_cumul(etalon, avance_nouvelles),
                valeur_actuelle_ecart=(
                    _valeur_actuelle(delta, {a: nouvelles[a] - etalon_nouvelles[a]
                                             for a in stock})
                    / _valeur_actuelle(delta, etalon_nouvelles)))
            if voie.stock.assuree:
                resultat.reserve = {a: masses_stock[DEBUT] * euro.reserve[a] for a in stock}
                resultat.euro_seuil = _pensions(
                    _voie(voies, cle, baisse, primes, retour="au_seuil"), trajectoire,
                    masses).detail_stock()
            elif voie.stock.plancher == "reserve":
                # La répartition paie au stock la règle ; le stock touche le
                # plancher diminué de la prime ; la réserve garde l'écart.
                flux = {a: etalon_stock[a] - stock[a] for a in stock}
                resultat.reserve = _cumul(etalon, flux)
                resultat.reserve_actuelle = (_valeur_actuelle(delta, flux)
                                             / _valeur_actuelle(delta, etalon_stock))
            resultats[(cle, nom_t)] = resultat
    return Etude(voies, trajectoires, baisse, primes, resultats)


# -- l'impression -------------------------------------------------------------


LIBELLES = {
    "avant": "La règle d'avant",
    "regle": "α = 1 sans plancher (l'étalon)",
    "decidee": "α = 1, plancher et dette pour tous",
    "voie_1_inflation_basse": "Voie 1, prime couvrant 0,5 % d'inflation",
    "voie_1_emploi_ia": "Voie 1, prime couvrant la crise de l'emploi",
    "voie_2": "Voie 2, l'effort pris d'avance",
    "voie_3": "Voie 3, la même règle pour toutes",
    "v1_dates": "Voie 1 décidée, la crise à ses dates",
    "v1_dates_deux": "Voie 1 décidée, la crise à ses dates et l'inflation basse",
    "v1_recommencee": "Voie 1 décidée, la crise recommencée",
    "v1_recommencee_deux": "Voie 1 décidée, la crise recommencée et l'inflation basse",
    "v1_un_pour_cent": "Une contribution de 1 % tout le temps",
}


def _pc(valeur: float, decimales: int = 2) -> str:
    return f"{100 * valeur:+.{decimales}f}".replace(".", ",").replace("+", "+")


def _nb(valeur: float, decimales: int = 2) -> str:
    return f"{valeur:.{decimales}f}".replace(".", ",")


def _gel(euro: I.Detail, inflation: dict[int, float]) -> tuple[int, float]:
    """Les années où la pension ne monte pas en euros courants, et sa plus
    forte hausse refusée : la plus basse règle d'un an sur l'autre."""
    gelees, pire = 0, 0.0
    for annee in range(DEBUT + 1, FIN + 1):
        nominal = euro.servi[annee] * (1 + inflation[annee]) / euro.servi[annee - 1]
        regle = euro.regle[annee] * (1 + inflation[annee]) / euro.regle[annee - 1]
        if nominal <= 1.0 + 1e-12:
            gelees += 1
        pire = min(pire, regle - 1.0)
    return gelees, pire


def imprimer_synthese(etude: Etude) -> None:
    for nom_t, trajectoire in etude.trajectoires.items():
        print(f"\n## {trajectoire.libelle}\n")
        print("| Voie | Dépense 2026-2070 | Garantie | Solde | Dette 2070 | Écart à α = 1 | "
              "dont stock | dont nouvelles | dont garantie | Dette du plancher, 2070 | "
              "Réserve, 2070 |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        etalon = etude.resultat("regle", nom_t)
        for cle in CLES:
            r = etude.resultat(cle, nom_t)
            ecart = r.moyenne(r.depense) - etalon.moyenne(etalon.depense)
            ecart_stock = r.moyenne({a: r.pib(r.stock.servi, a) - r.pib(r.stock.etalon, a)
                                     for a in r.depense})
            ecart_nouvelles = r.moyenne({a: r.pib(r.nouvelles.servi, a)
                                         - r.pib(r.nouvelles.etalon, a) for a in r.depense})
            ecart_garantie = r.moyenne(r.garantie) - etalon.moyenne(etalon.garantie)
            dette = r.pib(r.stock.dette, FIN) + r.pib(r.nouvelles.dette, FIN)
            reserve = r.pib(r.reserve, FIN) if r.reserve else 0.0
            print(f"| {LIBELLES[cle]} | {_nb(100 * r.moyenne(r.depense))} | "
                  f"{_nb(100 * r.moyenne(r.garantie))} | "
                  f"{_nb(100 * r.moyenne(r.solde))} | {_nb(100 * r.dette_publique[FIN], 1)} | "
                  f"{_pc(ecart)} | {_pc(ecart_stock)} | {_pc(ecart_nouvelles)} | "
                  f"{_pc(ecart_garantie)} | {_nb(100 * dette)} | {_nb(100 * reserve)} |")
        print("\nUn euro de pension du stock (euros constants de la bascule) et une "
              "pension liquidée en 2030 :\n")
        print("| Voie | Stock 2030 | 2040 | 2050 | 2060 | Années sans hausse | "
              "Pire année de la règle | Dette d'un retraité du stock, 2040 | 2050 | "
              "Pension de 2030, en 2050 | Écart du stock à α = 1 sur sa vie | "
              "des nouvelles |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for cle in CLES:
            r = etude.resultat(cle, nom_t)
            gelees, pire = _gel(r.euro_stock, r.inflation)
            dettes = [r.euro_stock.dette[a] / (r.euro_stock.servi[a] * _prix(r, a))
                      for a in (2040, 2050)]
            print(f"| {LIBELLES[cle]} | "
                  + " | ".join(_nb(r.euro_stock.servi[a], 3) for a in (2030, 2040, 2050, 2060))
                  + f" | {gelees} | {_pc(pire)} | "
                  + " | ".join(_pc(d, 1) for d in dettes) + " | "
                  f"{_nb(r.euro_2030.servi[2050], 3)} | "
                  f"{_pc(r.stock.valeur_actuelle_ecart, 1)} | "
                  f"{_pc(r.nouvelles.valeur_actuelle_ecart, 1)} |")


def _dette_en_annees(euro: I.Detail, r: "Resultat") -> tuple[float, int]:
    """La plus forte dette d'un retraité du stock, en part d'une année de sa
    pension, et l'année où elle l'atteint."""
    parts = {a: euro.dette[a] / (euro.servi[a] * _prix(r, a)) for a in range(DEBUT, FIN + 1)}
    annee = max(parts, key=parts.get)
    return parts[annee], annee


def _premiere(euro: I.Detail, condition) -> str:
    for annee in range(DEBUT, FIN + 1):
        if condition(euro.prime[annee]):
            return str(annee)
    return "—"


def imprimer_decidee(etude: Etude) -> None:
    """La voie 1 décidée, en chacune des lectures de la décision 75."""
    print("\n# La voie 1 décidée : les lectures de la décision 75\n")
    print("Prime en % de la pension du stock, négative quand elle rend la réserve ; "
          "réserve et écarts en points de PIB ; dette d'un retraité du stock en part "
          "d'une année de sa pension.")
    for nom_t, trajectoire in etude.trajectoires.items():
        etalon = etude.resultat("regle", nom_t)
        print(f"\n## {trajectoire.libelle}\n")
        print("| Lecture | Prime 2027 | 2030 | 2035 | 2040 | 2050 | 2060 | Sous zéro dès | "
              "Réserve max | Dette d'un retraité, max | Écart à α = 1 | dont stock | "
              "Dette 2070 | Un euro du stock 2040 | 2050 | α = 1, 2050 |")
        print("|---" * 16 + "|")
        for cle in DECIDEES:
            r = etude.resultat(cle, nom_t)
            euro = r.euro_stock
            dette, annee = _dette_en_annees(euro, r)
            ecart = r.moyenne(r.depense) - etalon.moyenne(etalon.depense)
            ecart_stock = r.moyenne({a: r.pib(r.stock.servi, a) - r.pib(r.stock.etalon, a)
                                     for a in r.depense})
            print(f"| {LIBELLES[cle]} | "
                  + " | ".join(_nb(100 * euro.prime[a]) for a in (2027, 2030, 2035, 2040,
                                                                   2050, 2060))
                  + f" | {_premiere(euro, lambda p: p < 0)} | "
                  f"{_nb(100 * max(r.pib(r.reserve, a) for a in r.depense))} | "
                  f"{_pc(dette, 1)}" + (f" ({annee})" if dette > 5e-4 else "") + " | "
                  f"{_pc(ecart)} | {_pc(ecart_stock)} | "
                  f"{_nb(100 * r.dette_publique[FIN], 1)} | "
                  f"{_nb(euro.servi[2040], 3)} | {_nb(euro.servi[2050], 3)} | "
                  f"{_nb(etalon.euro_stock.servi[2050], 3)} |")
        print("\nÀ la lettre, la prime ne baisse qu'une fois la réserve seule suffisante "
              "(« au seuil ») :\n")
        print("| Lecture | Prime 2030 | 2035 | 2040 | 2045 | 2050 | 2060 | Sous zéro dès | "
              "Dette d'un retraité, max | Un euro du stock 2040 | 2050 |")
        print("|---" * 11 + "|")
        for cle in DECIDEES:
            r = etude.resultat(cle, nom_t)
            euro = r.euro_seuil
            dette, annee = _dette_en_annees(euro, r)
            print(f"| {LIBELLES[cle]} | "
                  + " | ".join(_nb(100 * euro.prime[a]) for a in (2030, 2035, 2040, 2045,
                                                                   2050, 2060))
                  + f" | {_premiere(euro, lambda p: p < 0)} | {_pc(dette, 1)}"
                  + (f" ({annee})" if dette > 5e-4 else "") + " | "
                  f"{_nb(euro.servi[2040], 3)} | {_nb(euro.servi[2050], 3)} |")


def imprimer_personnelle(etude: Etude) -> None:
    """La contribution de 1 % dans une réserve à soi, en plus du compte : la
    survie vaut un, rien ne passe des morts aux vivants. Ce qui reste à la
    mort, le coût ne le compte pas encore."""
    print("\n# Une réserve personnelle de 1 %, en années de la pension servie\n")
    print("| Trajectoire | Réserve 2030 | 2035 | 2040 | 2045 | 2050 | "
          "Dette 2040 | 2045 | 2050 |")
    print("|---" * 9 + "|")
    une = tuple((annee, 1.0) for annee in range(DEBUT, FIN + 1))
    voie = _voie(etude.voies, "v1_un_pour_cent", etude.baisse_voie_2, etude.primes)
    for nom_t, trajectoire in etude.trajectoires.items():
        r = etude.resultat("v1_un_pour_cent", nom_t)
        euro = _pensions(voie, trajectoire, une).detail_stock()
        annuelle = {a: euro.servi[a] for a in euro.servi}
        print(f"| {trajectoire.libelle} | "
              + " | ".join(_nb(euro.reserve[a] / annuelle[a]) for a in (2030, 2035, 2040,
                                                                         2045, 2050))
              + " | " + " | ".join(_nb(euro.dette[a] / (annuelle[a] * _prix(r, a)))
                                   for a in (2040, 2045, 2050)) + " |")


def _prix(r: Resultat, annee: int) -> float:
    """Les prix de ``annee`` sur ceux de la bascule, sous la trajectoire."""
    prix = 1.0
    for a in range(DEBUT + 1, annee + 1):
        prix *= 1 + r.inflation[a]
    return prix


def imprimer_annees(etude: Etude, trajectoire: str, annees=VUES) -> None:
    print(f"\n## {etude.trajectoires[trajectoire].libelle}, année par année\n")
    print("Dépense du scénario 6 (pensions, réversion gardée comprise), en % du PIB ; "
          "entre parenthèses, la dette du plancher ou la réserve.\n")
    print("| Année | " + " | ".join(LIBELLES[c] for c in CLES) + " |")
    print("|---" * (len(CLES) + 1) + "|")
    for annee in annees:
        cases = []
        for cle in CLES:
            r = etude.resultat(cle, trajectoire)
            case = _nb(100 * r.depense[annee])
            dette = r.pib(r.stock.dette, annee) + r.pib(r.nouvelles.dette, annee)
            if r.reserve:
                case += f" (réserve {_nb(100 * r.pib(r.reserve, annee))})"
            elif dette > 5e-5:
                case += f" (dette {_nb(100 * dette)})"
            cases.append(case)
        print(f"| {annee} | " + " | ".join(cases) + " |")


def ecrire_csv(etude: Etude, chemin: Path) -> None:
    with chemin.open("w", newline="", encoding="utf-8") as flux:
        ecrivain = csv.writer(flux)
        ecrivain.writerow([
            "trajectoire", "voie", "annee", "depense_pib", "garantie_pib", "solde_pib",
            "dette_publique_pib", "stock_pib", "nouvelles_pib", "etalon_stock_pib",
            "etalon_nouvelles_pib", "dette_plancher_stock_pib",
            "dette_plancher_nouvelles_pib", "reserve_pib", "euro_stock_constants",
            "euro_stock_regle_constants", "dette_retraite_stock_courants",
            "euro_2030_constants", "inflation"])
        for (cle, nom_t), r in etude.resultats.items():
            for annee in range(DEBUT, FIN + 1):
                ecrivain.writerow([
                    nom_t, cle, annee, r.depense[annee], r.garantie[annee], r.solde[annee],
                    r.dette_publique[annee], r.pib(r.stock.servi, annee),
                    r.pib(r.nouvelles.servi, annee), r.pib(r.stock.etalon, annee),
                    r.pib(r.nouvelles.etalon, annee), r.pib(r.stock.dette, annee),
                    r.pib(r.nouvelles.dette, annee),
                    r.pib(r.reserve, annee) if r.reserve else 0.0,
                    r.euro_stock.servi[annee], r.euro_stock.regle[annee],
                    r.euro_stock.dette[annee],
                    r.euro_2030.servi.get(annee, ""), r.inflation[annee]])


def main(arguments: list[str] | None = None) -> None:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    lecteur.add_argument("--annees", action="store_true",
                         help="chaque année de 2026 à 2070, sous chaque trajectoire")
    lecteur.add_argument("--csv", type=Path, help="tout écrire dans ce fichier")
    lecteur.add_argument("--decidee", action="store_true",
                         help="la voie 1 décidée seule, en ses lectures")
    options = lecteur.parse_args(arguments)
    etude = etudier()
    if options.decidee:
        imprimer_decidee(etude)
        imprimer_personnelle(etude)
        return
    print(f"Baisse d'avance de la voie 2, sous le COR : {_nb(100 * etude.baisse_voie_2)} %")
    for choc, prime in etude.primes.items():
        print(f"Prime de la voie 1 couvrant « {etude.trajectoires[choc].libelle} » : "
              f"{_nb(100 * prime)} %")
    regle = etude.resultat("avant", "cor")
    print("Le stock aux prix, en part de la masse de droits directs du scénario 6 : "
          + ", ".join(f"{a} {_nb(100 * regle.stock.servi[a] / (regle.stock.servi[a] + regle.nouvelles.servi[a]), 0)} %"
                      for a in (2026, 2030, 2040, 2050, 2060)))
    imprimer_synthese(etude)
    imprimer_decidee(etude)
    imprimer_personnelle(etude)
    for trajectoire in etude.trajectoires:
        imprimer_annees(etude, trajectoire,
                        range(DEBUT, FIN + 1) if options.annees else VUES)
    if options.csv:
        ecrire_csv(etude, options.csv)


if __name__ == "__main__":
    main()
