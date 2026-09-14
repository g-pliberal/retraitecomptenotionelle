#!/usr/bin/env python3
"""Récupération des documents des institutions dont le régime n'est dans aucun texte de l'index.

    python scripts/fetch/sites_institutionnels.py

Huit régimes de l'inventaire n'ont ni décret ni arrêté dans le JORF ou dans
LEGI : les caisses des assemblées parlementaires et du CESE sont réglées par
leurs bureaux, les régimes du Pacifique par des délibérations locales, le
RAVGDT et les régimes de l'IRCEC par des règlements que seule la caisse publie.
Ce script télécharge, dans ``data/brut/sites_institutionnels/``, les pages et
les PDF sur lesquels leurs fiches ont été SAISIES (``statut_integration:
saisi`` dans ``data/sources.yaml``) : il ne produit aucune série, il garde la
pièce. Chaque fiche cite le document et la phrase qu'elle en tire.

Le texte des PDF est extrait à côté (``.txt``) quand ``pypdf`` est installé,
pour qu'un ``grep`` retrouve la phrase citée sans ouvrir le document.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

SORTIE = Path("data/brut/sites_institutionnels")

#: (nom du fichier, URL, ce que la fiche y lit)
DOCUMENTS = [
    ("assemblee_nationale_crd_2018.pdf",
     "https://www2.assemblee-nationale.fr/static/CRD-janvier-2018.pdf",
     "règlement de la Caisse de pensions des députés au 1er janvier 2018 : art. 5, 8, "
     "21, 21 ter et arrêté des Questeurs n° 15-043 (fiche assemblees_parlementaires)"),
    ("senat_protection_sociale.html",
     "https://www.senat.fr/connaitre-le-senat/role-et-fonctionnement/la-protection-sociale-des-senateurs.html",
     "62 à 64 ans et 43 annuités, Bureau du 12 juillet 2023 (note de la même fiche)"),
    ("cese_reglement_2025.pdf",
     "https://www.lecese.fr/sites/default/files/documents/REGLEMENT-Caisse-de-retraites-1erjanvier2025.pdf",
     "règlement de la caisse de retraites des membres du CESE : art. 4, 7, 17 (fiche cese_membres)"),
    ("cleiss_polynesie_salaries.html",
     "https://www.cleiss.fr/docs/regimes/regime_pf_salaries.html",
     "formule de la tranche A, points de la tranche B (fiches cps_polynesie, cps_polynesie_tranche_b)"),
    ("cleiss_polynesie_cotisations.html",
     "https://www.cleiss.fr/docs/cotisations/pf.html",
     "taux et plafonds des tranches A et B au 1er janvier 2026"),
    ("cleiss_nouvelle_caledonie_salaries.html",
     "https://www.cleiss.fr/docs/regimes/regime_nc_salaries.html",
     "âge, durée, valeur du point CAFAT (fiche cafat_nouvelle_caledonie)"),
    ("cleiss_nouvelle_caledonie_cotisations.html",
     "https://www.cleiss.fr/docs/cotisations/nc.html",
     "taux et plafond de l'assurance retraite CAFAT au 1er janvier 2026"),
    ("cafat_montant_retraite.html",
     "https://www.cafat.nc/le-montant-de-ma-retraite-cafat/",
     "acquisition des points par division des cotisations, valeur du point"),
    ("cpswf_retraites.html",
     "https://www.cpswf.wf/portail/index.php/retraites/",
     "âge, durée minimale, taux de 2,60 % et 1,30 % par an (fiche wallis_et_futuna)"),
    ("cpswf_taux_cotisation.html",
     "https://www.cpswf.wf/portail/index.php/entreprises/les-taux-de-cotisation/",
     "cotisation retraite de 17,1 % (2009) à 27 % (2020)"),
    ("drhfpnc_clr_2023.html",
     "https://drhfpnc.gouv.nc/actualites/03-10-2023/mesures-durgence-en-faveur-de-la-clr",
     "cotisations CLR de 10,8 à 13 % et de 25,1 à 28,8 %, minoration (fiche fonctionnaires_pacifique)"),
    ("drhfpnc_clr_2024.html",
     "https://drhfpnc.gouv.nc/actualites/16-09-2024/mesures-favorisant-la-perennite-du-regime-de-retraite-des-fonctionnaires-de",
     "âge de 60 à 62 ans de 2025 à 2030"),
    ("douane_ravgdt.html",
     "https://www.douane.gouv.fr/fiche/regime-dallocations-viageres-des-gerants-de-tabacs-ravgdt",
     "point d'achat 4,94 € et de service 2,42 €, cotisation de 2 % (fiche gerants_debits_tabac)"),
    ("ifrap_reforme_retraites_banques.html",
     "https://www.ifrap.org/retraite/la-reforme-des-retraites-des-banques",
     "pension bancaire de 72 à 75 % du dernier salaire en 42 ans, cotisation de 12 à 20 % "
     "(fiche regimes_professionnels_integres)"),
    ("ircec_memo_2026.html",
     "https://www.ircec.fr/actualite/memo-des-valeurs-2026/",
     "taux, prix d'achat et valeurs de service du RAAP, du RACD et du RACL (fiches ircec_racd, ircec_racl)"),
    ("cor_parametres_cnav_2009.pdf",
     "https://www.cor-retraites.fr/sites/default/files/2019-06/doc-1071.pdf",
     "COR, « L'évolution des paramètres du régime de la CNAV » : tableau des taux de "
     "cotisation des assurances sociales 1945-1967, d'après la Cnav "
     "(taux_cotisation_annuels.csv, années d'avant 1967)"),
]


def _telecharger(url: str) -> bytes:
    demande = urllib.request.Request(
        url, headers={"User-Agent": "retraite-notionnelle/0.1 (lecture unique, sans suivi)"}
    )
    with urllib.request.urlopen(demande, timeout=60) as reponse:
        return reponse.read()


def _texte_pdf(chemin: Path) -> str | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        # Le lecteur du dépôt, sans dépendance : celui des barèmes de la CNBF.
        try:
            from lecture_pdf import texte_pdf
        except ImportError:
            return None
        return texte_pdf(chemin.read_bytes())
    lecteur = PdfReader(str(chemin))
    return "\n".join(page.extract_text() or "" for page in lecteur.pages)


def principal() -> int:
    SORTIE.mkdir(parents=True, exist_ok=True)
    journal = {"date": date.today().isoformat(), "documents": []}
    echecs = 0
    for nom, url, usage in DOCUMENTS:
        cible = SORTIE / nom
        try:
            contenu = _telecharger(url)
        except (urllib.error.URLError, OSError) as erreur:
            print(f"  ÉCHEC {nom} : {erreur}", file=sys.stderr)
            echecs += 1
            journal["documents"].append({"fichier": nom, "url": url, "usage": usage,
                                         "recupere": False})
            continue
        cible.write_bytes(contenu)
        entree = {"fichier": nom, "url": url, "usage": usage, "recupere": True,
                  "octets": len(contenu)}
        if nom.endswith(".pdf"):
            texte = _texte_pdf(cible)
            if texte is not None:
                cible.with_suffix(".txt").write_text(texte, encoding="utf-8")
                entree["texte"] = cible.with_suffix(".txt").name
        journal["documents"].append(entree)
        print(f"  {nom} : {len(contenu)} octets")
    (SORTIE / "journal.json").write_text(
        json.dumps(journal, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{len(DOCUMENTS) - echecs} document(s) récupéré(s), {echecs} échec(s) → {SORTIE}")
    return 1 if echecs == len(DOCUMENTS) else 0


if __name__ == "__main__":
    sys.exit(principal())
