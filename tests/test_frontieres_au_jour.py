"""Les lignes de liquidation commencent au jour que leur texte nomme.

Étape 6 de la séparation des axes (note de décision 0009) : une ligne de
liquidation coupée au 1er janvier de l'année d'un texte prend la date que ce
texte donne. Chaque date vient du texte, lu dans l'index de la DILA le
23 novembre 2026 ; la note
`docs/feuille_de_route/191/2026-11-23-etape-6-les-dates-sans-effet.md` dit,
frontière par frontière, la phrase lue.

- **1er décembre 1964.** Loi n° 64-1339, article 1er (LEGIARTI000006450745) :
  les dispositions du code « prendront effet au 1er décembre 1964 ».
- **1er avril 1983.** Arrêté du 27 janvier 1983 (JORFTEXT000000654120) :
  l'Ircantec liquide sans coefficient de réduction les titulaires d'une
  pension à taux plein du régime général « à compter du 01-04-1983 ».
- **1er juillet 1992.** Décret n° 46-2769, article 131 : « pour les pensions
  liquidées à compter du 1er juillet 1992 » (LEGIARTI000006765010).
- **1er avril 2010.** Loi n° 2009-1646, article 65 (JORFARTI000021529299) :
  L. 643-1-1 vaut pour les pensions « prenant effet à compter du 1er avril
  2010 » (LEGIARTI000021537910).
- **3 juin 2011.** Décret n° 2004-569, rédaction en vigueur le 3 juin 2011
  (LEGIARTI000024113145) : la retraite additionnelle s'ouvre à l'âge de
  L. 161-17-2.
- **30 juin 2011.** Arrêté du 23 juin 2011 (JORFTEXT000024270202), publié le
  29 juin sans date propre : les statuts de la CAVP et ceux des prestations
  complémentaires des directeurs de laboratoire valent le lendemain.
- **1er juillet 2011.** Loi n° 2010-1330, article 118, II
  (JORFARTI000023022348) : ses articles 18 à 40, 79, 83 et 84 « sont
  applicables aux pensions prenant effet à compter du 1er juillet 2011 » —
  L. 351-1 et L. 351-1-4 du code de la sécurité sociale, L. 732-18 du code
  rural, L. 24 du code des pensions, que la CNRACL et les ouvriers de l'État
  suivent ; arrêté du 21 juin 2011, article 4, pour l'Ircantec
  (JORFARTI000024249370).
- **1er septembre 2023.** Loi n° 2023-270, article 10, XXX, B, et article 11,
  VII, B : « pensions prenant effet à compter du 1er septembre 2023 » —
  L. 351-1-2-1 (LEGIARTI000047449229), L. 14 du code des pensions
  (LEGIARTI000047452815) ; article 21, II, pour les
  avocats : L. 653-3 (LEGIARTI000047453367).
- **10 janvier 2024.** Arrêté du 27 décembre 2023 (JORFTEXT000048880637),
  publié le 9 janvier 2024 sans date propre : les statuts de la CARPIMKO
  valent le lendemain.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.types_du_pont.carriere import Metier

from facade import Carriere, Simulateur, commun

RACINE_DONNEES = Path(__file__).resolve().parents[1] / "data"

#: (régime, le jour du texte, le 1er janvier que la ligne portait)
FRONTIERES = [
    ("fonction_publique_etat", "1964-12-01", "1964-01-01"),
    ("ircantec", "1983-04-01", "1983-01-01"),
    ("mines", "1992-07-01", "1992-01-01"),
    ("cnavpl", "2010-04-01", "2010-01-01"),
    ("rafp", "2011-06-03", "2011-01-01"),
    ("cavp_complementaire", "2011-06-30", "2012-01-01"),
    ("asv_directeurs_laboratoire", "2011-06-30", "2009-01-01"),
    ("regime_general", "2011-07-01", "2011-01-01"),
    ("msa_salaries", "2011-07-01", "2011-01-01"),
    ("msa_non_salaries", "2011-07-01", "2011-01-01"),
    ("fonction_publique_etat", "2011-07-01", "2011-01-01"),
    ("cnracl", "2011-07-01", "2011-01-01"),
    ("fspoeie", "2011-07-01", "2011-01-01"),
    ("ircantec", "2011-07-01", "2011-01-01"),
    ("regime_general", "2023-09-01", "2023-01-01"),
    ("msa_salaries", "2023-09-01", "2023-01-01"),
    ("fonction_publique_etat", "2023-09-01", "2023-01-01"),
    ("cnracl", "2023-09-01", "2023-01-01"),
    ("fspoeie", "2023-09-01", "2023-01-01"),
    ("cnbf", "2023-09-01", "2024-01-01"),
    ("carpimko_complementaire", "2024-01-10", "2024-01-01"),
]


@pytest.fixture(scope="module")
def catalogue() -> CatalogueRegimes:
    return CatalogueRegimes(RACINE_DONNEES)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


@pytest.mark.parametrize("regime,jour,ancien", FRONTIERES)
def test_la_ligne_de_liquidation_commence_au_jour_du_texte(catalogue, regime, jour, ancien):
    debuts = [ligne["du"] for ligne in catalogue[regime].liquidation]
    fins = [ligne["au"] for ligne in catalogue[regime].liquidation]
    assert jour in debuts and jour in fins
    assert ancien not in debuts


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int, mois: int,
              liquidation: float, debut: float, sexe: str = "H", enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, mois_naissance=mois, jour_naissance=15, sexe=sexe,
        metiers=[Metier(affiliation=affiliation, age_debut=debut, niveau_salaire=1.0)],
        age_liquidation=liquidation, macro=simulateur.macro, nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return commun.date_d_effet(carriere), resultat


def _avantage(resultat, code: str, regime: str) -> float:
    for avantage in resultat.avantages_appliques:
        if avantage.code == code:
            return dict(avantage.par_regime).get(regime, 0.0)
    return 0.0


def test_l_avocat_majore_pour_trois_enfants_des_le_1er_septembre_2023(simulateur):
    """L. 653-3, que crée l'article 21 de la loi n° 2023-270, étend L. 351-12
    aux avocats pour « les pensions prenant effet à compter du 1er septembre
    2023 » : un dixième de la pension de base au père de trois enfants parti
    ce jour-là, rien à celui du 1er août. Le dépôt attendait janvier 2024."""
    effet, aout = _calculer(simulateur, "avocat", 1956, 7, 67.0, 27.0, enfants=3)
    assert effet == "2023-08-01"
    assert _avantage(aout, "majoration_enfants", "cnbf") == 0.0
    effet, septembre = _calculer(simulateur, "avocat", 1956, 8, 67.0, 27.0, enfants=3)
    assert effet == "2023-09-01"
    base = next(p.montant for p in septembre.pensions_par_regime if p.regime == "cnbf")
    assert base > 0
    assert _avantage(septembre, "majoration_enfants", "cnbf") == pytest.approx(0.10 * base)


def test_la_base_des_liberaux_majore_la_duree_pour_enfant_au_1er_avril_2010(simulateur):
    """L. 643-1-1, créé par l'article 65 de la loi n° 2009-1646, vaut pour les
    pensions « prenant effet à compter du 1er avril 2010 » : la mère de trois
    enfants partie le 1er mars 2010 après trente-cinq ans d'exercice n'a que
    ses trimestres d'exercice, 140 au plus, celle du 1er avril en a vingt-quatre de plus, huit
    par enfant (L. 351-4). Le dépôt les servait dès janvier."""
    def duree(mois: int):
        effet, resultat = _calculer(simulateur, "profession_liberale", 1945, mois, 65.0, 30.0,
                                    sexe="F", enfants=3)
        codes = {avantage.code for avantage in resultat.avantages_appliques}
        return effet, resultat.trimestres_valides, "majoration_duree_assurance" in codes
    effet, mars, majoree = duree(2)
    assert (effet, majoree) == ("2010-03-01", False) and mars <= 140
    effet, avril, majoree = duree(3)
    assert (effet, majoree) == ("2010-04-01", True) and avril >= mars + 24
