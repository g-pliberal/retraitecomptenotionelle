"""Le registre des autres modèles tient sa forme, et ses renvois tiennent.

`data/reference/referents.yaml` est le registre que `docs/architecture.md`
(§ 3.4) prévoit : aucun modèle ne fait autorité sur la loi, chacun confirme ou
contredit sur ce qu'il couvre. Ce n'est pas une bibliographie, et ces tests
exigent ce qui fait la différence. Un modèle dit ce dont il dépend, sinon deux
accords qui n'en font qu'un compteraient pour deux confirmations. Il dit ce
que sa licence permet, sinon un code à réciprocité finirait recopié dans un
dépôt sous Apache. Il dit où il a été lu, et quand, sinon la session suivante
relira tout. Et tout modèle que le dépôt nomme ailleurs, dans une fiche ou au
registre des sources, y a sa ligne : la liste se veut exhaustive.
"""

from __future__ import annotations

import csv
import datetime
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from retraite_notionnelle.carriere import Carriere, LigneRelevee
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.contributions_equilibre import charger_contributions_equilibre
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.impot_revenu import charger_baremes_impot_revenu
from retraite_notionnelle.droit import foyer
from retraite_notionnelle.droit.releve import points_de_l_annee
from retraite_notionnelle.impot_revenu import Declarant, Foyer, impot_aux_parametres
from retraite_notionnelle.scenarios.actuel import (
    AgesOuvertureAvantReforme2023, AgesOuvertureAvantSuspension, TableRecouverte)
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
REGISTRE = RACINE / "data" / "reference" / "referents.yaml"

#: Ce que fait le modèle. La différence qui compte est entre ce qui calcule une
#: pension (les trois premières) et ce qui projette des masses ou publie des
#: paramètres : on ne les confronte pas de la même manière.
NATURES = {
    "calculateur", "cas_types", "microsimulation_dynamique",
    "microsimulation_statique", "projection", "parametres", "methode",
}

#: Ce qu'on peut en lire. `documente` : la méthode et les résultats sont
#: publiés, pas le code ; `non_public` : seuls des résultats le sont.
PUBLICATIONS = {"ouvert", "sur_demande", "documente", "non_public"}

#: Ce que sa licence permet au dépôt d'en faire (§ 3.4).
USAGES = {"copier", "executer_a_part", "lire_et_citer", "selon_conditions",
          "resultats_publies"}

#: Ce qu'il confronte : le droit réel du scénario 1, les masses de la page
#: Coût, ou la mécanique des comptes notionnels de la proposition — son
#: arithmétique, jamais ses choix, que le README décide (§ 3.1).
CONFRONTE = {"scenario_1", "cout", "proposition"}

CHAMPS_EXIGES = (
    "id", "nom", "auteur", "nature", "publication", "licence", "usage",
    "confronte", "couvre", "confrontation", "lu_le", "lu_dans",
)
CHAMPS_CONNUS = set(CHAMPS_EXIGES) | {
    "pays", "code", "documentation", "version", "depend_de", "ecarts",
    "fait_mieux", "bilan", "manifeste", "sas", "note",
}
CHAMPS_ECART = ("constat", "tranche", "preuve")

#: Ce qu'un autre modèle fait mieux que le dépôt, et ce qu'on en a fait. Le
#: propriétaire veut le dépôt « meilleur en tous points » (action 138) : chaque
#: point vérifié reste au registre jusqu'à être repris, tranché ou écarté. Le
#: 14 octobre 2026, il a coupé : le léger et le nul se déclarent sans se faire.
CHAMPS_FAIT_MIEUX = ("quoi", "preuve", "etat")
ETATS_FAIT_MIEUX = {"a_reprendre", "a_trancher", "repris", "ecarte", "coupe"}

#: Les licences à réciprocité : un code qui les porte s'exécute à part, et
#: seules ses sorties entrent au dépôt (§ 3.4).
RECIPROQUES = re.compile(r"\b(A?GPL|LGPL|EUPL|CeCILL(?!-[BC])|BY-SA|ODbL)", re.I)


@pytest.fixture(scope="module")
def referents() -> list[dict]:
    return yaml.safe_load(REGISTRE.read_text(encoding="utf-8"))["referents"]


@pytest.fixture(scope="module")
def par_id(referents) -> dict[str, dict]:
    return {r["id"]: r for r in referents}


def test_chaque_modele_porte_les_champs_exiges(referents):
    for modele in referents:
        manquants = [c for c in CHAMPS_EXIGES if c not in modele]
        assert not manquants, f"{modele.get('id', modele)} : champs manquants {manquants}"
        inconnus = set(modele) - CHAMPS_CONNUS
        assert not inconnus, f"{modele['id']} : champs inconnus {sorted(inconnus)}"


def test_les_identifiants_sont_uniques_et_lisibles(referents):
    identifiants = [r["id"] for r in referents]
    doublons = {i for i in identifiants if identifiants.count(i) > 1}
    assert not doublons, f"identifiants en double : {sorted(doublons)}"
    for identifiant in identifiants:
        assert re.fullmatch(r"[a-z0-9_]+", identifiant), identifiant


def test_les_vocabulaires_sont_ceux_du_registre(referents):
    for modele in referents:
        assert modele["nature"] in NATURES, f"{modele['id']} : nature {modele['nature']}"
        assert modele["publication"] in PUBLICATIONS, (
            f"{modele['id']} : publication {modele['publication']}")
        assert modele["usage"] in USAGES, f"{modele['id']} : usage {modele['usage']}"
        confronte = modele["confronte"]
        assert confronte and set(confronte) <= CONFRONTE, (
            f"{modele['id']} : confronte {confronte}")


def test_un_code_ouvert_a_son_adresse_et_un_modele_ferme_n_en_a_pas(referents):
    """`ouvert` veut dire qu'on peut le lire : l'adresse du code est là."""
    for modele in referents:
        if modele["publication"] in {"ouvert", "sur_demande"}:
            assert str(modele.get("code", "")).startswith("https://"), (
                f"{modele['id']} : code {modele['publication']} sans adresse")
        else:
            assert "code" not in modele, (
                f"{modele['id']} : {modele['publication']}, mais une adresse de code")
            assert modele.get("documentation") or modele.get("manifeste"), (
                f"{modele['id']} : ni code, ni documentation, ni résultat au "
                "manifeste — rien ne dit qu'il existe")


def test_la_licence_decide_de_l_usage(referents):
    """La règle du § 3.4, tenue modèle par modèle.

    Un code sous GPL, EUPL ou AGPL s'exécute à part : le copier ferait passer
    le dépôt sous sa licence. Un code sans licence se lit et se cite, sans se
    copier. D'un modèle non public, on n'a que des résultats publiés.
    """
    for modele in referents:
        licence, usage = str(modele["licence"]), modele["usage"]
        if modele["publication"] == "non_public":
            assert usage == "resultats_publies", f"{modele['id']} : {usage}"
            continue
        if modele["publication"] == "ouvert" and RECIPROQUES.search(licence):
            assert usage == "executer_a_part", (
                f"{modele['id']} : sous {licence}, il s'exécute à part ({usage})")
        if usage == "executer_a_part":
            assert RECIPROQUES.search(licence), (
                f"{modele['id']} : exécuté à part, mais sous « {licence} »")
        if modele["publication"] == "ouvert" and licence == "aucune":
            assert usage == "lire_et_citer", f"{modele['id']} : sans licence, {usage}"


def test_un_modele_dit_ou_et_quand_il_a_ete_lu(referents):
    """« Une mémoire n'est pas une source » (`CLAUDE.md`)."""
    for modele in referents:
        assert isinstance(modele["lu_le"], datetime.date), (
            f"{modele['id']} : lu_le {modele['lu_le']!r} n'est pas une date")
        assert modele["lu_dans"], f"{modele['id']} : lu nulle part"
        for adresse in modele["lu_dans"]:
            assert re.match(r"https?://|data/|docs/|tests/|scripts/", adresse), (
                f"{modele['id']} : {adresse!r} n'est ni une adresse ni un fichier du dépôt")


def test_ce_dont_un_modele_depend_est_au_registre(referents, par_id):
    """Deux modèles qui partagent une source ne comptent que pour une
    confirmation : la source partagée doit donc avoir sa ligne."""
    for modele in referents:
        for source in modele.get("depend_de", []):
            assert source != modele["id"], f"{modele['id']} dépend de lui-même"
            assert source in par_id, f"{modele['id']} : dépend de {source}, absent du registre"


def test_un_ecart_dit_qui_avait_raison_et_sa_preuve(referents):
    """§ 3.3 : un écart se tranche par la preuve, et la fiche garde ce qui a
    tranché. Un écart sans preuve est une opinion."""
    for modele in referents:
        for ecart in modele.get("ecarts", []):
            manquants = [c for c in CHAMPS_ECART if not ecart.get(c)]
            assert not manquants, f"{modele['id']} : écart sans {manquants}"


def test_chaque_modele_dit_ce_qu_il_fait_mieux_ou_pourquoi_rien(referents):
    """Le propriétaire a voulu savoir, modèle par modèle, tout ce que le dépôt
    fait de moins bien (le relevé du 4 octobre 2026, action 138) : chaque
    modèle porte son bilan, même quand il ne fait mieux sur rien, sans quoi
    on ne saurait pas s'il a été regardé."""
    for modele in referents:
        assert str(modele.get("bilan", "")).strip(), f"{modele['id']} : sans bilan"


def test_ce_qu_un_modele_fait_mieux_dit_sa_preuve_et_son_chantier(referents):
    """Un avantage n'en est un que lu chez lui : sa preuve. Il dit l'étape de la
    feuille de route qui le reprend (« action.étape »), ou, tranché par le
    propriétaire ou écarté, sa raison ; sans quoi la liste ne dirait pas ce
    qui reste pour que le dépôt soit meilleur en tous points."""
    feuille = "".join((RACINE / "docs" / chemin).read_text(encoding="utf-8")
                      for chemin in ("feuille_de_route.md",
                                     "archives/feuille_de_route.md"))
    actions = set(re.findall(r"^### (\d+)\.", feuille, re.M))
    for modele in referents:
        for point in modele.get("fait_mieux", []):
            manquants = [c for c in CHAMPS_FAIT_MIEUX if not point.get(c)]
            assert not manquants, f"{modele['id']} : point sans {manquants}"
            assert point["etat"] in ETATS_FAIT_MIEUX, (
                f"{modele['id']} : état « {point['etat']} » hors de {sorted(ETATS_FAIT_MIEUX)}")
            if point["etat"] in {"a_reprendre", "repris"}:
                chantier = re.fullmatch(r"(\d+)\.\d+", str(point.get("chantier", "")))
                assert chantier, f"{modele['id']} : « {point['quoi'][:40]}… » sans chantier"
                assert chantier.group(1) in actions, (
                    f"{modele['id']} : l'action {chantier.group(1)} n'est pas à la feuille de route")
            else:
                assert point.get("raison"), (
                    f"{modele['id']} : « {point['quoi'][:40]}… » {point['etat']} sans raison")


