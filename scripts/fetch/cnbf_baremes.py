#!/usr/bin/env python3
"""Récupération des valeurs du point des avocats, dans les barèmes de la CNBF.

    python scripts/fetch/cnbf_baremes.py

La Caisse nationale des barreaux français ne diffuse ni série ni API : elle
publie, chaque janvier, un **barème annuel en PDF**. C'est pourtant la seule
source qui existe — ni OpenFisca, ni les barèmes IPP, ni la base LEGI ne portent
la valeur du point des avocats, et deux dépouillements complets de la
législation consolidée l'ont confirmé (voir docs/limites.md §1).

Chaque barème donne les deux grandeurs qu'il faut :

* le **coût d'acquisition du point** — ce qu'un point coûte dans l'année ;
* la **valeur de service du point** — ce qu'il rapporte, en rente annuelle.

Leur rapport est le rendement instantané du régime complémentaire : 10,1 % en
2017, 8,2 % en 2026. La décrue est régulière, et c'est ce qui permet de
contrôler l'extraction.

Pourquoi ce garde-fou. Lire un PDF, c'est reconstituer une mise en page : si
elle change, on peut prendre un nombre pour un autre sans que rien ne le
signale. Le script refuse donc d'écrire une série qui ne serait pas strictement
croissante sur les deux grandeurs, ni décroissante en rendement. Une année
manquante est tolérée — la CNBF ne met pas tous ses barèmes en ligne — mais une
valeur aberrante arrête tout.

Ces valeurs concernent le **régime complémentaire** des avocats, pas leur régime
de base, qui est forfaitaire. Elles sont donc versées sous le code
``cnbf_complementaire`` — et **le moteur s'en sert**, depuis que la fiche a été
scindée en ses deux étages : une base forfaitaire de 19 154 € par an au taux
plein, indépendante du revenu, et un complémentaire en points.

Le barème porte tout ce qu'il fallait pour cette scission, et deux décisions
seules la retardaient. Elles sont tranchées, et écrites dans la fiche :

* **classe C1** — trois classes coexistent (C1, C2, C2+) et rien ne permet de
  deviner celle d'un avocat donné. C1 est celle qui s'applique SANS option, et
  le modèle ne prête jamais à personne un avantage facultatif ;
* **tranches en euros** — la caisse les fixe en euros et ne les indexe pas :
  42 507 € en 2023, en 2025 et en 2026, quand le plafond de la Sécurité sociale
  passait de 43 992 à 48 060 €. Les exprimer en plafonds, comme le fait le reste
  du catalogue, les ferait dériver. C'est ce constat, et non un arbitrage, qui a
  levé l'obstacle : il fallait un champ de bornes en euros, il existe désormais.

Les TAUX de cotisation des mêmes barèmes — grille C1 du complémentaire, taux
proportionnel et cotisation forfaitaire de la base — ne sont pas extraits par
ce script : leur mise en page change d'une année à l'autre, et ils sont
transcrits à la main dans les fiches `cnbf` et `cnbf_complementaire`.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import lignes_pdf  # noqa: E402
from source_locale import lire_ou_telecharger  # noqa: E402

RACINE = "https://www.cnbf.fr/wp-content/uploads"

#: Les barèmes mis en ligne par la CNBF, année par année. La caisse les range
#: par date de dépôt et non par millésime, et ne les publie pas tous : 2016 est
#: une image, sans texte à extraire.
#:
#: 2024 N'EST PLUS EN LIGNE, mais il l'a été : la caisse l'a retiré en
#: remaniant son site, et Internet Archive l'a gardé, capturé le 15 juillet
#: 2024 à son adresse d'origine. Une adresse complète est lue telle quelle ;
#: le suffixe ``id_`` demande à l'archive le fichier brut, sans son bandeau.
BAREMES = {
    2017: "2024/11/Bareme-cotisations-et-prestations-2017.pdf",
    2018: "2024/11/Bareme-des-cotisations-et-prestations-2018.pdf",
    2019: "2024/11/Bareme-CNBF-2019.pdf",
    2020: "2024/11/Bareme-CNBF-2020-Revise.pdf",
    2021: "2024/11/Bareme-CNBF-2021.pdf",
    2022: "2024/11/Bareme-CNBF-2022-7.pdf",
    2023: "2024/11/Bareme-CNBF-2023-01.10.pdf",
    2024: "https://web.archive.org/web/20240715164610id_/"
          "https://www.cnbf.fr/wp-content/uploads/2023/09/Bareme-CNBF-2024-01.20.pdf",
    2025: "2025/02/Bareme-CNBF-2025-01.01_vDf-1.pdf",
    2026: "2026/01/Bareme-CNBF-2026.01.01.pdf",
}

ACHAT = re.compile(r"[Cc]o[ûu]td'acquisitiondupoint=?(\d+[,.]\d+)")
SERVICE = re.compile(r"multipli[ée]par(?:de)?(\d+[,.]\d+)")
SORTIE = Path("data/brut/cnbf_baremes.json")


#: Réparation d'une table ``/ToUnicode`` fautive.
#:
#: Les barèmes de 2017 à 2025 écrivent leurs CHIFFRES dans une police dont la
#: table ToUnicode les déclare caractères grecs : « 11,1654 € » y est encodé
#: ``ϭϭ͕ϭϲϱϰΦ``. Le glyphe affiché est bien un chiffre — la caisse publie
#: un barème lisible — mais le texte extrait ne l'est pas, et les expressions
#: régulières ne trouvaient plus rien : les huit barèmes antérieurs à 2026
#: étaient silencieusement ignorés, la série tombant de dix-huit valeurs à deux.
#:
#: Les dix chiffres sont contigus à partir de U+03EC, ce qui est la signature
#: d'une police dont les glyphes ont été renumérotés à l'export. On ne devine
#: pas cette table : on la CONTRÔLE. Le barème 2023 ainsi décodé donne 11,1654 €
#: et 0,9815 €, valeurs déjà certifiées lorsque la caisse servait ces PDF dans
#: une police saine, et le garde-fou de `verifier` refuse toute série qui ne
#: serait pas monotone. Deux lectures indépendantes du même document, même
#: résultat.
REPARATION = {chr(0x03EC + chiffre): str(chiffre) for chiffre in range(10)}
REPARATION.update({"\u0355": ",", "\u0358": ".", "\u03a6": "€"})


def _normaliser(lignes: list[str]) -> str:
    """Colle le texte extrait, en ôtant les artefacts de mise en page.

    Les barèmes anciens intercalent un ``x-none`` entre chaque cellule, les
    récents suppriment les espaces : on supprime les deux pour retrouver une
    chaîne comparable d'une année à l'autre. Les chiffres mal encodés sont
    remis d'aplomb au passage — voir `REPARATION`.
    """
    texte = "\n".join(lignes).replace("x-none", " ")
    texte = texte.replace(" ", " ").replace(" ", " ")
    texte = texte.translate(str.maketrans(REPARATION))
    return re.sub(r"\s+", "", texte)


def _adresse(chemin: str) -> str:
    """L'adresse d'un barème : sous ``RACINE``, ou telle quelle si complète."""
    return chemin if chemin.startswith("https://") else f"{RACINE}/{chemin}"


def _nombre(texte: str) -> float:
    return float(texte.replace(",", "."))


def extraire(octets: bytes) -> tuple[float, float] | None:
    """Renvoie (coût d'acquisition, valeur de service) ou ``None``."""
    texte = _normaliser(lignes_pdf(octets))
    achat, service = ACHAT.search(texte), SERVICE.search(texte)
    if not achat or not service:
        return None
    return _nombre(achat.group(1)), _nombre(service.group(1))


def verifier(serie: dict[int, tuple[float, float]]) -> list[str]:
    """Contrôle de structure : sans lui, une erreur de lecture passerait."""
    anomalies = []
    annees = sorted(serie)
    for precedente, courante in zip(annees, annees[1:]):
        avant, apres = serie[precedente], serie[courante]
        if apres[0] <= avant[0]:
            anomalies.append(
                f"coût d'acquisition non croissant : {precedente} {avant[0]} "
                f"-> {courante} {apres[0]}"
            )
        if apres[1] <= avant[1]:
            anomalies.append(
                f"valeur de service non croissante : {precedente} {avant[1]} "
                f"-> {courante} {apres[1]}"
            )
        if apres[1] / apres[0] >= avant[1] / avant[0]:
            anomalies.append(
                f"rendement non décroissant : {precedente} {avant[1] / avant[0]:.2%} "
                f"-> {courante} {apres[1] / apres[0]:.2%}"
            )
    return anomalies


def _telecharger(url: str) -> bytes:
    demande = urllib.request.Request(
        url, headers={"User-Agent": "retraite-notionnelle/0.1"}
    )
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return reponse.read()


def main() -> int:
    serie: dict[int, tuple[float, float]] = {}
    for annee, chemin in sorted(BAREMES.items()):
        url = _adresse(chemin)
        try:
            octets = lire_ou_telecharger(url, _telecharger)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
            print(f"ÉCHEC   barème {annee} : {erreur}", file=sys.stderr)
            return 1
        valeurs = extraire(octets)
        if valeurs is None:
            print(f"IGNORÉ  barème {annee} : les deux valeurs n'ont pas été trouvées")
            continue
        serie[annee] = valeurs
        print(f"OK      {annee} : achat {valeurs[0]} €, service {valeurs[1]} €, "
              f"rendement {valeurs[1] / valeurs[0]:.2%}")

    anomalies = verifier(serie)
    if anomalies:
        print("\nSérie incohérente, rien n'est écrit :", file=sys.stderr)
        for anomalie in anomalies:
            print(f"  {anomalie}", file=sys.stderr)
        return 1

    plat = {}
    for annee, (achat, service) in sorted(serie.items()):
        plat[f"cnbf_complementaire|{annee}|salaire_reference"] = achat
        plat[f"cnbf_complementaire|{annee}|valeur_service"] = service

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "recupere_le": date.today().isoformat(),
            "baremes": {str(a): _adresse(c) for a, c in sorted(BAREMES.items())},
            "note": "régime complémentaire des avocats ; le régime de base est "
                    "forfaitaire et n'a pas de point",
            "serie": plat,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    annees = sorted(serie)
    print(f"\n{len(plat)} valeurs écrites dans {SORTIE}")
    print(f"Couverture {annees[0]}-{annees[-1]}, {len(annees)} barèmes lus")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
