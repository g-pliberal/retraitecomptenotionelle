#!/usr/bin/env python3
"""Les projets annuels de performances du PLF 2026, lus : ce que l'État finance.

    python scripts/fetch/pap_plf_2026.py                # lit les deux PAP, écrit data/brut/pap_plf_2026.json
    python scripts/fetch/pap_plf_2026.py --confronter   # compare à pap_regimes_subventionnes.csv, ligne à ligne
    python scripts/verifier_donnees.py --appliquer      # verse les valeurs lues au niveau haute

Deux documents, déposés au Parlement avec le projet de loi de finances et
servis par l'Assemblée nationale (``budget.gouv.fr`` refuse la session) :

* la mission « Régimes sociaux et de retraite » (programmes 195, 197, 198) :
  les régimes que l'État équilibre — SNCF, RATP, marins, mines, SEITA, Opéra,
  Comédie-Française, gérants de débits de tabac ;
* le compte d'affectation spéciale « Pensions » (programme 741) : les
  pensions civiles et militaires de l'État.

``data/reference/regimes/pap_regimes_subventionnes.csv`` en porte 294 valeurs,
SAISIES à la lecture de leur page imprimée. Ce script relit les mêmes
documents et rend ce qu'il sait lire, en trois familles :

1. **Les séries annuelles du programme 198**, 2012-2023, par leur ligne
   d'années : subvention et pensions servies, cotisations reçues, ratio
   démographique, années validées et cotisées du flux de la SNCF, trimestres
   cotisés et validés du flux de la RATP, durées d'activité et de service du
   stock. Le tableau est écrit sur trois lignes — un mot du libellé, les douze
   valeurs, la suite du libellé — et les milliers sont séparés d'espaces
   ordinaires : « 3 307 3 334 » ne se découpe qu'en sachant qu'il y a douze
   colonnes. Les âges moyens de départ, écrits « 55 ans et 8 mois » sur trois
   lignes enchevêtrées, ne sont pas lus : ils restent saisis.
2. **Les crédits 2026 par action**, dans la ligne « Hors titre 2 » de chaque
   action, en crédits de paiement, ramenés au dixième de million.
3. **Les points en prose** — cotisants, pensionnés, pensions moyennes,
   dépenses, âges, espérances de vie — et les petits tableaux du programme
   741, par des motifs écrits pour cette édition. Les motifs se comparent au
   texte SANS AUCUNE ESPACE : le PDF en glisse au milieu des mots (« direc t »,
   « prévisi on »), le compte d'affectation spéciale a perdu ses apostrophes
   et son signe euro dans sa table de police, et c'est le seul moyen de ne
   dépendre ni des unes ni des autres. Le document est figé par son empreinte
   dans ``data/sources.yaml`` : un motif qui cesserait de trouver dirait
   qu'on ne lit plus le même fichier, et c'est ce qu'on veut savoir.

**NIVEAU ``haute``, PAS ``certifiee``.** Le producteur de ces chiffres est la
caisse — CPR PF, CRP RATP, ENIM, CANSSM… — et le PAP les transcrit. La règle du
manifeste plafonne à ``haute`` une transcription tierce, fût-elle lue par un
script : c'est ce que ``verifier_donnees.py`` appose aux lignes que ce script
retrouve, et les autres gardent ``moyenne``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import lignes_pdf  # noqa: E402
from source_locale import (  # noqa: E402
    RACINE, jeux_bloques, lire_ou_telecharger, option_fichier, telecharger,
)

MISSION = "db_pap_regimes_sociaux"
CAS = "db_cas_pensions"
SORTIE = RACINE / "data" / "brut" / "pap_plf_2026.json"
CIBLE = RACINE / "data" / "reference" / "regimes" / "pap_regimes_subventionnes.csv"

#: Les séries du programme 198, reconnues sur leur libellé sans accents.
SERIES_198 = (
    ("subvention", "subvention_meur"),
    ("pensions servies", "pensions_servies_meur"),
    ("cotisations recues", "cotisations_recues_meur"),
    ("ratio demographique", "ratio_demographique"),
    ("annees validees", "annees_validees_flux"),
    ("annees cotisees", "annees_cotisees_flux"),
    ("duree moyenne d'activit", "duree_activite_stock"),
    ("duree moyenne de service", "duree_service_pension_stock"),
    ("trimestres cotises", "trimestres_cotises_flux"),
    ("trimestres valides", "trimestres_valides_flux"),
)
#: Les actions dont la ligne « Hors titre 2 » porte les crédits 2026 du régime.
ACTIONS = (
    ("regime de retraite du personnel de la sncf", "sncf"),
    ("regime de retraite du personnel de la ratp", "ratp"),
    ("regimes de retraite et de securite sociale des marins", "enim"),
    ("regime de retraite de la seita", "seita"),
    ("caisse de retraites du personnel de la comedie francaise", "comedie_francaise"),
    ("caisse de retraites des personnels de l'opera national de paris", "opera_de_paris"),
    ("regime d'allocations viageres des gerants de debit de tabac", "gerants_debits_tabac"),
)

#: Un nombre dans le texte compacté : les milliers y sont déjà collés.
N = r"(\d+(?:[.,]\d+)?)"
#: « 64 ans et 2 mois », compacté.
AGE = r"(\d+anset\d+mois)"

#: Les points en prose de la mission : (regime, poste, annee, motif). Le motif
#: est écrit avec ses espaces pour rester lisible ; il est compacté avant
#: d'être cherché, comme le texte. L'apostrophe est facultative.
POINTS_MISSION = (
    ("sncf", "cotisants", 2023, rf"compte {N} cotisants pour {N} pensionnes en 2023"),
    ("sncf", "pensionnes", 2023, rf"compte \d+ cotisants pour {N} pensionnes en 2023"),
    ("ratp", "cotisants", 2023, rf"comptait {N} cotisants pour pres de {N} pensionnes"),
    ("ratp", "pensionnes", 2023, rf"comptait \d+ cotisants pour pres de {N} pensionnes"),
    ("enim", "cotisants", 2024, rf"\({N} actifs cotisants en 2024 pour {N} pensionnes et {N} pensions"),
    ("enim", "pensionnes", 2024, rf"\(\d+ actifs cotisants en 2024 pour {N} pensionnes et"),
    ("enim", "pensions_en_paiement", 2024, rf"\(\d+ actifs cotisants en 2024 pour \d+ pensionnes et {N} pensions"),
    ("enim", "ratio_demographique", 2024, rf"avec un ratio de {N} entre le"),
    ("enim", "pension_moyenne_droit_direct_eur", 2025, rf"pension de droit direct de {N} €, contre {N} € pour 2024"),
    ("enim", "pension_moyenne_droit_direct_eur", 2024, rf"pension de droit direct de \d+ €, contre {N} € pour 2024"),
    ("enim", "pension_moyenne_reversion_eur", 2025, rf"pensions de reversion, les montants sont respectivement de {N} € en 2025 et {N} € en 2024"),
    ("enim", "pension_moyenne_reversion_eur", 2024, rf"pensions de reversion, les montants sont respectivement de \d+ € en 2025 et {N} € en 2024"),
    ("enim", "subvention_meur", 2026, rf"prestations legales vieillesse \({N} m€ en ae et cp\)"),
    ("enim", "pensions_servies_meur", 2026, rf"pensions qui devraient s'elever a {N} m€ en 2026"),
    ("enim", "depenses_branche_vieillesse_meur", 2026, rf"incluant les provisions\) de {N} m€ en 2026"),
    ("enim", "depenses_branche_vieillesse_meur", 2025, rf"prevision d'atterrissage 2025 de {N} m€"),
    ("enim", "depenses_branche_vieillesse_meur", 2024, rf"executions a {N} m€ en 2024"),
    ("enim", "depenses_branche_vieillesse_meur", 2023, rf"executions a [\d,.]+ m€ en 2024, {N} m€ en 2023"),
    ("enim", "depenses_branche_vieillesse_meur", 2022, rf"m€ en 2023, et {N} m€ en 2022\)"),
    ("canssm", "pensionnes", 2025, rf"exercice 2025, le regime devrait compter en moyenne pres de {N} pensionnes"),
    ("canssm", "pensionnes_droit_direct", 2025, rf"dont quasiment {N} de droit direct pour seulement {N} cotisants"),
    ("canssm", "cotisants", 2025, rf"dont quasiment \d+ de droit direct pour seulement {N} cotisants"),
    ("canssm", "pension_moyenne_droit_direct_eur", 2025, rf"s'elever a environ {N} € par an tandis que"),
    ("canssm", "pension_moyenne_droit_derive_eur", 2025, rf"droits derives ne devrait pas depasser {N} € par an"),
    ("canssm", "age_moyen_beneficiaires", 2024, rf"pension de retraite s'eleve a {N} ans, contre {N} ans en 2023"),
    ("canssm", "age_moyen_beneficiaires", 2023, rf"pension de retraite s'eleve a [\d,.]+ ans, contre {N} ans en 2023"),
    ("canssm", "engagements_actualises_mdeur", 2024, rf"canssm est estimee a {N} milliards d'euros au 31 decembre 2024"),
    ("seita", "pensionnes", 2024, rf"seita comptait {N} pensionnes pour, desormais, plus aucun actif"),
    ("seita", "besoin_de_financement_meur", 2025, rf"besoin de financement du regime s'elevera a environ {N} m€ en 2025"),
    ("comedie_francaise", "pensionnes", 2023, rf"le regime comptait {N} pensionnes \(-[\d,.]+ % par rapport a 2022\) et {N} cotisants"),
    ("comedie_francaise", "cotisants", 2023, rf"le regime comptait \d+ pensionnes \(-[\d,.]+ % par rapport a 2022\) et {N} cotisants"),
    ("comedie_francaise", "ratio_demographique", 2023, rf"cotisants \(\+[\d,.]+ % par rapport a 2022\), soit un ratio demographique cotisants/retraites de {N}"),
    ("comedie_francaise", "cotisations_recues_meur", 2023, rf"faveur de la crcf et represente {N} m€ en 2023 contre {N} m€ en 2022"),
    ("comedie_francaise", "cotisations_recues_meur", 2022, rf"faveur de la crcf et represente [\d,.]+ m€ en 2023 contre {N} m€ en 2022"),
    ("opera_de_paris", "cotisants", 2024, rf"le regime comptait {N} cotisants \(\+[\d,.]+ % par rapport a 2023\) et {N} pensionnes"),
    ("opera_de_paris", "pensionnes", 2024, rf"le regime comptait \d+ cotisants \(\+[\d,.]+ % par rapport a 2023\) et {N} pensionnes"),
    ("opera_de_paris", "ratio_demographique", 2024, rf"pensionnes \(\+[\d,.]+ % par rapport a 2023\), soit un ratio demographique cotisants/retraites de {N}"),
    ("opera_de_paris", "cotisations_recues_meur", 2023, rf"cotisations salariales et patronales, representant {N} m€ en 2023"),
    ("opera_de_paris", "cotisations_recues_meur", 2022, rf"cotisations salariees\), contre {N} m€ en 2022"),
    ("opera_de_paris", "subvention_meur", 2023, rf"porte a {N} m€ la subvention de fonctionnement en 2023"),
    ("gerants_debits_tabac", "cotisants", 2022, rf"en 2022, le regime comptait {N} cotisants et {N} pensionnes"),
    ("gerants_debits_tabac", "pensionnes", 2022, rf"en 2022, le regime comptait \d+ cotisants et {N} pensionnes"),
    ("gerants_debits_tabac", "ratio_demographique", 2022, rf"pensionnes, soit un ratio demographique cotisants/retraites de {N}\."),
    ("gerants_debits_tabac", "fiscalite_affectee_meur", 2024, rf"cette part de fiscalite representait {N} m€ en"),
)

#: Les points du compte d'affectation spéciale Pensions (programme 741). Le
#: signe euro n'y survit pas à la police : « m€ » s'y lit « m ».
POINTS_CAS = (
    ("fonction_publique_etat", "age_moyen_depart_sedentaires", 2024, rf"pour s'etablir a {AGE} en 2024"),
    ("fonction_publique_etat", "age_moyen_depart_militaires", 2023, rf"droits a la retraite en moyenne a {AGE}"),
    ("fonction_publique_etat", "esperance_vie_65_civils_femmes", 2024, rf"cet indicateur s'etablit a {N} ans pour les femmes et {N} ans pour les hommes"),
    ("fonction_publique_etat", "esperance_vie_65_civils_hommes", 2024, rf"cet indicateur s'etablit a [\d,.]+ ans pour les femmes et {N} ans pour les hommes"),
    ("fonction_publique_etat", "duree_retraite_civils_femmes", 2024, rf"en moyenne en 2024, {N} ans pour les femmes et {N} ans pour les hommes"),
    ("fonction_publique_etat", "duree_retraite_civils_hommes", 2024, rf"en moyenne en 2024, [\d,.]+ ans pour les femmes et {N} ans pour les hommes"),
    ("fonction_publique_etat", "pension_mensuelle_nouveaux_sedentaires_eur", 2023, rf"il passe en moyenne de {N} €? ?a {N} €?, confirmant"),
    ("fonction_publique_etat", "pension_mensuelle_nouveaux_sedentaires_eur", 2024, rf"il passe en moyenne de \d+ €? ?a {N} €?, confirmant"),
    ("fonction_publique_etat", "nouvelles_pensions_civiles_droit_direct", 2024, rf"s'etablissant a {N} nouvelles pensions en 2024"),
    ("fonction_publique_etat", "departs_anticipes_civils", 2024, rf"s'etablir a {N}\. ils representent moins d'un tiers des departs"),
    ("fonction_publique_etat", "engagements_actualises_mdeur", 2024, rf"a {N} milliards d'euros\. ce niveau est tres sensible"),
    ("fonction_publique_etat", "retraite_progressive_meur", 2024, rf"la depense de retraite progressive en 2024 est de {N} m€?\."),
    ("fonction_publique_etat", "retraite_progressive_meur", 2025, rf"retraite progressive est estimee a {N} m€? en 2025 et {N} m€? en 2026"),
    ("fonction_publique_etat", "retraite_progressive_meur", 2026, rf"retraite progressive est estimee a \d+ m€? en 2025 et {N} m€? en 2026"),
    ("fonction_publique_etat", "ressortissants", 2024, rf"pensionnes et affilies cotisants: {N} millions"),
)
#: Les petits tableaux du programme 741 : l'en-tête compacté qui les ouvre,
#: la ligne qui porte les valeurs, le nombre de colonnes et la première année.
TABLEAUX_CAS = (
    ("nouvelles_pensions_civiles_droit_direct", "civils2025202620272028", "", 4, 2025),
    ("nouvelles_pensions_militaires_droit_direct", "militaires2025202620272028", "", 4, 2025),
    ("depenses_pensions_civiles_meur", "civils,enm", "depenses n", 5, 2024),
    ("depenses_pensions_militaires_meur", "militaires,enm", "depenses n", 5, 2024),
)


# -- outils --------------------------------------------------------------------

def plat(texte: str) -> str:
    """Sans accents, en minuscules, une seule espace, l'apostrophe droite —
    pour reconnaître le document sans souffrir de sa police, dont la table
    Unicode n'a pas toutes les lettres."""
    # Le compte d'affectation spéciale écrit ses apostrophes, ses tirets et
    # son signe euro en codes Windows-1252 (0x80-0x9F) que sa police ne
    # traduit pas : on les lit comme tels avant d'ôter les accents.
    texte = "".join(
        bytes([ord(c)]).decode("cp1252", errors="replace") if 0x80 <= ord(c) <= 0x9F else c
        for c in texte
    )
    texte = unicodedata.normalize("NFD", texte)
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    texte = texte.replace("’", "'").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", texte).strip().lower()