def test_un_point_coupe_dit_son_chantier_et_la_fiche_qui_le_declare(referents):
    """La coupe du 14 octobre 2026 (action 138) : un point léger ou nul n'est
    pas fait, mais déclaré. Il garde l'étape d'où il vient ; quand c'est une
    règle, il nomme la fiche de la carte qui le déclare, et celle-ci ne se dit
    pas conforme, puisqu'elle ne le sert pas."""
    fiches = {f.stem: f for f in (RACINE / "data" / "reference" / "regles").rglob("*.yaml")}
    for modele in referents:
        for point in modele.get("fait_mieux", []):
            if point["etat"] != "coupe":
                continue
            assert re.fullmatch(r"\d+\.\d+", str(point.get("chantier", ""))), (
                f"{modele['id']} : « {point['quoi'][:40]}… » coupé sans chantier")
            if point.get("fiche"):
                assert point["fiche"] in fiches, (
                    f"{modele['id']} : la fiche {point['fiche']} n'existe pas")
                etat = yaml.safe_load(fiches[point["fiche"]].read_text(encoding="utf-8"))["etat"]
                assert etat != "conforme", (
                    f"{modele['id']} : la fiche {point['fiche']} se dit conforme")


def test_les_renvois_au_manifeste_et_au_registre_des_sources_existent(referents):
    manifeste = yaml.safe_load(
        (RACINE / "data" / "sources.yaml").read_text(encoding="utf-8"))["institutions"]
    jeux = {jeu["id"] for institution in manifeste.values()
            for jeu in institution.get("jeux", [])}
    sas = yaml.safe_load(
        (RACINE / "data" / "sources_a_explorer.yaml").read_text(encoding="utf-8"))["sources"]
    lignes = {s["id"] for s in sas}
    for modele in referents:
        inconnus = [j for j in modele.get("manifeste", []) if j not in jeux]
        assert not inconnus, f"{modele['id']} : {inconnus} absents de data/sources.yaml"
        inconnues = [s for s in modele.get("sas", []) if s not in lignes]
        assert not inconnues, (
            f"{modele['id']} : {inconnues} absentes de data/sources_a_explorer.yaml")


def test_tout_code_du_registre_des_sources_est_un_modele_du_registre(referents):
    """Le registre des sources range un modèle en `code` ; celui-ci dit ce
    qu'il vaut. Une ligne `code` que personne ne rattache serait un modèle
    sorti de la liste exhaustive."""
    sas = yaml.safe_load(
        (RACINE / "data" / "sources_a_explorer.yaml").read_text(encoding="utf-8"))["sources"]
    rattachees = {s for modele in referents for s in modele.get("sas", [])}
    orphelines = sorted(s["id"] for s in sas
                        if s["nature"] == "code" and s["id"] not in rattachees)
    assert not orphelines, f"modèles du registre des sources sans ligne ici : {orphelines}"


def test_tout_modele_qu_une_fiche_nomme_est_au_registre(par_id):
    """Le champ `referents` d'une fiche dit sa correspondance avec chaque autre
    modèle (contrat de la fiche) : il le nomme par son identifiant d'ici."""
    for chemin in sorted((RACINE / "data" / "reference" / "regles").rglob("*.yaml")):
        fiche = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        if not isinstance(fiche, dict):
            continue
        inconnus = [m for m in fiche.get("referents") or {} if m not in par_id]
        assert not inconnus, (
            f"{chemin.relative_to(RACINE)} : {inconnus} absents de "
            "data/reference/referents.yaml")


# ---- Ce que les modèles confrontés par leurs paramètres ont donné ----------
#
# Lu chez eux, à la version que leur ligne nomme (`version`), et rapporté à la
# donnée du dépôt qui dit la même règle, la même année ou pour la même
# génération. Le registre les dit d'accord avec le dépôt, sauf les écarts
# qu'il déclare : ces tests le tiennent. Une donnée du dépôt qui change remet
# leur accord en question, et leur ligne se relit (action 137, la remise à plat
# du 22 octobre 2026).

LEGISLATION = RACINE / "data" / "reference" / "legislation"


def _csv(chemin: Path) -> list[dict]:
    lignes = [ligne for ligne in chemin.read_text(encoding="utf-8").splitlines()
              if ligne and not ligne.startswith("#")]
    return list(csv.DictReader(lignes))


def _par_generation(fichier: str, colonne: str):
    """La valeur d'une génération, celle de la dernière borne qui la précède :
    1961.667 dit les nés à compter du 1er septembre 1961."""
    bornes = sorted((float(ligne["generation"]), float(ligne[colonne]))
                    for ligne in _csv(LEGISLATION / fichier))
    return lambda generation: [v for b, v in bornes if b <= generation][-1]


def _de_l_annee(serie: list[dict], annee: int) -> dict:
    """La marche d'une série de l'impôt en vigueur pour les revenus d'une année."""
    return [m for m in serie if m["annee"] <= annee][-1]


@pytest.fixture(scope="module")
def depot() -> dict:
    """Ce que le dépôt porte, sous les noms que les constats ci-dessous lisent."""
    impot = yaml.safe_load((LEGISLATION / "impot_revenu.yaml").read_text(
        encoding="utf-8"))["series"]
    bareme = yaml.safe_load((LEGISLATION / "prelevements_remuneration.yaml").read_text(
        encoding="utf-8"))["pensions"]["bareme_csg"][:3]
    seuils = {int(ligne["annee"]): ligne for ligne in _csv(LEGISLATION / "csg_pensions_seuils.csv")}
    point = {int(ligne["annee"]): float(ligne["valeur"])
             for ligne in _csv(LEGISLATION / "point_indice_fonction_publique.csv")}
    minimum = {(ligne["mesure"], ligne["date"]): float(ligne["valeur"])
               for ligne in _csv(LEGISLATION / "minimum_contributif.csv")}

    def lu(serie: str, annee: int, *champs: str) -> tuple:
        return tuple(_de_l_annee(impot[serie], annee)[c] for c in champs)

    return {
        "seuils_csg_2017": tuple(int(seuils[2017][c]) for c in ("exoneration", "reduit")),
        "seuils_csg_2026": tuple(t["revenu_fiscal_maximum"] for t in bareme),
        "seuils_csg_2026_deux_parts": tuple(
            t["revenu_fiscal_maximum"] + 2 * t["majoration_demi_part"] for t in bareme),
        "majorations_csg_2026": tuple(t["majoration_demi_part"] for t in bareme),
        **{f"abattement_pensions_{a}": lu("deductions", a, "pensions_minimum", "pensions_maximum")
           for a in (2015, 2016, 2022, 2025)},
        **{f"abattement_ages_{a}": lu("abattement_age_invalidite", a, "abattement_plein",
                                      "seuil_plein", "abattement_reduit", "seuil_reduit")
           for a in (2015, 2016, 2025)},
        "decote_2025": lu("decote", 2025, "seuil_celibataire", "seuil_couple"),
        "point_indice_mensuel_2019": (round(point[2019] / 12, 3),),
        "minimum_contributif_majore_mensuel_2019": (
            round(minimum["montant_majore", "2019-01-01"] / 12, 2),),
    }


#: Ce que les modèles du net et de l'impôt portent pour une année, lu chez
#: eux : (modèle, ce que la donnée du dépôt dit sous ce nom, leurs valeurs).
#: Saphir : `7a-Legislation_sociale.sas:118-129` et `7b-Legislation_IR.sas:
#: 346-358` (l'impôt de 2016, sur les revenus de 2015) ; pour l'impôt de 2017, les
#: mêmes montants multipliés par 1,001 et arrondis à l'euro
#: (`9b-Calcul_de_l_impot_sur_le_revenu_2017.sas:33`). ir-catala :
#: `archives_cgi.catala_fr:340-370`, « sous condition année_revenus = 2022 ».
#: EUROMOD : FR.xml, système FR_2026. Retraites 2027 : `params.js:52-64`, ses
#: valeurs de 2026 citées en commentaire. Aurain : `parametres_fiscaux_2026.yaml`.
#: SUD éducation : `static/js/retraites.js:47, 51`, le minimum contributif et le
#: point de son « système actuel », écrits en octobre 2019 ; le point mensuel,
#: 4,686025 €, au millième, comme il l'écrit.
CONSTATS = [
    ("saphir", "seuils_csg_2017", (10996, 14375)),
    ("saphir", "abattement_pensions_2015", (379, 3711)),
    ("saphir", "abattement_pensions_2016", (379, 3715)),
    ("ir_catala", "abattement_pensions_2022", (422, 4123)),
    ("euromod", "seuils_csg_2026", (13048, 17057, 26472)),
    ("euromod", "majorations_csg_2026", (3484, 4555, 7066)),
    ("retraites_2027", "seuils_csg_2026", (13048, 17057, 26472)),
    ("retraites_2027", "seuils_csg_2026_deux_parts", (20016, 26167, 40604)),
    ("retraites_2027", "abattement_ages_2025", (2822, 17670, 1411, 28430)),
    ("retraites_2027", "decote_2025", (897, 1483)),
    ("simulateur_aurain", "majorations_csg_2026", (3484, 4555, 7066)),
    ("simulateur_aurain", "abattement_pensions_2025", (454, 4439)),
    ("simulateur_sud_education", "point_indice_mensuel_2019", (4.686,)),
    ("simulateur_sud_education", "minimum_contributif_majore_mensuel_2019", (695.59,)),
]

#: Les taux de vieillesse du régime général d'EDIFIS, en % : salarié
#: déplafonné et plafonné, employeur déplafonné et plafonné (feuille
#: « Barème » de chaque année, lignes « Assurance vieillesse », au commit
#: `95ef983`).
TAUX_EDIFIS = {
    2015: (0.30, 6.85, 1.80, 8.50), 2016: (0.35, 6.90, 1.85, 8.55),
    **{annee: (0.40, 6.90, 1.90, 8.55) for annee in range(2017, 2024)},
    2024: (0.40, 6.90, 2.02, 8.55), 2025: (0.40, 6.90, 2.02, 8.55),
}

