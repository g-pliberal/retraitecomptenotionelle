"""La réversion du régime des non-salariés agricoles, saisie (fiche
``pension_majoree_reference`` ; action 138, étape 8).

La veuve ou le veuf d'un assuré du régime des non-salariés agricoles en reçoit
une pension de réversion (L. 732-41 du code rural), que la pension majorée de
référence lit trois fois : de 2009 à 2021, elle porte au montant du chef toutes
les périodes de qui peut y prétendre, nulle ou non (D. 732-110, II, 2°) ; elle
se retranche de la PMR (D. 732-112) ; elle compte au plafond (D. 732-114). Les
deux moteurs la servent depuis le 18 octobre 2026 ; la saisie la déclare par
deux champs, le mois où elle commence et son montant mensuel brut de ce mois,
zéro compris quand les ressources l'absorbent. Sans eux, la présomption
``pas_de_reversion_agricole`` : aucune réversion, ni retranchée, ni au 2°.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import ReversionAgricole
from retraite_notionnelle.web.site import ErreurSite

from outils_pont import Saisies, saisie_du_portage

RACINE = Path(__file__).resolve().parents[1]

#: La conjointe collaboratrice des tests de la règle (``_veuve``, dans
#: ``test_minima_agricoles.py``), saisie : née le 15 janvier 1952,
#: collaboratrice de ses vingt ans à son départ, le 1er février 2016.
VEUVE = {
    "naissance": "1952-01-15", "sexe": "F", "statut": "collaborateur_agricole",
    "debut": "1972-01", "liquidation": "2016-02", "unite_revenu": "moyen",
    "salaire": "0.3",
}
#: Sa réversion du régime : 150 € par mois depuis mars 2010.
REVERSION = {"reversion_agricole": "2010-03", "reversion_agricole_mensuel": "150"}
#: Ce qu'elle sert par an au départ : les 150 € de mars 2010 revalorisés
#: jusqu'au 1er février 2016 par les coefficients que la Cnav publie, d'avril
#: 2010, 2011, 2012 et 2013 et d'octobre 2015 (L. 161-23-1).
REVERSION_EN_2016 = 150 * 12 * 1.009 * 1.021 * 1.021 * 1.013 * 1.001
#: Une veuve salariée de ses vingt ans à 1999, puis collaboratrice de son
#: conjoint exploitant jusqu'à son départ en 2016, qui saisit sa pension : le
#: revenu d'une collaboratrice ne changeant pas la sienne, l'inversion cherche
#: celui de ses années de salariée.
PAR_PENSION = {
    "naissance": "1952-01-15", "sexe": "F", "statut": "salarie_prive_non_cadre",
    "debut": "1972-01", "liquidation": "2016-02", "situation": "retraite",
    "saisie_par": "pension", "pension": "1200", "montants": "brut",
    "metier2_debut": "1999-01", "metier2_statut": "collaborateur_agricole",
}


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


def _pmr(comparaison):
    """L'avantage de la pension majorée de référence que le droit en vigueur sert."""
    return next(avantage for avantage in comparaison.actuel.avantages_appliques
                if avantage.code == "pension_majoree_reference")


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_lit_la_reversion_et_l_adresse_la_garde():
    """Le mois et le montant, lus tels quels ; l'adresse les réécrit, un montant
    nul compris, et ne porte rien sans eux."""
    saisie = saisie_du_portage({**VEUVE, **REVERSION})
    assert saisie.reversion_agricole_declaree() == {"debut": "2010-03", "mensuel": 150.0}
    lu = parse_qs(saisie.requete())
    assert lu["reversion_agricole"] == ["2010-03"]
    assert lu["reversion_agricole_mensuel"] == ["150"]
    relue = saisie_du_portage({cle: valeur[0] for cle, valeur in lu.items()})
    assert relue.reversion_agricole_declaree() == saisie.reversion_agricole_declaree()
    nulle = saisie_du_portage({**VEUVE, **REVERSION, "reversion_agricole_mensuel": "0"})
    assert nulle.reversion_agricole_declaree() == {"debut": "2010-03", "mensuel": 0.0}
    assert parse_qs(nulle.requete())["reversion_agricole_mensuel"] == ["0"]
    sans = saisie_du_portage(VEUVE)
    assert sans.reversion_agricole_declaree() is None
    assert not {"reversion_agricole", "reversion_agricole_mensuel"} & set(
        parse_qs(sans.requete()))


@pytest.mark.parametrize("champs, motif", [
    # Un montant sans mois, un mois sans montant : la réversion se dit entière.
    ({"reversion_agricole_mensuel": "150"}, "dites aussi le mois où elle commence"),
    ({"reversion_agricole": "2010-03"}, "dites aussi son montant"),
    ({"reversion_agricole": "2010-13", "reversion_agricole_mensuel": "150"},
     "attendu en AAAA ou AAAA-MM"),
    # Le jour même de la naissance, comme la chronologie, qui le refuse aussi.
    ({"reversion_agricole": "1952-01-15", "reversion_agricole_mensuel": "150"},
     "suit votre naissance"),
    ({"reversion_agricole": "2010-03", "reversion_agricole_mensuel": "-1"},
     "positif ou nul"),
])
def test_une_reversion_incomplete_ou_impossible_est_refusee(champs, motif):
    with pytest.raises(ErreurSite, match=motif):
        saisie_du_portage({**VEUVE, **champs})