def compact(texte: str) -> str:
    return plat(texte).replace(" ", "")


def motif_compact(motif: str) -> re.Pattern:
    """Le motif sans ses espaces, l'apostrophe facultative."""
    return re.compile(motif.replace(" ", "").replace("'", "'?"))


def nombre(texte: str) -> float:
    """« 3 307 » → 3307 ; « 1 041,7 » → 1041.7 ; « 0.63 » → 0.63."""
    return float(texte.replace(" ", "").replace(" ", "").replace(",", "."))


def annees_decimales(texte: str) -> float:
    """« 64anset2mois » → 64.17, comme le CSV l'écrit."""
    m = re.fullmatch(r"(\d+)anset(\d+)mois", texte)
    if not m:
        raise ValueError(texte)
    return round(int(m.group(1)) + int(m.group(2)) / 12, 2)


def decouper(jetons: list[str], attendu: int) -> list[float] | None:
    """``attendu`` nombres dans une suite de groupes de chiffres où les
    milliers sont séparés d'espaces ordinaires : « 3 307 3 334 » est 3307
    puis 3334.

    Un groupe qui porte une virgule ou un point est un nombre à lui seul ; un
    groupe d'un ou deux chiffres est la tête d'un nombre et prend tous les
    groupes de trois chiffres qui le suivent ; un groupe de trois chiffres est
    un nombre. Rend ``None`` si le compte n'y est pas : la ligne n'était pas
    une ligne de valeurs, ou le tableau a une autre forme.
    """
    valeurs: list[float] = []
    i = 0
    while i < len(jetons):
        jeton = jetons[i]
        if not re.fullmatch(r"-?\d+(?:[.,]\d+)?", jeton):
            return None
        if "," in jeton or "." in jeton or len(jeton.lstrip("-")) >= 3:
            valeurs.append(nombre(jeton))
            i += 1
            continue
        entier = jeton
        i += 1
        # Le dernier groupe peut porter la décimale : « 1 041,7 ».
        while i < len(jetons) and re.fullmatch(r"\d{3}(?:[.,]\d+)?", jetons[i]):
            entier += jetons[i]
            i += 1
            if "," in entier or "." in entier:
                break
        valeurs.append(nombre(entier))
    return valeurs if len(valeurs) == attendu else None