#: L'âge d'ouverture, en mois, et la durée requise, en trimestres, du droit en
#: vigueur, par génération du dépôt — 1961.667 pour les nés à compter du 1er
#: septembre 1961, 1965.25 à compter du 1er avril 1965. Chez Aurain, les
#: bornes de naissance du texte (`baselines_retraites.yaml`, B1, au commit
#: `59b7985`). Chez « Quand pourrai-je partir » (`outil.js:57-102`, au commit
#: `94616bc`), l'année de naissance de 1961 à 2010, son curseur : il dit
#: retenir, pour 1961 et 1965, la règle de la majorité des mois, celle des nés
#: d'avril à décembre pour 1965, mais sert pour 1961 celle des nés de septembre
#: à décembre, l'écart que sa ligne déclare.
AGES_AURAIN = {
    1961.0: (744, 168), 1961.667: (747, 169), 1962: (750, 169), 1963: (753, 170),
    1964: (753, 170), 1965.0: (753, 170), 1965.25: (756, 171), 1966: (759, 172),
    1967: (762, 172), 1968: (765, 172), 1969: (768, 172),
}
AGES_QUAND_PARTIR = {
    1961.667: (747, 169), 1962: (750, 169), 1963: (753, 170), 1964: (753, 170),
    1965.25: (756, 171), 1966: (759, 172), 1967: (762, 172), 1968: (765, 172),
    **{annee: (768, 172) for annee in range(1969, 2011)},
}

#: Les modèles dont ces constats tiennent l'accord : leur ligne nomme la version
#: confrontée, sans quoi le tableau de bord les compterait jamais confrontés.
CONFRONTES_PAR_LEURS_PARAMETRES = (
    {m for m, _, _ in CONSTATS}
    | {"edifis", "simulateur_aurain", "outil_quand_partir", "modele_as", "catala",
       "nosretraites_cas_types"})


@pytest.mark.parametrize("modele, donnee, valeurs", CONSTATS,
                         ids=[f"{m}-{d}" for m, d, _ in CONSTATS])
def test_les_valeurs_d_un_modele_confronte_sont_celles_du_depot(depot, modele, donnee, valeurs):
    assert depot[donnee] == valeurs, (
        f"{modele} : {donnee} vaut {valeurs} chez lui, {depot[donnee]} au dépôt ; "
        "sa ligne du registre se relit")


def test_les_taux_de_vieillesse_d_edifis_sont_ceux_du_depot():
    taux = {(int(ligne["annee"]), ligne["mesure"]): float(ligne["valeur"])
            for ligne in _csv(RACINE / "data" / "reference" / "regimes" / "taux_cotisation_annuels.csv")
            if ligne["regime"] == "regime_general"}
    for annee, attendu in TAUX_EDIFIS.items():
        plafonne, deplafonne = taux[annee, "taux_plafonne"], taux[annee, "taux_deplafonne"]
        salarie = taux[annee, "part_salariale"]
        salarie_deplafonne = taux[annee, "part_salariale_deplafonnee"]
        au_depot = tuple(round(100 * t, 2) for t in (
            deplafonne * salarie_deplafonne, plafonne * salarie,
            deplafonne * (1 - salarie_deplafonne), plafonne * (1 - salarie)))
        assert au_depot == attendu, f"{annee} : {au_depot} au dépôt, {attendu} chez EDIFIS"


@pytest.mark.parametrize("modele, table", [
    ("simulateur_aurain", AGES_AURAIN), ("outil_quand_partir", AGES_QUAND_PARTIR)])
def test_les_ages_et_les_durees_d_un_calculateur_sont_ceux_du_depot(modele, table):
    age = _par_generation("age_ouverture_requis.csv", "age")
    duree = _par_generation("duree_assurance_requise.csv", "trimestres")
    for generation, (mois, trimestres) in table.items():
        au_depot = (round(12 * age(generation)), int(duree(generation)))
        assert au_depot == (mois, trimestres), (
            f"{modele}, {generation} : {(mois, trimestres)} chez lui, {au_depot} au dépôt")


def test_quand_pourrai_je_partir_sert_a_toute_la_generation_1961_la_regle_de_sa_minorite():
    """L'écart que sa ligne déclare : les nés de janvier à août 1961, huit mois
    sur douze, gardent 62 ans et 168 trimestres au dépôt."""
    age = _par_generation("age_ouverture_requis.csv", "age")
    duree = _par_generation("duree_assurance_requise.csv", "trimestres")
    assert (round(12 * age(1961)), int(duree(1961))) == (744, 168) != AGES_QUAND_PARTIR[1961.667]


def test_un_modele_dont_les_valeurs_sont_tenues_ici_nomme_sa_version(par_id):
    for modele in sorted(CONFRONTES_PAR_LEURS_PARAMETRES):
        assert par_id[modele].get("version"), (
            f"{modele} : ses paramètres sont confrontés ici, et sa ligne ne nomme "
            "pas la version confrontée")


# ---- modele-as, rejoué -------------------------------------------------------
# Le paquet npm modele-as 0.1.0 de l'Urssaf (MIT), exécuté à part le 23 octobre
# 2026 sous publicodes 1.10.4 (action 137) : la rémunération brute annuelle d'un
# dirigeant assimilé salarié, au 1er juillet de l'année. Le dépôt, qui saisit ce
# dirigeant en salarié du privé (fiche `un_statut_par_annee`), en valide les
# trimestres et en compte les points Agirc-Arrco, sauf deux erreurs, les siennes,
# que sa ligne du registre déclare. Il arrondit à l'euro le revenu MENSUEL cotisé
# avant de le comparer au seuil : à moins de 6 € d'un seuil, il compte un
# trimestre de trop ou de moins. Et il compte les points de la tranche 1 sur la
# cotisation divisée par 1,27 : 6,197 % de l'assiette, au lieu des 6,20 % du
# taux de calcul.

#: (année, rémunération) : (trimestres, points Agirc-Arrco), chez lui.
MODELE_AS = {
    (2023, 29_538): (4, 97.5348),      # le livret n° 3 de la fédération : 97,58 points
    (2024, 6_990): (3, 22.0639),       # 600 heures du SMIC de 11,65 €, pile
    (2024, 6_990.5): (4, 22.0654),
    (2024, 20_000): (4, 63.1298),
    (2024, 69_368): (4, 345.5237),     # le livret n° 3 : 345,59 points
    (2025, 3_558): (2, 10.9217),       # 6 € sous 300 heures du SMIC de 11,88 €
    (2025, 47_100): (4, 144.5790),     # le plafond de la Sécurité sociale
    (2026, 1_803): (0, 5.5345),        # 150 heures du SMIC de 12,02 €, pile
    (2026, 1_804): (0, 5.5376),
    (2026, 100_000): (4, 584.9109),
    (2026, 500_000): (4, 2_980.5082),  # au-delà de huit plafonds
}

#: Les trimestres de R. 351-9 là où il arrondit : autant que la rémunération
#: annuelle « représente de fois » 150 heures du SMIC du 1er janvier, quatre au
#: plus (LEGIARTI000053335598).
TRIMESTRES_DE_R_351_9 = {(2024, 6_990): 4, (2025, 3_558): 1, (2026, 1_803): 1,
                         (2026, 1_804): 1}

#: Ses paramètres de l'année, qui sont ceux du dépôt : le plafond annuel de la
#: Sécurité sociale et la valeur d'achat du point Agirc-Arrco.
PLAFOND_ET_VALEUR_D_ACHAT = {2023: (43_992, 18.7669), 2024: (46_368, 19.6321),
                             2025: (47_100, 20.1877), 2026: (48_060, 20.1877)}


@pytest.fixture(scope="module")
def simulateur():
    return Simulateur()


@pytest.fixture(scope="module")
def moteur(simulateur):
    return simulateur.scenario_actuel


@pytest.mark.parametrize("annee, remuneration", sorted(MODELE_AS))
def test_modele_as_valide_les_trimestres_du_depot_sauf_pres_d_un_seuil(moteur, annee,
                                                                       remuneration):
    chez_lui = MODELE_AS[annee, remuneration][0]
    attendu = TRIMESTRES_DE_R_351_9.get((annee, remuneration), chez_lui)
    assert moteur.macro.trimestres_valides(remuneration, annee) == attendu, (
        f"modele_as, {annee}, {remuneration} € : {chez_lui} trimestres chez lui, "
        f"{attendu} attendus au dépôt ; sa ligne du registre se relit")


@pytest.mark.parametrize("annee, remuneration", sorted(MODELE_AS))
def test_modele_as_compte_les_points_du_depot_sauf_sur_la_tranche_1(moteur, annee,
                                                                    remuneration):
    """Ses points de la tranche 2 sont ceux du dépôt, à 17 % de l'assiette ;
    ceux de la tranche 1, à 7,87 % / 1,27 au lieu de 6,20 %."""
    plafond, achat = PLAFOND_ET_VALEUR_D_ACHAT[annee]
    chez_lui = MODELE_AS[annee, remuneration][1]
    attendu = chez_lui + min(remuneration, plafond) * (0.062 - 0.0787 / 1.27) / achat
    au_depot = points_de_l_annee(moteur, "salarie_prive_cadre", annee, "complementaire",
                                 remuneration)
    assert au_depot == pytest.approx(attendu, abs=1e-4), (
        f"modele_as, {annee}, {remuneration} € : {chez_lui} points chez lui, "
        f"{au_depot} au dépôt ; sa ligne du registre se relit")


# ---- Catala, rejoué ----------------------------------------------------------
# Les règles de retraite de catala-examples (Apache 2.0), au commit `2694b17`,
# interprétées à part le 24 octobre 2026 par Catala 1.3.0 (action 137), au droit
# de leur date : l'âge d'ouverture que rend `OuvertureDroitsRetraite` à la date
# du calcul ; l'âge du taux plein et celui de l'inaptitude, par l'ascendant que
# son aide au logement compte à charge (R. 823-4, 2°) ; le plafond de l'ASPA,
# par les ressources qui l'y font compter, 1,25 fois ce plafond au plus. Ses
# âges, son taux plein d'avant septembre 2023, son inaptitude et son ASPA de
# D. 815-1 sont ceux du dépôt ; ses erreurs, sa ligne du registre les déclare.


def _generation(naissance: str) -> float:
    """La génération d'une date de naissance, comme `Carriere.generation` :
    l'année et ses mois écoulés, à trois décimales."""
    annee, mois = int(naissance[:4]), int(naissance[5:7])
    return round(annee + (mois - 1) / 12, 3)


