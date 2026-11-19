"""Les cinq cliquets de la note de décision 0009 : le droit daté dans les
versions de fiche (action 191, étape 1).

« Ne peuvent plus que baisser : les valeurs de repli des renvois de régime ;
les renvois sans texte cité ; les copies d'avant réforme, nommées une à une ;
les versions reprises sans leurs deux preuves ni ce qui manque ; les chiffres
de la loi dans le code des règles. » Chaque nombre est posé ici, à sa valeur
du jour : un test échoue quand il monte, et quand il baisse, pour qu'on
l'abaisse. Aucun ne dit que le droit est juste : ils tiennent la migration.

Ce qui se compte, et comment, est dans ``outils_droit_date.py``.
"""

from __future__ import annotations

import yaml

import outils_droit_date as outils
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.tables_du_droit import FichesDatees
from retraite_notionnelle.noyau import carte

LISTE = outils.RACINE / "tests" / "cliquets_du_droit_date" / "constantes.yaml"

#: Les valeurs de repli écrites à côté d'un renvoi, période par période.
VALEURS_DE_REPLI = 1442
#: Les renvois, en séries, qui ne citent pas le texte qui les fait.
RENVOIS_SANS_TEXTE = 306
#: Les copies d'avant réforme encore dans le dépôt.
COPIES_D_AVANT_REFORME = (
    "age_ouverture_avant_reforme_2023.csv",
    "age_ouverture_avant_suspension.csv",
    "duree_requise_avant_reforme_2023.csv",
    "duree_requise_avant_suspension.csv",
)
#: Les versions que le moteur lit, sans leurs deux preuves ni ce qui manque.
VERSIONS_SANS_PREUVES = 237
#: Les constantes du moteur qui sont du droit à migrer, et celles d'entre
#: elles dont la fiche reste à désigner.
CONSTANTES_A_MIGRER = 113
CONSTANTES_SANS_FICHE = 67

#: Les tables de ``data/reference/`` dont le nom porte ``_avant_`` et qui
#: sont du droit, non une copie posée sur une autre table : le droit d'avant
#: une date. La note les distingue des copies, qu'elle nomme une à une.
TABLES_DU_DROIT_D_AVANT_UNE_DATE = frozenset({
    "duree_requise_avant_soixante_ans.csv",
    "minimum_vieillesse_avant_2007.csv",
    "pension_minimum_avant_1983.csv",
    "plafond_assujettissement_avant_1947.csv",
    "salaire_validant_trimestre_avant_1972.csv",
    "taux_retenue_avant_1946.csv",
})

#: Pourquoi une constante datée n'est pas du droit des retraites à migrer.
RAISONS = {
    "impot": "une règle ou un barème de l'impôt sur le revenu",
    "saisie": "une borne, un défaut ou une monnaie de la saisie et du relevé lu",
    "reglage": "un réglage par défaut du simulateur ou de la proposition",
    "projection": "l'ancrage d'une carrière type ou d'une projection",
    "remuneration": "la rémunération des agents publics, hors de la pension",
    "technique": "une sentinelle, sans valeur de droit",
}


def _baisse_seulement(nombre: int, pose: int, quoi: str) -> None:
    assert nombre <= pose, f"{nombre} {quoi}, le cliquet en admet {pose} : il ne peut que baisser"
    assert nombre == pose, f"{nombre} {quoi}, et le cliquet en admet encore {pose} : l'abaisser"


# --- Ce que le relevé compte, sur des cas fabriqués ------------------------