def ligne_de_valeurs(ligne: str, attendu: int) -> tuple[str, list[float]] | None:
    """Une ligne dont la fin est ``attendu`` nombres : (libellé en tête, valeurs)."""
    jetons = ligne.replace(" ", " ").split()
    for debut in range(len(jetons)):
        if not re.fullmatch(r"-?\d+(?:[.,]\d+)?", jetons[debut]):
            continue
        valeurs = decouper(jetons[debut:], attendu)
        if valeurs is not None:
            return " ".join(jetons[:debut]), valeurs
    return None


# -- lecture -------------------------------------------------------------------

def series_198(lignes: list[str]) -> dict[tuple[int, str, str], float]:
    """Les séries 2012-2023 de la SNCF et de la RATP, par leur ligne d'années."""
    lu: dict[tuple[int, str, str], float] = {}
    regime: str | None = None
    annees: list[int] = []
    avant: list[str] = []       # les mots de libellé lus depuis la dernière ligne de valeurs
    dernier: tuple[str, list[float]] | None = None
    for ligne in lignes:
        p = plat(ligne)
        if re.match(r"03 [–-] regime de retraite du personnel de la sncf", p):
            regime = "sncf"
        elif re.match(r"04 [–-] regime de retraite du personnel de la ratp", p):
            regime = "ratp"
        elif re.match(r"05 [–-] ", p):
            regime = None
        if regime is None:
            continue
        m = re.fullmatch(r"annee((?: \d{4})+)", p)
        if m:
            annees = [int(a) for a in m.group(1).split()]
            avant, dernier = [], None
            continue
        if not annees:
            continue
        lu_ligne = ligne_de_valeurs(ligne, len(annees))
        if lu_ligne is None:
            # Un mot de libellé : à la ligne de valeurs précédente s'il est en
            # minuscule ou porte un appel « (a) », à la suivante sinon. Une
            # phrase — « Les années validées comprennent… », « En millions
            # d'euros. » — n'est un libellé de rien.
            mot = p
            if not mot or mot.startswith(("les ", "en annees", "en millions", "*en", "donnees",
                                          "financement", "la ", "le ", "des ", "cette ", "ces ")):
                continue
            if dernier is not None and (ligne.strip()[:1].islower() or re.search(r"\([ab]\)", mot)):
                dernier = (dernier[0] + " " + mot, dernier[1])
                _ranger(lu, regime, annees, dernier)
            else:
                avant.append(mot)
            continue
        libelle, valeurs = lu_ligne
        dernier = (" ".join(avant + [libelle]), valeurs)
        avant = []
        _ranger(lu, regime, annees, dernier)
    return lu