#: L'âge d'ouverture, en mois, chez lui, des nés au jour dit : calculé le
#: 31 août 2023, sous la loi de 2010, et le 1er janvier 2024, sous celle de
#: 2023 ; le droit contrefactuel du dépôt qui garde chacune.
AGES_CATALA = {
    "au_31_aout_2023": {
        "1951-06-30": 720, "1951-07-01": 724, "1952-06-15": 729, "1953-06-15": 734,
        "1954-06-15": 739, "1955-01-01": 744, "1961-08-31": 744, "1961-09-01": 744,
        "1963-06-15": 744, "1967-06-15": 744, "1975-06-15": 744},
    "loi_2023_sans_suspension": {
        "1951-06-30": 720, "1951-07-01": 724, "1952-06-15": 729, "1953-06-15": 734,
        "1954-06-15": 739, "1955-01-01": 744, "1961-08-31": 744, "1961-09-01": 747,
        "1961-12-31": 747, "1962-06-15": 750, "1963-06-15": 753, "1964-06-15": 756,
        "1965-06-15": 759, "1966-06-15": 762, "1967-06-15": 753, "1968-01-01": 768,
        "1975-06-15": 768},
}

#: La génération 1967 sous la loi de 2023 : « 13° Soixante-trois ans et neuf
#: mois pour les assurés nés en 1967 » (D. 161-2-1-9, LEGIARTI000047634502),
#: qu'il recopie, et qu'il code 62 ans et 9 mois.
AGE_DE_1967_SOUS_LA_LOI_DE_2023 = 765

#: L'âge du taux plein (L. 351-8, 1°), en mois, chez lui, selon la naissance du
#: demandeur : l'âge de l'ascendant qu'il compte à charge, le 1er juin 2021 et
#: le 1er mars 2024. L'âge légal du demandeur, plus cinq ans avant septembre
#: 2023, plus trois ans après.
TAUX_PLEIN_CATALA = {
    "2021-06-01": {"1951-06-15": 780, "1951-09-15": 784, "1952-06-15": 789,
                   "1953-06-15": 794, "1954-06-15": 799, "1955-01-01": 804,
                   "1980-01-01": 804},
    "2024-03-01": {"1955-01-01": 780, "1960-01-01": 780, "1961-10-15": 783,
                   "1962-06-15": 786, "1963-06-15": 789, "1964-06-15": 792,
                   "1965-06-15": 795, "1966-06-15": 798, "1967-06-15": 789,
                   "1968-01-01": 804, "1985-01-01": 804},
}

#: « l'âge prévu au premier alinéa de l'article L. 161-17-2 augmenté de trois
#: années » (L. 351-8, 1°, LEGIARTI000047452736 et 051289852) : ce premier
#: alinéa dit soixante-quatre ans, et le taux plein vient à 67 ans, en mois.
TAUX_PLEIN_DEPUIS_SEPTEMBRE_2023 = 804

#: L'âge de l'inapte (L. 351-1-5, D. 351-1-14), en mois, chez lui : celui de
#: l'ascendant pensionné qu'il compte à charge le 1er mars 2024.
INAPTITUDE_CATALA = 744

#: Le plafond de l'ASPA d'une personne seule chez lui, à partir du 1er janvier
#: de l'année (du 1er avril en 2018) : D. 815-1, a, qu'il recopie, jusqu'en
#: 2020 ; ensuite l'annuel des circulaires de la Cnav
#: (`autres_sources.catala_fr:31-129`), le seul de 2023 servi encore en 2026.
#: Rejoué en 2021, 2022 et 2023, lu avant.
ASPA_CATALA = {2018: 9_998.40, 2019: 10_418.40, 2020: 10_838.40, 2021: 10_881.75,
               2022: 11_001.44, 2023: 11_533.02}

#: Celui d'un couple d'allocataires, que D. 815-1, b, recopié, fixe et qu'il ne
#: code pas.
ASPA_COUPLE_CATALA = {2018: 15_522.54, 2019: 16_174.59, 2020: 16_826.64}


@pytest.mark.parametrize("droit, dessus", [
    ("au_31_aout_2023", AgesOuvertureAvantReforme2023),
    ("loi_2023_sans_suspension", AgesOuvertureAvantSuspension)])
def test_catala_ouvre_le_droit_a_l_age_du_depot_sauf_en_1967(moteur, droit, dessus):
    """Ses âges sont ceux que le droit contrefactuel du dépôt pose sur l'âge en
    vigueur, comme `ScenarioActuel._sous_le_droit` : la loi de 2010 au 31 août
    2023, celle de 2023 sans la suspension. Sauf 1967, son erreur."""
    ages = TableRecouverte(dessus(moteur.parametres.racine_donnees), moteur.ages_ouverture)
    for naissance, chez_lui in AGES_CATALA[droit].items():
        attendu = (AGE_DE_1967_SOUS_LA_LOI_DE_2023
                   if droit == "loi_2023_sans_suspension" and naissance.startswith("1967")
                   else chez_lui)
        au_depot = round(12 * ages.age(_generation(naissance))[0])
        assert au_depot == attendu, (
            f"catala, {droit}, né le {naissance} : {chez_lui} mois chez lui, {au_depot} "
            f"au dépôt, {attendu} attendus ; sa ligne du registre se relit")


def test_catala_compte_le_taux_plein_du_depot_avant_septembre_2023_et_non_apres(moteur):
    """Avant septembre 2023, l'âge du taux plein de chaque génération est celui
    du dépôt, l'âge légal plus cinq ans. Après, Catala l'abaisse à l'âge légal
    plus trois ans jusqu'à la génération 1967 ; le dépôt le garde à 67 ans."""
    for date, seuils in TAUX_PLEIN_CATALA.items():
        for naissance, chez_lui in seuils.items():
            au_depot = round(12 * moteur.ages_annulation_decote.age(_generation(naissance))[0])
            if date < "2023-09-01" or naissance >= "1968":
                assert au_depot == chez_lui, (
                    f"catala, {date}, demandeur né le {naissance} : {chez_lui} mois chez "
                    f"lui, {au_depot} au dépôt ; sa ligne du registre se relit")
            else:
                assert au_depot == TAUX_PLEIN_DEPUIS_SEPTEMBRE_2023 > chez_lui, (
                    f"catala, {date}, demandeur né le {naissance} : {chez_lui} mois chez "
                    f"lui, {au_depot} au dépôt ; sa ligne du registre se relit")


def test_catala_ouvre_le_droit_de_l_inapte_a_l_age_du_depot(moteur):
    version = moteur.invalidites.version("inaptitude", "2024-03-01")
    assert 12 * version["parametres"]["age"] == INAPTITUDE_CATALA


