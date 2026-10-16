"""L'oracle au-delà des carrières simples, quatrième famille : la carrière
longue des fonctionnaires, confrontée à OpenFisca-France-Pension (action 153,
étape 2).

Le frère de ``tests/test_oracle_categorie_active.py``, dont il reprend la
méthode : la convention de traduction d'abord, écrite dans
``scripts/fetch/openfisca_carriere_longue_fonction_publique.py`` et portée par
le témoin, puis chaque règle ; un écart connu est déclaré avec le texte qui le
tranche, et chacun des deux modèles doit rendre exactement ce que SA règle
commande.

* **Les portes d'avant 2009** : la fonction publique n'a la carrière longue
  qu'en 2005, chaque porte à sa date, sur une durée fixe (L. 25 bis ; loi
  n° 2004-1370, article 57). Le dépôt lui ouvrait les portes du régime
  général dès 2004, sur la durée de l'année d'ouverture. Corrigé le
  16 octobre 2026 ; les deux concordent.
* **L'entrée avant vingt ans** : OpenFisca la lit à la fin de l'année des
  seize ans. L'écart est le sien.
* **La CNRACL** : OpenFisca y lit les services de l'État. L'écart est le sien.
* **La durée cotisée** : les deux ouvrent et refusent les mêmes départs ;
  OpenFisca date l'ouverture à l'âge de la porte, le dépôt au mois où la
  durée est réunie, sans effet sur la pension.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.simulateur import Simulateur
from test_oracle_familles import AFFILIATIONS, PRECISION_OPENFISCA, PREFIXES

TEMOIN = (Path(__file__).resolve().parent / "temoins"
          / "openfisca_carriere_longue_fonction_publique.json")

PORTES_AVANT_2009 = "portes_avant_2009"
ENTREE_AVANT_VINGT_ANS = "entree_avant_vingt_ans"
CNRACL = "cnracl"
DUREE_COTISEE = "duree_cotisee"

#: Les entrées d'OpenFisca que la convention doit dire, au témoin.
CONVENTION_ATTENDUE = {
    "date_de_naissance", "sexe", "liquidation_date", "salaire_de_base",
    "duree_de_service_cotisee_annuelle", "quotite_de_travail", "taux_de_prime",
    "raison_depart_taux_plein_anticipe", "entree_precoce", "ouverture",
    "non_traduit",
}

#: L. 25 bis du code des pensions, rédaction du 1er janvier 2005
#: (LEGIARTI000006362733), et loi n° 2004-1370, article 57
#: (LEGIARTI000006759076), pour la CNRACL : chaque porte, son premier mois.
PORTES_DE_L_ARTICLE = {59.0: DateMois(2005, 1), 58.0: DateMois(2006, 7),
                       56.0: DateMois(2008, 1)}
#: « au moins égale à 168 trimestres », 164 ou 160 selon la porte : cent
#: soixante et le supplément, jusqu'à la rédaction du 19 décembre 2008.
DUREE_FIXE = 160

#: Ce que le droit commande à chaque profil des portes d'avant 2009.
OUVERT_AVANT_2009 = {
    "etat_1946_debut_15_en_2004": False,  # aucune porte avant 2005
    "etat_1947_debut_15_en_2005": False,  # cinquante-neuf ans seulement
    "etat_1950_debut_15_en_2007": False,  # cinquante-six ans en 2008
    "etat_1949_debut_15_en_2008": True,
}
#: Décret n° 2012-847, D. 16-1, I : l'âge de soixante ans à qui a débuté
#: avant vingt ans et cotisé la durée de sa génération.
AGE_DE_L_ENTREE_AVANT_VINGT_ANS = 60.0
#: Cinq trimestres à la fin de l'année des seize, dix-sept ou vingt ans.
TRIMESTRES_D_ENTREE = 5


@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _carriere(profil: dict, absentes: tuple[int, ...] = ()) -> Carriere:
    """La carrière que le profil décrit, sans les années ``absentes``."""
    lignes = [AnneeCarriere(annee=annee, revenu=profil["traitement"],
                            affiliation=AFFILIATIONS[profil["regime"]],
                            trimestres_valides=4)
              for annee in range(profil["debut"], profil["liquidation"])
              if annee not in absentes]
    return Carriere(annee_naissance=profil["naissance"], sexe="H", lignes=lignes,
                    age_liquidation=float(profil["liquidation"] - profil["naissance"]),
                    identifiant=profil["code"], jour_naissance=1)


def _le_droit(simulateur: Simulateur, profil: dict,
              absentes: tuple[int, ...] = ()) -> dict:
    """Ce que le scénario 1 rend : l'ouverture, son motif, l'âge où la
    carrière longue s'ouvre, la pension."""
    scenario = simulateur.scenario_actuel
    carriere = _carriere(profil, absentes)
    resultat = scenario.calculer(carriere)
    periode = simulateur.catalogue[profil["regime"]].periode(profil["liquidation"])
    pension = next(p for p in resultat.pensions_par_regime if p.regime == profil["regime"])
    return {
        "ouverte": resultat.liquidation_ouverte,
        "motif": resultat.motif_ouverture,
        "age": ouvrir.ouverture_carriere_longue(scenario, periode, carriere),
        "taux": resultat.taux_liquidation,
        "pension": pension.montant,
    }


