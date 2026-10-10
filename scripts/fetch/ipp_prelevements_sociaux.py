#!/usr/bin/env python3
"""Les prélèvements sur les pensions et sur les salaires, date par date, chez l'IPP.

    python scripts/fetch/ipp_prelevements_sociaux.py           # réécrit la donnée
    python scripts/fetch/ipp_prelevements_sociaux.py --lister  # imprime, sans écrire

À quoi il sert. Les indicateurs de cycle de vie nets (action 138, étape 9 ;
``retraite_notionnelle/cycle_de_vie.py``) rapportaient une pension nette des
prélèvements de 2026 à un salaire net des prélèvements de 2026, quelle que soit
l'année. Ce script lit chez l'IPP l'histoire de ces prélèvements — la CSG, la
CRDS, la CASA et la cotisation maladie des pensions ; la CSG, la CRDS, la
maladie, le veuvage, l'assurance chômage des salaires du privé, la maladie et
la contribution de solidarité des agents publics — et l'écrit, marche par
marche, dans ``data/reference/legislation/prelevements_historiques.yaml``.

LES CONVENTIONS DE L'IPP. Chaque barème est un CSV daté, du plus récent au plus
ancien, et chaque ligne est une PHOTOGRAPHIE : elle répète tous les taux en
vigueur à sa date — le 0,75 % de la maladie salariale en 2016 et en 2017, le
6,6 % de la CSG des pensions de 2005 à 2017. Une cellule vide après une valeur
dit donc qu'un taux n'est plus en vigueur, même quand la ligne en porte
d'autres : la maladie salariale au 1er janvier 2018 (les cellules de
l'employeur restent pleines), le chômage salarié au 1er octobre 2018, le
veuvage au 1er juillet 2004, la maladie des agents publics et celle des
pensions du régime général au 1er janvier 1998 — le décret n° 97-1252 ne la
fixe plus, quand la CSG des pensions monte des mêmes 2,8 points —, la
contribution de solidarité au 1er janvier 2018. Une cellule vide avant toute
valeur dit qu'un taux n'existe pas encore (le taux médian de CSG avant 2019).

AVANT LA PREMIÈRE MARCHE. La CSG (1991), la CRDS (1996), la CASA (2013), la
maladie des pensions (1980), le veuvage (1981), la solidarité (1982) et
l'assurance chômage (1959) sont nés à leur première marche, et ne prélèvent
rien avant. La maladie des salariés et des agents publics existait avant 1967,
où commencent les barèmes de l'IPP : ses taux de 1967 sont tenus en deçà
(`tenues_avant_leur_premiere_marche`), et le dépôt le dit.

LES INDÉPENDANTS (action 138, étape 9, sixième partie). La maladie des
artisans et commerçants et celle des professions libérales, la cotisation
d'allocations familiales des travailleurs indépendants, chez l'IPP de 1970 et
de 1974 ; leur CSG et leur CRDS, aux taux de l'activité, sur leur revenu
augmenté de leurs cotisations jusqu'en 2024 (``ASSIETTE_CSG``). L'IPP s'arrête
en 2018, et se trompe à quelques marches que les textes, lus dans les index
JORF et LEGI de la DILA, disent autrement (``CORRECTIONS``) : les échéances
semestrielles de 1991 et 1992, que l'IPP avance d'une marche ; l'indemnité
journalière des artisans, à 0,50 % dès 1996 et non 1997 ; le 1er octobre
1984 des libéraux, que l'IPP met au 1er janvier. Depuis 2013 pour les artisans
et commerçants, depuis 2017 pour les libéraux, les marches sont celles des
articles D. 612-4 à D. 621-3, version par version (``LUES_AUX_TEXTES``) :
l'IPP y oublie l'indemnité journalière de 2013 à 2017, retarde à mars le
déplafonnement de 2013, ignore la réduction de 2017 des libéraux, prête 7,35 %
au revenu de plus de cinq plafonds de 2018 quand le décret n° 2017-1894 dit
6,5 %, et n'a rien après 2018.

Ce qu'il ne fait pas. L'IPP est une transcription, non une source productrice :
la donnée plafonne à ``haute``. Il n'ancre pas chaque marche au Journal officiel
(``ipp_taux_cotisation.py`` le fait pour la vieillesse) : l'index de la DILA
n'était pas présent quand il a été écrit ; les références que l'IPP cite sont
gardées, marche par marche.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import sys
import urllib.request
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
SORTIE = RACINE_DEPOT / "data" / "reference" / "legislation" / "prelevements_historiques.yaml"
RACINE = "https://baremes.ipp.eu/parameters/prelevements-sociaux"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
FRANC = 6.55957

#: Chaque série écrite : son chemin dans la donnée, le barème de l'IPP, et ses
#: colonnes — le nom qu'elles prennent, la colonne de l'IPP.
SERIES = {
    ("pensions", "csg_taux_plein"): (
        "prelevements_sociaux.contributions_sociales.csg.remplacement",
        {"taux": "pensions_retraite_invalidite.taux_plein"}),
    ("pensions", "csg_taux_median"): (
        "prelevements_sociaux.contributions_sociales.csg.remplacement",
        {"taux": "pensions_retraite_invalidite.taux_median"}),
    ("pensions", "csg_taux_reduit"): (
        "prelevements_sociaux.contributions_sociales.csg.remplacement",
        {"taux": "pensions_retraite_invalidite.taux_reduit"}),
    ("pensions", "crds"): (
        "prelevements_sociaux.contributions_sociales.crds",
        {"taux": "prelevements_sociaux.contributions_sociales.crds"}),
    ("pensions", "casa"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.casa",
        {"taux": "pensions_retraite_preretraite_invalidite.0-"}),
    ("pensions", "maladie_regime_general"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.mmid_ret",
        {"taux": "avantages_de_retraite.regime_general"}),
    ("pensions", "maladie_complementaires"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.mmid_ret",
        {"taux": "avantages_de_retraite.regimes_comp"}),
    ("salaires", "csg"): (
        "prelevements_sociaux.contributions_sociales.csg.activite",
        {"taux": "taux_global", "abattement": "abattement.0-",
         "abattement_jusqu_a_quatre_plafonds": "abattement.0-4"}),
    ("salaires", "crds"): (
        "prelevements_sociaux.contributions_sociales.crds",
        {"taux": "prelevements_sociaux.contributions_sociales.crds"}),
    ("salaires", "maladie_prive"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.mmid",
        {"tout_salaire": "salarie.maladie.0-", "sous_plafond": "salarie.maladie.0-1",
         "au_dela_du_plafond": "salarie.maladie.1-"}),
    ("salaires", "veuvage_prive"): (
        "prelevements_sociaux.cotisations_securite_sociale_regime_general.veuvage",
        {"tout_salaire": "salaries.sur_tout_salaire", "sous_plafond": "salaries.sous_plafond"}),
    ("salaires", "chomage_prive"): (
        "prelevements_sociaux.cotisations_regime_assurance_chomage.chomage",
        {"tout_salaire": "salarie.chomage.0-", "sous_plafond": "salarie.chomage.0-1",
         "de_un_a_quatre_plafonds": "salarie.chomage.1-4"}),
    ("salaires", "maladie_etat"): (
        "prelevements_sociaux.cotisations_secteur_public.mmid.etat",
        {"tout_salaire": "tout_traitement.salarie.maladie.0-",
         "sous_plafond": "sous_plafond.salarie.maladie.0-1"}),
    ("salaires", "maladie_collectivites"): (
        "prelevements_sociaux.cotisations_secteur_public.mmid.colloc",
        {"tout_salaire": "tout_traitement.salarie.maladie.0-",
         "sous_plafond": "sous_plafond.salarie.maladie.0-1"}),
    ("salaires", "solidarite_public"): (
        "prelevements_sociaux.cotisations_secteur_public.fds",
        {"taux": "salarie.solidarite.0-4", "seuil_mensuel": "salarie.seuil_d_assujettissement"}),
}

#: Les indépendants : la maladie des artisans et commerçants, celle des
#: professions libérales, la cotisation d'allocations familiales. Les colonnes
#: de l'IPP sont des TRANCHES qui s'ajoutent — 3,10 % sous le plafond et
#: 8,45 % sous cinq plafonds font 11,55 % sous le plafond —, et ses taux
#: modulés selon le revenu, depuis 2015, se récrivent en paliers (``_famille``).
SERIES.update({
    ("independants", "maladie_artisans_commercants"): (
        "prelevements_sociaux.cotisations_taxes_independants_artisans_commercants.mmid.mmid_ac",
        {"tout_revenu": "assures_actifs.toute_remuneration",
         "sous_plafond": "assures_actifs.sous_pss",
         "sous_quatre_plafonds": "assures_actifs.sous_4_pss",
         "sous_cinq_plafonds": "assures_actifs.sous_5_pss",
         "ij_artisans_sous_cinq_plafonds": "assures_actifs.supplement_artisans_ij.sous_5_pss"}),
    ("independants", "maladie_professions_liberales"): (
        "prelevements_sociaux.professions_liberales.mmid_pl",
        {"tout_revenu": "assures_actifs.toute_remuneration",
         "sous_plafond": "assures_actifs.sous_pss",
         "sous_quatre_plafonds": "assures_actifs.sous_4_pss",
         "sous_cinq_plafonds": "assures_actifs.sous_5_pss"}),
    ("independants", "famille"): (
        "prelevements_sociaux.cotisations_taxes_independants_artisans_commercants.famille",
        {"tout_revenu": "arti.famille.0-", "sous_plafond": "famille_ind.sous_pss",
         "sous_seuil": "famille_ind.sous_10_000_frf",
         "du_seuil_au_plafond": "famille_ind.entre_10_000_frf_et_1_pss",
         "jusqu_a_110_pc": "famille_ind.si_revenu_d_activite_110_pss",
         "des_140_pc": "famille_ind.si_revenu_d_activite_140_pss"}),
})

#: Le seuil de la cotisation familiale de 1974 à 1982 : 10 000 F, en euros.
SEUIL_FAMILLE_FRANCS = 10_000

#: Les séries dont l'IPP ne donne pas la naissance : leur première marche est
#: tenue en deçà d'elle, au lieu de zéro. La cotisation familiale des
#: indépendants était forfaitaire avant 1974 (arrêté du 20 juin 1963, que l'IPP
#: cite sans le chiffrer) : ses taux de 1974 valent en deçà, comme la maladie
#: des salariés.
TENUES_AVANT = ("maladie_prive", "maladie_etat", "maladie_collectivites", "famille")


def _taux_reduit_2018(revenu_en_plafonds: float) -> float:
    """Le taux réduit de D. 621-2 en 2018 sous 40 % du plafond, en ce point :
    ``[(T1 - T2) / (1,1 × PSS)] × r + [(T2 - T3) / (0,4 × PSS)] × r + T3``."""
    return round((0.072 - 0.022) / 1.1 * revenu_en_plafonds
                 + (0.022 - 0.0085) / 0.4 * revenu_en_plafonds + 0.0085, 8)


#: Ce que les textes disent autrement que l'IPP, lus dans les index JORF et LEGI
#: de la DILA. ``ipp`` nomme la marche de l'IPP que la correction ôte, ``lue``
#: celle qu'elle met, ses autres taux étant ceux de la marche qui la précède ;
#: une correction dont la marche a disparu de l'IPP arrête le script.
CORRECTIONS: dict[str, list[dict]] = {
    "maladie_artisans_commercants": [
        {"ipp": "1991-08-01", "lue": None},
        {"ipp": "1991-10-01", "lue": {"depuis": "1991-10-01", "sous_cinq_plafonds": 0.0915},
         "texte": "Décret 91-745 du 31/07/1991, art. 1 : à l'échéance du 1er octobre 1991 "
                  "(JORFTEXT000000571495)"},
        {"ipp": None, "lue": {"depuis": "1992-10-01", "sous_cinq_plafonds": 0.0975},
         "texte": "Décret 92-295 du 30/03/1992, art. 1 : à l'échéance du 1er octobre 1992 "
                  "(JORFARTI000001372694)"},
        {"ipp": None, "lue": {"depuis": "1996-01-01", "ij_artisans_sous_cinq_plafonds": 0.005},
         "texte": "Décret 95-556 du 06/05/1995, art. 1 et 5 : 0,25 % pour la seule année 1995 "
                  "(JORFARTI000001398418)"},
    ],
    "maladie_professions_liberales": [
        {"ipp": "1984-01-01", "lue": {"depuis": "1984-10-01", "sous_plafond": 0.031,
                                      "sous_cinq_plafonds": 0.0845},
         "texte": "Décret 84-817 du 03/09/1984, art. 1 : à compter du 1er octobre 1984 "
                  "(JORFTEXT000000873004)"},
        {"ipp": "1991-08-01", "lue": None},
        {"ipp": "1991-10-01", "lue": {"depuis": "1991-10-01", "sous_cinq_plafonds": 0.0915},
         "texte": "Décret 91-745 du 31/07/1991, art. 1 : à l'échéance du 1er octobre 1991 "
                  "(JORFTEXT000000571495)"},
        {"ipp": None, "lue": {"depuis": "1992-10-01", "sous_cinq_plafonds": 0.0975},
         "texte": "Décret 92-295 du 30/03/1992, art. 1 : à l'échéance du 1er octobre 1992 "
                  "(JORFARTI000001372694)"},
    ],
}

#: Les barèmes de 2025, communs à tous les indépendants : le taux réduit de
#: D. 621-2 sous trois plafonds, sur tout le revenu ; au-delà, 8,50 % jusqu'à
#: trois plafonds et 6,50 % au-dessus (D. 621-1).
_BAREME_2025 = {"progressif_jusqu_a": 3.0,
                "paliers": [[0.2, 0.0], [0.4, 0.015], [0.6, 0.04], [1.1, 0.065],
                            [2.0, 0.077], [3.0, 0.085]],
                "sous_trois_plafonds": 0.085, "au_dela_de_trois_plafonds": 0.065}
_TEXTE_2025 = ("Décret 2024-688 du 5/07/2024, art. 6 : CSS, D. 621-1, D. 621-2 et D. 621-3 "
               "(LEGIARTI000049904610, LEGIARTI000049904592, LEGIARTI000049904537)")
_TEXTE_2017 = ("Décret 2017-301 du 8/03/2017, art. 3 et 5 : CSS, D. 612-4 et D. 612-5 "
               "(LEGIARTI000034163552, LEGIARTI000034163561)")

#: Les marches que l'IPP n'a pas, ou pas justes, lues dans les versions des
#: articles de LEGI. Elles prennent le relais de l'IPP à leur première date. Une
#: marche ``paliers`` porte un taux sur TOUT le revenu, interpolé entre deux
#: paliers, en deçà de ``progressif_jusqu_a`` plafonds — partout sans lui — ;
#: au-delà, ses tranches. L'indemnité journalière des artisans et commerçants
#: entre de 2001 à 2012 dans les 6,40 et 6,60 % de l'IPP, de 2018 à 2024 dans les
#: 7,20 % de D. 621-1 ; hors d'eux, elle a sa colonne, que le taux réduit ne
#: touche pas.
LUES_AUX_TEXTES: dict[str, list[dict]] = {
    "maladie_artisans_commercants": [
        {"depuis": "2013-01-01", "tout_revenu": 0.065, "ij_sous_cinq_plafonds": 0.007,
         "texte": "Décret 2012-1551 du 28/12/2012, art. 2 : CSS, D. 612-4 "
                  "(LEGIARTI000026885410) ; D. 612-9 (LEGIARTI000025629824)"},
        {"depuis": "2017-01-01", "tout_revenu": 0.065, "progressif_jusqu_a": 0.7,
         "paliers": [[0.0, 0.03], [0.7, 0.065]], "ij_sous_cinq_plafonds": 0.007,
         "texte": _TEXTE_2017},
        {"depuis": "2018-01-01",
         "paliers": [[0.0, 0.0085], [0.4, _taux_reduit_2018(0.4)], [1.1, 0.072],
                     [5.0, 0.072], [5.0, 0.065]],
         "texte": "Décret 2017-1894 du 30/12/2017, art. 5 et 8 : CSS, D. 621-1 et D. 621-2 "
                  "(LEGIARTI000036469673, LEGIARTI000036469691)"},
        {"depuis": "2020-05-25", "progressif_jusqu_a": 1.1,
         "paliers": [[0.0, 0.0085], [0.4, _taux_reduit_2018(0.4)], [1.1, 0.072]],
         "sous_cinq_plafonds": 0.072, "au_dela_de_cinq_plafonds": 0.065,
         "texte": "Décret 2020-621 du 22/05/2020, art. 1 (II, 8°) et 5 : CSS, D. 621-1 "
                  "(LEGIARTI000041966835)"},
        {"depuis": "2022-01-01", "progressif_jusqu_a": 1.1,
         "paliers": [[0.4, 0.005], [0.6, 0.045], [1.1, 0.072]],
         "sous_cinq_plafonds": 0.072, "au_dela_de_cinq_plafonds": 0.065,
         "texte": "Décret 2022-1529 du 7/12/2022, art. 4 : CSS, D. 621-1 et D. 621-2 "
                  "(LEGIARTI000046714760, LEGIARTI000046714747)"},
        {"depuis": "2025-01-01", **_BAREME_2025, "ij_sous_cinq_plafonds": 0.005,
         "texte": _TEXTE_2025},
    ],
    "maladie_professions_liberales": [
        {"depuis": "2017-01-01", "tout_revenu": 0.065, "progressif_jusqu_a": 0.7,
         "paliers": [[0.0, 0.03], [0.7, 0.065]], "texte": _TEXTE_2017},
        {"depuis": "2018-01-01", "tout_revenu": 0.065, "progressif_jusqu_a": 1.1,
         "paliers": [[0.0, 0.015], [1.1, 0.065]],
         "texte": "Décret 2017-1894 du 30/12/2017, art. 5 et 8 : CSS, D. 621-3 "
                  "(LEGIARTI000036469693)"},
        {"depuis": "2021-01-01", "tout_revenu": 0.065, "progressif_jusqu_a": 1.1,
         "paliers": [[0.0, 0.015], [1.1, 0.065]], "ij_sous_trois_plafonds": 0.0015,
         "texte": "Décret 2021-755 du 12/06/2021, art. 2 et 3 : 0,15 % pour la seule année "
                  "2021 ; CSS, D. 621-3 (LEGIARTI000043656764)"},
        {"depuis": "2022-01-01", "tout_revenu": 0.065, "progressif_jusqu_a": 1.1,
         "paliers": [[0.4, 0.0], [0.6, 0.04], [1.1, 0.065]], "ij_sous_trois_plafonds": 0.003,
         "texte": "Décret 2022-1529 du 7/12/2022, art. 4 : CSS, D. 621-3 (LEGIARTI000046714732)"},
        {"depuis": "2025-01-01", **_BAREME_2025, "ij_sous_trois_plafonds": 0.003,
         "texte": _TEXTE_2025},
    ],
}

#: La CSG et la CRDS d'un indépendant, aux taux de l'activité et sans abattement :
#: sur son revenu professionnel augmenté de ses cotisations personnelles de
#: sécurité sociale, puis, depuis l'assiette unique, sur l'assiette de ses
#: cotisations.
ASSIETTE_CSG = [
    {"depuis": "1991-02-01", "cotisations_ajoutees": 1.0,
     "texte": "Loi 90-1168 du 29/12/1990, art. 129 (LF pour 1991) : les cotisations "
              "personnelles de sécurité sociale sont ajoutées au bénéfice "
              "(JORFARTI000002299239) ; CSS, L. 136-3"},
    {"depuis": "2025-01-01", "cotisations_ajoutees": 0.0,
     "texte": "Loi 2023-1250 du 26/12/2023, art. 18 VII (LFSS pour 2024) : CSS, L. 136-3 "
              "(LEGIARTI000048683641)"},
]

#: L'ordre des colonnes d'une marche d'indépendant dans la donnée.
ORDRE_INDEPENDANTS = (
    "tout_revenu", "sous_plafond", "sous_trois_plafonds", "sous_quatre_plafonds",
    "sous_cinq_plafonds", "au_dela_de_trois_plafonds", "au_dela_de_cinq_plafonds",
    "sous_seuil", "du_seuil_au_plafond", "seuil_euros", "ij_sous_trois_plafonds",
    "ij_sous_cinq_plafonds", "ij_artisans_sous_cinq_plafonds", "progressif_jusqu_a", "paliers",
    "cotisations_ajoutees")


def _telecharger(parametre: str) -> list[dict[str, str]]:
    demande = urllib.request.Request(f"{RACINE}/{parametre}/csv", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return list(csv.DictReader(io.StringIO(reponse.read().decode("utf-8"))))


def _nombre(brut: str) -> float | None:
    """« 6,55 % » -> 0.0655 ; « 1 439,35 € » -> 1439.35 ; « 8 157,58 FRF » en
    euros. Une cellule vide rend ``None``."""
    texte = (brut or "").replace(" ", " ").replace("\xa0", " ").strip()
    if not texte:
        return None
    francs = texte.endswith("FRF")
    pourcent = texte.endswith("%")
    nombre = float(texte.replace("%", "").replace("€", "").replace("FRF", "")
                   .replace(" ", "").replace(",", "."))
    if pourcent:
        return round(nombre / 100.0, 8)
    return round(nombre / FRANC, 2) if francs else nombre


def _jour(brut: str) -> str:
    jour, mois, annee = (int(x) for x in brut.split("/"))
    return dt.date(annee, mois, jour).isoformat()


def marches(lignes: list[dict[str, str]], colonnes: dict[str, str]) -> list[dict]:
    """Les marches d'une série, de la plus ancienne à la plus récente : une
    marche par date où ses valeurs changent. Chaque ligne est une photographie
    des taux en vigueur ; une colonne vide après une valeur vaut zéro."""
    lues: list[dict] = []
    for ligne in sorted(lignes, key=lambda l: _jour(l["date"])):
        valeurs = {nom: _nombre(ligne.get(colonne, "")) for nom, colonne in colonnes.items()}
        if not lues and all(v is None for v in valeurs.values()):
            continue
        valeurs = {nom: (0.0 if v is None else v) for nom, v in valeurs.items()}
        if lues and all(lues[-1][nom] == v for nom, v in valeurs.items()):
            continue
        reference = " ".join((ligne.get("reference") or "").split())
        lues.append({"depuis": _jour(ligne["date"]), **valeurs,
                     "texte": reference.split(";")[0].strip() or "IPP, sans référence"})
    # Une colonne qui n'est jamais en vigueur ne s'écrit pas.
    vides = [nom for nom in colonnes if all(m[nom] == 0.0 for m in lues)]
    return [{k: v for k, v in m.items() if k not in vides} for m in lues]


def corriger(nom: str, lues: list[dict]) -> list[dict]:
    """Les marches de l'IPP, aux corrections des textes près (:data:`CORRECTIONS`)."""
    par_date = {marche["depuis"]: marche for marche in lues}
    for correction in CORRECTIONS.get(nom, ()):
        if correction["ipp"] is not None:
            if correction["ipp"] not in par_date:
                raise SystemExit(f"{nom} : l'IPP n'a plus de marche au {correction['ipp']}, "
                                 "la correction est à relire")
            del par_date[correction["ipp"]]
        lue = correction["lue"]
        if lue is None:
            continue
        avant = [m for depuis, m in sorted(par_date.items()) if depuis <= lue["depuis"]]
        precedente = {k: v for k, v in (avant[-1] if avant else {}).items()
                      if k not in ("depuis", "texte")}
        par_date[lue["depuis"]] = {**precedente, **lue, "texte": correction["texte"]}
    return [par_date[depuis] for depuis in sorted(par_date)]


