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

import pytest
import yaml

from retraite_notionnelle.carriere import Carriere, LigneRelevee
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit.releve import points_de_l_annee
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
           for a in (2015, 2022, 2025)},
        "abattement_ages_2025": lu("abattement_age_invalidite", 2025, "abattement_plein",
                                   "seuil_plein", "abattement_reduit", "seuil_reduit"),
        "decote_2025": lu("decote", 2025, "seuil_celibataire", "seuil_couple"),
        "point_indice_mensuel_2019": (round(point[2019] / 12, 3),),
        "minimum_contributif_majore_mensuel_2019": (
            round(minimum["montant_majore", "2019-01-01"] / 12, 2),),
    }


#: Ce que les modèles du net et de l'impôt portent pour une année, lu chez
#: eux : (modèle, ce que la donnée du dépôt dit sous ce nom, leurs valeurs).
#: Saphir : `7a-Legislation_sociale.sas:118-129` et `7b-Legislation_IR.sas:
#: 346-358` (l'impôt de 2016, sur les revenus de 2015). ir-catala :
#: `archives_cgi.catala_fr:340-370`, « sous condition année_revenus = 2022 ».
#: EUROMOD : FR.xml, système FR_2026. Retraites 2027 : `params.js:52-64`, ses
#: valeurs de 2026 citées en commentaire. Aurain : `parametres_fiscaux_2026.yaml`.
#: SUD éducation : `static/js/retraites.js:47, 51`, le minimum contributif et le
#: point de son « système actuel », écrits en octobre 2019 ; le point mensuel,
#: 4,686025 €, au millième, comme il l'écrit.
CONSTATS = [
    ("saphir", "seuils_csg_2017", (10996, 14375)),
    ("saphir", "abattement_pensions_2015", (379, 3711)),
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
    | {"edifis", "simulateur_aurain", "outil_quand_partir", "modele_as", "catala"})


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
def moteur():
    return Simulateur().scenario_actuel


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