@pytest.fixture(scope="module")
def nous(temoin, simulateur) -> dict[str, dict]:
    """Le calcul du dépôt pour chaque profil, fait une fois."""
    return {code: _le_droit(simulateur, entree["profil"])
            for code, entree in temoin["profils"].items()}


def _de_la_regle(temoin: dict, regle: str) -> list[tuple[str, dict]]:
    return [(code, entree) for code, entree in temoin["profils"].items()
            if entree["profil"]["regle"] == regle]


def _ouvert_chez_openfisca(entree: dict) -> bool:
    """La convention : sa date d'ouverture tombe au plus tard à la liquidation."""
    return (entree["openfisca"]["ouverture_des_droits_le"]
            <= f"{entree['profil']['liquidation']}-01-01")


def _age(profil: dict, date: str) -> float:
    """L'âge, au mois, à une date du témoin, du profil né un 1er janvier."""
    annee, mois, _ = (int(x) for x in date.split("-"))
    return annee - profil["naissance"] + (mois - 1) / 12


# -- la convention ---------------------------------------------------------------

def test_le_temoin_suit_sa_convention_de_traduction(temoin):
    """Le témoin dit d'où il vient, porte sa convention, et chaque profil les
    entrées qu'OpenFisca a reçues : ni enfant, ni raison de départ déclarée,
    ni temps partiel ; une carrière entrée de quatorze à dix-huit ans, que
    les deux comptent de même, quatre trimestres par année."""
    assert temoin["source"] == "OpenFisca-France-Pension"
    assert temoin["version"]
    assert CONVENTION_ATTENDUE <= set(temoin["convention"])
    profils = temoin["profils"]
    assert {e["profil"]["regle"] for e in profils.values()} == {
        PORTES_AVANT_2009, ENTREE_AVANT_VINGT_ANS, CNRACL, DUREE_COTISEE}
    for code, entree in profils.items():
        profil, recu, eux = entree["profil"], entree["entrees_openfisca"], entree["openfisca"]
        assert recu == {"sexe": False, "nombre_enfants": 0}, code
        assert 14 <= profil["debut"] - profil["naissance"] <= 18, code
        assert 2004 <= profil["liquidation"] <= 2019, code
        assert profil["liquidation"] - profil["naissance"] < 61, code
        cotises = 4 * (profil["liquidation"] - profil["debut"])
        assert eux["cotises_tous_regimes"] == eux["duree_assurance"] == cotises, code
        assert eux["pension_brute"] > 0, code
        assert code.startswith(PREFIXES[profil["regime"]].replace(
            "fonction_publique", "etat")), code


