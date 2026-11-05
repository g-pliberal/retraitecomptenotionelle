"""L'Ircantec, lue au droit.

Deux fiches de la carte, lues au droit le 3 novembre 2026 (action 130) dans
les treize rédactions de l'article 16 de l'arrêté du 30 décembre 1970, de sa
publication, le 9 février 1971, à celle du 14 septembre 2023, et dans les
arrêtés qui les ont faites, au Journal officiel : le coefficient
d'anticipation (`coefficient_anticipation_ircantec`), que l'Ircantec applique
aussi aux points de l'IPACTE et de l'IGRANTE qu'elle a repris le 1er janvier
1971, et les deux majorations des points d'après l'âge du taux plein
(`surcote_ircantec`).

Chaque paramètre d'une version porte le nom du champ de la période qui le
porterait, ou celui d'une constante du portage, qui fait foi
(`moteur/js/droit/liquider.js`). Les fiches de régime en portent la valeur
sur chaque année que la version couvre en entier : `regimes/ircantec.yaml`,
ses deux séries de périodes, une par tranche ; `regimes/ipacte.yaml` et
`regimes/igrante.yaml`, une période chacune, que le moteur lit encore après
leur fermeture (`droit/commun.periode_de_liquidation`). Sinon, la fiche
déclare l'écart, et le test qui suit `ECARTS_DECLARES` le tient, cas par cas.
"""

from __future__ import annotations

import csv
import functools
import json
import re
from datetime import date
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte

ANTICIPATION, SURCOTE = "coefficient_anticipation_ircantec", "surcote_ircantec"
LOT = (ANTICIPATION, SURCOTE)
REFERENCE = RACINE_DONNEES / "reference"
RACINE = Path(__file__).resolve().parents[1]
PORTAGE = RACINE / "moteur" / "js" / "droit" / "liquider.js"
#: La création de l'IPACTE, et la dernière année que les confrontations
#: parcourent.
DEBUT, HORIZON = 1951, 2050
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre")

#: Les paramètres que sert le portage, et non une période : le nom de sa
#: constante, ou rien, quand il ne sert pas ce que le paramètre dit — un
#: trimestre de quatre-vingt-dix jours : il compte au trimestre, en mois.
DU_PORTAGE = {
    "coefficient_plancher": "COEFFICIENT_ANTICIPATION_PLANCHER",
    "paliers_d_anticipation": "PALIERS_ANTICIPATION",
    "majoration_par_trimestre_ecoule": "SURCOTE_IRCANTEC_AGE",
    "majoration_par_trimestre_cotise": "SURCOTE_IRCANTEC_DUREE",
    "trimestre_en_jours": None,
}
#: Ce que le moteur lit dans la version même, à la date d'effet de la pension
#: (`baremeIrcantec`, dans le portage), et qu'aucune période n'a donc à
#: porter : la table par année d'âge, jusqu'au 31 août 1983, et, là où elle
#: sert, l'absence des paliers de l'escalier qui la remplace ; l'absence de
#: durée, jusqu'au 1er avril 1983, qui abat à l'âge seul quelle que soit la
#: période — celle de l'IPACTE et de l'IGRANTE porte la durée.
DE_LA_VERSION = {"coefficients_par_annee_d_age"}
#: Le paramètre qu'un test à lui confronte au dépôt : la durée que la seconde
#: table lit de 1983 à 2003.
A_PART = {"duree_de_la_seconde_table_trimestres"}

#: Les versions du coefficient qui couvrent une année entière, et celles
#: d'après le 1er juillet 2011.
COUVRANTES = ("ipacte_et_igrante", "arrete_de_1970", "femmes_de_la_loi_de_1977",
              "escalier_au_trimestre_1983", "retraite_anticipee_2004", "ages_de_2010",
              "compte_de_prevention_2018", "ancres_fixes_2023")
DEPUIS_2011 = ("ages_de_2010", "compte_de_prevention_2018", "ancres_fixes_2023")
FERMES = ("ipacte", "igrante")

