"""Les taux de cotisation de l'Ircantec, tels que le décret les fixe et que la
caisse les appelle.

Le IV de l'article 7 du décret n° 70-1277 du 23 décembre 1970 fixe les taux
théoriques, agent et employeur, sous le plafond de la sécurité sociale
(tranche A) et au-dessus (tranche B) ; l'article 9 bis de l'arrêté du
30 décembre 1970 fixe le taux d'appel, qui les majore sans ouvrir de points.
La fiche du régime, `data/reference/regimes/ircantec.yaml`, porte les taux
APPELÉS, part de l'agent comprise : ce sont eux que le moteur prélève.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees import CatalogueRegimes


@pytest.fixture(scope="module")
def catalogue() -> CatalogueRegimes:
    return CatalogueRegimes(RACINE_DONNEES)


def test_les_taux_ircantec_du_decret_du_5_octobre_2026(catalogue):
    """Décret n° 2026-926 du 5 octobre 2026, article 1er, qui réécrit le IV de
    l'article 7 du décret n° 70-1277 : taux théoriques, agent et employeur, de
    2,24 % et 3,36 % sous le plafond « pour la période antérieure au
    31 décembre 2027 », 2,30 % et 3,45 % en 2028, 2,36 % et 3,54 % à compter de
    2029 ; au-dessus, 5,56 % et 10,04 %, 5,86 % et 10,09 %, 6,16 % et 10,14 %
    (JORFARTI000054953274). Le taux d'appel vaut 127 % depuis le 1er janvier
    2026 (arrêté du 30 décembre 1970, article 9 bis, LEGIARTI000053281114) ;
    les taux appelés, arrondis au centième, sont ceux que les centres de
    gestion publient : 2,84 + 4,27, puis 2,92 + 4,38, puis 3 + 4,50 sous le
    plafond ; 7,06 + 12,75, puis 7,44 + 12,81, puis 7,82 + 12,88 au-dessus.
    La fiche portait 7,11 % et 19,81 % « de 2026 à aujourd'hui », sans fin."""

    def periode(annee, assiette):
        trouvees = [p for p in catalogue["ircantec"].periodes
                    if p.debut <= annee <= (p.fin or 9999) and p.assiette == assiette]
        assert len(trouvees) == 1, (annee, assiette, trouvees)
        return trouvees[0]

    attendus = {
        (2026, "tranche_1"): (0.0711, 2.84), (2027, "tranche_1"): (0.0711, 2.84),
        (2028, "tranche_1"): (0.0730, 2.92), (2029, "tranche_1"): (0.0750, 3.00),
        (2050, "tranche_1"): (0.0750, 3.00),
        (2026, "tranche_2"): (0.1981, 7.06), (2027, "tranche_2"): (0.1981, 7.06),
        (2028, "tranche_2"): (0.2025, 7.44), (2029, "tranche_2"): (0.2070, 7.82),
        (2050, "tranche_2"): (0.2070, 7.82),
    }
    for (annee, assiette), (taux, part_agent) in attendus.items():
        p = periode(annee, assiette)
        assert p.taux_cotisation_retraite == pytest.approx(taux), (annee, assiette)
        assert p.taux_cotisation_retraite * p.part_salariale * 100 == pytest.approx(
            part_agent, abs=0.006), (annee, assiette)
    # Les taux appelés sont les taux théoriques du décret au taux d'appel de
    # 127 %, arrondis au centième.
    for theorique, appele in ((2.30, 2.92), (3.45, 4.38), (2.36, 3.00), (3.54, 4.50),
                              (5.86, 7.44), (10.09, 12.81), (6.16, 7.82), (10.14, 12.88)):
        assert round(theorique * 1.27, 2) == pytest.approx(appele)
