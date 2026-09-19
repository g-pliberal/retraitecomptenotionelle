#!/usr/bin/env python3
"""Ce que la branche famille et l'assurance chômage versent à la retraite.

    python scripts/fetch/ccss_transferts_retraite.py

CE QU'ON VIENT CHERCHER
------------------------
Le poste « transferts d'organismes extérieurs » du compte du système de
retraite (``cor_comptes_retraite.py``) est un agrégat : la CNAF y paie les
droits liés aux enfants — les cotisations d'assurance vieillesse des parents au
foyer et les majorations de pension pour trois enfants —, l'Unédic y paie les
points de retraite complémentaire des chômeurs, et quelques transferts plus
petits s'y ajoutent. Le COR ne ventile cet agrégat que pour la dernière année
de chaque rapport, et seulement depuis 2023.

Le compte notionnel du dépôt SUPPRIME les droits que la CNAF finance (ni AVPF,
ni majorations) ; il ne peut pas compter la recette qui les finance comme
acquise. Pour la retirer, il faut la connaître année par année : c'est ce que
ce script va chercher.

OÙ, ET POURQUOI LÀ
-------------------
Dans les rapports à la Commission des comptes de la Sécurité sociale, que la
Direction de la Sécurité sociale publie deux fois par an et qui sont la source
que le COR consolide. Deux fiches y portent ce qu'on cherche, chacune du côté
de celui qui PAIE :

* la fiche de la CNAF, dont les « transferts versés » distinguent la « prise en
  charge de cotisations au titre de l'AVPF » et les « majorations pour
  enfants » ;
* les fiches des régimes complémentaires — Agirc-Arrco, et Agirc et Arrco
  séparément avant leur fusion de 2019 —, dont les transferts reçus portent une
  ligne « au titre du chômage par l'Unédic », et la fiche de l'Ircantec, qui
  porte la même ligne.

La somme des deux dernières redonne EXACTEMENT le « dont Unédic » que le COR
publie depuis 2023 — 3 346 millions en 2022, 3 730 en 2023, 3 949 en 2024 —,
ce qui dit que le périmètre est le bon. Le « dont CNAF » du COR, lui, s'écarte
de la somme des deux lignes de la CNAF de quelques pour cent, dans un sens ou
dans l'autre — 2,7 % en dessous en 2022, 4 % au-dessus en 2024 : il est
consolidé du côté des régimes qui REÇOIVENT, chacun avec son millésime et son
périmètre. C'est le producteur du paiement qu'on retient, et
``verifier_donnees.py`` confronte les deux.

CE QUE LE SCRIPT LIT, ET CE QU'IL NE LIT PAS
---------------------------------------------
Chaque rapport donne trois ou quatre années : les comptes arrêtés des deux
dernières, puis des prévisions marquées « (p) ». On ne retient d'un rapport que
les années ANTÉRIEURES à celle de sa parution — les comptes clos —, et quand
plusieurs rapports donnent la même année, c'est le PREMIER qui l'arrête qui
l'emporte : celui de l'année suivante, où le compte vient d'être clos. Les
rapports d'après ne reprennent cette année que pour mémoire, et parfois sur une
seule des deux lignes qu'on additionne — l'Agirc sans l'Arrco —, ce qui ferait
tomber 2014 de 3 092 à 653 millions si le plus récent l'emportait.
Les rapports de 2007 à 2012 sont chiffrés et ceux de 2004 à 2006 compressent
leurs objets ; le lecteur PDF du dépôt n'ouvre ni les uns ni les autres, et la
série commence donc en 2011, première année que le rapport de 2013 arrête.
``docs/limites.md`` §5 le dit.

Les tableaux se lisent par leur en-tête d'années. Une ligne d'en-tête alterne
années et colonnes « % » — « 2021 2022 % 2023(p) % 2024(p) % » — et la ligne
de valeurs qui suit un libellé porte autant de nombres qu'il y a de colonnes ;
les taux d'évolution, à une décimale, se distinguent des montants, en millions
sans décimale ou avec une décimale et toujours au-dessus de cinquante. Une
ligne dont le compte ne tombe pas juste est ignorée, jamais devinée.
"""

from __future__ import annotations

import json
import re
import ssl
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fetch.lecture_pdf import lignes_pdf  # noqa: E402