def _ranger(lu: dict, regime: str, annees: list[int], bloc: tuple[str, list[float]]) -> None:
    libelle, valeurs = bloc
    libelle = re.sub(r"\s+", " ", libelle).strip()
    # Le libellé grandit à mesure que ses mots arrivent : « Subvention » seul
    # est déjà `subvention_meur`, « Subvention versée (a) » aussi ; « Durée
    # moyenne » seul ne désigne rien, et devient `duree_activite_stock` ou
    # `duree_service_pension_stock` quand la suite du libellé arrive.
    for motif, poste in SERIES_198:
        if motif in libelle:
            for annee, valeur in zip(annees, valeurs, strict=True):
                lu[(annee, regime, poste)] = valeur
            return


def credits_actions(lignes: list[str]) -> dict[tuple[int, str, str], float]:
    """Les crédits de paiement 2026 de chaque action, au dixième de million."""
    lu: dict[tuple[int, str, str], float] = {}
    regime: str | None = None
    for ligne in lignes:
        p = plat(ligne)
        for motif, code in ACTIONS:
            if re.match(rf"0\d [–-] {re.escape(motif)}\b", p) and not re.search(r"\d{3} \d{3}", p):
                regime = code
        if regime and p.startswith("hors titre 2 "):
            # Autorisations d'engagement, puis crédits de paiement, puis les
            # deux colonnes de fonds de concours. Les AE et les CP sont égaux
            # sur ces actions : la répétition (\1) est ce qui fixe la coupure
            # entre deux nombres de neuf chiffres que rien d'autre ne sépare.
            m = re.fullmatch(r"hors titre 2 (\d{1,3}(?: \d{3})*) \1 \d+ \d+", p)
            if m:
                lu[(2026, regime, "credits_etat_meur")] = round(nombre(m.group(1)) / 1e6, 1)
            regime = None
    return lu


