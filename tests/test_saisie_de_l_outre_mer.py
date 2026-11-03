"""Le département d'outre-mer, saisi (action 177, étape 7).

L'assuré qui a travaillé en Guadeloupe, en Guyane, en Martinique ou à La Réunion
le dit par années entières, « 1975:1994:reunion », comme une dispense de
l'assiette minimale ; la saisie le lit et refuse ce qui est mal dit ; le relevé
et les métiers le portent sur les lignes d'emploi des années qu'il nomme, et le
modèle sert alors les règles qui le lisent : le seuil du trimestre des années
travaillées outre-mer de 1948 à 1995 (R. 753-21, R. 351-9 ; action 138,
étape 6), l'exonération de l'artisan et du commerçant des DOM dont le revenu ne
dépasse pas 390 € (L. 756-3, D. 756-7 ; action 177, étape 4).
"""

from __future__ import annotations

import html
import re
from urllib.parse import parse_qs

import pytest

from retraite_notionnelle.web.site import ErreurSite, module

from outils_pont import Saisies, saisie_du_portage
from outils_web import page  # noqa: F401 — la fixture partagée

#: Née le 15 mars 1962, partie le 1er avril 2027 : son relevé se prolonge
#: jusqu'au départ.
NEE_EN_1962 = {"naissance": "1962-03-15", "liquidation": "2027-04-01"}

#: Né le 15 mars 1925, parti à soixante et un ans le 1er avril 1986 : son
#: relevé dit toute sa carrière, rien ne s'y ajoute.
NE_EN_1925 = {"naissance": "1925-03-15", "liquidation": "1986-04-01"}

#: 30 000 F en 1981, puis 2 900 F en 1982 : entre le seuil d'un trimestre de La
#: Réunion, 200 heures à 13,841 F, soit 2 768,20 F (la semaine de 40 heures à
#: 553,64 F, arrêté du 30 décembre 1981), et celui de la métropole, 200 heures à
#: 18,15 F, soit 3 630 F. Le relevé est en euros, les francs divisés par 6,55957.
RELEVE_1982 = "1981:salarie_prive_non_cadre:4573.47\n1982:salarie_prive_non_cadre:442.10"


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


def _saisie(**champs):
    """La saisie du portage, de ses champs."""
    return module("saisie").Saisie(champs)


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_lit_les_annees_et_leur_departement():
    saisie = _saisie(outre_mer="1975:1977:reunion,\n 1990:1990: martinique")
    assert saisie.outre_mer_analyse() == {
        1975: "reunion", 1976: "reunion", 1977: "reunion", 1990: "martinique"}
    assert _saisie().outre_mer_analyse() == {}


#: Chaque faute, et la phrase qui la refuse.
REFUS = {
    "1975-1994:reunion": "Années outre-mer mal formées : « 1975-1994:reunion ». Attendu "
                         "« année_début:année_fin:département », par exemple "
                         "1975:1994:reunion.",
    "1975:1994:": "Années outre-mer mal formées : « 1975:1994: ». Attendu "
                  "« année_début:année_fin:département », par exemple 1975:1994:reunion.",
    "1700:1710:reunion": "Années outre-mer « 1700:1710:reunion » : 1700 ne tombe dans "
                         "aucune carrière possible. Attendu entre",
    "1994:1975:reunion": "Années outre-mer « 1994:1975:reunion » : elles finissent (1975) "
                         "avant de commencer (1994).",
    "1975:1994:corse": "Années outre-mer « 1975:1994:corse » : département inconnu "
                       "« corse ». Attendu l'un de : guadeloupe, guyane, martinique, "
                       "reunion.",
    "2015:2020:mayotte": "Années outre-mer « 2015:2020:mayotte » : Mayotte a sa propre "
                         "caisse ; dites-le par le statut de la période, salarié ou "
                         "travailleur indépendant de Mayotte.",
    "1975:1994:reunion, 1990:1999:martinique": "Années outre-mer « 1990:1999:martinique » : "
                                               "l'année 1990 a déjà son département.",
}


@pytest.mark.parametrize("texte", list(REFUS))
def test_des_annees_outre_mer_mal_dites_sont_refusees(texte):
    """Se tromper de touche ne donne pas un autre chiffre, mais un refus — et
    la saisie le prononce avant tout calcul (``verifier``). Mayotte, dont la
    caisse a ses statuts, n'est pas un département de ce champ : le modèle
    le refuserait (``DEPARTEMENTS_D_OUTRE_MER``)."""
    with pytest.raises(ErreurSite, match="ErreurSaisie : " + re.escape(REFUS[texte])):
        _saisie(outre_mer=texte).verifier()