def test_l_aspa_de_catala_est_celle_du_depot_au_mensuel_arrondi_pres():
    """D. 815-1 jusqu'en 2020, au centime. Ensuite, le dépôt porte douze fois le
    mensuel de la Cnav, l'annuel divisé par douze et tronqué au centime :
    l'approximation que sa fiche déclare (`minimum_vieillesse`), quand Catala,
    comme la Cnav, porte l'annuel."""
    seule = {int(l["annee"]): float(l["valeur"])
             for l in _csv(LEGISLATION / "minimum_vieillesse.csv")}
    couple = {int(l["annee"]): float(l["valeur"])
              for l in _csv(LEGISLATION / "minimum_vieillesse_couple.csv")}
    for annee, chez_lui in ASPA_CATALA.items():
        attendu = chez_lui if annee <= 2020 else 12 * (round(100 * chez_lui) // 12) / 100
        assert seule[annee] == pytest.approx(attendu, abs=0.005), (
            f"catala, ASPA de {annee} : {chez_lui} € chez lui, {seule[annee]} € au dépôt")
    for annee, chez_lui in ASPA_COUPLE_CATALA.items():
        assert couple[annee] == pytest.approx(chez_lui, abs=0.005), (
            f"catala, ASPA d'un couple en {annee} : {chez_lui} € chez lui, "
            f"{couple[annee]} € au dépôt")


# ---- Le simulateur de SUD éducation, rejoué ----------------------------------
# Le « système actuel » du simulateur de SUD éducation (MIT), au commit `eec62c9`,
# exécuté à part sous Node le 24 octobre 2026 (action 137), au droit de sa date :
# ses constantes datent d'octobre 2019, et ses pensions partent de 2020. Pour un
# titulaire, 75 % du dernier traitement, au prorata des trimestres acquis sur les
# requis, multipliés par 1 − 1,25 % × (requis − acquis) (`static/js/retraites.js:
# 150-185`). Le dépôt liquide les mêmes services et le même traitement sous le
# droit au 31 août 2023, les lois de 2010 et de 2014, qui étaient celles de sa
# date : le relevé d'années pleines d'un assuré né un 1er janvier, de
# l'anniversaire du début à celui du départ, et la pension avant le minimum
# garanti (`total_contributif`). Ses pensions sont celles du dépôt, au centime qu'il
# tronque, sauf trois erreurs, les siennes, que sa ligne du registre déclare.

#: (corps, naissance, âges de début et de fin de carrière) : (trimestres requis,
#: acquis, dernier traitement mensuel, pension mensuelle), chez lui. Ses corps :
#: ADJAENES, certifiés, professeurs des écoles, agrégés, SAENES
#: (`content/_index.md:24-33`), ses grilles comprises.
SUD_EDUCATION = {
    ("professeur_des_ecoles", 1960, 22, 62): (167, 160, 3_739.42, 2_451.89),
    ("certifie", 1963, 22, 64): (168, 168, 3_739.42, 2_804.56),
    ("certifie", 1970, 22, 62): (171, 160, 3_739.42, 2_263.33),
    ("agrege", 1975, 20, 63): (172, 172, 4_554.79, 3_416.09),
    ("adjaenes", 1985, 22, 64): (172, 168, 2_108.69, 1_467.50),
    ("saenes", 1998, 24, 67): (172, 172, 2_357.05, 1_767.78),
    ("certifie", 1958, 22, 62): (172, 160, 3_739.42, 2_217.56),
    ("agrege", 1959, 22, 62): (172, 160, 4_554.79, 2_701.09),
    ("adjaenes", 1990, 28, 62): (172, 136, 1_925.94, 628.16),
    ("certifie", 1985, 28, 67): (172, 156, 3_739.42, 2_034.94),
    ("professeur_des_ecoles", 1980, 27, 65): (172, 152, 3_739.42, 1_858.83),
    ("certifie", 1960, 20, 62): (167, 168, 3_739.42, 2_856.62),
    ("agrege", 1975, 20, 65): (172, 180, 4_554.79, 3_932.47),
}

#: Là où il se trompe, le droit de sa date posé à la main : (durée requise,
#: trimestres de décote, trimestres de surcote). L. 161-17-3 (LEGIARTI000028494794,
#: de 2014 à 2023) : « 1° 167 trimestres, pour les assurés nés entre le 1er janvier
#: 1958 et le 31 décembre 1960 », que L. 13, III (LEGIARTI000028498258) applique
#: aux fonctionnaires nés à compter de 1958 ; sa table ne commence qu'à 1960. L. 14,
#: I (LEGIARTI000037200740, de 2018 à 2023) : la décote compte le plus petit des
#: trimestres qui manquent à la durée et de ceux qui séparent l'âge de la limite
#: d'âge, soixante-sept ans, « dans la limite de vingt trimestres » ; il ne compte
#: que les premiers. L. 14, III : la surcote compte les trimestres « au-delà de
#: l'âge » de soixante-deux ans et « en sus » de la durée ; il compte tous ceux qui
#: la dépassent, à un prorata qui dépasse un, quand L. 13, I, borne la pension à
#: 75 % du traitement.
LOI_DE_2019_SUD = {
    ("certifie", 1958, 22, 62): (167, 7, 0),
    ("agrege", 1959, 22, 62): (167, 7, 0),
    ("adjaenes", 1990, 28, 62): (172, 20, 0),               # 36 manquent à la durée
    ("certifie", 1985, 28, 67): (172, 0, 0),                # à la limite d'âge
    ("professeur_des_ecoles", 1980, 27, 65): (172, 8, 0),   # 20 manquent, 8 à 67 ans
    ("certifie", 1960, 20, 62): (167, 0, 0),                # aucun après 62 ans
    ("agrege", 1975, 20, 65): (172, 0, 8),                  # à 180/172 chez lui
}

#: Sa durée requise par année de naissance (`static/js/retraites.js:150-170`) : sa
#: table, de 1960 à 1972, et 172 trimestres pour toute autre année de son menu, de
#: 1958 à 1998.
DUREES_SUD = {1960: 167, **dict.fromkeys(range(1961, 1964), 168),
              **dict.fromkeys(range(1964, 1967), 169), **dict.fromkeys(range(1967, 1970), 170),
              **dict.fromkeys(range(1970, 1973), 171)}


@pytest.fixture(scope="module")
def moteur_2019():
    """Le droit au 31 août 2023 : pour l'âge légal et la durée, celui de 2019."""
    return Simulateur(Parametres().avec(droit_contrefactuel="au_31_aout_2023")).scenario_actuel


def test_sud_education_demande_la_duree_de_2014_sauf_en_1958_et_1959(moteur_2019):
    for naissance in range(1958, 1999):
        chez_lui = DUREES_SUD.get(naissance, 172)
        attendu = 167 if naissance in (1958, 1959) else chez_lui
        au_depot = moteur_2019.durees_requises.trimestres(float(naissance))[0]
        assert au_depot == attendu, (
            f"simulateur_sud_education, né en {naissance} : {chez_lui} trimestres chez "
            f"lui, {au_depot} au dépôt ; sa ligne du registre se relit")


@pytest.mark.parametrize("cas", sorted(SUD_EDUCATION))
def test_sud_education_liquide_le_titulaire_du_depot_sauf_trois_erreurs(moteur_2019, cas):
    corps, naissance, debut, fin = cas
    requis, acquis, traitement, chez_lui = SUD_EDUCATION[cas]
    lignes = [LigneRelevee(annee, "fonctionnaire_etat", 12 * traitement, 4)
              for annee in range(naissance + debut, naissance + fin)]
    carriere = Carriere.depuis_releve(naissance, "H", lignes, float(fin), moteur_2019.macro,
                                      mois_naissance=1, jour_naissance=1)
    resultat = moteur_2019.calculer(carriere)
    au_depot = resultat.total_contributif / 12
    assert resultat.trimestres_valides == acquis
    if cas in LOI_DE_2019_SUD:
        duree, decote, surcote = LOI_DE_2019_SUD[cas]
        attendu = (traitement * 0.75 * min(acquis, duree) / duree
                   * (1 - 0.0125 * decote) * (1 + 0.0125 * surcote))
        assert resultat.trimestres_requis == duree
        assert au_depot == pytest.approx(attendu, abs=0.005) and abs(au_depot - chez_lui) > 1, (
            f"simulateur_sud_education, {cas} : {chez_lui} € chez lui, {au_depot:.2f} € "
            f"au dépôt, {attendu:.2f} € attendus ; sa ligne du registre se relit")
    else:
        assert resultat.trimestres_requis == requis
        assert 0 <= au_depot - chez_lui < 0.01, (
            f"simulateur_sud_education, {cas} : {chez_lui} € chez lui, {au_depot:.2f} € "
            "au dépôt ; sa ligne du registre se relit")


# ---- Nos Retraites, rejoué ---------------------------------------------------
# Le simulateur de cas types de Nos Retraites (sans licence : lu, cité, exécuté à
# part), au commit `5e4abf1`, rejoué sous Node le 24 octobre 2026 (action 137), au
# droit de sa date : son état « now », le droit de janvier 2023 — les lois de 2010
# et de 2014 —, que le dépôt garde au droit contrefactuel `au_31_aout_2023`. Pour
# une carrière continue depuis l'âge du début, moins des années sans validation,
# il dit à chaque âge de 58 à 67 ans si le départ est possible, et sa décote et sa
# surcote (`utils/calculationUtils.js`). Le dépôt liquide la même carrière d'un
# assuré né le dernier jour d'un trimestre : l'âge légal et l'âge du taux plein y
# tombent en fin de trimestre civil, où le décompte de la caisse, en trimestres
# civils (circulaire Cnav 2018-04), égale le sien, en années. Ses réponses sont
# celles du dépôt, sauf les erreurs, les siennes, que sa ligne du registre déclare.

#: Sa table de l'état « now », par année de naissance (`utils/
#: legalParametersByYearOfBirth.json`) : l'âge d'ouverture et l'âge du taux plein,
#: en mois, la durée requise, en trimestres. Sa ligne 1951 est celle des nés du
#: second semestre, qu'il sert à toute l'année.
PARAMETRES_NR = {
    1950: (720, 162, 780), 1951: (724, 163, 784), 1952: (729, 164, 789),
    1953: (734, 165, 794), 1954: (739, 165, 799),
    **{annee: (744, duree, 804) for duree, debut, fin in (
        (166, 1955, 1958), (167, 1958, 1961), (168, 1961, 1964), (169, 1964, 1967),
        (170, 1967, 1970), (171, 1970, 1973), (172, 1973, 2011))
       for annee in range(debut, fin)},
}

#: Les nés avant le 1er juillet 1951 : « Soixante ans » (D. 161-2-1-9,
#: LEGIARTI000025089933), et le taux plein cinq ans plus tard (L. 351-8, 1°,
#: LEGIARTI000028498855).
NES_AVANT_JUILLET_1951 = (720, 163, 780)

#: Les familles de la grille : le sexe, le statut, et le nombre d'enfants, nés aux
#: 25, 28 et 31 ans de la mère. La mère fonctionnaire de l'État, la seule que son
#: menu ouvre au public, a ses deux enfants à 25 et 28 ans.
FAMILLES_NR = {"aucune": ("H", "salarie_prive_non_cadre", 0),
               "mere_privee_1": ("F", "salarie_prive_non_cadre", 1),
               "mere_privee_3": ("F", "salarie_prive_non_cadre", 3),
               "mere_publique_2": ("F", "fonctionnaire_etat", 2)}

#: (naissance, mois de naissance, âge du début, années sans validation, famille,
#: âge du départ) : (départ possible, décote %, surcote %), chez lui, ou
#: ``(False,)`` pour un départ qu'il dit impossible. Né le 31 mars, ou le 30
#: septembre ; les années sans validation posées à 31 ans.
NOS_RETRAITES = {
    (1969, 3, 21, 0, "aucune", 62): (True, 7.5, 0),           # sa saisie par défaut
    (1969, 3, 21, 0, "aucune", 64): (True, 0, 2.5),
    (1975, 3, 22, 0, "mere_privee_3", 62): (True, 0, 0),
    (1980, 3, 17, 0, "aucune", 61): (True, 0, 0),              # carrière longue
    (1953, 3, 21, 0, "aucune", 63): (True, 0, 3.75),
    (1975, 3, 22, 0, "mere_publique_2", 62): (True, 5, 0),
    (1990, 3, 24, 2.5, "mere_privee_1", 63): (True, 20, 0),
    (2005, 3, 20, 0, "aucune", 67): (True, 0, 20),
    (1962, 3, 19, 0, "mere_publique_2", 61): (True, 0, 0),     # carrière longue
    (1951, 9, 21, 0, "aucune", 60): (False,),
    (1950, 3, 18, 2.5, "aucune", 60): (True, 5, 0),
    (1952, 3, 21, 0, "aucune", 61): (True, 5, 0),
    (1951, 3, 21, 0, "aucune", 60): (False,),
    (1953, 3, 23, 2.5, "aucune", 62): (True, 20.8333333333335, 0),
    (1950, 3, 17, 0, "aucune", 58): (True, 0, 0),
    (1952, 3, 18, 0, "aucune", 60): (True, 0, 0),
    (1951, 9, 18, 0, "aucune", 60): (True, 0, 0),
    (1954, 3, 24, 2.5, "mere_publique_2", 62): (True, 18.75, 0),
    (1950, 3, 16, 0, "mere_publique_2", 66): (True, 0, 30),
}

#: Là où il se trompe, le droit de sa date posé à la main : (ouvert, décote %,
#: surcote %), ou ``(False,)`` pour un départ que le droit n'ouvre pas.
LOI_D_AVANT_2023_NR = {
    # R. 351-27, II (LEGIARTI000024113020) : « 1,625 % pour l'assuré né en
    # 1950 », « 1,375 % pour l'assuré né en 1952 » ; il compte 1,25 % à tous.
    (1950, 3, 18, 2.5, "aucune", 60): (True, 4 * 1.625, 0),
    (1952, 3, 21, 0, "aucune", 61): (True, 4 * 1.375, 0),
    # D. 161-2-1-9 : soixante ans avant le 1er juillet 1951 ; sept trimestres
    # manquent aux 163, à 1,5 % chacun.
    (1951, 3, 21, 0, "aucune", 60): (True, 7 * 1.5, 0),
    # R. 351-27, I, 2° : le nombre de trimestres « est éventuellement arrondi au
    # chiffre immédiatement supérieur » ; de 62 ans à 66 ans et 2 mois, 16,67
    # trimestres, soit 17, qu'il compte 16,67.
    (1953, 3, 23, 2.5, "aucune", 62): (True, 17 * 1.25, 0),
    # D. 351-1-1 de 2003 (LEGIARTI000006736521), qui vaut jusqu'en juin 2011 :
    # avant soixante ans, qui a débuté avant seize ou dix-sept ans ; il ouvre
    # 58 ans à tout début avant vingt ans.
    (1950, 3, 17, 0, "aucune", 58): (False,),
    # D. 351-1-1 de 2010 (LEGIARTI000023397567), du 1er juillet 2011 au 31
    # octobre 2012 : à soixante ans, qui a débuté avant dix-huit ans, cinq
    # trimestres avant la fin de cette année-là (D. 351-1-3) ; entré à 18 ans au
    # printemps ou à l'automne, il n'en a que trois, ou un.
    (1952, 3, 18, 0, "aucune", 60): (False,),
    (1951, 9, 18, 0, "aucune", 60): (False,),
    # Article 66, III, de la loi n° 2003-775 (LEGIARTI000006758610) : le droit
    # ouvert en 2015, 1,25 % et la limite d'âge, 66 ans et 7 mois, moins cinq
    # trimestres ; de 62 ans à 65 ans et 4 mois, 13,33 trimestres, soit 14. Il
    # sert à la fonctionnaire la décote du régime général.
    (1954, 3, 24, 2.5, "mere_publique_2", 62): (True, 14 * 1.25, 0),
    # La limite d'âge du sédentaire, 65 ans pour les nés avant le 1er juillet
    # 1951 (décret n° 2011-754, article 3, LEGIARTI000024272411) : radiée à 65
    # ans, sa pension compte vingt trimestres de surcote ; il la laisse
    # surcoter jusqu'à 67 ans.
    (1950, 3, 16, 0, "mere_publique_2", 66): (True, 0, 20 * 1.25),
}


def _carriere_nos_retraites(moteur, naissance, mois, debut, sans_validation, famille,
                            age) -> Carriere:
    """La carrière d'un cas du rejeu : né le dernier jour du mois ``mois``, un
    trimestre par trimestre civil, de l'anniversaire du début à la date d'effet,
    moins ``sans_validation`` années posées à 31 ans (trois ans après le début,
    s'il est plus tardif)."""
    sexe, affiliation, nombre = FAMILLES_NR[famille]
    trimestres = {annee: 4 for annee in range(naissance + debut + 1, naissance + age)}
    trimestres[naissance + debut] = (12 - mois) // 3
    trimestres[naissance + age] = mois // 3
    if sans_validation:
        depuis = naissance + max(debut + 2, 30) + 1
        for annee in range(depuis, depuis + int(sans_validation)):
            trimestres[annee] = 0
        reste = round(4 * (sans_validation - int(sans_validation)))
        if reste:
            trimestres[depuis + int(sans_validation)] = 4 - reste
    lignes = [LigneRelevee(annee, affiliation, 7_500.0 * nombre_de, nombre_de)
              for annee, nombre_de in sorted(trimestres.items()) if nombre_de]
    enfants = [f"{naissance + a}-06-01" for a in (25, 28, 31)[:nombre]]
    return Carriere.depuis_releve(naissance, sexe, lignes, float(age), moteur.macro,
                                  mois_naissance=mois, jour_naissance={3: 31, 9: 30}[mois],
                                  nombre_enfants=nombre, naissances_enfants=enfants)


def test_nos_retraites_a_les_ages_et_les_durees_du_depot_sauf_en_1951(moteur_2019):
    """Sa table de l'état « now » est celle du droit au 31 août 2023, génération
    par génération ; pour 1951, celle des nés du second semestre. Les nés du
    premier semestre partent à 60 ans, et à taux plein à 65."""
    for annee, chez_lui in PARAMETRES_NR.items():
        for generation in ((annee, annee + 0.5) if annee == 1951 else (annee,)):
            attendu = NES_AVANT_JUILLET_1951 if generation == 1951 else chez_lui
            au_depot = (round(12 * moteur_2019.ages_ouverture.age(generation)[0]),
                        moteur_2019.durees_requises.trimestres(generation)[0],
                        round(12 * moteur_2019.ages_annulation_decote.age(generation)[0]))
            assert au_depot == attendu, (
                f"nosretraites_cas_types, génération {generation} : {chez_lui} chez lui, "
                f"{au_depot} au dépôt, {attendu} attendus ; sa ligne du registre se relit")


@pytest.mark.parametrize("cas", sorted(NOS_RETRAITES))
def test_nos_retraites_ouvre_decote_et_surcote_comme_le_depot_sauf_ses_erreurs(
        moteur_2019, cas):
    chez_lui = NOS_RETRAITES[cas]
    attendu = LOI_D_AVANT_2023_NR.get(cas, chez_lui)
    resultat = moteur_2019.calculer(_carriere_nos_retraites(moteur_2019, *cas))
    base = 0.75 if FAMILLES_NR[cas[4]][1] == "fonctionnaire_etat" else 0.5
    taux = resultat.taux_liquidation / base
    au_depot = (resultat.liquidation_ouverte, round(100 * max(0.0, 1 - taux), 6),
                round(100 * max(0.0, taux - 1), 6))
    assert au_depot[:len(attendu)] == pytest.approx(attendu, abs=1e-6), (
        f"nosretraites_cas_types, {cas} : {chez_lui} chez lui, {au_depot} au dépôt, "
        f"{attendu} attendus ; sa ligne du registre se relit")
    if cas in LOI_D_AVANT_2023_NR:
        assert chez_lui[:len(attendu)] != pytest.approx(attendu[:len(chez_lui)], abs=1e-6)


def test_le_droit_au_31_aout_2023_garde_les_trimestres_d_enfant_reputes_cotises(moteur_2019):
    """Le contrefactuel ne change que l'âge légal, la durée requise et les portes
    de la carrière longue : il garde D. 351-1-2-1, qui répute cotisés deux
    trimestres de la majoration pour enfants aux pensions prenant effet depuis le
    1er septembre 2026. La mère née en 1970, entrée à 16 ans, qui n'a cotisé à 61
    ans que 170 des 171 trimestres requis, y part en carrière longue ; le
    simulateur, au droit de janvier 2023, la fait attendre 62 ans, et à sa date il
    a raison. Sans enfant, le dépôt la fait attendre aussi."""
    cas = (1970, 3, 16, 2.5, "mere_privee_1", 61)
    mere = moteur_2019.calculer(_carriere_nos_retraites(moteur_2019, *cas))
    sans_enfant = moteur_2019.calculer(
        _carriere_nos_retraites(moteur_2019, *cas[:4], "aucune", cas[5]))
    assert (mere.liquidation_ouverte, mere.motif_ouverture) == (True, "carriere_longue")
    assert not sans_enfant.liquidation_ouverte


# ---- EDIFIS, rejoué : l'Agirc-Arrco ---------------------------------------------
# Le code R d'EDIFIS (GPL-3.0 : exécuté à part), rejoué sous R 4.3.3 le 24 octobre
# 2026 (action 137), pour le salarié non cadre de ses ménages types, au droit de
# chaque année de ses barèmes. Au commit `95ef983`, celui que sa ligne confrontait :
# `cs_sal` et `cs_emp` (`R/base.R:328-385`) sur la feuille « Barème » de 2015 à
# 2025, que lisent `read_excel` et `modif_df` (`R/bareme.R`). À sa tête, `2fa5bc0`
# (19 octobre 2026), la maquette 2026, refondue :
# `calculVect_PrelevementsSociaux_salaires` (`R/2b calc_PrelevementsSociaux.R`) sur
# `data/baremes.RData`, de 2019, le bas de son curseur, à 2026. Sa retraite
# complémentaire est celle du dépôt — l'Arrco et l'AGFF jusqu'en 2018, les tranches
# 1 et 2, la CEG et la CET depuis —, à deux choses près : il partage les cotisations
# comme la caisse, au centième, quand le dépôt prend 40 et 60 % exacts (le point
# coupé de sa ligne du registre) ; et ses erreurs, que sa ligne déclare.

#: Ses taux de retraite complémentaire, en % : le salarié, puis l'employeur, sous
#: le plafond, au-dessus — jusqu'à trois plafonds avant 2019, huit depuis —, et la
#: CET. Au commit `95ef983`, la feuille « Barème » de chaque année, lignes
#: « Retraites complémentaires » : « Arrco + AGFF » jusqu'en 2018, « Retraite
#: complémentaire + Contribution d'équilibre général » et la CET depuis. À sa tête,
#: chaque taux à part (`tx_sal_AA2_tr1`, `tx_sal_AA2_ceg_tr1`…), les mêmes à chaque
#: mois de 2019 à 2026, réunis ici.
TAUX_AGIRC_ARRCO_EDIFIS = {
    **{("95ef983", annee): ((3.90, 9.00, 0.0), (5.85, 13.45, 0.0)) for annee in range(2015, 2019)},
    **{("95ef983", annee): ((4.01, 9.72, 0.14), (6.01, 14.57, 0.21))
       for annee in range(2019, 2026)},
    **{("2fa5bc0", annee): ((3.15 + 0.86, 8.64 + 1.02, 0.14), (4.72 + 1.29, 12.95 + 1.62, 0.21))
       for annee in range(2019, 2027)},
}

#: Son plafond mensuel de la Sécurité sociale, sur lequel il découpe ses tranches.
PLAFOND_MENSUEL_EDIFIS = {2015: 3_170, 2018: 3_311, 2019: 3_377, 2021: 3_428, 2025: 3_925,
                          2026: 4_005}

#: (version, année, salaire en plafonds) : ce qu'il prélève dans l'année pour la
#: retraite complémentaire, en euros, la part du salarié puis celle de
#: l'employeur — douze fois le mois de son rejeu.
EDIFIS_REJOUE = {
    ("95ef983", 2015, 2): (4_907.16, 7_341.72),
    ("95ef983", 2018, 3): (8_701.31, 13_012.23),
    ("95ef983", 2018, 4): (8_701.31, 13_012.23),     # l'Arrco d'un non-cadre s'arrête à trois
    ("95ef983", 2019, 2): (5_677.41, 8_510.04),
    ("95ef983", 2021, 2): (5_763.15, 8_724.95),
    ("95ef983", 2025, 1): (1_888.71, 2_830.71),      # le plafond, pile : sans CET
    ("95ef983", 2025, 2): (6_664.65, 9_989.91),
    ("95ef983", 2025, 10): (34_924.65, 52_351.65),
    ("2fa5bc0", 2019, 0.5): (812.51, 1_217.75),
    ("2fa5bc0", 2026, 1): (1_994.49, 2_989.33),
    ("2fa5bc0", 2026, 2): (6_704.37, 10_092.60),
    ("2fa5bc0", 2026, 10): (35_098.22, 52_914.06),
}


def _agirc_arrco_au_depot(moteur, annee: int, brut: float) -> tuple[float, float]:
    """Ce que le dépôt prélève pour la retraite complémentaire d'un salarié non
    cadre payé ``brut`` dans l'année, la part du salarié puis celle de l'employeur :
    les cotisations de ses fiches de régime, sur leurs tranches, et les
    contributions d'équilibre (`contributions_equilibre_agirc_arrco.yaml`)."""
    plafond = moteur.macro.plafond_securite_sociale(annee)
    codes = frozenset(moteur.affiliations.regimes("salarie_prive_non_cadre", annee,
                                                  revenu=brut, plafond=plafond))
    salarie = employeur = 0.0
    for code in sorted(codes & {"arrco", "arrco_tranche_2", "agirc_arrco"}):
        for periode in moteur.catalogue[code].periodes_actives(annee):
            bas, haut = periode.bornes_assiette_en_euros(plafond, annee)
            assiette = max(0.0, min(brut, haut) - bas)
            salarie += assiette * periode.taux_cotisation_salarie
            employeur += assiette * periode.taux_cotisation_retraite * (1 - periode.part_salariale)
    for contribution in charger_contributions_equilibre(
            moteur.parametres.racine_donnees).contributions:
        if contribution.due_pour("salarie_prive_non_cadre", codes):
            part = contribution.montant(annee, brut, plafond, False, salarie=True)
            salarie += part
            employeur += contribution.montant(annee, brut, plafond, False) - part
    return salarie, employeur


def _ce_qui_l_ecarte_du_depot(version: str, annee: int, brut: float,
                              plafond: float) -> tuple[float, float]:
    """Son écart au dépôt, posé à la main, salarié puis employeur. Depuis 2019, le
    partage de la caisse, 3,15 et 8,64 % au salarié, contre 40 % exacts de 7,87 et
    de 21,59 % (accord du 17 novembre 2017, articles 36 et 38). Au commit
    `95ef983`, la CET (0,14 et 0,21 %, article 37, 2°) prélevée une seconde fois
    sur la tranche 2, pour l'employeur depuis 2021, pour le salarié en 2025. À sa
    tête, la CEG du salarié sur la tranche 2 à 1,02 % au lieu de 1,08 % — 40 % de
    2,70 % (article 37, 1°) —, et la CET due au plafond pile, qu'elle doit
    « excéder », et assise au-delà de huit plafonds, hors des tranches 1 et 2."""
    if annee < 2019:
        return 0.0, 0.0
    tranche_1 = min(brut, plafond) / 100
    tranche_2 = max(0.0, min(brut, 8 * plafond) - plafond) / 100
    salarie = (3.15 - 0.4 * 7.87) * tranche_1 + (8.64 - 0.4 * 21.59) * tranche_2
    employeur = -salarie
    if version == "95ef983" and brut > plafond:
        employeur += 0.21 * tranche_2 * (annee >= 2021)
        salarie += 0.14 * tranche_2 * (annee >= 2025)
    if version == "2fa5bc0":
        salarie += (1.02 - 1.08) * tranche_2
        hors_texte = (brut if brut == plafond else 0.0) + max(0.0, brut - 8 * plafond)
        salarie += 0.14 * hors_texte / 100
        employeur += 0.21 * hors_texte / 100
    return salarie, employeur


@pytest.mark.parametrize("cas", sorted(TAUX_AGIRC_ARRCO_EDIFIS))
def test_les_taux_agirc_arrco_d_edifis_sont_ceux_du_depot_au_centieme(moteur, cas):
    """Ses taux, tranche par tranche, sont ceux que le dépôt prélève, chaque part
    au centième — le dépôt prend 40 % exacts, 4,008 % sous le plafond, quand la
    caisse publie 3,15 + 0,86 = 4,01 % —, sauf, à sa tête, la CEG du salarié sur la
    tranche 2, 1,02 % au lieu de 1,08. Lus au plafond, à deux et à trois plafonds,
    où la CET, due dès qu'il est dépassé, l'est sur tout le salaire."""
    version, annee = cas
    plafond = moteur.macro.plafond_securite_sociale(annee)
    sous_le_plafond, a_deux, a_trois = (
        _agirc_arrco_au_depot(moteur, annee, k * plafond) for k in (1, 2, 3))
    au_depot = []
    for part in (0, 1):
        cet = (a_deux[part] - sous_le_plafond[part] - (a_trois[part] - a_deux[part])) / plafond
        au_dessus = (a_trois[part] - a_deux[part]) / plafond - cet
        au_depot.append(tuple(round(100 * t, 2)
                              for t in (sous_le_plafond[part] / plafond, au_dessus, cet)))
    chez_lui = TAUX_AGIRC_ARRCO_EDIFIS[cas]
    attendu = ((au_depot[0][0], round(au_depot[0][1] - 0.06, 2), au_depot[0][2]), au_depot[1]) \
        if version == "2fa5bc0" else tuple(au_depot)
    assert tuple(tuple(round(t, 2) for t in partie) for partie in chez_lui) == attendu, (
        f"edifis, {version}, {annee} : {chez_lui} chez lui, {tuple(au_depot)} au dépôt ; "
        "sa ligne du registre se relit")


@pytest.mark.parametrize("cas", sorted(EDIFIS_REJOUE))
def test_edifis_preleve_l_agirc_arrco_du_depot_sauf_le_partage_et_ses_erreurs(moteur, cas):
    version, annee, plafonds = cas
    plafond = moteur.macro.plafond_securite_sociale(annee)
    assert plafond == 12 * PLAFOND_MENSUEL_EDIFIS[annee]
    brut = plafonds * plafond
    au_depot = _agirc_arrco_au_depot(moteur, annee, brut)
    ecart = _ce_qui_l_ecarte_du_depot(version, annee, brut, plafond)
    attendu = tuple(d + e for d, e in zip(au_depot, ecart))
    assert attendu == pytest.approx(EDIFIS_REJOUE[cas], abs=0.006), (
        f"edifis, {cas} : {EDIFIS_REJOUE[cas]} chez lui, {au_depot} au dépôt, écart "
        f"déclaré {ecart} ; sa ligne du registre se relit")


def test_la_ligne_d_edifis_nomme_les_deux_versions_rejouees(par_id):
    """Rejoué au commit que sa ligne confrontait et à sa tête du 19 octobre 2026,
    la maquette 2026, refondue, qui a ses erreurs à elle : sa ligne nomme les deux."""
    version = par_id["edifis"]["version"]
    assert "95ef983" in version and "2fa5bc0" in version, version


# ---- Saphir, rejoué : l'ASPA et l'impôt des pensions de 2017 -------------------
# Les programmes SAS de Saphir (CeCILL 2.1 ; ses paramètres sous Licence Ouverte),
# au commit `7bc72c9`, son seul, rejoués à part le 24 octobre 2026 (action 137)
# au droit de 2017, l'année qu'il représente. SAS n'est pas dans le conteneur :
# ses `%let` sont évalués comme SAS les évalue, et ses étapes transcrites ligne à
# ligne, sous leurs noms — l'ASPA (`12-Prestations_20ans.sas:561-605`), sur les
# paramètres de `7a-Legislation_sociale.sas:56-59, 1500-1511` ; l'abattement de
# 10 % des pensions et celui des personnes âgées ou invalides
# (`8b-Calcul_de_l_impot_sur_le_revenu_2016.sas:599-605, 895-960, 2017-2022`), sur
# ceux de `7b-Legislation_IR.sas:350-351, 396-399`, que l'impôt de 2017 multiplie
# par 1,001 (`9b-Calcul_de_l_impot_sur_le_revenu_2017.sas:33`). Sa règle de l'ASPA
# est celle du dépôt, son barème celui de la caisse ; son abattement des pensions
# de 2017 est celui du dépôt ; ses abattements des revenus d'activité, dans
# l'ASPA, et des personnes âgées, dans l'impôt, sont faux, ce que sa ligne du
# registre déclare.

#: Son ASPA mensuelle d'une personne seule et d'un couple d'allocataires, avant
#: et après la revalorisation du 1er avril 2017 : 800,8 et 1 243,24 €, puis les
#: mêmes multipliées par `tx_revalo`, 1,003, sans arrondi. Il sert sur l'année la
#: moyenne des douze mois, trois puis neuf (`minvi_1p`, `minvi_2p`).
ASPA_MENSUELLE_SAPHIR = {"seule": (800.8, 800.8 * 1.003), "couple": (1_243.24, 1_243.24 * 1.003)}
ASPA_SAPHIR_2017 = {cle: 3 * avant + 9 * apres
                    for cle, (avant, apres) in ASPA_MENSUELLE_SAPHIR.items()}

#: L'ASPA de l'année qu'il sert, rejouée, à un allocataire de 70 ans sans autres
#: ressources que ses pensions : (ses pensions, l'âge et les pensions de son
#: conjoint, s'il en déclare un ; son allocation). Deux allocataires partagent par
#: moitié ce qui manque au couple ; un seul reçoit tout ce qui manque, au plus le
#: montant d'une personne seule.
ASPA_SAPHIR = [
    (0, None, 9_631.2216), (6_000, None, 3_631.2216), (9_000, None, 631.2216),
    (12_000, None, 0.0), (4_000, (70, 3_000), 3_976.2237), (8_000, (70, 6_000), 476.2237),
    (10_000, (70, 5_000), 0.0), (3_000, (60, 2_000), 9_631.2216),
    (5_000, (60, 7_000), 2_952.4475), (9_000, (60, 6_000), 0.0),
]

#: Son abattement des revenus d'activité dans les ressources de l'ASPA :
#: `abat_celib` et `abat_couple`, 0,9 et 1,5 fois le SMIC horaire de 2017,
#: 9,76 €, par 1 820 / 12 heures, au centime — une fois, sur les revenus de
#: l'année. R. 815-29 (LEGIARTI000029968931) le fixe sur trois mois de
#: ressources, 0,9 fois la rémunération mensuelle minimale d'une personne seule :
#: quatre fois sur l'année.
ABATTEMENT_ASPA_SAPHIR = {"seule": 1_332.24, "couple": 2_220.40}

#: Ce qu'il sert, rejoué, à une personne seule de 70 ans : (ses revenus
#: d'activité, ses pensions ; son allocation).
ASPA_SAPHIR_AVEC_ACTIVITE = [(3_000, 5_000, 2_963.4616), (6_000, 3_000, 1_963.4616),
                             (12_000, 0, 0.0)]

#: L'abattement des personnes âgées ou invalides (plein, son plafond, réduit, son
#: plafond) chez lui, pour les revenus de 2015 et de 2016 : `7b-Legislation_IR.sas:
#: 396-399`, multipliés par l'indexation de l'année et arrondis à l'euro le plus
#: proche. Dans le code, les rédactions de l'article 157 bis du code général des
#: impôts que les lois de finances pour 2016 et pour 2017 ont fait écrire
#: (LEGIARTI000032701889 et LEGIARTI000034597178, lues dans l'index LEGI), qui
#: arrondissent « à l'euro supérieur en ce qui concerne les abattements et à la
#: dizaine d'euros supérieure en ce qui concerne les plafonds de revenus ».
ABATTEMENT_AGES_SAPHIR = {2015: (2_346, 14_725, 1_173, 23_724),
                          2016: (2_348, 14_740, 1_174, 23_748)}
ABATTEMENT_AGES_CODE = {2015: (2_348, 14_730, 1_174, 23_730),
                        2016: (2_352, 14_750, 1_176, 23_760)}

#: Des pensionnés seuls de 70 ans, rejoués entre ses plafonds et ceux du code :
#: (revenus de, pensions ; son revenu net global, après 10 %, son abattement des
#: personnes âgées, celui du code).
ABATTEMENT_AGES_REJOUE = {
    (2015, 16_364): (14_728, 1_173, 2_348), (2015, 26_363): (23_727, 0, 1_174),
    (2016, 16_383): (14_745, 1_174, 2_352), (2016, 26_400): (23_760, 0, 1_176)}


class _BaremeDeSaphir:
    """Son barème de l'ASPA de 2017, où le dépôt lit le sien : la moyenne de
    l'année, d'une personne seule et d'un couple, sans les deux étages."""

    def plafond(self, annee):
        return ASPA_SAPHIR_2017["seule"], Fiabilite.HAUTE

    def plafond_couple(self, annee):
        return ASPA_SAPHIR_2017["couple"], Fiabilite.HAUTE

    def deux_etages(self, annee):
        return None


@pytest.mark.parametrize("pensions, conjoint, chez_lui", ASPA_SAPHIR)
def test_l_aspa_de_saphir_est_celle_du_depot_a_bareme_egal(simulateur, pensions, conjoint,
                                                            chez_lui):
    """L'allocation différentielle sous le plafond d'une personne seule ou du
    couple, partagée par moitié ou bornée au montant d'une personne seule : la
    règle du dépôt (`droit/foyer.py`), sur son barème, au dixième de centime."""
    actuel = simulateur.scenario_actuel
    moteur = SimpleNamespace(minimum_vieillesse=_BaremeDeSaphir(), parametres=actuel.parametres,
                             macro=actuel.macro,
                             carrieres_hors_de_france=actuel.carrieres_hors_de_france)
    du_conjoint = None if conjoint is None else {
        "naissance": f"{2017 - conjoint[0]}-07-01", "sexe": "F", "mariage": None,
        "ressources": conjoint[1], "invalidite": None}
    carriere = simulateur.carriere_simple(
        annee_naissance=1947, sexe="H", affiliation="salarie_prive_non_cadre",
        age_liquidation=66.0, age_debut=20.0, niveau_salaire=0.3, conjoint=du_conjoint)
    au_depot = foyer.foyer_et_net(moteur, carriere.personne, "2017-12-31", 2017, pensions,
                                  True, carriere=carriere).minimum_vieillesse
    assert au_depot == pytest.approx(chez_lui, abs=1e-3), (
        f"saphir, ASPA de {pensions} € (conjoint {conjoint}) : {chez_lui} € chez lui, "
        f"{au_depot} € au dépôt ; sa ligne du registre se relit")


def test_le_bareme_de_l_aspa_de_saphir_est_celui_du_depot_au_centime_du_mensuel():
    """Avant et après la revalorisation d'avril 2017, son montant mensuel est celui
    du dépôt au centime, qu'il n'arrondit pas (803,2024 €). Sur l'année, il sert
    trois mois au premier, neuf au second, comme la caisse, à trois centimes près ;
    le dépôt, le montant du 31 décembre, l'approximation que sa fiche déclare
    (`minimum_vieillesse`) : 7,20 € de plus en 2017 pour une personne seule."""
    series = {cle: {int(l["annee"]): float(l["valeur"]) for l in _csv(LEGISLATION / fichier)}
              for cle, fichier in (("seule", "minimum_vieillesse.csv"),
                                   ("couple", "minimum_vieillesse_couple.csv"))}
    servi = {}
    for cle, (avant, apres) in ASPA_MENSUELLE_SAPHIR.items():
        mensuel = tuple(round(series[cle][a] / 12, 2) for a in (2016, 2017))
        assert (round(avant, 2), round(apres, 2)) == mensuel, (
            f"saphir, ASPA {cle} : {(avant, apres)} € par mois chez lui, {mensuel} au dépôt")
        servi[cle] = 3 * mensuel[0] + 9 * mensuel[1]
        assert ASPA_SAPHIR_2017[cle] == pytest.approx(servi[cle], abs=0.03)
    assert series["seule"][2017] - servi["seule"] == pytest.approx(7.20, abs=0.03)


@pytest.mark.parametrize("activite, pensions, chez_lui", ASPA_SAPHIR_AVEC_ACTIVITE)
def test_saphir_n_abat_qu_un_trimestre_des_revenus_d_activite_d_une_annee(activite, pensions,
                                                                          chez_lui):
    """Son erreur, que sa ligne déclare : sur les revenus de l'année, l'abattement
    de trois mois. Le dépôt, qui ne compte pas les revenus d'activité dans les
    ressources de l'allocation (fiche `minimum_vieillesse`), n'a pas de règle à
    lui opposer : celle de R. 815-29 est posée à la main."""
    bareme, abattement = ASPA_SAPHIR_2017["seule"], ABATTEMENT_ASPA_SAPHIR["seule"]
    assert abattement == round(0.9 * 9.76 * 35 * 52 / 12, 2)
    une_fois = max(0.0, bareme - max(0.0, activite - abattement) - pensions)
    quatre_fois = max(0.0, bareme - max(0.0, activite - 4 * abattement) - pensions)
    assert chez_lui == pytest.approx(une_fois, abs=1e-3)
    assert activite > abattement and chez_lui < quatre_fois


def test_l_abattement_des_personnes_agees_du_depot_est_celui_du_code_et_non_celui_de_saphir(
        depot):
    """Saphir indexe lui-même les montants de l'année précédente et les arrondit à
    l'euro le plus proche ; le code les porte arrondis à l'euro supérieur, les
    plafonds à la dizaine supérieure, et le dépôt avec lui."""
    for annee, code in ABATTEMENT_AGES_CODE.items():
        assert depot[f"abattement_ages_{annee}"] == code != ABATTEMENT_AGES_SAPHIR[annee], (
            f"{annee} : {depot[f'abattement_ages_{annee}']} au dépôt, {code} au code, "
            f"{ABATTEMENT_AGES_SAPHIR[annee]} chez Saphir")


@pytest.mark.parametrize("cas", sorted(ABATTEMENT_AGES_REJOUE))
def test_saphir_abat_les_personnes_agees_moins_que_le_code_entre_ses_plafonds(cas):
    """Entre ses plafonds et ceux du code, il passe à l'abattement réduit, ou à
    rien, quand le code donne encore le plein, ou le réduit ; le dépôt, celui du
    code. Son 10 % des pensions est celui du dépôt, au même revenu net global."""
    annee, pension = cas
    revenu_net_global, chez_lui, code = ABATTEMENT_AGES_REJOUE[cas]
    baremes = charger_baremes_impot_revenu(RACINE / "data")
    impot = impot_aux_parametres(Foyer(declarants=(Declarant(pensions=pension, age=70),)),
                                 baremes.parametres(annee))
    assert impot.revenu_net_global == revenu_net_global
    assert impot.abattement_age_invalidite == code != chez_lui, (
        f"saphir, revenus de {annee}, {pension} € : {chez_lui} € chez lui, "
        f"{impot.abattement_age_invalidite} € au dépôt, {code} € au code")


def test_la_ligne_de_saphir_dit_l_ecart_de_son_abattement_des_personnes_agees(par_id):
    """L'écart que le rejeu trouve est au registre, avec les rédactions du code
    qui le tranchent."""
    preuves = " ".join(e["preuve"] for e in par_id["saphir"].get("ecarts", []))
    assert "LEGIARTI000032701889" in preuves and "LEGIARTI000034597178" in preuves


def test_le_tableau_de_bord_dit_combien_d_ecarts_sont_chez_les_modeles_confrontes(referents):
    """L'état (§ 3.4) compte les modèles confrontés, puis les écarts : ceux du
    registre ne viennent pas tous d'eux, beaucoup d'une lecture d'un modèle
    jamais confronté, et le compte le dit (`scripts/tableau_de_bord.py`)."""
    etat = (RACINE / "docs" / "etat.md").read_text(encoding="utf-8")
    ligne = next(l for l in etat.splitlines() if l.startswith("- **Les autres modèles**"))
    confrontes = [r for r in referents if r.get("manifeste") or r.get("version")]
    total = sum(len(r.get("ecarts", [])) for r in referents)
    chez_eux = sum(len(r.get("ecarts", [])) for r in confrontes)
    assert f"; le registre compte {total} écarts, dont {chez_eux} chez eux." in ligne


def test_le_tableau_de_bord_dit_quand_plus_aucun_modele_n_est_a_confronter_en_premier(referents):
    """Les modèles à confronter en premier — code ouvert, jamais confrontés, sans
    source partagée — se nomment ; quand il n'en reste aucun, la ligne le dit, au
    lieu d'en compter zéro et d'ouvrir une liste vide (action 137, le 24 octobre
    2026, Nos Retraites rejoué, le dernier des treize)."""
    etat = (RACINE / "docs" / "etat.md").read_text(encoding="utf-8")
    ligne = next(l for l in etat.splitlines() if l.startswith("- **Les autres modèles**"))
    premiers = [r for r in referents
                if r["publication"] == "ouvert" and not r.get("depend_de")
                and not (r.get("manifeste") or r.get("version"))
                and "scenario_1" in r["confronte"]]
    assert " : ." not in ligne
    if not premiers:
        assert ("Aucun n'est plus à confronter au scénario 1 en premier : tous ceux dont "
                "le code est ouvert et qui ne dépendent d'aucune autre source du registre "
                "l'ont été.") in ligne