#: Ce que le modèle fait autrement que le droit : la fiche, la version, le
#: champ qu'elle lit et que le dépôt porte autrement, les régimes où il le
#: porte autrement (tous, ou le portage, sans eux), et l'article que cite
#: l'approximation qui le déclare. Le modèle liquide l'Ircantec avec la
#: pension de base, jamais avant l'âge d'ouverture de sa période, quand
#: l'article ouvre l'anticipation dix ans avant l'âge du taux plein ; il garde
#: soixante-cinq ans aux points de l'IPACTE et de l'IGRANTE après le
#: 1er juillet 2011 ; il compte en mois
#: le trimestre de la surcote, de quatre-vingt-dix jours depuis 2023.
ECARTS_DECLARES = [
    *[(ANTICIPATION, version, "anticipation_maximale_annees", None, "article 16, I")
      for version in COUVRANTES],
    *[(ANTICIPATION, version, "age_taux_plein_par_generation", FERMES, "L. 351-8")
      for version in DEPUIS_2011],
    (SURCOTE, "precisions_de_2023", "trimestre_en_jours", None, "IV, 3°"),
]


def _versions(nom: str) -> list[dict]:
    versions = carte.fiches()[nom].get("versions") or []
    assert versions, f"{nom} n'a pas de versions"
    return versions


def _version(nom: str, identifiant: str) -> dict:
    return next(v for v in _versions(nom) if v["id"] == identifiant)


def _bornes(version: dict) -> list:
    return version["bornes"]["liquidation.date_effet"]


def _annees_entieres(debut: date | None, fin: date | None) -> range:
    """Les années civiles que [debut, fin) couvre en entier, depuis 1951."""
    premiere = DEBUT if debut is None else debut.year + (debut.timetuple().tm_yday > 1)
    return range(max(premiere, DEBUT), HORIZON + 1 if fin is None else fin.year)


@functools.cache
def _periodes_du_regime(code: str) -> tuple[dict, ...]:
    return tuple(yaml.safe_load((REFERENCE / "regimes" / f"{code}.yaml")
                                .read_text(encoding="utf-8"))["periodes"])


def _periodes(code: str, annee: int) -> list[dict]:
    """Les périodes qui liquident dans ce régime une pension de l'année : les
    deux tranches de l'Ircantec ; la période de la dernière année d'un régime
    fermé, après elle ; rien avant sa première."""
    periodes = _periodes_du_regime(code)
    annee = min(annee, max(9999 if p["fin"] is None else p["fin"] for p in periodes))
    return [p for p in periodes
            if p["debut"] <= annee and (p["fin"] is None or annee <= p["fin"])]


def _constante(nom: str):
    """Une constante du portage, sa valeur littérale."""
    trouve = re.search(rf"^const {nom} = (.+);$", PORTAGE.read_text(encoding="utf-8"), re.M)
    assert trouve, f"le portage ne définit plus {nom}"
    return json.loads(trouve.group(1))


def _valeur(valeur):
    """Une valeur comparable : un barème, liste dans le YAML, en tuple."""
    return tuple(_valeur(v) for v in valeur) if isinstance(valeur, list) else valeur


def _portes(version: dict, champ: str, code: str | None) -> set:
    """Ce que le dépôt porte pour ce champ : la constante du portage, ou les
    valeurs des périodes du régime sur les années que la version couvre en
    entier ; rien si elle n'en couvre aucune."""
    if champ in DU_PORTAGE:
        constante = DU_PORTAGE[champ]
        return {None if constante is None else _valeur(_constante(constante))}
    return {_valeur(periode.get(champ))
            for annee in _annees_entieres(*_bornes(version))
            for periode in _periodes(code, annee)}