def test_l_adresse_porte_les_annees_outre_mer_qu_on_a_dites():
    """L'adresse réécrite garde le champ, et ne l'écrit pas quand il est vide."""
    saisie = saisie_du_portage({"outre_mer": " 1975:1994:reunion "})
    lu = parse_qs(saisie.requete())
    assert lu["outre_mer"] == ["1975:1994:reunion"]
    assert saisie_du_portage({k: v[0] for k, v in lu.items()}).outre_mer == "1975:1994:reunion"
    assert "outre_mer" not in parse_qs(saisie_du_portage({}).requete())


# -- le relevé ----------------------------------------------------------------------

def test_le_releve_porte_le_departement_des_annees_qu_il_nomme(saisies):
    """Chaque ligne d'emploi du relevé prend le département de son année ; une
    année d'interruption, qui ne cotise pas, n'en prend aucun. Les années qui
    prolongent le relevé jusqu'au départ prennent celui de leur année, comme
    une dispense : celles que le champ ne nomme pas sont en métropole."""
    requete = {**NEE_EN_1962,
               "releve": "2019:artisan:3000\n2020:artisan:3000\n2021:artisan:3000",
               "interruptions": "2020:2020:chomage_indemnise",
               "outre_mer": "2015:2023:martinique"}
    assert [(ligne.annee, ligne.outre_mer)
            for ligne in saisie_du_portage(requete).releve_analyse()] == [
        (2019, "martinique"), (2020, ""), (2021, "martinique")]
    assert [(ligne.annee, ligne.outre_mer) for ligne in saisies.carriere(requete).lignes] == [
        (2019, "martinique"), (2020, ""), (2021, "martinique"), (2022, "martinique"),
        (2023, "martinique"), (2024, ""), (2025, ""), (2026, ""), (2027, "")]


def test_l_annee_travaillee_outre_mer_valide_au_seuil_du_departement(saisies):
    """2 900 F en 1982 valent un trimestre à La Réunion, où 2 768,20 F en
    valent un, et aucun en métropole, où il en faut 3 630 F (R. 753-21,
    R. 351-9) ; 30 000 F en 1981 en valent quatre partout."""
    def trimestres(**champs):
        carriere = saisies.carriere({**NE_EN_1925, "releve": RELEVE_1982, **champs})
        return [(ligne.annee, ligne.outre_mer, ligne.trimestres_valides)
                for ligne in carriere.lignes]
    assert trimestres(outre_mer="1981:1982:reunion") == [
        (1981, "reunion", 4), (1982, "reunion", 1)]
    assert trimestres() == [(1981, "", 4), (1982, "", 0)]


def test_sous_390_euros_l_artisan_des_dom_ne_valide_rien(saisies):
    """L'artisan de La Réunion qui déclare 300 € en 2010 est exonéré de toute
    cotisation (L. 756-3 ; D. 756-7, 390 € depuis 2002) : « Il ne bénéficie
    d'aucun droit à retraite », dit la caisse. En métropole, il cotise sur
    l'assiette minimale, 200 heures de SMIC à 8,86 €, soit 1 772 € (D. 633-2),
    qui lui en valide un."""
    releve = {**NEE_EN_1962, "releve": "2010:artisan:300"}

    def annee_2010(**champs):
        ligne = next(ligne for ligne in saisies.carriere({**releve, **champs}).lignes
                     if ligne.annee == 2010)
        return ligne.trimestres_valides, ligne.cotisations_versees
    assert annee_2010() == (1, True)
    assert annee_2010(outre_mer="2010:2010:reunion") == (0, False)


def _texte(fragment: str) -> str:
    """Le texte d'un fragment de page, balises ôtées, espaces fines comprises."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))
                  .replace(" ", " ").replace("\xa0", " ")).strip()


def test_le_controle_du_releve_lit_le_seuil_du_departement(page):
    """Le contrôle du relevé (action 138, étape 10) lit chaque année contre le
    seuil de son département : 1982, que le relevé dit à quatre trimestres
    pour 2 900 F, se contrôle à La Réunion contre 2 768,20 F, soit 422,01 €,
    où son revenu en valide un, et non contre les 3 630 F de la métropole,
    soit 553,39 €, où il n'en valide aucun."""
    releve = "1981:salarie_prive_non_cadre:4573.47:4\n1982:salarie_prive_non_cadre:442.10:4"

    def rangees(**champs):
        corps = page("/simuler", **NE_EN_1925, releve=releve, **champs)
        debut = corps.index("Votre relevé, contrôlé")
        bloc = corps[debut:corps.index("</details>", debut)]
        return [(int(_texte(tete)), [_texte(cellule) for cellule in
                                     re.findall(r"<td[^>]*>(.*?)</td>", cellules)])
                for tete, cellules in re.findall(
                    r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)]
    assert rangees(outre_mer="1981:1982:reunion") == [
        (1982, ["442,10 €", "422,01 €", "1 trimestre", "4 trimestres"])]
    assert rangees() == [(1982, ["442,10 €", "553,39 €", "0 trimestre", "4 trimestres"])]