def credits_mines(lignes: list[str]) -> dict[tuple[int, str, str], float]:
    """Les crédits 2026 de la CANSSM : la part « caisse autonome nationale de
    sécurité sociale [dans les mines] » de l'action 01 du programme 195, que
    le tableau des crédits par action écrit sur sa seconde ligne."""
    for ligne in lignes:
        m = re.match(r"caisse autonome nationale de securite sociale( dans les mines)? (\d{3} \d{3} \d{3})",
                     plat(ligne))
        if m:
            return {(2026, "canssm", "credits_etat_meur"): round(nombre(m.group(2)) / 1e6, 1)}
    return {}


def points(texte_compact: str, motifs) -> dict[tuple[int, str, str], float]:
    lu: dict[tuple[int, str, str], float] = {}
    for regime, poste, annee, motif in motifs:
        m = motif_compact(motif).search(texte_compact)
        if not m:
            continue
        brut = m.group(1)
        lu[(annee, regime, poste)] = annees_decimales(brut) if "anset" in brut else nombre(brut)
    return lu


def seita_sans_actif(texte_compact: str) -> dict[tuple[int, str, str], float]:
    """« plus aucun actif » : zéro cotisant, que le document écrit en toutes lettres."""
    if re.search(r"seitacomptait\d+pensionnespour,desormais,plusaucunactif", texte_compact):
        return {(2024, "seita", "cotisants"): 0.0}
    return {}