def test_un_renvoi_se_compte_en_series_et_garde_sa_valeur_de_repli():
    """Le même champ qui renvoie à la même fiche de période en période est un
    renvoi ; il en commence un autre quand il change de fiche, ou reprend
    après une période qui ne renvoie pas. La valeur de repli se compte à
    chaque période qui l'écrit à côté de son renvoi."""
    periodes = [
        {"debut": 1930, "age_ouverture": 55},
        {"debut": 2008, "age_ouverture": 60, "age_ouverture_par_generation": "age_legal_par_generation"},
        {"debut": 2011, "age_ouverture": 60, "age_ouverture_par_generation": "age_legal_par_generation"},
        {"debut": 2014, "age_ouverture": 62},
        {"debut": 2016, "age_ouverture_par_generation": "age_legal_par_generation",
         "bareme_decote": "decote_fonction_publique"},
        {"debut": 2020, "age_ouverture_par_generation": "age_legal_par_generation",
         "bareme_decote": "decote_regimes_speciaux"},
    ]
    series = outils.renvois([("fictif", periodes)])
    assert sorted((s["champ"], s["fiche"], s["debut"]) for s in series) == [
        ("age_ouverture_par_generation", "age_legal_par_generation", 2008),
        ("age_ouverture_par_generation", "age_legal_par_generation", 2016),
        ("bareme_decote", "decote_fonction_publique", 2016),
        ("bareme_decote", "decote_regimes_speciaux", 2020),
    ]
    assert outils.valeurs_de_repli([("fictif", periodes)]) == [
        ("fictif", 2008, "age_ouverture"), ("fictif", 2011, "age_ouverture")]


def test_le_releve_prend_les_dates_du_code_et_laisse_les_libelles():
    """Une constante nommée est datée par un ``DateMois``, une date entière ou
    une année, jusqu'au bout de sa déclaration ; une statique posée après sa
    classe aussi. Un commentaire, un libellé, une constante sans date ne
    comptent pas. Hors des constantes, chaque année écrite dans le code se
    compte, par année."""
    source = """
/** Depuis 1999, d'après la circulaire de 2003. */
export const SURCOTE_DEPUIS = new DateMois(2004, 1);
const LIBELLE = "la pension d'avant le 31 mai 1983";
const BASCULE = "2023-09-01";
const TAUX = 0.0125;
export const GENERATION = 1961.667;
const TABLE = [
  [1, "un"],
  [2, "deux"],
  [3, "trois"],
  [4, "quatre"],
  [5, "cinq"],
  [6, "six"],
  [7, "sept"],
  [new DateMois(2015, 3), "huit"],
];
class Minimum {
  static PLANCHER = 1975;
  montant(annee) {
    // l'année 1990 n'y change rien
    if (annee >= 1998 && annee < 2026) return `depuis ${annee}, et non 2001`;
    return annee === 1998 ? 1 : 0;
  }
}
Minimum.ANNEE_GEL = 2004;
"""
    assert outils.releve_d_une_source(source) == {
        "SURCOTE_DEPUIS": 1, "BASCULE": 1, "GENERATION": 1, "TABLE": 1, "PLANCHER": 1,
        "Minimum.ANNEE_GEL": 1, "1998": 2, "2026": 1}


# --- Les cinq cliquets, sur le dépôt ---------------------------------------

def test_les_valeurs_de_repli_des_renvois_ne_peuvent_que_baisser():
    """Un renvoi est le droit du régime à sa date, et perd sa valeur de repli
    (note 0009, « Le fichier de régime garde son droit propre et ses
    renvois ») ; une valeur ne se retire qu'une fois montrée morte (son
    rectificatif du 19 novembre)."""
    ecrites = outils.valeurs_de_repli(outils.periodes_des_regimes())
    _baisse_seulement(len(ecrites), VALEURS_DE_REPLI, "valeurs de repli à côté d'un renvoi")


def test_les_renvois_sans_texte_cite_ne_peuvent_que_baisser():
    """« Chaque renvoi […] prend la date du texte qui la fait, au jour et non à
    l'année, et cite ce texte. » Un renvoi de plus naît donc cité."""
    series = outils.renvois(outils.periodes_des_regimes())
    sans_texte = [s for s in series if outils.texte_cite(s) is None]
    _baisse_seulement(len(sans_texte), RENVOIS_SANS_TEXTE, "renvois sans texte cité")