def test_les_deux_servent_la_meme_pension(temoin, nous):
    """La pension ne dépend pas de l'ouverture chez OpenFisca, et ces carrières
    ont toutes leur durée : au taux plein, sur la durée entière, les deux la
    servent au millionième."""
    for code, entree in temoin["profils"].items():
        eux, moi = entree["openfisca"], nous[code]
        assert eux["coefficient_de_proratisation"] == 1.0, code
        assert eux["decote_trimestres"] == 0, code
        assert moi["taux"] == pytest.approx(eux["taux_de_liquidation"], abs=1e-6), code
        assert moi["pension"] == pytest.approx(eux["pension_avant_minimum"],
                                               rel=PRECISION_OPENFISCA), code


# -- les portes d'avant 2009 -----------------------------------------------------

def test_les_portes_de_la_fonction_publique_s_ouvrent_chacune_a_sa_date(
        temoin, nous, simulateur):
    """L. 25 bis, rédaction du 1er janvier 2005 (LEGIARTI000006362733) :
    « 1° A compter du 1er janvier 2008, à cinquante-six ans [...] ; 2° A
    compter du 1er juillet 2006, à cinquante-huit ans [...] ; 3° A compter du
    1er janvier 2005, à cinquante-neuf ans » ; la loi n° 2004-1370, article
    57, le dit de la CNRACL. Le régime général ouvrait les trois dès 2004 :
    le dépôt les ouvrait de même aux fonctionnaires, et laissait partir à 58
    ans en 2004 et 2005, à 57 en 2007. Corrigé, il les refuse comme
    OpenFisca, qui ne les connaît que par génération."""
    profils = _de_la_regle(temoin, PORTES_AVANT_2009)
    assert {code for code, _ in profils} == set(OUVERT_AVANT_2009)
    carriere_longue = simulateur.scenario_actuel.carriere_longue
    assert carriere_longue.PORTES_FONCTION_PUBLIQUE_DEPUIS == PORTES_DE_L_ARTICLE
    for code, entree in profils:
        profil, moi = entree["profil"], nous[code]
        ouvert = OUVERT_AVANT_2009[code]
        assert moi["ouverte"] is ouvert, code
        assert (moi["motif"] == "carriere_longue") is ouvert, code
        assert _ouvert_chez_openfisca(entree) is ouvert, code
        carriere = _carriere(profil)
        portes = {porte[2] for porte in carriere_longue._portes(carriere)}
        de_l_article = {porte[2] for porte in carriere_longue._portes(carriere, True)}
        assert portes == set(PORTES_DE_L_ARTICLE), code
        assert de_l_article == {age for age, depuis in PORTES_DE_L_ARTICLE.items()
                                if depuis.rang <= carriere.date_liquidation.rang}, code


def test_la_duree_est_fixe_avant_2009(simulateur):
    """« au moins égale à 160 trimestres » à cinquante-neuf ans, en 2005 : le
    dépôt opposait la durée de l'année d'ouverture des fonctionnaires, 154
    trimestres en 2005, et ouvrait la porte à 156 trimestres cotisés.
    Quatre années manquent ici à une carrière entrée à seize ans ; trois,
    et la porte s'ouvre."""
    profil = {"code": "etat_1946_lacunes_en_2005", "regime": "fonction_publique_etat",
              "naissance": 1946, "debut": 1962, "liquidation": 2005,
              "traitement": 30000.0}
    carriere_longue = simulateur.scenario_actuel.carriere_longue
    assert carriere_longue.DUREE_FIXE_FONCTION_PUBLIQUE == DUREE_FIXE
    trois, quatre = (1980, 1981, 1982), (1980, 1981, 1982, 1983)
    ouverte = _le_droit(simulateur, profil, trois)
    refusee = _le_droit(simulateur, profil, quatre)
    assert ouverte["ouverte"] and ouverte["motif"] == "carriere_longue"
    assert not refusee["ouverte"] and refusee["motif"] == "non_ouverte"
    periode = simulateur.catalogue[profil["regime"]].periode(profil["liquidation"])
    requis, _ = ouvrir.duree_requise(simulateur.scenario_actuel, periode,
                                     _carriere(profil, quatre))
    assert requis < 4 * (profil["liquidation"] - profil["debut"] - len(quatre)) < DUREE_FIXE