def _famille(marche: dict) -> dict:
    """Une marche de la cotisation familiale : le seuil de 10 000 F en euros, et
    le taux modulé de 2015 et de 2018 — le taux ``jusqu_a_110_pc`` jusqu'à 110 %
    du plafond, ``des_140_pc`` dès 140 %, interpolé entre les deux et sur tout le
    revenu (notes de l'IPP ; CSS, D. 613-1) — en paliers."""
    marche = dict(marche)
    bas, haut = marche.pop("jusqu_a_110_pc", 0.0), marche.pop("des_140_pc", 0.0)
    if haut:
        marche.update(tout_revenu=haut, progressif_jusqu_a=1.4,
                      paliers=[[1.1, bas], [1.4, haut]])
    if marche.get("sous_seuil") or marche.get("du_seuil_au_plafond"):
        marche["seuil_euros"] = round(SEUIL_FAMILLE_FRANCS / FRANC, 2)
    return marche


def _normaliser(lues: list[dict]) -> list[dict]:
    """Chaque marche dit tous les taux de sa série, zéro compris, dans l'ordre de
    :data:`ORDRE_INDEPENDANTS` ; une marche qui ne change rien s'efface, une
    colonne jamais en vigueur ne s'écrit pas."""
    taux = [cle for cle in ORDRE_INDEPENDANTS if cle not in ("paliers", "progressif_jusqu_a")
            and any(marche.get(cle) for marche in lues)]
    sorties: list[dict] = []
    for marche in sorted(lues, key=lambda m: m["depuis"]):
        sortie = {"depuis": marche["depuis"], **{cle: float(marche.get(cle, 0.0)) for cle in taux}}
        for cle in ("progressif_jusqu_a", "paliers"):
            if marche.get(cle):
                sortie[cle] = marche[cle]
        if sorties and {k: v for k, v in sorties[-1].items() if k not in ("depuis", "texte")} == {
                k: v for k, v in sortie.items() if k != "depuis"}:
            continue
        sorties.append({**sortie, "texte": marche["texte"]})
    return sorties


