"""Le panorama « Les retraités et les retraites » de la DREES, édition 2026.

L'action 178 l'exploite en entier. Le site de la DREES refuse le cloud
(réponse vide à curl, 503 à WebFetch) : le manifeste déclare le document, son
miroir et son empreinte, et ``source_locale.py --recuperer`` l'apporte à toute
session ; ses classeurs, que le site ne sert qu'à un poste, la release
``documents-apportes`` les sert en une archive.
``scripts/fetch/drees_panorama.py`` en relève les fiches, les
tableaux, les graphiques et leurs sources dans un témoin,
``tests/temoins/drees_panorama_2026.json`` ; le suivi,
``data/reference/drees_panorama_2026.yaml``, dit fiche par fiche ce que le
dépôt en a déjà et ce qu'il en tirera. Aucune fiche n'y manque.

Les valeurs attendues sont lues dans le PDF : le sommaire (pages 3 et 4), la
page 21 (fiche 1, tableau 1) et la page 22 (fiche 1, graphiques 1 et 2).
Celles de l'accès le sont sur la page de la DREES et dans ce qu'elle sert,
depuis un poste, le 2 novembre 2026 : l'adresse du PDF, celles des
classeurs, et leurs empreintes.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "drees_panorama_2026.json"
SUIVI = RACINE / "data" / "reference" / "drees_panorama_2026.yaml"


def _module():
    chemin = RACINE / "scripts" / "fetch" / "drees_panorama.py"
    specification = importlib.util.spec_from_file_location("drees_panorama", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["drees_panorama"] = module
    specification.loader.exec_module(module)
    return module


def _source_locale():
    chemin = RACINE / "scripts" / "fetch" / "source_locale.py"
    specification = importlib.util.spec_from_file_location("source_locale", chemin)
    module = importlib.util.module_from_spec(specification)
    sys.modules["source_locale"] = module
    specification.loader.exec_module(module)
    return module


def _jeux() -> dict[str, dict]:
    manifeste = yaml.safe_load((RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))
    return {
        jeu["id"]: jeu
        for institution in manifeste["institutions"].values()
        for jeu in institution.get("jeux", [])
    }


# Deux pages du PDF, telles que ``pdftotext -layout`` les rend (lignes vides et
# colonnes de chiffres des graphiques omises) : la page 21 et la page 22, que
# sépare un saut de page.
PAGES = (
    "                                     Les effectifs de retraités de droit direct      01\n"
    "     Tableau 1 Effectifs de retraités de droit direct tous régimes\n"
    "          En milliers\n"
    "     Note > Voir annexe 3, note sur le champ de la retraite.\n"
    "     Sources > Drees, EIR, modèle ANCETRE.\n"
    "                    Les retraités et les retraites > Édition 2026 > Drees       21\n"
    "\f"
    "01     Les effectifs de retraités de droit direct\n"
    "     Graphique 1 Rapport entre les effectifs de personnes en emploi et les effectifs\n"
    "     de retraités de droit direct, résidant en France ou à l’étranger\n"
    "          En %\n"
    "     Note > Voir annexe 3, note sur le champ de la retraite.\n"
    "     Champ > Retraités ayant perçu une pension de droit direct au cours de l’année n, résidant en France ou à l’étranger,\n"
    "     vivants au 31 décembre de l’année.\n"
    "     Sources > Drees, EIR, modèle ANCETRE ; Insee, comptes nationaux.\n"
    "     Graphique 2 Variation annuelle du nombre de retraités et effectifs annuels\n"
    "     de nouveaux retraités\n"
    "     Sources > Drees, EIR 2020 pour les générations nées entre 1926 et 1953, modèle ANCETRE pour les générations nées entre\n"
    "     1954 et 1957.\n"
    "     22                               Les retraités et les retraites > Édition 2026 > Drees\n"
)


def test_le_releve_lit_chaque_figure_sa_page_et_sa_source():
    figures = _module().relever_figures(PAGES)
    assert figures == [
        {"fiche": "01", "page": 21, "nature": "Tableau", "numero": "1",
         "titre": "Effectifs de retraités de droit direct tous régimes",
         "sources": "Drees, EIR, modèle ANCETRE."},
        {"fiche": "01", "page": 22, "nature": "Graphique", "numero": "1",
         "titre": "Rapport entre les effectifs de personnes en emploi et les effectifs "
                  "de retraités de droit direct, résidant en France ou à l’étranger",
         "sources": "Drees, EIR, modèle ANCETRE ; Insee, comptes nationaux."},
        {"fiche": "01", "page": 22, "nature": "Graphique", "numero": "2",
         "titre": "Variation annuelle du nombre de retraités et effectifs annuels "
                  "de nouveaux retraités",
         "sources": "Drees, EIR 2020 pour les générations nées entre 1926 et 1953, "
                    "modèle ANCETRE pour les générations nées entre 1954 et 1957."},
    ]


# Les pages 45 et 46 (fiche 4), 63 (fiche 5) et 112 (fiche 11), réduites aux
# lignes qui comptent. Une source continue après un « ; », même sur une ligne
# qui commence par une majuscule ; une note numérotée (« 6. »), l'étiquette
# d'un volet (« 4a. », « 4b. ») ou la ligne des années d'un tableau ne
# prolongent ni un titre ni une source ; un encadré ne prend pas la source de
# la figure qui le suit.
SUITES = (
    "                                   La revalorisation des pensions individuelles      04\n"
    "   Encadré 1 Les modalités de revalorisation des pensions de retraite\n"
    "                    Les retraités et les retraites > Édition 2026 > Drees       45\n"
    "\f"
    "04     La revalorisation des pensions individuelles\n"
    "     Tableau 1 Revalorisation annuelle des pensions brutes depuis 2014\n"
    "     Lecture > Entre fin 2019 et fin 2024, les pensions de retraite des régimes de base ont augmenté de 2,4 % par an\n"
    "     en moyenne en euros courants.\n"
    "     Sources > CNAV, MSA, RSI, SRE, CNRACL, Agirc-Arrco, Ircantec, RAFP ; Insee, indice des prix à la consommation ;\n"
    "     Drees, EIR 2020, modèle ANCETRE.\n"
    "     6. Les euros courants sont les prix tels qu’ils sont indiqués à une période donnée, ils sont dits « en valeur nominale ».\n"
    "     46                               Les retraités et les retraites > Édition 2026 > Drees\n"
    "\f"
    "                                                          Le niveau des pensions      05\n"
    " Graphique 4 Distribution des montants bruts mensuels de la pension de droit direct\n"
    "(y compris éventuelle majoration pour trois enfants ou plus) des retraités résidant\n"
    "en France\n"
    "4a. Ensemble des retraités, fin 2020\n"
    "dans au moins un régime de base, résidant en France, vivants au 31 décembre 2020.\n"
    "Source > Drees, EIR.\n"
    "4b. Ensemble des retraités ayant effectué une carrière complète, fin 2020\n"
    "Source > Drees, EIR.\n"
    "                    Les retraités et les retraites > Édition 2026 > Drees       63\n"
    "\f"
    "11     Les durées de carrière des retraités et la part des carrières complètes ou incomplètes\n"
    "     Tableau 3 Comparaison des effectifs par tête et en EQCC, selon la génération\n"
    "                              1930 1932 1934 1936 1938 1940 1942 1944 1946 1947 1948 1949 1950 1951 1952 1953\n"
    "     Effectifs de droit direct\n"
    "     Source > Drees, EIR 2020.\n"
    "     112                             Les retraités et les retraites > Édition 2026 > Drees\n"
    "\f"
    "20     Les motivations de départ à la retraite\n"
    "     Tableau 1 Âge de départ à la retraite : souhaits et situation réelle des nouveaux retraités\n"
    "     Source > Drees, CNAV, SRE, CDC, CPRPF, Agirc-Arrco, COR, DSS, enquêtes Motivations de départ à la retraite\n"
    "     2010, 2014, 2017 et 2021.\n"
    "     176                             Les retraités et les retraites > Édition 2026 > Drees\n"
    "\f"
    "22     Les dispositifs de cumul d’une activité avec la retraite\n"
    "     Graphique 1 Évolution des effectifs d’assurés en retraite progressive au régime général\n"
    "     35 000\n"
    "                                                                    31 370\n"
    "     30 000\n"
    "     Source > CNAV, Recueil statistique.\n"
    "     196                             Les retraités et les retraites > Édition 2026 > Drees\n"
)


def test_le_releve_s_arrete_aux_notes_aux_volets_et_aux_en_tetes():
    figures = _module().relever_figures(SUITES)
    assert [(f["fiche"], f["page"], f["nature"], f["numero"], f["titre"], f["sources"])
            for f in figures] == [
        ("04", 45, "Encadré", "1", "Les modalités de revalorisation des pensions de retraite", ""),
        ("04", 46, "Tableau", "1", "Revalorisation annuelle des pensions brutes depuis 2014",
         "CNAV, MSA, RSI, SRE, CNRACL, Agirc-Arrco, Ircantec, RAFP ; Insee, indice des prix "
         "à la consommation ; Drees, EIR 2020, modèle ANCETRE."),
        ("05", 63, "Graphique", "4",
         "Distribution des montants bruts mensuels de la pension de droit direct (y compris "
         "éventuelle majoration pour trois enfants ou plus) des retraités résidant en France",
         "Drees, EIR."),
        ("11", 112, "Tableau", "3",
         "Comparaison des effectifs par tête et en EQCC, selon la génération",
         "Drees, EIR 2020."),
        ("20", 176, "Tableau", "1",
         "Âge de départ à la retraite : souhaits et situation réelle des nouveaux retraités",
         "Drees, CNAV, SRE, CDC, CPRPF, Agirc-Arrco, COR, DSS, enquêtes Motivations de "
         "départ à la retraite 2010, 2014, 2017 et 2021."),
        ("22", 196, "Graphique", "1",
         "Évolution des effectifs d’assurés en retraite progressive au régime général",
         "CNAV, Recueil statistique."),
    ]


SOMMAIRE = (
    " Les effectifs de retraités ........................................ 19\n"
    " Fiche 01 • Les effectifs de retraités de droit direct ............. 20\n"
    " Fiche 11 • Les durées de carrière des retraités et la part des carrières\n"
    "            complètes ou incomplètes ............................... 106\n"
    " Fiche 34 • La retraite supplémentaire d’entreprise ................ 280\n"
    "Annexes  289\n"
    " Annexe 2 • Sources et méthodes .................................... 293\n"
)


def test_le_releve_lit_le_sommaire():
    assert _module().lire_sommaire(SOMMAIRE) == {
        "01": {"titre": "Les effectifs de retraités de droit direct", "page": 20},
        "11": {"titre": "Les durées de carrière des retraités et la part des carrières "
                        "complètes ou incomplètes", "page": 106},
        "34": {"titre": "La retraite supplémentaire d’entreprise", "page": 280},
    }


def test_le_temoin_porte_les_trente_quatre_fiches_et_leurs_figures():
    """Le sommaire de l'édition 2026 compte 34 fiches, de « Les effectifs de
    retraités de droit direct » (page 20) à « La retraite supplémentaire
    d'entreprise » (page 280) ; chacune a au moins un tableau ou un graphique,
    et chaque figure, sa source."""
    releve = json.loads(TEMOIN.read_text(encoding="utf-8"))
    assert releve["sha256"] == _jeux()["drees_panorama_retraites_2026"]["sha256"]
    assert releve["pages"] == 314  # pdfinfo, pages blanches comprises
    fiches = releve["fiches"]
    assert sorted(fiches) == [f"{n:02d}" for n in range(1, 35)]
    assert fiches["01"]["titre"] == "Les effectifs de retraités de droit direct"
    assert fiches["01"]["page"] == 20
    assert fiches["34"]["titre"] == "La retraite supplémentaire d’entreprise"
    assert fiches["34"]["page"] == 280
    for numero, fiche in fiches.items():
        assert fiche["figures"], f"fiche {numero} : aucune figure relevée"
        for figure in fiche["figures"]:
            assert figure["sources"], f"fiche {numero}, {figure['nature']} {figure['numero']}"
    premiere = fiches["01"]["figures"][0]
    assert (premiere["nature"], premiere["numero"], premiere["page"]) == ("Tableau", "1", 21)


def test_le_panorama_2026_se_recupere_par_son_miroir():
    """Le site de la DREES refuse le cloud ; l'UNSA Retraités sert le PDF,
    créé par la DREES le 12 octobre 2026, depuis le 14 octobre."""
    jeu = _jeux()["drees_panorama_retraites_2026"]
    assert jeu["blocage"] == "refus"
    assert jeu["miroir"] == (
        "https://retraites.unsa.org/IMG/pdf/les_retraites_et_les_retraites_-_edition_2026-1.pdf")
    assert jeu["fichier_local"] == "les_retraites_et_les_retraites_-_edition_2026-1.pdf"
    assert jeu["sha256"] == "9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be"


#: Le dossier où la DREES sert l'ouvrage et ses classeurs.
DREES = "https://drees.solidarites-sante.gouv.fr/sites/default/files/2026-10/"


def test_le_pdf_du_miroir_est_celui_de_la_drees():
    """Depuis un poste, la page de la DREES mène à l'ouvrage par deux adresses,
    le bouton de son en-tête et l'onglet « Ouvrage » ; l'une et l'autre rendent
    le fichier de l'UNSA, octet pour octet. Ses mentions légales concèdent la
    reproduction et la diffusion de ses publications, et chacune de ses pages
    les place sous la licence ouverte Etalab 2.0, « sauf mention contraire » :
    le PDF n'en porte aucune. L'UNSA le servant, la release n'a pas à le porter."""
    source_locale = _source_locale()
    jeu = _jeux()["drees_panorama_retraites_2026"]
    assert jeu["document"] == (
        DREES + "Les%20retrait%C3%A9s%20et%20les%20retraites%20-%20%C3%89dition%202026.pdf")
    assert jeu["sha256"] == "9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be"
    assert source_locale.rediffusion(jeu) == "libre"
    texte = " ".join(jeu["rediffusion"]["texte"].split())
    assert "Sauf mention contraire, tous les contenus de ce site sont sous licence etalab-2.0" in texte
    assert "concède des droits de reproduction et de diffusion" in texte
    assert jeu["rediffusion"]["lu_le"] == "2026-11-02"
    assert not source_locale.a_publier([jeu])