def _lu_dans_la_version(nom: str, version: dict, champ: str) -> bool:
    """Le moteur lit-il ce paramètre dans la version même (:data:`DE_LA_VERSION`) ?
    Les paliers aussi, là où la version n'en a pas et lit la table ; la durée,
    là où la version n'en a pas."""
    parametres = version["contenu"]["parametres"]
    return nom == ANTICIPATION and (
        champ in DE_LA_VERSION
        or (champ == "paliers_d_anticipation" and parametres[champ] is None
            and parametres.get("coefficients_par_annee_d_age") is not None)
        or (champ == "duree_requise_par_generation" and parametres[champ] is None))


def _declare(nom: str, version: str, champ: str, code: str | None) -> bool:
    return any((n, v, c) == (nom, version, champ) and (regimes is None or code in regimes)
               for n, v, c, regimes, _ in ECARTS_DECLARES)


def _en_toutes_lettres(jour: date) -> str:
    return f"{'1er' if jour.day == 1 else jour.day} {MOIS[jour.month - 1]} {jour.year}"


def test_chaque_version_nait_du_texte_qui_la_coupe():
    """Chaque fiche du lot couvre toute date d'effet ; chaque version commence
    le jour où entre en vigueur le texte qui la fait naître (`nee_de`), qu'elle
    cite parmi ses textes, ou le jour que ce texte fixe, et qu'il cite : « à
    compter du 1er avril 1983 », plus tôt que sa publication, « à compter du
    1er janvier 2010 », plus tard."""
    for nom in LOT:
        versions = _versions(nom)
        assert _bornes(versions[0])[0] is None and _bornes(versions[-1])[1] is None, nom
        for avant, apres in zip(versions, versions[1:]):
            assert _bornes(avant)[1] == _bornes(apres)[0], (nom, apres["id"])
        for version in versions:
            if version.get("nee_de"):
                texte = next((t for t in version.get("textes") or []
                              if t.get("id") == version["nee_de"]), None)
                assert texte is not None, (nom, version["id"])
                debut = _bornes(version)[0]
                assert (texte["en_vigueur"] == debut
                        or f"compter du {_en_toutes_lettres(debut)}" in str(texte.get("citation"))
                        ), (nom, version["id"])


def test_les_periodes_et_le_portage_portent_ce_que_chaque_version_lit():
    """Sur chaque année que la version couvre en entier, les périodes de chacun
    de ses régimes portent la valeur que la version lit, sous le même nom ; le
    portage, la constante qui la sert ; sinon, l'écart est déclaré."""
    for nom in LOT:
        regimes = carte.fiches()[nom]["regimes"]
        for version in _versions(nom):
            for champ, lu in (version["contenu"].get("parametres") or {}).items():
                if champ in A_PART or _lu_dans_la_version(nom, version, champ):
                    continue
                for code in [None] if champ in DU_PORTAGE else regimes:
                    portes = _portes(version, champ, code)
                    if portes and not _declare(nom, version["id"], champ, code):
                        assert portes == {_valeur(lu)}, (nom, version["id"], champ, code)


@pytest.mark.parametrize("nom, version, champ, regimes, article", ECARTS_DECLARES)
def test_ce_que_le_modele_fait_autrement_la_fiche_le_declare(nom, version, champ, regimes,
                                                             article):
    """La version lit une valeur que le dépôt ne porte pas, dans les régimes
    nommés ; une approximation de la fiche touche cette version et cite
    l'article qui la fonde."""
    fiche = carte.fiches()[nom]
    lue = _version(nom, version)
    valeur = _valeur(lue["contenu"]["parametres"][champ])
    codes = [None] if champ in DU_PORTAGE else (regimes or fiche["regimes"])
    portes = set().union(*(_portes(lue, champ, code) for code in codes))
    assert portes and valeur not in portes, (nom, version, champ)
    assert any(version in (a.get("version") or []) and article in str(a.get("textes") or "")
               for a in fiche.get("approximations") or []), (nom, version, article)


def _lignes(relatif: str) -> list[dict]:
    with (REFERENCE / relatif).open(encoding="utf-8", newline="") as flux:
        return list(csv.DictReader(ligne for ligne in flux if not ligne.startswith("#")))