def tableaux_cas(lignes: list[str]) -> dict[tuple[int, str, str], float]:
    """Les petits tableaux du programme 741 : sous l'en-tête, la première ligne
    de valeurs qui porte le libellé attendu (vide pour les entrées de pensions,
    « Dépenses N » pour les dépenses)."""
    lu: dict[tuple[int, str, str], float] = {}
    compacts = [compact(ligne) for ligne in lignes]
    for poste, entete, libelle, colonnes, premiere in TABLEAUX_CAS:
        for i, c in enumerate(compacts):
            if not c.startswith(entete):
                continue
            for suite in lignes[i + 1:i + 40]:
                lu_ligne = ligne_de_valeurs(suite, colonnes)
                if lu_ligne and plat(lu_ligne[0]) == libelle:
                    for k, valeur in enumerate(lu_ligne[1]):
                        lu[(premiere + k, "fonction_publique_etat", poste)] = valeur
                    break
            break
    return lu


def lire(mission: bytes, cas: bytes) -> dict[tuple[int, str, str], float]:
    lignes_mission = lignes_pdf(mission)
    lignes_cas = lignes_pdf(cas)
    compact_mission = compact(" ".join(lignes_mission))
    compact_cas = compact(" ".join(lignes_cas))
    lu: dict[tuple[int, str, str], float] = {}
    lu.update(series_198(lignes_mission))
    lu.update(credits_actions(lignes_mission))
    lu.update(credits_mines(lignes_mission))
    lu.update(points(compact_mission, POINTS_MISSION))
    lu.update(seita_sans_actif(compact_mission))
    lu.update(points(compact_cas, POINTS_CAS))
    lu.update(tableaux_cas(lignes_cas))
    cle = (2024, "fonction_publique_etat", "ressortissants")
    if cle in lu:
        lu[cle] = round(lu[cle] * 1e6)
    return dict(sorted(lu.items()))


