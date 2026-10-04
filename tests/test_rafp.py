"""Le RAFP liquidé comme le conseil d'administration de l'ERAFP l'a réglé.

Le décret n° 2004-569 renvoie au conseil d'administration de l'ERAFP le barème
qui module la valeur de service selon l'âge (article 8), celui qui convertit la
rente en capital et le versement de ce capital par fractions (article 9). Ses
délibérations, lues le 4 octobre 2026 (fiche `rafp_majoration_capital`) :
le barème de 2005, au pivot de soixante ans, puis celui du 5 février 2015, au
pivot de soixante-deux, « ≥ 75 1,81 », pour les prestations qui prennent effet
depuis le 1er mars 2015 ; le barème de conversion de 2005, puis celui du 16
décembre 2021 au 1er janvier 2022 ; le capital fractionné de 4 600 points en mai
2019, de 4 900 en avril 2024. L'ERAFP calcule l'âge « en tenant compte du nombre
d'années et du nombre de mois ». Les carrières sont fictives.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.saisie import Saisie
from outils_web import contexte  # noqa: F401 — la fixture partagée

RACINE = Path(__file__).resolve().parents[1]


def test_le_bareme_de_2015_ne_vaut_que_depuis_le_1er_mars_2015():
    """« Jusqu'à la fin du mois de février 2015, la surcote s'appliquait à
    partir d'un âge pivot de 60 ans » : à 64 ans, 1,18 en février 2015, 1,08
    en mars — l'exemple de la question écrite n° 92389. À 75 ans et au-delà,
    1,81, comme la délibération l'écrit, et non 1,80."""
    fevrier, mars = DateMois(2015, 2), DateMois(2015, 3)
    assert liquider.majoration_rafp(64.0, fevrier) == 1.18
    assert liquider.majoration_rafp(64.0, mars) == 1.08
    assert liquider.majoration_rafp(60.0, fevrier) == 1.00
    assert liquider.majoration_rafp(62.0, fevrier) == 1.08
    assert liquider.majoration_rafp(61.0, mars) == liquider.majoration_rafp(62.0, mars) == 1.00
    assert liquider.majoration_rafp(75.0, mars) == liquider.majoration_rafp(77.5, mars) == 1.81
    assert liquider.majoration_rafp(75.0, fevrier) == 2.08


def test_le_coefficient_se_prend_au_mois_sans_arrondi():
    """Entre deux âges entiers, au prorata des mois révolus : 62 ans et 9 mois
    valent 1,03 et 64 ans et 6 mois 1,10, comme le simulateur ; 68 ans et 4
    mois, 1,28 + 0,05 × 4 / 12, que le simulateur arrondit à 1,30 et qu'aucun
    texte n'arrondit. Avant 2015, 62 ans et 6 mois valaient 1,105 (SNES,
    2014)."""
    effet = DateMois(2027, 1)
    assert liquider.majoration_rafp(62.75, effet) == pytest.approx(1.03, abs=1e-12)
    assert liquider.majoration_rafp(64.5, effet) == pytest.approx(1.10, abs=1e-12)
    assert liquider.majoration_rafp(68 + 4 / 12, effet) == pytest.approx(1.28 + 0.05 * 4 / 12)
    assert liquider.majoration_rafp(74 + 11 / 12, effet) == pytest.approx(1.71 + 0.10 * 11 / 12)
    assert liquider.majoration_rafp(62.5, DateMois(2014, 9)) == pytest.approx(1.105)


def test_la_conversion_en_capital_change_au_1er_janvier_2022():
    """Le barème de 2005, confirmé en 2015, jusqu'au 31 décembre 2021 : 24,62 à
    62 ans ; celui de la délibération du 16 décembre 2021 depuis : 27,11. Au
    mois aussi : 64 ans et 6 mois valent 25,18 en 2031, comme le simulateur."""
    assert liquider.conversion_capital_rafp(62.0, DateMois(2021, 12)) == 24.62
    assert liquider.conversion_capital_rafp(62.0, DateMois(2022, 1)) == 27.11
    assert liquider.conversion_capital_rafp(60.0, DateMois(2010, 1)) == 25.98
    assert liquider.conversion_capital_rafp(64.5, DateMois(2031, 1)) == pytest.approx(25.18)


def test_le_capital_se_verse_en_une_fois_ou_en_deux_selon_la_date_et_les_points():
    """En deux fois près du seuil : de 4 600 points en mai 2019, quinze mois de
    rente puis le solde au seizième mois ; de 4 900 en avril 2024, quatre mois
    puis le solde au cinquième. En une fois avant mai 2019, sous le seuil du
    fractionnement, ou quand le RAFP prend effet plus de quinze, puis plus de
    quatre mois après la retraite de base. À 5 125 points, une rente."""
    def forme(points, effet, ecart=0):
        return liquider.prestation_rafp(1200.0, points, 5125, 64.0, effet, ecart)

    avril_2024, mars_2024 = DateMois(2024, 4), DateMois(2024, 3)
    assert forme(5125, avril_2024).forme == "rente"
    assert forme(4899, avril_2024).forme == "capital"
    deux_fois = forme(4900, avril_2024)
    assert deux_fois.forme == "capital_fractionne"
    assert deux_fois.premiere_fraction == pytest.approx(400.0)
    assert deux_fois.mois_du_solde == 5
    assert deux_fois.capital == pytest.approx(1200.0 * 25.57)
    assert forme(4900, avril_2024, ecart=5).forme == "capital"
    assert forme(4900, avril_2024, ecart=4).forme == "capital_fractionne"
    avant = forme(4700, mars_2024, ecart=15)
    assert (avant.forme, avant.premiere_fraction, avant.mois_du_solde) == (
        "capital_fractionne", pytest.approx(1500.0), 16)
    assert forme(4700, mars_2024, ecart=16).forme == "capital"
    assert forme(4700, DateMois(2020, 5), ecart=40).forme == "capital_fractionne"
    assert forme(4700, DateMois(2019, 4)).forme == "capital"
    assert forme(4599, DateMois(2020, 1)).forme == "capital"


