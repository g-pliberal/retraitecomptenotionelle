#!/usr/bin/env python3
"""Régénère, dans la prose, les tableaux que le modèle sait calculer.

    python scripts/construire_tableaux_md.py             # réécrit
    python scripts/construire_tableaux_md.py --verifier  # échoue s'il est périmé

Le problème qu'il traite
------------------------

Le site calcule le tableau des règles d'indexation à chaque rendu — c'est
``cumulsIndexation`` de ``moteur/js/pages.js``, quatre millisecondes — et la prose
en porte deux copies, dans le README et dans la méthodologie, recopiées à la
main. La page l'a déjà payé une fois : ses neuf nombres y étaient écrits en dur
et l'un d'eux mentait de trois dixièmes de point. Les deux copies de la prose
sont restées dans cet état, à ceci près que personne ne les rend : elles ne se
périment pas bruyamment, elles se périment en silence.

Ce script les écrit entre deux repères, depuis le modèle, et
``tests/test_prose.py`` refuse une prose qui ne serait plus celle qu'il
produit. Le geste est celui de ``construire_regimes_md.py`` pour
``docs/regimes.md`` : ce qui se calcule ne se recopie pas.

Ce qu'il ne fait pas
--------------------

Il ne touche qu'aux lignes entre les repères. La phrase qui commente le
tableau — « une cotisation de 1950 ne conserve que 1,5 % de sa valeur
réelle » — reste de la prose, et c'est l'ancre de ``verifier_prose.py`` qui la
tient, avec la sonde ``tableau`` qui lit la cellule produite ici.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import Parametres, pont  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402
from retraite_notionnelle.web.site import module, site  # noqa: E402

#: Les règles que le site compare, et les bornes de leur cumul : le texte du
#: site les écrit, en JavaScript (``moteur/js/pages.js``), et ce script les y
#: lit, par node, comme ce qu'elles rendent (:func:`cumuls`).
_SITE = module("pages")
REGLES_COMPAREES = tuple(tuple(regle) for regle in _SITE.REGLES_COMPAREES)
ANNEE_VERSEMENT_COMPARE = _SITE.ANNEE_VERSEMENT_COMPARE
ANNEE_ARRIVEE_COMPAREE = _SITE.ANNEE_ARRIVEE_COMPAREE

#: Les documents qui portent une copie du tableau, et l'intitulé de leur
#: première colonne — le README parle des « comptes », la méthodologie de la
#: « revalorisation cumulée ». Le reste est identique, et c'est bien le
#: problème : deux copies d'un même calcul.
DOCUMENTS = {
    "README.md": "Comptes 1941-2025",
    "docs/methodologie.md": f"Revalorisation cumulée "
                            f"{ANNEE_VERSEMENT_COMPARE + 1}-{ANNEE_ARRIVEE_COMPAREE}",
}

REPERE = "indexation"

#: Le second tableau du §1 du README : ce que la correction de la ligne de
#: référence déplace, génération par génération. Les cinq générations sont
#: celles que la prose commente — deux carrières d'avant 1987, une à cheval,
#: deux d'après —, et la carrière est celle qu'elle annonce.
GENERATIONS = (1920, 1930, 1945, 1958, 1990)
AGE_DEBUT_GENERATIONS = 20
AGE_LIQUIDATION_GENERATIONS = 62
REPERE_GENERATIONS = "generations"
#: Le scénario dont le tableau lit l'écart au système actuel.
SCENARIO_COMPARE = "notionnel_retroactif"


def nombre(valeur: float, decimales: int = 1) -> str:
    """« 1 538,2 » : virgule décimale, espace ordinaire pour les milliers.

    C'est la typographie du dépôt, celle que `verifier_prose.py` sait relire.
    """
    rendu = f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return rendu


def cumuls() -> dict[str, float]:
    """Le rendement cumulé de chaque règle, tel que le site le calcule : par
    sa propre fonction, ``cumulsIndexation`` de ``moteur/js/pages.js``, sous
    les réglages de référence (action 161, lot A)."""
    return dict(_SITE.cumuls_indexation(site().contexte))


def tableau(entete: str) -> str:
    """Le tableau markdown, prêt à poser entre les repères."""
    rendus = cumuls()
    prix = rendus["Indexation sur les prix"]
    lignes = [
        f"| Règle | {entete} | Prix | Pouvoir d'achat conservé |",
        "|---|---|---|---|",
    ]
    for libelle, _, _ in REGLES_COMPAREES:
        valeur = rendus[libelle]
        conserve = f"{nombre(valeur / prix * 100)} %"
        # La règle demandée par le programme est celle que la prose commente :
        # elle est mise en valeur des deux côtés, comme sur la page.
        if libelle == REGLES_COMPAREES[0][0]:
            libelle_rendu, conserve = libelle, f"**{conserve}**"
        else:
            libelle_rendu = libelle
        lignes.append(f"| {libelle_rendu} | ×{nombre(valeur)} | ×{nombre(prix)} "
                      f"| {conserve} |")
    return "\n".join(lignes)


def ecarts_par_generation() -> list[tuple[int, float, float]]:
    """L'écart du scénario rétroactif au scénario 1, sous les deux règles.

    La ligne de référence « Prix » est celle que le dépôt a longtemps donnée
    pour la règle qui neutralise l'indexation ; la ligne corrigée est la
    revalorisation réellement portée au compte. Ce que leur différence
    déplace se lit génération par génération, et change de signe pour les
    carrières entièrement postérieures à 1987.

    Le portage bâtit et simule les cinq carrières sous chaque règle
    (``pont.carrieres``, action 161, lot A) ; l'écart qu'il rend, la pension
    du scénario rapportée à celle du système actuel, moins un, se lit ici en
    points.
    """
    from retraite_notionnelle.config import ModeIndexation

    cas = [{"cle": str(generation),
            "options": {"annee_naissance": generation, "sexe": "H",
                        "affiliation": "salarie_prive_non_cadre",
                        "age_debut": AGE_DEBUT_GENERATIONS,
                        "age_liquidation": AGE_LIQUIDATION_GENERATIONS}}
           for generation in GENERATIONS]
    ecarts = []
    for mode in (ModeIndexation.PRIX,
                 ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE):
        lus, refus = pont.carrieres(cas, [SCENARIO_COMPARE],
                                    parametres=replace(Parametres(), mode_indexation=mode))
        if refus:
            raise SystemExit(
                f"le portage refuse des carrières du tableau des générations : {refus}")
        ecarts.append({cle: lu["ecarts"][SCENARIO_COMPARE] * 100 for cle, lu in lus.items()})
    return [(generation, *(lus[str(generation)] for lus in ecarts)) for generation in GENERATIONS]


def tableau_generations() -> str:
    """Le tableau des cinq générations, prêt à poser entre les repères."""
    rendus = ecarts_par_generation()
    differences = [corrige - prix for _, prix, corrige in rendus]
    haut, bas = max(differences), min(differences)
    lignes = [
        "| Génération | Carrière | Ligne de référence « Prix » | Ligne corrigée | Écart |",
        "|---|---|---|---|---|",
    ]
    for (generation, prix, corrige), difference in zip(rendus, differences):
        debut = generation + AGE_DEBUT_GENERATIONS
        fin = generation + AGE_LIQUIDATION_GENERATIONS
        # Un écart nul n'a pas de signe : « -0,0 pt » se lit comme une erreur
        # de calcul, quand c'est la mesure qui dit « rien ne bouge ».
        arrondi = round(difference, 1)
        ecrit = (f"{arrondi:+.1f}" if arrondi else "0,0").replace(".", ",")
        ecrit = ecrit if ecrit.endswith("pt") else f"{ecrit} pt"
        # Les deux extrêmes portent le propos : le plus grand écart, et celui
        # qui change de signe. Les mettre en valeur est le geste de la page.
        if difference in (haut, bas):
            ecrit = f"**{ecrit}**"
        lignes.append(
            f"| {generation} | {debut}-{fin} | {nombre(prix)} % "
            f"| {nombre(corrige)} % | {ecrit} |")
    return "\n".join(lignes)


#: L'exemple du §3 du README : le tableau des six scénarios, du pilier et de
#: qui verse la cotisation, pour la carrière dont le bloc donne l'adresse sur
#: le site. Il était collé à la main, et il avait vieilli — la rente du pilier
#: annonçait 1 569 € quand le modèle en sert 1 515 — sans que rien puisse le
#: dire.
REPERE_EXEMPLE = "exemple_fonctionnaire"
TITRE_EXEMPLE = "Fonctionnaire d'État née en 1975, 20 % de primes, partie à 64 ans"

#: L'exemple de l'introduction : un agent de conduite parti à cinquante ans,
#: avant la bascule. Seuls les six scénarios sont repris ; son titre dit
#: l'anticipation que le modèle calcule, et non celle qu'on a cru lire.
REPERE_SNCF = "exemple_sncf"

#: Le simulateur du site, et la requête de chaque exemple : le README donne
#: cette adresse, et son tableau est ce que le portage en simule
#: (``pont.simulations``, comme le site). La carrière est celle des sondes de
#: la prose (``mesures_prose.EXEMPLES``), au résultat près, ce que
#: ``tests/test_prose.py`` vérifie (note de décision 0008, action 161).
SIMULATEUR_DU_SITE = "https://g-pliberal.github.io/retraitecomptenotionelle/simuler/"
REQUETES = {
    "fonctionnaire": {"naissance": "1975", "sexe": "F", "statut": "fonctionnaire_etat",
                      "debut": "22", "liquidation": "64", "unite_revenu": "moyen",
                      "salaire": "1", "profil": "ascendant", "primes": "0.2",
                      "montants": "brut"},
    "sncf": {"naissance": "1955", "sexe": "H", "statut": "agent_sncf",
             "debut": "20", "liquidation": "50", "unite_revenu": "moyen",
             "salaire": "1.1", "profil": "ascendant", "montants": "brut"},
}

LARGEUR = 104


def adresse_du_site(exemple: str) -> str:
    """L'adresse du simulateur du site qui ouvre la carrière d'un exemple."""
    from urllib.parse import urlencode

    return f"{SIMULATEUR_DU_SITE}#{urlencode(REQUETES[exemple])}"


@lru_cache(maxsize=None)
def simulation(exemple: str) -> dict:
    """Le résultat que le portage simule de l'adresse d'un exemple, comme le
    site la simule (``Comparaison.dictionnaire()``)."""
    lus, refus = pont.simulations([{"cle": exemple, "requete": REQUETES[exemple]}])
    if refus:
        raise SystemExit(f"le portage refuse l'exemple {exemple} du README : {refus}")
    return lus[exemple]["resultat"]


def _titres() -> list[tuple[str, int, str]]:
    """Les scénarios notionnels, dans l'ordre : leur clé, leur numéro et leur
    nom, que les univers de la proposition écrivent en données."""
    from retraite_notionnelle.noyau import univers

    return [(u.id, u.numero, u.nom) for u in univers.de_la_proposition()]


class _Tableau:
    """La mise en forme du tableau d'une simulation, lue du résultat que le
    pont rend : celle que ``Comparaison.tableau()`` écrivait, à l'octet, pour
    les lignes que le README reprend."""

    def __init__(self, resultat: dict) -> None:
        self.r = resultat
        self.scenarios = resultat["scenarios"]
        self.reporte = resultat["liquidation_liberal"]["reportee"]

    def coefficient(self, scenario: str | None) -> float:
        if scenario == "notionnel_liberal" and self.reporte:
            return self.r["liquidation_liberal"]["coefficient_euros_constants"]
        return self.r["unite"]["coefficient"]

    def ecart(self, montant: float, scenario: str) -> float:
        reference = self.scenarios["actuel"]["pension_annuelle"]
        if reference <= 0:
            return float("nan")
        if not (scenario == "notionnel_liberal" and self.reporte):
            return montant / reference - 1.0
        return (montant * self.coefficient(scenario)
                / (reference * self.coefficient(None)) - 1.0)

    def ligne(self, nom: str, montant: float, ecart: float | str | None,
              scenario: str | None = None) -> str:
        if isinstance(ecart, str):
            variation = ecart
        else:
            variation = "réf." if ecart is None else f"{ecart:+.1%}"
        constant = montant * self.coefficient(scenario)
        return (f"{nom:<62} {montant:>10,.0f}€ {constant:>10,.0f}€ "
                f"{constant/12:>8,.0f}€ {variation:>8}")

    def scenarios_(self) -> list[str]:
        """L'en-tête et les six scénarios."""
        bascule = self.r["regime_fusionne"]["annee_bascule"]
        lignes = [f"{'Scénario':<62} {'Courants':>11} {'Constants':>11} "
                  f"{'Mensuel':>9} {'Écart':>8}",
                  "-" * LARGEUR,
                  self.ligne("1. Système actuel", self.scenarios["actuel"]["pension_annuelle"],
                             None)]
        for cle, numero, titre in _titres():
            montant = self.scenarios[cle]["pension_annuelle"]
            lignes.append(self.ligne(f"{numero}. " + titre.format(bascule=bascule),
                                     montant, self.ecart(montant, cle), cle))
        return lignes

    def a_part(self) -> list[str]:
        """Ce qui est servi à part : la retraite additionnelle, que les six
        scénarios servent à l'identique, puis le pilier capitalisé du dernier,
        et son total."""
        lignes = []
        hors_repartition = self.scenarios["actuel"]["pension_hors_repartition"]
        if hors_repartition > 0:
            lignes += ["-" * LARGEUR,
                       self.ligne("   hors répartition (RAFP), servi à part, identique aux 6",
                                  hors_repartition, "")]
        liberal = self.scenarios["notionnel_liberal"]
        rente = liberal["rente_capitalisation_obligatoire"]
        if rente > 0:
            numero = _titres()[-1][1]
            volontaire = liberal["rente_capitalisation_volontaire"]
            lignes.append("-" * LARGEUR)
            if volontaire > 0:
                lignes += [
                    self.ligne(f"   + rente capitalisée obligatoire, scénario {numero}",
                               rente - volontaire, "", "notionnel_liberal"),
                    self.ligne("   + rente capitalisée volontaire, les 5 points rendus",
                               volontaire, "", "notionnel_liberal")]
            else:
                lignes.append(self.ligne(
                    f"   + rente du pilier capitalisé, scénario {numero} seul",
                    rente, "", "notionnel_liberal"))
            total = liberal["pension_totale"]
            lignes.append(self.ligne(f"   = total servi par le scénario {numero}", total,
                                     self.ecart(total, "notionnel_liberal"),
                                     "notionnel_liberal"))
        return lignes

    def qui_verse(self) -> list[str]:
        """Qui verse la cotisation, en euros courants cumulés."""
        employeur = self.r["contribution_employeur"]
        origines = employeur["annees_par_origine"]
        if not (employeur["employeur"] > 0 or origines):
            return []
        lignes = ["Qui verse la cotisation, en euros courants cumulés :"]
        if employeur["employeur"] > 0:
            lignes += [
                f"  part salariale     {employeur['agent']:>13,.0f} €   scénarios 2 et 3",
                f"  part patronale     {employeur['employeur']:>13,.0f} €"
                f"   soit {employeur['part']:.0%} du total",
                f"  total              {employeur['total']:>13,.0f} €   scénarios 4 et 5",
            ]
        if origines:
            trouvees = somme_ordonnee(nombre for origine, nombre in origines.items()
                                      if origine != "repli")
            repli = origines.get("repli", 0)
            lignes.append(
                f"  contribution employeur publique trouvée sur {trouvees} année(s)"
                + (f", inconnue sur {repli} — le taux du privé y tient lieu d'étalon"
                   if repli else ""))
        return lignes