# -- confrontation -------------------------------------------------------------

def confronter(lu: dict[tuple[int, str, str], float], cible: Path = CIBLE) -> tuple[int, list[str], int]:
    """(identiques, écarts, lignes du CSV non lues)."""
    import csv

    with cible.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(
            ligne for ligne in flux if not ligne.lstrip().startswith("#")))
    identiques, ecarts, non_lues = 0, [], 0
    for ligne in lignes:
        cle = (int(ligne["annee"]), ligne["regime"], ligne["poste"])
        if cle not in lu:
            non_lues += 1
            continue
        if abs(lu[cle] - float(ligne["valeur"])) <= 5e-3:
            identiques += 1
        else:
            ecarts.append(f"{cle[0]} {cle[1]} {cle[2]} : CSV {ligne['valeur']}, document {lu[cle]:g}")
    return identiques, ecarts, non_lues


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    analyseur.add_argument("--fichier-cas", type=Path, metavar="CHEMIN", default=None,
                           help="le PAP du CAS Pensions, si --fichier donne celui de la mission")
    analyseur.add_argument("--confronter", action="store_true",
                           help="compare ce qui est lu à pap_regimes_subventionnes.csv")
    options = analyseur.parse_args(argv)
    jeux = {j["id"]: j for j in jeux_bloques()}
    if MISSION not in jeux or CAS not in jeux:
        print(f"{MISSION} ou {CAS} absent de data/sources.yaml, ou plus déclaré bloqué", file=sys.stderr)
        return 1
    try:
        documents = []
        for ident, fichier in ((MISSION, options.fichier), (CAS, options.fichier_cas)):
            jeu = jeux[ident]
            documents.append(lire_ou_telecharger(
                jeu["url"], telecharger, fichier, nom_local=jeu.get("fichier_local"),
                miroir=jeu.get("miroir"), sha256=jeu.get("sha256")))
    except (OSError, ValueError) as erreur:
        print(f"échec de la lecture d'un document : {erreur}", file=sys.stderr)
        return 1
    lu = lire(*documents)
    if not lu:
        print("rien n'a été lu — rien n'est écrit", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "sources": {ident: jeux[ident]["miroir"] for ident in (MISSION, CAS)},
        "empreintes": {ident: jeux[ident]["sha256"] for ident in (MISSION, CAS)},
        "recupere_le": date.today().isoformat(),
        "producteur": "Direction du budget, projets annuels de performances annexés au PLF 2026, "
                      "qui transcrivent les données des caisses : une transcription, d'où le "
                      "niveau haute et non certifiee.",
        "serie": {f"{annee}|{regime}|{poste}": valeur for (annee, regime, poste), valeur in lu.items()},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    regimes = sorted({cle[1] for cle in lu})
    print(f"{SORTIE.relative_to(RACINE)} : {len(lu)} valeurs lues, {len(regimes)} régimes "
          f"({', '.join(regimes)})")
    if options.confronter:
        identiques, ecarts, non_lues = confronter(lu)
        print(f"confrontation : {identiques} identiques, {len(ecarts)} écart(s), "
              f"{non_lues} ligne(s) du CSV que le script ne lit pas")
        for ecart in ecarts:
            print(f"  ÉCART   {ecart}")
        return 1 if ecarts else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
