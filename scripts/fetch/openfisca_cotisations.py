#!/usr/bin/env python3
"""Récupération des taux de cotisation vieillesse du régime général.

    python scripts/fetch/openfisca_cotisations.py

Le taux de cotisation est ce qui alimente le compte notionnel : c'est, avec le
salaire, la seule grandeur qui détermine le capital accumulé. Une erreur de deux
points sur quarante ans déplace la pension d'autant.

Les taux historiques ne sont publiés dans aucune série statistique : ils vivent
dans des décrets. La seule transcription machine complète est celle
d'**OpenFisca-France**, le modèle socio-fiscal de référence maintenu par
l'administration, qui date chaque taux au jour de son entrée en vigueur depuis
octobre 1967 et cite ses références.

Quatre taux sont récupérés, dont la somme donne le taux total pesant sur le
salaire — c'est cette somme que le modèle appelle ``taux_cotisation_retraite`` :

* part salariale et part patronale **sous plafond** (depuis 1967) ;
* part salariale et part patronale **déplafonnées** (depuis 1991).

Statut de fiabilité. OpenFisca est une transcription tierce, pas le producteur :
ces taux ne sont pas versés automatiquement dans les fiches de régime et ne
peuvent pas y porter le niveau ``certifiee``. ``scripts/verifier_donnees.py`` les
confronte aux valeurs saisies et signale les écarts ; la correction d'une fiche
reste une décision, prise à la main, tracée dans ses notes.

Avant octobre 1967, rien : les taux de 1930 à 1967 restent saisis depuis les
ordonnances de 1945 et leurs modificatifs.

Les COMPLÉMENTAIRES du privé (Agirc, Arrco, régime unifié) sont récupérées dans
le même fichier, tranche par tranche et sous quatre formes : le taux EFFECTIF
(ce qui est prélevé), le taux CONTRACTUEL (ce qui ouvre des points), le taux
d'APPEL qui relie les deux, et la répartition salarié/employeur. OpenFisca
transcrit deux barèmes par régime, selon la date d'adhésion de l'entreprise ;
les deux sont récupérés, et ``VARIANTE_RETENUE`` dit lequel les fiches portent.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = ("https://raw.githubusercontent.com/openfisca/openfisca-france/master/"
          "openfisca_france/parameters/prelevements_sociaux/"
          "cotisations_securite_sociale_regime_general/cnav")
COMPOSANTES = {
    "salarie_plafonnee": "salarie/vieillesse_plafonnee.yaml",
    "employeur_plafonnee": "employeur/vieillesse_plafonnee.yaml",
    "salarie_deplafonnee": "salarie/vieillesse_deplafonnee.yaml",
    "employeur_deplafonnee": "employeur/vieillesse_deplafonnee.yaml",
}
SORTIE = Path("data/brut/openfisca_cotisations.json")
PREMIERE_ANNEE = 1967

#: Racine des barèmes des régimes COMPLÉMENTAIRES du privé.
RACINE_COMPLEMENTAIRES = (
    "https://raw.githubusercontent.com/openfisca/openfisca-france/master/"
    "openfisca_france/parameters/prelevements_sociaux/"
    "regimes_complementaires_retraite_secteur_prive"
)

#: Barèmes à tranches des complémentaires : régime -> variante -> fichier.
#:
#: TAUX EFFECTIFS, c'est-à-dire ce qui est prélevé — taux d'appel compris. Les
#: fiches du dépôt portent la même grandeur, si bien que les deux se comparent
#: directement. L'Arrco distingue les entreprises créées avant et après le
#: 1er janvier 1997, l'Agirc avant et après le 1er janvier 1981 : chaque accord
#: a imposé aux entreprises NOUVELLES un taux plus élevé que le minimum laissé
#: aux entreprises déjà adhérentes, jusqu'à ce que les relèvements de 1994
#: (Agirc) et de 1996-2005 (Arrco) rejoignent les deux barèmes.
COMPLEMENTAIRES = {
    "arrco": {
        "entreprises_existantes": (
            "arrco/taux_effectifs/entreprises_avant_01_01_1997/arrco.yaml", 1962),
        "entreprises_nouvelles": (
            "arrco/taux_effectifs/entreprises_apres_01_01_1997/arrco.yaml", 1962),
    },
    "agirc": {
        "entreprises_existantes": (
            "agirc/taux_effectifs/entreprises_avant_01_01_1981/agirc.yaml", 1947),
        "entreprises_nouvelles": (
            "agirc/taux_effectifs/entreprises_apres_01_01_1981/agirc.yaml", 1947),
    },
    "agirc_arrco": {
        "entreprises_existantes": ("agirc_arrco/tx_total.yaml", 2019),
    },
}

#: Le barème que les fiches du dépôt portent : celui des entreprises qui
#: existaient déjà à la date de l'accord (Agirc : avant 1981 ; Arrco : avant
#: 1997). C'est la population la plus nombreuse — la carrière saisie ne dit pas
#: la date de création de l'employeur, et l'assuré né avant 1965 a passé
#: l'essentiel de sa carrière dans une entreprise antérieure à ces dates —, et
#: c'est la seule variante qui porte une tranche 2 pour les non-cadres avant
#: 1997 : le barème des entreprises nouvelles n'y cotise rien avant cette date.
#: Le dépôt portait auparavant le barème des entreprises nouvelles, décrit
#: comme « de droit commun » ; il est conservé dans le fichier de sortie pour
#: mesurer ce que ce choix déplace.
VARIANTE_RETENUE = "entreprises_existantes"

#: TAUX CONTRACTUELS — ceux qui ouvrent des points —, mêmes variantes.
#: ``effectif = contractuel × appel``, et c'est l'appel que le moteur retire
#: quand il convertit une cotisation en points (``ValeursPoint.achat``).
CONTRACTUELS = {
    "arrco": {
        "entreprises_existantes": (
            "arrco/taux_contractuels/entreprises_avant_01_01_1997/arrco.yaml", 1962),
        "entreprises_nouvelles": (
            "arrco/taux_contractuels/entreprises_apres_01_01_1997/arrco.yaml", 1962),
    },
    "agirc": {
        "entreprises_existantes": (
            "agirc/taux_contractuels/entreprises_avant_01_01_1981/agirc.yaml", 1947),
        "entreprises_nouvelles": (
            "agirc/taux_contractuels/entreprises_apres_01_01_1981/agirc.yaml", 1947),
    },
    "agirc_arrco": {
        "entreprises_existantes": ("agirc_arrco/tx_calcul.yaml", 2019),
    },
}

#: Taux d'appel, un par régime et par année : fichiers à une seule valeur.
APPELS = {
    "arrco": ("arrco/taux_appel.yaml", 1962),
    "agirc": ("agirc/taux_appel.yaml", 1948),
    "agirc_arrco": ("agirc_arrco/tx_appel.yaml", 2019),
}

#: Barèmes salarié et employeur des taux effectifs, pour la répartition. Pour
#: l'Arrco, le barème non cadre porte les deux tranches ; le barème cadre
#: n'a que la tranche 1, la tranche 2 du cadre étant l'Agirc.
REPARTITION = {
    "arrco": {
        "salarie": "arrco/taux_effectifs_salaries_employeurs/salarie/noncadre/arrco.yaml",
        "employeur": "arrco/taux_effectifs_salaries_employeurs/employeur/noncadre/arrco.yaml",
    },
    "agirc": {
        "salarie": "agirc/taux_effectifs_salaries_employeurs/avant81/salarie/agirc.yaml",
        "employeur": "agirc/taux_effectifs_salaries_employeurs/avant81/employeur/agirc.yaml",
    },
    "agirc_arrco": {
        "salarie": "agirc_arrco/salarie/agirc_arrco.yaml",
        "employeur": "agirc_arrco/employeur/agirc_arrco.yaml",
    },
}


def _taux(texte: str) -> dict[str, float]:
    """Extrait le barème d'un fichier OpenFisca : date d'effet -> taux.

    Les fichiers décrivent un barème à une seule tranche ; seul son taux nous
    intéresse, le seuil valant zéro. Une valeur nulle signifie « cotisation non
    encore instituée » et vaut donc zéro.
    """
    import yaml

    charge = yaml.safe_load(texte)
    bareme = charge["brackets"][0]["rate"]
    return {
        str(cle): float(contenu["value"] or 0.0)
        for cle, contenu in bareme.items()
    }


def _valeurs(texte: str) -> dict[str, float]:
    """Fichier à une seule valeur datée (les taux d'appel) : date -> valeur.

    Une valeur nulle marque la fin de la série — l'Agirc et l'Arrco s'arrêtent
    au 1er janvier 2019, où le régime unifié prend leur place — et vaut zéro,
    que ``_en_vigueur`` laisse ensuite tomber.
    """
    import yaml

    charge = yaml.safe_load(texte)
    return {
        str(cle): float((contenu or {}).get("value") or 0.0)
        for cle, contenu in charge["values"].items()
    }


def _tranches(texte: str) -> list[dict[str, float]]:
    """Barème à plusieurs tranches : une table date -> taux par tranche.

    Les complémentaires cotisent par tranche de salaire, et le taux de chacune
    a sa propre histoire — 2,5 % en 1962 sur la première tranche de l'Arrco,
    7,75 % en 2015 ; rien sur la seconde avant 1997, 20,25 % ensuite. Une
    valeur nulle signifie « tranche non cotisée cette année-là ».
    """
    import yaml

    charge = yaml.safe_load(texte)
    tranches = []
    for tranche in charge["brackets"]:
        tranches.append({
            str(cle): float((contenu or {}).get("value") or 0.0)
            for cle, contenu in tranche["rate"].items()
        })
    return tranches


def _en_vigueur(bareme: dict[str, float], annee: int) -> float:
    """Taux applicable au 1er janvier de l'année.

    Les revalorisations de milieu d'année sont ignorées : le modèle raisonne en
    années pleines, et retenir le taux du 1er janvier est le choix le plus
    lisible — il est explicité ici plutôt que caché dans un calcul.
    """
    anterieures = [cle for cle in sorted(bareme) if cle[:4] <= str(annee)]
    return bareme[anterieures[-1]] if anterieures else 0.0


def main() -> int:
    baremes: dict[str, dict[str, float]] = {}
    for nom, chemin in COMPOSANTES.items():
        try:
            demande = urllib.request.Request(
                f"{RACINE}/{chemin}", headers={"User-Agent": "retraite-notionnelle/0.1"}
            )
            with urllib.request.urlopen(demande, timeout=120) as reponse:
                baremes[nom] = _taux(reponse.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"ÉCHEC   {nom} : {erreur}", file=sys.stderr)
            return 1
        print(f"OK      {nom:<24} {len(baremes[nom])} dates d'effet")

    derniere = max(int(cle[:4]) for bareme in baremes.values() for cle in bareme)
    serie = {}
    for annee in range(PREMIERE_ANNEE, derniere + 1):
        parts = {nom: _en_vigueur(bareme, annee) for nom, bareme in baremes.items()}
        serie[str(annee)] = {
            **{nom: round(valeur, 5) for nom, valeur in parts.items()},
            "total": round(sum(parts.values()), 5),
        }

    def _lire(chemin: str) -> str:
        demande = urllib.request.Request(
            f"{RACINE_COMPLEMENTAIRES}/{chemin}",
            headers={"User-Agent": "retraite-notionnelle/0.1"},
        )
        with urllib.request.urlopen(demande, timeout=120) as reponse:
            return reponse.read().decode("utf-8")

    def _annuel(tranches: list[dict[str, float]], premiere: int
                ) -> dict[str, dict[str, float]]:
        annuel: dict[str, dict[str, float]] = {}
        for annee in range(premiere, derniere + 1):
            valeurs = {f"tranche_{i + 1}": round(_en_vigueur(t, annee), 5)
                       for i, t in enumerate(tranches)}
            if any(valeurs.values()):
                annuel[str(annee)] = valeurs
        return annuel

    complementaires: dict[str, dict[str, dict[str, float]]] = {}
    variantes: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    contractuels: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    appels: dict[str, dict[str, float]] = {}
    repartition: dict[str, dict[str, dict[str, float]]] = {}
    try:
        for regime, par_variante in COMPLEMENTAIRES.items():
            for variante, (chemin, premiere) in par_variante.items():
                annuel = _annuel(_tranches(_lire(chemin)), premiere)
                variantes.setdefault(regime, {})[variante] = annuel
                if variante == VARIANTE_RETENUE:
                    complementaires[regime] = annuel
            print(f"OK      {regime:<24} taux effectifs, "
                  f"{len(par_variante)} variante(s), "
                  f"{len(complementaires[regime])} années")
        for regime, par_variante in CONTRACTUELS.items():
            for variante, (chemin, premiere) in par_variante.items():
                contractuels.setdefault(regime, {})[variante] = _annuel(
                    _tranches(_lire(chemin)), premiere)
            print(f"OK      {regime:<24} taux contractuels")
        for regime, (chemin, premiere) in APPELS.items():
            bareme = _valeurs(_lire(chemin))
            appels[regime] = {
                str(a): round(_en_vigueur(bareme, a), 5)
                for a in range(premiere, derniere + 1)
                if _en_vigueur(bareme, a) > 0
            }
            print(f"OK      {regime:<24} taux d'appel, {len(appels[regime])} années")
        for regime, cotes in REPARTITION.items():
            salarie = _tranches(_lire(cotes["salarie"]))
            employeur = _tranches(_lire(cotes["employeur"]))
            premiere = min(int(cle[:4]) for t in salarie for cle in t)
            parts: dict[str, dict[str, float]] = {}
            for annee in range(premiere, derniere + 1):
                par_tranche = {}
                for i, (ts, te) in enumerate(zip(salarie, employeur)):
                    s_, e_ = _en_vigueur(ts, annee), _en_vigueur(te, annee)
                    if s_ + e_ > 0:
                        par_tranche[f"tranche_{i + 1}"] = round(s_ / (s_ + e_), 5)
                if par_tranche:
                    parts[str(annee)] = par_tranche
            repartition[regime] = parts
            print(f"OK      {regime:<24} répartition salarié/employeur")
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"ÉCHEC   complémentaires : {erreur}", file=sys.stderr)
        return 1

    # Cohérence interne de la transcription : effectif = contractuel × appel,
    # tranche par tranche. Un écart signalerait une erreur d'OpenFisca ou
    # une année où l'appel ne s'applique pas à toutes les tranches.
    ecarts = 0
    for regime in CONTRACTUELS:
        for variante, annuel in contractuels[regime].items():
            for annee, par_tranche in annuel.items():
                appel = appels[regime].get(annee, 1.0)
                effectif = variantes[regime].get(variante, {}).get(annee, {})
                for tranche, contractuel in par_tranche.items():
                    attendu = round(contractuel * appel, 5)
                    if abs(attendu - effectif.get(tranche, 0.0)) > 0.0001:
                        ecarts += 1
    print(f"{ecarts} écart(s) entre effectif et contractuel × appel")

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "source_complementaires": RACINE_COMPLEMENTAIRES,
            "recupere_le": date.today().isoformat(),
            "regime": "regime_general",
            "note": "taux au 1er janvier ; total = salarié + employeur, plafonné "
                    "et déplafonné. Les complémentaires portent leurs TAUX "
                    "EFFECTIFS, taux d'appel compris, tranche par tranche : "
                    "c'est la même grandeur que celle des fiches du dépôt.",
            "baremes": baremes,
            "serie": serie,
            "variante_retenue": VARIANTE_RETENUE,
            "complementaires": complementaires,
            "complementaires_variantes": variantes,
            "contractuels": contractuels,
            "taux_appel": appels,
            "part_salariale": repartition,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\n{len(serie)} années écrites dans {SORTIE} "
          f"({PREMIERE_ANNEE}-{derniere})")
    print(f"Taux total {PREMIERE_ANNEE} : {serie[str(PREMIERE_ANNEE)]['total']:.2%} ; "
          f"{derniere} : {serie[str(derniere)]['total']:.2%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