#: Les classeurs que la page sert hors des fiches, et ce qui les nomme chez elle.
CLASSEURS_HORS_FICHES = {"vue_d_ensemble.xlsx": "Vue%20d%27ensemble%20-%20",
                         "annexe_02.xlsx": "RR2026%20-%20Annexe%20%2002%20-%20"}


def test_les_classeurs_des_fiches_se_recuperent_par_la_release():
    """Chaque fiche renvoie au « fichier Excel associé à cette fiche » ; la page
    de la DREES en sert trente-six, un par fiche, un pour la vue d'ensemble et
    un pour l'annexe 2, et les refuse au cloud comme elle refuse l'ouvrage. Le
    dépôt les sert tels quels, en une archive sur la release
    ``documents-apportes`` : le manifeste dit de chacun son adresse à la DREES
    et l'empreinte du fichier qu'elle sert. L'archive n'ayant pas d'adresse à
    la DREES, le workflow mensuel n'a rien à retélécharger."""
    source_locale = _source_locale()
    jeu = _jeux()["drees_panorama_retraites_2026_classeurs"]
    assert jeu["blocage"] == "refus"
    assert jeu["fichier_local"] == "drees_panorama_retraites_2026_classeurs.zip"
    assert jeu["miroir"] == source_locale.url_publiee(jeu["fichier_local"])
    assert re.fullmatch(r"[0-9a-f]{64}", jeu["sha256"])
    assert source_locale.rediffusion(jeu) == "libre"
    assert not source_locale.a_publier([jeu])
    fiches = json.loads(TEMOIN.read_text(encoding="utf-8"))["fiches"]
    contenu = jeu["contenu"]
    assert sorted(contenu) == sorted([f"fiche_{numero}.xlsx" for numero in fiches]
                                     + list(CLASSEURS_HORS_FICHES))
    attendus = {f"fiche_{numero}.xlsx": f"RR2026%20-%20Fiche%20{numero}%20-%20" for numero in fiches}
    for nom, classeur in contenu.items():
        prefixe = DREES + {**attendus, **CLASSEURS_HORS_FICHES}[nom]
        assert classeur["document"].startswith(prefixe) and classeur["document"].endswith(".xlsx"), nom
        assert re.fullmatch(r"[0-9a-f]{64}", classeur["sha256"]), nom
    assert contenu["fiche_01.xlsx"] == {
        "document": DREES + "RR2026%20-%20Fiche%2001%20-%20Les%20effectifs%20de%20retraite%CC%81s"
                            "%20de%20droit%20direct.xlsx",
        "sha256": "64513052449b30c4bdad1fd7a00ea94193d2ea16ed8a433f3a959dac1223bfaf",
    }


STATUTS ={"au_depot", "a_tirer", "a_confronter", "hors_champ"}


def test_chaque_fiche_a_son_statut_au_suivi():
    """« Exploité en entier » : aucune fiche du relevé n'échappe au suivi, et
    chacune dit ce que le dépôt en a déjà et ce qu'il en tirera."""
    fiches = json.loads(TEMOIN.read_text(encoding="utf-8"))["fiches"]
    suivi = yaml.safe_load(SUIVI.read_text(encoding="utf-8"))["fiches"]
    assert sorted(suivi) == sorted(fiches)
    jeux = _jeux()
    for numero, ligne in suivi.items():
        assert ligne["titre"] == fiches[numero]["titre"], numero
        assert ligne["statut"] in STATUTS, f"fiche {numero} : statut {ligne['statut']}"
        assert len(" ".join(str(ligne["a_tirer"]).split())) > 40, (
            f"fiche {numero} : « a_tirer » n'apprend rien")
        for ident in ligne.get("au_depot", []):
            assert ident in jeux, f"fiche {numero} : {ident} n'est pas au manifeste"
        if ligne["statut"] == "au_depot":
            assert ligne.get("au_depot"), f"fiche {numero} : au dépôt, mais par quel jeu ?"