# -- l'entrée avant vingt ans ----------------------------------------------------

def test_l_entree_avant_vingt_ans_est_l_ecart_d_openfisca(temoin, nous):
    """D. 16-1, I, rédaction du décret n° 2012-847 (LEGIARTI000026140012) :
    l'âge est abaissé à soixante ans « pour les fonctionnaires ayant débuté
    leur activité avant l'âge de vingt ans » et cotisé la durée de leur
    génération. Le dépôt l'ouvre aux deux profils entrés à dix-huit ans.
    OpenFisca lit la condition dans les services à la fin de l'année des
    seize ans (``duree_assurance_cotisee_seuil_haut``, qui reprend
    ``seuil_bas``) : zéro trimestre, et la porte se ferme."""
    profils = _de_la_regle(temoin, ENTREE_AVANT_VINGT_ANS)
    assert len(profils) == 2
    for code, entree in profils:
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        prefixe = PREFIXES[profil["regime"]]
        assert moi["ouverte"] and moi["motif"] == "carriere_longue", code
        assert moi["age"] == AGE_DE_L_ENTREE_AVANT_VINGT_ANS
        assert profil["liquidation"] - profil["naissance"] == AGE_DE_L_ENTREE_AVANT_VINGT_ANS
        assert eux[f"services_{prefixe}_a_20_ans"] >= TRIMESTRES_D_ENTREE, code
        assert eux["cotises_a_la_porte_haute"] == eux["services_fonction_publique_a_16_ans"] == 0
        assert not eux["carriere_longue"] and not _ouvert_chez_openfisca(entree), code


# -- la CNRACL -------------------------------------------------------------------

def test_la_cnracl_est_l_ecart_d_openfisca(temoin, nous):
    """La loi n° 2004-1370, article 57, puis D. 16-1, ouvrent la carrière
    longue aux affiliés de la CNRACL comme aux fonctionnaires de l'État. Le
    dépôt l'ouvre aux trois profils de la CNRACL. OpenFisca y compte
    l'entrée précoce dans les services de la fonction publique de l'État
    (``fonction_publique_duree_de_service_effective``, écrit en dur dans les
    deux seuils du gabarit des régimes) : zéro, et jamais de carrière
    longue à un fonctionnaire territorial ou hospitalier."""
    profils = [(code, entree) for code, entree in temoin["profils"].items()
               if entree["profil"]["regime"] == "cnracl"]
    assert len(profils) == 3 and len(_de_la_regle(temoin, CNRACL)) == 2
    for code, entree in profils:
        eux, moi = entree["openfisca"], nous[code]
        assert moi["ouverte"] and moi["motif"] == "carriere_longue", code
        assert eux["services_fonction_publique_a_16_ans"] == 0
        assert eux["services_fonction_publique_a_20_ans"] == 0
        assert eux["services_cnracl_a_20_ans"] >= TRIMESTRES_D_ENTREE, code
        assert eux["cotises_a_la_porte_basse"] == eux["cotises_a_la_porte_haute"] == 0
        assert not eux["carriere_longue"] and not _ouvert_chez_openfisca(entree), code
    # À l'État, les mêmes carrières entrées à quinze ans s'ouvrent chez lui.
    jumeau = temoin["profils"]["etat_1955_debut_15_en_2014"]
    assert jumeau["openfisca"]["cotises_a_la_porte_basse"] >= TRIMESTRES_D_ENTREE
    assert _ouvert_chez_openfisca(jumeau)


# -- la durée cotisée ------------------------------------------------------------