def _escalier(manquants: int) -> float:
    """Le coefficient du portage pour un nombre de trimestres d'anticipation,
    lu dans ses paliers."""
    coefficient, precedent = 1.0, 0
    for borne, pas in _constante("PALIERS_ANTICIPATION"):
        coefficient -= max(0, min(manquants, borne) - precedent) * pas
        precedent = borne
    return round(coefficient, 6)


def test_la_table_de_1970_est_l_escalier_aux_annees_revolues():
    """« AGES COEFFICIENTS : 55 ans 0,43 […] 64 ans 0,96 » : la table de
    l'arrêté du 30 décembre 1970, que les rédactions suivent jusqu'au 31 août
    1983, est l'escalier du portage à chaque anniversaire ; entre deux, elle
    garde le coefficient de l'âge révolu, que l'escalier relève à chaque
    trimestre, jusqu'à 5,25 points de plus. Le moteur la lit dans la fiche
    jusqu'à cette date (:data:`DE_LA_VERSION`)."""
    table = _version(ANTICIPATION, "arrete_de_1970")["contenu"]["parametres"][
        "coefficients_par_annee_d_age"]
    assert len(table) == 10
    assert [round(c, 6) for c in table] == [_escalier(4 * (65 - age)) for age in range(55, 65)]
    entre_deux = max(_escalier(4 * (65 - age) - t) - table[age - 55]
                     for age in range(55, 65) for t in range(1, 4))
    assert round(entre_deux, 6) == 0.0525


def test_les_ancres_fixes_de_2023_tombent_sur_l_escalier_du_portage():
    """La rédaction du 14 septembre 2023 ancre l'escalier à soixante-deux ans,
    0,78, et à soixante-quatre, 0,88, et non plus à l'âge légal : pour toute
    génération qui atteint après ce jour l'âge du 1° de L. 351-8, soixante-sept
    ans, ce sont vingt et douze trimestres avant lui, où le portage, qui
    ancre ses paliers sur l'âge du taux plein, rend les mêmes coefficients ;
    et 0,43 dix ans avant."""
    ages = {float(l["generation"]): float(l["age"])
            for l in _lignes("legislation/age_annulation_decote.csv")}

    def age(generation: int) -> float:
        """La ligne de la génération, ou de la dernière qui la précède."""
        return ages[max(g for g in ages if g <= generation)]

    tardives = {age(g) for g in range(1950, 2001) if g + 1 + age(g) > 2023 + 8.5 / 12}
    assert tardives == {67.0}
    assert (_escalier(4 * (67 - 62)), _escalier(4 * (67 - 64)), _escalier(40)) == (0.78, 0.88, 0.43)
    assert _constante("COEFFICIENT_ANTICIPATION_PLANCHER") == _escalier(40)


def test_la_seconde_table_de_1983_lit_trente_sept_ans_et_demi():
    """De 1983 à 2003, le II de l'article 16 ouvre la seconde table à la durée
    « comprise entre trente-deux ans et demi et trente-sept ans et demi », et
    assimile à soixante-cinq ans l'âge où l'agent « aurait effectivement
    compté trente-sept années et demie d'assurance » ; le modèle y lit la
    durée du régime général de la génération (`duree_requise_par_generation`).
    Elles sont égales pour toute génération de soixante à soixante-cinq ans
    jusqu'en 1993 ; la loi du 22 juillet 1993 relève la seconde d'un trimestre
    par génération dès 1934 : de 1994 à 2003, la fiche déclare l'écart."""
    lignes = _lignes("legislation/duree_assurance_requise.csv")
    durees = {int(float(l["generation"])): int(l["trimestres"]) for l in lignes}

    def duree(generation: int) -> int:
        return durees[max(g for g in durees if g <= generation)]

    lues = [(version, version["contenu"]["parametres"].get("duree_de_la_seconde_table_trimestres"))
            for version in _versions(ANTICIPATION)]
    lues = [(version, lu) for version, lu in lues if lu]
    assert {lu for _, lu in lues} == {150}
    ecarts = {annee for version, lu in lues for annee in _annees_entieres(*_bornes(version))
              if any(duree(annee - age) != lu for age in range(60, 66))}
    assert min(ecarts) == 1994 and max(ecarts) == 2003
    fiche = carte.fiches()[ANTICIPATION]
    touchees = {version["id"] for version, _ in lues
                if set(_annees_entieres(*_bornes(version))) & ecarts}
    assert any(touchees <= set(a.get("version") or []) and "1994" in str(a.get("ecart"))
               for a in fiche.get("approximations") or []), touchees