def test_les_copies_d_avant_reforme_ne_peuvent_que_partir():
    """Les copies d'avant réforme se nomment une à une, et non par leur
    suffixe, que portent aussi des tables d'avant une date qui sont du droit :
    toute table dont le nom porte ``_avant_`` est l'une ou l'autre."""
    trouvees = {chemin.name for chemin in (RACINE_DONNEES / "reference").rglob("*_avant_*.csv")}
    inconnues = trouvees - set(COPIES_D_AVANT_REFORME) - TABLES_DU_DROIT_D_AVANT_UNE_DATE
    assert not inconnues, (
        f"{sorted(inconnues)} : une table du droit d'avant une date se déclare dans "
        "TABLES_DU_DROIT_D_AVANT_UNE_DATE ; une copie d'avant réforme ne naît plus, "
        "le droit daté va dans les versions de sa fiche")
    parties = set(COPIES_D_AVANT_REFORME) - trouvees
    assert not parties, f"{sorted(parties)} : partie(s), à retirer de COPIES_D_AVANT_REFORME"
    assert not TABLES_DU_DROIT_D_AVANT_UNE_DATE - trouvees


def _a_ses_deux_preuves(version: dict) -> bool:
    """La lecture du texte et l'exemple officiel. La première se lit ici au
    statut ``lue`` et aux textes que la version cite ; la seconde, à un
    exemple officiel au moins."""
    lue = version.get("statut", "lue") == "lue" and bool(version.get("textes"))
    exemples = version.get("exemples")
    return lue and isinstance(exemples, list) and bool(exemples)


def _dit_ce_qui_manque(version: dict) -> bool:
    """Ce qui manque à l'une ou l'autre preuve, dit par la version. « Une
    version cite ce qu'elle a, et son statut ce qui manque » (note 0009, « Ce
    qui reste ouvert ») : faute du texte, elle est ``supposee`` et son
    hypothèse le dit ; faute d'exemple, elle écrit « aucun trouvé » et ce qui
    a été cherché, où et quand, dans ``exemples_cherches``, que le contrat de
    la fiche porte depuis l'étape 2 du domaine du cumul, la première à
    reprendre des fiches (``data/reference/contrats/fiche.yaml``). Une
    version qui ne dit rien de l'une des deux reste comptée."""
    def dit(texte) -> bool:
        return isinstance(texte, str) and bool(texte.strip())

    lue = version.get("statut", "lue") == "lue" and bool(version.get("textes"))
    exemples = version.get("exemples")
    exemple = isinstance(exemples, list) and bool(exemples)
    le_texte = lue or (version.get("statut") == "supposee" and dit(version.get("hypothese")))
    l_exemple = exemple or (exemples == "aucun trouvé" and dit(version.get("exemples_cherches")))
    return le_texte and l_exemple and not (lue and exemple)


def test_une_version_sans_exemple_dit_ce_qui_a_ete_cherche():
    """« Aucun trouvé » ne suffit pas : la version dit aussi ce qui a été
    cherché. Un exemple officiel et un texte lu font les deux preuves."""
    sans_rien = {"statut": "lue", "textes": [{"id": "LEGIARTI000000000001"}],
                 "exemples": "aucun trouvé"}
    assert not _a_ses_deux_preuves(sans_rien) and not _dit_ce_qui_manque(sans_rien)
    assert not _dit_ce_qui_manque({**sans_rien, "exemples_cherches": "  "})
    assert _dit_ce_qui_manque({**sans_rien, "exemples_cherches": "la fiche F13243, le 19 novembre 2026"})
    assert _a_ses_deux_preuves({**sans_rien, "exemples": ["un_exemple"]})
    # Une version supposée dit par son hypothèse ce qui manque au texte ; il
    # lui faut encore son exemple, ou ce qui a été cherché.
    supposee = {"statut": "supposee", "hypothese": "aucun texte général avant 2014",
                "exemples": "aucun trouvé"}
    assert not _dit_ce_qui_manque(supposee)
    assert _dit_ce_qui_manque({**supposee, "exemples": ["un_exemple"]})
    assert _dit_ce_qui_manque({**supposee, "exemples_cherches": "la circulaire Cnav 2015/8"})
    assert not _dit_ce_qui_manque({**supposee, "hypothese": "", "exemples": ["un_exemple"]})