RACINE_SITE = "https://www.securite-sociale.fr"
PAGE_RAPPORTS = (
    RACINE_SITE + "/home/la-secu-en-detail/comptes-statistiques-et-etudes-de-la-"
    "s%c3%a9curit%c3%a9-sociale/rapports-a-la-commission-des-comptes-de-la-"
    "securite-sociale.html"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/ccss_transferts_retraite.json")
#: Les rapports pèsent de trois à huit mégaoctets chacun ; on les garde.
CACHE = Path("data/brut/ccss_rapports")

#: Liens vers les rapports, sur la page qui les liste. Le chemin porte l'année
#: dans un dossier — ``CCSS/2023/`` ou, une fois, ``DSS/2023/``.
LIEN_RAPPORT = re.compile(
    r'href="((?:https?://[^"/]+)?/files/live/sites/SSFR/files/medias/'
    r'(?:CCSS|DSS)/(\d{4})/[^"]+\.pdf)"'
)
#: Le rapport d'automne, qui arrête les comptes de l'année précédente ; à
#: défaut celui de printemps, qui les arrête aussi mais un rapport plus tôt.
AUTOMNE = re.compile(r"sept|oct|-09-|-10-", re.I)
PRINTEMPS = re.compile(r"juin|juil|mai|-0[5-7]-", re.I)
PREMIERE_ANNEE_LISIBLE = 2013

#: Les lignes cherchées. Le libellé est comparé sans espaces ni accents ni
#: casse, parce que le lecteur PDF colle les mots d'une même cellule. Les motifs
#: sont essayés dans l'ordre : le premier qui trouve une ligne au compte juste
#: l'emporte, sauf pour les lignes ADDITIVES, où toutes les lignes distinctes
#: s'ajoutent — l'Agirc et l'Arrco avaient chacune la leur avant 2019.
LIGNES: tuple[tuple[str, tuple[str, ...], bool], ...] = (
    ("cnaf_avpf", (
        r"^priseenchargedecotisationsautitredel'avpf$",
        r"^prisesenchargedescotisationsautitredel'avpf$",
        r"^prisesenchargedescotisationsavpf$",
    ), False),
    ("cnaf_majorations", (
        r"^majorationspourenfants$",
        r"^majorationspourenfantsacharge$",
    ), False),
    ("unedic_agirc_arrco", (
        r"^autitreduchomageparl'unedic$",
        r"^parl'unedic$",
    ), True),
    ("unedic_ircantec", (
        r"^autitreduchomage\(unedic\)$",
    ), False),
    # Le fonds de solidarité vieillesse paie deux choses, et les deux lignes
    # sont ADDITIVES : le fonds verse à plusieurs régimes, et chaque fiche
    # porte la sienne. Le libellé de la seconde s'est précisé en 2024 — « au
    # titre du minimum vieillesse » —, et les deux se voient nommer « (CNAV à
    # partir de 2026) » depuis que le fonds est promis à la suppression.
    ("fsv_cotisations", (
        r"^prisesenchargedecotisationsparlefsv(\(cnavapartirde\d{4}\))?$",
    ), True),
    ("fsv_prestations", (
        r"^prisesenchargedeprestationsparlefsv"
        r"(autitreduminimumvieillesse)?(\(cnavapartirde\d{4}\))?$",
    ), True),
)

#: Une ligne d'en-tête : des années, éventuellement marquées « (p) » ou « (t) »,
#: et des colonnes « % ». Deux années au moins, sinon c'est un numéro de page.
COLONNE = re.compile(r"20\d\d\s*\(?[pt]?\)?|%")
ENTETE = re.compile(r"^(?:\s*(?:20\d\d\s*\(?[pt]?\)?|%))+\s*$")
#: Les jetons d'une ligne de valeurs, en deux lectures. La première groupe les
#: milliers séparés par une espace — « 4 432 » —, la seconde non ; « 775 490 »
#: est un nombre dans la première et deux dans la seconde, et seul le compte
#: des colonnes de l'en-tête dit laquelle est la bonne.
JETONS_GROUPES = re.compile(
    r"\+\+|--|-(?![\d,])|-?\d{1,3}(?: \d{3})+(?:,\d+)?|-?\d+(?:,\d+)?"
)
JETONS_SEPARES = re.compile(r"\+\+|--|-(?![\d,])|-?\d+(?:,\d+)?")


def _plie(texte: str) -> str:
    plie = unicodedata.normalize("NFD", texte)
    plie = "".join(c for c in plie if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", "", plie).lower().replace("’", "'")


#: Le site de la Sécurité sociale présente une chaîne de certificats que le
#: niveau de sécurité par défaut d'OpenSSL refuse — la poignée de main échoue
#: avant tout échange. Le niveau 1 l'accepte, vérification du certificat
#: comprise : on ne désactive rien, on abaisse une exigence de longueur de clé.
def _contexte() -> ssl.SSLContext:
    contexte = ssl.create_default_context()
    contexte.set_ciphers("DEFAULT:@SECLEVEL=1")
    return contexte


def _recuperer(url: str) -> bytes:
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=300, context=_contexte()) as reponse:
        return reponse.read()


def rapports() -> dict[int, str]:
    """Un rapport par année, d'automne de préférence, lu sur la page qui les liste."""
    page = _recuperer(PAGE_RAPPORTS).decode("utf-8", "replace")
    par_annee: dict[int, list[str]] = {}
    for lien, annee in LIEN_RAPPORT.findall(page):
        if not lien.startswith("http"):
            lien = RACINE_SITE + lien
        par_annee.setdefault(int(annee), []).append(lien)
    choisis: dict[int, str] = {}
    for annee, liens in par_annee.items():
        if annee < PREMIERE_ANNEE_LISIBLE:
            continue
        noms = {lien: urllib.parse.unquote(lien.rsplit("/", 1)[-1]) for lien in liens}
        automne = [l for l in liens if AUTOMNE.search(noms[l])]
        printemps = [l for l in liens if PRINTEMPS.search(noms[l])]
        if automne:
            choisis[annee] = automne[0]
        elif printemps:
            choisis[annee] = printemps[0]
    if not choisis:
        raise LookupError("aucun rapport à la CCSS sur la page qui les liste")
    return dict(sorted(choisis.items()))


def _telecharger(annee: int, url: str) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    chemin = CACHE / f"{annee}.pdf"
    if chemin.exists() and chemin.stat().st_size > 100_000:
        return chemin.read_bytes()
    octets = _recuperer(url)
    if not octets.startswith(b"%PDF"):
        raise LookupError(f"{url} n'est pas un PDF")
    chemin.write_bytes(octets)
    return octets


def _colonnes(entete: str) -> list[tuple[int, bool] | None]:
    """Les colonnes d'un en-tête : une année et son marquage, ou ``None`` pour « % »."""
    colonnes: list[tuple[int, bool] | None] = []
    for jeton in COLONNE.findall(entete):
        if jeton == "%":
            colonnes.append(None)
        else:
            colonnes.append((int(jeton[:4]), bool(re.search(r"[pt]", jeton[4:]))))
    return colonnes


def _est_taux(jeton: str) -> bool:
    """Un taux d'évolution : « ++ », « -- », « - », ou un nombre à une décimale sous cinquante."""
    if jeton in ("++", "--", "-"):
        return True
    m = re.fullmatch(r"(-?\d+),(\d)", jeton.replace(" ", ""))
    return bool(m) and abs(float(m.group(1) + "." + m.group(2))) < 50.0


def _montant(jeton: str) -> float:
    return float(jeton.replace(" ", "").replace(",", "."))


#: Cellules vides d'un tableau : le rapport y met un tiret ou un double signe
#: quand la valeur n'existe pas ou que l'évolution n'a pas de sens. Elles ne
#: sont ni un montant ni un taux, et les compter pour l'un ou pour l'autre
#: faisait rejeter toute ligne qui en portait une.
CELLULES_VIDES = frozenset({"--", "++", "-"})


def _valeurs(ligne: str, libelle: str, colonnes: list) -> dict[int, float] | None:
    """Les montants d'une ligne, année par année, ou ``None`` si le compte n'y est pas.

    Le libellé est retiré, ce qui laisse des nombres des deux côtés : certains
    tableaux mettent les taux d'évolution AVANT le libellé et les montants
    après. On ne se fie donc pas à l'ordre des jetons pour distinguer les deux,
    mais à leur forme.

    DEUX TOLÉRANCES, ET CE QU'ELLES COÛTENT. Une cellule vide est SAUTÉE au
    lieu de faire rejeter la ligne. Et une ligne qui porte PLUS de montants que
    l'en-tête n'annonce d'années est lue sur son PRÉFIXE, parce que les
    tableaux des comptes de la CNAV portent depuis 2024 des colonnes « pro
    forma » qu'aucun en-tête ne déclare : les colonnes de gauche sont les
    années closes, celles de droite des variantes de périmètre de l'année en
    cours, et seules les premières sont retenues de toute façon. Sans ces deux
    tolérances, les prises en charge du fonds de solidarité vieillesse étaient
    illisibles une année sur deux. Avec elles, aucune des quatre séries déjà
    certifiées ne bouge d'un euro — c'est le contrôle qui a décidé de les
    poser.
    """
    reste = ligne.replace(libelle, " ")
    annees = [c for c in colonnes if c is not None]
    taux = sum(1 for c in colonnes if c is None)
    for lecture in (JETONS_GROUPES, JETONS_SEPARES):
        montants: list[float] = []
        evolutions = 0
        illisible = False
        for jeton in lecture.findall(reste):
            if jeton in CELLULES_VIDES:
                continue
            if _est_taux(jeton):
                evolutions += 1
            else:
                try:
                    montants.append(_montant(jeton))
                except ValueError:
                    illisible = True
                    break
        if illisible:
            continue
        # Le nombre de taux peut dépasser d'un le nombre de colonnes « % » :
        # la première année d'un tableau porte parfois le sien sans que
        # l'en-tête ne l'annonce. Il peut aussi en manquer un, quand la
        # dernière colonne est une cellule vide.
        if len(montants) >= len(annees) and evolutions >= taux - 1:
            return {
                annee: montant
                for (annee, _), montant in zip(annees, montants[:len(annees)])
            }
    return None


def _libelle(ligne: str) -> str:
    """Ce qui reste d'une ligne une fois les nombres retirés de ses deux bouts."""
    return re.sub(r"^[-\d,.+\s]+|[-\d,.+\s]+$", "", ligne)


def lire_rapport(annee_rapport: int, octets: bytes) -> dict[str, dict[int, float]]:
    """Les lignes cherchées d'un rapport, restreintes à ses comptes arrêtés."""
    lignes = lignes_pdf(octets)
    trouvees: dict[str, list[tuple[str, dict[int, float]]]] = {}
    colonnes: list | None = None
    for ligne in lignes:
        if ENTETE.match(ligne) and len(COLONNE.findall(ligne)) >= 2:
            candidates = _colonnes(ligne)
            if sum(1 for c in candidates if c is not None) >= 2:
                colonnes = candidates
            continue
        if colonnes is None:
            continue
        libelle = _libelle(ligne)
        plie = _plie(libelle)
        for cle, motifs, _ in LIGNES:
            for rang, motif in enumerate(motifs):
                if re.search(motif, plie):
                    valeurs = _valeurs(ligne, libelle, colonnes)
                    if valeurs:
                        trouvees.setdefault(cle, []).append((f"{rang}", valeurs))
    resultat: dict[str, dict[int, float]] = {}
    for cle, _, additive in LIGNES:
        lignes_cle = trouvees.get(cle, [])
        if not lignes_cle:
            continue
        # Les doublons — le même tableau repris dans la vue d'ensemble — sont
        # écartés sur l'égalité des valeurs.
        distinctes: list[tuple[str, dict[int, float]]] = []
        for rang, valeurs in lignes_cle:
            if all(valeurs != autre for _, autre in distinctes):
                distinctes.append((rang, valeurs))
        if additive:
            somme: dict[int, float] = {}
            for _, valeurs in distinctes:
                for annee, montant in valeurs.items():
                    somme[annee] = somme.get(annee, 0.0) + montant
            retenu = somme
        else:
            distinctes.sort(key=lambda paire: paire[0])
            retenu = distinctes[0][1]
        resultat[cle] = {
            annee: montant for annee, montant in retenu.items()
            if annee < annee_rapport
        }
    return resultat


def main() -> int:
    try:
        liens = rapports()
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"Site de la Sécurité sociale indisponible : {erreur}", file=sys.stderr)
        return 1
    except LookupError as erreur:
        print(f"Page des rapports illisible : {erreur}", file=sys.stderr)
        return 1

    series: dict[str, dict[str, float]] = {cle: {} for cle, _, _ in LIGNES}
    provenance: dict[str, dict[str, int]] = {cle: {} for cle, _, _ in LIGNES}
    lus: dict[str, str] = {}
    for annee_rapport, url in liens.items():
        try:
            octets = _telecharger(annee_rapport, url)
        except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
            print(f"Rapport {annee_rapport} non lu : {erreur}", file=sys.stderr)
            continue
        trouve = lire_rapport(annee_rapport, octets)
        lus[str(annee_rapport)] = url
        for cle, valeurs in trouve.items():
            for annee, montant in valeurs.items():
                # Le premier rapport qui arrête l'année l'emporte : les
                # rapports sont lus dans l'ordre des années.
                if str(annee) in series[cle]:
                    continue
                series[cle][str(annee)] = round(montant, 1)
                provenance[cle][str(annee)] = annee_rapport
        print(f"{annee_rapport} : " + ", ".join(
            f"{cle} {min(v)}-{max(v)}" for cle, v in sorted(trouve.items()) if v
        ) if trouve else f"{annee_rapport} : rien de lisible")

    charge = {
        "source": PAGE_RAPPORTS,
        "unite": "millions d'euros courants",
        "rapports": lus,
        "series": series,
        "provenance": provenance,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8",
    )
    print(f"{SORTIE} écrit depuis {len(lus)} rapports")
    for cle, valeurs in series.items():
        if valeurs:
            print(f"  {cle} : {min(valeurs)}-{max(valeurs)}, {len(valeurs)} années")
        else:
            print(f"  {cle} : rien")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