def independant(nom: str, lues: list[dict]) -> list[dict]:
    """Une série d'indépendant : l'IPP corrigé, ses taux modulés en paliers, puis
    les marches lues aux textes, qui prennent le relais à leur première date."""
    lues = corriger(nom, lues)
    if nom == "famille":
        lues = [_famille(marche) for marche in lues]
    textes = LUES_AUX_TEXTES.get(nom)
    if textes:
        lues = [m for m in lues if m["depuis"] < textes[0]["depuis"]] + [dict(m) for m in textes]
    return _normaliser(lues)


def _valeur(valeur) -> str:
    if isinstance(valeur, list):
        return "[" + ", ".join(_valeur(v) for v in valeur) + "]"
    return f"{valeur:g}" if isinstance(valeur, float) else str(valeur)


def _yaml(marche: dict) -> str:
    champs = []
    for cle, valeur in marche.items():
        if cle == "texte":
            champs.append(f'texte: "{valeur.replace(chr(34), chr(39))}"')
        elif cle == "depuis":
            champs.append(f'depuis: "{valeur}"')
        else:
            champs.append(f"{cle}: {_valeur(valeur)}")
    return "    - {" + ", ".join(champs) + "}"


ENTETE = """\
# Les prélèvements sur les pensions et sur les salaires, marche par marche
# -----------------------------------------------------------------------
# source_id: ipp_prelevements_sociaux
#
# ÉCRIT PAR `scripts/fetch/ipp_prelevements_sociaux.py`, jamais à la main : les
# barèmes de l'Institut des politiques publiques, lus le {lu_le}, chacun avec la
# référence que l'IPP cite pour sa marche. Une transcription, non une source
# productrice : `haute` au plus (data/sources.yaml, `ipp`).
#
# QUI LE LIT. Les indicateurs de cycle de vie nets
# (`retraite_notionnelle/cycle_de_vie.py`, action 138, étape 9) : la pension
# nette de chaque année aux taux de son année, le salaire net de chaque année
# aux siens. La fiche de paie du site et la pension nette qu'il affiche restent
# aux taux de l'année courante (`prelevements_remuneration.yaml`), qui doivent
# rendre ceux de la dernière marche de chaque série : un test le tient.
#
# LES SÉRIES. Un taux s'entend en part de son assiette ; chaque marche dit
# tous les taux en vigueur à sa date, zéro compris. Une contribution n'existait
# pas avant sa première marche, sauf celles de `tenues_avant_leur_premiere_marche`,
# la maladie, que les barèmes de l'IPP ne prennent qu'en 1967 : leurs taux de
# 1967 valent en deçà.
#   pensions : la CSG au taux plein, médian, réduit ; la CRDS ; la CASA ; la
#     cotisation maladie des pensions du régime général et celle des
#     complémentaires (les régimes de `maladie_complementaire`).
#   salaires : la CSG et la CRDS d'activité, sur le brut abattu de
#     `abattement` (sans limite) ou de `abattement_jusqu_a_quatre_plafonds`
#     (jusqu'à quatre plafonds, depuis 2011) — l'IPP n'en donne pas avant 1998,
#     et le dépôt n'en retient pas ; la maladie, le veuvage et l'assurance
#     chômage du salarié du privé, `tout_salaire`, `sous_plafond`,
#     `au_dela_du_plafond`, `de_un_a_quatre_plafonds` ; la maladie des agents de
#     l'État et des collectivités ; la contribution exceptionnelle de solidarité
#     des agents publics, au-delà d'un seuil mensuel en euros.
#   independants : la maladie des artisans et commerçants (D. 612-4, puis
#     D. 621-1 et D. 621-2) et celle des professions libérales (D. 621-3), leur
#     indemnité journalière ; la cotisation d'allocations familiales des
#     travailleurs indépendants ; l'assiette de leur CSG et de leur CRDS, aux
#     taux de `salaires` et sans abattement. Les colonnes sont des tranches qui
#     s'ajoutent, en plafonds de l'année : `tout_revenu`, `sous_plafond`,
#     `sous_trois_plafonds`, `sous_quatre_plafonds`, `sous_cinq_plafonds`,
#     `au_dela_de_trois_plafonds`, `au_dela_de_cinq_plafonds` ; de 1974 à 1982,
#     la cotisation familiale porte `sous_seuil` jusqu'à `seuil_euros` (10 000 F)
#     et `du_seuil_au_plafond` au-delà. Une marche à `paliers` porte, en deçà de
#     `progressif_jusqu_a` plafonds (partout sans lui), un taux sur tout le
#     revenu, interpolé entre deux paliers `[plafonds, taux]` : la réduction des
#     petits revenus depuis 2015 et 2017. L'indemnité journalière
#     (`ij_sous_cinq_plafonds`, `ij_sous_trois_plafonds` pour les libéraux,
#     `ij_artisans_sous_cinq_plafonds` pour les seuls artisans) n'est pas
#     réduite ; de 2001 à 2012 et de 2018 à 2024, elle est dans le taux.
#     `assiette_csg` dit si les cotisations personnelles s'ajoutent au revenu
#     pour la CSG : de 1991 à 2024, oui (L. 136-3).
#
# LES INDÉPENDANTS, CE QUI N'EST PAS DE L'IPP. L'IPP s'arrête en 2018 : les
# marches de 2013 à 2025 des artisans et commerçants, de 2017 à 2025 des
# libéraux, sont lues dans les versions de D. 612-4, D. 612-5, D. 612-9 et
# D. 621-1 à D. 621-3 (index LEGI) ; et quatre marches de l'IPP sont corrigées
# par les décrets qu'il cite (index JORF). Le texte de chaque marche le dit.
# L'AMPI, née en 1969, ne prélève ici qu'à la première marche de l'IPP, en
# avril 1970. L'indemnité journalière des commerçants y naît en 2001, et non à
# 0,25 % pour l'année 2000 (D. 612-9) ; l'invalidité-décès n'y est pas, et garde
# les taux de l'année courante.
#
# CE QUE L'IPP NE DIT PAS. Le taux de la maladie des pensions des autres régimes
# de base (la fonction publique, les indépendants) : seule celle du régime
# général est écrite ; le dépôt n'en prélève donc aucune ailleurs.
"""