def test_ses_voisines_sont_acceptees():
    """Le lendemain de la naissance, et un montant nul : la réversion que les
    ressources absorbent ouvre encore le 2° de D. 732-110, II."""
    for champs in ({"reversion_agricole": "1952-01-16", "reversion_agricole_mensuel": "150"},
                   {"reversion_agricole": "2010", "reversion_agricole_mensuel": "0"}):
        assert saisie_du_portage({**VEUVE, **champs}).reversion_agricole_declaree()


# -- la carrière --------------------------------------------------------------------

def test_les_trois_chemins_de_la_carriere_portent_la_reversion(saisies):
    """Les métiers, le relevé et la pension saisie : chaque carrière que la
    saisie bâtit porte la réversion déclarée ; sans elle, aucune
    (présomption ``pas_de_reversion_agricole``)."""
    attendue = ReversionAgricole(debut=DateMois(2010, 3), mensuel=150.0)
    assert saisies.carriere({**VEUVE, **REVERSION}).reversion_agricole == attendue
    releve = {**VEUVE, **REVERSION, "releve": "2014:collaborateur_agricole:3000\n"
                                              "2015:collaborateur_agricole:3000"}
    assert saisies.carriere(releve).reversion_agricole == attendue
    inverse = saisies.simuler({**PAR_PENSION, **REVERSION})
    assert inverse.carriere.reversion_agricole == attendue
    assert saisies.carriere(VEUVE).reversion_agricole is None


def test_la_veuve_saisie_recoit_la_pmr_que_sa_reversion_ouvre_et_reduit(saisies):
    """Sa réversion, même nulle, porte toutes ses périodes au montant du chef
    (D. 732-110, II, 2°) ; la PMR en retranche ce qu'elle sert au départ,
    revalorisée (D. 732-112). Sans elle, le montant du chef ne va qu'à ses
    années de 1999 à 2008, au montant réduit pour les autres, et rien ne se
    retranche."""
    sans = _pmr(saisies.simuler(VEUVE))
    nulle = _pmr(saisies.simuler({**VEUVE, **REVERSION, "reversion_agricole_mensuel": "0"}))
    servie = _pmr(saisies.simuler({**VEUVE, **REVERSION}))
    assert " + " in sans.detail.split(", au taux")[0]
    assert " + " not in nulle.detail.split(", au taux")[0]
    assert nulle.montant > sans.montant
    assert "réversion" not in sans.detail + nulle.detail
    assert f", moins {REVERSION_EN_2016:,.2f} € de réversion du régime" in servie.detail
    assert servie.montant == pytest.approx(nulle.montant - REVERSION_EN_2016, abs=1e-6)


# -- le portage ---------------------------------------------------------------------

LECTURE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
  const comparaison = contexte.simuler(saisie);
  const reversion = comparaison.carriere.reversionAgricole;
  const pmr = comparaison.actuel.avantages_appliques
    .find((avantage) => avantage.code === "pension_majoree_reference");
  return {
    requete: saisie.requete(),
    declaree: saisie.reversionAgricoleDeclaree(),
    carriere: reversion === null ? null
      : [reversion.debut.annee, reversion.debut.mois, reversion.mensuel],
    pmr: pmr === undefined ? null : [Math.round(pmr.montant * 100), pmr.detail],
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _lu_par_python(saisies: Saisies, requete: dict) -> dict:
    """Ce que le moteur Python lit de la carrière que le portage bâtit, et
    sert."""
    comparaison = saisies.simuler(requete)
    reversion = comparaison.carriere.reversion_agricole
    pmr = next((avantage for avantage in comparaison.actuel.avantages_appliques
                if avantage.code == "pension_majoree_reference"), None)
    return {
        "carriere": None if reversion is None else [
            reversion.debut.annee, reversion.debut.mois, reversion.mensuel],
        "pmr": None if pmr is None else [round(pmr.montant * 100), pmr.detail],
    }


def test_le_portage_lit_la_meme_reversion(saisies):
    """La saisie du portage lit la réversion, et la donne à la carrière ; sur
    elle, les deux moteurs servent la même PMR, par les métiers, par le relevé
    et par la pension."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    requetes = [
        VEUVE,
        {**VEUVE, **REVERSION},
        {**VEUVE, **REVERSION, "reversion_agricole_mensuel": "0"},
        {**VEUVE, "reversion_agricole": "2018-06", "reversion_agricole_mensuel": "150.5"},
        {**VEUVE, **REVERSION, "releve": "2014:collaborateur_agricole:3000"},
        {**PAR_PENSION, **REVERSION},
    ]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LECTURE_JS], cwd=RACINE,
        input=json.dumps(requetes), capture_output=True, text=True, encoding="utf-8",
        check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    lus = json.loads(execution.stdout)
    attendus = [_lu_par_python(saisies, requete) for requete in requetes]
    assert [{cle: lu[cle] for cle in attendu} for lu, attendu in zip(lus, attendus)] == attendus
    assert [lu["declaree"] for lu in lus] == [
        None, {"debut": "2010-03", "mensuel": 150.0}, {"debut": "2010-03", "mensuel": 0.0},
        {"debut": "2018-06", "mensuel": 150.5}, {"debut": "2010-03", "mensuel": 150.0},
        {"debut": "2010-03", "mensuel": 150.0}]