# -- le coefficient servi, dans les deux moteurs --------------------------------

#: Un agent contractuel de l'État, né le 15 janvier 1922, payé deux plafonds :
#: des points de l'IPACTE au-dessus du plafond de 1951 à 1970, de l'IGRANTE
#: au-dessous de 1960 à 1970, de l'Ircantec ensuite. Ses âges se comptent de
#: février (R. 351-37) : soixante ans en février 1982.
REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "30", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "60", "naissance": "1922-01-15", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "2", "sexe": "H",
    "statut": "contractuel_public", "stock": "prix", "table": "unisexe",
}
#: Les trois régimes dont l'article 16 affecte les points.
EN_POINTS = ("igrante", "ipacte", "ircantec")


def _servis(sortie: dict) -> dict:
    """La date d'effet, et le coefficient d'anticipation que la formule de
    chacun des trois régimes affiche, ``None`` sans coefficient."""
    liquidation = sortie["liquidations"][0]
    servis = {"date": liquidation["ouverture"]["date_effet"]}
    for pension in liquidation["pensions"]["regimes"]:
        if pension["regime"] in EN_POINTS:
            trouve = re.search(r"coefficient d'anticipation ([0-9.]+)", pension["detail"])
            servis[pension["regime"]] = float(trouve.group(1)) if trouve else None
    return servis


@functools.cache
def _deux_moteurs(cas: str) -> tuple[list[dict], list[dict]]:
    """Ce que servent le portage, qui fait foi, puis son jumeau Python, pour
    chaque requête de ``cas`` (JSON, une liste de retouches de la requête)."""
    import shutil
    import subprocess
    import tempfile

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _python

    requetes = [{**REQUETE, **retouche} for retouche in json.loads(cas)]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True,
            encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    return ([_servis(sortie) for sortie in json.loads(execution.stdout)],
            [_servis(sortie) for sortie in _python(requetes)])


def _attendus(date: str, coefficient: float | None) -> dict:
    return {"date": date, **{code: coefficient for code in EN_POINTS}}


#: La table par année d'âge, jusqu'au 31 août 1983 : la retouche de la
#: requête, la date d'effet, et le coefficient lu à la main dans l'article 16
#: (« 60 ans 0,78 […] 61 ans 0,83 […] 63 ans 0,92 […] 64 ans 0,96 »), là où
#: l'escalier au trimestre de l'arrêté du 26 juillet 1983 donnerait 0,8175,
#: 0,95 et 0,95 ; puis l'escalier, dès sa publication.
TABLE_PAR_ANNEE_D_AGE = [
    # Soixante ans et neuf mois en novembre 1982 : la ligne de soixante ans,
    # 0,78 ; l'escalier en eût donné 0,78 + 3 × 0,0125 = 0,8175.
    ({"liquidation_mois": "9"}, "1982-11-01", 0.78),
    # Né en 1919, soixante-trois ans et onze mois en janvier 1983 : la ligne
    # de soixante-trois ans, 0,92 ; l'escalier, 0,88 + 7 × 0,01 = 0,95.
    ({"naissance": "1919-01-15", "liquidation": "63", "liquidation_mois": "11"},
     "1983-01-01", 0.92),
    # Né en 1922, au travail à vingt-cinq ans, parti à soixante et un ans et
    # trois mois en mai 1983 avec cent quarante-cinq trimestres : la seconde
    # table, ouverte le 1er avril 1983 (II), assimile à soixante-cinq ans l'âge
    # où il aurait les cent cinquante, cinq trimestres plus tard : il est
    # « âgé » de 65 − 5/4 = 63,75 ans, la ligne de soixante-trois ans, 0,92,
    # meilleure que celle de son âge, soixante et un ans, 0,83. L'escalier lui
    # eût donné 1 − 5 × 0,01 = 0,95.
    ({"debut": "25", "liquidation": "61", "liquidation_mois": "3"}, "1983-05-01", 0.92),
    # Né en 1923, soixante ans et neuf mois en novembre 1983, après la
    # publication de l'arrêté du 26 juillet 1983 : l'escalier, 0,8175.
    ({"naissance": "1923-01-15", "liquidation_mois": "9"}, "1983-11-01", 0.8175),
]