def ecrire(series: dict[tuple[str, str], list[dict]], lu_le: str) -> str:
    lignes = [ENTETE.format(lu_le=lu_le).rstrip("\n"), f'lu_le: "{lu_le}"', "fiabilite: haute",
              f"tenues_avant_leur_premiere_marche: [{', '.join(TENUES_AVANT)}]"]
    for partie in ("pensions", "salaires", "independants"):
        lignes += ["", f"{partie}:"]
        for (bloc, nom), marches_lues in series.items():
            if bloc != partie:
                continue
            lignes.append(f"  {nom}:")
            lignes += [_yaml(marche) for marche in marches_lues]
    return "\n".join(lignes) + "\n"


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--lister", action="store_true", help="imprime sans écrire")
    arguments = analyseur.parse_args(argv)
    telecharges: dict[str, list[dict[str, str]]] = {}
    series = {}
    for cle, (parametre, colonnes) in SERIES.items():
        if parametre not in telecharges:
            telecharges[parametre] = _telecharger(parametre)
        series[cle] = marches(telecharges[parametre], colonnes)
        if cle[0] == "independants":
            series[cle] = independant(cle[1], series[cle])
    series[("independants", "assiette_csg")] = _normaliser(ASSIETTE_CSG)
    texte = ecrire(series, dt.date.today().isoformat())
    if arguments.lister:
        print(texte)
        return 0
    SORTIE.write_text(texte, encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE_DEPOT)} : {sum(len(m) for m in series.values())} marches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
