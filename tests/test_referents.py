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
    }


#: Ce que les modèles du net et de l'impôt portent pour une année, lu chez
#: eux : (modèle, ce que la donnée du dépôt dit sous ce nom, leurs valeurs).
#: Saphir : `7a-Legislation_sociale.sas:118-129` et `7b-Legislation_IR.sas:
#: 346-358` (l'impôt de 2016, sur les revenus de 2015). ir-catala :
#: `archives_cgi.catala_fr:340-370`, « sous condition année_revenus = 2022 ».
#: EUROMOD : FR.xml, système FR_2026. Retraites 2027 : `params.js:52-64`, ses
#: valeurs de 2026 citées en commentaire. Aurain : `parametres_fiscaux_2026.yaml`.
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
    {m for m, _, _ in CONSTATS} | {"edifis", "simulateur_aurain", "outil_quand_partir"})


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