def test_les_versions_lues_par_le_moteur_sans_leurs_preuves_ne_peuvent_que_baisser():
    """« Une version que l'action 191 reprend a les deux, ou "aucun trouvé"
    avec ce qui a été cherché. » Les versions reprises sont celles des fiches
    que le moteur lit par leurs versions (``FichesDatees.NOMS``) : une fiche
    qui y entre apporte ses versions, qui naissent donc prouvées."""
    fiches = carte.fiches()
    sans = [(nom, version["id"]) for nom in FichesDatees.NOMS if nom in fiches
            for version in fiches[nom].get("versions") or []
            if isinstance(version, dict)
            and not _a_ses_deux_preuves(version) and not _dit_ce_qui_manque(version)]
    _baisse_seulement(len(sans), VERSIONS_SANS_PREUVES,
                      "versions lues par le moteur sans leurs deux preuves ni ce qui manque")


def _liste() -> tuple[dict, dict]:
    lue = yaml.safe_load(LISTE.read_text(encoding="utf-8"))
    return lue["constantes"], lue["sans_date"]


def test_chaque_constante_datee_du_moteur_est_classee():
    """Le cinquième cliquet se relève, il ne se choisit pas : toute constante
    datée du moteur hors du site, toute année écrite en clair dans son code,
    est dans la liste, qui dit si elle est du droit à migrer ou pourquoi elle
    n'en est pas. Une fiche que la liste nomme nomme la constante dans son
    champ ``code``."""
    constantes, sans_date = _liste()
    releve = outils.constantes_datees()
    assert sorted(set(releve) - set(constantes)) == [], (
        "à classer dans tests/cliquets_du_droit_date/constantes.yaml : du droit daté "
        "va dans les versions d'une fiche, non dans une constante du moteur")
    assert sorted(set(constantes) - set(releve)) == [], "partie(s) du moteur : à retirer de la liste"
    fiches = carte.fiches()
    for cle, entree in {**constantes, **sans_date}.items():
        fichier, nom = cle.split(" : ")
        assert entree["classe"] in ("droit", "hors"), cle
        if entree["classe"] == "hors":
            assert entree["raison"] in RAISONS, cle
            assert "fiches" not in entree, cle
        else:
            for fiche in entree["fiches"]:
                assert fiche in fiches, (cle, fiche)
                assert outils.nomme_par_la_fiche(fiches[fiche], fichier, nom), (
                    f"{cle} : la fiche {fiche} ne nomme pas cette constante dans son code")
        if nom.isdigit():
            assert entree["lignes"] == releve[cle], (
                f"{cle} : {releve[cle]} occurrence(s) dans le code, la liste en classe "
                f"{entree['lignes']}")
        else:
            assert "lignes" not in entree, cle
    for cle in sans_date:
        fichier, nom = cle.split(" : ")
        source = outils.code_nu((outils.RACINE / fichier).read_text(encoding="utf-8"))
        assert f"const {nom} =" in source, f"{cle} : cette constante n'est plus dans le fichier"
        assert cle not in constantes, cle


def test_les_constantes_du_droit_a_migrer_ne_peuvent_que_baisser():
    """« Les chiffres de la loi quittent le code des règles pour les
    versions. » Le nombre des constantes classées ``droit`` ne peut que
    baisser, et celui des constantes dont la fiche reste à désigner aussi."""
    constantes, sans_date = _liste()
    droit = [entree for entree in {**constantes, **sans_date}.values() if entree["classe"] == "droit"]
    _baisse_seulement(len(droit), CONSTANTES_A_MIGRER, "constantes du droit dans le moteur")
    _baisse_seulement(sum(1 for entree in droit if not entree["fiches"]), CONSTANTES_SANS_FICHE,
                      "constantes du droit sans fiche désignée")