def _bloc(exemple: str, titre: str, corps: list[str]) -> str:
    return "\n".join([
        f"[Ouvrir cette carrière dans le simulateur du site]({adresse_du_site(exemple)})",
        "", "```", titre, "", *(l.rstrip() for l in corps), "```"])


def sortie_exemple() -> str:
    """Le tableau de l'exemple et la ligne de qui verse quoi, sans le reste."""
    tableau_ = _Tableau(simulation("fonctionnaire"))
    return _bloc("fonctionnaire", TITRE_EXEMPLE,
                 tableau_.scenarios_() + tableau_.a_part() + [""] + tableau_.qui_verse())


def sortie_sncf() -> str:
    """Les six scénarios de l'agent de conduite, sous le titre qui les situe."""
    resultat = simulation("sncf")
    ecart = resultat["age_reference"]
    situation = (f" ({abs(ecart['ecart_annees']):g} ans avant l'âge de référence)"
                 if ecart["anticipe"] else "")
    titre = f"Agent de conduite SNCF né en 1955, parti à 50 ans{situation}"
    return _bloc("sncf", titre, _Tableau(resultat).scenarios_())


def remplacer(texte: str, repere: str, contenu: str) -> str:
    debut, fin = f"<!-- {repere}:debut -->", f"<!-- {repere}:fin -->"
    if debut not in texte or fin not in texte:
        raise SystemExit(f"repères « {repere} » absents du document")
    avant = texte.split(debut)[0]
    apres = texte.split(fin, 1)[1]
    return f"{avant}{debut}\n{contenu}\n{fin}{apres}"


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="échoue si un document est périmé")
    arguments = analyseur.parse_args()

    perimes = []
    for document, entete in DOCUMENTS.items():
        chemin = RACINE / document
        texte = chemin.read_text(encoding="utf-8")
        voulu = remplacer(texte, REPERE, tableau(entete))
        if voulu == texte:
            continue
        if arguments.verifier:
            perimes.append(document)
            continue
        chemin.write_text(voulu, encoding="utf-8", newline="\n")
        print(f"{document} : tableau des règles d'indexation réécrit")

    # Le second tableau ne vit que dans le README : il commente la correction
    # de la ligne de référence, que la méthodologie ne reprend pas. La sortie
    # de l'exemple du §3 non plus.
    chemin = RACINE / "README.md"
    for repere, fabrique, quoi in (
            (REPERE_GENERATIONS, tableau_generations, "tableau des générations"),
            (REPERE_EXEMPLE, sortie_exemple, "sortie de l'exemple du §3"),
            (REPERE_SNCF, sortie_sncf, "sortie de l'exemple de l'introduction")):
        texte = chemin.read_text(encoding="utf-8")
        voulu = remplacer(texte, repere, fabrique())
        if voulu == texte:
            continue
        if arguments.verifier:
            perimes.append(f"README.md ({quoi})")
        else:
            chemin.write_text(voulu, encoding="utf-8", newline="\n")
            print(f"README.md : {quoi} réécrit")

    if perimes:
        print("\n".join(
            f"{document} : un bloc produit a dérivé — "
            "lancer python scripts/construire_tableaux_md.py"
            for document in perimes), file=sys.stderr)
        return 1
    if arguments.verifier:
        print("les tableaux produits sont à jour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