def test_la_duree_cotisee_ouvre_et_refuse_les_memes_departs(temoin, nous):
    """D. 16-1, II : cinquante-six ans à qui a cotisé la durée de sa
    génération et huit trimestres, avant les marches du décret
    n° 2014-350 ; 174 trimestres pour la génération 1955, 173 pour 1953 et
    1954. Les deux ouvrent les départs de 2014 et 2019, et refusent ceux de
    2010 et 2011, à 172 trimestres. Pour les premiers, OpenFisca date
    l'ouverture à l'âge de la porte, sur la durée cotisée à la liquidation ;
    le dépôt, au mois où la durée est réunie : plus tard, sans effet sur la
    pension."""
    profils = _de_la_regle(temoin, DUREE_COTISEE)
    assert len(profils) == 4
    ouverts = []
    for code, entree in profils:
        profil, eux, moi = entree["profil"], entree["openfisca"], nous[code]
        assert eux["carriere_longue"], code
        assert moi["ouverte"] is _ouvert_chez_openfisca(entree), code
        assert (moi["motif"] == "carriere_longue") is moi["ouverte"], code
        if moi["ouverte"]:
            ouverts.append(code)
            date_d_openfisca = _age(profil, eux["ouverture_des_droits_le"])
            assert date_d_openfisca < moi["age"] <= profil["liquidation"] - profil["naissance"]
    assert ouverts == ["etat_1955_debut_15_en_2014", "etat_1960_debut_15_en_2019"]
    # Soixante-quatre trimestres manquent aux 174 de la génération 1955 à
    # cinquante-six ans ; le dépôt ouvre quand ils sont réunis.
    assert nous["etat_1955_debut_15_en_2014"]["age"] == 15 + 174 / 4


# -- le portage -------------------------------------------------------------------

_PORTAGE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { PARAMETRES_DEFAUT } from "./moteur/js/config.js";
import { AnneeCarriere, Carriere } from "./moteur/js/carriere.js";
const [profils, affiliations] = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const simulateur = new Contexte(paquet).simulateur(PARAMETRES_DEFAUT);
const sortie = {};
for (const p of profils) {
  const lignes = [];
  for (let annee = p.debut; annee < p.liquidation; annee++) {
    if ((p.absentes ?? []).includes(annee)) continue;
    lignes.push(new AnneeCarriere({
      annee, revenu: p.traitement, trimestres_valides: 4,
      affiliation: affiliations[p.regime] }));
  }
  const resultat = simulateur.scenarioActuel.calculer(new Carriere({
    annee_naissance: p.naissance, sexe: "H", lignes, jour_naissance: 1,
    age_liquidation: p.liquidation - p.naissance, identifiant: p.code }));
  const pension = resultat.pensions_par_regime.find((r) => r.regime === p.regime);
  sortie[p.code] = [resultat.liquidation_ouverte, resultat.motif_ouverture,
                    pension ? pension.montant : null];
}
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_javascript_ouvre_les_memes_portes(temoin, nous, simulateur):
    """Le jumeau JavaScript ouvre et refuse les mêmes départs, pour le même
    motif, et sert la même pension, au milliardième : les portes datées et
    la durée fixe des fonctionnaires sont portées des deux côtés."""
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    lacunes = {"code": "etat_1946_lacunes_en_2005", "regime": "fonction_publique_etat",
               "naissance": 1946, "debut": 1962, "liquidation": 2005,
               "traitement": 30000.0, "absentes": [1980, 1981, 1982, 1983]}
    profils = [entree["profil"] for entree in temoin["profils"].values()] + [lacunes]
    attendus = {**nous, lacunes["code"]: _le_droit(
        simulateur, lacunes, tuple(lacunes["absentes"]))}
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE_JS,
         json.dumps([profils, AFFILIATIONS])],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = json.loads(execution.stdout)
    for code, moi in attendus.items():
        ouverte, motif, pension = portage[code]
        assert ouverte is moi["ouverte"] and motif == moi["motif"], code
        assert pension == pytest.approx(moi["pension"], rel=1e-9), code