def _rafp(contexte, **requete):
    """La pension du RAFP qu'une saisie fictive liquide au scénario 1."""
    resultat = contexte.simuler(Saisie.depuis_requete(requete)).actuel
    return next(p for p in resultat.pensions_par_regime if p.regime == "rafp")


def test_un_fonctionnaire_parti_a_64_ans_et_6_mois_touche_le_coefficient_du_mois(contexte):
    """Né le 15 juin 1966, parti en janvier 2031 : 64 ans et 6 mois révolus,
    1,10 — la majoration d'un âge entier, 1,08, lui retirait 1,8 %."""
    pension = _rafp(contexte, naissance="1966-06-15", statut="fonctionnaire_etat",
                    debut="1990-09", liquidation="64.5", primes="0.2")
    assert "coefficient de majoration 1.1000" in pension.detail


def test_un_fonctionnaire_parti_en_2012_garde_le_bareme_de_2005(contexte):
    """Né le 15 juin 1950, parti à 62 ans en juillet 2012 : le barème au pivot
    de soixante ans lui sert 1,08, et ses sept années de primes, sous le seuil,
    un capital au coefficient de conversion de 2005, 24,62."""
    pension = _rafp(contexte, naissance="1950-06-15", statut="fonctionnaire_etat",
                    debut="1975-09", liquidation="62", primes="0.15")
    assert "coefficient de majoration 1.0800" in pension.detail
    assert "en une fois" in pension.detail
    assert pension.capital == pytest.approx(pension.montant * 24.62)


def test_le_rafp_qui_attend_l_age_legal_compte_ses_mois_depuis_le_depart(contexte):
    """Le RAFP d'un fonctionnaire parti avant l'âge légal prend effet à cet
    âge : les mois qui le séparent du départ déclaré, ceux que le
    fractionnement oppose à la retraite de base."""
    saisie = Saisie.depuis_requete({"naissance": "1970-06-15", "statut": "fonctionnaire_etat",
                                    "debut": "1992-09", "liquidation": "60"})
    carriere = contexte.carriere(saisie)
    assert liquider.mois_apres_le_depart(carriere, 64.0) == 48
    assert liquider.mois_apres_le_depart(carriere, 60.0) == 0
    assert liquider.mois_apres_le_depart(carriere.liquidee_au(carriere.date_de_l_age(64.0)),
                                         64.0) == 48


#: Le jumeau JavaScript, sur les mêmes âges, dates et points.
_JUMEAU = """
import { DateMois } from "./moteur/js/calendrier.js";
import { conversionCapitalRafp, majorationRafp, prestationRafp }
  from "./moteur/js/droit/liquider.js";
const { ages, dates, prestations } = JSON.parse(process.argv[1]);
const date = ([a, m]) => new DateMois(a, m);
process.stdout.write(JSON.stringify({
  majorations: dates.map((d) => ages.map((age) => majorationRafp(age, date(d)))),
  conversions: dates.map((d) => ages.map((age) => conversionCapitalRafp(age, date(d)))),
  prestations: prestations.map(([rente, points, age, d, ecart]) =>
    prestationRafp(rente, points, 5125, age, date(d), ecart)),
}));
"""


def test_le_portage_javascript_rend_les_memes_coefficients_au_bit_pres():
    ages = [60 + mois / 12 for mois in range(0, 12 * 18)]
    dates = [(2014, 9), (2015, 2), (2015, 3), (2021, 12), (2022, 1), (2030, 1)]
    prestations = [(1234.5, points, 63 + 4 / 12, d, ecart)
                   for points in (4599, 4600, 4899, 4900, 5000, 5124, 5125)
                   for d in ((2019, 4), (2019, 5), (2020, 6), (2024, 3), (2024, 4))
                   for ecart in (0, 4, 5, 15, 16)]
    attendu = {
        "majorations": [[liquider.majoration_rafp(age, DateMois(*d)) for age in ages]
                        for d in dates],
        "conversions": [[liquider.conversion_capital_rafp(age, DateMois(*d)) for age in ages]
                        for d in dates],
        "prestations": [vars(liquider.prestation_rafp(rente, points, 5125, age,
                                                      DateMois(*d), ecart))
                        for rente, points, age, d, ecart in prestations],
    }
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU,
         json.dumps({"ages": ages, "dates": dates, "prestations": prestations})],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    assert json.loads(execution.stdout) == json.loads(json.dumps(attendu))