def test_avant_le_31_aout_1983_la_table_par_annee_d_age():
    """De 1971 au 31 août 1983, l'article 16 ne donne qu'un coefficient par
    année d'âge, et les deux moteurs le servent aux points des trois régimes,
    à l'âge révolu ; l'escalier au trimestre, dès la publication de l'arrêté
    qui le crée (« fixés désormais par trimestre »)."""
    cas = json.dumps([retouche for retouche, _, _ in TABLE_PAR_ANNEE_D_AGE])
    portage, jumeau = _deux_moteurs(cas)
    attendus = [_attendus(date, coefficient) for _, date, coefficient in TABLE_PAR_ANNEE_D_AGE]
    assert portage == attendus
    assert jumeau == attendus


#: L'exonération de qui a la durée du taux plein du régime général : la
#: retouche de la requête, et ce que servent les trois régimes — le
#: coefficient lu à la main dans la table de l'article 16, ``None`` sans
#: coefficient. Au travail dès dix-huit ans, l'agent né en 1922 a plus de cent
#: cinquante trimestres à soixante ans ; le 6° c) ne l'exonère qu'« à compter
#: du 1er avril 1983 », et l'IPACTE et l'IGRANTE, dont les fiches portent la
#: durée du régime général sur leur seule période, avec l'Ircantec.
EXONERATION_A_LA_DUREE = [
    # Soixante ans et neuf mois en novembre 1982 : la ligne de soixante ans.
    ({"debut": "18", "liquidation_mois": "9"}, _attendus("1982-11-01", 0.78)),
    # Soixante et un ans et un mois en mars 1983 : la ligne de soixante et un
    # ans, le 6° c) n'est pas encore en vigueur.
    ({"debut": "18", "liquidation": "61", "liquidation_mois": "1"},
     _attendus("1983-03-01", 0.83)),
    # Le mois suivant, en avril 1983 : aucun coefficient.
    ({"debut": "18", "liquidation": "61", "liquidation_mois": "2"},
     _attendus("1983-04-01", None)),
    # Né en 1905, parti à soixante-deux ans en février 1967, avant l'Ircantec :
    # la ligne de soixante-deux ans, 0,88, de la table que la version
    # ipacte_et_igrante présume, sur ses points de l'IPACTE et de l'IGRANTE.
    ({"naissance": "1905-01-15", "debut": "18", "liquidation": "62"},
     {"date": "1967-02-01", "igrante": 0.88, "ipacte": 0.88}),
]


def test_la_duree_n_exonere_qu_a_compter_du_1er_avril_1983():
    """Avant le 1er avril 1983, la durée d'assurance n'exonère pas : les deux
    moteurs lisent dans la version de la date d'effet que le coefficient se
    lit à l'âge seul, pour les points de l'Ircantec comme pour ceux de
    l'IPACTE et de l'IGRANTE, dès 1951."""
    portage, jumeau = _deux_moteurs(json.dumps([retouche for retouche, _ in
                                                EXONERATION_A_LA_DUREE]))
    attendus = [attendu for _, attendu in EXONERATION_A_LA_DUREE]
    assert portage == attendus
    assert jumeau == attendus
