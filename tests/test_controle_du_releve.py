"""Le contrôle d'un relevé, sur la page des résultats (action 138, étape 10).

Le calculateur « calcul-verification-pension-retraite » (registre,
``calcul_verification_pension``) recalcule les trimestres d'un relevé réel
depuis ses montants, et le contrôle ainsi ; dans le dépôt, le relevé faisait
foi sans que rien ne signale une année sous-validée. Le dépliant « Votre
relevé, contrôlé » (``releveControle``, ``moteur/js/pages.js``) met en regard,
pour chaque année de salarié du régime général ou des salariés agricoles dont
le relevé porte les trimestres, ceux que son revenu valide au seuil de l'année
(R. 351-9), quand ils diffèrent ; le calcul, lui, garde ceux du relevé. Les
carrières sont fictives.
"""

from __future__ import annotations

import html
import re

from outils_pont import Saisies
from outils_web import page  # noqa: F401 — la fixture partagée


def _annees(debut: int, fin: int) -> list[str]:
    """Des années pleines de salarié, dont le revenu valide les quatre
    trimestres que le relevé retient."""
    return [f"{annee}:salarie_prive_non_cadre:{20_000 + 500 * (annee - 1997)}:4"
            for annee in range(debut, fin + 1)]


#: Le relevé d'une salariée née en 1975, dont trois années ne s'accordent pas
#: à leur revenu, et deux ne se contrôlent pas.
RELEVE = {"naissance": "1975-01-01", "sexe": "F", "liquidation": "2039-01",
          "releve": "\n".join([
              *_annees(1997, 2008),
              # 200 heures du SMIC du 1er janvier 2009, 8,71 € : 1 742 € le
              # trimestre ; 3 600 € en valident deux, le relevé en retient un.
              "2009:salarie_prive_non_cadre:3600:1",
              *_annees(2010, 2014),
              # 150 heures du SMIC de 2015, 9,61 € : 1 441,50 € ; 3 000 € en
              # valident deux, le relevé en retient un.
              "2015:salarie_prive_non_cadre:3000:1",
              # Aucun revenu, quatre trimestres : une période que le relevé
              # valide sans revenu.
              "2016:salarie_prive_non_cadre:0:4",
              # La fonction publique compte ses services au jour, l'artisan
              # valide aussi par son assiette minimale : ni l'une ni l'autre
              # année ne se contrôle au revenu.
              "2017:fonctionnaire_etat:30000:3.33",
              "2018:artisan:3000:1",
              *_annees(2019, 2025),
          ])}


def _sans_trimestres(releve: str) -> str:
    return "\n".join(":".join(ligne.split(":")[:3]) for ligne in releve.split("\n"))


def _controle(corps: str) -> str:
    debut = corps.index("Votre relevé, contrôlé")
    return corps[debut:corps.index("</details>", debut)]


def _texte(fragment: str) -> str:
    """Le texte d'un fragment de page, balises ôtées, espaces fines comprises."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))
                  .replace(" ", " ").replace("\xa0", " ")).strip()


def test_le_releve_se_controle_annee_par_annee_au_seuil_du_trimestre(page):
    """Les années de salarié dont le relevé retient d'autres trimestres que
    leur revenu n'en valide, au seuil de leur année, et celles-là seulement :
    2009 et 2015, d'un trimestre de moins chacune, et 2016, que le relevé
    valide sans revenu. Le revenu valide ce que le modèle Python compte du même
    relevé sans ses trimestres ; ni la fonctionnaire de 2017 ni l'artisane de
    2018 ne se contrôlent. Le résumé du relevé renvoie au dépliant."""
    corps = page("/simuler", **RELEVE)
    bloc = _controle(corps)
    entetes = re.findall(r'<th class="[^"]*" scope="col">([^<]*)</th>', bloc)
    assert [html.unescape(entete) for entete in entetes] == [
        "Année", "Revenu du relevé", "Seuil d'un trimestre", "Le revenu valide",
        "Le relevé retient"]
    rangees = [(int(_texte(tete)), [_texte(cellule) for cellule in
                                    re.findall(r"<td[^>]*>(.*?)</td>", cellules)])
               for tete, cellules in re.findall(
                   r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)]
    assert rangees == [
        (2009, ["3 600,00 €", "1 742,00 €", "2 trimestres", "1 trimestre"]),
        (2015, ["3 000,00 €", "1 441,50 €", "2 trimestres", "1 trimestre"]),
        (2016, ["0,00 €", "1 450,50 €", "0 trimestre", "4 trimestres"]),
    ]
    carriere = Saisies().carriere({**RELEVE, "releve": _sans_trimestres(RELEVE["releve"])})
    valides = {ligne.annee: ligne.trimestres_valides for ligne in carriere.lignes}
    assert [valides[annee] for annee, _ in rangees] == [2, 2, 0]
    texte = _texte(bloc)
    assert "27 années" in texte
    assert "2 trimestres de moins" in texte
    resume = corps[corps.index("lue sur un relevé"):]
    assert 'data-vers="releve-controle"' in resume[:resume.index("</p>")]


def test_l_annee_du_depart_se_controle_sous_le_plafond_du_calcul(page):
    """L'année du départ ne compte que ses trimestres civils d'avant la date
    d'effet : à un départ de juillet 2025, le calcul ne retient de 2025 que
    deux des quatre trimestres que le relevé porte, et son revenu n'en valide
    pas davantage. Les deux comptes sont bornés de même, et le relevé n'y
    retient pas plus que son revenu n'en valide."""
    releve = "\n".join(f"{annee}:salarie_prive_non_cadre:{20_000 + 500 * (annee - 1985)}:4"
                       for annee in range(1985, 2026))
    bloc = _controle(page("/simuler", naissance="1963-01-01", sexe="F",
                          liquidation="2025-07", releve=releve))
    assert "<table" not in bloc
    assert "autant de trimestres" in _texte(bloc)


def test_un_releve_d_accord_le_dit_et_sans_trimestres_ne_se_controle_pas(page):
    """Un relevé dont chaque année valide au revenu ce qu'il retient le dit,
    sans tableau ; un relevé qui ne porte pas de trimestres, ni une carrière
    décrite par ses métiers, n'ont rien à contrôler."""
    accord = {**RELEVE, "releve": "\n".join(_annees(1997, 2025))}
    corps = page("/simuler", **accord)
    bloc = _controle(corps)
    assert "<table" not in bloc
    assert "autant de trimestres" in _texte(bloc)
    assert 'data-vers="releve-controle"' not in corps
    sans = {**RELEVE, "releve": _sans_trimestres(accord["releve"])}
    assert "Votre relevé, contrôlé" not in page("/simuler", **sans)
    assert "Votre relevé, contrôlé" not in page("/simuler", naissance="1975-01-01")
